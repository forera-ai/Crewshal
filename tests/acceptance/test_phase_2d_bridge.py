"""Ordinary FD/socket fixtures with explicit synthetic Linux proc/credential seams."""

from array import array
import copy
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import socket
import struct
from types import SimpleNamespace
import tempfile
import time
import unittest
from unittest.mock import Mock, patch

from crewshal.linux_bridge import (
    BridgeRefusal,
    CAPTURE_PACKETS,
    NATIVE_PACKET,
    ParentBridgeEndpoint,
    StoppedNativeBridge,
    WATCHDOG_PACKET,
    _mapped_host_proc,
    _send,
    prepare_stopped_native_bridge,
    retain_parent_bridge,
    send_original_native_capture,
)
from crewshal.admission import AdmittedNative
from crewshal.linux_parent import RetainedTrustedTask
from crewshal.linux_production import EffectiveInstallation
from crewshal.linux_setup import OwnedNamespaceSetup, OwnedWatchdogLifetime
from crewshal.runtime import ProcessObservation, STREAM_BYTES
from crewshal.supervisor import CapturedProcess, CgroupIdentity, CgroupSample


def proc_stat(pid, parent, start, state="T"):
    values = [state, str(parent)] + ["0"] * 17 + [str(start)]
    return f"{pid} (synthetic proc) {' '.join(values)}\n"


class Phase2DBridgeProcMapping(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.directory = Path(self.temporary.name)
        self.host = self.directory / "host"
        self.source = self.directory / "namespace"
        self.source.mkdir()
        (self.host / "self" / "fdinfo").mkdir(parents=True)
        (self.host / "2001").mkdir()
        (self.source / "stat").write_text(proc_stat(3, 2, 17))
        (self.source / "status").write_text("Pid:\t3\nTgid:\t3\nPPid:\t2\nNSpid:\t3\n")
        (self.host / "2001" / "stat").write_text(proc_stat(2001, 2000, 17))
        (self.host / "2001" / "status").write_text(
            "Pid:\t2001\nTgid:\t2001\nPPid:\t2000\nNSpid:\t2001 3\n"
        )
        self.fdinfo = self.host / "self" / "fdinfo" / "9"
        self.fdinfo.write_text("Pid:\t2001\nNSpid:\t2001 3\n")
        self.root_fd = os.open(self.host, os.O_RDONLY | os.O_DIRECTORY)
        self.source_fd = os.open(self.source, os.O_RDONLY | os.O_DIRECTORY)
        self.received = []
        self.addCleanup(self.close_fds)

    def close_fds(self):
        for fd in [self.root_fd, self.source_fd, *self.received]:
            os.close(fd)

    def mapping(self):
        with (
            patch("crewshal.linux_bridge._filesystem_magic", return_value=0x9FA0),
            patch("crewshal.linux_bridge.select.select", return_value=([], [], [])),
            patch(
                "crewshal.linux_bridge._namespaces",
                return_value={"actual": "synthetic namespace inode"},
            ),
        ):
            return _mapped_host_proc(self.root_fd, self.source_fd, 9, self.received)

    def test_host_pid_comes_from_actual_pidfd_view_not_namespace_pid(self):
        descriptor, pid, parent, start = self.mapping()
        self.assertEqual((pid, parent, start), (2001, 2000, 17))
        self.assertNotEqual(os.fstat(descriptor).st_ino, os.fstat(self.source_fd).st_ino)
        self.assertIn(descriptor, self.received)

    def test_missing_dead_foreign_or_malformed_pidfd_mapping_refuses(self):
        for data in (
            "Pid:\t-1\nNSpid:\t-1\n",
            "Pid:\t0\nNSpid:\t0\n",
            "Pid:\t2001\n",
            "Pid:\t2001\nNSpid:\t2001 99\n",
            "Pid:\t2001\nNSpid:\t2002 3\n",
        ):
            with self.subTest(data=data):
                self.fdinfo.write_text(data)
                with self.assertRaises(ValueError):
                    self.mapping()

    def test_changed_start_or_host_status_refuses_and_retains_opened_host_fd(self):
        for content in (proc_stat(2001, 2000, 18), proc_stat(2001, 2000, 17, "R")):
            with self.subTest(content=content):
                (self.host / "2001" / "stat").write_text(content)
                before = len(self.received)
                with self.assertRaises(ValueError):
                    self.mapping()
                self.assertEqual(len(self.received), before + 1)
                os.fstat(self.received[-1])

    def test_actual_proc_namespace_identity_must_agree(self):
        with (
            patch("crewshal.linux_bridge._filesystem_magic", return_value=0x9FA0),
            patch("crewshal.linux_bridge.select.select", return_value=([], [], [])),
            patch(
                "crewshal.linux_bridge._namespaces", side_effect=[{"pid": "one"}, {"pid": "other"}]
            ),
            self.assertRaises(ValueError),
        ):
            _mapped_host_proc(self.root_fd, self.source_fd, 9, self.received)
        self.assertEqual(len(self.received), 1)

    def test_ordinary_directory_cannot_impersonate_received_procfs(self):
        with (
            patch("crewshal.linux_bridge._filesystem_magic", return_value=0xEF53),
            self.assertRaisesRegex(ValueError, "actual procfs"),
        ):
            _mapped_host_proc(self.root_fd, self.source_fd, 9, self.received)
        self.assertEqual(self.received, [])

    def test_pidfd_exit_before_mapping_refuses_without_opening_new_proc(self):
        with (
            patch("crewshal.linux_bridge._filesystem_magic", return_value=0x9FA0),
            patch("crewshal.linux_bridge.select.select", return_value=([9], [], [])),
            self.assertRaises(ValueError),
        ):
            _mapped_host_proc(self.root_fd, self.source_fd, 9, self.received)
        self.assertEqual(self.received, [])


class Phase2DBridgePacketCustody(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.directory = Path(self.temporary.name)
        self.root_fd = os.open(self.directory, os.O_RDONLY | os.O_DIRECTORY)
        self.addCleanup(os.close, self.root_fd)
        self.bridge = object.__new__(StoppedNativeBridge)
        self.bridge.received, self.bridge.handles = [], []
        self.bridge.failed, self.bridge.stage = False, 0
        self.bridge.parent_channel = Mock()
        self.bridge.installation = SimpleNamespace(
            reservation=SimpleNamespace(_retain_installation_refusal=Mock())
        )
        self.credential_kind = 100001
        self.patch = patch.object(socket, "SCM_CREDENTIALS", self.credential_kind, create=True)
        self.patch.start()
        self.addCleanup(self.patch.stop)
        self.cloexec = patch.object(socket, "MSG_CMSG_CLOEXEC", 0, create=True)
        self.cloexec.start()
        self.addCleanup(self.cloexec.stop)
        self.fds = []
        self.addCleanup(self.close_fds)

    def close_fds(self):
        for fd in self.fds:
            os.close(fd)

    def packet(
        self, *, credentials=(2000, 0, 0), flags=0, raw=b"original packet", count=1, extra=()
    ):
        values = [os.dup(self.root_fd) for _ in range(count)]
        self.fds.extend(values)
        ancillary = [(socket.SOL_SOCKET, socket.SCM_RIGHTS, array("i", values).tobytes())]
        if credentials is not None:
            ancillary.append(
                (socket.SOL_SOCKET, self.credential_kind, struct.pack("=iii", *credentials))
            )
        ancillary.extend(extra)
        self.bridge.parent_channel.recvmsg.return_value = raw, ancillary, flags, None
        return values

    def test_fd_rights_are_pinned_before_packet_is_parsed(self):
        original = self.packet()
        raw, received, credentials = self.bridge._packet()
        self.assertEqual(raw, b"original packet")
        self.assertEqual(received, original)
        self.assertEqual(self.bridge.received, original)
        self.assertEqual(credentials, (2000, 0, 0))

    def test_missing_or_nonroot_credentials_refuse_without_closing_received_fds(self):
        for credentials in (None, (2000, 1, 0), (2000, 0, 1)):
            with self.subTest(credentials=credentials):
                values = self.packet(credentials=credentials)
                with self.assertRaises(ValueError):
                    self.bridge._packet()
                self.assertIn(values[0], self.bridge.received)
                os.fstat(values[0])

    def test_truncated_or_unknown_ancillary_packets_keep_all_rights(self):
        for flags, extra in (
            (socket.MSG_TRUNC, ()),
            (socket.MSG_CTRUNC, ()),
            (0, ((socket.SOL_SOCKET, 9999, b"unknown"),)),
        ):
            with self.subTest(flags=flags, extra=extra):
                values = self.packet(count=2, flags=flags, extra=extra)
                with self.assertRaises(ValueError):
                    self.bridge._packet()
                self.assertTrue(all(fd in self.bridge.received for fd in values))

    def test_duplicate_credentials_or_malformed_rights_refuse(self):
        duplicate = (socket.SOL_SOCKET, self.credential_kind, struct.pack("=iii", 2000, 0, 0))
        values = self.packet(extra=(duplicate,))
        with self.assertRaises(ValueError):
            self.bridge._packet()
        self.assertIn(values[0], self.bridge.received)
        malformed = (socket.SOL_SOCKET, socket.SCM_RIGHTS, b"x")
        values = self.packet(extra=(malformed,))
        with self.assertRaises(ValueError):
            self.bridge._packet()
        self.assertIn(values[0], self.bridge.received)

    def test_unbounded_received_handles_refuse_without_refunding(self):
        self.bridge.received = [-1] * 32
        values = self.packet()
        with self.assertRaises(ValueError):
            self.bridge._packet()
        self.assertIn(values[0], self.bridge.received)

    def test_malformed_watchdog_frame_consumes_original_bridge(self):
        self.bridge._wait = Mock()
        values = self.packet(raw=b'{"protocol":"caller","origin_ns":1,"expires_ns":2}', count=4)
        with self.assertRaises(BridgeRefusal):
            self.bridge.receive_watchdog(Mock())
        self.assertTrue(self.bridge.failed)
        self.assertEqual(self.bridge.received, values)
        self.bridge.installation.reservation._retain_installation_refusal.assert_called_once()
        with self.assertRaisesRegex(BridgeRefusal, "consumed"):
            self.bridge.receive_watchdog(Mock())

    def test_watchdog_origin_cannot_renew_to_another_duration(self):
        self.bridge._wait = Mock()
        raw = json.dumps(
            {"protocol": WATCHDOG_PACKET, "origin_ns": 1, "expires_ns": 6_000_000_001}
        ).encode()
        self.packet(raw=raw, count=4)
        with self.assertRaises(BridgeRefusal):
            self.bridge.receive_watchdog(Mock())
        self.assertTrue(self.bridge.failed)

    def test_native_packet_without_retained_actual_watchdog_cannot_begin(self):
        self.packet(raw=NATIVE_PACKET, count=5)
        with self.assertRaisesRegex(BridgeRefusal, "missing"):
            self.bridge.receive_native()
        self.bridge.parent_channel.recvmsg.assert_not_called()

    def test_native_packet_wrong_sender_or_size_consumes_original_attempt(self):
        self.bridge.stage = 1
        self.bridge._wait = Mock()
        self.bridge.parent = SimpleNamespace(spec=SimpleNamespace(pid=2000))
        values = self.packet(raw=NATIVE_PACKET, credentials=(3000, 0, 0), count=5)
        with self.assertRaises(BridgeRefusal):
            self.bridge.receive_native()
        self.assertTrue(self.bridge.failed)
        self.assertEqual(self.bridge.received, values)

    def test_wait_uses_original_native_expiry_not_new_five_seconds(self):
        self.bridge.stage = 1
        self.bridge._verify_original = Mock()
        self.bridge.expires_ns = 102_000_000_000
        self.bridge.installation.reservation.batch_started = 0
        with (
            patch("crewshal.linux_bridge.time.monotonic", return_value=100),
            patch(
                "crewshal.linux_bridge.select.select",
                return_value=([self.bridge.parent_channel], [], []),
            ) as waiting,
        ):
            self.bridge._wait()
        self.assertEqual(waiting.call_args.args[3], 2)

    def test_initial_wait_uses_original_preparation_origin(self):
        self.bridge._verify_original = Mock()
        self.bridge.installation.reservation.batch_started = 10
        with (
            patch("crewshal.linux_bridge.time.monotonic", return_value=129),
            patch(
                "crewshal.linux_bridge.select.select",
                return_value=([self.bridge.parent_channel], [], []),
            ) as waiting,
        ):
            self.bridge._wait()
        self.assertEqual(waiting.call_args.args[3], 1)

    def test_no_serialized_or_constructed_live_bridge(self):
        with self.assertRaises(ValueError):
            StoppedNativeBridge()
        with self.assertRaises(TypeError):
            copy.copy(self.bridge)

    def capture_fixture(self, *, tree_stopped=True):
        identity = CgroupIdentity(relative_path="original/worker", device=1, inode=2)
        sample = CgroupSample(
            identity=identity,
            controls={},
            populated=False,
            direct_pids=[],
            memory_events={},
            pids_events={},
        )
        instant = datetime(2026, 10, 10, tzinfo=timezone.utc)
        observation = ProcessObservation(
            started=instant,
            ended=instant,
            elapsed_seconds=0,
            exit_code=0,
            stdout_complete=True,
            stderr_complete=True,
            tree_stopped=tree_stopped,
        )
        self.bridge.stage = 2
        self.bridge.parent = SimpleNamespace(spec=SimpleNamespace(pid=2000))
        self.bridge.lifetime = SimpleNamespace(worker=SimpleNamespace(identity=identity))
        self.bridge.freeze = SimpleNamespace(verify_custody=Mock(), _verify_terminal_kernel=Mock())
        self.bridge._wait = Mock()
        self.bridge._verify_original = Mock()
        self.bridge.parent_channel.send.return_value = 1
        data = {
            "observation": observation.model_dump(mode="json"),
            "initial": sample.model_dump(mode="json"),
            "final": sample.model_dump(mode="json"),
            "overflow": False,
            "stop_error": False,
        }
        payloads = (b"raw native stdout", b"raw native stderr", json.dumps(data).encode())
        frames = []
        for prefix, payload in zip(CAPTURE_PACKETS, payloads):
            self.packet(raw=prefix + payload, count=0)
            frames.append(self.bridge.parent_channel.recvmsg.return_value)
        self.bridge.parent_channel.recvmsg.side_effect = frames
        return observation, sample, frames

    def test_capture_receives_exact_bounded_streams_and_retains_original_identity(self):
        observation, sample, _ = self.capture_fixture()
        captured = self.bridge.receive_capture()
        self.assertIs(captured, self.bridge.native_capture)
        self.assertIs(captured, self.bridge._capture_owner)
        self.assertEqual(captured.stdout, b"raw native stdout")
        self.assertEqual(captured.stderr, b"raw native stderr")
        self.assertEqual(captured.observation, observation)
        self.assertEqual(captured.initial, sample)
        self.assertEqual(self.bridge.stage, 3)
        self.bridge.freeze._verify_terminal_kernel.assert_called_once()
        self.assertEqual(self.bridge.parent_channel.send.call_count, 3)
        with self.assertRaisesRegex(BridgeRefusal, "consumed"):
            self.bridge.receive_capture()

    def test_true_tree_stopped_metadata_cannot_substitute_for_kernel_reap(self):
        self.capture_fixture(tree_stopped=True)
        self.bridge.freeze._verify_terminal_kernel.side_effect = ValueError("actual pidfd unreaped")
        with self.assertRaisesRegex(BridgeRefusal, "actual pidfd unreaped"):
            self.bridge.receive_capture()
        self.assertFalse(hasattr(self.bridge, "native_capture"))
        self.assertEqual(self.bridge.stage, 2)
        self.assertTrue(self.bridge.failed)
        self.assertEqual(len(self.bridge.capture_packets), 3)
        self.assertEqual(self.bridge.parent_channel.send.call_count, 2)

    def test_false_tree_stopped_flag_does_not_override_actual_terminal_kernel_readback(self):
        self.capture_fixture(tree_stopped=False)
        captured = self.bridge.receive_capture()
        self.assertFalse(captured.observation.tree_stopped)
        self.bridge.freeze._verify_terminal_kernel.assert_called_once()

    def test_verify_capture_refuses_same_object_metadata_mutation(self):
        self.capture_fixture()
        captured = self.bridge.receive_capture()
        self.bridge.verify_capture()
        captured.observation.elapsed_seconds = 1
        with self.assertRaisesRegex(BridgeRefusal, "capture changed"):
            self.bridge.verify_capture()
        self.assertTrue(self.bridge.failed)
        self.assertIs(self.bridge.native_capture, captured)

    def test_verify_capture_refuses_reconstructed_equal_capture(self):
        self.capture_fixture()
        captured = self.bridge.receive_capture()
        self.bridge.native_capture = CapturedProcess(
            captured.observation,
            captured.stdout,
            captured.stderr,
            captured.initial,
            captured.final,
            captured.overflow,
            captured.stop_error,
        )
        with self.assertRaisesRegex(BridgeRefusal, "capture changed"):
            self.bridge.verify_capture()
        self.assertIs(self.bridge._capture_owner, captured)

    def retained_stage_three_fixture(self):
        self.capture_fixture()
        captured = self.bridge.receive_capture()
        # Restore the real bridge custody verifier, retaining explicit synthetic
        # task/cgroup/kernel readback. No process or kernel storage operation runs.
        del self.bridge._verify_original
        lifetime = object.__new__(OwnedNamespaceSetup)
        worker = self.bridge.lifetime.worker
        config, aggregate, setup, supervisor, observer_group = (
            object(),
            object(),
            object(),
            SimpleNamespace(identity=object()),
            object(),
        )
        lifetime.controls = SimpleNamespace(configuration=config, boot_id="fixture")
        lifetime.aggregate, lifetime.worker, lifetime.setup = aggregate, worker, setup
        lifetime.supervisor, lifetime.observer_group = supervisor, observer_group
        lifetime.wrapper = Mock()
        lifetime.wrapper.poll.return_value = None
        self.bridge.lifetime = lifetime
        self.bridge.watchdog = SimpleNamespace(spec=object(), verify_handles=Mock())
        self.bridge.parent.verify = Mock()
        reservation = self.bridge.installation.reservation
        reservation.observer = SimpleNamespace(
            spec=SimpleNamespace(pid=os.getpid(), boot_id="fixture")
        )
        reservation.batch_started, reservation._configuration = 0, config
        reservation.aggregate, reservation.observer_group = aggregate, observer_group
        reservation._batch_timer = SimpleNamespace(
            worker=worker, setup=setup, supervisor=supervisor
        )
        reservation._setup_lifetime, lifetime.storage_reservation = lifetime, reservation
        self.bridge.installation.verify_custody = Mock()
        self.bridge.installation._bridge = self.bridge
        self.bridge.origin_ns, self.bridge.expires_ns = 100_000_000_000, 105_000_000_000
        self.bridge._deadline = (self.bridge.origin_ns, self.bridge.expires_ns)
        self.bridge._parent_owners = (self.bridge.parent, self.bridge.watchdog)
        self.bridge._parent_specs = ("synthetic", "synthetic")
        self.bridge.freeze._verify_terminal_kernel.reset_mock()
        return captured

    def test_retained_capture_after_original_six_seconds_requires_repeated_terminal_readback(self):
        captured = self.retained_stage_three_fixture()
        with (
            patch("crewshal.linux_bridge.record_digest", return_value="synthetic"),
            patch("crewshal.linux_bridge.time.monotonic", return_value=107),
            patch("crewshal.linux_bridge.time.monotonic_ns", return_value=107_000_000_000),
        ):
            self.bridge.verify_capture()
        self.assertIs(self.bridge.native_capture, captured)
        self.assertEqual(self.bridge.freeze._verify_terminal_kernel.call_count, 2)
        self.assertFalse(self.bridge.failed)

    def test_delayed_retained_capture_refuses_repopulated_worker_or_unreaped_zombie(self):
        for error in (
            "original native tree remains populated",
            "original native/watchdog reap remains unobserved",
        ):
            with self.subTest(error=error):
                if hasattr(self.bridge, "capture_packets"):
                    del self.bridge.capture_packets
                self.bridge.failed = False
                self.retained_stage_three_fixture()
                self.bridge.freeze._verify_terminal_kernel.side_effect = ValueError(error)
                with (
                    patch("crewshal.linux_bridge.record_digest", return_value="synthetic"),
                    patch("crewshal.linux_bridge.time.monotonic", return_value=107),
                    patch("crewshal.linux_bridge.time.monotonic_ns", return_value=107_000_000_000),
                    self.assertRaisesRegex(BridgeRefusal, error),
                ):
                    self.bridge.verify_capture()
                self.assertTrue(self.bridge.failed)

    def test_delayed_retained_capture_refuses_at_original_batch_cutoff(self):
        self.retained_stage_three_fixture()
        with (
            patch("crewshal.linux_bridge.record_digest", return_value="synthetic"),
            patch("crewshal.linux_bridge.time.monotonic", return_value=570),
            self.assertRaisesRegex(BridgeRefusal, "cutoff expired"),
        ):
            self.bridge.verify_capture()
        self.assertTrue(self.bridge.failed)

    def test_capture_metadata_missing_flag_or_foreign_worker_refuses(self):
        for mutation in ("foreign-worker", "string-flag", "missing-field"):
            with self.subTest(mutation=mutation):
                _, _, frames = self.capture_fixture()
                if hasattr(self.bridge, "capture_packets"):
                    del self.bridge.capture_packets
                self.bridge.failed = False
                raw, ancillary, flags, address = frames[2]
                data = json.loads(raw[len(CAPTURE_PACKETS[2]) :])
                if mutation == "foreign-worker":
                    data["initial"]["identity"]["inode"] = 99
                elif mutation == "string-flag":
                    data["overflow"] = "false"
                else:
                    del data["stop_error"]
                frames[2] = (
                    CAPTURE_PACKETS[2] + json.dumps(data).encode(),
                    ancillary,
                    flags,
                    address,
                )
                self.bridge.parent_channel.recvmsg.side_effect = frames
                with self.assertRaises(BridgeRefusal):
                    self.bridge.receive_capture()
                self.assertFalse(hasattr(self.bridge, "native_capture"))
                self.bridge.freeze._verify_terminal_kernel.assert_not_called()

    def test_terminal_transport_wait_cannot_consume_fixed_batch_reserve(self):
        self.bridge.stage = 2
        self.bridge._verify_original = Mock()
        self.bridge.expires_ns = 570_000_000_000
        self.bridge.installation.reservation.batch_started = 0
        with (
            patch("crewshal.linux_bridge.time.monotonic", return_value=569.5),
            patch(
                "crewshal.linux_bridge.select.select",
                return_value=([self.bridge.parent_channel], [], []),
            ) as waiting,
        ):
            self.bridge._wait()
        self.assertEqual(waiting.call_args.args[3], 0.5)

    def test_capture_unknown_rights_retained_before_refusal_no_retry(self):
        self.capture_fixture()
        self.bridge.parent_channel.recvmsg.side_effect = None
        values = self.packet(raw=CAPTURE_PACKETS[0] + b"data", count=1)
        with self.assertRaisesRegex(BridgeRefusal, "rights differs"):
            self.bridge.receive_capture()
        self.assertIn(values[0], self.bridge.received)
        os.fstat(values[0])
        self.assertTrue(self.bridge.failed)
        with self.assertRaisesRegex(BridgeRefusal, "consumed"):
            self.bridge.receive_capture()

    def test_capture_requires_original_host_parent_credentials_and_fixed_order(self):
        for raw, sender in ((CAPTURE_PACKETS[1] + b"data", 2000), (CAPTURE_PACKETS[0], 999)):
            with self.subTest(raw=raw, sender=sender):
                self.capture_fixture()
                if hasattr(self.bridge, "capture_packets"):
                    del self.bridge.capture_packets
                self.bridge.failed = False
                self.bridge.parent_channel.recvmsg.side_effect = None
                self.packet(raw=raw, credentials=(sender, 0, 0), count=0)
                with self.assertRaisesRegex(BridgeRefusal, "framing/sender/rights"):
                    self.bridge.receive_capture()
                self.assertFalse(hasattr(self.bridge, "native_capture"))

    def test_capture_truncated_or_oversized_packet_refuses_before_data_acceptance(self):
        for raw, flags in (
            (CAPTURE_PACKETS[0] + b"x" * (STREAM_BYTES + 1), 0),
            (CAPTURE_PACKETS[0], socket.MSG_TRUNC),
        ):
            with self.subTest(flags=flags):
                self.capture_fixture()
                if hasattr(self.bridge, "capture_packets"):
                    del self.bridge.capture_packets
                self.bridge.failed = False
                self.bridge.parent_channel.recvmsg.side_effect = None
                self.packet(raw=raw, flags=flags, count=0)
                with self.assertRaisesRegex(BridgeRefusal, "unknown original bridge"):
                    self.bridge.receive_capture()
                self.assertEqual(self.bridge.capture_packets, [])

    def test_terminal_transport_wait_uses_only_original_expiry_plus_fixed_grace(self):
        self.bridge.stage = 2
        self.bridge._verify_original = Mock()
        self.bridge.expires_ns = 102_000_000_000
        self.bridge.installation.reservation.batch_started = 0
        with (
            patch("crewshal.linux_bridge.time.monotonic", return_value=102.5),
            patch(
                "crewshal.linux_bridge.select.select",
                return_value=([self.bridge.parent_channel], [], []),
            ) as waiting,
        ):
            self.bridge._wait()
        self.assertEqual(waiting.call_args.args[3], 0.5)
        with (
            patch("crewshal.linux_bridge.time.monotonic", return_value=103),
            self.assertRaisesRegex(ValueError, "deadline exhausted"),
        ):
            self.bridge._wait()

    def test_verified_observer_stdin_duplicate_closes_before_ack_parent_writer_survives(self):
        # Ordinary pipes only; proc, pidfd, role and frozen binder checks are
        # explicitly mocked. EOF behavior uses actual retained file descriptors.
        read_end, parent_writer = os.pipe()
        self.addCleanup(os.close, read_end)
        self.addCleanup(os.close, parent_writer)
        observer_writer = os.dup(parent_writer)
        source, pidfd, stdout, stderr = (os.dup(self.root_fd) for _ in range(4))
        self.fds.extend((source, pidfd, stdout, stderr))
        native_fds = [source, pidfd, observer_writer, stdout, stderr]
        self.bridge.stage = 1
        self.bridge.received = [self.root_fd, *native_fds]
        self.bridge.handles = []
        self.bridge.host_proc = self.root_fd
        self.bridge.parent = SimpleNamespace(spec=SimpleNamespace(pid=2000, namespaces={}))
        self.bridge.watchdog = Mock()
        config = object()
        self.bridge.lifetime = SimpleNamespace(
            controls=SimpleNamespace(configuration=config, boot_id="fixture"),
            worker=SimpleNamespace(identity=object()),
            aggregate=SimpleNamespace(identity=object()),
        )
        self.bridge.installation.production = SimpleNamespace(
            _root_manifest=SimpleNamespace(
                root={"/opt/codex/bin/codex": SimpleNamespace(sha256="a" * 64)}
            )
        )
        self.bridge._wait = Mock()
        self.bridge._verify_original = Mock()
        self.bridge._packet = Mock(return_value=(NATIVE_PACKET, native_fds, (2000, 0, 0)))
        native = Mock()
        frozen = Mock()

        def acknowledge(raw):
            self.assertEqual(raw, b"1")
            with self.assertRaises(OSError):
                os.fstat(observer_writer)
            os.fstat(parent_writer)
            self.assertNotIn(observer_writer, self.bridge.received)
            return 1

        self.bridge.parent_channel.send.side_effect = acknowledge
        with (
            patch(
                "crewshal.linux_bridge._mapped_host_proc",
                return_value=(self.root_fd, 2001, 2000, 17),
            ),
            patch("crewshal.linux_bridge._read", return_value="synthetic"),
            patch(
                "crewshal.linux_bridge._stat_identity",
                side_effect=[(3, "T", 2, 17), (2, "S", 1, 11)],
            ),
            patch("crewshal.linux_bridge._namespaces", return_value={}),
            patch("crewshal.linux_bridge.record_digest", return_value="a" * 64),
            patch("crewshal.linux_bridge.NativeAdmissionSpec"),
            patch("crewshal.linux_bridge.RetainedProc", return_value=native),
            patch("crewshal.linux_bridge.bind_original_freeze", return_value=frozen),
        ):
            self.assertIs(self.bridge.receive_native(), frozen)
        self.assertEqual(self.bridge.stage, 2)
        self.assertEqual(self.bridge.closed_stdio[0], observer_writer)
        self.assertEqual(native.verify_pipes.call_count, 2)

    def test_sender_requires_actual_admitted_capture_and_original_terminal_owner(self):
        observation, sample, _ = self.capture_fixture()
        captured = CapturedProcess(observation, b"out", b"err", sample, sample, False, False)
        watchdog = object.__new__(OwnedWatchdogLifetime)
        admitted = object.__new__(AdmittedNative)
        object.__setattr__(admitted, "_captured_process", captured)
        watchdog.parent = SimpleNamespace(_native_handoff=(admitted, None, None, None, None))
        channel = Mock()
        endpoint = object.__new__(ParentBridgeEndpoint)
        endpoint.channel, endpoint.verify = channel, Mock()
        watchdog.parent._parent_bridge = endpoint
        watchdog.observed = SimpleNamespace(deadline=SimpleNamespace(expires_ns=102_000_000_000))
        watchdog._host_bridge = channel
        watchdog._host_native_bridge = admitted
        watchdog._native_capture = captured
        watchdog.verify_native_terminal = Mock()
        with patch("crewshal.linux_bridge._send") as sender:
            send_original_native_capture(channel, watchdog)
        self.assertEqual(sender.call_count, 3)
        self.assertEqual(
            [call.args[1].split(b"\0", 1)[0] + b"\0" for call in sender.call_args_list],
            list(CAPTURE_PACKETS),
        )
        self.assertTrue(
            all(call.args[2:] == ((), 103_000_000_000) for call in sender.call_args_list)
        )
        watchdog.verify_native_terminal.assert_called_with(admitted, 0)
        with self.assertRaisesRegex(ValueError, "consumed"):
            send_original_native_capture(channel, watchdog)

    def test_sender_reconstructed_capture_cannot_replace_actual_admitted_result(self):
        observation, sample, _ = self.capture_fixture()
        captured = CapturedProcess(observation, b"out", b"err", sample, sample, False, False)
        watchdog = object.__new__(OwnedWatchdogLifetime)
        admitted = object.__new__(AdmittedNative)
        object.__setattr__(admitted, "_captured_process", captured)
        watchdog.parent = SimpleNamespace(_native_handoff=(admitted, None, None, None, None))
        channel = Mock()
        endpoint = object.__new__(ParentBridgeEndpoint)
        endpoint.channel = channel
        watchdog.parent._parent_bridge = endpoint
        watchdog.observed = SimpleNamespace(deadline=SimpleNamespace(expires_ns=102_000_000_000))
        watchdog._host_bridge, watchdog._host_native_bridge = channel, admitted
        watchdog._native_capture = CapturedProcess(
            observation, b"out", b"err", sample, sample, False, False
        )
        with (
            patch("crewshal.linux_bridge._send") as sender,
            self.assertRaisesRegex(ValueError, "binding differs"),
        ):
            send_original_native_capture(channel, watchdog)
        sender.assert_not_called()
        self.assertIs(watchdog._host_capture_bridge, channel)


class Phase2DBridgeOrdinarySocket(unittest.TestCase):
    def test_actual_ordinary_fd_rights_preserve_file_identity(self):
        # Local IPC only; no fork, Linux proc, timer, mount or native execution.
        left, right = socket.socketpair(socket.AF_UNIX, socket.SOCK_DGRAM)
        self.addCleanup(left.close)
        self.addCleanup(right.close)
        with tempfile.TemporaryFile() as retained:
            right.send(b"1")
            _send(
                left, b"bounded packet", (retained.fileno(),), time.monotonic_ns() + 1_000_000_000
            )
            raw, ancillary, flags, _ = right.recvmsg(64, socket.CMSG_SPACE(array("i").itemsize))
            self.assertEqual(raw, b"bounded packet")
            self.assertFalse(flags & socket.MSG_CTRUNC)
            values = array("i")
            values.frombytes(ancillary[0][2])
            self.addCleanup(os.close, values[0])
            self.assertEqual(
                (os.fstat(values[0]).st_dev, os.fstat(values[0]).st_ino),
                (os.fstat(retained.fileno()).st_dev, os.fstat(retained.fileno()).st_ino),
            )

    def test_expired_sender_origin_performs_no_send(self):
        channel = Mock()
        with self.assertRaisesRegex(ValueError, "deadline exhausted"):
            _send(channel, b"packet", (), time.monotonic_ns() - 1)
        channel.sendmsg.assert_not_called()

    def test_wrong_acknowledgement_cannot_authorize_native_progress(self):
        channel = Mock()
        channel.sendmsg.return_value = 6
        channel.recv.return_value = b"0"
        with (
            patch(
                "crewshal.linux_bridge.select.select",
                side_effect=[([], [channel], []), ([channel], [], [])],
            ),
            self.assertRaisesRegex(ValueError, "acknowledgement"),
        ):
            _send(channel, b"packet", (), time.monotonic_ns() + 1_000_000_000)

    def test_prepare_failure_preserves_original_proof_and_proc_handle(self):
        proof = object.__new__(EffectiveInstallation)
        proof.verify_custody = Mock()
        proof.reservation = SimpleNamespace(
            observer=SimpleNamespace(spec=SimpleNamespace(pid=os.getpid(), boot_id="fixture")),
            batch_started=time.monotonic(),
            _retain_installation_refusal=Mock(),
        )
        with tempfile.TemporaryDirectory() as path:
            root = os.open(path, os.O_RDONLY | os.O_DIRECTORY)
            with (
                patch("crewshal.linux_bridge._proc_root", return_value=root),
                patch.object(socket, "SOCK_CLOEXEC", 0, create=True),
                patch.object(socket, "SOCK_NONBLOCK", 0, create=True),
                patch(
                    "crewshal.linux_bridge.socket.socketpair",
                    side_effect=OSError("synthetic socket refusal"),
                ),
                self.assertRaises(BridgeRefusal) as captured,
            ):
                prepare_stopped_native_bridge(proof)
            retained = getattr(proof, "_bridge")
            self.assertIs(captured.exception.bridge, retained)
            self.assertEqual(retained.host_proc, root)
            self.assertTrue(retained.failed)
            os.fstat(root)
            os.close(root)
        with self.assertRaisesRegex(ValueError, "consumed"):
            prepare_stopped_native_bridge(proof)

    def test_parent_endpoint_requires_fixed_original_fd_and_no_retry(self):
        parent = object.__new__(RetainedTrustedTask)
        parent.spec = SimpleNamespace(pid=os.getpid())
        controls = SimpleNamespace(setup=SimpleNamespace(bridge_control=False))
        with tempfile.TemporaryFile() as retained:
            duplicate = os.dup(retained.fileno())
            self.addCleanup(os.close, duplicate)
            with (
                patch("crewshal.linux_bridge.os.dup", return_value=duplicate),
                patch("crewshal.linux_bridge.os.close") as closing,
                self.assertRaisesRegex(ValueError, "fixed parent"),
            ):
                retain_parent_bridge(parent, controls)
            endpoint = getattr(parent, "_parent_bridge")
            self.assertTrue(endpoint.failed)
            self.assertEqual(endpoint.descriptor, duplicate)
            closing.assert_called_once_with(9)
            os.fstat(duplicate)
            with self.assertRaisesRegex(ValueError, "consumed"):
                retain_parent_bridge(parent, controls)
        with self.assertRaises(ValueError):
            ParentBridgeEndpoint()

    def test_parent_endpoint_pins_duplicate_then_checks_actual_socket_identity(self):
        # Ordinary datagram descriptors provide real socket inode/flag evidence;
        # Linux SEQPACKET/peer credentials and task readback are explicit mocks.
        left, right = socket.socketpair(socket.AF_UNIX, socket.SOCK_DGRAM)
        self.addCleanup(left.close)
        self.addCleanup(right.close)
        right.setblocking(False)
        duplicate = os.dup(right.fileno())
        actual_constructor = socket.socket
        owned_socket = actual_constructor(fileno=duplicate)
        self.addCleanup(owned_socket.close)
        observed = Mock(wraps=owned_socket)
        observed.getsockopt.side_effect = (
            lambda level, option, *args: socket.SOCK_SEQPACKET
            if option == socket.SO_TYPE
            else struct.pack("=iii", 0, 0, 0)
        )
        parent = object.__new__(RetainedTrustedTask)
        parent.spec = SimpleNamespace(pid=os.getpid(), configuration="0" * 64)
        parent.verify = Mock()
        identity = os.fstat(right.fileno())
        controls = SimpleNamespace(
            setup=SimpleNamespace(bridge_control=True),
            configuration=object(),
            bridge_identity=SimpleNamespace(device=identity.st_dev, inode=identity.st_ino),
            groups={"supervisor": object()},
        )
        with (
            patch("crewshal.linux_bridge.os.dup", return_value=duplicate),
            patch("crewshal.linux_bridge.os.close") as closing,
            patch("crewshal.linux_bridge.socket.socket", return_value=observed),
            patch.object(socket, "SO_PEERCRED", 100011, create=True),
            patch("crewshal.linux_bridge.record_digest", return_value="0" * 64),
        ):
            channel = retain_parent_bridge(parent, controls)
            self.assertIs(channel, observed)
            self.assertIs(parent._bridge_configuration, controls.configuration)
            self.assertEqual(parent._parent_bridge.descriptor, duplicate)
            closing.assert_called_once_with(9)
            parent._parent_bridge.verify()
            controls.bridge_identity.inode += 1
            with self.assertRaisesRegex(ValueError, "custody differs"):
                parent._parent_bridge.verify()
        os.fstat(duplicate)

    def test_sender_partial_packet_never_advances_to_ack(self):
        channel = Mock()
        channel.sendmsg.return_value = 1
        with (
            patch("crewshal.linux_bridge.select.select", return_value=([], [channel], [])),
            self.assertRaisesRegex(ValueError, "packet incomplete"),
        ):
            _send(channel, b"packet", (), time.monotonic_ns() + 1_000_000_000)
        channel.recv.assert_not_called()

    def test_fixed_fd_duplicate_failure_consumes_parent_without_closing_unknown_original(self):
        parent = object.__new__(RetainedTrustedTask)
        with (
            patch(
                "crewshal.linux_bridge.os.dup", side_effect=OSError("synthetic duplicate failure")
            ),
            patch("crewshal.linux_bridge.os.close") as closing,
            self.assertRaises(OSError),
        ):
            retain_parent_bridge(parent, Mock())
        self.assertTrue(parent._parent_bridge.failed)
        closing.assert_not_called()
        with self.assertRaisesRegex(ValueError, "consumed"):
            retain_parent_bridge(parent, Mock())


if __name__ == "__main__":
    unittest.main()
