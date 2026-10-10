"""Real pipes and bounded file readback; Linux/proc/pidfd effects are synthetic.

No native, validator, helper, cgroup attachment, signal or provider is executed.
Every fixture is new and contains no credentials or prior qualification artifact.
"""

from datetime import datetime, timezone
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from crewshal.admission import (
    NativeAdmissionSpec,
    NamespaceIdentity,
    RetainedProc,
    admit_native_process,
)
from crewshal.contracts import record_digest
from crewshal.model import digest
from crewshal.supervisor import CgroupIdentity, OwnedCgroup
from tests.acceptance import test_phase_2d_dispatch as dispatch_fixtures


class SyntheticChild(subprocess.Popen):
    """Explicitly synthetic retained handle; Popen.__init__ is never called."""

    def __init__(self, stdin, stdout, stderr):
        self.pid = 12345
        self.stdin, self.stdout, self.stderr = stdin, stdout, stderr
        self.result = None

    def poll(self):
        return self.result

    def __del__(self):
        pass


class Phase2DAdmission(unittest.TestCase):
    def setUp(self):
        preparation = dispatch_fixtures.Phase2DDispatch()
        preparation.setUp()
        self.addCleanup(preparation.doCleanups)
        self.configuration = preparation.configuration
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.aggregate_path = self.root / "aggregate"
        self.aggregate_path.mkdir()
        self.worker_path = self.aggregate_path / "worker"
        self.worker_path.mkdir()
        self.aggregate = self.group(self.aggregate_path, "owned.slice/session.scope", True)
        self.worker = self.group(self.worker_path, "owned.slice/session.scope/worker", False)
        self.proc_path = self.root / "proc"
        self.proc_path.mkdir()
        for name in ("fd", "fdinfo", "ns"):
            (self.proc_path / name).mkdir()
        namespaces = {}
        for name in ("mnt", "net", "pid", "user"):
            target = self.root / f"namespace-{name}"
            target.write_bytes(b"synthetic namespace handle")
            (self.proc_path / "ns" / name).symlink_to(target)
            info = target.stat()
            namespaces[name] = NamespaceIdentity(device=info.st_dev, inode=info.st_ino)
        self.spec = NativeAdmissionSpec(
            configuration=record_digest(self.configuration),
            pid=12345,
            parent_pid=4321,
            start_ticks=1234567,
            boot_id="00000000-1111-2222-3333-444444444444",
            worker=self.worker.identity,
            aggregate=self.aggregate.identity,
            namespaces=namespaces,
            executable_sha256=digest(b"synthetic native bytes"),
        )
        self.write("stat", "12345 (native with ) and\nspace) T 4321 " + "0 " * 17 + "1234567\n")
        self.status = {
            "Name": "synthetic",
            "Pid": "12345",
            "Tgid": "12345",
            "PPid": "4321",
            "TracerPid": "0",
            "Threads": "1",
            "NoNewPrivs": "1",
            "Uid": "65534 65534 65534 65534",
            "Gid": "65534 65534 65534 65534",
            "Groups": "",
            **{
                key: "0000000000000000"
                for key in ("CapInh", "CapPrm", "CapEff", "CapBnd", "CapAmb")
            },
        }
        self.write_status()
        self.write(
            "cmdline", b"\0".join(x.encode() for x in self.configuration.native_argv) + b"\0"
        )
        self.environment = (
            b"\0".join(
                f"{k}={v}".encode() for k, v in self.configuration.native_environment.items()
            )
            + b"\0"
        )
        self.write("environ", self.environment)
        self.write("cgroup", "0::/owned.slice/session.scope/worker\n")
        (self.proc_path / "cwd").symlink_to("/scratch/checkout")
        self.executable = self.root / "native"
        self.executable.write_bytes(b"synthetic native bytes")
        self.executable.chmod(0o555)
        (self.proc_path / "exe").symlink_to(self.executable)
        self.streams = []
        pairs = []
        for _ in range(4):
            reader, writer = os.pipe()
            read_stream, write_stream = (
                os.fdopen(reader, "rb", buffering=0),
                os.fdopen(writer, "wb", buffering=0),
            )
            self.streams.extend([read_stream, write_stream])
            pairs.append((read_stream, write_stream))
        self.addCleanup(self.close_streams)
        self.in_reader, self.in_writer = pairs[0]
        self.out_reader, self.out_writer = pairs[1]
        self.err_reader, self.err_writer = pairs[2]
        self.pid_reader, self.pid_writer = pairs[3]
        # These are synthetic Linux proc links to the parent's retained pipes.
        # macOS assigns different inode numbers to the two ends of a pipe.
        for number, stream, flags in (
            (0, self.in_writer, "00"),
            (1, self.out_reader, "01"),
            (2, self.err_reader, "01"),
        ):
            (self.proc_path / "fd" / str(number)).symlink_to(
                f"pipe:[{os.fstat(stream.fileno()).st_ino}]"
            )
            self.write(f"fdinfo/{number}", f"pos:\t0\nflags:\t{flags}\n")
        self.child = SyntheticChild(self.in_writer, self.out_reader, self.err_reader)
        descriptor = os.open(self.proc_path, os.O_RDONLY | os.O_DIRECTORY)
        try:
            self.proc = RetainedProc(descriptor, self.pid_reader.fileno(), self.spec)
        finally:
            os.close(descriptor)
        self.addCleanup(self.proc.close)
        self.started = datetime.now(timezone.utc)

    def close_streams(self):
        for stream in self.streams:
            stream.close()

    def group(self, path, relative, aggregate):
        values = {
            "memory.max": "805306368" if aggregate else "134217728",
            "memory.swap.max": "0",
            "cpu.max": "100000 100000",
            "pids.max": "128" if aggregate else "32",
            "cgroup.type": "domain",
            "cgroup.events": "populated 1\nfrozen 0",
            "cgroup.procs": "" if aggregate else "12345",
            "memory.events": "max 0\noom 0\noom_kill 0",
            "pids.events": "max 0",
            "cgroup.kill": "",
        }
        for name, value in values.items():
            (path / name).write_text(value)
        info = path.stat()
        identity = CgroupIdentity(relative_path=relative, device=info.st_dev, inode=info.st_ino)
        descriptor = os.open(path, os.O_RDONLY | os.O_DIRECTORY)
        try:
            group = OwnedCgroup(descriptor, identity)
        finally:
            os.close(descriptor)
        self.addCleanup(group.close)
        return group

    def write(self, name, data):
        (self.proc_path / name).write_bytes(data.encode() if isinstance(data, str) else data)

    def write_status(self):
        self.write("status", "\n".join(f"{k}:\t{v}" for k, v in self.status.items()) + "\n")

    def admit(self, **changes):
        with patch("crewshal.admission.time.monotonic", return_value=1.0):
            return admit_native_process(
                self.child,
                self.proc,
                self.worker,
                self.aggregate,
                changes.pop("configuration", self.configuration),
                started=changes.pop("started", self.started),
                started_monotonic=changes.pop("started_monotonic", 0.0),
                **changes,
            )

    def test_admission_retains_exact_identity_and_never_releases_child(self):
        admitted = self.admit()
        self.assertEqual(admitted.receipt.spec.pid, 12345)
        self.assertEqual(admitted.receipt.configuration, record_digest(self.configuration))
        self.assertFalse(admitted.receipt.execution_allowed)
        self.assertFalse(admitted.receipt.spend_authorized)
        self.assertFalse(admitted.receipt.profile_qualified)
        self.assertEqual((self.worker_path / "cgroup.kill").read_bytes(), b"")
        self.proc.verify_stopped()

    def test_pid_start_parent_and_unstopped_identity_refuse(self):
        original = (self.proc_path / "stat").read_bytes()
        for before, after in (
            (b"12345 (", b"12346 ("),
            (b"T 4321", b"R 4321"),
            (b"T 4321", b"T 9999"),
            (b"1234567", b"1234568"),
        ):
            with self.subTest(after=after), self.assertRaises(ValueError):
                self.write("stat", original.replace(before, after))
                self.admit()
            self.write("stat", original)

    def test_exited_pidfd_refuses_same_numeric_pid(self):
        self.pid_writer.write(b"synthetic pidfd exit readiness")
        with self.assertRaisesRegex(ValueError, "pidfd reports process exit"):
            self.admit()

    def test_unexpected_privilege_groups_threads_or_tracer_refuse(self):
        for key, value in (
            ("Uid", "65534 0 65534 65534"),
            ("Gid", "0 0 0 0"),
            ("Groups", "65533"),
            ("NoNewPrivs", "0"),
            ("CapBnd", "0000000000000001"),
            ("CapEff", "invalid"),
            ("Threads", "2"),
            ("TracerPid", "4321"),
            ("Tgid", "9"),
        ):
            original = self.status[key]
            with self.subTest(key=key), self.assertRaises(ValueError):
                self.status[key] = value
                self.write_status()
                self.admit()
            self.status[key] = original
        self.write_status()

    def test_missing_or_duplicate_status_is_not_empty_authority(self):
        original = (self.proc_path / "status").read_bytes()
        for raw in (
            original.replace(b"Groups:\t\n", b""),
            original + b"Uid:\t0 0 0 0\n",
            b"forged success",
        ):
            with self.subTest(raw=raw[-20:]), self.assertRaises(ValueError):
                self.write("status", raw)
                self.admit()

    def test_argv_and_ambient_or_duplicate_environment_refuse(self):
        for raw in (
            self.environment + b"TOKEN=synthetic\0",
            self.environment + b"HOME=/scratch\0",
            self.environment[:-1],
            b"malformed\0",
        ):
            with self.subTest(raw=raw[-20:]), self.assertRaises(ValueError):
                self.write("environ", raw)
                self.admit()
        self.write("environ", self.environment)
        self.write("cmdline", b"/bin/sh\0-c\0echo success\0")
        with self.assertRaisesRegex(ValueError, "argv differs"):
            self.admit()

    def test_worker_migration_and_wrong_cwd_refuse(self):
        self.write("cgroup", "0::/unrelated.slice/worker\n")
        with self.assertRaisesRegex(ValueError, "outside retained worker"):
            self.admit()
        self.write("cgroup", "0::/owned.slice/session.scope/worker\n")
        (self.proc_path / "cwd").unlink()
        (self.proc_path / "cwd").symlink_to("/original")
        with self.assertRaisesRegex(ValueError, "cwd differs"):
            self.admit()

    def test_subscription_readback_requires_candidate_cwd(self):
        from tests.acceptance.test_phase_2d_subscription import SubscriptionPreparation

        fixture = SubscriptionPreparation()
        fixture.setUp()
        self.addCleanup(fixture.doCleanups)
        configuration = fixture.configuration
        self.write("cmdline", b"\0".join(x.encode() for x in configuration.native_argv) + b"\0")
        self.write(
            "environ",
            b"\0".join(
                f"{key}={value}".encode() for key, value in configuration.native_environment.items()
            )
            + b"\0",
        )
        (self.proc_path / "cwd").unlink()
        (self.proc_path / "cwd").symlink_to("/candidate/owned")
        self.proc.read_configuration(configuration)
        (self.proc_path / "cwd").unlink()
        (self.proc_path / "cwd").symlink_to("/scratch/checkout")
        with self.assertRaisesRegex(ValueError, "cwd differs"):
            self.proc.read_configuration(configuration)

    def test_namespace_replacement_refuses(self):
        (self.proc_path / "ns" / "net").unlink()
        (self.proc_path / "ns" / "net").symlink_to(self.executable)
        with self.assertRaisesRegex(ValueError, "namespace identity"):
            self.admit()

    def test_changed_or_writable_executable_refuses(self):
        self.executable.chmod(0o777)
        with self.assertRaisesRegex(ValueError, "executable authority"):
            self.admit()
        self.executable.write_bytes(b"different executable bytes")
        self.executable.chmod(0o555)
        with self.assertRaisesRegex(ValueError, "executable bytes"):
            self.admit()

    def test_extra_broker_fd_or_wrong_pipe_direction_refuses(self):
        extra = self.proc_path / "fd" / "3"
        extra.symlink_to("socket:[9999]")
        with self.assertRaisesRegex(ValueError, "unexpected inherited"):
            self.admit()
        extra.unlink()
        self.write("fdinfo/1", "flags:\t00\n")
        with self.assertRaisesRegex(ValueError, "stdio direction"):
            self.admit()

    def test_different_pipe_and_aliased_parent_streams_refuse(self):
        (self.proc_path / "fd" / "1").unlink()
        (self.proc_path / "fd" / "1").symlink_to("pipe:[9999]")
        with self.assertRaisesRegex(ValueError, "match retained pipe"):
            self.admit()
        self.child.stderr = self.child.stdout
        with self.assertRaisesRegex(ValueError, "must be distinct"):
            self.admit()

    def test_parent_write_end_is_not_capture_read_end(self):
        self.child.stdout = self.out_writer
        with self.assertRaisesRegex(ValueError, "parent pipe direction"):
            self.admit()

    def test_worker_population_or_refusal_history_refuses(self):
        for name, value in (
            ("cgroup.procs", "12345\n12346"),
            ("cgroup.events", "populated 0\nfrozen 0"),
            ("pids.events", "max 1"),
        ):
            path = self.worker_path / name
            original = path.read_bytes()
            with self.subTest(name=name), self.assertRaises(ValueError):
                path.write_text(value)
                self.admit()
            path.write_bytes(original)

    def test_relaxed_or_missing_aggregate_controls_refuse(self):
        for name, value in (
            ("memory.max", "max"),
            ("pids.max", "129"),
            ("cpu.max", "200000 100000"),
            ("cgroup.procs", "9999"),
            ("memory.events", "max 0\noom 0"),
            ("pids.events", "max 1"),
        ):
            path = self.aggregate_path / name
            original = path.read_bytes()
            with self.subTest(name=name), self.assertRaises(ValueError):
                path.write_text(value)
                self.admit()
            path.write_bytes(original)

    def test_path_string_does_not_establish_actual_cgroup_ancestry(self):
        self.worker_path.rename(self.root / "moved-worker")
        with self.assertRaisesRegex(ValueError, "descriptor parent differs"):
            self.admit()

    def test_proc_path_replacement_keeps_original_descriptor(self):
        self.proc_path.rename(self.root / "retained-proc")
        self.proc_path.mkdir()
        (self.proc_path / "stat").write_text("forged success")
        self.admit()

    def test_oversized_fifo_or_symlink_proc_file_refuses(self):
        self.write("status", b"x" * 65537)
        with self.assertRaisesRegex(ValueError, "exceeds bound"):
            self.admit()
        path = self.proc_path / "status"
        path.unlink()
        os.mkfifo(path)
        with self.assertRaisesRegex(ValueError, "regular kernel"):
            self.admit()
        path.unlink()
        path.symlink_to(self.executable)
        with self.assertRaises(OSError):
            self.admit()

    def test_unbound_or_changed_dispatch_and_source_refuse(self):
        changed = self.configuration.model_copy(deep=True)
        changed.native_argv[0] = "/bin/sh"
        # Even retaining a new spec digest cannot substitute another argv.
        self.proc.spec.configuration = record_digest(changed)
        with self.assertRaisesRegex(ValueError, "pinned dispatch"):
            self.admit(configuration=changed)
        changed = self.configuration.model_copy(deep=True)
        changed.source_sha256["admission.py"] = digest(b"stale source")
        self.proc.spec.configuration = record_digest(changed)
        with self.assertRaisesRegex(ValueError, "source changed"):
            self.admit(configuration=changed)

    def test_invalid_or_expired_launch_clocks_refuse(self):
        for value in (float("nan"), float("inf"), -5.0, 2.0):
            with self.subTest(value=value), self.assertRaises(ValueError):
                self.admit(started_monotonic=value)
        with self.assertRaises(ValueError):
            self.admit(started=self.started.replace(tzinfo=None))

    def test_process_mutation_during_readback_is_refused(self):
        original = self.proc.read_configuration

        def mutate(configuration):
            values = original(configuration)
            self.write("stat", "12345 (native) R 4321 " + "0 " * 17 + "1234567\n")
            return values

        with patch.object(self.proc, "read_configuration", mutate), self.assertRaises(ValueError):
            self.admit()

    def test_admitted_handle_connects_to_bounded_supervisor_capture(self):
        admitted = self.admit()
        self.out_writer.write(b"literal native output\n")
        self.out_writer.close()
        self.err_writer.close()
        self.child.result = 0
        self.pid_writer.close()
        (self.worker_path / "cgroup.procs").write_text("")
        (self.worker_path / "cgroup.events").write_text("populated 0\nfrozen 0")
        with patch("crewshal.supervisor.time.monotonic", return_value=1.0):
            capture = admitted.capture(cancelled=lambda: False)
        self.assertEqual(capture.stdout, b"literal native output\n")
        self.assertTrue(capture.observation.tree_stopped)
        self.assertTrue(capture.observation.stdout_complete)

    def test_empty_worker_and_exit_code_cannot_replace_retained_native_exit(self):
        admitted = self.admit()
        self.out_writer.close()
        self.err_writer.close()
        self.child.result = 0
        (self.worker_path / "cgroup.procs").write_text("")
        (self.worker_path / "cgroup.events").write_text("populated 0\nfrozen 0")
        with (
            patch("crewshal.supervisor.time.monotonic", return_value=1.0),
            self.assertRaisesRegex(ValueError, "native exit"),
        ):
            admitted.capture(cancelled=lambda: False)
        self.assertGreaterEqual(self.proc.pidfd, 0)
        self.assertGreaterEqual(self.proc.descriptor, 0)

    def test_terminal_native_handle_rebinding_refuses_ready_substitute(self):
        for name in ("pidfd", "descriptor"):
            with self.subTest(name=name):
                admitted = self.admit()
                original = getattr(self.proc, name)
                if name == "pidfd":
                    reader, writer = os.pipe()
                    os.close(writer)
                    substitute = reader
                else:
                    substitute = os.open(self.root, os.O_RDONLY | os.O_DIRECTORY)
                try:
                    setattr(self.proc, name, substitute)
                    with self.assertRaisesRegex(ValueError, "descriptor changed"):
                        admitted.verify_terminal(0)
                finally:
                    setattr(self.proc, name, original)
                    os.close(substitute)

    def test_native_exit_does_not_replace_reap_or_empty_worker(self):
        admitted = self.admit()
        self.pid_writer.close()
        with self.assertRaisesRegex(ValueError, "exit/reap"):
            admitted.verify_terminal(0)
        self.child.result = 0
        with self.assertRaisesRegex(ValueError, "repopulated"):
            admitted.verify_terminal(0)
        (self.worker_path / "cgroup.procs").write_text("")
        (self.worker_path / "cgroup.events").write_text("populated 0\nfrozen 0")
        admitted.verify_terminal(0)
        with self.assertRaisesRegex(ValueError, "exit/reap"):
            admitted.verify_terminal(1)

    def test_terminal_capture_rechecks_changed_aggregate_after_native_exit(self):
        admitted = self.admit()
        self.pid_writer.close()
        self.child.result = 0
        (self.worker_path / "cgroup.procs").write_text("")
        (self.worker_path / "cgroup.events").write_text("populated 0\nfrozen 0")
        original = self.worker.sample

        def mutate():
            sample = original()
            (self.aggregate_path / "memory.max").write_text("max")
            return sample

        with patch.object(self.worker, "sample", side_effect=mutate):
            with self.assertRaisesRegex(ValueError, "aggregate controls"):
                admitted.verify_terminal(0)
        self.assertEqual((self.worker_path / "cgroup.kill").read_bytes(), b"")

    def test_mutated_configuration_after_admission_refuses_capture(self):
        admitted = self.admit()
        admitted.configuration.native_environment["TOKEN"] = "synthetic"
        with self.assertRaisesRegex(ValueError, "configuration changed"):
            admitted.capture(cancelled=lambda: False)

    def test_closed_proc_and_non_linux_attach_refuse(self):
        self.proc.close()
        with self.assertRaises((OSError, ValueError)):
            self.admit()
        with (
            patch("crewshal.admission.sys.platform", "darwin"),
            self.assertRaisesRegex(ValueError, "unavailable"),
        ):
            RetainedProc.attach(self.spec)

    def test_schema_boolean_authority_and_invalid_topology_refuse(self):
        for changes in (
            {"schema_version": True},
            {"execution_allowed": True},
            {"spend_authorized": True},
            {"native_uid": 0},
            {"namespaces": {}},
            {"parent_pid": 12345},
        ):
            with self.subTest(changes=changes), self.assertRaises(ValueError):
                NativeAdmissionSpec.model_validate({**self.spec.model_dump(), **changes})
        self.assertEqual(len(self.configuration.source_sha256), 23)

    def test_missing_or_reaped_child_cannot_supply_admission(self):
        self.child.result = 0
        with self.assertRaisesRegex(ValueError, "retained child"):
            self.admit()
        self.child.result = None
        self.child.stdin = None
        with self.assertRaisesRegex(ValueError, "retained child"):
            self.admit()

    def test_deadline_expiring_during_readback_refuses_receipt(self):
        with patch("crewshal.admission.time.monotonic", side_effect=[1.0, 5.0]):
            with self.assertRaisesRegex(ValueError, "deadline expired during admission"):
                admit_native_process(
                    self.child,
                    self.proc,
                    self.worker,
                    self.aggregate,
                    self.configuration,
                    started=self.started,
                    started_monotonic=0.0,
                )

    def test_closed_or_swapped_pipe_after_admission_refuses_capture(self):
        admitted = self.admit()
        self.child.stdout = self.in_reader
        with self.assertRaisesRegex(ValueError, "pipe identity changed"):
            admitted.capture(cancelled=lambda: False)

    def test_changed_aggregate_before_capture_refuses(self):
        admitted = self.admit()
        (self.aggregate_path / "memory.max").write_text("max")
        with self.assertRaisesRegex(ValueError, "aggregate controls"):
            admitted.capture(cancelled=lambda: False)
