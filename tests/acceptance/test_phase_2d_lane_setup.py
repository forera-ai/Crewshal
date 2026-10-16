"""Use fresh retained FDs. Linux role and timer observations are synthetic."""

import os
import pickle
import time
import unittest
from unittest.mock import patch

from crewshal import linux_setup as setup
from crewshal.contracts import record_digest
from tests.acceptance import test_phase_2d_setup as fixtures


class Phase2DLaneSetup(unittest.TestCase):
    def setUp(self):
        self.f = fixtures.Phase2DSetup()
        self.f.setUp()
        self.addCleanup(self.f.doCleanups)
        self.f.external_observer()
        origin = time.monotonic() - 1
        claim = fixtures.synthetic_capacity_claim(
            self, self.f.f.root, self.f.parent, self.f.configuration, origin
        )
        self.reservation = setup.OwnedStorageReservation(
            self.f.parent,
            self.f.observer_group,
            self.f.aggregate,
            self.f.configuration,
            batch_started_monotonic=origin,
            capacity_claim=claim,
        )
        self.groups = {}
        for lane in setup.LANE_IDS:
            roles = {}
            for role in setup.LANE_ROLES:
                name = role + "--" + lane
                path = self.f.f.aggregate_path / name
                path.mkdir()
                group = self.f.f.group(
                    path, "owned.slice/session.scope/" + name, role in ("setup", "supervisor")
                )
                path.joinpath("cgroup.procs").write_text("")
                path.joinpath("cgroup.events").write_text("populated 0\nfrozen 0\n")
                roles[role] = group
            self.groups[lane] = roles

    def reserve(self):
        return setup.reserve_lane_setups(self.reservation, self.groups)

    def test_exact_three_slots_keep_original_charge_origin_and_owner(self):
        contexts = self.reserve()
        self.assertIs(self.reservation._lane_contexts, contexts)
        self.assertEqual(tuple(context.lane_id for context in contexts), setup.LANE_IDS)
        self.assertEqual(self.reservation.charges, setup.StorageCharges())
        self.assertIs(self.f.parent._storage_reservation, self.reservation)
        for context in contexts:
            context.verify_handles()
            self.assertIs(context.reservation, self.reservation)
            self.assertEqual(context.configuration.lane_id, context.lane_id)
            payload = context.configuration.model_dump(mode="json")
            payload.pop("lane_id")
            original = self.f.configuration.model_dump(mode="json")
            original.pop("lane_id")
            self.assertEqual(payload, original)
            self.assertEqual(record_digest(context.configuration), context._configuration_digest)

    def test_repeated_declaration_consumes_no_new_slots(self):
        contexts = self.reserve()
        with self.assertRaises(ValueError):
            self.reserve()
        self.assertIs(self.reservation._lane_contexts, contexts)

    def test_role_readback_refusal_retains_all_original_handles(self):
        group = self.groups["qualification-2"]["setup"]
        with patch.object(group, "_verify", side_effect=ValueError("synthetic refusal")):
            with self.assertRaisesRegex(ValueError, "synthetic refusal"):
                self.reserve()
        contexts = self.reservation._lane_contexts
        self.assertEqual(len(contexts), 3)
        for context in contexts:
            for role in setup.LANE_ROLES:
                original = self.groups[context.lane_id][role]
                self.assertIs(getattr(context, role), original)
                os.fstat(original.descriptor)
        with self.assertRaises(ValueError):
            self.reserve()

    def test_shared_role_is_refused_and_retained(self):
        original = self.groups["qualification-1"]["worker"]
        self.groups["live"]["worker"] = original
        with self.assertRaisesRegex(ValueError, "not disjoint"):
            self.reserve()
        self.assertIs(self.reservation._lane_contexts[2].worker, original)

    def test_context_replacement_and_configuration_change_are_refused(self):
        contexts = self.reserve()
        context = contexts[0]
        original = context._configuration
        context._configuration = original.model_copy(update={"lane_id": "live"})
        with self.assertRaises(ValueError):
            context.verify_handles()
        context._configuration = original
        self.reservation._lane_contexts = tuple(list(contexts))
        with self.assertRaises(ValueError):
            context.verify_handles()

    def test_timer_pins_all_twelve_original_groups_and_one_deadline(self):
        contexts = self.reserve()
        first = contexts[0]
        timer = setup.OwnedBatchTimer(
            self.reservation,
            first.setup,
            first.supervisor,
            first.worker,
            validator=first.validator,
            lanes=contexts,
        )
        self.assertEqual(len(timer.operational_groups), 12)
        self.assertEqual(len({id(group) for group in timer.operational_groups}), 12)
        self.assertEqual(timer.cutoff_ns, timer.origin_ns + 570_000_000_000)
        self.assertEqual(timer.end_ns, timer.origin_ns + 600_000_000_000)
        for context in contexts:
            self.assertIs(context.timer, timer)
        timer._verify_validator()

    def test_context_cannot_be_exported_or_constructed(self):
        contexts = self.reserve()
        with self.assertRaises(ValueError):
            setup.RetainedLaneSetup()
        with self.assertRaises(TypeError):
            pickle.dumps(contexts[0])

    def test_singular_namespace_path_cannot_use_declared_lanes(self):
        self.reserve()
        with patch.object(setup.subprocess, "Popen") as birth:
            with self.assertRaisesRegex(ValueError, "exact active context"):
                setup.create_namespace_setup(
                    self.f.parent,
                    self.f.observer_group,
                    self.f.aggregate,
                    self.f.setup_group,
                    self.f.supervisor,
                    self.f.worker,
                    self.f.configuration,
                    self.f.preparation,
                    self.f.plan,
                    storage_reservation=self.reservation,
                )
            birth.assert_not_called()

    def test_inactive_lane_cannot_create_wrapper(self):
        context = self.reserve()[0]
        with patch.object(setup.subprocess, "Popen") as birth:
            with self.assertRaisesRegex(ValueError, "unused active lane"):
                setup.create_namespace_setup(
                    self.f.parent,
                    self.f.observer_group,
                    self.f.aggregate,
                    context.setup,
                    context.supervisor,
                    context.worker,
                    context.configuration,
                    self.f.preparation,
                    self.f.plan,
                    storage_reservation=self.reservation,
                    validator=context.validator,
                    lane_context=context,
                )
            birth.assert_not_called()
