"""Check finite source and refusal rules. These tests perform no network action."""

import copy
import json
import os
import pickle
import tempfile
import unittest
from unittest.mock import Mock, patch

from crewshal.linux_network import (
    LaneNetworkPlan,
    ProviderNetworkPlan,
    OwnedProviderNetworks,
    NetworkRefusal,
    canonical_nft,
    nft_table,
    _static_helper,
)
from crewshal.linux_setup import OwnedStorageReservation
from crewshal.linux_storage import BoundedStorageJobs


class Phase2DNetwork(unittest.TestCase):
    def plan(self):
        return ProviderNetworkPlan(
            configuration_source="a" * 64,
            ip_binary="b" * 64,
            nft_binary="c" * 64,
            host_table="crewshal_abcd1234",
            endpoints={"chatgpt.com": ["1.1.1.1"], "auth.openai.com": ["8.8.8.8"]},
            lanes=[
                LaneNetworkPlan(
                    lane_id=lane,
                    host_interface=f"csabcd1234{index}h",
                    private_interface=f"csabcd1234{index}p",
                    subnet=f"172.31.253.{(index - 1) * 4}/30",
                )
                for index, lane in enumerate(("qualification-1", "qualification-2", "live"), 1)
            ],
        )

    def test_private_metadata_and_special_provider_addresses_are_refused(self):
        for address in ("127.0.0.1", "169.254.169.254", "10.1.1.1", "224.0.0.1", "::1"):
            payload = self.plan().model_dump()
            payload["endpoints"] = {"chatgpt.com": [address]}
            with self.subTest(address=address), self.assertRaises(ValueError):
                ProviderNetworkPlan.model_validate(payload)

    def test_hostname_command_injection_and_empty_inventory_are_refused(self):
        for endpoints in (
            {},
            {"chatgpt.com;uname": ["1.1.1.1"]},
            {"chatgpt.com\nsecret": ["1.1.1.1"]},
        ):
            payload = self.plan().model_dump()
            payload["endpoints"] = endpoints
            with self.assertRaises(ValueError):
                ProviderNetworkPlan.model_validate(payload)

    def test_network_lanes_cannot_be_reordered_reused_or_overlap(self):
        for change in ("order", "reuse", "overlap"):
            payload = self.plan().model_dump()
            if change == "order":
                payload["lanes"].reverse()
            elif change == "reuse":
                payload["lanes"][2] = payload["lanes"][0]
            else:
                payload["lanes"][2]["subnet"] = payload["lanes"][0]["subnet"]
            with self.subTest(change=change), self.assertRaises(ValueError):
                ProviderNetworkPlan.model_validate(payload)

    def test_private_default_drop_requires_native_uid_exact_endpoint_and_https(self):
        plan = self.plan()
        objects = nft_table(plan, plan.lanes[0])
        chains = [item["chain"] for item in objects if "chain" in item]
        self.assertEqual(
            {item["name"]: item["policy"] for item in chains},
            {"input": "drop", "output": "drop", "forward": "drop"},
        )
        rule = next(
            item["rule"] for item in objects if "rule" in item and len(item["rule"]["expr"]) == 4
        )
        self.assertEqual(
            rule["expr"][0],
            {"match": {"op": "==", "left": {"meta": {"key": "skuid"}}, "right": 65534}},
        )
        self.assertEqual(rule["expr"][1]["match"]["right"], {"set": ["1.1.1.1", "8.8.8.8"]})
        self.assertEqual(rule["expr"][2]["match"]["right"], 443)

    def test_semantic_readback_retains_extra_allow_rule_and_changed_policy(self):
        expected = nft_table(self.plan(), self.plan().lanes[0])
        changed = copy.deepcopy(expected)
        changed[1]["chain"]["policy"] = "accept"
        self.assertNotEqual(canonical_nft(json.dumps({"nftables": changed}).encode()), expected)

    def test_synthetic_https_route_cannot_redirect_or_forward_the_live_lane(self):
        original = self.plan()
        plan = original.model_copy(update={"qualification_transport": "original_two_lane_tls_v1"})
        self.assertEqual(plan.hosts_bytes, original.hosts_bytes)
        self.assertEqual(nft_table(plan, plan.lanes[2]), nft_table(original, original.lanes[2]))
        for lane in plan.lanes[:2]:
            objects = nft_table(plan, lane)
            redirects = [
                value
                for item in objects
                if "rule" in item
                for value in item["rule"]["expr"]
                if "dnat" in value
            ]
            self.assertEqual(redirects, [{"dnat": {"addr": lane.host_address}}])
            route = next(
                item["rule"]
                for item in objects
                if "rule" in item and item["rule"]["chain"] == "fixture_route"
            )
            self.assertEqual(route["expr"][0]["match"]["right"], 65534)
            self.assertEqual(route["expr"][2]["match"]["right"], 443)
            outgoing = next(
                item["rule"]
                for item in objects
                if "rule" in item
                and len(item["rule"]["expr"]) == 4
                and item["rule"]["chain"] == "output"
            )
            self.assertEqual(outgoing["expr"][1]["match"]["right"], lane.host_address)
        rules = [item["rule"] for item in nft_table(plan, None) if "rule" in item]
        nat_sources = [
            rule["expr"][0]["match"]["right"] for rule in rules if rule["chain"] == "postrouting"
        ]
        self.assertEqual(nat_sources, [plan.lanes[2].private_address])
        for lane in plan.lanes[:2]:
            forwarded = [
                rule
                for rule in rules
                if rule["chain"] == "forward"
                and rule["expr"][0]
                == {
                    "match": {
                        "op": "==",
                        "left": {"meta": {"key": "iifname"}},
                        "right": lane.host_interface,
                    }
                }
            ]
            self.assertEqual(len(forwarded), 1)
            self.assertEqual(forwarded[0]["expr"][-1], {"drop": None})

    def test_synthetic_route_changes_remain_visible_to_semantic_readback(self):
        plan = self.plan().model_copy(
            update={"qualification_transport": "original_two_lane_tls_v1"}
        )
        expected = nft_table(plan, plan.lanes[0])
        changed = copy.deepcopy(expected)
        route = next(
            item["rule"]
            for item in changed
            if "rule" in item and item["rule"]["chain"] == "fixture_route"
        )
        route["expr"][-1] = {"dnat": {"addr": plan.lanes[2].host_address}}
        self.assertNotEqual(canonical_nft(json.dumps({"nftables": changed}).encode()), expected)
        changed = copy.deepcopy(expected)
        changed.append(
            {
                "rule": {
                    "family": "inet",
                    "table": "crewshal_provider",
                    "chain": "output",
                    "expr": [{"accept": None}],
                }
            }
        )
        self.assertNotEqual(canonical_nft(json.dumps({"nftables": changed}).encode()), expected)

    def test_handles_and_version_metadata_do_not_hide_semantic_fields(self):
        expected = nft_table(self.plan(), self.plan().lanes[0])
        observed = copy.deepcopy(expected)
        for item in observed:
            next(iter(item.values()))["handle"] = 42
        observed.insert(0, {"metainfo": {"version": "synthetic"}})
        self.assertEqual(canonical_nft(json.dumps({"nftables": observed}).encode()), expected)
        observed.append({"set": {"name": "extra"}})
        with self.assertRaises(ValueError):
            canonical_nft(json.dumps({"nftables": observed}).encode())

    def test_hosts_file_contains_only_frozen_hosts_and_loopback(self):
        self.assertEqual(
            self.plan().hosts_bytes,
            b"127.0.0.1 localhost\n::1 localhost\n8.8.8.8 auth.openai.com\n1.1.1.1 chatgpt.com\n",
        )

    def test_missing_namespace_capability_burns_original_owner_without_effect_or_retry(self):
        reservation = object.__new__(OwnedStorageReservation)
        reservation._retain_installation_refusal = Mock()
        jobs = object.__new__(BoundedStorageJobs)
        with (
            patch(
                "crewshal.linux_network._net_namespace",
                side_effect=ValueError("synthetic namespace refusal"),
            ),
            patch("crewshal.linux_network.subprocess.Popen") as command,
        ):
            with self.assertRaisesRegex(NetworkRefusal, "namespace refusal") as result:
                OwnedProviderNetworks(reservation, jobs, self.plan(), 101, 102, 103)
            owner = result.exception.owner
            self.assertIs(reservation._provider_networks, owner)
            self.assertTrue(owner.failed)
            self.assertFalse(result.exception.resources_reusable)
            self.assertEqual(
                (owner.host_namespace, owner.ip_binary, owner.nft_binary), (101, 102, 103)
            )
            command.assert_not_called()
            with self.assertRaisesRegex(ValueError, "one-shot"):
                OwnedProviderNetworks(reservation, jobs, self.plan(), 101, 102, 103)
            with self.assertRaises(TypeError):
                pickle.dumps(owner)

    def test_network_registry_permits_only_original_jobs_and_fixed_readback(self):
        from crewshal.linux_production import EffectiveInstallation

        proof = object.__new__(EffectiveInstallation)
        owner = object.__new__(OwnedProviderNetworks)
        owner.jobs = object.__new__(BoundedStorageJobs)
        owner.readback_jobs = object.__new__(BoundedStorageJobs)
        owner.verify_custody = Mock()
        proof.reservation = OwnedStorageReservation.__new__(OwnedStorageReservation)
        proof.reservation._provider_networks = owner
        proof.verify_custody = Mock()
        proof._jobs = object.__new__(BoundedStorageJobs)
        proof._readback_jobs = object.__new__(BoundedStorageJobs)
        proof.physical = Mock()
        for jobs in (owner.jobs, owner.readback_jobs):
            proof.verify_registered_job(jobs)
            proof.verify_registered_action(jobs, owner._readback_child)
            with self.assertRaisesRegex(ValueError, "readback action"):
                proof.verify_registered_action(jobs, owner._create_child)
            with self.assertRaisesRegex(ValueError, "readback action"):
                proof.verify_registered_action(jobs, lambda: b"forged")
        with self.assertRaisesRegex(ValueError, "original bounded readback"):
            proof.verify_registered_job(object.__new__(BoundedStorageJobs))
        self.assertGreaterEqual(proof.verify_custody.call_count, 6)

    def test_first_network_helper_refuses_any_host_elf_interpreter(self):
        header = bytearray(64)
        header[:6] = b"\x7fELF\x02\x01"
        header[32:40] = (64).to_bytes(8, "little")
        header[54:56] = (56).to_bytes(2, "little")
        header[56:58] = (1).to_bytes(2, "little")
        with tempfile.TemporaryFile() as binary:
            binary.write(header + b"\x01" + b"\0" * 55)
            binary.flush()
            _static_helper(binary.fileno())
            os.pwrite(binary.fileno(), (3).to_bytes(4, "little"), 64)
            with self.assertRaisesRegex(ValueError, "host ELF interpreter"):
                _static_helper(binary.fileno())

    def test_missing_readonly_tool_root_refuses_before_any_command(self):
        reservation = object.__new__(OwnedStorageReservation)
        reservation._retain_installation_refusal = Mock()
        jobs = object.__new__(BoundedStorageJobs)
        with (
            patch("crewshal.linux_network._net_namespace", return_value=(1, 2)),
            patch("crewshal.linux_network.subprocess.Popen") as command,
        ):
            with self.assertRaisesRegex(NetworkRefusal, "complete copied readonly root") as error:
                OwnedProviderNetworks(reservation, jobs, self.plan(), 101, 102, 103)
        self.assertTrue(error.exception.owner.failed)
        self.assertIs(reservation._provider_networks, error.exception.owner)
        command.assert_not_called()
