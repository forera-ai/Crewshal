"""Fresh storage-owner seam; all mounts/keyrings/loops/pidfds remain synthetic."""

from contextlib import ExitStack
import os
import time
import unittest
from unittest.mock import patch

from crewshal import linux_setup as setup
from crewshal import linux_teardown as teardown
from crewshal.admission import NamespaceIdentity
from crewshal.contracts import record_digest
from crewshal.linux_envelope import prepare_linux_envelope
from tests.acceptance import test_phase_2d_setup as setup_fixtures


class SyntheticPhysicalOwner:
    def __init__(self, fixture):
        self.f = fixture
        self.calls = []
        self.failure = None
        self.omit_effect = None
        self.after = None
        path = fixture.f.root / "backing.ext4"
        path.write_bytes(b"fresh synthetic ext4 backing")
        self.path = path
        info = path.stat()
        backing = teardown.FileIdentity(device=info.st_dev, inode=info.st_ino)
        namespace = fixture.parent.spec.namespaces["mnt"]
        root = prepare_linux_envelope(fixture.configuration).owned_root
        self.state = teardown.PhysicalState(
            namespace=namespace,
            mounts={
                "upper": teardown.MountIdentity(
                    mount_id=101,
                    parent_id=1,
                    target=root + "/candidate-upper",
                    filesystem="ecryptfs",
                    device="0:41",
                ),
                "lower": teardown.MountIdentity(
                    mount_id=100,
                    parent_id=1,
                    target=root + "/backing-mount",
                    filesystem="ext4",
                    device="7:0",
                ),
            },
            private_keyring=4567,
            keyring_state="present",
            loops={
                "loop": teardown.LoopIdentity(
                    device=teardown.FileIdentity(device=1, inode=99),
                    rdev=1792,
                    backing=backing,
                    backing_name=path.name,
                    size_limit=33554432,
                )
            },
            backing={path.name: backing},
            extra_mount_aliases=0,
            extra_open_holders=0,
        )

    def readback(self):
        observed = self.state.model_copy(deep=True)
        for name in self.state.backing:
            info = self.path.with_name(name).stat()
            observed.backing[name] = teardown.FileIdentity(device=info.st_dev, inode=info.st_ino)
        return observed

    def effect(self, name, operation):
        self.calls.append(name)
        if self.failure == name:
            raise OSError("synthetic physical release refusal")
        if self.omit_effect != name:
            operation()
        if self.after:
            self.after(name)

    def unmount(self, mount, deadline):
        name = next(name for name, item in self.state.mounts.items() if item == mount)
        self.effect("unmount:" + name, lambda: self.state.mounts.pop(name))

    def revoke_private_keyring(self, serial, deadline):
        if serial != self.state.private_keyring:
            raise ValueError("synthetic private keyring differs")
        self.effect("keyring", lambda: setattr(self.state, "keyring_state", "revoked"))

    def detach_loop(self, loop, deadline):
        self.effect("loop", lambda: self.state.loops.pop("loop"))

    def remove_backing(self, name, identity, deadline):
        def remove():
            info = self.path.stat()
            if (info.st_dev, info.st_ino) != (identity.device, identity.inode):
                raise ValueError("synthetic pinned backing leaf replaced")
            self.path.unlink()
            self.state.backing.pop(name)

        self.effect("backing", remove)


class Phase2DTeardown(unittest.TestCase):
    def setUp(self):
        fixture = setup_fixtures.Phase2DSetup()
        fixture.setUp()
        self.addCleanup(fixture.doCleanups)
        self.f = fixture
        terminal = setup.terminal_namespace_setup

        def capture(*args, **kwargs):
            self.terminal_args = args
            return terminal(*args, **kwargs)

        with patch.object(setup, "terminal_namespace_setup", side_effect=capture):
            self.lifetime, result, _ = fixture.external_terminal()
        self.assertTrue(result.groups_empty)
        _, self.observer, self.parent, self.watchdog = self.terminal_args
        self.owner = SyntheticPhysicalOwner(fixture)
        self.namespace = os.open(fixture.f.root / "namespace-mnt", os.O_RDONLY)
        self.backing_fd = os.open(self.owner.path, os.O_RDONLY)
        self.addCleanup(os.close, self.namespace)
        self.addCleanup(self.close_original_backing)
        self.resources = self.retain()
        self.close_original_backing()

    def close_original_backing(self):
        if self.backing_fd >= 0:
            os.close(self.backing_fd)
            self.backing_fd = -1

    def retain(self, **changes):
        values = dict(
            lifetime=self.lifetime,
            owner=self.owner,
            namespace_fd=self.namespace,
            storage_fds={self.owner.path.name: self.backing_fd},
            unmount_order=["upper", "lower"],
            batch_started_monotonic=time.monotonic() - 2,
        )
        values.update(changes)
        resource = teardown.OwnedPhysicalResources(**values)
        self.addCleanup(self.cleanup_private_handles, resource)
        return resource

    def cleanup_private_handles(self, resource):
        # Only known remaining private descriptors. A one-shot failed source
        # keeps these for explicit fixture cleanup, never operational retry.
        for handle in resource.descriptors.values():
            os.close(handle)
        resource.descriptors.clear()

    def run_teardown(self, *, terminal_ready=True, remove_group=True):
        original_rmdir = os.rmdir
        group_paths = {
            "worker": self.f.f.worker_path,
            "supervisor": self.f.supervisor_path,
            "setup": self.f.setup_path,
        }

        def rmdir(name, *, dir_fd):
            self.owner.calls.append("group:" + name)
            if not remove_group:
                raise OSError("synthetic cgroup release refusal")
            # Kernel cgroup pseudo-files vanish with rmdir. Model that effect
            # using only these independently built temporary fixture files.
            for child in group_paths[name].iterdir():
                child.unlink()
            original_rmdir(name, dir_fd=dir_fd)

        with ExitStack() as stack:
            stack.enter_context(
                patch.object(setup, "_terminal_task_exited", return_value=terminal_ready)
            )
            stack.enter_context(
                patch.object(teardown, "_terminal_task_exited", return_value=terminal_ready)
            )
            stack.enter_context(patch.object(teardown.os, "rmdir", side_effect=rmdir))
            return teardown.teardown_owned_physical_resources(
                self.resources, self.observer, self.parent, self.watchdog
            )

    def test_concrete_owner_deadline_never_restarts_cleanup_reserve(self):
        self.owner.cleanup_deadline = time.monotonic() + 2
        result = self.run_teardown()
        self.assertTrue(result.physical_released)
        self.assertEqual(self.resources.cleanup_deadline, self.owner.cleanup_deadline)

    def test_unknown_owner_deadline_retains_resources_without_effect(self):
        self.owner.cleanup_deadline = float("nan")
        result = self.run_teardown()
        self.assertFalse(result.physical_released)
        self.assertEqual(self.owner.calls, [])
        self.assertTrue(self.resources.descriptors)

    def test_owned_release_order_and_observer_aggregate_retained(self):
        aggregate_fd = self.lifetime.aggregate.descriptor
        observer_fd = self.lifetime.observer_group.descriptor
        result = self.run_teardown()
        self.assertEqual(
            self.owner.calls,
            [
                "unmount:upper",
                "unmount:lower",
                "keyring",
                "loop",
                "backing",
                "group:worker",
                "group:supervisor",
                "group:setup",
            ],
        )
        self.assertTrue(result.physical_released)
        self.assertTrue(result.handles_released)
        self.assertEqual(result.errors, ())
        self.assertFalse(result.resources_reusable)
        self.assertFalse(self.owner.path.exists())
        os.fstat(aggregate_fd)
        os.fstat(observer_fd)
        self.observer.verify(self.lifetime.observer_group.identity)

    def test_surviving_watchdog_blocks_every_physical_effect(self):
        result = self.run_teardown(terminal_ready=False)
        self.assertTrue(result.errors)
        self.assertEqual(self.owner.calls, [])
        self.assertTrue(self.owner.path.exists())
        self.resources._verify_handles()

    def test_missing_wrapper_reap_blocks_every_physical_effect(self):
        self.lifetime.wrapper.result = None
        result = self.run_teardown()
        self.assertEqual(self.owner.calls, [])
        self.assertFalse(result.physical_released)

    def test_process_emptiness_with_unknown_physical_holders_refused(self):
        self.owner.state.extra_open_holders = None
        result = self.run_teardown()
        self.assertTrue(result.errors)
        self.assertEqual(self.owner.calls, [])

    def test_namespace_substitution_blocks_effects(self):
        self.owner.state.namespace = NamespaceIdentity(device=999, inode=999)
        result = self.run_teardown()
        self.assertTrue(result.errors)
        self.assertEqual(self.owner.calls, [])

    def test_operation_success_without_readback_stops_later_releases(self):
        self.owner.omit_effect = "unmount:upper"
        result = self.run_teardown()
        self.assertEqual(self.owner.calls, ["unmount:upper"])
        self.assertFalse(result.physical_released)
        self.resources._verify_handles()

    def test_partial_mount_failure_retains_keys_loops_backing_and_fds(self):
        self.owner.failure = "unmount:lower"
        result = self.run_teardown()
        self.assertEqual(self.owner.calls, ["unmount:upper", "unmount:lower"])
        self.assertEqual(self.owner.state.keyring_state, "present")
        self.assertTrue(self.owner.state.loops)
        self.assertTrue(self.owner.path.exists())
        self.resources._verify_handles()
        self.assertFalse(result.resources_reusable)

    def test_key_revoke_unknown_prevents_loop_detach(self):
        self.owner.after = (
            lambda name: setattr(self.owner.state, "keyring_state", "unknown")
            if name == "keyring"
            else None
        )
        result = self.run_teardown()
        self.assertEqual(self.owner.calls, ["unmount:upper", "unmount:lower", "keyring"])
        self.assertTrue(result.errors)
        self.assertTrue(self.owner.state.loops)

    def test_loop_detach_unknown_prevents_backing_unlink(self):
        self.owner.omit_effect = "loop"
        result = self.run_teardown()
        self.assertNotIn("backing", self.owner.calls)
        self.assertTrue(result.errors)
        self.assertTrue(self.owner.path.exists())

    def test_backing_fd_closed_before_unlink_and_not_reused(self):
        descriptor = self.resources.descriptors["backing:" + self.owner.path.name]
        observed = []

        def check(name):
            if name == "backing":
                with self.assertRaises(OSError):
                    os.fstat(descriptor)
                observed.append(name)

        self.owner.after = check
        result = self.run_teardown()
        self.assertEqual(observed, ["backing"])
        self.assertTrue(result.physical_released)

    def test_cgroup_removal_failure_keeps_identity_handles_and_observer(self):
        result = self.run_teardown(remove_group=False)
        self.assertTrue(result.physical_released)
        self.assertFalse(result.handles_released)
        self.assertEqual(result.roles_released, ())
        os.fstat(self.lifetime.worker.descriptor)
        os.fstat(self.resources.namespace_fd)
        self.observer.verify(self.lifetime.observer_group.identity)

    def test_repeated_failed_teardown_has_no_retry_or_grace_reset(self):
        self.owner.failure = "unmount:upper"
        first = self.run_teardown()
        deadline = self.resources.cleanup_deadline
        recovery = self.lifetime.recovery_deadline
        calls = list(self.owner.calls)
        second = self.run_teardown()
        self.assertEqual(second.errors, first.errors)
        self.assertEqual(self.owner.calls, calls)
        self.assertEqual(self.resources.cleanup_deadline, deadline)
        self.assertEqual(self.lifetime.recovery_deadline, recovery)

    def test_success_never_allows_retry_or_resource_reuse(self):
        first = self.run_teardown()
        second = self.run_teardown()
        self.assertTrue(first.physical_released)
        self.assertFalse(second.physical_released)
        self.assertFalse(first.resources_reusable)
        self.assertFalse(second.resources_reusable)

    def test_expired_original_batch_stops_without_effects(self):
        self.resources.batch_started = time.monotonic() - 601
        result = self.run_teardown()
        self.assertEqual(self.owner.calls, [])
        self.assertIn("deadline exhausted", result.errors[0])

    def test_changed_retained_inventory_and_configuration_refused(self):
        self.resources.state.private_keyring += 1
        result = self.run_teardown()
        self.assertEqual(self.owner.calls, [])
        self.assertIn("inventory", result.errors[0])

    def test_fd_substitution_does_not_close_unrelated_file(self):
        unrelated = self.f.f.root / "unrelated-dirty"
        unrelated.write_bytes(b"preserve original bytes")
        handle = os.open(unrelated, os.O_RDONLY)
        try:
            os.dup2(handle, self.resources.namespace_fd)
        finally:
            os.close(handle)
        result = self.run_teardown()
        self.assertEqual(self.owner.calls, [])
        os.fstat(self.resources.namespace_fd)
        self.assertEqual(unrelated.read_bytes(), b"preserve original bytes")
        self.assertTrue(result.errors)

    def test_child_mount_order_and_owned_path_admission(self):
        for change in (
            dict(unmount_order=["lower", "upper"]),
            dict(unmount_order=["upper", "upper"]),
        ):
            with self.subTest(change=change), self.assertRaises(ValueError):
                self.retain(**change)
        self.owner.state.mounts["upper"].target = "/unrelated-host-mount"
        with self.assertRaisesRegex(ValueError, "owned session root"):
            self.retain()

    def test_new_alias_appearing_after_unmount_blocks_next_step(self):
        self.owner.after = (
            lambda name: setattr(self.owner.state, "extra_mount_aliases", 1)
            if name == "unmount:upper"
            else None
        )
        result = self.run_teardown()
        self.assertEqual(self.owner.calls, ["unmount:upper"])
        self.assertTrue(result.errors)

    def test_failed_worker_cleanup_never_reaches_storage_owner(self):
        self.lifetime.worker._read("cgroup.events")
        self.f.f.worker_path.joinpath("cgroup.events").write_text("populated 1\nfrozen 0")
        self.f.f.worker_path.joinpath("cgroup.procs").write_text("12345")
        result = self.run_teardown()
        self.assertEqual(self.owner.calls, [])
        self.assertFalse(result.physical_released)

    def test_storage_change_after_physical_release_blocks_group_closure(self):
        def reappear(name):
            if name == "backing":
                self.owner.state.extra_open_holders = 1

        self.owner.after = reappear
        result = self.run_teardown()
        self.assertNotIn("group:worker", self.owner.calls)
        self.assertFalse(result.handles_released)

    def test_new_origin_nan_and_unknown_keyring_admission_refused(self):
        for origin in (float("nan"), float("inf"), time.monotonic() + 10):
            with self.subTest(origin=origin), self.assertRaisesRegex(ValueError, "batch origin"):
                self.retain(batch_started_monotonic=origin)
        self.owner.state.keyring_state = "unknown"
        with self.assertRaisesRegex(ValueError, "complete owned physical inventory"):
            self.retain()

    def test_initial_resource_snapshot_not_mutated_by_owner_readback(self):
        original = record_digest(self.resources.state)
        self.owner.state.keyring_state = "revoked"
        self.assertEqual(record_digest(self.resources.state), original)
        result = self.run_teardown()
        self.assertTrue(result.errors)
        self.assertEqual(self.owner.calls, [])

    def test_second_retention_cannot_reconstruct_failed_cleanup(self):
        self.owner.failure = "unmount:upper"
        result = self.run_teardown()
        self.assertTrue(result.errors)
        with self.assertRaisesRegex(ValueError, "no reconstruction"):
            self.retain()

    def test_two_retained_owners_cannot_retry_same_namespace(self):
        handle = os.open(self.owner.path, os.O_RDONLY)
        try:
            second = self.retain(storage_fds={self.owner.path.name: handle})
        finally:
            os.close(handle)
        self.owner.failure = "unmount:upper"
        self.run_teardown()
        calls = list(self.owner.calls)
        result = teardown.teardown_owned_physical_resources(
            second, self.observer, self.parent, self.watchdog
        )
        self.assertEqual(self.owner.calls, calls)
        self.assertTrue(result.errors)

    def test_backing_replacement_prevents_unlink_and_group_release(self):
        replacement = self.owner.path.with_name("replacement")
        replacement.write_bytes(b"unrelated replacement bytes")

        def replace_backing(name):
            if name == "loop":
                os.replace(replacement, self.owner.path)

        self.owner.after = replace_backing
        result = self.run_teardown()
        self.assertNotIn("backing", self.owner.calls)
        self.assertTrue(result.errors)
        self.assertEqual(self.owner.path.read_bytes(), b"unrelated replacement bytes")

    def test_changed_configuration_refused_before_physical_effect(self):
        self.lifetime.controls.configuration.native_stdin += "different task"
        result = self.run_teardown()
        self.assertEqual(self.owner.calls, [])
        self.assertIn("configuration changed", result.errors[0])
