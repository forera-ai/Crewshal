"""Offline entry checks supply no Linux execution or acceptance evidence."""

import copy
import io
import json
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch
from unittest.mock import Mock

from crewshal.candidate import CandidateFile, FrozenCandidate
from crewshal.contracts import Binding, record_digest
from crewshal.contracts import CheckDefinition, Task
from crewshal.dispatch import SOURCE_FILES, prepare_dispatch_configuration
from crewshal.linux_batch import OriginalQualificationCollector
from crewshal.linux_batch_entry import (
    ConditionalFrozenApproval,
    OriginalLiveQualification,
    observer_entry_source,
    read_frozen_inputs,
    FrozenBatchInputs,
    OwnerDecisionProposal,
    assemble_frozen_batch,
    current_qualification_manifest,
)
from crewshal.linux_early_timer import FrozenEarlyTimerRuntime
from crewshal.linux_inventory import RootEntry
from crewshal.linux_network import LaneNetworkPlan, ProviderNetworkPlan
from crewshal.linux_qualification_fixture import FrozenQualificationTLS
from crewshal.linux_validator import validator_toolchain_digest
from crewshal.model import ProjectModel, digest
from crewshal.qualification import QualificationIdentity
from crewshal.qualification_bundle import PROTOCOL_SHA256
from crewshal.runtime_batch import AFTER, CHECK_SOURCE, PreparationSelection, REQUIREMENT
from tests.acceptance import test_phase_2d_schedule as fixtures
from tests.acceptance import test_phase_2d_subscription as subscription_fixtures
from tests.acceptance import test_phase_2d_bootstrap_build_closure as build_fixtures
from tests.acceptance import test_phase_2d_qualification_fixture as qualification_fixtures


class ConditionalApprovalTests(unittest.TestCase):
    def setUp(self):
        self.launch = Binding(
            model="a" * 64,
            task="b" * 64,
            policy="c" * 64,
            scope="d" * 64,
            candidate="e" * 64,
        )
        self.expected = FrozenCandidate(
            files=[
                CandidateFile(
                    path="README.md",
                    kind="file",
                    mode=0o644,
                    size=len(AFTER),
                    sha256=digest(AFTER),
                )
            ]
        )
        self.decision = ConditionalFrozenApproval(
            id="frozen-owner-decision",
            run_id="run",
            launch_binding=self.launch,
            expected=self.expected,
            owner="Synthetic owner",
            reason="Synthetic conditional decision.",
        )
        self.actual = self.launch.model_copy(update={"candidate": record_digest(self.expected)})

    def test_actual_matching_binding_preserves_the_supplied_owner_decision(self):
        result = self.decision.bind_actual("run", self.launch, self.actual)
        self.assertEqual(result.binding, self.actual)
        self.assertEqual(result.owner, self.decision.owner)
        self.assertEqual(result.reason, self.decision.reason)
        self.assertEqual(result.id, self.decision.id)

    def test_unrelated_run_launch_policy_scope_and_candidate_cannot_transfer_approval(self):
        for field in type(self.actual).model_fields:
            changed = self.actual.model_copy(update={field: "f" * 64})
            with self.subTest(field=field), self.assertRaisesRegex(ValueError, "actual candidate"):
                self.decision.bind_actual("run", self.launch, changed)
        with self.assertRaises(ValueError):
            self.decision.bind_actual("another-run", self.launch, self.actual)
        with self.assertRaises(ValueError):
            self.decision.bind_actual("run", self.actual, self.actual)

    def test_conditional_decision_refuses_different_bytes_metadata_and_extra_paths(self):
        for change in ({"mode": 0o600}, {"sha256": "f" * 64}, {"size": 0}, {"path": "other"}):
            file = self.expected.files[0].model_copy(update=change)
            payload = self.decision.model_dump()
            payload["expected"] = FrozenCandidate(files=[file])
            with self.subTest(change=change), self.assertRaises(ValueError):
                ConditionalFrozenApproval.model_validate(payload)
        payload = self.decision.model_dump()
        payload["expected"] = self.expected.model_copy(update={"files": []})
        with self.assertRaises(ValueError):
            ConditionalFrozenApproval.model_validate(payload)

    def test_bypassed_decision_validation_cannot_approve_changed_expected_bytes(self):
        self.decision.expected.files[0].sha256 = "f" * 64
        with self.assertRaises(ValueError):
            self.decision.bind_actual("run", self.launch, self.actual)


class LiveQualificationProjectionTests(unittest.TestCase):
    def setUp(self):
        self.fixture = fixtures.Phase2DThreeLaneSchedule()
        self.fixture.setUp()
        self.addCleanup(self.fixture.doCleanups)
        self.schedule = self.fixture.owner
        self.sources = self.fixture.qualification(0), self.fixture.qualification(1)
        for index, source in enumerate(self.sources):
            self.fixture.finish(index, source)
        collectors = []
        for index, source in enumerate(self.sources):
            collector = object.__new__(OriginalQualificationCollector)
            # Synthetic terminal readback fixtures exercise the source join only.
            # They cannot establish actual native, broker, or process custody.
            collector.failed = False
            collector.consumed = True
            collector.result = source
            collector.bridge = SimpleNamespace(lane_context=self.schedule.contexts[index])
            collectors.append(collector)
        self.collectors = tuple(collectors)

    def test_live_projection_binds_both_retained_records_and_only_live_configuration(self):
        owner = OriginalLiveQualification(self.schedule, self.collectors)
        owner.verify()
        self.assertEqual(owner.record.identity, self.schedule.identities[2])
        for source in self.sources:
            self.assertIn(record_digest(source), owner.record.results[0].observation)
        self.assertFalse(owner.record.execution_allowed)
        self.assertEqual(self.sources[0].identity, self.schedule.identities[0])

    def test_parsed_record_or_readiness_flag_cannot_replace_original_collectors(self):
        for value in (self.sources[0], True, SimpleNamespace(result=self.sources[0])):
            with self.subTest(value=type(value)), self.assertRaises(ValueError):
                OriginalLiveQualification(self.schedule, (value, self.collectors[1]))
            if hasattr(self.schedule, "_live_qualification"):
                del self.schedule._live_qualification

    def test_copied_record_cannot_replace_its_original_retained_result(self):
        self.collectors[0].result = copy.deepcopy(self.sources[0])
        with self.assertRaisesRegex(ValueError, "copied"):
            OriginalLiveQualification(self.schedule, self.collectors)

    def test_repeated_projection_cannot_create_a_second_original_owner(self):
        OriginalLiveQualification(self.schedule, self.collectors)
        with self.assertRaisesRegex(ValueError, "consumed"):
            OriginalLiveQualification(self.schedule, self.collectors)

    def test_changed_source_or_projection_refuses_after_the_original_join(self):
        owner = OriginalLiveQualification(self.schedule, self.collectors)
        self.sources[0].results[0].observation = "Changed synthetic source."
        with self.assertRaises(ValueError):
            owner.verify()

    def test_changed_lane_profile_cannot_project_the_original_cases(self):
        self.schedule.contexts[2]._configuration.selection.model = "changed-model"
        with self.assertRaises(ValueError):
            OriginalLiveQualification(self.schedule, self.collectors)


class ObserverEntryTests(unittest.TestCase):
    def test_child_failure_coordinates_reach_refusal_without_private_text(self):
        from crewshal import linux_batch_entry as entry
        from crewshal.linux_storage import StorageChildRefusal, STORAGE_FAILURE_PREFIX

        detail = {"type": "OSError", "errno": 9, "source": "linux_storage.py", "line": 123}
        failure = StorageChildRefusal(STORAGE_FAILURE_PREFIX + json.dumps(detail).encode())
        owner = SimpleNamespace(handles={}, run=Mock(side_effect=failure))
        output = io.StringIO()
        with (
            patch.dict(entry.os.environ, {}, clear=True),
            patch.object(entry.sys, "platform", "linux"),
            patch.object(entry.sys, "argv", ["observer", "frozen-plan"]),
            patch.object(
                entry.sys, "flags", SimpleNamespace(isolated=1, no_site=1, dont_write_bytecode=1)
            ),
            patch.object(entry.os, "getuid", return_value=0),
            patch.object(entry.os, "getgid", return_value=0),
            patch.object(entry, "read_frozen_inputs", return_value=(object(), 999)),
            patch.object(entry, "OriginalFiniteBatch", return_value=owner),
            patch.object(entry.sys, "stdout", output),
            patch.object(entry.signal, "pause", side_effect=InterruptedError),
            self.assertRaises(InterruptedError),
        ):
            entry.main()
        result = json.loads(output.getvalue())
        self.assertEqual(result["storage_child_failure"], detail)
        self.assertFalse(result["execution_allowed"])
        self.assertFalse(result["reusable"])
        self.assertIs(entry._original_failure, failure)
        self.assertIs(entry._original_batch, owner)

    def test_generated_entry_has_fixed_isolation_input_and_readonly_runtime_checks(self):
        source = observer_entry_source()
        compile(source, "synthetic-observer-entry", "exec")
        for literal in (
            b"sys.flags.no_site",
            b"sys.flags.isolated",
            b"sys.flags.dont_write_bytecode",
            b"os.environ",
            b"os.ST_RDONLY",
            b"0o555",
            b"os.O_NOFOLLOW",
            b"/run/crewshal-phase2d-input-v1/batch.json",
        ):
            self.assertIn(literal, source)
        self.assertNotIn(b"importlib", source)
        self.assertNotIn(b"subprocess", source)

    def test_writable_or_nonroot_plan_refuses_before_parsing_or_execution(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "plan.json"
            path.write_bytes(b'{"execution_allowed":true}')
            path.chmod(0o400)
            with self.assertRaisesRegex(ValueError, "immutable bytes"):
                read_frozen_inputs(str(path))

    def test_symlink_plan_refuses_before_opening_its_target(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "plan.json"
            path.write_bytes(b"{}")
            alias = Path(directory) / "alias"
            alias.symlink_to(path)
            with self.assertRaises(OSError):
                read_frozen_inputs(str(alias))

    def test_main_refuses_nonisolated_offline_startup_before_reading_plan(self):
        from crewshal import linux_batch_entry as entry

        with patch.object(entry, "read_frozen_inputs", side_effect=AssertionError("no plan read")):
            with self.assertRaises(ValueError):
                entry.main()


class FrozenBatchAssemblyTests(unittest.TestCase):
    def setUp(self):
        self.build_fixture = build_fixtures.BootstrapBuildClosure()
        self.build_fixture.setUp()
        self.addCleanup(self.build_fixture.doCleanups)
        self.subscription = subscription_fixtures.SubscriptionPreparation()
        self.subscription.setUp()
        self.addCleanup(self.subscription.doCleanups)
        installation = self.build_fixture.f.initial
        inventory = installation.inventory.model_copy(deep=True)
        raw = {
            "/bin/python3": b"Synthetic Python 3.12 bytes.",
            "/input/check_fixture.py": CHECK_SOURCE,
            "/input/fixture.crt": b"Synthetic certificate bytes.",
            "/input/fixture.key": b"Synthetic private fixture key bytes.",
            "/lib/libzstd.so": b"Synthetic zstd bytes.",
            "/usr/sbin/ip": b"Synthetic ip bytes.",
            "/usr/sbin/nft": b"Synthetic nft bytes.",
        }
        for name in SOURCE_FILES:
            raw["/opt/crewshal/lib/crewshal/" + name] = (
                Path(__file__).parents[2] / "src/crewshal" / name
            ).read_bytes()
        for name, data in raw.items():
            inventory.root[name] = RootEntry(kind="file", mode=0o555, sha256=digest(data))
            for parent in Path(name).parents:
                inventory.root[str(parent)] = RootEntry(kind="directory", mode=0o755)
        inventory.root["/usr/sbin/mkfs.ext4"] = RootEntry(
            kind="file", mode=0o555, sha256=installation.formatter_sha256
        )
        inventory.entry_kind = "python"
        inventory.entry_path = "/opt/crewshal/lib/crewshal/linux_parent_entry.py"
        inventory.parent_argv = ["/bin/python3", "-I", "-S", "-B", inventory.entry_path]
        selection = PreparationSelection.model_validate(
            {
                **self.subscription.selection.model_dump(),
                "destination": "https://chatgpt.com/backend-api/codex",
            }
        )
        profile = self.subscription.profile.model_copy(update={"expected_account_id": None})
        profile = profile.model_copy(deep=True)
        profile.expected_config["model_providers"]["openai"]["base_url"] = selection.destination
        draft = prepare_dispatch_configuration(
            selection,
            preparation_digest="1" * 64,
            linux_envelope=installation.configuration.linux_envelope.model_copy(
                update={"context": record_digest(selection)}
            ),
            app_server_profile=profile,
        )
        self.installation = installation.model_copy(
            update={
                "inventory": inventory,
                "sources": {
                    **installation.sources,
                    "/usr/sbin/mkfs.ext4": installation.formatter,
                },
                "configuration": draft,
                "helper_build": self.build_fixture.build,
                "early_timer": FrozenEarlyTimerRuntime(
                    interpreter="/prepared/python3.12",
                    interpreter_sha256="2" * 64,
                    files={"/prepared/python3.12": "2" * 64},
                ),
            }
        )
        self.task = Task(
            id="phase2d-task",
            requirement=REQUIREMENT,
            review_required=False,
            independent_provider=False,
            checks=[
                CheckDefinition(
                    id="exact-bytes",
                    argv=draft.validator_argv,
                    cwd=".",
                    environment=digest(b""),
                    toolchain=validator_toolchain_digest(inventory, draft.validator_argv),
                )
            ],
        )
        self.networks = ProviderNetworkPlan(
            configuration_source="3" * 64,
            ip_binary=digest(raw["/usr/sbin/ip"]),
            nft_binary=digest(raw["/usr/sbin/nft"]),
            host_table="crewshal_abcd1234",
            endpoints={"chatgpt.com": ["1.1.1.1"]},
            qualification_transport="original_two_lane_tls_v1",
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
        fixture = qualification_fixtures._plan().model_copy(update={"model": selection.model})
        self.tls = FrozenQualificationTLS(
            fixture=fixture,
            certificate_sha256=digest(raw["/input/fixture.crt"]),
            private_key_sha256=digest(raw["/input/fixture.key"]),
            zstd_library_sha256=digest(raw["/lib/libzstd.so"]),
            listener_addresses={
                lane.lane_id: (lane.host_address, 443) for lane in self.networks.lanes[:2]
            },
            peer_addresses={lane.lane_id: lane.private_address for lane in self.networks.lanes[:2]},
            bootstrap_replies={
                "/backend-api/codex/models?client_version=0.160.1": '{"models":[]}',
                "/backend-api/wham/usage": '{"synthetic":true}',
            },
        )
        self.qualification = QualificationIdentity(
            host_os="linux",
            host_kernel="synthetic-kernel",
            architecture="aarch64",
            substrate="direct-linux",
            substrate_version="synthetic-version",
            image="4" * 64,
            runtime="codex-rust-v0.160.1",
            toolchain="5" * 64,
            configuration="6" * 64,
            grant="7" * 64,
            harness="8" * 64,
            manifest=PROTOCOL_SHA256,
            credential_design="9" * 64,
        )
        self.project = ProjectModel(project_id="a" * 64, inputs=[], facts=[], notices=[])

    def assemble(self):
        return assemble_frozen_batch(
            self.installation,
            self.networks,
            self.tls,
            self.qualification,
            self.project,
            self.task,
            policy_sha256="b" * 64,
            run_id="phase2d-run",
            attempt_id="phase2d-attempt",
            decisions=OwnerDecisionProposal(
                owner="Synthetic owner",
                implementation_id="proposal-implementation",
                implementation_reason="Synthetic implementation decision proposal.",
                frozen_id="proposal-frozen",
                frozen_reason="Synthetic conditional frozen decision proposal.",
            ),
            certificate_path="/input/fixture.crt",
            private_key_path="/input/fixture.key",
            zstd_path="/lib/libzstd.so",
            one_use_parent="/prepared/markers",
            lease_token="synthetic-lease",
        )

    def test_missing_formatter_refuses_offline_before_any_process(self):
        del self.installation.inventory.root["/usr/sbin/mkfs.ext4"]
        with patch("subprocess.Popen", side_effect=AssertionError("no process")):
            with self.assertRaisesRegex(ValueError, "same original executable formatter"):
                self.assemble()

    def test_formatter_alias_missing_source_and_different_hash_refuse_offline(self):
        original = self.installation.model_copy(deep=True)
        for change in ("alias", "mode", "hash", "source"):
            self.installation = original.model_copy(deep=True)
            entry = self.installation.inventory.root["/usr/sbin/mkfs.ext4"]
            if change == "alias":
                entry.kind, entry.target, entry.sha256 = "symlink", "/other", None
            elif change == "mode":
                entry.mode = 0o444
            elif change == "hash":
                entry.sha256 = "f" * 64
            else:
                self.installation.sources["/usr/sbin/mkfs.ext4"] = "/other"
            with (
                self.subTest(change=change),
                self.assertRaisesRegex(ValueError, "same original executable formatter"),
            ):
                self.assemble()

    def test_frozen_batch_readback_rechecks_formatter_source_binding(self):
        batch = self.assemble().model_dump(mode="json")
        batch["installation"]["sources"]["/usr/sbin/mkfs.ext4"] = "/other"
        with self.assertRaisesRegex(ValueError, "same original executable formatter"):
            FrozenBatchInputs.model_validate_json(json.dumps(batch))

    def test_offline_assembly_joins_actual_supplied_fields_without_execution(self):
        with patch("subprocess.Popen", side_effect=AssertionError("no process")):
            result = self.assemble()
        self.assertEqual(result.run.binding.task, record_digest(self.task))
        self.assertEqual(result.installation.configuration.launch_binding, result.run.binding)
        self.assertIsNone(result.installation.configuration.app_server_profile.expected_account_id)
        self.assertEqual(result.qualification.manifest, current_qualification_manifest())
        self.assertEqual(
            result.authentication.configuration_source, result.networks.configuration_source
        )
        self.assertEqual(FrozenBatchInputs.model_validate_json(result.model_dump_json()), result)
        self.assertFalse(result.installation.configuration.execution_allowed)
        self.assertEqual(self.qualification.manifest, PROTOCOL_SHA256)

    def test_changed_tool_hash_task_scope_or_approval_cannot_cross_the_complete_input_gate(self):
        result = self.assemble()
        for mutate in (
            lambda p: p["networks"].update(ip_binary="f" * 64),
            lambda p: p["frozen_approval"].update(run_id="different-run"),
            lambda p: p["run"]["binding"].update(scope="f" * 64),
            lambda p: p["authentication"].update(account_reference="f" * 64),
            lambda p: p["qualification"].update(manifest=PROTOCOL_SHA256),
        ):
            payload = result.model_dump(mode="json")
            mutate(payload)
            with self.assertRaises(ValueError):
                FrozenBatchInputs.model_validate_json(json.dumps(payload))

    def test_changed_installed_package_source_and_unknown_extra_auth_fields_refuse(self):
        result = self.assemble()
        payload = result.model_dump(mode="json")
        payload["installation"]["inventory"]["root"][
            "/opt/crewshal/lib/crewshal/linux_parent_entry.py"
        ]["sha256"] = "f" * 64
        with self.assertRaisesRegex(ValueError, "package source"):
            FrozenBatchInputs.model_validate_json(json.dumps(payload))
        payload = result.model_dump(mode="json")
        payload["authentication"]["credential_file"] = "/home/owner/auth.json"
        with self.assertRaises(ValueError):
            FrozenBatchInputs.model_validate_json(json.dumps(payload))

    def test_source_manifest_preserves_protocol_and_detects_probe_source_change(self):
        baseline = current_qualification_manifest()
        self.assertNotEqual(baseline, PROTOCOL_SHA256)
        with patch(
            "crewshal.linux_batch_entry.qualification_probe_source", return_value=b"changed"
        ):
            self.assertNotEqual(current_qualification_manifest(), baseline)
