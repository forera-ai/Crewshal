"""Finite stopped-native FD custody between original parent and observer.

This preparation source creates no process and supplies no launch, spend,
release or retry authority. Its connected socket must be explicitly carried by
the installed namespace-parent control transport in an approved runtime batch.
"""

from array import array
import fcntl
import json
import os
import re
import select
import socket
import stat
import struct
import time
from types import SimpleNamespace
from typing import Literal, NoReturn, cast

from crewshal.admission import (
    AdmittedNative,
    NamespaceIdentity,
    NativeAdmissionSpec,
    RetainedProc,
    _fields,
    _read,
    _stat_identity,
)
from crewshal.contracts import record_digest
from crewshal.dispatch import DispatchConfiguration
from crewshal.linux_envelope import native_working_directory
from crewshal.linux_freeze import (
    OriginalVolumeFreeze,
    _verify_original_watchdog,
    bind_original_freeze,
)
from crewshal.linux_parent import RetainedTrustedTask, TrustedTaskSpec, _attach, _proc_root
from crewshal.linux_production import EffectiveInstallation, _filesystem_magic
from crewshal.linux_setup import (
    CAPABILITIES,
    InheritedControls,
    OwnedNamespaceSetup,
    OwnedWatchdogLifetime,
)
from crewshal.runtime import ProcessObservation, STREAM_BYTES
from crewshal.supervisor import CapturedProcess, CgroupSample


WATCHDOG_PACKET = "crewshal-original-watchdog-v1"
NATIVE_PACKET = b"crewshal-original-stopped-native-v1"
CAPTURE_PACKETS = (
    b"crewshal-original-capture-stdout-v1\0",
    b"crewshal-original-capture-stderr-v1\0",
    b"crewshal-original-capture-metadata-v1\0",
)
CONTROL_BYTES = 262_144


def _identity(descriptor: int) -> tuple[int, int]:
    info = os.fstat(descriptor)
    return info.st_dev, info.st_ino


class ParentBridgeEndpoint:
    """Original namespace parent retains its fixed FD9 custody before parsing."""

    parent: RetainedTrustedTask
    controls: InheritedControls
    descriptor: int
    channel: socket.socket
    identity: tuple[int, int]
    failed: bool
    configuration_digest: str

    def __init__(self) -> None:
        raise ValueError("parent bridge requires actual inherited original FD")

    def __reduce__(self) -> NoReturn:
        raise TypeError("original parent bridge cannot be copied or exported")

    def verify(self) -> None:
        info = os.fstat(self.descriptor)
        expected = getattr(self.controls, "bridge_identity", None)
        if (
            self.failed
            or getattr(self.parent, "_parent_bridge", None) is not self
            or getattr(self.parent, "_bridge_channel", None) is not self.channel
            or expected is None
            or (expected.device, expected.inode) != self.identity
            or _identity(self.descriptor) != self.identity
            or not stat.S_ISSOCK(info.st_mode)
            or self.channel.fileno() != self.descriptor
            or self.channel.getsockopt(socket.SOL_SOCKET, socket.SO_TYPE) != socket.SOCK_SEQPACKET
            or fcntl.fcntl(self.descriptor, fcntl.F_GETFL) & (os.O_ACCMODE | os.O_NONBLOCK)
            != os.O_RDWR | os.O_NONBLOCK
            or record_digest(self.controls.configuration) != self.configuration_digest
            or self.parent.spec.configuration != self.configuration_digest
            or getattr(self.parent, "_bridge_configuration", None)
            is not self.controls.configuration
        ):
            raise ValueError("original parent bridge FD/configuration custody differs")
        peer = self.channel.getsockopt(socket.SOL_SOCKET, getattr(socket, "SO_PEERCRED"), 12)
        if len(peer) != 12 or struct.unpack("=iii", peer)[1:] != (0, 0):
            raise ValueError("original parent bridge peer credentials differ")
        self.parent.verify(self.controls.groups["supervisor"])


def retain_parent_bridge(parent: RetainedTrustedTask, controls: InheritedControls) -> socket.socket:
    """Retain fixed FD9 once; no SQLite, reservation or serialized live owner."""
    if type(parent) is not RetainedTrustedTask or hasattr(parent, "_parent_bridge"):
        raise ValueError("original inherited parent bridge consumed or missing")
    endpoint = object.__new__(ParentBridgeEndpoint)
    endpoint.parent, endpoint.controls, endpoint.failed = parent, controls, False
    setattr(parent, "_parent_bridge", endpoint)
    try:
        endpoint.descriptor = os.dup(9)
        endpoint.identity = _identity(endpoint.descriptor)
        if not controls.setup.bridge_control or parent.spec.pid != os.getpid():
            raise ValueError("original fixed parent bridge role missing")
        endpoint.channel = socket.socket(fileno=endpoint.descriptor)
        endpoint.configuration_digest = record_digest(controls.configuration)
        setattr(parent, "_bridge_channel", endpoint.channel)
        setattr(parent, "_bridge_configuration", controls.configuration)
        endpoint.verify()
        return endpoint.channel
    except BaseException:
        endpoint.failed = True
        raise
    finally:
        # Only the normalized transport original closes after its duplicate is
        # retained. Unknown endpoints/descriptors survive on the original parent.
        if hasattr(endpoint, "descriptor"):
            os.close(9)


def _namespaces(descriptor: int) -> dict[str, NamespaceIdentity]:
    result = {}
    for name in ("mnt", "net", "pid", "user", "time"):
        info = os.stat("ns/" + name, dir_fd=descriptor)
        result[name] = NamespaceIdentity(device=info.st_dev, inode=info.st_ino)
    return result


def _mapped_host_proc(
    root: int, source: int, pidfd: int, retained: list[int]
) -> tuple[int, int, int, int]:
    """Derive host PID from the actual pidfd, then check both procfs views.

    Distinct procfs superblocks may assign distinct device/inode to one task.
    Pin each actual view independently; kernel pidfd/NSpid/start/namespace
    agreement supplies the cross-view binding, never packet PID text.
    """
    before = _identity(source)
    if _filesystem_magic(source) != 0x9FA0:
        raise ValueError("received task FD is not actual procfs")
    pid, state, parent, start = _stat_identity(_read(source, "stat"))
    fields = _fields(_read(root, f"self/fdinfo/{pidfd}"))
    host_text = fields.get("Pid", "")
    mapping = fields.get("NSpid", "").split()
    if (
        not re.fullmatch(r"[1-9][0-9]*", host_text)
        or not mapping
        or any(not re.fullmatch(r"[1-9][0-9]*", value) for value in mapping)
        or mapping[0] != host_text
        or int(mapping[-1]) != pid
        or state not in ("R", "S", "T")
        or start <= 0
        or select.select([pidfd], [], [], 0)[0]
    ):
        raise ValueError("original pidfd namespace mapping/liveness differs")
    host_pid = int(host_text)
    descriptor = os.open(
        str(host_pid), os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC, dir_fd=root
    )
    retained.append(descriptor)
    actual = _identity(descriptor)
    observed, host_state, host_parent, ticks = _stat_identity(_read(descriptor, "stat"))
    source_status = _fields(_read(source, "status"))
    host_status = _fields(_read(descriptor, "status"))
    if (
        observed != host_pid
        or ticks != start
        or host_state != state
        or source_status.get("Pid") != str(pid)
        or source_status.get("Tgid") != str(pid)
        or source_status.get("PPid") != str(parent)
        or host_status.get("Pid") != host_text
        or host_status.get("Tgid") != host_text
        or host_status.get("PPid") != str(host_parent)
        or host_status.get("NSpid", "").split() != mapping
        or source_status.get("NSpid", "").split() != [str(pid)]
        or _namespaces(source) != _namespaces(descriptor)
        or before != _identity(source)
        or actual != _identity(descriptor)
        or select.select([pidfd], [], [], 0)[0]
        or _fields(_read(root, f"self/fdinfo/{pidfd}")) != fields
    ):
        raise ValueError("original host/namespace proc inode/start mapping differs")
    return descriptor, host_pid, host_parent, start


def _wrapper_ancestry(
    root: int, ancestor: int, lifetime: OwnedNamespaceSetup, retained: list[int]
) -> None:
    wrapper = lifetime.wrapper
    if wrapper is None or wrapper.poll() is not None:
        raise ValueError("original namespace wrapper must remain live")
    for _ in range(8):
        descriptor, pidfd = _attach(root, ancestor)
        retained.extend((descriptor, pidfd))
        observed, state, parent, start = _stat_identity(_read(descriptor, "stat"))
        if (
            observed != ancestor
            or state not in ("R", "S")
            or start <= 0
            or select.select([pidfd], [], [], 0)[0]
        ):
            raise ValueError("original namespace wrapper ancestry unknown")
        if ancestor == wrapper.pid:
            return
        ancestor = parent
    raise ValueError("original parent is outside retained wrapper ancestry")


def _send(
    channel: socket.socket, raw: bytes, descriptors: tuple[int, ...], deadline_ns: int
) -> None:
    remaining = (deadline_ns - time.monotonic_ns()) / 1_000_000_000
    if remaining <= 0 or not select.select([], [channel], [], remaining)[1]:
        raise ValueError("original watchdog bridge send deadline exhausted")
    ancillary = (
        [(socket.SOL_SOCKET, socket.SCM_RIGHTS, array("i", descriptors))] if descriptors else []
    )
    if channel.sendmsg([raw], ancillary) != len(raw):
        raise ValueError("original bridge FD packet incomplete")
    remaining = (deadline_ns - time.monotonic_ns()) / 1_000_000_000
    if (
        remaining <= 0
        or not select.select([channel], [], [], remaining)[0]
        or channel.recv(2) != b"1"
    ):
        raise ValueError("original watchdog bridge acknowledgement unavailable")


def send_watchdog_bridge(channel: socket.socket, watchdog: OwnedWatchdogLifetime) -> None:
    """Send original armed watchdog before starting its direct native child."""
    if type(watchdog) is not OwnedWatchdogLifetime or hasattr(watchdog, "_host_bridge"):
        raise ValueError("original watchdog bridge consumed or missing")
    setattr(watchdog, "_host_bridge", channel)
    parent, observed = watchdog.parent, watchdog.observed
    endpoint = getattr(parent, "_parent_bridge", None)
    if type(endpoint) is not ParentBridgeEndpoint or endpoint.channel is not channel:
        raise ValueError("watchdog bridge requires original inherited parent endpoint")
    endpoint.verify()
    if (
        observed is None
        or watchdog.task is not observed.task
        or watchdog.process is None
        or parent.spec.pid != os.getpid()
        or getattr(parent, "_watchdog_lifetime", None) is not watchdog
    ):
        raise ValueError("original parent/watchdog bridge binding differs")
    observed.check(watchdog.worker, _watchdog_configuration(watchdog))
    parent.verify(watchdog.supervisor.identity)
    raw = json.dumps(
        {
            "protocol": WATCHDOG_PACKET,
            "origin_ns": observed.deadline.origin_ns,
            "expires_ns": observed.deadline.expires_ns,
        },
        separators=(",", ":"),
    ).encode("ascii")
    _send(
        channel,
        raw,
        (parent.descriptor, parent.pidfd, observed.task.descriptor, observed.task.pidfd),
        observed.deadline.expires_ns,
    )
    observed.check(watchdog.worker, _watchdog_configuration(watchdog))


def _watchdog_configuration(watchdog: OwnedWatchdogLifetime) -> DispatchConfiguration:
    """The finite parent entry must retain its original configuration object."""
    from crewshal.dispatch import DispatchConfiguration

    configuration = getattr(watchdog.parent, "_bridge_configuration", None)
    if (
        type(configuration) is not DispatchConfiguration
        or record_digest(configuration) != watchdog.parent.spec.configuration
    ):
        raise ValueError("original parent bridge configuration missing or changed")
    return configuration


def send_stopped_native_bridge(
    channel: socket.socket, admitted: AdmittedNative, watchdog: OwnedWatchdogLifetime
) -> None:
    """Transfer original stopped-native custody, preserving the existing origin."""
    if (
        type(admitted) is not AdmittedNative
        or type(watchdog) is not OwnedWatchdogLifetime
        or getattr(watchdog, "_host_bridge", None) is not channel
        or hasattr(watchdog, "_host_native_bridge")
    ):
        raise ValueError("original stopped-native bridge consumed or missing")
    setattr(watchdog, "_host_native_bridge", admitted)
    watchdog.verify_native_binding(admitted)
    endpoint = getattr(watchdog.parent, "_parent_bridge", None)
    if type(endpoint) is not ParentBridgeEndpoint or endpoint.channel is not channel:
        raise ValueError("native bridge requires original inherited parent endpoint")
    endpoint.verify()
    observed = watchdog.observed
    if (
        observed is None
        or admitted.child.stdin is None
        or admitted.child.stdout is None
        or admitted.child.stderr is None
    ):
        raise ValueError("original native bridge stdio/watchdog custody missing")
    observed.check(admitted.worker, admitted.configuration)
    admitted.proc.verify_stopped()
    admitted.proc.read_configuration(admitted.configuration)
    pipes = (
        admitted.child.stdin.fileno(),
        admitted.child.stdout.fileno(),
        admitted.child.stderr.fileno(),
    )
    admitted.proc.verify_pipes(*pipes)
    _send(
        channel,
        NATIVE_PACKET,
        (admitted.proc.descriptor, admitted.proc.pidfd, *pipes),
        observed.deadline.expires_ns,
    )
    observed.check(admitted.worker, admitted.configuration)
    admitted.proc.verify_stopped()


def send_original_native_capture(channel: socket.socket, watchdog: OwnedWatchdogLifetime) -> None:
    """Transfer bounded data after original native/watchdog exit and reap.

    The sender retains its actual capture; data and caller observation flags
    supply no terminal, physical release or reuse authority at the observer.
    """
    if (
        type(watchdog) is not OwnedWatchdogLifetime
        or getattr(watchdog, "_host_bridge", None) is not channel
        or hasattr(watchdog, "_host_capture_bridge")
    ):
        raise ValueError("original native capture transport consumed or missing")
    setattr(watchdog, "_host_capture_bridge", channel)
    endpoint = getattr(watchdog.parent, "_parent_bridge", None)
    anchor = getattr(watchdog.parent, "_native_handoff", None)
    captured = getattr(watchdog, "_native_capture", None)
    if (
        type(endpoint) is not ParentBridgeEndpoint
        or endpoint.channel is not channel
        or anchor is None
        or len(anchor) != 5
        or type(anchor[0]) is not AdmittedNative
        or type(captured) is not CapturedProcess
        or getattr(anchor[0], "_captured_process", None) is not captured
        or getattr(watchdog, "_host_native_bridge", None) is not anchor[0]
        or watchdog.observed is None
        or captured.observation.exit_code is None
        or type(captured.stdout) is not bytes
        or type(captured.stderr) is not bytes
        or max(len(captured.stdout), len(captured.stderr)) > STREAM_BYTES
    ):
        raise ValueError("original retained native capture binding differs")
    endpoint.verify()
    watchdog.verify_native_terminal(anchor[0], captured.observation.exit_code)
    metadata = json.dumps(
        {
            "observation": captured.observation.model_dump(mode="json"),
            "initial": captured.initial.model_dump(mode="json"),
            "final": captured.final.model_dump(mode="json") if captured.final is not None else None,
            "overflow": captured.overflow,
            "stop_error": captured.stop_error,
        },
        separators=(",", ":"),
        allow_nan=False,
    ).encode("ascii")
    if len(metadata) > STREAM_BYTES:
        raise ValueError("original capture metadata exceeds charged bound")
    deadline = watchdog.observed.deadline.expires_ns + 1_000_000_000
    for prefix, payload in zip(CAPTURE_PACKETS, (captured.stdout, captured.stderr, metadata)):
        endpoint.verify()
        watchdog.verify_native_terminal(anchor[0], captured.observation.exit_code)
        _send(channel, prefix + payload, (), deadline)
    watchdog.verify_native_terminal(anchor[0], captured.observation.exit_code)


class BridgeRefusal(ValueError):
    def __init__(self, reason: str, bridge: "StoppedNativeBridge"):
        super().__init__(reason)
        self.bridge = bridge
        self.resources_reusable = False


class StoppedNativeBridge:
    """Two FD and three capture packets in original bounded observer custody."""

    resources_reusable: Literal[False] = False
    installation: EffectiveInstallation
    received: list[int]
    handles: list[int]
    parent_channel: socket.socket
    child_channel: socket.socket
    failed: bool
    stage: int
    host_proc: int
    lifetime: OwnedNamespaceSetup
    parent: RetainedTrustedTask
    watchdog: RetainedTrustedTask
    native: RetainedProc
    origin_ns: int
    expires_ns: int
    freeze: OriginalVolumeFreeze
    native_capture: CapturedProcess
    capture_packets: list[bytes]
    _capture_owner: CapturedProcess
    _capture_streams: tuple[bytes, bytes]
    _capture_records: tuple[str, str, str | None, bool, bool]
    closed_stdio: tuple[int, tuple[int, int]]
    _socket_identities: tuple[tuple[int, int], tuple[int, int]]
    _host_proc_identity: tuple[int, int]
    _deadline: tuple[int, int]
    _parent_owners: tuple[RetainedTrustedTask, RetainedTrustedTask]
    _parent_specs: tuple[str, str]

    def __init__(self) -> None:
        raise ValueError("bridge requires original installed observer custody")

    def __reduce__(self) -> NoReturn:
        raise TypeError("original bridge custody cannot be copied or exported")

    def _verify_original(self) -> None:
        proof = self.installation
        if self.failed or getattr(proof, "_bridge", None) is not self:
            raise ValueError("original bridge consumed or changed")
        proof.verify_custody()
        if hasattr(self, "_socket_identities") and (
            (_identity(self.parent_channel.fileno()), _identity(self.child_channel.fileno()))
            != self._socket_identities
            or self.parent_channel.getsockopt(socket.SOL_SOCKET, socket.SO_TYPE)
            != socket.SOCK_SEQPACKET
            or self.child_channel.getsockopt(socket.SOL_SOCKET, socket.SO_TYPE)
            != socket.SOCK_SEQPACKET
            or not all(
                stat.S_ISSOCK(os.fstat(channel.fileno()).st_mode)
                for channel in (self.parent_channel, self.child_channel)
            )
            or _identity(self.host_proc) != self._host_proc_identity
            or self.parent_channel.getsockopt(socket.SOL_SOCKET, getattr(socket, "SO_PASSCRED"))
            != 1
            or any(
                fcntl.fcntl(channel.fileno(), fcntl.F_GETFL) & (os.O_ACCMODE | os.O_NONBLOCK)
                != os.O_RDWR | os.O_NONBLOCK
                for channel in (self.parent_channel, self.child_channel)
            )
        ):
            raise ValueError("original retained bridge sockets/proc identity changed")
        if proof.reservation.observer.spec.pid != os.getpid():
            raise ValueError("bridge requires original outer observer")
        if time.monotonic() >= proof.reservation.batch_started + 570:
            raise ValueError("original bridge cutoff expired")
        if hasattr(self, "lifetime"):
            lifetime = self.lifetime
            if (
                type(lifetime) is not OwnedNamespaceSetup
                or lifetime.controls.configuration != proof.reservation._configuration
                or lifetime.controls.boot_id != proof.reservation.observer.spec.boot_id
                or lifetime.aggregate is not proof.reservation.aggregate
                or lifetime.worker is not proof.reservation._batch_timer.worker
                or lifetime.setup is not proof.reservation._batch_timer.setup
                or lifetime.supervisor is not proof.reservation._batch_timer.supervisor
                or lifetime.observer_group is not proof.reservation.observer_group
                or getattr(proof.reservation, "_setup_lifetime", None) is not lifetime
                or lifetime.storage_reservation is not proof.reservation
                or lifetime.wrapper is None
                or lifetime.wrapper.poll() is not None
            ):
                raise ValueError("original bridge namespace lifetime differs")
        # Capture transport consumes only the original attempt and grace. Once
        # that transport finished, retained-data/freeze work uses the original
        # batch cutoff above; it still requires independent terminal readback
        # below and cannot reopen transport, restart native or renew grace.
        if self.stage in (1, 2):
            deadline = self.expires_ns + (1_000_000_000 if self.stage == 2 else 0)
            if not self.origin_ns <= time.monotonic_ns() < deadline:
                raise ValueError("original native/grace bridge deadline expired")
        if self.stage:
            if (
                not hasattr(self, "_deadline")
                or (self.origin_ns, self.expires_ns) != self._deadline
                or not hasattr(self, "_parent_owners")
                or self._parent_owners != (self.parent, self.watchdog)
                or self._parent_specs
                != (record_digest(self.parent.spec), record_digest(self.watchdog.spec))
            ):
                raise ValueError("original observed watchdog clock/task custody changed")
            self.parent.verify(self.lifetime.supervisor.identity)
            if self.stage < 2:
                self.watchdog.verify(self.lifetime.supervisor.identity)
            else:
                self.watchdog.verify_handles()
            if self.stage >= 3:
                self._verify_capture_data()
                self.freeze._verify_terminal_kernel()

    def _verify_capture_data(self) -> None:
        captured = self.native_capture
        if (
            captured is not self._capture_owner
            or captured.stdout is not self._capture_streams[0]
            or captured.stderr is not self._capture_streams[1]
            or self.capture_packets[0] is not captured.stdout
            or self.capture_packets[1] is not captured.stderr
            or self._capture_records
            != (
                captured.observation.model_dump_json(),
                captured.initial.model_dump_json(),
                captured.final.model_dump_json() if captured.final is not None else None,
                captured.overflow,
                captured.stop_error,
            )
        ):
            raise ValueError("original retained native capture changed")

    def verify_capture(self) -> None:
        """Check retained data immutability and independent original kernel state."""
        if self.stage != 3 or not hasattr(self, "native_capture"):
            raise ValueError("original terminal capture missing")
        try:
            self._verify_capture_data()
            self._verify_original()
            self.freeze.verify_custody()
            self.freeze._verify_terminal_kernel()
        except BaseException as error:
            self._refuse(error)

    def _packet(self, bound: int = 4096) -> tuple[bytes, list[int], tuple[int, int, int]]:
        raw, ancillary, flags, _ = self.parent_channel.recvmsg(
            bound,
            socket.CMSG_SPACE(16 * array("i").itemsize) + socket.CMSG_SPACE(12),
            getattr(socket, "MSG_CMSG_CLOEXEC"),
        )
        received: list[int] = []
        credentials: list[tuple[int, int, int]] = []
        malformed = False
        for level, kind, data in ancillary:
            if level == socket.SOL_SOCKET and kind == socket.SCM_RIGHTS:
                values = array("i")
                malformed |= bool(len(data) % values.itemsize)
                values.frombytes(data[: len(data) - len(data) % values.itemsize])
                for descriptor in values:
                    self.received.append(descriptor)
                    received.append(descriptor)
            elif (
                level == socket.SOL_SOCKET
                and kind == getattr(socket, "SCM_CREDENTIALS")
                and len(data) == 12
            ):
                credentials.append(struct.unpack("=iii", data))
            else:
                malformed = True
        if (
            malformed
            or len(raw) > bound
            or flags & (socket.MSG_TRUNC | socket.MSG_CTRUNC)
            or len(credentials) != 1
            or credentials[0][1:] != (0, 0)
            or len(self.received) > 32
        ):
            raise ValueError("unknown original bridge packet/credentials retained")
        return raw, received, credentials[0]

    def _wait(self) -> None:
        self._verify_original()
        # Before receiving the existing armed timer, use only the original
        # preparation cutoff. The first packet installs no renewed attempt clock.
        deadline = (
            min(
                self.installation.reservation.batch_started + 120,
                self.installation.reservation.batch_started + 570,
            )
            if self.stage == 0
            else min(
                (self.expires_ns + (1_000_000_000 if self.stage >= 2 else 0)) / 1_000_000_000,
                self.installation.reservation.batch_started + 570,
            )
        )
        remaining = deadline - time.monotonic()
        if remaining <= 0 or not select.select([self.parent_channel], [], [], remaining)[0]:
            raise ValueError("original bridge readiness deadline exhausted")

    def receive_watchdog(self, lifetime: OwnedNamespaceSetup) -> None:
        if self.stage != 0 or hasattr(self, "lifetime"):
            raise BridgeRefusal("original watchdog packet consumed; no retry", self)
        self.lifetime = lifetime
        try:
            self._wait()
            raw, received, credentials = self._packet()
            data = json.loads(raw)
            if (
                set(data) != {"protocol", "origin_ns", "expires_ns"}
                or data["protocol"] != WATCHDOG_PACKET
                or any(type(data[name]) is not int for name in ("origin_ns", "expires_ns"))
                or data["expires_ns"] - data["origin_ns"] != 5_000_000_000
                or len(received) != 4
            ):
                raise ValueError("original watchdog packet framing differs")
            self.origin_ns, self.expires_ns = data["origin_ns"], data["expires_ns"]
            parent_source, parent_pidfd, watchdog_source, watchdog_pidfd = received
            parent_fd, parent_pid, parent_parent, parent_start = _mapped_host_proc(
                self.host_proc, parent_source, parent_pidfd, self.handles
            )
            wd_fd, wd_pid, wd_parent, wd_start = _mapped_host_proc(
                self.host_proc, watchdog_source, watchdog_pidfd, self.handles
            )
            controls = lifetime.controls
            configuration = controls.configuration
            if (
                credentials[0] != parent_pid
                or wd_parent != parent_pid
                or _stat_identity(_read(watchdog_source, "stat"))[2]
                != _stat_identity(_read(parent_source, "stat"))[0]
            ):
                raise ValueError("original parent/watchdog sender ancestry differs")
            namespaces = _namespaces(parent_fd)
            if (
                any(
                    namespaces[name] == controls.outer_namespaces[name]
                    for name in ("mnt", "net", "pid")
                )
                or _namespaces(wd_fd) != namespaces
            ):
                raise ValueError("original parent/watchdog namespace separation differs")
            common = dict(
                configuration=record_digest(configuration),
                boot_id=controls.boot_id,
                cgroup=lifetime.supervisor.identity,
                namespaces=namespaces,
                environment={},
                cwd=native_working_directory(configuration),
            )
            self.parent = RetainedTrustedTask(
                parent_fd,
                parent_pidfd,
                TrustedTaskSpec.model_validate(
                    {
                        **common,
                        "pid": parent_pid,
                        "parent_pid": parent_parent,
                        "start_ticks": parent_start,
                        "executable": controls.setup.parent_executable,
                        "argv": controls.setup.parent_argv,
                        "capabilities": CAPABILITIES,
                    }
                ),
            )
            helper = controls.bootstrap.policy.helper_binary
            if helper is None:
                raise ValueError("original installed watchdog helper missing")
            self.watchdog = RetainedTrustedTask(
                wd_fd,
                watchdog_pidfd,
                TrustedTaskSpec.model_validate(
                    {
                        **common,
                        "pid": wd_pid,
                        "parent_pid": wd_parent,
                        "start_ticks": wd_start,
                        "executable": helper,
                        "argv": controls.bootstrap.watchdog_argv,
                        "capabilities": "0" * 16,
                    }
                ),
            )
            self.parent.verify(lifetime.supervisor.identity)
            self.watchdog.verify(lifetime.supervisor.identity)
            _wrapper_ancestry(self.host_proc, parent_parent, lifetime, self.handles)
            # Reuse only the effect-free kernel decoder. This view has no freeze
            # ownership, job or projection and cannot pass freeze custody.
            watchdog_view = SimpleNamespace(
                watchdog=self.watchdog, parent=self.parent, lifetime=lifetime
            )
            _verify_original_watchdog(cast(OriginalVolumeFreeze, watchdog_view))
            if set(lifetime.supervisor._read("cgroup.procs").split()) != {
                str(parent_pid),
                str(wd_pid),
            }:
                raise ValueError("original watchdog bridge supervisor population differs")
            sample = lifetime.worker.sample()
            if sample.populated or sample.direct_pids:
                raise ValueError("original watchdog bridge requires empty worker")
            before = time.monotonic_ns()
            timer = _fields(_read(wd_fd, "fdinfo/6"))
            after = time.monotonic_ns()
            match = re.fullmatch(r"\(([0-9]+), ([0-9]+)\)", timer.get("it_value", ""))
            if match is None:
                raise ValueError("original effective watchdog timer unavailable")
            seconds, nanos = (int(value) for value in match.groups())
            remaining = seconds * 1_000_000_000 + nanos
            if (
                timer.get("clockid") != "1"
                or timer.get("ticks") != "0"
                or timer.get("settime flags") != "01"
                or timer.get("it_interval") != "(0, 0)"
                or not 0 < remaining <= 5_000_000_000
                or nanos >= 1_000_000_000
                or not before + remaining <= self.expires_ns <= after + remaining
            ):
                raise ValueError("packet origin differs from original actual watchdog timer")
            self.stage = 1
            self._deadline = (self.origin_ns, self.expires_ns)
            self._parent_owners = (self.parent, self.watchdog)
            self._parent_specs = (
                record_digest(self.parent.spec),
                record_digest(self.watchdog.spec),
            )
            self._verify_original()
            if self.parent_channel.send(b"1") != 1:
                raise ValueError("original watchdog bridge acknowledgement refused")
        except BaseException as error:
            self._refuse(error)

    def receive_native(self) -> OriginalVolumeFreeze:
        if self.stage != 1 or hasattr(self, "native"):
            raise BridgeRefusal("original native packet consumed or missing; no retry", self)
        try:
            self._wait()
            raw, received, credentials = self._packet()
            if raw != NATIVE_PACKET or len(received) != 5 or credentials[0] != self.parent.spec.pid:
                raise ValueError("original stopped-native packet framing/sender differs")
            source, pidfd, *pipe_list = received
            descriptor, pid, parent, start = _mapped_host_proc(
                self.host_proc, source, pidfd, self.handles
            )
            lifetime, configuration = self.lifetime, self.lifetime.controls.configuration
            if (
                parent != self.parent.spec.pid
                or _stat_identity(_read(source, "stat"))[2]
                != _stat_identity(_read(self.received[0], "stat"))[0]
            ):
                raise ValueError("original stopped native is outside its retained parent")
            namespaces = _namespaces(descriptor)
            if namespaces != self.parent.spec.namespaces:
                raise ValueError("original native namespaces differ from parent")
            executable = self.installation.production._root_manifest.root[
                "/opt/codex/bin/codex"
            ].sha256
            if executable is None:
                raise ValueError("original installed native executable missing")
            spec = NativeAdmissionSpec(
                configuration=record_digest(configuration),
                pid=pid,
                parent_pid=parent,
                start_ticks=start,
                boot_id=lifetime.controls.boot_id,
                worker=lifetime.worker.identity,
                aggregate=lifetime.aggregate.identity,
                namespaces={name: value for name, value in namespaces.items() if name != "time"},
                executable_sha256=executable,
            )
            self.native = RetainedProc(descriptor, pidfd, spec)
            self.native.verify_stopped()
            self.native.read_configuration(configuration)
            pipes = (pipe_list[0], pipe_list[1], pipe_list[2])
            self.native.verify_pipes(*pipes)
            self._verify_original()
            self.freeze = bind_original_freeze(
                self.installation, lifetime, self.parent, self.native, self.watchdog, pipes
            )
            self._verify_original()
            # This positively verified transport duplicate would otherwise keep
            # app-server stdin open after the original parent closes its writer.
            # Record its exact identity, remove its numeric FD from every live
            # keep-set, then close only that known redundant stdio duplicate.
            stdio_identity = _identity(pipes[0])
            self.native.verify_pipes(*pipes)
            os.close(pipes[0])
            self.received.remove(pipes[0])
            self.closed_stdio = (pipes[0], stdio_identity)
            self.stage = 2
            if self.parent_channel.send(b"1") != 1:
                raise ValueError("original native bridge acknowledgement refused")
            return self.freeze
        except BaseException as error:
            self._refuse(error)

    def receive_capture(self) -> CapturedProcess:
        """Consume three bounded data packets; kernel readback gates retention."""
        if self.stage != 2 or hasattr(self, "capture_packets"):
            raise BridgeRefusal("original native capture consumed or missing; no retry", self)
        self.capture_packets = []
        try:
            for prefix in CAPTURE_PACKETS:
                self._wait()
                raw, descriptors, credentials = self._packet(STREAM_BYTES + len(prefix))
                # Unknown SCM_RIGHTS were retained by _packet before refusal.
                if (
                    descriptors
                    or credentials[0] != self.parent.spec.pid
                    or not raw.startswith(prefix)
                    or len(raw) - len(prefix) > STREAM_BYTES
                ):
                    raise ValueError("original capture packet framing/sender/rights differs")
                self.capture_packets.append(raw[len(prefix) :])
                if sum(len(value) for value in self.capture_packets) > CONTROL_BYTES:
                    raise ValueError("original capture exceeds charged control bound")
                if prefix != CAPTURE_PACKETS[-1] and self.parent_channel.send(b"1") != 1:
                    raise ValueError("original capture acknowledgement refused")
            data = json.loads(self.capture_packets[2])
            if (
                type(data) is not dict
                or set(data) != {"observation", "initial", "final", "overflow", "stop_error"}
                or any(type(data[key]) is not bool for key in ("overflow", "stop_error"))
            ):
                raise ValueError("original capture metadata framing differs")
            observation = ProcessObservation.model_validate_json(json.dumps(data["observation"]))
            initial = CgroupSample.model_validate(data["initial"])
            final = (
                CgroupSample.model_validate(data["final"]) if data["final"] is not None else None
            )
            if (
                initial.identity != self.lifetime.worker.identity
                or (final is not None and final.identity != self.lifetime.worker.identity)
                or observation.exit_code is None
            ):
                raise ValueError("original capture worker/exit observation differs")
            self._verify_original()
            self.freeze.verify_custody()
            # Observation.tree_stopped, serialized exit and cgroup samples never
            # substitute for original host pidfds, positive reap and sole parent.
            self.freeze._verify_terminal_kernel()
            captured = CapturedProcess(
                observation,
                self.capture_packets[0],
                self.capture_packets[1],
                initial,
                final,
                data["overflow"],
                data["stop_error"],
            )
            self.native_capture = self._capture_owner = captured
            self._capture_streams = (captured.stdout, captured.stderr)
            self._capture_records = (
                observation.model_dump_json(),
                initial.model_dump_json(),
                final.model_dump_json() if final is not None else None,
                captured.overflow,
                captured.stop_error,
            )
            if (
                sum(len(value) for value in self.capture_packets)
                + sum(
                    len(value.encode("utf-8"))
                    for value in self._capture_records[:3]
                    if value is not None
                )
                > CONTROL_BYTES
            ):
                raise ValueError("original retained capture exceeds charged control bound")
            self.stage = 3
            self._verify_original()
            if self.parent_channel.send(b"1") != 1:
                raise ValueError("original terminal capture acknowledgement refused")
            return captured
        except BaseException as error:
            self._refuse(error)

    def _refuse(self, error: BaseException) -> NoReturn:
        self.failed = True
        self.installation.reservation._retain_installation_refusal(error)
        raise BridgeRefusal(str(error), self) from error


def prepare_stopped_native_bridge(installation: EffectiveInstallation) -> StoppedNativeBridge:
    """Pin connected custody before namespace launch; no second owner or clock."""
    if type(installation) is not EffectiveInstallation or hasattr(installation, "_bridge"):
        raise ValueError("original installed bridge unavailable or consumed")
    bridge = object.__new__(StoppedNativeBridge)
    bridge.installation = installation
    bridge.received, bridge.handles, bridge.failed, bridge.stage = [], [], False, 0
    setattr(installation, "_bridge", bridge)
    try:
        bridge._verify_original()
        bridge.host_proc = _proc_root(installation.reservation.observer.spec.boot_id)
        bridge._host_proc_identity = _identity(bridge.host_proc)
        flags = (
            socket.SOCK_SEQPACKET
            | getattr(socket, "SOCK_CLOEXEC")
            | getattr(socket, "SOCK_NONBLOCK")
        )
        bridge.parent_channel, bridge.child_channel = socket.socketpair(socket.AF_UNIX, flags)
        bridge.parent_channel.setsockopt(socket.SOL_SOCKET, getattr(socket, "SO_PASSCRED"), 1)
        bridge._socket_identities = (
            _identity(bridge.parent_channel.fileno()),
            _identity(bridge.child_channel.fileno()),
        )
        bridge._verify_original()
        return bridge
    except BaseException as error:
        bridge._refuse(error)
