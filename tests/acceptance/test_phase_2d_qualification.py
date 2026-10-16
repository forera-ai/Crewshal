"""Observe fixed probe ordering with explicit kernel seams. No child is started."""

import ctypes
import os
import socket
import struct
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

from crewshal.contracts import record_digest
from crewshal import linux_qualification as probes
from crewshal.linux_setup import OwnedWatchdogLifetime
from tests.acceptance import test_phase_2d_setup as fixtures


class Phase2DQualification(unittest.TestCase):
    def setUp(self):
        fixture = self.fixture = fixtures.Phase2DSetup()
        fixture.setUp()
        self.addCleanup(fixture.doCleanups)
        self.parent = fixture.parent
        configuration = fixture.configuration.model_copy(update={"lane_id": "qualification-1"})
        self.parent.spec = self.parent.spec.model_copy(
            update={"configuration": record_digest(configuration)}
        )
        self.parent.verify = Mock()
        self.parent._installed_controls = SimpleNamespace(
            configuration=configuration, bootstrap=fixture.preparation
        )
        self.watchdog = OwnedWatchdogLifetime(self.parent, fixture.worker, fixture.supervisor)
        self.deadline = SimpleNamespace(origin_ns=100, expires_ns=5_000_000_100)
        self.watchdog.observed = SimpleNamespace(deadline=self.deadline, check=Mock())
        self.watchdog.verify_native_binding = Mock()
        self.parent._watchdog_lifetime = self.watchdog
        libc = Mock()

        def prctl(operation, value, *_):
            if operation == 37:
                ctypes.cast(value, ctypes.POINTER(ctypes.c_int)).contents.value = 1
            return 0

        libc.prctl.side_effect = prctl
        with patch.object(probes.ctypes, "CDLL", return_value=libc):
            self.owner = probes.OriginalQualificationProbes(self.parent, self.watchdog)
        self.owner.worker.sample = Mock(
            return_value=SimpleNamespace(populated=False, direct_pids=[])
        )
        self.owner.worker.stop = Mock()

    def tree(self, *, eof=True, heartbeat=b"12"):
        channel, peer = socket.socketpair()
        self.addCleanup(channel.close)
        self.addCleanup(peer.close)
        reading, writing = os.pipe()
        self.addCleanup(os.close, reading)
        os.set_blocking(reading, False)
        os.write(writing, heartbeat)
        if eof:
            os.close(writing)
        else:
            self.addCleanup(os.close, writing)
        return probes.ProbeTree(channel, peer, reading, -1)

    def test_changed_original_deadline_refuses_without_new_effect_or_origin(self):
        self.deadline.expires_ns += 1
        with patch.object(self.owner, "_create") as create:
            with self.assertRaisesRegex(probes.QualificationProbeRefusal, "deadline changed"):
                self.owner.cancel_before_native()
        create.assert_not_called()
        self.owner.worker.stop.assert_not_called()
        self.assertEqual(self.owner.origin_ns, 100)
        self.assertTrue(self.owner.failed)

    def test_cancellation_precedes_native_and_is_consumed_after_one_tree(self):
        tree = self.tree()

        def create():
            self.owner.trees.append(tree)
            return tree

        with (
            patch.object(self.owner, "_create", side_effect=create),
            patch.object(
                self.owner,
                "_terminal",
                side_effect=lambda value, **_: setattr(value, "terminal", True),
            ),
        ):
            self.assertIs(self.owner.cancel_before_native(), tree)
            self.assertEqual((self.owner.origin_ns, self.owner.expires_ns), (100, 5_000_000_100))
            with self.assertRaisesRegex(probes.QualificationProbeRefusal, "precede"):
                self.owner.cancel_before_native()
        self.owner.worker.stop.assert_called_once_with()
        self.assertIs(self.owner.cancelled_tree, tree)

    def test_existing_native_handoff_refuses_pre_native_cancellation(self):
        self.parent._native_handoff = (object(),)
        with patch.object(self.owner, "_create") as create:
            with self.assertRaisesRegex(probes.QualificationProbeRefusal, "precede"):
                self.owner.cancel_before_native()
        create.assert_not_called()

    def test_deadline_tree_requires_completed_cancellation_and_sole_native(self):
        with patch.object(self.owner, "_create") as create:
            with self.assertRaisesRegex(probes.QualificationProbeRefusal, "completed"):
                self.owner.start_deadline_after_native(object())
        create.assert_not_called()

    def test_sole_native_admission_keeps_original_watchdog_before_second_tree(self):
        first = self.tree()
        first.terminal = True
        self.owner.cancelled_tree = first
        self.owner.trees.append(first)
        admitted = SimpleNamespace(
            proc=SimpleNamespace(
                verify_stopped=Mock(), read_configuration=Mock(), spec=SimpleNamespace(pid=123)
            )
        )
        self.owner.worker.sample.return_value = SimpleNamespace(populated=True, direct_pids=[123])
        second = self.tree()
        with patch.object(self.owner, "_create", return_value=second):
            self.assertIs(self.owner.start_deadline_after_native(admitted), second)
        self.watchdog.verify_native_binding.assert_called_once_with(admitted)
        self.assertIs(self.owner.deadline, self.deadline)
        self.assertEqual(self.deadline.origin_ns, 100)

    def test_unknown_positive_wait_keeps_all_tree_handles_and_refuses_terminal(self):
        tree = self.tree()
        tree.actors = [probes.ProbeActor(1, 111, 112, 123, 1, (1, 2), (1, 3))]
        with patch.object(probes.os, "waitpid", return_value=(0, 0)):
            with self.assertRaisesRegex(ValueError, "positive terminal wait"):
                self.owner._terminal(tree, deadline=False)
        self.assertFalse(tree.terminal)
        self.assertTrue(tree.eof)
        self.assertEqual(bytes(tree.bytes), b"12")
        self.assertEqual(tree.actors[0].pidfd, 112)

    def test_heartbeat_must_stop_and_cannot_use_a_bare_exit_flag(self):
        tree = self.tree(eof=False)
        with patch.object(probes.os, "waitpid") as wait:
            with self.assertRaisesRegex(ValueError, "heartbeat stop"):
                self.owner._terminal(tree, deadline=False)
        wait.assert_not_called()
        self.assertFalse(tree.terminal)

    def test_heartbeat_content_and_size_are_fixed(self):
        for content in (b"3", b"1" * 4097):
            tree = self.tree(heartbeat=content)
            with self.assertRaisesRegex(ValueError, "heartbeat"):
                self.owner._drain(tree)

    def test_both_ready_packets_bind_first_writes_without_consuming_original_pipe(self):
        tree = self.tree()
        original_channel = tree.channel
        tree.channel = Mock()
        tree.actors = [
            probes.ProbeActor(1, 111, 112, 123, 1, (1, 2), (1, 3)),
            probes.ProbeActor(2, 113, 114, 124, 2, (1, 4), (1, 5)),
        ]
        kind = getattr(socket, "SCM_CREDENTIALS", 2)
        tree.channel.recvmsg.side_effect = [
            (
                b"READY 2\n",
                [(socket.SOL_SOCKET, kind, struct.pack("3i", 124, 65534, 65534))],
                0,
                None,
            ),
            (
                b"READY 1\n",
                [(socket.SOL_SOCKET, kind, struct.pack("3i", 123, 65534, 65534))],
                0,
                None,
            ),
        ]
        with patch.object(
            probes,
            "_wait_ready",
            side_effect=lambda values, *_: (values if values == [tree.channel] else [], [], []),
        ):
            self.owner._ready(tree)
        self.assertEqual(tree.bytes, b"")
        self.assertEqual(os.read(tree.heartbeat, 2), b"12")
        self.assertEqual(tree.channel.recvmsg.call_count, 2)
        self.assertGreaterEqual(original_channel.fileno(), 0)

    def test_ready_sender_cannot_replace_original_actor_birth_identity(self):
        tree = self.tree()
        tree.channel = Mock()
        tree.actors = [probes.ProbeActor(1, 111, 112, 123, 1, (1, 2), (1, 3))]
        kind = getattr(socket, "SCM_CREDENTIALS", 2)
        tree.channel.recvmsg.return_value = (
            b"READY 1\n",
            [(socket.SOL_SOCKET, kind, struct.pack("3i", 999, 65534, 65534))],
            0,
            None,
        )
        with patch.object(
            probes,
            "_wait_ready",
            side_effect=lambda values, *_: (values if values == [tree.channel] else [], [], []),
        ):
            with self.assertRaisesRegex(ValueError, "first heartbeat custody"):
                self.owner._ready(tree)
        self.assertEqual(os.read(tree.heartbeat, 2), b"12")
        self.assertEqual(tree.actors[0].pidfd, 112)

    def test_deadline_requires_original_capture_and_actual_timeout(self):
        tree = self.tree()
        self.owner.deadline_tree = tree
        self.owner.admitted = object()
        captured = SimpleNamespace(
            observation=SimpleNamespace(termination=None, tree_stopped=True, exit_code=0)
        )
        self.watchdog._native_capture = captured
        with patch.object(self.owner, "_terminal") as terminal:
            with self.assertRaisesRegex(probes.QualificationProbeRefusal, "terminal timeout"):
                self.owner.finish_deadline(captured)
        terminal.assert_not_called()
        self.assertIs(self.owner.deadline_tree, tree)

    def test_positive_wait_pidfd_and_empty_worker_prove_terminal_tree(self):
        tree = self.tree()
        tree.actors = [
            probes.ProbeActor(1, 111, 112, 123, 1, (1, 2), (1, 3)),
            probes.ProbeActor(2, 113, 114, 124, 2, (1, 4), (1, 5)),
        ]
        tree.process = SimpleNamespace(poll=Mock(return_value=0))
        tree.launcher_pidfd = 115
        with (
            patch.object(probes.os, "waitpid", side_effect=[(123, 9), (124, 9)]) as wait,
            patch.object(probes, "_wait_ready", side_effect=lambda values, *_: (values, [], [])),
        ):
            self.owner._terminal(tree, deadline=False)
        self.assertEqual(wait.call_count, 2)
        self.assertTrue(tree.terminal)
        self.assertEqual([actor.wait_status for actor in tree.actors], [9, 9])
        self.assertEqual(bytes(tree.bytes), b"12")


if __name__ == "__main__":
    unittest.main()
