"""Use original pipe FDs with explicit synthetic kernel pidfd readback seams."""

import json
import os
import pickle
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

from crewshal import linux_bridge as bridge_source
from crewshal.contracts import record_digest
from crewshal.linux_bridge import (
    QualificationTreeCustody,
    ObservedProbeActor,
    StoppedNativeBridge,
)
from tests.acceptance import test_phase_2d_setup as fixtures


class Phase2DProbeTransport(unittest.TestCase):
    def setUp(self):
        fixture = fixtures.Phase2DSetup()
        fixture.setUp()
        self.addCleanup(fixture.doCleanups)
        self.bridge = object.__new__(StoppedNativeBridge)
        self.bridge.parent = SimpleNamespace(spec=SimpleNamespace(pid=101))
        self.bridge.parent_channel = Mock()
        self.bridge.host_proc = 900
        self.bridge.origin_ns, self.bridge.expires_ns = 100, 5_000_000_100
        self.configuration = fixture.configuration.model_copy(update={"lane_id": "qualification-1"})
        self.worker = Mock()
        self.worker.sample.return_value = SimpleNamespace(populated=False, direct_pids=[])
        self.bridge.lifetime = SimpleNamespace(
            controls=SimpleNamespace(configuration=self.configuration), worker=self.worker
        )
        self.custody = object.__new__(QualificationTreeCustody)
        self.custody.bridge, self.custody.ordinal, self.custody.terminal = self.bridge, 1, True
        self.reading, self.writing = self.pipe()
        os.set_blocking(self.reading, False)
        self.launcher, launcher_writer = self.pipe()
        os.close(launcher_writer)
        self.descriptors = []
        actors = []
        for pid in (201, 202):
            proc = os.dup(fixture.parent.descriptor)
            self.addCleanup(os.close, proc)
            pidfd, writer = self.pipe()
            os.close(writer)
            actors.append(
                ObservedProbeActor(
                    proc,
                    pidfd,
                    pid,
                    pid + 10,
                    bridge_source._identity(proc),
                    bridge_source._identity(pidfd),
                )
            )
        self.custody.actors = actors[0], actors[1]
        self.custody.heartbeat, self.custody.launcher_pidfd = self.reading, self.launcher
        self.custody.identities = (
            bridge_source._identity(self.reading),
            bridge_source._identity(self.launcher),
        )
        self.custody._owners = self.bridge, 1, self.custody.actors
        self.custody._clock = 100, 5_000_000_100
        self.custody._configuration = record_digest(self.configuration)
        self.custody.heartbeat_bytes = self.custody._terminal_record = b"12"
        self.bridge.qualification_trees = [self.custody]
        self.pidfd_readback = patch.object(bridge_source, "_read", return_value=b"Pid:\t-1\n")
        self.pidfd_readback.start()
        self.addCleanup(self.pidfd_readback.stop)

    def pipe(self):
        reading, writing = os.pipe()
        self.addCleanup(os.close, reading)
        return reading, writing

    def close_heartbeat(self):
        os.close(self.writing)

    def test_terminal_requires_actual_eof_and_ready_retained_pidfds(self):
        self.close_heartbeat()
        self.custody.verify_terminal()
        self.worker.sample.assert_called_once_with()
        for actor in self.custody.actors:
            os.fstat(actor.pidfd)

    def test_parent_terminal_flag_cannot_replace_live_heartbeat_eof(self):
        self.addCleanup(os.close, self.writing)
        with self.assertRaises(BlockingIOError):
            self.custody.verify_terminal()
        self.assertTrue(self.custody.terminal)
        os.fstat(self.custody.heartbeat)

    def test_ready_pidfd_without_positive_reap_refuses(self):
        self.close_heartbeat()
        with patch.object(bridge_source, "_read", return_value=b"Pid:\t201\n"):
            with self.assertRaisesRegex(ValueError, "positive reap"):
                self.custody.verify_terminal()
        for actor in self.custody.actors:
            os.fstat(actor.pidfd)

    def test_terminal_requires_empty_original_worker(self):
        self.close_heartbeat()
        self.worker.sample.return_value = SimpleNamespace(populated=True, direct_pids=[333])
        with self.assertRaisesRegex(ValueError, "remains populated"):
            self.custody.verify_terminal()

    def test_changed_clock_configuration_or_capture_refuses(self):
        self.close_heartbeat()
        for name, value in (
            ("expires_ns", 6_000_000_100),
            ("heartbeat_bytes", b"11"),
            ("ordinal", 2),
        ):
            target = self.bridge if name == "expires_ns" else self.custody
            original = getattr(target, name)
            setattr(target, name, value)
            with self.assertRaisesRegex(ValueError, "custody changed"):
                self.custody.verify_terminal()
            setattr(target, name, original)
        self.configuration.lane_id = "live"
        with self.assertRaisesRegex(ValueError, "custody changed"):
            self.custody.verify_terminal()

    def test_terminal_packet_reads_original_pipe_and_sends_no_success_flag(self):
        self.custody.terminal = False
        self.custody.heartbeat_bytes = b""
        os.write(self.writing, b"1221")
        self.close_heartbeat()
        self.bridge._wait = Mock()
        self.bridge._packet = Mock(
            return_value=(
                json.dumps({"protocol": bridge_source.TREE_TERMINAL_PACKET, "ordinal": 1}).encode(),
                [],
                (101, 0, 0),
            )
        )
        self.bridge.parent_channel.send.return_value = 1
        bridge_source._receive_qualification_terminal(self.bridge, self.custody)
        self.assertEqual(self.custody.heartbeat_bytes, b"1221")
        self.bridge.parent_channel.send.assert_called_once_with(b"1")

    def test_unknown_terminal_rights_refuse_before_reading_heartbeat(self):
        self.custody.terminal = False
        os.write(self.writing, b"12")
        self.close_heartbeat()
        self.bridge._wait = Mock()
        self.bridge._packet = Mock(
            return_value=(
                json.dumps({"protocol": bridge_source.TREE_TERMINAL_PACKET, "ordinal": 1}).encode(),
                [12345],
                (101, 0, 0),
            )
        )
        with self.assertRaisesRegex(ValueError, "packet differs"):
            bridge_source._receive_qualification_terminal(self.bridge, self.custody)
        self.assertEqual(os.read(self.reading, 2), b"12")
        self.bridge.parent_channel.send.assert_not_called()

    def test_live_lane_cannot_receive_qualification_birth(self):
        self.close_heartbeat()
        self.configuration.lane_id = "live"
        self.bridge._wait = Mock()
        with self.assertRaisesRegex(ValueError, "sequence differs"):
            bridge_source._receive_qualification_birth(self.bridge, 1)
        self.bridge._wait.assert_not_called()

    def test_boolean_ordinal_cannot_replace_fixed_integer_frame(self):
        self.close_heartbeat()
        raw = json.dumps({"protocol": bridge_source.TREE_BIRTH_PACKET, "ordinal": True}).encode()
        self.assertFalse(bridge_source._probe_frame(raw, bridge_source.TREE_BIRTH_PACKET, 1))

    def test_retained_tree_cannot_be_serialized_as_authority(self):
        self.close_heartbeat()
        with self.assertRaises(TypeError):
            pickle.dumps(self.custody)


if __name__ == "__main__":
    unittest.main()
