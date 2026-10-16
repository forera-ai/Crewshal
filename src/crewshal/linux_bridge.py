"""Finite stopped-native FD custody between original parent and observer.

This preparation source creates no process and supplies no launch, spend,
release or retry authority. Its connected socket must be explicitly carried by
the installed namespace-parent control transport in an approved runtime batch.
"""

from array import array
import ctypes
from dataclasses import dataclass
import fcntl
import json
import os
import re
import socket
import stat
import struct
import time
from types import SimpleNamespace
from typing import TYPE_CHECKING, Literal, NoReturn, cast

from crewshal.admission import _wait_ready
from crewshal.admission import (
    AdmittedNative,
    NamespaceIdentity,
    NativeAdmissionReceipt,
    NativeAdmissionSpec,
    _aggregate_readback,
    RetainedProc,
    _fields,
    _read,
    _stat_identity,
)
from crewshal.contracts import Digest, record_digest
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
    RetainedLaneSetup,
    retained_setup_scope,
    retained_lane_handle,
)
from crewshal.runtime import ProcessObservation, STREAM_BYTES
from crewshal.supervisor import CapturedProcess, CgroupSample


if TYPE_CHECKING:
    from crewshal.linux_inventory import RetainedParentInventory
    from crewshal.linux_validator import AdmittedValidator, RetainedValidatorProc, ValidatorAttempt
    from crewshal.supervisor import OwnedCgroup
    from crewshal.linux_qualification import OriginalQualificationProbes, ProbeTree


WATCHDOG_PACKET = "crewshal-original-watchdog-v1"
NATIVE_PACKET = b"crewshal-original-stopped-native-v2"
CAPTURE_PACKETS = (
    b"crewshal-original-capture-stdout-v1\0",
    b"crewshal-original-capture-stderr-v1\0",
    b"crewshal-original-capture-metadata-v1\0",
)
CONTROL_BYTES = 262_144
TREE_BIRTH_PACKET = "crewshal-original-qualification-tree-birth-v1"
TREE_TERMINAL_PACKET = "crewshal-original-qualification-tree-terminal-v1"


def _qualification_lane(bridge: "StoppedNativeBridge") -> bool:
    lifetime = getattr(bridge, "lifetime", None)
    controls = getattr(lifetime, "controls", None)
    configuration = getattr(controls, "configuration", None)
    return getattr(configuration, "lane_id", None) in ("qualification-1", "qualification-2")


def send_qualification_tree_birth(owner: "OriginalQualificationProbes", tree: "ProbeTree") -> None:
    """Transfer actual stopped actors before any release or cancellation."""
    from crewshal.linux_qualification import OriginalQualificationProbes, ProbeTree

    endpoint = getattr(owner.parent, "_parent_bridge", None)
    if (
        type(owner) is not OriginalQualificationProbes
        or type(tree) is not ProbeTree
        or type(endpoint) is not ParentBridgeEndpoint
        or getattr(owner.parent, "_qualification_probes", None) is not owner
        or not any(tree is item for item in owner.trees)
        or tree.birth_transferred
        or len(tree.actors) != 2
        or tree.launcher_pidfd < 0
    ):
        raise ValueError("original qualification tree birth custody differs")
    endpoint.verify()
    owner._check()
    ordinal = next(index for index, item in enumerate(owner.trees, 1) if item is tree)
    if ordinal not in (1, 2):
        raise ValueError("original qualification tree ordinal differs")
    for actor in tree.actors:
        if _stat_identity(_read(actor.descriptor, "stat"))[1] != "T":
            raise ValueError("qualification birth transfer requires actual stopped actors")
    raw = json.dumps(
        {"protocol": TREE_BIRTH_PACKET, "ordinal": ordinal}, separators=(",", ":")
    ).encode("ascii")
    _send(
        endpoint.channel,
        raw,
        (
            tree.actors[0].descriptor,
            tree.actors[0].pidfd,
            tree.actors[1].descriptor,
            tree.actors[1].pidfd,
            tree.heartbeat,
            tree.launcher_pidfd,
        ),
        owner.expires_ns,
    )
    tree.birth_transferred = True
    owner._check()


def send_qualification_tree_terminal(
    owner: "OriginalQualificationProbes", tree: "ProbeTree"
) -> None:
    """Request independent terminal readback without sending success flags."""
    from crewshal.linux_qualification import OriginalQualificationProbes, ProbeTree

    endpoint = getattr(owner.parent, "_parent_bridge", None)
    if (
        type(owner) is not OriginalQualificationProbes
        or type(tree) is not ProbeTree
        or type(endpoint) is not ParentBridgeEndpoint
        or not any(tree is item for item in owner.trees)
        or not tree.birth_transferred
        or not tree.terminal
        or tree.terminal_transferred
    ):
        raise ValueError("original qualification tree terminal custody differs")
    endpoint.verify()
    ordinal = next(index for index, item in enumerate(owner.trees, 1) if item is tree)
    owner._check(terminal=ordinal == 2)
    raw = json.dumps(
        {"protocol": TREE_TERMINAL_PACKET, "ordinal": ordinal}, separators=(",", ":")
    ).encode("ascii")
    _send(endpoint.channel, raw, (), owner.expires_ns + (1_000_000_000 if ordinal == 2 else 0))
    tree.terminal_transferred = True


@dataclass(frozen=True)
class ObservedProbeActor:
    descriptor: int
    pidfd: int
    pid: int
    start_ticks: int
    proc_identity: tuple[int, int]
    pidfd_identity: tuple[int, int]


class QualificationTreeCustody:
    """Retain stopped host identities and read terminal kernel state independently."""

    def __init__(self) -> None:
        raise ValueError("qualification custody requires original birth FD transfer")

    def __reduce__(self) -> NoReturn:
        raise TypeError("original qualification observer custody cannot be exported")

    bridge: "StoppedNativeBridge"
    ordinal: int
    actors: tuple[ObservedProbeActor, ObservedProbeActor]
    heartbeat: int
    launcher_pidfd: int
    identities: tuple[tuple[int, int], tuple[int, int]]
    terminal: bool
    heartbeat_bytes: bytes
    _terminal_record: bytes
    _owners: tuple["StoppedNativeBridge", int, tuple[ObservedProbeActor, ObservedProbeActor]]
    _clock: tuple[int, int]
    _configuration: str

    def verify_terminal(self) -> None:
        bridge = self.bridge
        owners = getattr(bridge, "qualification_trees", ())
        if (
            not self.terminal
            or self not in owners
            or (bridge.origin_ns, bridge.expires_ns) != self._clock
            or record_digest(bridge.lifetime.controls.configuration) != self._configuration
            or self._owners != (bridge, self.ordinal, self.actors)
            or self.heartbeat_bytes != self._terminal_record
            or not 0 < len(self.heartbeat_bytes) <= 4096
            or set(self.heartbeat_bytes) != {49, 50}
            or (_identity(self.heartbeat), _identity(self.launcher_pidfd)) != self.identities
        ):
            raise ValueError("original qualification terminal custody changed or unknown")
        for actor in self.actors:
            if (
                _identity(actor.descriptor) != actor.proc_identity
                or _identity(actor.pidfd) != actor.pidfd_identity
                or not _wait_ready([actor.pidfd], [], [], 0)[0]
                or _fields(_read(bridge.host_proc, f"self/fdinfo/{actor.pidfd}")).get("Pid") != "-1"
            ):
                raise ValueError(
                    "original qualification actor exit or positive reap remains unknown"
                )
        if (
            not _wait_ready([self.launcher_pidfd], [], [], 0)[0]
            or _fields(_read(bridge.host_proc, f"self/fdinfo/{self.launcher_pidfd}")).get("Pid")
            != "-1"
        ):
            raise ValueError(
                "original qualification launcher exit or positive reap remains unknown"
            )
        sample = bridge.lifetime.worker.sample()
        if sample.populated or sample.direct_pids:
            raise ValueError("original qualification terminal worker remains populated")
        # EOF comes from the retained original pipe, never a parent flag.
        if os.read(self.heartbeat, 1) != b"":
            raise ValueError("original qualification heartbeat terminal EOF differs")


def _probe_frame(raw: bytes, protocol: str, ordinal: int) -> bool:
    data = json.loads(raw)
    return (
        type(data) is dict
        and set(data) == {"protocol", "ordinal"}
        and data["protocol"] == protocol
        and type(data["ordinal"]) is int
        and data["ordinal"] == ordinal
    )


def _receive_qualification_birth(
    bridge: "StoppedNativeBridge", ordinal: int
) -> QualificationTreeCustody:
    owners = getattr(bridge, "qualification_trees", None)
    if owners is None:
        owners = bridge.qualification_trees = []
    if not _qualification_lane(bridge) or len(owners) != ordinal - 1:
        raise ValueError("original qualification birth sequence differs")
    custody = object.__new__(QualificationTreeCustody)
    custody.bridge, custody.ordinal, custody.terminal = bridge, ordinal, False
    owners.append(custody)  # Retain incomplete custody before parsing.
    bridge._wait()
    raw, descriptors, credentials = bridge._packet()
    if (
        not _probe_frame(raw, TREE_BIRTH_PACKET, ordinal)
        or time.monotonic_ns() >= bridge.expires_ns
        or len(descriptors) != 6
        or credentials[0] != bridge.parent.spec.pid
    ):
        raise ValueError("original qualification birth packet differs")
    first, first_pidfd, second, second_pidfd, heartbeat, launcher = descriptors
    actors = []
    parents = []
    worker = bridge.lifetime.worker
    for source, pidfd in ((first, first_pidfd), (second, second_pidfd)):
        descriptor, pid, parent, ticks = _mapped_host_proc(
            bridge.host_proc, source, pidfd, bridge.handles
        )
        status = _fields(_read(descriptor, "status"))
        argv = _read(descriptor, "cmdline").split(b"\0")
        if argv and argv[-1] == b"":
            argv.pop()
        if (
            _stat_identity(_read(descriptor, "stat"))[1] != "T"
            or _namespaces(descriptor) != bridge.parent.spec.namespaces
            or status.get("Uid", "").split() != ["65534"] * 4
            or status.get("Gid", "").split() != ["65534"] * 4
            or status.get("Groups", "").split() not in ([], ["65534"])
            or status.get("NoNewPrivs") != "1"
            or status.get("Threads") != "1"
            or any(
                status.get(key) != "0000000000000000"
                for key in ("CapInh", "CapPrm", "CapEff", "CapBnd", "CapAmb")
            )
            or _read(descriptor, "environ") != b""
            or len(argv) != 4
            or argv[:2] != [b"/bin/crewshal-bootstrap", b"--qualification-tree-fds"]
            or any(not re.fullmatch(rb"[1-9][0-9]*", value) for value in argv[2:])
            or str(pid) not in worker._read("cgroup.procs").split()
        ):
            raise ValueError("actual qualification actor birth or placement differs")
        from crewshal.linux_parent import _image

        helper = bridge.lifetime.controls.bootstrap.policy.helper_binary
        if helper is None:
            raise ValueError("original qualification helper identity is missing")
        _image(descriptor, helper)
        stat_fields = _read(descriptor, "stat").rsplit(b") ", 1)[1].split()
        if stat_fields[2:4] != [str(pid).encode("ascii")] * 2:
            raise ValueError("actual qualification actor detached session differs")
        parents.append(parent)
        if _identity(heartbeat) != _identity_at(descriptor, "fd/4"):
            raise ValueError("original qualification heartbeat writer differs")
        from crewshal.linux_bootstrap import LinuxTrace

        driver = LinuxTrace(policy=getattr(bridge.lifetime, "_apparmor_export", None))
        driver._call(0x4206, pid, ctypes.c_void_p(0x00100000))
        driver._call(0x4207, pid, ctypes.c_void_p())
        while True:
            bridge._verify_original()
            waited, state = os.waitpid(pid, os.WNOHANG | 0x40000000)
            if waited == pid:
                if not os.WIFSTOPPED(state):
                    raise ValueError("original qualification observer trace stop missing")
                break
            time.sleep(0.001)
        driver.verify_storage_policy(descriptor, "native")
        driver.verify_storage_filter(pid)
        driver.detach_stopped(pid)
        actors.append(
            ObservedProbeActor(
                descriptor, pidfd, pid, ticks, _identity(descriptor), _identity(pidfd)
            )
        )
    if len({actor.pid for actor in actors}) != 2 or parents != [
        bridge.parent.spec.pid,
        actors[0].pid,
    ]:
        raise ValueError("original qualification actor identities repeat")
    expected = {str(actor.pid) for actor in actors}
    if ordinal == 2:
        expected.add(str(bridge.native.spec.pid))
    if set(worker._read("cgroup.procs").split()) != expected:
        raise ValueError("original qualification worker birth population differs")
    if (
        not stat.S_ISFIFO(os.fstat(heartbeat).st_mode)
        or fcntl.fcntl(heartbeat, fcntl.F_GETFL) & (os.O_ACCMODE | os.O_NONBLOCK)
        != os.O_RDONLY | os.O_NONBLOCK
    ):
        raise ValueError("original qualification heartbeat reader differs")
    custody.actors = actors[0], actors[1]
    custody.heartbeat, custody.launcher_pidfd = heartbeat, launcher
    custody.identities = _identity(heartbeat), _identity(launcher)
    custody._owners = bridge, ordinal, custody.actors
    custody._clock = bridge.origin_ns, bridge.expires_ns
    custody._configuration = record_digest(bridge.lifetime.controls.configuration)
    if bridge.parent_channel.send(b"1") != 1:
        raise ValueError("original qualification birth acknowledgement incomplete")
    return custody


def _identity_at(descriptor: int, path: str) -> tuple[int, int]:
    info = os.stat(path, dir_fd=descriptor)
    return info.st_dev, info.st_ino


def _receive_qualification_terminal(
    bridge: "StoppedNativeBridge", custody: QualificationTreeCustody
) -> None:
    if custody.terminal:
        raise ValueError("original qualification terminal packet consumed")
    bridge._wait()
    raw, descriptors, credentials = bridge._packet()
    if (
        not _probe_frame(raw, TREE_TERMINAL_PACKET, custody.ordinal)
        or descriptors
        or credentials[0] != bridge.parent.spec.pid
    ):
        raise ValueError("original qualification terminal packet differs")
    values = bytearray()
    while True:
        chunk = os.read(custody.heartbeat, 4097 - len(values))
        if not chunk:
            break
        values.extend(chunk)
        if len(values) > 4096:
            raise ValueError("original qualification heartbeat exceeds bound")
    custody.heartbeat_bytes = custody._terminal_record = bytes(values)
    custody.terminal = True
    custody.verify_terminal()
    if custody.ordinal == 2 and time.monotonic_ns() < bridge.expires_ns:
        raise ValueError("qualification deadline tree stopped before original expiry")
    if bridge.parent_channel.send(b"1") != 1:
        raise ValueError("original qualification terminal acknowledgement incomplete")


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
    received: list[int]
    _views_received: bool

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
        endpoint.channel.setsockopt(socket.SOL_SOCKET, getattr(socket, "SO_PASSCRED"), 1)
        endpoint.received = []
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
        or _wait_ready([pidfd], [], [], 0)[0]
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
        or _wait_ready([pidfd], [], [], 0)[0]
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
            or _wait_ready([pidfd], [], [], 0)[0]
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
    if remaining <= 0 or not _wait_ready([], [channel], [], remaining)[1]:
        raise ValueError("original watchdog bridge send deadline exhausted")
    ancillary = (
        [(socket.SOL_SOCKET, socket.SCM_RIGHTS, array("i", descriptors))] if descriptors else []
    )
    if channel.sendmsg([raw], ancillary) != len(raw):
        raise ValueError("original bridge FD packet incomplete")
    remaining = (deadline_ns - time.monotonic_ns()) / 1_000_000_000
    if (
        remaining <= 0
        or not _wait_ready([channel], [], [], remaining)[0]
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
    admitted._verify_binding()
    raw = json.dumps(
        {
            "protocol": NATIVE_PACKET.decode("ascii"),
            "receipt": admitted.receipt.model_dump(mode="json"),
        },
        separators=(",", ":"),
    ).encode("ascii")
    if len(raw) > CONTROL_BYTES:
        raise ValueError("original admission receipt exceeds charged control bound")
    _send(
        channel,
        raw,
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
    lane_context: RetainedLaneSetup | None
    qualification_trees: list[QualificationTreeCustody]
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
    admission_receipt: NativeAdmissionReceipt
    _admission_digest: str
    _admission_host_spec: str
    _validator_views_sent: bool
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
        context = getattr(self, "lane_context", None)
        scope = (
            retained_setup_scope(proof.reservation, context=context)
            if context is not None
            else proof
        )
        if (
            self.failed
            or getattr(scope, "_bridge", None) is not self
            or (getattr(proof.reservation, "_lane_contexts", None) is not None and context is None)
        ):
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
            retained_setup_scope(proof.reservation, lifetime, context=context)
            if (
                type(lifetime) is not OwnedNamespaceSetup
                or lifetime.controls.boot_id != proof.reservation.observer.spec.boot_id
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
            if _qualification_lane(self):
                if len(self.qualification_trees) != 2:
                    raise ValueError("original qualification tree custody missing")
                for tree in self.qualification_trees:
                    tree.verify_terminal()
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
        if remaining <= 0 or not _wait_ready([self.parent_channel], [], [], remaining)[0]:
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
            if _qualification_lane(self):
                tree = _receive_qualification_birth(self, 1)
                _receive_qualification_terminal(self, tree)
            self._wait()
            raw, received, credentials = self._packet(CONTROL_BYTES)
            data = json.loads(raw)
            if (
                type(data) is not dict
                or set(data) != {"protocol", "receipt"}
                or data["protocol"] != NATIVE_PACKET.decode("ascii")
                or len(received) != 5
                or credentials[0] != self.parent.spec.pid
            ):
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
            self._bind_admission(
                NativeAdmissionReceipt.model_validate(data["receipt"]), source, pipes
            )
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

    def _bind_admission(
        self, receipt: NativeAdmissionReceipt, source: int, pipes: tuple[int, int, int]
    ) -> None:
        """Bind the original namespace receipt to independent host readback."""
        configuration = self.lifetime.controls.configuration
        namespace_pid, _, namespace_parent, start = _stat_identity(_read(source, "stat"))
        spec = self.native.spec
        expected = NativeAdmissionSpec.model_validate(
            {**spec.model_dump(), "pid": namespace_pid, "parent_pid": namespace_parent}
        )
        values = self.native.read_configuration(configuration)
        controls = _aggregate_readback(self.lifetime.aggregate, self.lifetime.worker)
        identities = tuple(
            NamespaceIdentity(device=_identity(fd)[0], inode=_identity(fd)[1]) for fd in pipes
        )
        if (
            receipt.spec != expected
            or start != spec.start_ticks
            or receipt.configuration != record_digest(configuration)
            or receipt.argv != values["argv"]
            or receipt.initial_environment != values["initial_environment"]
            or receipt.aggregate_controls != controls
            or (receipt.stdin_pipe, receipt.stdout_pipe, receipt.stderr_pipe) != identities
            or receipt.started_monotonic != self.origin_ns / 1_000_000_000
        ):
            raise ValueError("original namespace admission differs from independent readback")
        self.admission_receipt = receipt
        self._admission_digest = record_digest(receipt)
        self._admission_host_spec = record_digest(spec)

    def verify_admission(self) -> NativeAdmissionReceipt:
        """Reject missing or changed original admission before journal linkage."""
        receipt = getattr(self, "admission_receipt", None)
        if (
            type(receipt) is not NativeAdmissionReceipt
            or record_digest(receipt) != self._admission_digest
            or record_digest(self.native.spec) != self._admission_host_spec
        ):
            raise ValueError("original namespace admission missing or changed")
        return receipt

    def receive_capture(self) -> CapturedProcess:
        """Consume three bounded data packets; kernel readback gates retention."""
        if self.stage != 2 or hasattr(self, "capture_packets"):
            raise BridgeRefusal("original native capture consumed or missing; no retry", self)
        self.capture_packets = []
        try:
            if _qualification_lane(self):
                tree = _receive_qualification_birth(self, 2)
                _receive_qualification_terminal(self, tree)
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


def prepare_stopped_native_bridge(
    installation: EffectiveInstallation, *, lane_context: RetainedLaneSetup | None = None
) -> StoppedNativeBridge:
    """Pin connected custody before namespace launch; no second owner or clock."""
    if type(installation) is not EffectiveInstallation:
        raise ValueError("original installed bridge unavailable or consumed")
    scope = (
        retained_setup_scope(installation.reservation, context=lane_context)
        if lane_context is not None
        else installation
    )
    if hasattr(scope, "_bridge") or (
        getattr(installation.reservation, "_lane_contexts", None) is not None
        and lane_context is None
    ):
        raise ValueError("original installed bridge unavailable or consumed")
    bridge = object.__new__(StoppedNativeBridge)
    bridge.installation = installation
    bridge.lane_context = lane_context
    bridge.received, bridge.handles, bridge.failed, bridge.stage = [], [], False, 0
    setattr(scope, "_bridge", bridge)
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


VALIDATOR_VIEW_PACKET = "crewshal-original-validator-views-v1"


def send_validator_views(bridge: StoppedNativeBridge) -> None:
    """Transfer actual original readonly projection and private scratch FDs once."""
    if getattr(bridge, "_validator_views_sent", False):
        raise BridgeRefusal("original validator view transfer consumed; no retry", bridge)
    bridge._validator_views_sent = True
    try:
        bridge.verify_capture()
        bridge.verify_admission()
        bridge.freeze.verify_projection()
        scratch = bridge.installation.production.handles[
            retained_lane_handle(bridge.lifetime, "validator-scratch-upper")
        ]
        frozen = bridge.freeze.handles["readonly-projection"]
        manifest = bridge.freeze.manifest
        if manifest is None:
            raise ValueError("actual original frozen validator manifest is missing")
        raw = json.dumps(
            {
                "protocol": VALIDATOR_VIEW_PACKET,
                "configuration": record_digest(bridge.lifetime.controls.configuration),
                "manifest": manifest.model_dump(mode="json"),
            },
            separators=(",", ":"),
        ).encode("ascii")
        if len(raw) > CONTROL_BYTES:
            raise ValueError("original validator manifest exceeds charged control bound")
        deadline = round((bridge.installation.reservation.batch_started + 570) * 1_000_000_000)
        _send(bridge.parent_channel, raw, (frozen, scratch), deadline)
        # The ACK permits the original parent to create its validator watchdog.
        # The next stopped packet supplies independent custody for that stage.
    except BaseException as error:
        bridge._refuse(error)


def receive_validator_views(
    parent: RetainedTrustedTask,
    controls: InheritedControls,
    inventory: "RetainedParentInventory",
    groups: dict[str, "OwnedCgroup"],
) -> "ValidatorAttempt":
    """Retain original transferred FDs before parsing the finite manifest."""
    from crewshal.candidate import FrozenCandidate
    from crewshal.linux_validator import prepare_validator_attempt

    endpoint = getattr(parent, "_parent_bridge", None)
    if type(endpoint) is not ParentBridgeEndpoint or getattr(endpoint, "_views_received", False):
        raise ValueError("original validator view receive unavailable or consumed")
    endpoint._views_received = True
    try:
        endpoint.verify()
        origin = controls.batch_origin_ns
        if type(origin) is not int or origin <= 0:
            raise ValueError("original validator batch origin is unavailable")
        remaining = (origin + 570_000_000_000 - time.monotonic_ns()) / 1_000_000_000
        if remaining <= 0 or not _wait_ready([endpoint.channel], [], [], remaining)[0]:
            raise ValueError("original validator transfer exceeded original batch cutoff")
        raw, ancillary, flags, _ = endpoint.channel.recvmsg(
            CONTROL_BYTES,
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
                endpoint.received.extend(values)
                received.extend(values)
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
            or flags & (socket.MSG_TRUNC | socket.MSG_CTRUNC)
            or len(received) != 2
            or len(credentials) != 1
            or credentials[0][1:] != (0, 0)
        ):
            raise ValueError("original validator view packet rights or credentials differ")
        data = json.loads(raw)
        if (
            type(data) is not dict
            or set(data) != {"protocol", "configuration", "manifest"}
            or data["protocol"] != VALIDATOR_VIEW_PACKET
            or data["configuration"] != record_digest(controls.configuration)
        ):
            raise ValueError("original validator view packet identity differs")
        attempt = prepare_validator_attempt(
            parent,
            groups["validator"],
            groups["supervisor"],
            groups["aggregate"],
            controls,
            inventory,
            received[0],
            received[1],
            FrozenCandidate.model_validate(data["manifest"]),
        )
        endpoint.verify()
        if endpoint.channel.send(b"1") != 1:
            raise ValueError("original validator view acknowledgement incomplete")
        return attempt
    except BaseException:
        endpoint.failed = True
        raise


VALIDATOR_STOP_PACKET = "crewshal-original-stopped-validator-v1"
VALIDATOR_CAPTURE_PACKETS = tuple(
    prefix.replace(b"capture", b"validator-capture") for prefix in CAPTURE_PACKETS
)


def send_stopped_validator_bridge(
    parent: RetainedTrustedTask, admitted: "AdmittedValidator"
) -> None:
    """Transfer stopped direct validator and its own original watchdog before resume."""
    from crewshal.linux_validator import AdmittedValidator

    if type(admitted) is not AdmittedValidator or getattr(parent, "_validator_bridge_sent", False):
        raise ValueError("original stopped validator transfer unavailable or consumed")
    setattr(parent, "_validator_bridge_sent", True)
    attempt = admitted.attempt
    endpoint = getattr(parent, "_parent_bridge", None)
    child, proc, watched = attempt.child, attempt.proc, attempt.watchdog
    if (
        type(endpoint) is not ParentBridgeEndpoint
        or attempt.parent is not parent
        or child is None
        or proc is None
        or watched.task is None
        or watched.observed is None
        or child.stdin is None
        or child.stdout is None
        or child.stderr is None
    ):
        raise ValueError("original stopped validator transfer lacks retained custody")
    endpoint.verify()
    attempt.verify(watchdog=True)
    proc.verify_state(traced=False)
    attempt.verify_view(proc)
    raw = json.dumps(
        {
            "protocol": VALIDATOR_STOP_PACKET,
            "spec": proc.spec.model_dump(mode="json"),
            "origin_ns": watched.observed.deadline.origin_ns,
            "expires_ns": watched.observed.deadline.expires_ns,
        },
        separators=(",", ":"),
    ).encode("ascii")
    if len(raw) > CONTROL_BYTES:
        raise ValueError("original validator stop packet exceeds charged bound")
    _send(
        endpoint.channel,
        raw,
        (
            proc.descriptor,
            proc.pidfd,
            watched.task.descriptor,
            watched.task.pidfd,
            child.stdin.fileno(),
            child.stdout.fileno(),
            child.stderr.fileno(),
        ),
        watched.observed.deadline.expires_ns,
    )
    attempt.verify(watchdog=True)
    proc.verify_state(traced=False)


def send_original_validator_capture(
    parent: RetainedTrustedTask, admitted: "AdmittedValidator", captured: CapturedProcess
) -> None:
    """Transfer finite validator capture after independently retained exit and reap."""
    if getattr(parent, "_validator_capture_sent", False):
        raise ValueError("original validator capture transfer consumed; no retry")
    setattr(parent, "_validator_capture_sent", True)
    attempt = admitted.attempt
    endpoint = getattr(parent, "_parent_bridge", None)
    if (
        type(endpoint) is not ParentBridgeEndpoint
        or attempt.parent is not parent
        or getattr(attempt, "_captured_process", None) is not captured
        or captured.observation.exit_code is None
        or attempt.watchdog.observed is None
    ):
        raise ValueError("original validator capture custody differs")
    admitted.verify_terminal(captured.observation.exit_code)
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
    if max(len(captured.stdout), len(captured.stderr), len(metadata)) > STREAM_BYTES:
        raise ValueError("original validator capture exceeds charged control bound")
    deadline = min(attempt.watchdog.observed.deadline.expires_ns + 1_000_000_000, attempt.cutoff_ns)
    for prefix, data in zip(
        VALIDATOR_CAPTURE_PACKETS, (captured.stdout, captured.stderr, metadata)
    ):
        endpoint.verify()
        admitted.verify_terminal(captured.observation.exit_code)
        _send(endpoint.channel, prefix + data, (), deadline)


class ValidatorBridgeCustody:
    """Retain actual stopped validator identities before accepting terminal data."""

    bridge: StoppedNativeBridge
    proc: "RetainedValidatorProc"
    watchdog: RetainedTrustedTask
    origin_ns: int
    expires_ns: int
    received_capture: bool
    pipes: tuple[int, int, int]
    captured: CapturedProcess
    _captured_owner: CapturedProcess
    _capture_record: tuple[bytes, bytes, str, str, str | None, bool, bool]
    observed_argv: list[str]
    observed_environment: Digest
    observed_toolchain: Digest
    _owners: tuple[StoppedNativeBridge, "RetainedValidatorProc", RetainedTrustedTask]
    _specs: tuple[Digest, Digest]
    _clock: tuple[int, int]
    _check_inputs: tuple[tuple[str, ...], Digest, Digest]

    def __init__(self) -> None:
        raise ValueError("validator observer custody requires original stopped FD transfer")

    def __reduce__(self) -> NoReturn:
        raise TypeError("original validator observer custody cannot be copied or exported")

    def verify_binding(self) -> None:
        bridge = self.bridge
        if (
            getattr(bridge, "_validator_custody", None) is not self
            or bridge.failed
            or getattr(self, "_owners", None) != (bridge, self.proc, self.watchdog)
            or getattr(self, "_specs", None)
            != (record_digest(self.proc.spec), record_digest(self.watchdog.spec))
            or getattr(self, "_clock", None) != (self.origin_ns, self.expires_ns)
            or getattr(self, "_check_inputs", None)
            != (tuple(self.observed_argv), self.observed_environment, self.observed_toolchain)
        ):
            raise ValueError("original validator observer custody changed")

    def verify_terminal(self) -> None:
        self.verify_binding()
        bridge = self.bridge
        bridge.parent.verify(bridge.lifetime.supervisor.identity)
        self.proc.verify_exited()
        self.watchdog.verify_handles()
        if not _wait_ready([self.watchdog.pidfd], [], [], 0)[0]:
            raise ValueError("original validator watchdog terminal exit remains unknown")
        for task in (self.proc, self.watchdog):
            if _fields(_read(bridge.host_proc, f"self/fdinfo/{task.pidfd}")).get("Pid") != "-1":
                raise ValueError("original validator or watchdog positive reap remains unknown")
        role = bridge.lifetime.validator
        if role is None:
            raise ValueError("original validator role is missing")
        sample = role.sample()
        if (
            sample.populated
            or sample.direct_pids
            or any(sample.memory_events.values())
            or any(sample.pids_events.values())
        ):
            raise ValueError("original validator terminal role differs")
        if bridge.lifetime.supervisor._read("cgroup.procs").split() != [
            str(bridge.parent.spec.pid)
        ]:
            raise ValueError("original validator terminal requires sole live namespace parent")
        bridge.freeze.verify_projection()
        self.proc.verify_exited()

    def verify_capture(self) -> None:
        captured = getattr(self, "captured", None)
        if captured is not getattr(self, "_captured_owner", None) or captured is None:
            raise ValueError("original validator capture missing or replaced")
        current = (
            captured.stdout,
            captured.stderr,
            captured.observation.model_dump_json(),
            captured.initial.model_dump_json(),
            captured.final.model_dump_json() if captured.final is not None else None,
            captured.overflow,
            captured.stop_error,
        )
        if current != self._capture_record:
            raise ValueError("original validator retained capture changed")
        self.verify_terminal()

    def receive_capture(self) -> CapturedProcess:
        if self.received_capture:
            raise BridgeRefusal(
                "original validator capture receive consumed; no retry", self.bridge
            )
        self.received_capture = True
        bridge = self.bridge
        values = []
        try:
            for prefix in VALIDATOR_CAPTURE_PACKETS:
                remaining = (self.expires_ns + 1_000_000_000 - time.monotonic_ns()) / 1_000_000_000
                if remaining <= 0 or not _wait_ready([bridge.parent_channel], [], [], remaining)[0]:
                    raise ValueError("original validator capture deadline exhausted")
                raw, received, credentials = bridge._packet(STREAM_BYTES + len(prefix))
                if (
                    received
                    or credentials[0] != bridge.parent.spec.pid
                    or not raw.startswith(prefix)
                ):
                    raise ValueError("original validator capture framing or sender differs")
                values.append(raw[len(prefix) :])
                if (
                    prefix != VALIDATOR_CAPTURE_PACKETS[-1]
                    and bridge.parent_channel.send(b"1") != 1
                ):
                    raise ValueError("original validator capture acknowledgement incomplete")
            data = json.loads(values[2])
            if type(data) is not dict or set(data) != {
                "observation",
                "initial",
                "final",
                "overflow",
                "stop_error",
            }:
                raise ValueError("original validator capture metadata differs")
            captured = CapturedProcess(
                ProcessObservation.model_validate(data["observation"]),
                values[0],
                values[1],
                CgroupSample.model_validate(data["initial"]),
                CgroupSample.model_validate(data["final"]) if data["final"] is not None else None,
                data["overflow"],
                data["stop_error"],
            )
            role = bridge.lifetime.validator
            if (
                role is None
                or type(captured.overflow) is not bool
                or type(captured.stop_error) is not bool
                or captured.observation.exit_code is None
                or captured.initial.identity != role.identity
                or captured.final is None
                or captured.final.identity != role.identity
            ):
                raise ValueError("original validator capture role or exit binding differs")
            self.verify_terminal()
            self.captured = self._captured_owner = captured
            self._capture_record = (
                captured.stdout,
                captured.stderr,
                captured.observation.model_dump_json(),
                captured.initial.model_dump_json(),
                captured.final.model_dump_json() if captured.final is not None else None,
                captured.overflow,
                captured.stop_error,
            )
            if bridge.parent_channel.send(b"1") != 1:
                raise ValueError("original validator terminal acknowledgement incomplete")
            return captured
        except BaseException as error:
            bridge._refuse(error)


def receive_stopped_validator(bridge: StoppedNativeBridge) -> ValidatorBridgeCustody:
    """Bind host proc/pidfd, private views and timer before the parent's resume."""
    from crewshal.linux_validator import (
        RetainedValidatorProc,
        ValidatorAdmissionSpec,
        verify_validator_private_view,
    )

    if getattr(bridge, "_validator_custody", None) is not None or not getattr(
        bridge, "_validator_views_sent", False
    ):
        raise BridgeRefusal("original stopped validator receive unavailable or consumed", bridge)
    custody = object.__new__(ValidatorBridgeCustody)
    custody.bridge, custody.received_capture = bridge, False
    setattr(bridge, "_validator_custody", custody)
    try:
        deadline = bridge.installation.reservation.batch_started + 570
        remaining = deadline - time.monotonic()
        if remaining <= 0 or not _wait_ready([bridge.parent_channel], [], [], remaining)[0]:
            raise ValueError("original stopped validator exceeded original batch cutoff")
        raw, received, credentials = bridge._packet(CONTROL_BYTES)
        data = json.loads(raw)
        if (
            type(data) is not dict
            or set(data) != {"protocol", "spec", "origin_ns", "expires_ns"}
            or data["protocol"] != VALIDATOR_STOP_PACKET
            or len(received) != 7
            or credentials[0] != bridge.parent.spec.pid
            or any(type(data[key]) is not int for key in ("origin_ns", "expires_ns"))
            or data["expires_ns"] - data["origin_ns"] != 5_000_000_000
            or data["expires_ns"] > round(deadline * 1_000_000_000)
        ):
            raise ValueError("original stopped validator framing or timer differs")
        custody.origin_ns, custody.expires_ns = data["origin_ns"], data["expires_ns"]
        source, pidfd, watcher_source, watcher_pidfd, *pipes = received
        descriptor, pid, parent, ticks = _mapped_host_proc(
            bridge.host_proc, source, pidfd, bridge.handles
        )
        watcher_fd, watcher_pid, watcher_parent, watcher_ticks = _mapped_host_proc(
            bridge.host_proc, watcher_source, watcher_pidfd, bridge.handles
        )
        local = ValidatorAdmissionSpec.model_validate(data["spec"])
        role = bridge.lifetime.validator
        if (
            role is None
            or parent != bridge.parent.spec.pid
            or watcher_parent != parent
            or local.configuration != record_digest(bridge.lifetime.controls.configuration)
            or local.validator != role.identity
            or local.aggregate != bridge.lifetime.aggregate.identity
            or (local.pid, "T", local.parent_pid, local.start_ticks)
            != _stat_identity(_read(source, "stat"))
            or local.start_ticks != ticks
            or local.pid_for_children is None
        ):
            raise ValueError("original stopped validator direct-parent or role binding differs")
        spec = ValidatorAdmissionSpec.model_validate(
            {**local.model_dump(), "pid": pid, "parent_pid": parent}
        )
        custody.proc = RetainedValidatorProc(descriptor, pidfd, spec)
        custody.proc.verify_state(traced=False)
        custody.proc.read_configuration(
            bridge.lifetime.controls.configuration,
            bridge.lifetime.controls.configuration.validator_argv,
        )
        verify_validator_private_view(
            custody.proc,
            bridge.parent,
            bridge.lifetime.controls.outer_namespaces,
            bridge.installation.production.root_inventory,
            bridge.freeze.handles["readonly-projection"],
            bridge.installation.production.handles[
                retained_lane_handle(bridge.lifetime, "validator-scratch-upper")
            ],
        )
        helper = bridge.lifetime.controls.bootstrap.policy.helper_binary
        if helper is None:
            raise ValueError("original installed validator watcher helper is missing")
        custody.watchdog = RetainedTrustedTask(
            watcher_fd,
            watcher_pidfd,
            TrustedTaskSpec(
                **{
                    **bridge.parent.spec.model_dump(),
                    "pid": watcher_pid,
                    "parent_pid": watcher_parent,
                    "start_ticks": watcher_ticks,
                    "executable": helper,
                    "argv": bridge.lifetime.controls.bootstrap.watchdog_argv,
                    "capabilities": "0" * 16,
                }
            ),
        )
        custody.watchdog.verify(bridge.lifetime.supervisor.identity)
        watcher_view = SimpleNamespace(
            watchdog=custody.watchdog, parent=bridge.parent, lifetime=SimpleNamespace(worker=role)
        )
        _verify_original_watchdog(cast(OriginalVolumeFreeze, watcher_view))
        if (
            not watcher_view.watchdog_expiry_range[0]
            <= custody.expires_ns
            <= watcher_view.watchdog_expiry_range[1]
        ):
            raise ValueError("actual validator watcher timer differs from original packet")
        if set(bridge.lifetime.supervisor._read("cgroup.procs").split()) != {
            str(parent),
            str(watcher_pid),
        }:
            raise ValueError("validator supervisor population differs")
        if role.sample().direct_pids != [pid]:
            raise ValueError("validator role contains another task")
        from crewshal.linux_validator import validator_toolchain_digest
        from crewshal.model import digest

        custody.observed_argv = list(bridge.lifetime.controls.configuration.validator_argv)
        custody.observed_environment = digest(_read(descriptor, "environ"))
        custody.observed_toolchain = validator_toolchain_digest(
            bridge.installation.production._root_manifest, custody.observed_argv
        )
        custody._owners = bridge, custody.proc, custody.watchdog
        custody._specs = record_digest(custody.proc.spec), record_digest(custody.watchdog.spec)
        custody._clock = custody.origin_ns, custody.expires_ns
        custody._check_inputs = (
            tuple(custody.observed_argv),
            custody.observed_environment,
            custody.observed_toolchain,
        )
        custody.pipes = (pipes[0], pipes[1], pipes[2])
        # The parent keeps its original stdin. Only this positively bound duplicate closes.
        for fd, number, access in zip(
            custody.pipes, (0, 1, 2), (os.O_WRONLY, os.O_RDONLY, os.O_RDONLY)
        ):
            actual = os.stat(f"fd/{number}", dir_fd=descriptor)
            if (
                not stat.S_ISFIFO(actual.st_mode)
                or _identity(fd) != (actual.st_dev, actual.st_ino)
                or fcntl.fcntl(fd, fcntl.F_GETFL) & os.O_ACCMODE != access
            ):
                raise ValueError("original validator stdio transfer differs")
        os.close(pipes[0])
        bridge.received.remove(pipes[0])
        if bridge.parent_channel.send(b"1") != 1:
            raise ValueError("original stopped validator acknowledgement incomplete")
        return custody
    except BaseException as error:
        bridge._refuse(error)


def wait_original_parent_completion(
    parent: RetainedTrustedTask, controls: InheritedControls
) -> None:
    """Keep the original parent alive until the observer records finite completion."""
    endpoint = getattr(parent, "_parent_bridge", None)
    if type(endpoint) is not ParentBridgeEndpoint or controls.batch_origin_ns is None:
        raise ValueError("original parent completion channel is missing")
    endpoint.verify()
    remaining = (controls.batch_origin_ns + 570_000_000_000 - time.monotonic_ns()) / 1_000_000_000
    if (
        remaining <= 0
        or not _wait_ready([endpoint.channel], [], [], remaining)[0]
        or endpoint.channel.recv(2) != b"F"
    ):
        raise ValueError("original parent completion receipt missing before cutoff")
    endpoint.verify()


def finish_original_parent(custody: ValidatorBridgeCustody) -> None:
    """Request parent exit only after original terminal readback and retained capture."""
    if getattr(custody, "_parent_finish_sent", False) or not hasattr(custody, "captured"):
        raise BridgeRefusal("original parent finish unavailable or consumed", custody.bridge)
    setattr(custody, "_parent_finish_sent", True)
    try:
        custody.verify_capture()
        custody.bridge.verify_capture()
        custody.bridge.verify_admission()
        if custody.bridge.parent_channel.send(b"F") != 1:
            raise ValueError("original parent finish transport incomplete")
    except BaseException as error:
        custody.bridge._refuse(error)
