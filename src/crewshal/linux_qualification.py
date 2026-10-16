"""Fixed tree probes use the original native deadline and original worker."""

import array
import ctypes
from dataclasses import dataclass, field
import os
import signal
import socket
import stat
import struct
import subprocess
import time
from typing import NoReturn

from crewshal.admission import _wait_ready
from crewshal.admission import AdmittedNative, _fields, _read, _stat_identity
from crewshal.contracts import record_digest
from crewshal.linux_bootstrap import LinuxTrace
from crewshal.linux_parent import RetainedTrustedTask, _image, _move_self, _namespaces
from crewshal.linux_setup import OwnedWatchdogLifetime
from crewshal.supervisor import CapturedProcess


@dataclass
class ProbeActor:
    ordinal: int
    descriptor: int
    pidfd: int
    pid: int
    start_ticks: int
    directory: tuple[int, int]
    pidfd_identity: tuple[int, int]
    wait_status: int | None = None


@dataclass
class ProbeTree:
    channel: socket.socket
    peer: socket.socket
    heartbeat: int
    writer: int
    process: subprocess.Popen[bytes] | None = None
    launcher_pidfd: int = -1
    handles: list[int] = field(default_factory=list)
    actors: list[ProbeActor] = field(default_factory=list)
    bytes: bytearray = field(default_factory=bytearray)
    eof: bool = False
    terminal: bool = False
    birth_transferred: bool = False
    terminal_transferred: bool = False


class QualificationProbeRefusal(ValueError):
    def __init__(self, reason: str, lifetime: "OriginalQualificationProbes"):
        super().__init__(reason)
        self.lifetime = lifetime
        self.resources_reusable = False


class OriginalQualificationProbes:
    """Retain two finite trees. No new group, timer, attempt, or recovery exists."""

    def __reduce__(self) -> NoReturn:
        raise TypeError("original qualification custody cannot be copied or exported")

    def __init__(self, parent: RetainedTrustedTask, watchdog: OwnedWatchdogLifetime):
        if getattr(parent, "_qualification_probes", None) is not None:
            raise ValueError("original qualification probes consumed")
        setattr(parent, "_qualification_probes", self)
        self.parent, self.watchdog = parent, watchdog
        self.trees: list[ProbeTree] = []
        self.cancelled_tree: ProbeTree | None = None
        self.deadline_tree: ProbeTree | None = None
        self.admitted: AdmittedNative | None = None
        self.failed = False
        self.resources_reusable = False
        try:
            if (
                type(parent) is not RetainedTrustedTask
                or type(watchdog) is not OwnedWatchdogLifetime
                or watchdog.parent is not parent
                or getattr(parent, "_watchdog_lifetime", None) is not watchdog
                or watchdog.observed is None
            ):
                raise ValueError("original qualification parent and watchdog custody required")
            self.deadline = watchdog.observed.deadline
            self.origin_ns = self.deadline.origin_ns
            self.expires_ns = self.deadline.expires_ns
            self.worker, self.supervisor = watchdog.worker, watchdog.supervisor
            controls = getattr(parent, "_installed_controls", None)
            if controls is None or controls.configuration.lane_id not in (
                "qualification-1",
                "qualification-2",
            ):
                raise ValueError("fixed probes require an original qualification lane")
            self.configuration = controls.configuration
            self.helper_digest = controls.bootstrap.policy.helper_binary
            if self.helper_digest is None:
                raise ValueError("fixed probe helper identity missing")
            self._owners = parent, watchdog, self.worker, self.supervisor, self.deadline
            self._check()
            libc = ctypes.CDLL(None, use_errno=True)
            if libc.prctl(36, 1, 0, 0, 0) != 0:
                raise OSError(ctypes.get_errno(), "qualification child subreaper unavailable")
            self._subreaper(libc)
            self.libc = libc
        except BaseException as error:
            self.failed = True
            raise QualificationProbeRefusal(str(error), self) from error

    @staticmethod
    def _subreaper(libc: ctypes.CDLL) -> None:
        value = ctypes.c_int()
        if libc.prctl(37, ctypes.byref(value), 0, 0, 0) != 0 or value.value != 1:
            raise ValueError("actual qualification child subreaper setting differs")

    def _check(self, *, terminal: bool = False) -> None:
        if (
            self.failed
            or getattr(self.parent, "_qualification_probes", None) is not self
            or getattr(self.parent, "_watchdog_lifetime", None) is not self.watchdog
            or self._owners
            != (self.parent, self.watchdog, self.worker, self.supervisor, self.deadline)
            or self.watchdog.observed is None
            or self.watchdog.observed.deadline is not self.deadline
            or (self.deadline.origin_ns, self.deadline.expires_ns)
            != (self.origin_ns, self.expires_ns)
            or self.expires_ns - self.origin_ns != 5_000_000_000
            or self.parent.spec.configuration != record_digest(self.configuration)
        ):
            raise ValueError("original qualification scope or deadline changed")
        self.parent.verify(self.supervisor.identity)
        if not terminal:
            self.watchdog.observed.check(self.worker, self.configuration)

    def _receive(self, tree: ProbeTree) -> None:
        while len(tree.actors) < 2:
            self._check()
            if not _wait_ready([tree.channel], [], [], 0)[0]:
                time.sleep(0.001)
                continue
            payload, ancillary, flags, _ = tree.channel.recvmsg(
                32, socket.CMSG_SPACE(8) + socket.CMSG_SPACE(12)
            )
            descriptors: list[int] = []
            credentials = None
            unexpected = False
            for level, kind, raw in ancillary:
                if level == socket.SOL_SOCKET and kind == socket.SCM_RIGHTS:
                    handles = array.array("i")
                    handles.frombytes(raw)
                    descriptors.extend(handles)
                    tree.handles.extend(handles)
                elif level == socket.SOL_SOCKET and kind == getattr(socket, "SCM_CREDENTIALS", 2):
                    if credentials is not None or len(raw) != 12:
                        unexpected = True
                    else:
                        credentials = struct.unpack("3i", raw)
                else:
                    unexpected = True
            ordinal = {b"TREE 1\n": 1, b"TREE 2\n": 2}.get(payload)
            if (
                flags
                or unexpected
                or ordinal is None
                or len(descriptors) != 2
                or ordinal in {actor.ordinal for actor in tree.actors}
            ):
                raise ValueError("fixed tree custody packet differs")
            descriptor, pidfd = descriptors
            pid, _, _, start = _stat_identity(_read(descriptor, "stat"))
            if credentials != (pid, 65534, 65534):
                raise ValueError("fixed tree birth credentials differ")
            directory = os.fstat(descriptor)
            birth = os.fstat(pidfd)
            tree.actors.append(
                ProbeActor(
                    ordinal,
                    descriptor,
                    pidfd,
                    pid,
                    start,
                    (directory.st_dev, directory.st_ino),
                    (birth.st_dev, birth.st_ino),
                )
            )
        if len({actor.pid for actor in tree.actors}) != 2:
            raise ValueError("fixed tree birth identities repeat")
        tree.actors.sort(key=lambda actor: actor.ordinal)

    def _ready(self, tree: ProbeTree) -> None:
        """Bind both first heartbeat writes without consuming observer pipe bytes."""
        received: set[int] = set()
        while len(received) != 2:
            self._check()
            if not _wait_ready([tree.channel], [], [], 0)[0]:
                time.sleep(0.001)
                continue
            payload, ancillary, flags, _ = tree.channel.recvmsg(
                32, socket.CMSG_SPACE(8) + socket.CMSG_SPACE(12)
            )
            credentials = None
            unexpected = False
            for level, kind, raw in ancillary:
                if level == socket.SOL_SOCKET and kind == socket.SCM_RIGHTS:
                    handles = array.array("i")
                    handles.frombytes(raw[: len(raw) - len(raw) % handles.itemsize])
                    tree.handles.extend(handles)
                    unexpected = True
                elif level == socket.SOL_SOCKET and kind == getattr(socket, "SCM_CREDENTIALS", 2):
                    if credentials is not None or len(raw) != 12:
                        unexpected = True
                    else:
                        credentials = struct.unpack("3i", raw)
                else:
                    unexpected = True
            ordinal = {b"READY 1\n": 1, b"READY 2\n": 2}.get(payload)
            actor = next((item for item in tree.actors if item.ordinal == ordinal), None)
            if (
                flags
                or unexpected
                or ordinal is None
                or ordinal in received
                or actor is None
                or credentials != (actor.pid, 65534, 65534)
                or _wait_ready([actor.pidfd], [], [], 0)[0]
            ):
                raise ValueError("fixed tree first heartbeat custody packet differs")
            received.add(ordinal)

    def _verify_actor(self, actor: ProbeActor, driver: LinuxTrace) -> None:
        self._check()
        info, birth = os.fstat(actor.descriptor), os.fstat(actor.pidfd)
        while True:
            self._check()
            pid, state, _, start = _stat_identity(_read(actor.descriptor, "stat"))
            if state in ("T", "t"):
                break
            if state not in ("R", "S"):
                raise ValueError("fixed tree birth did not reach its original stop")
            time.sleep(0.001)
        with open(f"/proc/self/fdinfo/{actor.pidfd}", "rb") as stream:
            fdinfo = _fields(stream.read(4096))
        status = _fields(_read(actor.descriptor, "status"))
        if (
            (info.st_dev, info.st_ino) != actor.directory
            or (birth.st_dev, birth.st_ino) != actor.pidfd_identity
            or not stat.S_ISDIR(info.st_mode)
            or (pid, start) != (actor.pid, actor.start_ticks)
            or state not in ("T", "t")
            or fdinfo.get("Pid") != str(pid)
            or status.get("Uid", "").split() != ["65534"] * 4
            or status.get("Gid", "").split() != ["65534"] * 4
            or status.get("Groups", "").split() not in ([], ["65534"])
            or status.get("NoNewPrivs") != "1"
            or status.get("Threads") != "1"
            or any(
                status.get(key) != "0000000000000000"
                for key in ("CapInh", "CapPrm", "CapEff", "CapBnd", "CapAmb")
            )
            or str(pid) not in self.worker._read("cgroup.procs").split()
        ):
            raise ValueError("actual fixed tree identity or worker placement differs")
        _namespaces(actor.descriptor, self.parent.spec.namespaces)
        _image(actor.descriptor, self.helper_digest)
        # The actual stopped tracee permits kernel filter readback.
        driver._call(0x4206, pid, ctypes.c_void_p(0x00100000))
        driver._call(0x4207, pid, ctypes.c_void_p())
        while True:
            self._check()
            waited, status_value = os.waitpid(pid, os.WNOHANG | 0x40000000)
            if waited == pid:
                if not os.WIFSTOPPED(status_value):
                    raise ValueError("fixed tree trace stop is missing")
                break
            time.sleep(0.001)
        driver.verify_storage_policy(actor.descriptor, "native")
        driver.verify_storage_filter(pid)
        driver.detach_stopped(pid)

    def _drain(self, tree: ProbeTree) -> None:
        while not tree.eof:
            try:
                chunk = os.read(tree.heartbeat, 4097 - len(tree.bytes))
            except BlockingIOError:
                return
            if not chunk:
                tree.eof = True
                return
            tree.bytes.extend(chunk)
            if len(tree.bytes) > 4096 or any(value not in (49, 50) for value in chunk):
                raise ValueError("fixed tree heartbeat exceeds its exact bound")

    def _create(self) -> ProbeTree:
        self._check()
        self._subreaper(self.libc)
        channel, peer = socket.socketpair(socket.AF_UNIX, socket.SOCK_SEQPACKET)
        channel.setsockopt(socket.SOL_SOCKET, getattr(socket, "SO_PASSCRED", 16), 1)
        reading, writing = getattr(os, "pipe2")(os.O_CLOEXEC | os.O_NONBLOCK)
        tree = ProbeTree(channel, peer, reading, writing)
        self.trees.append(tree)
        try:
            _move_self(self.worker)
            self.parent.verify(self.worker.identity)
            tree.process = subprocess.Popen(
                [
                    "/bin/setpriv",
                    "--reuid=65534",
                    "--regid=65534",
                    "--clear-groups",
                    "--bounding-set=-all",
                    "--inh-caps=-all",
                    "--ambient-caps=-all",
                    "--no-new-privs",
                    "--",
                    "/bin/crewshal-bootstrap",
                    "--qualification-tree-fds",
                    str(peer.fileno()),
                    str(writing),
                ],
                pass_fds=(peer.fileno(), writing),
                stdin=subprocess.DEVNULL,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                env={},
                close_fds=True,
                cwd=self.parent.spec.cwd,
            )
            tree.launcher_pidfd = getattr(os, "pidfd_open")(tree.process.pid, 0)
            tree.handles.append(tree.launcher_pidfd)
        finally:
            _move_self(self.supervisor)
            self.parent.verify(self.supervisor.identity)
        peer.close()
        os.close(writing)
        tree.writer = -1
        self._receive(tree)
        driver = LinuxTrace(policy=getattr(self.parent, "_apparmor_export", None))
        for actor in tree.actors:
            self._verify_actor(actor, driver)
        endpoint = getattr(self.parent, "_parent_bridge", None)
        if endpoint is not None:
            from crewshal.linux_bridge import send_qualification_tree_birth

            send_qualification_tree_birth(self, tree)
        for _ in tree.actors:
            if channel.send(b"GO\n") != 3:
                raise ValueError("fixed tree release packet incomplete")
        sender = getattr(signal, "pidfd_send_signal", None)
        if sender is None:
            raise ValueError("fixed tree retained pidfd signalling unavailable")
        for actor in tree.actors:
            sender(actor.pidfd, signal.SIGCONT, None, 0)
        self._ready(tree)
        if tree.birth_transferred:
            return tree
        while set(tree.bytes) != {49, 50}:
            self._check()
            self._drain(tree)
            if tree.eof:
                raise ValueError("fixed tree heartbeat ended before both actors")
            time.sleep(0.001)
        return tree

    def _terminal(self, tree: ProbeTree, *, deadline: bool) -> None:
        self._check(terminal=deadline)
        self._subreaper(self.libc)
        if not tree.birth_transferred:
            self._drain(tree)
        if not tree.birth_transferred and (not tree.bytes or not tree.eof):
            raise ValueError("fixed tree heartbeat stop remains unknown")
        for actor in tree.actors:
            if actor.wait_status is None:
                waited, status_value = os.waitpid(actor.pid, os.WNOHANG)
                if waited != actor.pid or not (
                    os.WIFEXITED(status_value) or os.WIFSIGNALED(status_value)
                ):
                    raise ValueError("fixed tree positive terminal wait remains unknown")
                actor.wait_status = status_value
            if not _wait_ready([actor.pidfd], [], [], 0)[0]:
                raise ValueError("fixed tree retained pidfd exit remains unknown")
        if tree.process is None or tree.process.poll() != 0:
            raise ValueError("fixed tree original launcher positive wait remains unknown")
        if tree.launcher_pidfd < 0 or not _wait_ready([tree.launcher_pidfd], [], [], 0)[0]:
            raise ValueError("fixed tree original launcher retained pidfd exit remains unknown")
        sample = self.worker.sample()
        if sample.populated or sample.direct_pids:
            raise ValueError("fixed tree original worker remains populated")
        tree.terminal = True

    def cancel_before_native(self) -> ProbeTree:
        try:
            self._check()
            if self.trees or getattr(self.parent, "_native_handoff", None) is not None:
                raise ValueError("fixed cancellation must precede the original native child")
            sample = self.worker.sample()
            if sample.populated or sample.direct_pids:
                raise ValueError("fixed cancellation requires the original empty worker")
            tree = self._create()
            self.cancelled_tree = tree
            self.worker.stop()
            while self.worker.sample().populated:
                self._check()
                if not tree.birth_transferred:
                    self._drain(tree)
                time.sleep(0.001)
            self._terminal(tree, deadline=False)
            if tree.birth_transferred:
                from crewshal.linux_bridge import send_qualification_tree_terminal

                send_qualification_tree_terminal(self, tree)
            return tree
        except BaseException as error:
            self.failed = True
            raise QualificationProbeRefusal(str(error), self) from error

    def start_deadline_after_native(self, admitted: AdmittedNative) -> ProbeTree:
        try:
            self._check()
            if (
                self.cancelled_tree is None
                or not self.cancelled_tree.terminal
                or len(self.trees) != 1
            ):
                raise ValueError("fixed deadline tree requires completed original cancellation")
            self.watchdog.verify_native_binding(admitted)
            admitted.proc.verify_stopped()
            admitted.proc.read_configuration(self.configuration)
            if self.worker.sample().direct_pids != [admitted.proc.spec.pid]:
                raise ValueError("fixed deadline tree follows sole original native admission")
            self.admitted = admitted
            tree = self._create()
            self.deadline_tree = tree
            return tree
        except BaseException as error:
            self.failed = True
            raise QualificationProbeRefusal(str(error), self) from error

    def finish_deadline(self, captured: CapturedProcess) -> ProbeTree:
        try:
            self._check(terminal=True)
            tree = self.deadline_tree
            if (
                tree is None
                or tree.terminal
                or self.admitted is None
                or getattr(self.watchdog, "_native_capture", None) is not captured
                or captured.observation.termination != "timeout"
                or not captured.observation.tree_stopped
                or captured.observation.exit_code is None
                or time.monotonic_ns() < self.expires_ns
            ):
                raise ValueError("fixed deadline requires actual original terminal timeout")
            self._terminal(tree, deadline=True)
            if tree.birth_transferred:
                from crewshal.linux_bridge import send_qualification_tree_terminal

                send_qualification_tree_terminal(self, tree)
            return tree
        except BaseException as error:
            self.failed = True
            raise QualificationProbeRefusal(str(error), self) from error
