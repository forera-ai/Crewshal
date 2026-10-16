"""Offline entry and receipt checks use fresh FDs and synthetic Linux observations."""

from array import array
import json
import os
import socket
import struct
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

from crewshal.linux_bridge import (
    ParentBridgeEndpoint,
    StoppedNativeBridge,
    VALIDATOR_VIEW_PACKET,
    receive_validator_views,
)
from crewshal.linux_parent_entry import main
from tests.acceptance import test_phase_2d_parent as parent_fixtures


class Phase2DOriginalAdmissionTransport(unittest.TestCase):
    def setUp(self):
        fixture = parent_fixtures.Phase2DParent()
        fixture.setUp()
        self.addCleanup(fixture.doCleanups)
        self.fixture = fixture
        self.admitted = fixture.stage()
        self.addCleanup(self.admitted.proc.close)
        bridge = self.bridge = object.__new__(StoppedNativeBridge)
        bridge.native = self.admitted.proc
        bridge.lifetime = SimpleNamespace(
            configuration=self.admitted.configuration,
            controls=SimpleNamespace(configuration=self.admitted.configuration),
            worker=self.admitted.worker,
            aggregate=self.admitted.aggregate,
        )
        bridge.origin_ns = fixture.owned.deadline.origin_ns
        self.pipes = tuple(
            stream.fileno()
            for stream in (
                self.admitted.child.stdin,
                self.admitted.child.stdout,
                self.admitted.child.stderr,
            )
        )

    def bind(self, receipt=None):
        self.bridge._bind_admission(
            receipt or self.admitted.receipt, self.admitted.proc.descriptor, self.pipes
        )

    def test_original_receipt_matches_independent_retained_proc_and_actual_pipes(self):
        self.bind()
        self.assertEqual(self.bridge.verify_admission(), self.admitted.receipt)
        self.assertEqual(self.bridge._admission_digest, self.admitted.receipt_digest)

    def test_namespace_receipt_changed_identity_refuses(self):
        receipt = self.admitted.receipt.model_copy(deep=True)
        receipt.spec.start_ticks += 1
        with self.assertRaisesRegex(ValueError, "independent readback"):
            self.bind(receipt)
        self.assertFalse(hasattr(self.bridge, "admission_receipt"))

    def test_namespace_receipt_changed_clock_refuses_without_renewing_origin(self):
        receipt = self.admitted.receipt.model_copy(deep=True)
        receipt.started_monotonic += 1
        with self.assertRaisesRegex(ValueError, "independent readback"):
            self.bind(receipt)
        self.assertEqual(self.bridge.origin_ns, self.fixture.owned.deadline.origin_ns)

    def test_namespace_receipt_wrong_argv_environment_or_controls_refuses(self):
        for name, value in (
            ("argv", "0" * 64),
            ("initial_environment", "0" * 64),
            ("aggregate_controls", {}),
        ):
            with self.subTest(name=name):
                receipt = self.admitted.receipt.model_copy(deep=True)
                setattr(receipt, name, value)
                with self.assertRaisesRegex(ValueError, "independent readback"):
                    self.bind(receipt)

    def test_transport_receipt_mutation_refuses_journal_linkage(self):
        self.bind()
        self.bridge.admission_receipt.argv = "0" * 64
        with self.assertRaisesRegex(ValueError, "missing or changed"):
            self.bridge.verify_admission()

    def test_host_proc_rebinding_refuses_journal_linkage(self):
        self.bind()
        self.bridge.native.spec.pid += 1
        with self.assertRaisesRegex(ValueError, "missing or changed"):
            self.bridge.verify_admission()


class Phase2DInstalledEntry(unittest.TestCase):
    def entry(self, *, isolated=1, environment=None, platform="linux"):
        return (
            patch(
                "crewshal.linux_parent_entry.sys.flags",
                SimpleNamespace(isolated=isolated, no_site=1, dont_write_bytecode=1),
            ),
            patch("crewshal.linux_parent_entry.sys.platform", platform),
            patch(
                "crewshal.linux_parent_entry.sys.argv",
                ["/opt/crewshal/lib/crewshal/linux_parent_entry.py"],
            ),
            patch.dict(os.environ, environment or {}, clear=True),
        )

    def test_entry_refuses_nonisolated_before_imported_operational_function(self):
        a, b, c, d = self.entry(isolated=0)
        with a, b, c, d, patch("crewshal.linux_parent.run_installed_namespace_parent") as run:
            with self.assertRaises(ValueError):
                main()
            run.assert_not_called()

    def test_entry_refuses_ambient_environment(self):
        a, b, c, d = self.entry(environment={"HOME": "/ambient"})
        with a, b, c, d, patch("crewshal.linux_parent.run_installed_namespace_parent") as run:
            with self.assertRaises(ValueError):
                main()
            run.assert_not_called()

    def test_entry_uses_one_fixed_import_path_and_one_finite_call(self):
        a, b, c, d = self.entry()
        path = []
        with (
            a,
            b,
            c,
            d,
            patch("crewshal.linux_parent_entry.sys.path", path),
            patch("crewshal.linux_parent.run_installed_namespace_parent") as run,
        ):
            main()
            self.assertEqual(path, ["/opt/crewshal/lib"])
            run.assert_called_once()
            self.assertFalse(run.call_args.kwargs["cancelled"]())


class Phase2DValidatorViewTransfer(unittest.TestCase):
    def setUp(self):
        self.fds = [os.open("/", os.O_RDONLY | os.O_DIRECTORY) for _ in range(3)]
        for fd in self.fds:
            self.addCleanup(os.close, fd)
        self.parent = SimpleNamespace()
        endpoint = self.endpoint = object.__new__(ParentBridgeEndpoint)
        endpoint.verify = Mock()
        endpoint.channel = Mock()
        endpoint.received = []
        self.parent._parent_bridge = endpoint
        self.controls = SimpleNamespace(batch_origin_ns=1, configuration=SimpleNamespace())
        endpoint.channel.send.return_value = 1

    def receive(self, *, uid=0, extra=False, protocol=VALIDATOR_VIEW_PACKET):
        ancillary = [
            (
                socket.SOL_SOCKET,
                socket.SCM_RIGHTS,
                array("i", self.fds if extra else self.fds[:2]).tobytes(),
            ),
            (socket.SOL_SOCKET, 100099, struct.pack("=iii", 0, uid, 0)),
        ]
        self.endpoint.channel.recvmsg.return_value = (
            json.dumps(
                {
                    "protocol": protocol,
                    "configuration": "a" * 64,
                    "manifest": {"schema_version": 1, "files": []},
                }
            ).encode(),
            ancillary,
            0,
            None,
        )
        with (
            patch.object(socket, "SCM_CREDENTIALS", 100099, create=True),
            patch.object(socket, "MSG_CMSG_CLOEXEC", 0, create=True),
            patch("crewshal.linux_bridge.time.monotonic_ns", return_value=2),
            patch(
                "crewshal.linux_bridge._wait_ready",
                return_value=([self.endpoint.channel], [], []),
            ),
            patch("crewshal.linux_bridge.record_digest", return_value="a" * 64),
        ):
            return receive_validator_views(
                self.parent,
                self.controls,
                Mock(),
                {name: Mock() for name in ("validator", "supervisor", "aggregate")},
            )

    def test_wrong_credentials_retains_received_fds_before_refusal(self):
        with patch("crewshal.linux_validator.prepare_validator_attempt") as prepare:
            with self.assertRaisesRegex(ValueError, "credentials differ"):
                self.receive(uid=65534)
            self.assertEqual(self.endpoint.received, self.fds[:2])
            prepare.assert_not_called()
            self.endpoint.channel.send.assert_not_called()

    def test_extra_rights_retains_all_unknown_descriptors(self):
        with self.assertRaisesRegex(ValueError, "rights or credentials"):
            self.receive(extra=True)
        self.assertEqual(self.endpoint.received, self.fds)
        for fd in self.fds:
            os.fstat(fd)

    def test_bad_protocol_retains_actual_views_and_consumes_attempt(self):
        with self.assertRaisesRegex(ValueError, "identity differs"):
            self.receive(protocol="forged")
        self.assertTrue(self.endpoint.failed)
        self.assertEqual(self.endpoint.received, self.fds[:2])
        with self.assertRaisesRegex(ValueError, "consumed"):
            self.receive()

    def test_success_ack_follows_original_attempt_readback(self):
        events = []
        self.endpoint.channel.send.side_effect = lambda raw: events.append("ack") or 1
        result = object()
        with patch(
            "crewshal.linux_validator.prepare_validator_attempt",
            side_effect=lambda *args: events.append("readback") or result,
        ):
            self.assertIs(self.receive(), result)
        self.assertEqual(events, ["readback", "ack"])
        self.assertEqual(self.endpoint.received, self.fds[:2])


class Phase2DCleanInstalledRoot(unittest.TestCase):
    def setUp(self):
        from crewshal.linux_inventory import RetainedParentInventory

        self.descriptor = os.open("/", os.O_RDONLY | os.O_DIRECTORY)
        self.addCleanup(os.close, self.descriptor)
        self.owner = object.__new__(RetainedParentInventory)
        self.owner.descriptor = self.descriptor
        info = os.fstat(self.descriptor)
        self.owner.identity = info.st_dev, info.st_ino
        self.path = "/owned/readonly-root"
        self.device = f"{os.major(info.st_dev)}:{os.minor(info.st_dev)}"

    def verify(self, *, mount="7", tail="", link=None):
        actual_open = os.open

        def opened(path, *args, **kwargs):
            return (
                os.dup(self.descriptor) if path == "/proc" else actual_open(path, *args, **kwargs)
            )

        def read(root, name):
            return (
                f"mnt_id:\t{mount}\n"
                if name.startswith("self/fdinfo/")
                else f"{mount} 0 {self.device} / {self.path} ro - ext4 x ro\n{tail}"
            ).encode()

        with (
            patch("crewshal.linux_inventory.os.open", side_effect=opened),
            patch("crewshal.admission._read", side_effect=read),
            patch(
                "crewshal.linux_inventory.os.fstatvfs",
                return_value=SimpleNamespace(f_flag=os.ST_RDONLY),
            ),
            patch("crewshal.linux_inventory.os.readlink", return_value=link or self.path),
        ):
            self.owner.verify_clean_current_mount(self.path)

    def test_clean_readonly_current_mount_binds_one_original_mount_id(self):
        self.verify()
        self.assertEqual(self.owner._clean_mount, (self.path, "7"))
        self.verify()

    def test_same_inode_different_mount_id_refuses(self):
        self.verify()
        with self.assertRaisesRegex(ValueError, "mount identity changed"):
            self.verify(mount="8")
        self.assertEqual(self.owner._clean_mount, (self.path, "7"))

    def test_parent_root_source_overmount_refuses(self):
        with self.assertRaisesRegex(ValueError, "overmount"):
            self.verify(tail=f"8 7 {self.device} / {self.path}/candidate rw - ext4 x rw\n")
        self.assertFalse(hasattr(self.owner, "_clean_mount"))

    def test_changed_source_path_refuses_with_original_fd_retained(self):
        with self.assertRaisesRegex(ValueError, "current mount differs"):
            self.verify(link="/different-root")
        os.fstat(self.descriptor)


class Phase2DValidatorObserverTerminal(unittest.TestCase):
    def setUp(self):
        from crewshal.linux_bridge import ValidatorBridgeCustody
        from crewshal.admission import NamespaceIdentity
        from crewshal.contracts import record_digest

        self.custody = object.__new__(ValidatorBridgeCustody)
        bridge = self.bridge = SimpleNamespace(failed=False)
        self.custody.bridge = bridge
        bridge._validator_custody = self.custody
        bridge.parent = SimpleNamespace(spec=SimpleNamespace(pid=20), verify=Mock())
        self.custody.proc = SimpleNamespace(pidfd=30, verify_exited=Mock())
        self.custody.watchdog = SimpleNamespace(pidfd=31, verify_handles=Mock())
        self.custody.proc.spec = NamespaceIdentity(device=1, inode=30)
        self.custody.watchdog.spec = NamespaceIdentity(device=1, inode=31)
        self.custody.origin_ns, self.custody.expires_ns = 1, 5_000_000_001
        self.custody.observed_argv = [
            "/bin/python3",
            "-I",
            "-B",
            "/input/check_fixture.py",
            "/candidate/owned",
        ]
        self.custody.observed_environment = "a" * 64
        self.custody.observed_toolchain = "b" * 64
        self.custody._owners = bridge, self.custody.proc, self.custody.watchdog
        self.custody._specs = (
            record_digest(self.custody.proc.spec),
            record_digest(self.custody.watchdog.spec),
        )
        self.custody._clock = self.custody.origin_ns, self.custody.expires_ns
        self.custody._check_inputs = (
            tuple(self.custody.observed_argv),
            self.custody.observed_environment,
            self.custody.observed_toolchain,
        )
        bridge.host_proc = 40
        sample = SimpleNamespace(
            populated=False, direct_pids=[], memory_events={"oom": 0}, pids_events={"max": 0}
        )
        self.sample = sample
        bridge.lifetime = SimpleNamespace(
            validator=SimpleNamespace(sample=Mock(return_value=sample)),
            supervisor=SimpleNamespace(identity=object(), _read=Mock(return_value="20")),
        )
        bridge.freeze = SimpleNamespace(verify_projection=Mock())

    def verify(self, *, pid="-1", exited=True):
        with (
            patch(
                "crewshal.linux_bridge._wait_ready", return_value=([31] if exited else [], [], [])
            ),
            patch("crewshal.linux_bridge._read", return_value=f"Pid:\t{pid}\n".encode()),
        ):
            self.custody.verify_terminal()

    def test_terminal_requires_both_pidfd_exit_and_positive_reap(self):
        self.verify()
        self.assertEqual(self.custody.proc.verify_exited.call_count, 2)
        self.bridge.freeze.verify_projection.assert_called_once()

    def test_zombie_pidfd_readiness_cannot_supply_positive_reap(self):
        with self.assertRaisesRegex(ValueError, "positive reap"):
            self.verify(pid="30")
        self.bridge.freeze.verify_projection.assert_not_called()

    def test_unobserved_watchdog_exit_refuses(self):
        with self.assertRaisesRegex(ValueError, "watchdog terminal exit"):
            self.verify(exited=False)

    def test_repopulated_validator_role_refuses(self):
        self.sample.populated = True
        self.sample.direct_pids = [30]
        with self.assertRaisesRegex(ValueError, "terminal role differs"):
            self.verify()

    def test_another_supervisor_task_refuses_terminal_result(self):
        self.bridge.lifetime.supervisor._read.return_value = "20 21"
        with self.assertRaisesRegex(ValueError, "sole live"):
            self.verify()


class Phase2DOriginalValidatorStageTransition(unittest.TestCase):
    def setUp(self):
        from crewshal.candidate import FrozenCandidate

        self.fd = os.open("/", os.O_RDONLY | os.O_DIRECTORY)
        self.addCleanup(os.close, self.fd)
        bridge = self.bridge = object.__new__(StoppedNativeBridge)
        bridge.failed = False
        bridge.verify_capture = Mock()
        bridge.verify_admission = Mock()
        bridge.parent_channel = Mock()
        bridge.lifetime = SimpleNamespace(controls=SimpleNamespace(configuration=object()))
        bridge.freeze = SimpleNamespace(
            verify_projection=Mock(),
            manifest=FrozenCandidate(files=[]),
            handles={"readonly-projection": self.fd},
        )
        bridge.installation = SimpleNamespace(
            production=SimpleNamespace(handles={"mounted:validator-scratch-upper": self.fd}),
            reservation=SimpleNamespace(batch_started=1, _retain_installation_refusal=Mock()),
        )

    def test_view_ack_may_start_next_watchdog_without_requiring_idle_supervisor_again(self):
        from crewshal.linux_bridge import send_validator_views

        def transfer(*args):
            self.bridge.freeze.verify_projection.side_effect = ValueError(
                "validator watcher is now present"
            )

        with (
            patch("crewshal.linux_bridge.record_digest", return_value="a" * 64),
            patch("crewshal.linux_bridge._send", side_effect=transfer) as send,
        ):
            send_validator_views(self.bridge)
        self.bridge.freeze.verify_projection.assert_called_once()
        self.bridge.verify_capture.assert_called_once()
        self.assertEqual(send.call_args.args[2], (self.fd, self.fd))
        self.assertEqual(send.call_args.args[3], 571_000_000_000)

    def test_failed_view_transfer_keeps_original_charge_and_consumed_marker(self):
        from crewshal.linux_bridge import BridgeRefusal, send_validator_views

        with (
            patch("crewshal.linux_bridge.record_digest", return_value="a" * 64),
            patch(
                "crewshal.linux_bridge._send", side_effect=ValueError("synthetic transfer failure")
            ),
        ):
            with self.assertRaisesRegex(BridgeRefusal, "transfer failure"):
                send_validator_views(self.bridge)
        self.assertTrue(self.bridge.failed)
        self.assertTrue(self.bridge._validator_views_sent)
        self.bridge.installation.reservation._retain_installation_refusal.assert_called_once()
        os.fstat(self.fd)
