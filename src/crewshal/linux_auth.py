"""Retain one stock device login in the original charged live setup role."""

import ctypes
import json
import os
import signal
import stat
import subprocess
import resource
import time
from typing import Literal, NoReturn

from crewshal.admission import _wait_ready
from crewshal.admission import _fields, _read, _stat_identity
from crewshal.contracts import Digest
from crewshal.linux_bootstrap import LinuxTrace
from crewshal.linux_inventory import _metadata
from crewshal.linux_inventory import RetainedParentInventory
from crewshal.linux_installed import RetainedInstalledImages
from crewshal.linux_setup import OwnedStorageReservation
from crewshal.supervisor import OwnedCgroup
from crewshal.linux_network import OwnedProviderNetworks, _inventory_file, _static_helper
from crewshal.linux_operational import OriginalInstallationDriver, _hash_file
from crewshal.model import Contract, digest

AUTH_ARGV = [
    "/opt/codex/bin/codex",
    "--config",
    'cli_auth_credentials_store="file"',
    "login",
    "--device-auth",
]
AUTH_ENVIRONMENT = {"HOME": "/native-auth", "CODEX_HOME": "/native-auth", "PATH": "/usr/bin:/bin"}


class FrozenAuthenticationPlan(Contract):
    """Only metadata enters this record. It contains no credential bytes."""

    native_interface: Literal["stock_device_login_v1"] = "stock_device_login_v1"
    configuration_source: Digest
    account_reference: Digest


class AuthenticationRefusal(ValueError):
    def __init__(self, reason: str, owner: "OriginalAuthenticationOwner"):
        super().__init__(reason)
        self.owner = owner


class OriginalAuthenticationProc:
    """Read the original direct child at its two kernel trace stops."""

    owner: "OriginalAuthenticationOwner"
    descriptor: int
    pidfd: int
    directory: tuple[int, int]
    birth: tuple[int, int]
    identity: tuple[int, int, int]
    phase: Literal["helper", "native"]
    _original: tuple[object, ...]

    def __init__(self) -> None:
        raise ValueError("authentication process requires original direct-child custody")

    def __reduce__(self) -> NoReturn:
        raise TypeError("original authentication process cannot be exported")

    def verify_stopped(self) -> None:
        owner = self.owner
        owner._custody()
        if self is not owner.helper_task and self is not owner.task:
            raise ValueError("authentication requires its original retained trace object")
        proc, pidfd = self.descriptor, self.pidfd
        info, birth = os.fstat(proc), os.fstat(pidfd)
        pid, state, parent, ticks = _stat_identity(_read(proc, "stat"))
        status = _fields(_read(proc, "status"))
        if self._original != (
            owner,
            proc,
            pidfd,
            self.directory,
            self.birth,
            self.identity,
            self.phase,
        ):
            raise ValueError("original authentication trace custody changed")
        directory = os.open("fd", os.O_RDONLY | os.O_DIRECTORY | os.O_CLOEXEC, dir_fd=proc)
        try:
            descriptor_names = set(os.listdir(directory))
        finally:
            os.close(directory)
        expected_argv = (
            ["/bin/crewshal-bootstrap", "--authentication-exec"]
            if self.phase == "helper"
            else AUTH_ARGV
        )
        expected_env = {} if self.phase == "helper" else AUTH_ENVIRONMENT
        if (
            (info.st_dev, info.st_ino) != self.directory
            or (birth.st_dev, birth.st_ino) != self.birth
            or (pid, parent, ticks) != self.identity
            or owner.child is None
            or owner.child.pid != pid
            or state not in ("T", "t")
            or status.get("TracerPid") != str(os.getpid())
            or status.get("Uid", "").split() != ["65534"] * 4
            or status.get("Gid", "").split() != ["65534"] * 4
            or status.get("Groups", "").split()
            or status.get("NoNewPrivs") != "1"
            or any(
                status.get(key) != "0000000000000000"
                for key in ("CapEff", "CapPrm", "CapBnd", "CapInh", "CapAmb")
            )
            or _read(proc, "cgroup").strip()
            != ("0::/" + owner.group.identity.relative_path).encode()
            or _read(proc, "cmdline")
            != b"\0".join(value.encode() for value in expected_argv) + b"\0"
            or _read(proc, "environ")
            != b"\0".join((key + "=" + value).encode() for key, value in expected_env.items())
            + (b"\0" if expected_env else b"")
            or os.readlink("cwd", dir_fd=proc) != "/"
            or descriptor_names != {"0", "1", "2"}
            or getattr(resource, "prlimit")(pid, resource.RLIMIT_FSIZE) != (131072, 131072)
        ):
            raise ValueError("actual authentication trace stop or original role differs")
        with open("/proc/self/fdinfo/" + str(pidfd), "rb") as stream:
            if _fields(stream.read(4096)).get("Pid") != str(pid):
                raise ValueError("original authentication pidfd birth differs")
        owner.root.verify_task_root(proc)
        target = os.stat("ns/net", dir_fd=proc)
        original = os.fstat(owner.networks.namespaces["live"])
        if (target.st_dev, target.st_ino) != (original.st_dev, original.st_ino):
            raise ValueError("authentication escaped the original live provider namespace")
        root = os.open("root", os.O_RDONLY | os.O_DIRECTORY | os.O_CLOEXEC, dir_fd=proc)
        try:
            current = os.stat("native-auth", dir_fd=root)
        finally:
            os.close(root)
        original = os.fstat(owner.home)
        if (current.st_dev, current.st_ino) != (original.st_dev, original.st_ino):
            raise ValueError("authentication does not use its original exclusively owned home")
        name = expected_argv[0]
        image = _inventory_file(owner.root, name)
        try:
            if _metadata(os.stat("exe", dir_fd=proc)) != _metadata(os.fstat(image)):
                raise ValueError("authentication executable differs from the actual copied root")
        finally:
            os.close(image)
        owner.trace.verify_storage_policy(proc, "native")
        owner.trace.verify_storage_filter(pid)


class OriginalAuthenticationOwner:
    """A login result cannot reconstruct this original process and volume custody."""

    driver: OriginalInstallationDriver
    reservation: OwnedStorageReservation
    networks: OwnedProviderNetworks
    plan: FrozenAuthenticationPlan
    _plan_payload: str
    group: OwnedCgroup
    root: RetainedParentInventory
    home: int
    origin: float
    deadline: float
    handles: dict[str, int]
    identities: dict[str, tuple[int, int]]
    _owners: tuple[object, ...]
    child: subprocess.Popen[bytes] | None
    failed: bool
    complete: bool
    stdout: bytes
    stderr: bytes
    trace: LinuxTrace
    task: OriginalAuthenticationProc
    helper_task: OriginalAuthenticationProc
    initial_images: RetainedInstalledImages
    native_images: RetainedInstalledImages
    _auth_metadata: tuple[int, ...]
    _buffers: dict[int, bytearray]

    def __init__(self) -> None:
        raise ValueError("authentication requires the original charged driver")

    def __reduce__(self) -> NoReturn:
        raise TypeError("original authentication custody cannot be exported")

    def _retain(self, name: str, descriptor: int) -> int:
        self.handles[name] = descriptor
        info = os.fstat(descriptor)
        self.identities[name] = (info.st_dev, info.st_ino)
        return descriptor

    def _custody(self) -> None:
        from crewshal.linux_batch import _require_original

        _require_original(self.driver)
        if (
            self.failed
            or getattr(self.driver, "_authentication_owner", None) is not self
            or self._owners
            != (
                self.driver,
                self.driver.reservation,
                self.networks,
                self.group,
                self.root,
                self.home,
            )
            or self.plan.model_dump_json() != self._plan_payload
            or self.driver.origin != self.origin
        ):
            raise ValueError("original authentication owner changed")
        profile = self.driver.inputs.configuration.app_server_profile
        if profile is None or profile.account_reference != self.plan.account_reference:
            raise ValueError("authentication account differs from the frozen live profile")
        source = digest(
            json.dumps(
                self.driver.inputs.configuration.source_sha256,
                sort_keys=True,
                separators=(",", ":"),
            ).encode()
        )
        if source != self.plan.configuration_source:
            raise ValueError("authentication source differs from the original frozen profile")
        for name, handle in self.handles.items():
            info = os.fstat(handle)
            if (info.st_dev, info.st_ino) != self.identities[name]:
                raise ValueError("original authentication retained handle changed")
        self.root.verify()

    def _refuse(self, error: BaseException) -> NoReturn:
        self.failed = True
        self.reservation._retain_installation_refusal(error)
        if self.child is not None and self.child.poll() is None:
            try:
                self.group.stop()
            except BaseException as stopping_error:
                error.add_note(f"authentication setup stop remains unknown: {stopping_error}")
            birth = self.handles.get("pidfd")
            if birth is not None:
                try:
                    getattr(signal, "pidfd_send_signal")(birth, signal.SIGKILL, None, 0)
                except BaseException as stopping_error:
                    error.add_note(f"authentication child stop remains unknown: {stopping_error}")
        raise AuthenticationRefusal(str(error), self) from error

    def _wait_stop(self) -> int:
        assert self.child is not None
        assert self.driver.timer is not None
        while time.monotonic() < self.deadline:
            pid, status = os.waitpid(self.child.pid, os.WNOHANG | os.WUNTRACED)
            if pid == self.child.pid:
                if not os.WIFSTOPPED(status):
                    raise ValueError("authentication trace stop remains unknown")
                return status
            proc = self.handles.get("proc")
            if (
                proc is not None
                and _read(proc, "cgroup").strip()
                == ("0::/" + self.group.identity.relative_path).encode()
            ):
                self.driver.timer.verify()
            _wait_ready([], [], [], min(0.001, max(0, self.deadline - time.monotonic())))
        raise ValueError("original authentication preparation deadline expired")

    def verify(self) -> None:
        self._custody()
        if not self.complete or self.child is None or self.child.returncode != 0:
            raise ValueError("original stock authentication completion remains unknown")
        if (
            not _wait_ready([self.task.pidfd], [], [], 0)[0]
            or self.group._read("cgroup.procs")
            or "populated 1" in self.group._read("cgroup.events")
        ):
            raise ValueError("authentication positive reap or empty setup remains unknown")
        with open("/proc/self/fdinfo/" + str(self.task.pidfd), "rb") as stream:
            if _fields(stream.read(4096)).get("Pid") != "-1":
                raise ValueError("authentication original child is not positively reaped")
        info = os.fstat(self.handles["auth-file"])
        now = os.stat("auth.json", dir_fd=self.home, follow_symlinks=False)
        if (
            _metadata(info) != self._auth_metadata
            or _metadata(now) != self._auth_metadata
            or not stat.S_ISREG(info.st_mode)
            or info.st_uid != 65534
            or info.st_gid != 65534
            or info.st_nlink != 1
            or stat.S_IMODE(info.st_mode) != 0o600
            or not 0 < info.st_size <= 65536
        ):
            raise ValueError("original managed authentication inode or exclusive ownership differs")
        # Tokens stay in the native-only home. Actual account/read still occurs
        # inside the one later live app-server exchange.


def authenticate_original_live(
    driver: OriginalInstallationDriver,
    networks: OwnedProviderNetworks,
    plan: FrozenAuthenticationPlan,
) -> OriginalAuthenticationOwner:
    from crewshal.linux_batch import _require_original
    from crewshal.linux_installed import retain_installed_images
    from crewshal.linux_schedule import OwnedThreeLaneSchedule

    _require_original(driver)
    assert driver.reservation is not None
    assert driver.production is not None
    assert driver.timer is not None
    if (
        type(networks) is not OwnedProviderNetworks
        or type(plan) is not FrozenAuthenticationPlan
        or hasattr(driver, "_authentication_owner")
    ):
        raise ValueError("original authentication preparation consumed or unavailable")
    schedule = getattr(driver.reservation, "_lane_schedule", None)
    if (
        type(schedule) is not OwnedThreeLaneSchedule
        or schedule._next != 2
        or schedule._active is not None
        or len(schedule._qualifications) != 2
    ):
        raise ValueError("authentication requires both original completed qualifications")
    schedule.verify()
    owner = object.__new__(OriginalAuthenticationOwner)
    owner.driver, owner.networks = driver, networks
    owner.reservation = driver.reservation
    owner.plan = FrozenAuthenticationPlan.model_validate_json(plan.model_dump_json())
    owner._plan_payload = owner.plan.model_dump_json()
    owner.group = schedule.contexts[2].setup
    owner.root = driver.production.projected_inventory
    owner.home = driver.production.handles["mounted:live--native-auth-upper"]
    owner.origin = driver.origin
    owner.deadline = min(owner.origin + 120, owner.origin + 570)
    owner.handles, owner.identities = {}, {}
    owner._owners = (driver, driver.reservation, networks, owner.group, owner.root, owner.home)
    owner.child = None
    owner.failed = owner.complete = False
    owner.stdout = owner.stderr = b""
    setattr(driver, "_authentication_owner", owner)
    try:
        owner._custody()
        if time.monotonic() >= owner.deadline or os.listdir(owner.home):
            raise ValueError(
                "original authentication requires a fresh empty home before startup expires"
            )
        if owner.group._read("cgroup.procs") or "populated 1" in owner.group._read("cgroup.events"):
            raise ValueError("original live setup is not empty before authentication")
        networks.readback()
        policy = driver.production._payload_storage.policy
        owner.trace = LinuxTrace(policy=policy)
        helper = owner._retain("helper", _inventory_file(owner.root, "/bin/crewshal-bootstrap"))
        _static_helper(helper)
        helper_hash = driver.inputs.bootstrap.policy.helper_binary
        if helper_hash is None:
            raise ValueError("original installed helper identity missing")
        _hash_file(helper, helper_hash, owner.deadline)
        null = owner._retain("null", os.open("/dev/null", os.O_RDONLY | os.O_CLOEXEC))
        controls = (
            owner.group.descriptor,
            owner.root.descriptor,
            owner.home,
            networks.namespaces["live"],
            null,
            driver.production.handles["namespace"],
        )
        owner.child = subprocess.Popen(
            [
                "/proc/self/fd/" + str(helper),
                "--authentication-preparation-fds",
                *(str(fd) for fd in controls),
            ],
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env={},
            cwd="/",
            close_fds=True,
            pass_fds=(*controls, helper),
        )
        pidfd = owner._retain("pidfd", getattr(os, "pidfd_open")(owner.child.pid, 0))
        proc = owner._retain(
            "proc",
            os.open(
                "/proc/" + str(owner.child.pid),
                os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC,
            ),
        )
        stopped = owner._wait_stop()
        if os.WSTOPSIG(stopped) != signal.SIGSTOP:
            raise ValueError("authentication initial trace signal differs")
        task = owner.task = object.__new__(OriginalAuthenticationProc)
        task.owner, task.descriptor, task.pidfd = owner, proc, pidfd
        task.directory = (os.fstat(proc).st_dev, os.fstat(proc).st_ino)
        task.birth = (os.fstat(pidfd).st_dev, os.fstat(pidfd).st_ino)
        pid, _, parent, ticks = _stat_identity(_read(proc, "stat"))
        task.identity, task.phase = (pid, parent, ticks), "helper"
        task._original = (owner, proc, pidfd, task.directory, task.birth, task.identity, task.phase)
        owner.helper_task = task
        if parent != os.getpid():
            raise ValueError("authentication is not the original direct observer child")
        owner.initial_images = retain_installed_images(task, owner.root)
        owner.trace.options(pid)
        owner.trace.continue_exec(pid)
        stopped = owner._wait_stop()
        if (
            os.WSTOPSIG(stopped) != signal.SIGTRAP
            or stopped >> 16 != 4
            or owner.trace.exec_pid(pid) != pid
        ):
            raise ValueError("actual stock authentication exec differs")
        task = owner.task = object.__new__(OriginalAuthenticationProc)
        task.owner, task.descriptor, task.pidfd = owner, proc, pidfd
        task.directory, task.birth, task.identity = (
            owner.helper_task.directory,
            owner.helper_task.birth,
            owner.helper_task.identity,
        )
        task.phase = "native"
        task._original = (owner, proc, pidfd, task.directory, task.birth, task.identity, task.phase)
        owner.native_images = retain_installed_images(task, owner.root)
        owner.trace._call(17, pid, ctypes.c_void_p())
        assert owner.child.stdout is not None and owner.child.stderr is not None
        buffers = {
            owner.child.stdout.fileno(): bytearray(),
            owner.child.stderr.fileno(): bytearray(),
        }
        owner._buffers = buffers
        pending = set(buffers)
        for fd in pending:
            os.set_blocking(fd, False)
        while pending:
            owner._custody()
            remaining = owner.deadline - time.monotonic()
            if remaining <= 0:
                raise ValueError("original device authentication deadline expired")
            for fd in _wait_ready(list(pending), [], [], min(remaining, 0.05))[0]:
                data = os.read(fd, 65537 - len(buffers[fd]))
                buffers[fd].extend(data)
                if len(buffers[fd]) > 65536:
                    raise ValueError("authentication stream exceeds original bound")
                if not data:
                    pending.remove(fd)
                elif fd == owner.child.stdout.fileno():
                    # The approved entry's private console shows the stock
                    # device code. Public evidence excludes these bytes.
                    os.write(1, data)
        owner.stdout, owner.stderr = (
            bytes(buffers[owner.child.stdout.fileno()]),
            bytes(buffers[owner.child.stderr.fileno()]),
        )
        if owner.child.wait(timeout=max(0, owner.deadline - time.monotonic())) != 0:
            raise ValueError("stock device authentication failed")
        auth = owner._retain(
            "auth-file",
            os.open("auth.json", os.O_RDONLY | os.O_NOFOLLOW | os.O_CLOEXEC, dir_fd=owner.home),
        )
        owner._auth_metadata = _metadata(os.fstat(auth))
        owner.complete = True
        owner.verify()
        return owner
    except BaseException as error:
        owner._refuse(error)
