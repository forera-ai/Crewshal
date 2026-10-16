"""Fresh charge and role FD fixtures. Kernel and terminal readbacks are synthetic."""

import copy
import pickle
import time
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

from crewshal import linux_schedule as schedule
from crewshal import linux_setup as setup
from crewshal.contracts import record_digest
from crewshal.durable import CoordinatorStore
from crewshal.linux_bridge import ValidatorBridgeCustody
from crewshal.qualification import (
    MANDATORY_CASES,
    ProbeResult,
    Qualification,
    QualificationIdentity,
)
from tests.acceptance import test_phase_2d_setup as fixtures


class Phase2DThreeLaneSchedule(unittest.TestCase):
    def setUp(self):
        fixture = fixtures.Phase2DSetup()
        fixture.setUp()
        self.addCleanup(fixture.doCleanups)
        fixture.external_observer()
        self.fixture = fixture
        self.store = CoordinatorStore(fixture.f.root / "schedule-journal")
        self.addCleanup(self.store.close)
        self.reservation = setup.reserve_storage_installation(
            self.store,
            fixture.parent,
            fixture.observer_group,
            fixture.aggregate,
            fixture.configuration,
            batch_started_monotonic=time.monotonic() - 1,
        )
        groups = {}
        for lane_id in schedule.LANE_IDS:
            roles = {}
            for name in ("setup", "supervisor", "worker", "validator"):
                basename = name + "--" + lane_id
                directory = fixture.f.aggregate_path / basename
                directory.mkdir()
                group = fixture.f.group(
                    directory,
                    "owned.slice/session.scope/" + basename,
                    name in ("setup", "supervisor"),
                )
                directory.joinpath("cgroup.procs").write_text("")
                directory.joinpath("cgroup.events").write_text("populated 0\nfrozen 0\n")
                roles[name] = group
            groups[lane_id] = roles
        self.contexts = setup.reserve_lane_setups(self.reservation, groups)
        first = self.contexts[0]
        self.timer = setup.OwnedBatchTimer(
            self.reservation,
            first.setup,
            first.supervisor,
            first.worker,
            validator=first.validator,
            lanes=self.contexts,
        )
        self.timer.task = fixture.bridge.watchdog.task
        observer_path = fixture.f.aggregate_path / "observer"
        observer_path.joinpath("cgroup.procs").write_text(
            f"{fixture.parent.spec.pid}\n{self.timer.task.spec.pid}\n"
        )
        # The fixture retains real role FDs and a real irreversible SQLite charge.
        # It supplies no actual helper, namespace, process, mount, or installed observation.
        self.timer_readback = patch.object(setup.OwnedBatchTimer, "verify", autospec=True)
        self.timer_readback.start()
        self.addCleanup(self.timer_readback.stop)
        self.configurations = tuple(context.configuration for context in self.contexts)
        self.identities = tuple(
            QualificationIdentity(
                host_os="linux",
                host_kernel="synthetic-kernel",
                architecture="synthetic-architecture",
                substrate="direct-linux",
                substrate_version="synthetic-version",
                image="a" * 64,
                runtime="synthetic-runtime",
                toolchain="b" * 64,
                configuration=record_digest(configuration),
                grant="c" * 64,
                harness="d" * 64,
                manifest="e" * 64,
                credential_design="f" * 64,
            )
            for configuration in self.configurations
        )
        self.owner = schedule.OwnedThreeLaneSchedule(
            self.reservation, self.timer, self.contexts, self.identities
        )

    def qualification(self, index, **changes):
        values = {
            "id": "fresh-qualification-" + str(index),
            "identity": self.identities[index],
            "results": [
                ProbeResult(case=case, status="passed", observation="Synthetic fixture only.")
                for case in MANDATORY_CASES
            ],
        }
        values.update(changes)
        return Qualification(**values)

    def bind(self, index):
        context = self.contexts[index]
        self.owner.activate(context)
        lifetime = setup.OwnedNamespaceSetup(
            None,
            self.fixture.controls,
            self.fixture.aggregate,
            context.setup,
            context.supervisor,
            context.worker,
            self.fixture.observer_group,
        )
        lifetime.storage_reservation = self.reservation
        lifetime.lane_context = context
        for name in ("setup", "supervisor", "worker", "validator"):
            setattr(lifetime, name, getattr(context, name))
        self.owner.bind_lifetime(context, lifetime)
        custody = object.__new__(ValidatorBridgeCustody)
        custody.bridge = SimpleNamespace(lifetime=lifetime)
        return custody

    def test_active_lifetime_remains_usable_without_permitting_a_second_birth(self):
        custody = self.bind(0)
        context = self.contexts[0]
        self.owner.require_active(context, lifetime=custody.bridge.lifetime)
        with self.assertRaisesRegex(ValueError, "consumed"):
            self.owner.require_active(context)
        with self.assertRaisesRegex(ValueError, "missing or already consumed"):
            self.owner.require_active(context, lifetime=object())
        self.assertIs(self.owner._lifetimes[0], custody.bridge.lifetime)

    def test_another_lifetime_cannot_select_the_active_lane_custody(self):
        custody = self.bind(0)
        lifetime = custody.bridge.lifetime
        changed = copy.copy(lifetime)
        with self.assertRaisesRegex(ValueError, "missing or already consumed"):
            self.owner.require_active(self.contexts[0], lifetime=changed)
        self.assertIs(self.owner._lifetimes[0], lifetime)

    def finish(self, index, qualification=None):
        custody = self.bind(index)
        with patch.object(schedule, "_verify_terminal", autospec=True) as readback:
            self.owner.finish(self.contexts[index], custody, qualification)
        readback.assert_called_once_with(self.contexts[index], custody)
        return custody

    def test_two_complete_distinct_records_precede_one_live_slot(self):
        first = self.qualification(0)
        second = self.qualification(1)
        self.finish(0, first)
        self.finish(1, second)
        self.finish(2)
        self.assertEqual(self.owner._next, 3)
        self.assertIs(self.owner._qualifications[0], first)
        self.assertIs(self.owner._qualifications[1], second)
        self.assertEqual(self.reservation.capacity_claim.record.logical_bytes, 8589934592)
        self.assertEqual(self.reservation.capacity_claim.record.allocated_bytes, 8589934592)
        self.assertEqual(self.timer.cutoff_ns - self.timer.origin_ns, 570_000_000_000)
        self.assertEqual(self.timer.end_ns - self.timer.origin_ns, 600_000_000_000)
        with self.assertRaisesRegex(ValueError, "one-shot"):
            self.owner.activate(self.contexts[2])

    def test_activation_is_sequential_and_needs_terminal_readback(self):
        with self.assertRaisesRegex(ValueError, "sequential"):
            self.owner.activate(self.contexts[2])
        self.bind(0)
        with self.assertRaisesRegex(ValueError, "sequential"):
            self.owner.activate(self.contexts[1])

    def test_terminal_unknown_retains_custody_and_denies_retry(self):
        custody = self.bind(0)
        with patch.object(schedule, "_verify_terminal", side_effect=ValueError("unknown")):
            with self.assertRaisesRegex(ValueError, "unknown"):
                self.owner.finish(self.contexts[0], custody, self.qualification(0))
        self.assertIs(self.owner._custodies[0], custody)
        with self.assertRaises(ValueError):
            self.owner.finish(self.contexts[0], custody, self.qualification(0))
        with self.assertRaises(ValueError):
            self.owner.activate(self.contexts[1])

    def test_missing_case_denies_the_second_lane_and_burns_result(self):
        record = self.qualification(0)
        record.results.pop()
        custody = self.bind(0)
        with patch.object(schedule, "_verify_terminal"):
            with self.assertRaisesRegex(ValueError, "incomplete"):
                self.owner.finish(self.contexts[0], custody, record)
        with self.assertRaises(ValueError):
            self.owner.activate(self.contexts[1])

    def test_a_readiness_flag_cannot_replace_qualification_or_terminal_custody(self):
        custody = self.bind(0)
        with self.assertRaisesRegex(ValueError, "custody"):
            self.owner.finish(self.contexts[0], True, self.qualification(0))
        with patch.object(schedule, "_verify_terminal"):
            with self.assertRaisesRegex(ValueError, "Qualification"):
                self.owner.finish(self.contexts[0], custody, True)

    def test_repeated_result_id_denies_live(self):
        first = self.qualification(0)
        self.finish(0, first)
        custody = self.bind(1)
        second = self.qualification(1, id=first.id)
        with patch.object(schedule, "_verify_terminal"):
            with self.assertRaisesRegex(ValueError, "repeated"):
                self.owner.finish(self.contexts[1], custody, second)
        with self.assertRaises(ValueError):
            self.owner.activate(self.contexts[2])

    def test_configuration_identity_cannot_claim_another_lane(self):
        custody = self.bind(0)
        stale = self.qualification(0, identity=self.identities[1])
        with patch.object(schedule, "_verify_terminal"):
            with self.assertRaisesRegex(ValueError, "stale"):
                self.owner.finish(self.contexts[0], custody, stale)

    def test_changed_retained_record_denies_later_activation(self):
        first = self.qualification(0)
        self.finish(0, first)
        first.results[0].observation = "Changed after terminal custody."
        with self.assertRaisesRegex(ValueError, "qualification changed"):
            self.owner.activate(self.contexts[1])

    def test_different_transport_cannot_share_a_profile(self):
        changed = self.configurations[1].model_copy(update={"native_stdin": "changed transport"})
        self.contexts[1]._configuration = changed
        with self.assertRaisesRegex(ValueError, "configuration identity"):
            self.owner.verify()

    def test_schedule_cannot_be_copied_reconstructed_or_replaced(self):
        for copier in (copy.copy, copy.deepcopy, pickle.dumps):
            with self.assertRaises(TypeError):
                copier(self.owner)
        replacement = object.__new__(schedule.OwnedThreeLaneSchedule)
        replacement.__dict__.update(self.owner.__dict__)
        with self.assertRaises(ValueError):
            replacement.verify()
        with self.assertRaisesRegex(ValueError, "replacement"):
            schedule.OwnedThreeLaneSchedule(
                self.reservation, self.timer, self.contexts, self.identities
            )

    def test_role_alias_and_timer_replacement_fail(self):
        self.contexts[1].worker = self.contexts[0].worker
        with self.assertRaises(ValueError):
            self.owner.verify()

    def test_original_timer_failure_denies_activation(self):
        with patch.object(setup.OwnedBatchTimer, "verify", side_effect=ValueError("expired")):
            with self.assertRaisesRegex(ValueError, "expired"):
                self.owner.activate(self.contexts[0])

    def test_replaced_lifetime_and_repeated_binding_fail(self):
        custody = self.bind(0)
        with self.assertRaises(ValueError):
            self.owner.bind_lifetime(self.contexts[0], custody.bridge.lifetime)
        custody.bridge.lifetime = object.__new__(setup.OwnedNamespaceSetup)
        with self.assertRaisesRegex(ValueError, "custody"):
            self.owner.finish(self.contexts[0], custody, self.qualification(0))

    def terminal_fixture(self):
        custody = self.bind(0)
        bridge = custody.bridge
        bridge.failed = False
        bridge._validator_custody = custody
        custody._parent_finish_sent = True
        record = SimpleNamespace(model_dump_json=lambda: "synthetic-record")
        observation = SimpleNamespace(exit_code=0, model_dump_json=lambda: "synthetic-observation")
        custody.captured = custody._captured_owner = SimpleNamespace(
            stdout=b"fixture",
            stderr=b"",
            observation=observation,
            initial=record,
            final=record,
            overflow=False,
            stop_error=False,
        )
        custody._capture_record = (
            b"fixture",
            b"",
            "synthetic-observation",
            "synthetic-record",
            "synthetic-record",
            False,
            False,
        )
        bridge.lifetime.wrapper = SimpleNamespace(poll=lambda: 0)
        bridge._verify_capture_data = Mock()
        tasks = [
            SimpleNamespace(pidfd=index, verify_handles=Mock(), verify_exited=Mock())
            for index in range(20, 25)
        ]
        bridge.parent, bridge.native, bridge.watchdog, custody.proc, custody.watchdog = tasks
        bridge.host_proc = 99
        return custody

    def test_terminal_reads_all_five_reaped_tasks_and_actual_empty_role_fixtures(self):
        custody = self.terminal_fixture()
        with (
            patch.object(
                schedule, "_wait_ready", side_effect=lambda readers, *args: (readers, [], [])
            ),
            patch.object(schedule, "_read", return_value=b"Pid: -1\n") as kernel_readback,
        ):
            schedule._verify_terminal(self.contexts[0], custody)
        self.assertEqual(kernel_readback.call_count, 5)
        custody.bridge._verify_capture_data.assert_called_once()

    def test_terminal_refuses_live_parent_before_another_lane(self):
        custody = self.terminal_fixture()
        custody.bridge.lifetime.wrapper = SimpleNamespace(poll=lambda: None)
        with self.assertRaisesRegex(ValueError, "parent exit"):
            schedule._verify_terminal(self.contexts[0], custody)

    def test_terminal_refuses_actual_role_population_after_synthetic_positive_reap(self):
        custody = self.terminal_fixture()
        directory = self.fixture.f.aggregate_path / "worker--qualification-1"
        directory.joinpath("cgroup.procs").write_text("12345")
        directory.joinpath("cgroup.events").write_text("populated 1\nfrozen 0\n")
        with (
            patch.object(
                schedule, "_wait_ready", side_effect=lambda readers, *args: (readers, [], [])
            ),
            patch.object(schedule, "_read", return_value=b"Pid: -1\n"),
            self.assertRaisesRegex(ValueError, "role terminal"),
        ):
            schedule._verify_terminal(self.contexts[0], custody)

    def test_terminal_refuses_validator_capture_change_after_parent_exit(self):
        custody = self.terminal_fixture()
        custody.captured.stdout = b"changed"
        with self.assertRaisesRegex(ValueError, "capture changed"):
            schedule._verify_terminal(self.contexts[0], custody)


if __name__ == "__main__":
    unittest.main()
