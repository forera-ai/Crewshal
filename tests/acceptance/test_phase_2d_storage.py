"""Current fresh owner fixtures; never fork, join a keyring or enter a namespace."""

from contextlib import ExitStack
import errno
import os
import signal
import stat
from types import SimpleNamespace
import time
import unittest
from unittest.mock import Mock, patch

from crewshal import linux_storage as storage
from crewshal.contracts import record_digest
from crewshal.linux_envelope import prepare_linux_envelope, LinuxEnvelopeBindings
from crewshal.dispatch import prepare_dispatch_configuration
from tests.acceptance import test_phase_2d_dispatch as dispatch_fixtures


class InlineJobs:
    """Explicit synthetic bounded-child seam; exercise source parsers/readbacks."""

    def __init__(self, configuration):
        self.deadline = time.monotonic() + 20
        self.observer = SimpleNamespace(
            spec=SimpleNamespace(configuration=record_digest(configuration), boot_id="fixture-only")
        )
        self.calls = []

    def run(self, action, keep):
        self.calls.append(keep)
        return action()


class Phase2DStorage(unittest.TestCase):
    def setUp(self):
        fixture = dispatch_fixtures.Phase2DDispatch()
        fixture.setUp()
        self.addCleanup(fixture.doCleanups)
        fixture.configuration = prepare_dispatch_configuration(
            fixture.selection,
            task=fixture.task,
            binding=fixture.binding,
            linux_envelope=LinuxEnvelopeBindings(context=record_digest(fixture.selection)),
        )
        self.f = fixture
        self.root = fixture.root / "storage"
        self.root.mkdir(mode=0o700)
        self.backing = self.root / "backing.ext4"
        self.backing.write_bytes(b"new independent backing bytes")
        self.namespace = self.root / "namespace"
        self.namespace.write_bytes(b"synthetic namespace inode")
        self.loop = self.root / "loop"
        self.loop.write_bytes(b"synthetic loop node")
        self.proc = self.root / "proc"
        (self.proc / "self" / "ns").mkdir(parents=True)
        (self.proc / "self" / "ns" / "mnt").symlink_to(self.namespace)
        owned = prepare_linux_envelope(fixture.configuration).owned_root
        self.targets = {"upper": owned + "/candidate-upper", "lower": owned + "/lower"}
        self.rows = (
            f"1 1 0:1 / / rw - rootfs rootfs rw\n"
            f"101 1 0:41 / {self.targets['upper']} rw - ecryptfs /lower rw\n"
            f"100 1 7:0 / {self.targets['lower']} rw - ext4 /dev/loop0 rw\n"
        )
        self.mountinfo = self.proc / "self" / "mountinfo"
        self.mountinfo.write_text(self.rows)
        self.fds = {}
        for name, path in {
            "directory": self.root,
            "backing": self.backing,
            "namespace": self.namespace,
            "loop": self.loop,
        }.items():
            self.fds[name] = os.open(path, os.O_RDONLY)
            self.addCleanup(os.close, self.fds[name])
        self.original_fstat = os.fstat
        self.loop_identity = storage._identity(self.fds["loop"])
        self.directory_identity = storage._identity(self.fds["directory"])
        self.key = "present"
        self.loop_present = True
        self.loop_changes = {}
        self.calls = []
        self.stack = ExitStack()
        self.addCleanup(self.stack.close)
        self.stack.enter_context(patch.object(storage.os, "fstat", side_effect=self.fstat))
        self.stack.enter_context(
            patch.object(storage.os, "readlink", return_value=owned + "/backing")
        )
        self.stack.enter_context(
            patch.object(
                storage.os,
                "setns",
                create=True,
                side_effect=lambda *args: self.calls.append("setns"),
            )
        )
        self.stack.enter_context(
            patch.object(
                storage, "_proc_root", side_effect=lambda _: os.open(self.proc, os.O_RDONLY)
            )
        )
        self.stack.enter_context(patch.object(storage, "_keyctl", side_effect=self.keyctl))
        self.stack.enter_context(patch.object(storage.fcntl, "ioctl", side_effect=self.ioctl))
        # Guard every forbidden execution path, even if source changes later.
        self.stack.enter_context(
            patch.object(storage.os, "fork", side_effect=AssertionError("real fork forbidden"))
        )
        self.jobs = InlineJobs(fixture.configuration)
        self.ring = storage.AnonymousKeyring.create()
        self.owner = self.retain()
        self.saved_namespace = self.owner.handles["namespace"]
        self.addCleanup(self.close_owner, self.owner)

    def fstat(self, fd):
        info = self.original_fstat(fd)
        values = {name: getattr(info, name) for name in dir(info) if name.startswith("st_")}
        identity = (info.st_dev, info.st_ino)
        if identity == (self.loop_identity.device, self.loop_identity.inode):
            values.update(st_mode=stat.S_IFBLK | 0o600, st_rdev=os.makedev(7, 0))
        if identity == (self.directory_identity.device, self.directory_identity.inode):
            values.update(st_uid=0, st_mode=stat.S_IFDIR | 0o700)
        return SimpleNamespace(**values)

    def keyctl(self, operation, serial=0, buffer=None, size=0):
        self.calls.append(("keyctl", operation, serial))
        if operation == 0:
            return 222
        if operation == 1:
            return 333
        if operation == 3:
            self.key = "revoked"
            return 0
        if self.key != "present":
            raise OSError(128 if self.key == "revoked" else 126, "synthetic key state")
        description = b"keyring;0;0;3f030000;_ses\0"
        buffer.value = description[:-1]
        return len(description)

    def ioctl(self, fd, command, raw, mutate=True):
        self.calls.append(("ioctl", command))
        if command == storage.LOOP_CLR_FD:
            self.loop_present = False
            return 0
        if not self.loop_present:
            raise OSError(errno.ENXIO, "synthetic unbound loop")
        info = self.backing.stat()
        encoded = (
            os.minor(info.st_dev) & 0xFF
            | os.major(info.st_dev) << 8
            | (os.minor(info.st_dev) & ~0xFF) << 12
        )
        values = dict(
            device=encoded,
            inode=info.st_ino,
            rdev=0,
            offset=0,
            size=33554432,
            number=0,
            encryption=0,
            keysize=0,
            flags=0,
        )
        values.update(self.loop_changes)
        raw[:] = storage.LOOP_INFO64.pack(
            *values.values(), b"".ljust(64, b"\0"), b"".ljust(64, b"\0"), b"".ljust(32, b"\0"), 0, 0
        )
        return 0

    def retain(self, **changes):
        arguments = dict(
            configuration=self.f.configuration,
            namespace_fd=self.fds["namespace"],
            directory_fd=self.fds["directory"],
            loop_fds={"loop": self.fds["loop"]},
            backing_fds={self.backing.name: self.fds["backing"]},
            mounts=self.targets,
            ring=self.ring,
            jobs=self.jobs,
            batch_started_monotonic=time.monotonic() - 1,
        )
        arguments.update(changes)
        return storage.LinuxPhysicalOwner(**arguments)

    def close_owner(self, owner):
        for fd in owner.handles.values():
            os.close(fd)
        owner.handles.clear()

    def clear_mounts(self):
        self.mountinfo.write_text(self.rows.splitlines()[0] + "\n")

    def synthetic_closed(self):
        return patch.object(self.owner, "_scan_references", return_value=(0, 0))

    def test_actual_fresh_descriptor_and_parser_readback_stays_unknown(self):
        observed = self.owner.readback()
        self.assertEqual(observed.namespace.inode, self.namespace.stat().st_ino)
        self.assertEqual(observed.mounts["upper"].mount_id, 101)
        self.assertEqual(observed.loops["loop"].backing.inode, self.backing.stat().st_ino)
        self.assertEqual(observed.keyring_state, "present")
        self.assertIsNone(observed.extra_open_holders)
        self.assertIsNone(observed.extra_mount_aliases)

    def test_empty_reference_scan_never_authorizes_effects(self):
        with (
            patch.object(storage.ctypes, "CDLL") as libc,
            self.assertRaisesRegex(ValueError, "closure"),
        ):
            self.owner.unmount(self.owner.initial.mounts["upper"], self.jobs.deadline)
        libc.assert_not_called()

    def test_key_revocation_has_actual_errno_readback(self):
        self.key = "revoked"
        self.assertEqual(self.owner.readback().keyring_state, "revoked")
        self.key = "unknown"
        self.assertEqual(self.owner.readback().keyring_state, "unknown")

    def test_access_denied_missing_expired_never_mean_revoked(self):
        for code in [errno.EACCES, errno.EPERM, 126, 127]:
            with (
                self.subTest(code=code),
                patch.object(storage, "_keyctl", side_effect=OSError(code, "unknown")),
            ):
                self.assertEqual(storage._key_state(333), "unknown")

    def test_key_description_must_be_anonymous_root_ring(self):
        def describe(operation, serial, buffer, size):
            buffer.value = b"keyring;1;0;3f030000;named"
            return len(buffer.value) + 1

        with patch.object(storage, "_keyctl", side_effect=describe), self.assertRaises(ValueError):
            storage._key_state(333)

    def test_private_ring_created_without_named_or_ambient_mutation(self):
        self.assertEqual(self.calls[:3], [("keyctl", 0, -3), ("keyctl", 1, 0), ("keyctl", 6, 333)])
        with self.assertRaises(ValueError):
            storage.AnonymousKeyring()

    def test_unknown_new_ring_keeps_serial_for_audit(self):
        with (
            patch.object(storage, "_key_state", return_value="unknown"),
            self.assertRaises(storage.KeyringCreationRefusal) as caught,
        ):
            storage.AnonymousKeyring.create()
        self.assertEqual(caught.exception.ring.serial, 333)

    def test_private_ring_cannot_be_claimed_twice(self):
        with self.assertRaises(ValueError):
            self.retain()

    def test_mutated_ring_cannot_revoke_foreign_serial(self):
        self.ring.serial = 444
        with self.assertRaisesRegex(ValueError, "keyring"):
            self.owner.readback()

    def test_namespace_descriptor_substitution_refused(self):
        self.owner.handles["namespace"] = self.fds["backing"]
        with self.assertRaises(ValueError):
            self.owner.readback()
        # Avoid closing caller FD in cleanup; restore actual privately held FD.
        self.owner.handles["namespace"] = self.saved_namespace

    def test_mount_replacement_same_target_refused(self):
        self.mountinfo.write_text(self.rows.replace("101 1", "102 1"))
        with self.assertRaises(ValueError):
            self.owner.readback()

    def test_ext4_cannot_use_host_block_device(self):
        self.mountinfo.write_text(self.rows.replace("100 1 7:0", "100 1 8:0"))
        with self.assertRaises(ValueError):
            self.owner.readback()

    def test_loop_identity_mutations_refused(self):
        for changes in [
            dict(offset=1),
            dict(size=0),
            dict(size=8589934593),
            dict(flags=4),
            dict(encryption=1),
            dict(number=1),
            dict(inode=1),
        ]:
            with self.subTest(changes=changes):
                self.loop_changes = changes
                with self.assertRaises(ValueError):
                    self.owner.readback()
        self.loop_changes = {}

    def test_only_enxio_means_loop_unbound(self):
        with (
            patch.object(storage.fcntl, "ioctl", side_effect=OSError(errno.EPERM, "denied")),
            self.assertRaises(OSError),
        ):
            self.owner.readback()
        self.clear_mounts()
        self.loop_present = False
        self.assertEqual(self.owner.readback().loops, {})

    def test_backing_leaf_replacement_and_hardlink_refused(self):
        self.backing.rename(self.backing.with_suffix(".old"))
        self.backing.write_bytes(b"replacement")
        with self.assertRaises(ValueError):
            self.owner.readback()

    def test_backing_hardlink_refused(self):
        os.link(self.backing, self.root / "alias")
        with self.assertRaises(ValueError):
            self.owner.readback()

    def test_deadline_extension_or_shorter_mismatch_refused(self):
        for value in [self.jobs.deadline + 1, self.jobs.deadline - 1, float("nan")]:
            with self.subTest(value=value), self.assertRaises(ValueError):
                self.owner.revoke_private_keyring(333, value)

    def test_any_failed_effect_stops_later_different_effects(self):
        with self.assertRaises(ValueError):
            self.owner.revoke_private_keyring(333, self.jobs.deadline)
        self.clear_mounts()
        with self.synthetic_closed(), self.assertRaises(ValueError):
            self.owner.detach_loop(self.owner.initial.loops["loop"], self.jobs.deadline)
        self.assertTrue(self.loop_present)

    def test_failed_operation_cannot_retry(self):
        for _ in range(2):
            with self.assertRaises(ValueError):
                self.owner.revoke_private_keyring(333, self.jobs.deadline)
        self.assertEqual(self.owner.attempted, {"keyring"})

    def test_mount_effect_uses_no_lazy_or_forced_flag(self):
        libc = Mock()
        libc.umount2.return_value = 0
        with self.synthetic_closed(), patch.object(storage.ctypes, "CDLL", return_value=libc):
            self.owner.unmount(self.owner.initial.mounts["upper"], self.jobs.deadline)
        self.assertEqual(libc.umount2.call_args.args[1].value, 0)
        # Successful syscall does not mutate readback or imply absence.
        self.assertIn("upper", self.owner.readback().mounts)

    def test_key_revocation_requires_no_mounts_and_exact_private_serial(self):
        with self.synthetic_closed(), self.assertRaises(ValueError):
            self.owner.revoke_private_keyring(333, self.jobs.deadline)
        self.assertEqual(self.key, "present")

    def test_synthetic_key_then_loop_then_pinned_leaf_order(self):
        self.clear_mounts()
        with self.synthetic_closed():
            self.owner.revoke_private_keyring(333, self.jobs.deadline)
            self.assertEqual(self.owner.readback().keyring_state, "revoked")
            loop = self.owner.readback().loops["loop"]
            self.owner.detach_loop(loop, self.jobs.deadline)
            self.assertFalse(self.owner.readback().loops)
            # Fixture unlinks only its own temporary backing; production closure
            # remains unknown and cannot reach this path.
            identity = self.owner.backing[self.backing.name]
            self.owner.remove_backing(self.backing.name, identity, self.jobs.deadline)
        self.assertFalse(self.backing.exists())
        self.assertIsNone(self.owner.readback().extra_open_holders)

    def test_loop_cannot_detach_while_key_present(self):
        self.clear_mounts()
        with self.synthetic_closed(), self.assertRaises(ValueError):
            self.owner.detach_loop(self.owner.initial.loops["loop"], self.jobs.deadline)
        self.assertTrue(self.loop_present)

    def test_remove_backing_cannot_escape_directory(self):
        for name in ["../backing.ext4", "/backing.ext4", ".", ""]:
            with self.subTest(name=name), self.assertRaises(ValueError):
                self.owner.remove_backing(
                    name, self.owner.backing[self.backing.name], self.jobs.deadline
                )

    def test_transfer_requires_exact_retained_backing_identity(self):
        with self.assertRaises(ValueError):
            self.owner.bind_backing_handles({self.backing.name: self.fds["namespace"]})
        self.owner.bind_backing_handles({self.backing.name: self.fds["backing"]})

    def test_readback_refusal_retains_private_handles(self):
        ring = storage.AnonymousKeyring.create()
        self.mountinfo.write_text("invalid")
        with self.assertRaises(storage.StorageOwnerRefusal) as caught:
            self.retain(ring=ring)
        owner = caught.exception.owner
        self.assertTrue(owner.handles)
        for fd in owner.handles.values():
            self.original_fstat(fd)
        self.close_owner(owner)

    def test_owned_mount_target_cannot_escape_session_root(self):
        ring = storage.AnonymousKeyring.create()
        with self.assertRaises(ValueError):
            self.retain(ring=ring, mounts={"upper": "/host"})
        self.assertFalse(ring.claimed)

    def test_mount_parser_decodes_only_kernel_escapes(self):
        row = storage.parse_mountinfo(b"5 1 7:0 / /with\\040space rw - ext4 /dev/loop0 rw\n")
        self.assertEqual(row[5][2], "/with space")
        for raw in [
            b"",
            b"5 1 7:0 / /x\\001 rw - ext4 /dev/loop0 rw\n",
            b"5 1 7:0 / /x rw - ext4 /dev/loop0 rw\n" * 2,
            b"x" * 1048577,
        ]:
            with self.subTest(raw=raw[:30]), self.assertRaises(ValueError):
                storage.parse_mountinfo(raw)

    def test_moved_mount_id_does_not_mean_unmounted(self):
        self.mountinfo.write_text(
            self.rows.replace(self.targets["upper"], self.targets["upper"] + "-moved")
        )
        with self.assertRaisesRegex(ValueError, "moved"):
            self.owner.readback()

    def test_retained_cleanup_deadline_cannot_be_mutated(self):
        self.jobs.deadline += 1
        with self.assertRaises(ValueError):
            self.owner.readback()

    def test_mutated_initial_inventory_refused(self):
        self.owner.initial.mounts.clear()
        with self.assertRaises(ValueError):
            self.owner.readback()

    def test_pinned_backing_directory_cannot_target_host_directory(self):
        with (
            patch.object(storage.os, "readlink", return_value="/host/private"),
            self.assertRaises(ValueError),
        ):
            self.owner.readback()

    def test_partial_process_scan_is_unknown(self):
        (self.proc / "998").mkdir()
        self.assertEqual(self.owner._scan_references({os.makedev(7, 0)}), (None, None))

    def test_actual_deleted_open_backing_reference_remains_positive(self):
        process = self.proc / "999"
        (process / "ns").mkdir(parents=True)
        (process / "fd").mkdir()
        (process / "ns" / "mnt").symlink_to(self.namespace)
        (process / "mountinfo").write_text(self.rows)
        stat_fields = ["0"] * 50
        stat_fields[0] = "S"
        stat_fields[1] = "1"
        stat_fields[19] = "123"
        (process / "stat").write_text("999 (synthetic) " + " ".join(stat_fields))
        (process / "maps").write_bytes(b"")
        for name in ["cwd", "root"]:
            (process / name).symlink_to(self.root)
        (process / "fd" / "123").write_bytes(b"synthetic proc inode")
        self.backing.unlink()
        actual_stat = os.stat

        def observe(path, *, dir_fd=None, follow_symlinks=True):
            if path == "123":
                return self.original_fstat(self.fds["backing"])
            return actual_stat(path, dir_fd=dir_fd, follow_symlinks=follow_symlinks)

        with patch.object(storage.os, "stat", side_effect=observe):
            aliases, holders = self.owner._scan_references({os.makedev(7, 0)})
        self.assertIsNone(aliases)
        self.assertEqual(holders, 1)
        self.assertEqual(self.original_fstat(self.fds["backing"]).st_nlink, 0)

    def test_actual_mapped_deleted_reference_is_positive_unknown_not_zero(self):
        process = self.proc / "999"
        (process / "ns").mkdir(parents=True)
        (process / "fd").mkdir()
        (process / "ns" / "mnt").symlink_to(self.namespace)
        (process / "mountinfo").write_text(self.rows)
        stat_fields = ["0"] * 50
        stat_fields[0] = "S"
        stat_fields[1] = "1"
        stat_fields[19] = "123"
        (process / "stat").write_text("999 (synthetic) " + " ".join(stat_fields))
        for name in ["cwd", "root"]:
            (process / name).symlink_to(self.root)
        info = self.backing.stat()
        (process / "maps").write_text(
            f"0-1 rw-p 0 {os.major(info.st_dev):x}:{os.minor(info.st_dev):x} {info.st_ino} /gone (deleted)\n"
        )
        aliases, holders = self.owner._scan_references({os.makedev(7, 0), os.makedev(0, 41)})
        self.assertIsNone(aliases)
        self.assertEqual(holders, 1)


class Phase2DStorageJobs(unittest.TestCase):
    def setUp(self):
        self.observer = SimpleNamespace(spec=SimpleNamespace(pid=os.getpid()), verify=Mock())
        identity = SimpleNamespace(relative_path="crewshal/session/observer")
        self.group = SimpleNamespace(identity=identity, sample=Mock())
        controls = {
            "memory.max": "805306368",
            "memory.swap.max": "0",
            "pids.max": "128",
            "cpu.max": "100000 100000",
        }
        self.aggregate = SimpleNamespace(
            identity=SimpleNamespace(relative_path="crewshal/session"),
            _verify=Mock(),
            _read=lambda name: controls[name],
        )
        self.jobs = storage.BoundedStorageJobs(
            self.observer, self.group, self.aggregate, time.monotonic() + 20
        )
        self.descriptors = set()
        self.addCleanup(self.cleanup)

    def cleanup(self):
        for fd in self.descriptors:
            try:
                os.close(fd)
            except OSError:
                pass

    def test_off_linux_refuses_before_fork(self):
        with (
            patch.object(storage.sys, "platform", "darwin"),
            patch.object(storage.os, "fork") as fork,
            self.assertRaises(ValueError),
        ):
            self.jobs.run(lambda: b"", set())
        fork.assert_not_called()

    def test_existing_pending_child_refuses_retry(self):
        self.jobs.pending = (999, 123)
        with patch.object(storage.os, "fork") as fork, self.assertRaises(ValueError):
            self.jobs.run(lambda: b"", set())
        fork.assert_not_called()

    def test_expired_original_deadline_refuses_before_fork(self):
        self.jobs.deadline = time.monotonic() - 1
        with patch.object(storage.os, "fork") as fork, self.assertRaises(ValueError):
            self.jobs.run(lambda: b"", set())
        fork.assert_not_called()

    def test_role_and_aggregate_ceiling_checked_before_fork(self):
        with (
            patch.object(storage.sys, "platform", "linux"),
            patch.object(storage.os, "pidfd_open", create=True),
            patch.object(storage.signal, "getsignal", return_value=signal.SIG_DFL),
            patch.object(storage.os, "fork") as fork,
        ):
            self.observer.spec.pid = os.getpid() + 1
            with self.assertRaises(ValueError):
                self.jobs.run(lambda: b"", set())
            self.observer.spec.pid = os.getpid()
            self.aggregate._read = lambda name: "unbounded"
            with self.assertRaises(ValueError):
                self.jobs.run(lambda: b"", set())
        fork.assert_not_called()

    def simulate(self, payload=b"+observed", *, timeout=False, terminal=False, pidfd_failure=False):
        actual_pipe = os.pipe
        pairs = []

        def pipe2(flags):
            pair = actual_pipe()
            for fd in pair:
                os.set_blocking(fd, False)
            pairs.append(pair)
            self.descriptors.update(pair)
            return pair

        def fork():
            # Retain a synthetic child copy of the control reader. No child is
            # created; this models inherited pipe ownership in parent transport.
            self.descriptors.add(os.dup(pairs[1][0]))
            os.write(pairs[0][1], payload)
            return 999

        def pidfd(pid, flags):
            if pidfd_failure:
                raise OSError(errno.EMFILE, "synthetic pidfd failure")
            fd = os.open("/dev/null", os.O_RDONLY)
            self.descriptors.add(fd)
            return fd

        def selected(readers, writers, errors, remaining):
            if timeout:
                return [], [], []
            if readers and readers[0] != pairs[0][0] and not terminal:
                return [], [], []
            return readers, writers, []

        with ExitStack() as stack:
            stack.enter_context(patch.object(self.jobs, "_admit"))
            stack.enter_context(patch.object(storage.os, "pipe2", create=True, side_effect=pipe2))
            stack.enter_context(patch.object(storage.os, "fork", side_effect=fork))
            stack.enter_context(
                patch.object(storage.os, "pidfd_open", create=True, side_effect=pidfd)
            )
            stack.enter_context(patch.object(storage.select, "select", side_effect=selected))
            stack.enter_context(patch.object(storage.os, "waitpid", return_value=(999, 0)))
            kill = stack.enter_context(
                patch.object(storage.signal, "pidfd_send_signal", create=True)
            )
            value = self.jobs.run(lambda: b"not executed", set())
            return value, kill

    def test_synthetic_parent_transport_needs_pidfd_and_reaping(self):
        value, _ = self.simulate(terminal=True)
        self.assertEqual(value, b"observed")
        self.assertIsNone(self.jobs.pending)

    def test_timeout_keeps_unreaped_pidfd_and_blocks_later_jobs(self):
        with self.assertRaises(ValueError):
            self.simulate(timeout=True)
        self.assertTrue(self.jobs.failed)
        self.assertIsNotNone(self.jobs.pending)
        os.fstat(self.jobs.pending[1])
        with self.assertRaises(ValueError):
            self.jobs.run(lambda: b"", set())

    def test_unreaped_terminal_transport_is_unknown(self):
        with self.assertRaises(ValueError):
            self.simulate(terminal=False)
        self.assertIsNotNone(self.jobs.pending)

    def test_pidfd_failure_never_falls_back_to_numeric_signal(self):
        with patch.object(storage.os, "kill") as kill, self.assertRaises(OSError):
            self.simulate(pidfd_failure=True)
        kill.assert_not_called()
        self.assertEqual(self.jobs.pending, (999, -1))

    def test_child_unknown_transport_cannot_be_observed_success(self):
        with self.assertRaises(ValueError):
            self.simulate(payload=b"-unknown", terminal=True)
        self.assertTrue(self.jobs.failed)
        self.assertIsNone(self.jobs.pending)
