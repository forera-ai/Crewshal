"""Owned setup and terminal lifetime source, never an operational entry point.

Every startup/kernel effect below requires separately qualified trusted callers
and the concrete project/session gate. Offline tests replace those effects.
Inherited sealed data is configuration, not authority or containment evidence.
"""

from dataclasses import dataclass
from datetime import datetime, timezone
import fcntl
import os
from pathlib import PurePosixPath
import select
import stat
import subprocess
import sys
import time
from typing import Literal

from crewshal.admission import (
    NamespaceIdentity,
    _aggregate_readback,
    _current_source,
    _read,
    _stat_identity,
)
from crewshal.contracts import Digest, record_digest
from crewshal.dispatch import DispatchConfiguration
from crewshal.linux_bootstrap import ArmedDeadline, BootstrapPreparation, audit_linux_bootstrap
from crewshal.linux_envelope import prepare_linux_envelope
from crewshal.linux_inventory import (
    RetainedParentInventory,
    TrustedParentInventory,
    bind_parent_inventory,
)
from crewshal.linux_parent import (
    ObservedWatchdog,
    RetainedTrustedTask,
    TrustedTaskSpec,
    _attach,
    _move_self,
    _proc_root,
)
from crewshal.model import Contract
from crewshal.supervisor import CgroupIdentity, OwnedCgroup, _counters

CAPABILITIES = "00000000002801c0"
CONTROL_BOUND = 262144


class NamespaceSetupPreparation(Contract):
    configuration: Digest
    bootstrap: Digest
    parent_argv: list[str]
    parent_executable: Digest
    namespace_argv: list[str]
    control_fds: dict[str, int]
    setup_controls: dict[str, str]
    parent_inventory: TrustedParentInventory | None = None
    unresolved: list[str]
    execution_allowed: Literal[False] = False
    profile_qualified: Literal[False] = False


def prepare_namespace_setup(
    configuration: DispatchConfiguration,
    bootstrap: BootstrapPreparation,
    parent_argv: list[str],
    parent_executable: Digest,
    *,
    parent_inventory: TrustedParentInventory | None = None,
) -> NamespaceSetupPreparation:
    """Passive trusted-parent fragment. It never substitutes for native argv."""
    bootstrap = audit_linux_bootstrap(configuration, bootstrap)
    if (
        parent_inventory is None
        and configuration.linux_envelope is not None
        and configuration.linux_envelope.parent_inventory_sha256 is not None
    ):
        raise ValueError("bound parent inventory cannot be omitted from namespace setup")
    if parent_inventory is not None:
        parent_inventory = bind_parent_inventory(
            configuration,
            parent_inventory,
            parent_argv,
            parent_executable,
            bootstrap.policy.helper_binary,
        )
    if (
        not parent_argv
        or not PurePosixPath(parent_argv[0]).is_absolute()
        or any(not value or "\x00" in value for value in parent_argv)
        or parent_argv[0] in {"/opt/codex/bin/codex", "/usr/bin/bwrap", "/bin/crewshal-bootstrap"}
    ):
        raise ValueError("explicit qualified namespace-parent program required")
    envelope = prepare_linux_envelope(configuration)
    command = ["/usr/bin/bwrap"]
    for mount in envelope.mounts["native"]:
        # The shm overmount must follow bwrap's fresh /dev, as in the envelope.
        if mount.target != "/dev/shm":
            command += ["--ro-bind" if mount.readonly else "--bind", mount.source, mount.target]
    command += [
        "--proc",
        "/proc",
        "--dev",
        "/dev",
        "--unshare-pid",
        "--unshare-net",
        "--unshare-ipc",
        "--unshare-uts",
        "--new-session",
        "--die-with-parent",
        "--clearenv",
        "--chdir",
        "/scratch/checkout",
    ]
    for mount in envelope.mounts["native"]:
        if mount.target == "/dev/shm":
            command += ["--ro-bind", mount.source, mount.target]
    command += ["--cap-drop", "ALL"]
    for name in ("SETGID", "SETUID", "SETPCAP", "SYS_PTRACE", "SYS_ADMIN"):
        command += ["--cap-add", "CAP_" + name]
    # Bwrap introduces PWD even with clearenv. Remove it before the exact parent.
    command += [
        "--",
        "/usr/bin/env",
        "-i",
        "/bin/setpriv",
        "--reuid=0",
        "--regid=0",
        "--clear-groups",
        "--inh-caps=-all",
        "--ambient-caps=-all",
        "--no-new-privs",
        "--",
        *parent_argv,
    ]
    return NamespaceSetupPreparation(
        configuration=record_digest(configuration),
        bootstrap=record_digest(bootstrap),
        parent_argv=list(parent_argv),
        parent_executable=parent_executable,
        namespace_argv=command,
        control_fds={
            "sealed_configuration": 3,
            "aggregate": 4,
            "setup": 5,
            "supervisor": 6,
            "worker": 7,
        },
        setup_controls=dict(envelope.aggregate_controls),
        parent_inventory=parent_inventory,
        unresolved=[
            "qualified_parent_program_and_root_library_inventory",
            "exact_bwrap_init_wrapper_fd_and_role_readback",
            "mediated_network_policy_in_fresh_namespace_before_worker",
            "owned_storage_mount_key_backing_terminal_cleanup",
            *bootstrap.unresolved,
        ],
    )


class InheritedControls(Contract):
    configuration: DispatchConfiguration
    bootstrap: BootstrapPreparation
    setup: NamespaceSetupPreparation
    boot_id: str
    outer_namespaces: dict[str, NamespaceIdentity]
    groups: dict[str, CgroupIdentity]


def _role_controls(group: OwnedCgroup) -> None:
    group._verify()
    for name, expected in {
        "memory.max": "805306368",
        "memory.swap.max": "0",
        "cpu.max": "100000 100000",
        "pids.max": "128",
        "cgroup.type": "domain",
    }.items():
        if group._read(name) != expected:
            raise ValueError("setup/supervisor controls differ from original aggregate ceiling")
    for name, keys in (("memory.events", {"max", "oom", "oom_kill"}), ("pids.events", {"max"})):
        if any(_counters(group._read(name), keys)[key] for key in keys):
            raise ValueError("setup/supervisor has resource-refusal history")


def _topology(
    aggregate: OwnedCgroup, setup: OwnedCgroup, supervisor: OwnedCgroup, worker: OwnedCgroup
) -> None:
    if (
        len({(g.identity.device, g.identity.inode) for g in (aggregate, setup, supervisor, worker)})
        != 4
    ):
        raise ValueError("setup roles require distinct retained groups")
    for group in (setup, supervisor, worker):
        _aggregate_readback(aggregate, group)
    _role_controls(setup)
    _role_controls(supervisor)
    worker.sample()


def _seals() -> tuple[int, int, int]:
    if sys.platform != "linux" or not hasattr(os, "memfd_create"):
        raise ValueError("Linux sealed control transport unavailable")
    return (
        getattr(fcntl, "F_ADD_SEALS"),
        getattr(fcntl, "F_GET_SEALS"),
        sum(
            getattr(fcntl, key)
            for key in ("F_SEAL_WRITE", "F_SEAL_GROW", "F_SEAL_SHRINK", "F_SEAL_SEAL")
        ),
    )


def _capsule(controls: InheritedControls) -> int:
    add, get, seals = _seals()
    raw = controls.model_dump_json().encode()
    if not 0 < len(raw) <= CONTROL_BOUND:
        raise ValueError("inherited configuration exceeds sealed transport bound")
    create = getattr(os, "memfd_create")
    handle: int = create(
        "crewshal-owned-controls", getattr(os, "MFD_CLOEXEC") | getattr(os, "MFD_ALLOW_SEALING")
    )
    try:
        offset = 0
        while offset < len(raw):
            written = os.write(handle, raw[offset:])
            if written <= 0:
                raise ValueError("inherited configuration write incomplete")
            offset += written
        fcntl.fcntl(handle, add, seals)
        if fcntl.fcntl(handle, get) != seals:
            raise ValueError("inherited configuration seals differ")
        return handle
    except BaseException:
        os.close(handle)
        raise


@dataclass
class OwnedNamespaceSetup:
    wrapper: subprocess.Popen[bytes] | None
    controls: InheritedControls
    aggregate: OwnedCgroup
    setup: OwnedCgroup
    supervisor: OwnedCgroup
    worker: OwnedCgroup
    observer_group: OwnedCgroup
    # The outer wrapper is never a native child handle. Physical resources are
    # not reusable from process observations; no unmount/key deletion is supplied.
    resources_reusable: Literal[False] = False
    recovery_deadline: float | None = None
    physical_teardown_claimed: bool = False


class NamespaceSetupRefusal(ValueError):
    def __init__(self, reason: str, lifetime: OwnedNamespaceSetup):
        super().__init__(reason)
        self.lifetime = lifetime
        self.resources_reusable = False


def create_namespace_setup(
    observer: RetainedTrustedTask,
    observer_group: OwnedCgroup,
    aggregate: OwnedCgroup,
    setup: OwnedCgroup,
    supervisor: OwnedCgroup,
    worker: OwnedCgroup,
    configuration: DispatchConfiguration,
    bootstrap: BootstrapPreparation,
    preparation: NamespaceSetupPreparation,
    *,
    inventory: RetainedParentInventory | None = None,
) -> OwnedNamespaceSetup:
    """Unqualified source: fork wrapper/init inside setup, return observer outside.

    The root observer is single-threaded in a bounded aggregate sibling.
    Setup holds only wrappers/init; the inherited child moves itself to the
    supervisor before creating the watchdog. No child is migrated by numeric PID.
    """
    expected = prepare_namespace_setup(
        configuration,
        bootstrap,
        preparation.parent_argv,
        preparation.parent_executable,
        parent_inventory=preparation.parent_inventory,
    )
    if preparation.parent_inventory is not None:
        if inventory is None or inventory.inventory != preparation.parent_inventory:
            raise ValueError("bound setup requires its retained trusted root inventory")
        inventory.verify()
    if (
        expected != preparation
        or bootstrap.policy.helper_binary is None
        or configuration.linux_envelope is None
        or configuration.linux_envelope.bootstrap_policy_sha256 != record_digest(bootstrap.policy)
    ):
        raise ValueError("namespace setup requires current exact source/helper bindings")
    _current_source(configuration)
    _observer_placement(observer, observer_group, aggregate, (setup, supervisor, worker))
    if observer.spec.configuration != record_digest(configuration):
        raise ValueError("owned observer configuration differs")
    _aggregate_readback(aggregate, observer_group)
    _role_controls(observer_group)
    if observer_group._read("cgroup.procs").split() != [str(observer.spec.pid)]:
        raise ValueError("bounded outer observer role must contain only observer")
    _topology(aggregate, setup, supervisor, worker)
    for group in (setup, supervisor, worker):
        if (
            group._read("cgroup.procs")
            or _counters(group._read("cgroup.events"), {"populated"})["populated"]
        ):
            raise ValueError("owned namespace setup requires empty fresh role groups")
    if getattr(observer, "_setup_started", False):
        raise ValueError("namespace setup is one-shot; no retry or reset")
    observer._setup_started = True
    controls = InheritedControls(
        configuration=configuration,
        bootstrap=bootstrap,
        setup=preparation,
        boot_id=observer.spec.boot_id,
        outer_namespaces=observer.spec.namespaces,
        groups={
            name: group.identity
            for name, group in (
                ("aggregate", aggregate),
                ("setup", setup),
                ("supervisor", supervisor),
                ("worker", worker),
            )
        },
    )
    lifetime = OwnedNamespaceSetup(
        None, controls, aggregate, setup, supervisor, worker, observer_group
    )
    capsule = _capsule(controls)
    try:
        try:
            _move_self(setup)
            observer.verify(setup.identity)
            lifetime.wrapper = subprocess.Popen(
                [
                    "/bin/crewshal-bootstrap",
                    "--namespace-fds",
                    str(capsule),
                    str(aggregate.descriptor),
                    str(setup.descriptor),
                    str(supervisor.descriptor),
                    str(worker.descriptor),
                    "--",
                    *preparation.namespace_argv,
                ],
                pass_fds=(
                    capsule,
                    aggregate.descriptor,
                    setup.descriptor,
                    supervisor.descriptor,
                    worker.descriptor,
                ),
                stdin=subprocess.DEVNULL,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                env={},
                close_fds=True,
                cwd="/scratch/checkout",
            )
        finally:
            _move_self_to_observer(observer, observer_group)
        return lifetime
    except BaseException as error:
        raise NamespaceSetupRefusal(str(error), lifetime) from error
    finally:
        os.close(capsule)


def _move_self_to_observer(observer: RetainedTrustedTask, group: OwnedCgroup) -> None:
    _move_self(group)
    observer.verify(group.identity)


def _observer_placement(
    observer: RetainedTrustedTask,
    group: OwnedCgroup,
    aggregate: OwnedCgroup,
    targets: tuple[OwnedCgroup, ...],
) -> None:
    observer.verify(group.identity)
    group._verify()
    aggregate._verify()
    if (
        observer.spec.pid != os.getpid()
        or observer.spec.cgroup != group.identity
        or group.identity in [target.identity for target in targets]
        or PurePosixPath(group.identity.relative_path).parent
        != PurePosixPath(aggregate.identity.relative_path)
    ):
        raise ValueError(
            "outer observer must remain in its owned aggregate sibling outside stopped roles"
        )
    handle = os.open(
        "..", os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC, dir_fd=group.descriptor
    )
    try:
        info = os.fstat(handle)
        if (info.st_dev, info.st_ino) != (aggregate.identity.device, aggregate.identity.inode):
            raise ValueError("outer observer actual aggregate ancestry differs")
    finally:
        os.close(handle)


def receive_namespace_controls() -> tuple[InheritedControls, dict[str, OwnedCgroup]]:
    """Read fixed sealed controls once, independently attach groups, close originals.

    The namespace parent must derive its own actual PID/start/namespace role,
    verify its program, move itself setup->supervisor and establish effective
    policies before creating the watchdog. Capsule data cannot assert that work.
    """
    _, get, seals = _seals()
    groups: dict[str, OwnedCgroup] = {}
    try:
        info = os.fstat(3)
        if (
            not stat.S_ISREG(info.st_mode)
            or not 0 < info.st_size <= CONTROL_BOUND
            or fcntl.fcntl(3, get) != seals
        ):
            raise ValueError("namespace control capsule must be bounded and immutable")
        raw = os.pread(3, info.st_size + 1, 0)
        if len(raw) != info.st_size:
            raise ValueError("namespace control capsule read incomplete")
        controls = InheritedControls.model_validate_json(raw)
        if set(controls.groups) != {"aggregate", "setup", "supervisor", "worker"}:
            raise ValueError("namespace control role inventory differs")
        if (
            prepare_namespace_setup(
                controls.configuration,
                controls.bootstrap,
                controls.setup.parent_argv,
                controls.setup.parent_executable,
                parent_inventory=controls.setup.parent_inventory,
            )
            != controls.setup
        ):
            raise ValueError("inherited namespace preparation differs")
        _current_source(controls.configuration)
        for number, name in enumerate(("aggregate", "setup", "supervisor", "worker"), 4):
            expected = controls.groups[name]
            observed = os.fstat(number)
            if not stat.S_ISDIR(observed.st_mode) or (observed.st_dev, observed.st_ino) != (
                expected.device,
                expected.inode,
            ):
                raise ValueError("inherited group descriptor differs from retained identity")
            groups[name] = OwnedCgroup.attach(expected)
        _topology(groups["aggregate"], groups["setup"], groups["supervisor"], groups["worker"])
        return controls, groups
    except BaseException:
        for group in groups.values():
            group.close()
        raise
    finally:
        for number in range(3, 8):
            os.close(number)


class NamespaceParentRefusal(ValueError):
    def __init__(self, reason: str, parent: RetainedTrustedTask, groups: dict[str, OwnedCgroup]):
        super().__init__(reason)
        self.parent, self.groups = parent, groups
        self.resources_reusable = False


def enter_namespace_parent(
    controls: InheritedControls,
    groups: dict[str, OwnedCgroup],
    *,
    inventory: RetainedParentInventory | None = None,
) -> RetainedTrustedTask:
    """Derive namespace PID/start from procfs, then move only self to supervisor.

    Host and namespace PID numbers are deliberately never compared or passed
    as migration targets. The outer wrapper handle cannot be native admission.
    """
    if controls.setup.parent_inventory is not None:
        if inventory is None or inventory.inventory != controls.setup.parent_inventory:
            raise ValueError("namespace parent requires retained exact root inventory")
        bind_parent_inventory(
            controls.configuration,
            inventory.inventory,
            controls.setup.parent_argv,
            controls.setup.parent_executable,
            controls.bootstrap.policy.helper_binary,
        )
        inventory.verify()
    if set(groups) != set(controls.groups) or any(
        groups[name].identity != identity for name, identity in controls.groups.items()
    ):
        raise ValueError("namespace parent retained controls differ")
    _topology(groups["aggregate"], groups["setup"], groups["supervisor"], groups["worker"])
    if groups["supervisor"]._read("cgroup.procs") or groups["worker"].sample().populated:
        raise ValueError("namespace parent requires empty supervisor and worker")
    root = _proc_root(controls.boot_id)
    descriptor = pidfd = -1
    try:
        descriptor, pidfd = _attach(root, os.getpid())
        pid, _, parent_pid, start = _stat_identity(_read(descriptor, "stat"))
        namespaces: dict[str, NamespaceIdentity] = {}
        if set(controls.outer_namespaces) != {"mnt", "net", "pid", "user", "time"}:
            raise ValueError("namespace parent requires independently retained outer namespaces")
        for name in controls.outer_namespaces:
            observed = os.stat("ns/" + name, dir_fd=descriptor)
            namespaces[name] = NamespaceIdentity(device=observed.st_dev, inode=observed.st_ino)
        if any(
            namespaces[name] == controls.outer_namespaces[name] for name in ("mnt", "net", "pid")
        ):
            raise ValueError("namespace parent must differ from outer mount/network/PID namespaces")
        spec = TrustedTaskSpec(
            configuration=record_digest(controls.configuration),
            pid=pid,
            parent_pid=parent_pid,
            start_ticks=start,
            boot_id=controls.boot_id,
            cgroup=groups["supervisor"].identity,
            namespaces=namespaces,
            executable=controls.setup.parent_executable,
            argv=controls.setup.parent_argv,
            environment={},
            capabilities=CAPABILITIES,
        )
        parent = RetainedTrustedTask(descriptor, pidfd, spec)
    finally:
        for handle in (descriptor, pidfd, root):
            if handle >= 0:
                os.close(handle)
    try:
        if inventory is not None:
            inventory.verify_task_root(parent.descriptor)
        parent.verify(groups["setup"].identity)
        _move_self(groups["supervisor"])
        parent.verify(groups["supervisor"].identity)
        if groups["supervisor"]._read("cgroup.procs").split() != [str(pid)]:
            raise ValueError("supervisor must contain only the namespace parent")
        return parent
    except BaseException as error:
        raise NamespaceParentRefusal(str(error), parent, groups) from error


@dataclass(frozen=True)
class TerminalObservation:
    worker_empty: bool
    watchdog_exited: bool
    watchdog_reaped: bool
    errors: tuple[str, ...]
    resources_reusable: Literal[False] = False


@dataclass(frozen=True)
class NamespaceTerminalObservation:
    groups_empty: bool
    parent_exited: bool
    watchdog_exited: bool
    wrapper_reaped: bool
    errors: tuple[str, ...]
    resources_reusable: Literal[False] = False


def _terminal_task_exited(task: RetainedTrustedTask) -> bool:
    info = os.fstat(task.descriptor)
    if (info.st_dev, info.st_ino) != task.directory:
        raise ValueError("terminal retained task identity changed")
    return bool(select.select([task.pidfd], [], [], 0)[0])


def _terminal_topology(lifetime: OwnedNamespaceSetup) -> None:
    """Cleanup ownership is independent of a resource refusal or changed ceiling."""
    aggregate = lifetime.aggregate
    aggregate._verify()
    groups = {
        "aggregate": aggregate,
        "setup": lifetime.setup,
        "supervisor": lifetime.supervisor,
        "worker": lifetime.worker,
    }
    if any(group.identity != lifetime.controls.groups[name] for name, group in groups.items()):
        raise ValueError("terminal retained cgroup identities differ")
    if len({(g.identity.device, g.identity.inode) for g in groups.values()}) != 4:
        raise ValueError("terminal owned roles must remain distinct")
    for group in (lifetime.setup, lifetime.supervisor, lifetime.worker):
        group._verify()
        if PurePosixPath(group.identity.relative_path).parent != PurePosixPath(
            aggregate.identity.relative_path
        ):
            raise ValueError("terminal owned role ancestry differs")
        handle = os.open(
            "..",
            os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC,
            dir_fd=group.descriptor,
        )
        try:
            info = os.fstat(handle)
            if (info.st_dev, info.st_ino) != (aggregate.identity.device, aggregate.identity.inode):
                raise ValueError("terminal actual owned ancestry differs")
        finally:
            os.close(handle)


def terminal_namespace_setup(
    lifetime: OwnedNamespaceSetup,
    observer: RetainedTrustedTask,
    host_parent: RetainedTrustedTask,
    host_watchdog: RetainedTrustedTask,
    *,
    recovery_already_attempted: bool = False,
) -> NamespaceTerminalObservation:
    """External recovery after parent loss; pinned groups only, one grace.

    Host-side task handles must be attached/qualified independently in the host
    procfs view. Namespace PID values or wrapper PIDs never substitute for them.
    Worker emptiness must be observed before stopping supervisor or setup. Mount,
    key and backing resources remain retained and cannot be reused from this.
    """
    _observer_placement(
        observer,
        lifetime.observer_group,
        lifetime.aggregate,
        (lifetime.setup, lifetime.supervisor, lifetime.worker),
    )
    if (
        host_parent.spec.cgroup != lifetime.supervisor.identity
        or host_watchdog.spec.cgroup != lifetime.supervisor.identity
        or host_parent.spec.pid == host_watchdog.spec.pid
        or host_watchdog.spec.parent_pid != host_parent.spec.pid
        or host_parent.spec.configuration != record_digest(lifetime.controls.configuration)
        or host_watchdog.spec.configuration != host_parent.spec.configuration
        or host_parent.spec.boot_id != observer.spec.boot_id
        or host_watchdog.spec.boot_id != observer.spec.boot_id
        or host_watchdog.spec.executable != lifetime.controls.bootstrap.policy.helper_binary
        or host_parent.spec.executable != lifetime.controls.setup.parent_executable
        or host_parent.spec.argv != lifetime.controls.setup.parent_argv
        or host_parent.spec.capabilities != CAPABILITIES
        or host_watchdog.spec.argv != ["/bin/crewshal-bootstrap", "--watchdog"]
        or host_watchdog.spec.capabilities != "0" * 16
        or host_parent.spec.namespaces != host_watchdog.spec.namespaces
    ):
        raise ValueError("external terminal task/configuration identities differ")
    _terminal_topology(lifetime)
    errors: list[str] = []
    first = lifetime.recovery_deadline is None
    if first:
        lifetime.recovery_deadline = time.monotonic() + (0 if recovery_already_attempted else 1)
        try:
            lifetime.worker.stop()
        except (OSError, ValueError) as error:
            errors.append(str(error))
    empty = parent_exited = watchdog_exited = reaped = False
    roles_stopped = False
    assert lifetime.recovery_deadline is not None
    while True:
        try:
            sample = lifetime.worker.sample()
            worker_empty = not sample.populated and not sample.direct_pids
            if first and worker_empty and not roles_stopped and not errors:
                lifetime.supervisor.stop()
                lifetime.setup.stop()
                roles_stopped = True
            empty = worker_empty and all(
                not group._read("cgroup.procs")
                and _counters(group._read("cgroup.events"), {"populated"})["populated"] == 0
                for group in (lifetime.supervisor, lifetime.setup)
            )
            parent_exited = _terminal_task_exited(host_parent)
            watchdog_exited = _terminal_task_exited(host_watchdog)
            reaped = lifetime.wrapper is not None and lifetime.wrapper.poll() is not None
            if empty and parent_exited and watchdog_exited and reaped:
                break
        except (OSError, ValueError) as error:
            errors.append(str(error))
            break
        if time.monotonic() >= lifetime.recovery_deadline:
            break
        time.sleep(0.001)
    return NamespaceTerminalObservation(
        empty, parent_exited, watchdog_exited, reaped, tuple(errors)
    )


class OwnedWatchdogLifetime:
    """Own every created handle, including a watcher not yet armed or attached."""

    def __init__(self, parent: RetainedTrustedTask, worker: OwnedCgroup, supervisor: OwnedCgroup):
        self.parent, self.worker, self.supervisor = parent, worker, supervisor
        self.process: subprocess.Popen[bytes] | None = None
        self.task: RetainedTrustedTask | None = None
        self.observed: ObservedWatchdog | None = None
        self.kill = self.lifeline = -1
        self.lifeline_identity: tuple[int, int] | None = None
        self.recovery_deadline: float | None = None
        self.resources_reusable = False

    def terminal(self, *, recovery_already_attempted: bool = False) -> TerminalObservation:
        """Close lifeline to stop, never disarm. Re-observation never resets grace.

        A previous handoff refusal consumes recovery grace; this API then only
        performs immediate readback. Retained handles survive every unknown
        result. Even terminal processes do not prove physical storage cleanup.
        """
        errors: list[str] = []
        if self.recovery_deadline is None:
            self.recovery_deadline = time.monotonic() + (0 if recovery_already_attempted else 1)
            # Never kill the worker while cleanup parent might still be inside it.
            try:
                self.parent.verify(self.supervisor.identity)
                if self.lifeline >= 0:
                    info = os.fstat(self.lifeline)
                    if (
                        not stat.S_ISFIFO(info.st_mode)
                        or (info.st_dev, info.st_ino) != self.lifeline_identity
                    ):
                        raise ValueError("terminal lifeline identity changed")
                    os.close(self.lifeline)
                    self.lifeline = -1
                self.worker.stop()
            except (OSError, ValueError) as error:
                errors.append(str(error))
        empty = exited = reaped = False
        while True:
            try:
                sample = self.worker.sample()
                empty = not sample.populated and not sample.direct_pids
                if self.task is not None:
                    exited = _terminal_task_exited(self.task)
                if self.process is not None:
                    reaped = self.process.poll() is not None
                if empty and exited and reaped:
                    break
            except (OSError, ValueError) as error:
                errors.append(str(error))
                break
            if time.monotonic() >= self.recovery_deadline:
                break
            time.sleep(0.001)
        return TerminalObservation(empty, exited, reaped, tuple(errors))


class WatchdogSetupRefusal(ValueError):
    def __init__(self, reason: str, lifetime: OwnedWatchdogLifetime):
        super().__init__(reason)
        self.lifetime = lifetime
        self.resources_reusable = False


def create_owned_watchdog(
    parent: RetainedTrustedTask,
    worker: OwnedCgroup,
    supervisor: OwnedCgroup,
    aggregate: OwnedCgroup,
    configuration: DispatchConfiguration,
    preparation: BootstrapPreparation,
) -> OwnedWatchdogLifetime:
    """Source-only direct watchdog creation before the existing worker bridge."""
    preparation = audit_linux_bootstrap(configuration, preparation)
    _current_source(configuration)
    if (
        preparation.policy.helper_binary is None
        or configuration.linux_envelope is None
        or configuration.linux_envelope.bootstrap_policy_sha256 != record_digest(preparation.policy)
    ):
        raise ValueError("watchdog requires exact current helper/policy binding")
    if (
        parent.spec.pid != os.getpid()
        or parent.spec.cgroup != supervisor.identity
        or parent.spec.configuration != record_digest(configuration)
        or parent.spec.capabilities != CAPABILITIES
    ):
        raise ValueError("watchdog requires the retained namespace parent's exact role")
    _aggregate_readback(aggregate, worker)
    _aggregate_readback(aggregate, supervisor)
    _role_controls(supervisor)
    parent.verify(supervisor.identity)
    if parent._watchdog_started:
        raise ValueError("watchdog creation is one-shot; no retry or reset")
    if supervisor._read("cgroup.procs").split() != [str(parent.spec.pid)]:
        raise ValueError("supervisor must contain only parent before watchdog creation")
    sample = worker.sample()
    if sample.populated or sample.direct_pids:
        raise ValueError("watchdog creation requires an empty worker")
    parent._watchdog_started = True
    lifetime = OwnedWatchdogLifetime(parent, worker, supervisor)
    reading = writing = ready_read = ready_write = -1
    origin_bound = time.monotonic_ns()
    started = datetime.now(timezone.utc)
    try:
        lifetime.kill = os.open(
            "cgroup.kill",
            os.O_WRONLY | os.O_NONBLOCK | os.O_NOFOLLOW | os.O_CLOEXEC,
            dir_fd=worker.descriptor,
        )
        pipe2 = getattr(os, "pipe2")
        reading, writing = pipe2(os.O_CLOEXEC)
        lifetime.lifeline, writing = writing, -1
        info = os.fstat(lifetime.lifeline)
        lifetime.lifeline_identity = (info.st_dev, info.st_ino)
        ready_read, ready_write = pipe2(os.O_CLOEXEC | os.O_NONBLOCK)
        lifetime.process = subprocess.Popen(
            [
                "/bin/setpriv",
                "--reuid=0",
                "--regid=0",
                "--clear-groups",
                "--bounding-set=-all",
                "--inh-caps=-all",
                "--ambient-caps=-all",
                "--no-new-privs",
                "--",
                "/bin/crewshal-bootstrap",
                "--watchdog-fds",
                str(lifetime.kill),
                str(reading),
                str(ready_write),
            ],
            pass_fds=(lifetime.kill, reading, ready_write),
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            cwd="/scratch/checkout",
            env={},
            close_fds=True,
        )
        os.close(reading)
        reading = -1
        os.close(ready_write)
        ready_write = -1
        # Attach before reading readiness, retaining a pidfd even for malformed
        # acknowledgements. No process is identified from helper stdout text.
        root = _proc_root(parent.spec.boot_id)
        descriptor = pidfd = -1
        try:
            descriptor, pidfd = _attach(root, lifetime.process.pid)
            pid, _, parent_pid, start = _stat_identity(_read(descriptor, "stat"))
            spec = TrustedTaskSpec(
                configuration=record_digest(configuration),
                pid=pid,
                parent_pid=parent_pid,
                start_ticks=start,
                boot_id=parent.spec.boot_id,
                cgroup=supervisor.identity,
                namespaces=parent.spec.namespaces,
                executable=preparation.policy.helper_binary,
                argv=preparation.watchdog_argv,
                environment={},
                capabilities="0" * 16,
            )
            lifetime.task = RetainedTrustedTask(descriptor, pidfd, spec)
        finally:
            for handle in (descriptor, pidfd, root):
                if handle >= 0:
                    os.close(handle)
        acknowledgement = bytearray()
        while True:
            if (
                time.monotonic_ns() >= origin_bound + 5_000_000_000
                or lifetime.process.poll() is not None
            ):
                raise ValueError("watchdog startup exhausted original five-second bound")
            readable = select.select([ready_read], [], [], 0.001)[0]
            if not readable:
                continue
            chunk = os.read(ready_read, 81)
            acknowledgement.extend(chunk)
            if len(acknowledgement) > 80:
                raise ValueError("watchdog readiness exceeds bounded record")
            if not chunk:
                break
        deadline = ArmedDeadline.retain(
            lifetime.process,
            lifetime.lifeline,
            worker,
            configuration,
            bytes(acknowledgement),
            started=started,
        )
        if not origin_bound <= deadline.origin_ns:
            raise ValueError("watchdog origin predates owned creation")
        lifetime.observed = ObservedWatchdog(lifetime.task, deadline, lifetime.kill)
        lifetime.observed.check(worker, configuration)
        if set(supervisor._read("cgroup.procs").split()) != {
            str(parent.spec.pid),
            str(lifetime.process.pid),
        }:
            raise ValueError("supervisor watchdog population differs")
        return lifetime
    except BaseException as error:
        # No hidden second grace. Caller receives all handles and performs the
        # single terminal recovery explicitly, before any resource release.
        raise WatchdogSetupRefusal(str(error), lifetime) from error
    finally:
        for handle in (reading, writing, ready_read, ready_write):
            if handle >= 0:
                os.close(handle)
