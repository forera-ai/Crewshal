"""Fresh passive Linux envelope preparation; no kernel or startup claims."""

from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from crewshal.contracts import Binding, CheckDefinition, Task, record_digest
from crewshal.dispatch import prepare_dispatch_configuration
from crewshal.linux_envelope import (
    LinuxEnvelopeBindings,
    LinuxEnvelopePreparation,
    audit_linux_envelope,
    prepare_linux_envelope,
)
from crewshal.model import digest
from crewshal.runtime_batch import PreparationSelection


class Phase2DEnvelope(unittest.TestCase):
    def setUp(self):
        self.selection = PreparationSelection(project="fresh", session="one", model="test-model")
        self.task = Task(
            id="task",
            requirement="fresh inert task",
            checks=[
                CheckDefinition(
                    id="bytes",
                    argv=[
                        "/bin/python3",
                        "-I",
                        "-B",
                        "/input/check_fixture.py",
                        "/candidate/owned",
                    ],
                    cwd=".",
                    environment=digest(b"empty"),
                    toolchain=digest(b"toolchain"),
                )
            ],
        )
        self.binding = Binding(
            model=digest(b"model"),
            task=record_digest(self.task),
            policy=digest(b"policy"),
            candidate=digest(b"candidate"),
            scope=digest(b"scope"),
        )
        self.inputs = LinuxEnvelopeBindings(context=record_digest(self.selection))
        self.configuration = self.compile()

    def replace(self, value, **changes):
        return type(value).model_validate({**value.model_dump(), **changes})

    def compile(self, **changes):
        arguments = dict(task=self.task, binding=self.binding, linux_envelope=self.inputs)
        arguments.update(changes)
        return prepare_dispatch_configuration(self.selection, **arguments)

    def test_preparation_has_no_startup_network_signal_or_repository_writes(self):
        with tempfile.TemporaryDirectory() as directory:
            original = Path(directory) / "dirty"
            original.write_bytes(b"original dirty bytes\n")
            with (
                patch("subprocess.Popen", side_effect=AssertionError("no startup")),
                patch("socket.socket", side_effect=AssertionError("no network")),
                patch("os.kill", side_effect=AssertionError("no signal")),
            ):
                plan = prepare_linux_envelope(self.configuration)
                audit_linux_envelope(self.configuration, plan)
            self.assertEqual(original.read_bytes(), b"original dirty bytes\n")
        self.assertFalse(plan.execution_allowed)
        self.assertFalse(plan.spend_authorized)
        self.assertFalse(plan.profile_qualified)
        self.assertFalse(plan.bootstrap_implemented)

    def test_unresolved_route_stays_missing_and_bootstrap_never_becomes_ready(self):
        plan = prepare_linux_envelope(self.configuration)
        self.assertIsNone(plan.broker_argv)
        self.assertIn("provider", plan.unresolved)
        self.assertIn("destination", plan.unresolved)
        self.assertIn("bootstrap_implementation_and_stopped_checkpoint", plan.unresolved)
        self.assertIn("owned_admission_failure_recovery", plan.unresolved)
        self.assertIn("effective_controls_and_exact_qualification", plan.unresolved)

    def test_original_worker_aggregate_validator_and_broker_ceilings(self):
        plan = prepare_linux_envelope(self.configuration)
        for role in ("worker", "validator"):
            controls = plan.unit_properties[role]
            for key, value in {
                "MemoryMax": "134217728",
                "MemorySwapMax": "0",
                "TasksMax": "32",
                "CPUQuota": "100%",
                "CPUQuotaPeriodSec": "100ms",
                "RuntimeMaxSec": "5s",
                "TimeoutStopSec": "1s",
                "KillMode": "control-group",
                "Restart": "no",
            }.items():
                self.assertEqual(controls[key], value)
        self.assertEqual(plan.unit_properties["supervisor"]["MemoryMax"], "805306368")
        self.assertEqual(plan.unit_properties["supervisor"]["TasksMax"], "128")
        self.assertEqual(plan.unit_properties["supervisor"]["RuntimeMaxSec"], "570s")
        self.assertEqual(plan.unit_properties["supervisor"]["TimeoutStopSec"], "30s")
        self.assertEqual(plan.unit_properties["broker"]["MemoryMax"], "67108864")
        self.assertEqual(plan.unit_properties["broker"]["TasksMax"], "16")
        self.assertIn("deadline_origin_and_manager_readback", plan.unresolved)

    def test_native_mount_and_role_fragments_never_include_original_or_credentials(self):
        plan = prepare_linux_envelope(self.configuration)
        argv = plan.native_argv
        self.assertEqual(argv[0], "/usr/bin/bwrap")
        self.assertEqual(
            argv[-len(self.configuration.native_argv) :], self.configuration.native_argv
        )
        self.assertIn("--clearenv", argv)
        self.assertIn("--no-new-privs", argv)
        self.assertIn("--reuid=65534", argv)
        self.assertEqual(argv[argv.index("--chdir") + 1], "/scratch/checkout")
        self.assertIn("--bounding-set=-all", argv)
        self.assertNotIn("--unshare-net", argv)  # Requires the already-private mediated network.
        self.assertIn("private_network_namespace_and_actor_egress", plan.unresolved)
        for path in ("/original", "/coordinator", "/root", "/home", "/run/docker.sock"):
            self.assertNotIn(path, argv)
        mounts = plan.mounts["native"]
        self.assertEqual(
            {m.target for m in mounts if not m.readonly}, {"/candidate/owned", "/scratch"}
        )
        self.assertIn("native_tool_role_policy_and_transport_denial", plan.unresolved)

    def test_validator_has_readonly_independent_candidate_empty_environment_and_no_network(self):
        plan = prepare_linux_envelope(self.configuration)
        self.assertIn("--unshare-net", plan.validator_argv)
        self.assertIn("--reuid=65531", plan.validator_argv)
        self.assertNotIn("--setenv", plan.validator_argv)
        self.assertEqual(
            plan.validator_argv[plan.validator_argv.index("--chdir") + 1], "/candidate/owned"
        )
        self.assertEqual(
            plan.validator_argv[-len(self.configuration.validator_argv) :],
            self.configuration.validator_argv,
        )
        mounts = plan.mounts["validator"]
        candidate = next(m for m in mounts if m.target == "/candidate/owned")
        self.assertTrue(candidate.readonly)
        self.assertTrue(candidate.source.endswith("/validator-candidate"))
        self.assertNotEqual(
            candidate.source,
            next(m.source for m in plan.mounts["native"] if m.target == "/candidate/owned"),
        )
        self.assertIn("independent_validator_freeze_and_readback", plan.unresolved)

    def test_broker_keeps_token_outside_argv_environment_and_worker_mounts(self):
        selection = self.replace(
            self.selection,
            provider="synthetic",
            destination="https://provider.invalid/v1/responses",
            billing_mode="api_metered",
            credential_treatment="external_scoped_channel",
        )
        inputs = self.replace(self.inputs, context=record_digest(selection))
        configuration = prepare_dispatch_configuration(
            selection, task=self.task, binding=self.binding, linux_envelope=inputs
        )
        plan = prepare_linux_envelope(configuration)
        self.assertIn("--reuid=65533", plan.broker_argv)
        self.assertEqual(
            plan.broker_argv[-len(configuration.proxy_argv) :], configuration.proxy_argv
        )
        self.assertFalse(any(not m.readonly for m in plan.mounts["broker"]))
        self.assertEqual(plan.credential_input, "separate_broker_stdin")
        self.assertNotIn("--setenv", plan.broker_argv)
        self.assertIn("credential_caller_separation_and_upstream_readback", plan.unresolved)
        self.assertIn("financial_enforcement_or_explicit_nonhard_exposure", plan.unresolved)

    def test_storage_counts_every_owned_representation_but_never_claims_enforcement(self):
        plan = prepare_linux_envelope(self.configuration)
        self.assertEqual(plan.storage_reservations["candidate_each_representation"], 16777216)
        self.assertEqual(plan.storage_reservations["scratch_each_representation"], 33554432)
        self.assertEqual(plan.storage_reservations["candidate_representations"], 3)
        self.assertEqual(plan.storage_reservations["scratch_representations"], 3)
        self.assertEqual(plan.reserved_disk_bytes, 1358954496)
        self.assertLessEqual(plan.reserved_disk_bytes, 8589934592)
        self.assertEqual(plan.storage_mechanism, "private_keyring_ext4_ecryptfs")
        for name in (
            "storage_logical_allocated_alias_and_deleted_open",
            "private_keyring_loop_mount_and_role_readback",
        ):
            self.assertIn(name, plan.unresolved)

    def test_bootstrap_preserves_exact_admission_contract_without_ptrace_or_wrapper_assumptions(
        self,
    ):
        plan = prepare_linux_envelope(self.configuration)
        self.assertEqual(plan.checkpoint.state, "T")
        self.assertEqual(plan.checkpoint.tracer_pid, 0)
        self.assertEqual(plan.checkpoint.threads, 1)
        self.assertEqual(plan.checkpoint.child_fds, [0, 1, 2])
        self.assertEqual(plan.checkpoint.worker_direct_processes, 1)
        self.assertEqual(plan.checkpoint.parent_handle, "native_subprocess_popen")
        self.assertEqual(plan.checkpoint.deadline_origin, "before_worker_start")
        self.assertIn("native_exec_identity_before_any_native_instruction", plan.unresolved)

    def test_complete_prospective_hashes_supply_no_observation_or_authority(self):
        filled = {
            name: digest(name.encode())
            for name in type(self.inputs).model_fields
            if name.endswith("_sha256")
        }
        configuration = self.compile(linux_envelope=self.replace(self.inputs, **filled))
        plan = prepare_linux_envelope(configuration)
        audit_linux_envelope(configuration, plan)
        self.assertFalse(plan.bootstrap_implemented)
        self.assertIn("bootstrap_implementation_and_stopped_checkpoint", plan.unresolved)
        self.assertIn("effective_controls_and_exact_qualification", plan.unresolved)
        self.assertIn("separate_owner_execution_and_spend_gate", plan.unresolved)

    def test_changed_context_cannot_transfer_envelope_between_project_or_session(self):
        for field in ("project", "session", "model"):
            with self.subTest(field=field), self.assertRaisesRegex(ValueError, "context"):
                prepare_dispatch_configuration(
                    self.replace(self.selection, **{field: "other"}), linux_envelope=self.inputs
                )

    def test_each_binding_changes_prospective_dispatch_and_refuses_old_plan(self):
        plan = prepare_linux_envelope(self.configuration)
        for field in type(self.inputs).model_fields:
            if not field.endswith("_sha256"):
                continue
            changed = self.compile(
                linux_envelope=self.replace(self.inputs, **{field: digest(field.encode())})
            )
            with self.subTest(field=field):
                self.assertNotEqual(record_digest(changed), record_digest(self.configuration))
                with self.assertRaises(ValueError):
                    audit_linux_envelope(changed, plan)

    def test_changed_source_invalidates_envelope_and_dispatch(self):
        from crewshal.qualification_bundle import _Reader

        original = _Reader.read

        def changed(reader, name):
            data = original(reader, name)
            return data + b"\n# changed envelope\n" if name == "linux_envelope.py" else data

        plan = prepare_linux_envelope(self.configuration)
        self.assertIn("linux_envelope.py", self.configuration.source_sha256)
        with patch("crewshal.dispatch._Reader.read", changed):
            with self.assertRaisesRegex(ValueError, "current source"):
                audit_linux_envelope(self.configuration, plan)

    def test_altered_plan_controls_mounts_role_argv_and_pending_checks_refuse(self):
        plan = prepare_linux_envelope(self.configuration)
        variants = {
            "native_argv": ["/bin/sh", "-c", "true"],
            "validator_argv": ["/bin/true"],
            "unit_properties": {**plan.unit_properties, "worker": {"MemoryMax": "max"}},
            "mounts": {**plan.mounts, "native": []},
            "unresolved": [],
            "storage_reservations": {"prepared": 1},
        }
        for field, value in variants.items():
            with self.subTest(field=field), self.assertRaises(ValueError):
                audit_linux_envelope(self.configuration, self.replace(plan, **{field: value}))

    def test_false_flags_unknown_fields_and_missing_bindings_refuse(self):
        plan = prepare_linux_envelope(self.configuration)
        for field in (
            "execution_allowed",
            "spend_authorized",
            "profile_qualified",
            "bootstrap_implemented",
        ):
            with self.subTest(field=field), self.assertRaises(ValueError):
                self.replace(plan, **{field: True})
        with self.assertRaises(ValueError):
            self.replace(self.inputs, token="synthetic-secret")
        with self.assertRaises(ValueError):
            self.replace(plan, systemd_readback={"passed": True})
        with self.assertRaisesRegex(ValueError, "bindings"):
            prepare_linux_envelope(self.compile(linux_envelope=None))

    def test_canonical_roundtrip_and_mutable_input_copies(self):
        plan = prepare_linux_envelope(self.configuration)
        restored = LinuxEnvelopePreparation.model_validate_json(plan.model_dump_json())
        self.assertEqual(record_digest(restored), record_digest(plan))
        audit_linux_envelope(self.configuration, restored)
        self.inputs.root_inventory_sha256 = digest(b"later mutation")
        self.assertIsNone(self.configuration.linux_envelope.root_inventory_sha256)
        self.assertIsNone(plan.bindings.root_inventory_sha256)

    def test_source_readback_keeps_envelope_bindings_through_admission(self):
        from crewshal.admission import _current_source

        _current_source(self.configuration)
        plan = prepare_linux_envelope(self.configuration)
        changed = self.replace(self.configuration, native_environment={"HOME": "/host"})
        with self.assertRaises(ValueError):
            _current_source(changed)
        with self.assertRaises(ValueError):
            audit_linux_envelope(changed, plan)

    def test_source_bound_dispatch_join_accepts_only_fresh_exact_envelope_data(self):
        from tests.acceptance.test_phase_2d_dispatch import Phase2DDispatch

        fixture = Phase2DDispatch()
        fixture.setUp()
        self.addCleanup(fixture.doCleanups)
        inputs = LinuxEnvelopeBindings(context=record_digest(fixture.selection))
        fixture.configuration = fixture.compile(linux_envelope=inputs)
        fingerprint = record_digest(fixture.configuration)
        fixture.identity = fixture.replace(fixture.identity, configuration=fingerprint)
        fixture.qualified_identity = fixture.replace(
            fixture.qualified_identity, configuration=fingerprint
        )
        fixture.qualification = fixture.replace(
            fixture.qualification, identity=fixture.qualified_identity
        )
        prepared = fixture.prepare()
        plan = prepare_linux_envelope(prepared.configuration)
        self.assertFalse(prepared.execution_allowed)
        self.assertFalse(plan.profile_qualified)
        altered = fixture.replace(
            prepared.configuration,
            linux_envelope=self.replace(inputs, deadline_policy_sha256=digest(b"changed")),
        )
        with self.assertRaises(ValueError):
            fixture.prepare(configuration=altered)
        with self.assertRaises(ValueError):
            audit_linux_envelope(altered, plan)

    def test_task_check_binding_change_requires_new_envelope_and_preserves_old_snapshot(self):
        plan = prepare_linux_envelope(self.configuration)
        task = self.replace(
            self.task, checks=[self.replace(self.task.checks[0], environment=digest(b"other"))]
        )
        changed = self.compile(
            task=task, binding=self.replace(self.binding, task=record_digest(task))
        )
        self.assertNotEqual(record_digest(changed), record_digest(self.configuration))
        with self.assertRaises(ValueError):
            audit_linux_envelope(changed, plan)
        audit_linux_envelope(self.configuration, plan)


if __name__ == "__main__":
    unittest.main()
