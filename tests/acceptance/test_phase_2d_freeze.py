"""Ordinary FD-copy fixtures; every Linux process/mount/syscall is synthetic."""

from contextlib import ExitStack
import copy
import os
from pathlib import Path
from types import SimpleNamespace
import tempfile
import unittest
from unittest.mock import Mock, patch

from crewshal.candidate import _scan_fd
from crewshal.linux_freeze import (
    FreezeRefusal,
    OriginalVolumeFreeze,
    _host_handle,
    bind_original_freeze,
)
from crewshal.linux_production import EffectiveInstallation
from crewshal.contracts import record_digest


class Phase2DOriginalVolumeFreeze(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.source = self.root / "candidate"
        self.volume = self.root / "validator-volume"
        self.owned = self.root / "owned"
        for path in (self.source, self.volume, self.owned):
            path.mkdir()
            path.chmod(0o700)
        (self.source / "README.md").write_bytes(b"bounded original bytes\n")
        (self.source / "README.md").chmod(0o600)
        self.fds = []
        self.owner = object.__new__(OriginalVolumeFreeze)
        self.owner.source = self.open_directory(self.source)
        self.owner.volume = self.open_directory(self.volume)
        self.owner.received = []
        self.owner.handles = {}
        self.owner.failed = False
        self.owner.jobs = Mock()
        self.owner.parent = SimpleNamespace(spec=SimpleNamespace(boot_id="fixture"))
        self.owner._verify_terminal_kernel = Mock()
        self.production = SimpleNamespace(
            root=str(self.owned),
            handles={"namespace": -1, "root-parent": self.open_directory(self.owned)},
        )
        self.owner.installation = SimpleNamespace(
            production=self.production,
            reservation=SimpleNamespace(_retain_installation_refusal=Mock()),
        )
        self.sequence = []
        self.transferred = []
        self.owner.transfer = SimpleNamespace(transfer=self.transfer)
        self.addCleanup(self.close_fds)

    def close_fds(self):
        for fd in set(self.fds):
            try:
                os.close(fd)
            except OSError:
                pass

    def open_directory(self, path):
        fd = os.open(path, os.O_RDONLY | os.O_DIRECTORY)
        self.fds.append(fd)
        return fd

    def transfer(self, name, fd):
        self.fds.append(fd)
        retained = os.dup(fd)
        self.fds.append(retained)
        self.owner.received.append(retained)
        self.owner.handles[name] = retained
        self.transferred.append((name, retained))
        self.sequence.append(("custody", name, os.fstat(fd).st_size))

    def synthetic_kernel(self):
        """No mount, namespace, chown, proc or process syscall is executed."""
        stack = ExitStack()
        actual_open = os.open

        def opening(path, flags, mode=0o777, *, dir_fd=None):
            if path == str(self.owned / "validator-frozen"):
                fd = os.dup(self.owner.handles["frozen-root"])
                self.fds.append(fd)
                return fd
            return actual_open(path, flags, mode, dir_fd=dir_fd)

        def bind(source, path, *, remount):
            self.sequence.append(("remount" if remount else "bind", path))

        def proc_read(root, name):
            if name.startswith("self/fdinfo/"):
                return b"mnt_id:\t42\n"
            info = os.fstat(self.owner.handles["frozen-root"])
            return (
                f"42 1 {os.major(info.st_dev)}:{os.minor(info.st_dev)} /frozen "
                f"{self.owned}/validator-frozen ro,nosuid,nodev,noexec - ecryptfs owned ro\n"
            ).encode()

        stack.enter_context(patch("crewshal.linux_freeze._enter_owned_namespace"))
        stack.enter_context(patch("crewshal.linux_freeze._bind_projection", side_effect=bind))
        stack.enter_context(patch("crewshal.linux_freeze.os.open", side_effect=opening))
        stack.enter_context(patch("crewshal.linux_freeze.os.fchown"))
        actual_fstat = os.fstat

        def role_stat(descriptor):
            info = actual_fstat(descriptor)
            if descriptor not in (self.owner.source, self.owner.volume):
                return info
            values = list(info)
            values[4] = values[5] = 65534 if descriptor == self.owner.source else 0
            return os.stat_result(values)

        stack.enter_context(patch("crewshal.linux_freeze.os.fstat", side_effect=role_stat))
        stack.enter_context(patch("crewshal.linux_freeze._filesystem_magic", return_value=0xF15F))
        stack.enter_context(
            patch(
                "crewshal.linux_freeze.os.fstatvfs",
                return_value=SimpleNamespace(f_flag=os.ST_RDONLY),
            )
        )
        stack.enter_context(
            patch(
                "crewshal.linux_freeze._proc_root",
                side_effect=lambda boot: os.dup(self.owner.source),
            )
        )
        stack.enter_context(patch("crewshal.linux_freeze._read", side_effect=proc_read))
        return stack

    def test_actual_fd_copy_preserves_manifest_bytes_and_modes(self):
        (self.source / "nested").mkdir(mode=0o700)
        (self.source / "nested" / "item").write_bytes(b"nested bytes")
        (self.source / "nested" / "item").chmod(0o400)
        initial = _scan_fd(self.owner.source)[0]
        with self.synthetic_kernel():
            raw = self.owner._freeze_child()
        self.assertEqual(_scan_fd(self.owner.handles["frozen-root"])[0], initial)
        self.assertEqual(raw.partition(b"\n")[0], initial.model_dump_json().encode())
        self.assertEqual((self.source / "README.md").read_bytes(), b"bounded original bytes\n")
        self.assertEqual(os.fstat(self.owner.volume).st_mode & 0o777, 0o700)
        self.assertGreaterEqual(self.owner._verify_terminal_kernel.call_count, 2)

    def test_custody_precedes_file_write_and_readonly_remount(self):
        with self.synthetic_kernel():
            self.owner._freeze_child()
        entry = next(item for item in self.sequence if item[:2] == ("custody", "entry:0"))
        self.assertEqual(entry[2], 0)
        names = [item[0:2] for item in self.sequence]
        self.assertLess(
            names.index(("custody", "readonly-projection")),
            names.index(("remount", str(self.owned / "validator-frozen"))),
        )
        self.assertTrue(all(os.fstat(fd).st_ino for _, fd in self.transferred))

    def test_source_symlink_refused_before_creating_frozen_entry(self):
        (self.source / "outside").symlink_to(self.root)
        with self.synthetic_kernel(), self.assertRaises(ValueError):
            self.owner._freeze_child()
        self.assertFalse((self.volume / "frozen").exists())
        self.assertEqual(self.owner.received, [])

    def test_original_inode_cap_refuses_before_copy(self):
        for index in range(61):
            (self.source / f"extra{index}").write_bytes(b"")
        with self.synthetic_kernel(), self.assertRaisesRegex(ValueError, "inode/byte"):
            self.owner._freeze_child()
        self.assertFalse((self.volume / "frozen").exists())

    def test_source_modes_cannot_be_changed_to_claim_readability(self):
        manifest, contents = _scan_fd(self.owner.source)
        unreadable = manifest.model_copy(deep=True)
        unreadable.files[0].mode = 0o200
        with (
            self.synthetic_kernel(),
            patch("crewshal.linux_freeze._scan_fd", return_value=(unreadable, contents)),
            self.assertRaisesRegex(ValueError, "readability"),
        ):
            self.owner._freeze_child()
        self.assertEqual((self.source / "README.md").stat().st_mode & 0o777, 0o600)
        self.assertFalse((self.volume / "frozen").exists())

    def test_copy_failure_retains_partial_original_volume_and_fds(self):
        with (
            self.synthetic_kernel(),
            patch("crewshal.linux_freeze.os.write", side_effect=OSError("synthetic failed write")),
            self.assertRaises(OSError),
        ):
            self.owner._freeze_child()
        self.assertTrue((self.volume / "frozen" / "README.md").exists())
        self.assertEqual((self.volume / "frozen" / "README.md").stat().st_size, 0)
        self.assertEqual(len(self.owner.received), 2)
        self.assertTrue(all(os.fstat(fd).st_ino for fd in self.owner.received))

    def test_original_file_growth_limit_never_raised_for_freeze(self):
        (self.source / "README.md").write_bytes(b"x" * 131073)
        with self.synthetic_kernel(), self.assertRaisesRegex(ValueError, "inherited growth"):
            self.owner._freeze_child()
        self.assertEqual((self.volume / "frozen" / "README.md").stat().st_size, 0)
        self.assertEqual((self.source / "README.md").stat().st_size, 131073)

    def test_mutating_source_during_copy_refuses_retained_partial(self):
        original_transfer = self.transfer

        def changing(name, fd):
            original_transfer(name, fd)
            if name == "entry:0":
                (self.source / "README.md").write_bytes(b"changed original")

        self.owner.transfer.transfer = changing
        with self.synthetic_kernel(), self.assertRaisesRegex(ValueError, "changed during freeze"):
            self.owner._freeze_child()
        self.assertEqual(
            (self.volume / "frozen" / "README.md").read_bytes(), b"bounded original bytes\n"
        )
        self.assertTrue(all(os.fstat(fd).st_ino for fd in self.owner.received))

    def test_unknown_remount_retains_projected_fd_without_cleanup(self):
        with (
            self.synthetic_kernel(),
            patch(
                "crewshal.linux_freeze._bind_projection",
                side_effect=[None, OSError("synthetic unknown remount")],
            ),
            self.assertRaises(OSError),
        ):
            self.owner._freeze_child()
        self.assertIn("readonly-projection", self.owner.handles)
        self.assertTrue((self.volume / "frozen" / "README.md").exists())
        self.assertTrue((self.owned / "validator-frozen").exists())
        os.fstat(self.owner.handles["readonly-projection"])

    def test_missing_native_terminal_prevents_first_copy_effect(self):
        self.owner._verify_terminal_kernel.side_effect = ValueError("synthetic native remains live")
        with self.synthetic_kernel(), self.assertRaises(ValueError):
            self.owner._freeze_child()
        self.assertFalse((self.volume / "frozen").exists())

    def test_existing_frozen_subdirectory_is_never_deleted_or_reused(self):
        (self.volume / "frozen").mkdir()
        (self.volume / "frozen" / "retained").write_bytes(b"unknown retained")
        with self.synthetic_kernel(), self.assertRaises(FileExistsError):
            self.owner._freeze_child()
        self.assertEqual((self.volume / "frozen" / "retained").read_bytes(), b"unknown retained")

    def test_retained_writable_alias_mutation_is_detected_by_actual_readback(self):
        with self.synthetic_kernel():
            raw = self.owner._freeze_child()
            from crewshal.candidate import FrozenCandidate

            self.owner.manifest = FrozenCandidate.model_validate_json(raw.partition(b"\n")[0])
            self.owner._verify_readonly_child()
            entry = self.owner.handles["entry:0"]
            os.pwrite(entry, b"tampered", 0)
            with self.assertRaisesRegex(ValueError, "contents changed"):
                self.owner._verify_readonly_child()
        self.assertTrue(os.fstat(entry).st_ino)

    def test_no_serialized_or_copied_freeze_owner(self):
        with self.assertRaises(ValueError):
            OriginalVolumeFreeze()
        with self.assertRaises(TypeError):
            copy.copy(self.owner)

    def test_bad_binding_consumes_original_attempt_before_effects(self):
        proof = object.__new__(EffectiveInstallation)
        proof.verify = Mock()
        proof.reservation = SimpleNamespace(_retain_installation_refusal=Mock())
        with self.assertRaises(FreezeRefusal) as captured:
            bind_original_freeze(proof, Mock(), Mock(), Mock(), Mock(), (-1, -1, -1))
        retained = getattr(proof, "_freeze")
        self.assertIs(captured.exception.owner, retained)
        self.assertTrue(retained.failed)
        proof.reservation._retain_installation_refusal.assert_called_once()
        with self.assertRaisesRegex(ValueError, "consumed"):
            bind_original_freeze(proof, Mock(), Mock(), Mock(), Mock(), (-1, -1, -1))

    def test_failed_custody_acquisition_cannot_retry_freeze(self):
        del self.owner.transfer
        with (
            patch(
                "crewshal.linux_freeze._FreezeTransfer",
                side_effect=ValueError("synthetic transport failure"),
            ),
            self.assertRaises(FreezeRefusal),
        ):
            self.owner.freeze()
        self.assertTrue(self.owner.failed)
        with self.assertRaisesRegex(FreezeRefusal, "consumed"):
            self.owner.freeze()

    def terminal_fixture(self):
        del self.owner._verify_terminal_kernel
        self.owner.parent = SimpleNamespace(spec=SimpleNamespace(pid=101), verify=Mock())
        self.owner.native = SimpleNamespace(pidfd=18, verify_exited=Mock())
        self.owner.watchdog = SimpleNamespace(pidfd=19, verify_handles=Mock())
        self.worker = SimpleNamespace(
            sample=Mock(return_value=SimpleNamespace(populated=False, direct_pids=[]))
        )
        self.supervisor = SimpleNamespace(identity=object(), _read=Mock(return_value="101"))
        self.owner.lifetime = SimpleNamespace(worker=self.worker, supervisor=self.supervisor)
        self.owner._roots = (
            (os.fstat(self.owner.source).st_dev, os.fstat(self.owner.source).st_ino),
            (os.fstat(self.owner.volume).st_dev, os.fstat(self.owner.volume).st_ino),
        )
        stack = ExitStack()
        self.owner.host_proc = self.owner.source
        stack.enter_context(patch("crewshal.linux_freeze._role_controls"))
        stack.enter_context(patch("crewshal.linux_freeze._read", return_value=b"Pid:\t-1\n"))
        stack.enter_context(
            patch("crewshal.linux_freeze.select.select", return_value=([19], [], []))
        )
        return stack

    def test_terminal_requires_native_watchdog_and_only_original_parent(self):
        with self.terminal_fixture():
            self.owner._verify_terminal_kernel()
        self.assertEqual(self.owner.native.verify_exited.call_count, 2)
        self.assertEqual(self.owner.parent.verify.call_count, 2)
        self.assertEqual(self.owner.watchdog.verify_handles.call_count, 2)

    def test_unknown_watchdog_terminal_refuses_even_with_empty_worker(self):
        with (
            self.terminal_fixture(),
            patch("crewshal.linux_freeze.select.select", return_value=([], [], [])),
            self.assertRaisesRegex(ValueError, "watchdog terminal"),
        ):
            self.owner._verify_terminal_kernel()

    def test_pidfd_exit_without_actual_reap_refuses_freeze(self):
        with self.terminal_fixture():
            for fdinfo in (
                b"Pid:\t202\n",
                b"Pid:\t0\n",
                b"Pid:\t-2\n",
                b"flags:\t02\n",
                b"Pid:\t-1\nPid:\t-1\n",
            ):
                with (
                    self.subTest(fdinfo=fdinfo),
                    patch("crewshal.linux_freeze._read", return_value=fdinfo),
                    self.assertRaises(ValueError),
                ):
                    self.owner._verify_terminal_kernel()

    def test_original_watchdog_reap_must_be_read_independently(self):
        with (
            self.terminal_fixture(),
            patch("crewshal.linux_freeze._read", side_effect=[b"Pid:\t-1\n", b"Pid:\t303\n"]),
            self.assertRaisesRegex(ValueError, "reap remains"),
        ):
            self.owner._verify_terminal_kernel()

    def test_worker_population_or_extra_supervisor_task_refuses_freeze(self):
        with self.terminal_fixture():
            for populated, direct_pids, supervisors in (
                (True, [], "101"),
                (False, [202], "101"),
                (False, [], "101 303"),
            ):
                with self.subTest(
                    populated=populated, direct_pids=direct_pids, supervisors=supervisors
                ):
                    self.worker.sample.return_value = SimpleNamespace(
                        populated=populated, direct_pids=direct_pids
                    )
                    self.supervisor._read.return_value = supervisors
                    with self.assertRaises(ValueError):
                        self.owner._verify_terminal_kernel()

    def test_unknown_native_exit_or_parent_liveness_refuses_terminal(self):
        with self.terminal_fixture():
            self.owner.native.verify_exited.side_effect = ValueError("synthetic unknown native")
            with self.assertRaises(ValueError):
                self.owner._verify_terminal_kernel()
            self.owner.native.verify_exited.side_effect = None
            self.owner.parent.verify.side_effect = ValueError("synthetic parent exited")
            with self.assertRaises(ValueError):
                self.owner._verify_terminal_kernel()

    def test_host_binding_requires_both_actual_proc_inode_and_pidfd_pid(self):
        # This ordinary-directory fixture exercises the identity decoder only;
        # production obtains root through independently verified Linux procfs.
        proc = self.root / "synthetic-proc"
        (proc / "self" / "fdinfo").mkdir(parents=True)
        (proc / "202").mkdir()
        (proc / "self" / "fdinfo" / "9").write_text("Pid:\t202\n")
        root = self.open_directory(proc)
        task = self.open_directory(proc / "202")
        _host_handle(root, task, 9, 202)
        (proc / "self" / "fdinfo" / "9").write_text("Pid:\t303\n")
        with self.assertRaisesRegex(ValueError, "pidfd/proc"):
            _host_handle(root, task, 9, 202)
        (proc / "self" / "fdinfo" / "9").write_text("Pid:\t202\n")
        with self.assertRaisesRegex(ValueError, "host procfs"):
            _host_handle(root, self.owner.source, 9, 202)

    def test_registered_actions_cannot_replay_copy_or_use_arbitrary_callback(self):
        self.owner.verify_registered_job = Mock()
        self.owner._attempted = True
        self.owner.transfer.stage = 0
        self.owner.verify_registered_action(self.owner.jobs, self.owner._freeze_child)
        with self.assertRaises(ValueError):
            self.owner.verify_registered_action(self.owner.jobs, lambda: b"caller")
        self.owner.transfer.stage = 3
        self.owner.manifest = _scan_fd(self.owner.source)[0]
        self.owner.verify_registered_action(self.owner.jobs, self.owner._verify_readonly_child)
        with self.assertRaises(ValueError):
            self.owner.verify_registered_action(self.owner.jobs, self.owner._freeze_child)

    def projection_fixture(self):
        with self.synthetic_kernel():
            raw = self.owner._freeze_child()
        from crewshal.candidate import FrozenCandidate

        self.owner.manifest = FrozenCandidate.model_validate_json(raw.partition(b"\n")[0])
        self.owner.mount_row = raw.partition(b"\n")[2].decode("ascii")
        self.owner._manifest_digest = record_digest(self.owner.manifest)
        self.owner.jobs.run.return_value = self.owner._manifest_digest.encode("ascii")
        self.owner.verify_custody = Mock()
        self.owner.parent.descriptor = self.owner.parent.pidfd = -1
        self.owner.native = SimpleNamespace(descriptor=-1, pidfd=-1)
        self.owner.watchdog = SimpleNamespace(descriptor=-1, pidfd=-1)
        self.owner.lifetime = SimpleNamespace(
            worker=SimpleNamespace(descriptor=-1), supervisor=SimpleNamespace(descriptor=-1)
        )
        self.owner.host_proc = self.owner.source
        stack = self.synthetic_kernel()
        actual_fstat = os.fstat
        projection = self.owner.handles["readonly-projection"]

        def actual_projection(fd):
            info = actual_fstat(fd)
            if fd != projection:
                return info
            values = list(info)
            values[4] = values[5] = 65531
            return os.stat_result(values)

        stack.enter_context(patch("crewshal.linux_freeze.os.fstat", side_effect=actual_projection))
        return stack

    def test_projection_requires_actual_readonly_flag_and_mount_binding(self):
        with self.projection_fixture():
            self.owner.verify_projection()
            self.assertFalse(self.owner.failed)
            self.owner.mount_row = self.owner.mount_row.replace("ro,nosuid", "rw,nosuid")
            with self.assertRaises(FreezeRefusal):
                self.owner.verify_projection()
            self.assertTrue(self.owner.failed)
            self.assertTrue(os.fstat(self.owner.handles["readonly-projection"]).st_ino)

    def test_projection_readback_cannot_be_replaced_by_manifest_hash(self):
        with self.projection_fixture():
            self.owner.jobs.run.return_value = b"caller supplied fingerprint"
            with self.assertRaisesRegex(FreezeRefusal, "content readback"):
                self.owner.verify_projection()
            self.assertTrue(self.owner.failed)


if __name__ == "__main__":
    unittest.main()
