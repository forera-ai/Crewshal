"""Prepare three retained provider networks through the original bounded setup.

Kernel actions require the separate approved batch. This module performs no DNS
lookup, host forwarding change, namespace cleanup, or credential operation.
"""

from array import array
import ctypes
import fcntl
import hashlib
import ipaddress
import json
import os
import re
import signal
import socket
import stat
import subprocess
import time
from typing import NoReturn, Literal

from pydantic import Field, model_validator

from crewshal.admission import _wait_ready
from crewshal.contracts import Digest, record_digest
from crewshal.admission import _fields, _read, _stat_identity
from crewshal.linux_bootstrap import LinuxTrace, TRACEEXEC
from crewshal.linux_installed import _mappings
from crewshal.linux_inventory import RetainedParentInventory, _metadata
from crewshal.linux_setup import LANE_IDS, OwnedStorageReservation
from crewshal.linux_storage import BoundedStorageJobs
from crewshal.model import Contract, digest

NETWORK_BOUND = 65_535
CLONE_NEWNET = 0x40000000
NS_GET_NSTYPE = 0xB703


def _inventory_file(root: RetainedParentInventory, name: str) -> int:
    entry = root.inventory.root.get(name)
    if entry is None or entry.kind != "file" or not name.startswith("/"):
        raise ValueError("network tool file is absent from the exact readonly inventory")
    parts = name.split("/")[1:]
    if any(part in ("", ".", "..") for part in parts):
        raise ValueError("network tool inventory path differs")
    directory = os.dup(root.descriptor)
    try:
        for part in parts[:-1]:
            child = os.open(
                part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC, dir_fd=directory
            )
            os.close(directory)
            directory = child
        return os.open(parts[-1], os.O_RDONLY | os.O_NOFOLLOW | os.O_CLOEXEC, dir_fd=directory)
    finally:
        os.close(directory)


def _static_helper(descriptor: int) -> None:
    """The first helper must not load an unbound host interpreter."""
    raw = os.pread(descriptor, 64, 0)
    if len(raw) != 64 or raw[:6] != b"\x7fELF\x02\x01":
        raise ValueError("network root helper requires a static 64-bit little-endian ELF")
    offset = int.from_bytes(raw[32:40], "little")
    width = int.from_bytes(raw[54:56], "little")
    count = int.from_bytes(raw[56:58], "little")
    info = os.fstat(descriptor)
    if width != 56 or not 0 < count <= 128 or offset + width * count > info.st_size:
        raise ValueError("network root helper ELF program inventory differs")
    headers = os.pread(descriptor, width * count, offset)
    if len(headers) != width * count or any(
        int.from_bytes(headers[index : index + 4], "little") == 3
        for index in range(0, len(headers), width)
    ):
        raise ValueError("network root helper has an unbound host ELF interpreter")


class RetainedNetworkTool:
    """Check original trace stops and all observed mappings before positive reap."""

    def __init__(
        self,
        owner: "OwnedProviderNetworks",
        child: subprocess.Popen[bytes],
        name: str,
        arguments: list[str],
        network: tuple[int, int],
        inherited: bool,
    ):
        self.owner, self.child = owner, child
        self.name, self.arguments, self.network = name, list(arguments), network
        self.inherited = inherited
        self.descriptor = self.pidfd = -1
        self.handles: dict[tuple[str, int, int], int] = {}
        self.metadata: dict[tuple[str, int, int], tuple[int, ...]] = {}
        self.snapshots: list[dict[str, object]] = []
        self.closed = False
        self.pidfd = getattr(os, "pidfd_open")(child.pid, 0)
        self.descriptor = os.open(
            f"/proc/{child.pid}", os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC
        )
        info = os.fstat(self.descriptor)
        self.directory = info.st_dev, info.st_ino
        info = os.fstat(self.pidfd)
        self.birth = info.st_dev, info.st_ino
        self.start = _stat_identity(_read(self.descriptor, "stat"))[3]

    def verify(self, *, initial: bool) -> None:
        root = self.owner.inventory
        group = self.owner.jobs.execution_group
        if root is None or group is None or self.closed:
            raise ValueError("original network tool copied root custody missing")
        info, birth = os.fstat(self.descriptor), os.fstat(self.pidfd)
        pid, state, parent, start = _stat_identity(_read(self.descriptor, "stat"))
        fields = _fields(_read(self.descriptor, "status"))
        with open(f"/proc/self/fdinfo/{self.pidfd}", "rb") as stream:
            fdinfo = _fields(stream.read(4096))
        expected = "/bin/crewshal-bootstrap" if initial else "/usr/sbin/" + self.name
        expected_argv = (
            [
                expected,
                "--network-tool-exec",
                "4" if self.inherited else "0",
                self.name,
                *self.arguments,
            ]
            if initial
            else [expected, *self.arguments]
        )
        if (
            (info.st_dev, info.st_ino) != self.directory
            or (birth.st_dev, birth.st_ino) != self.birth
            or (pid, parent, start) != (self.child.pid, os.getpid(), self.start)
            or state not in ("T", "t")
            or fdinfo.get("Pid") != str(pid)
            or fields.get("TracerPid") != str(os.getpid())
            or fields.get("Uid", "").split() != ["0"] * 4
            or fields.get("Gid", "").split() != ["0"] * 4
            or fields.get("Groups", "").split()
            or fields.get("Threads") != "1"
            or fields.get("NoNewPrivs") != "1"
            or any(
                fields.get(key) != self.owner.reservation.observer.spec.capabilities
                for key in ("CapEff", "CapPrm", "CapBnd")
            )
            or any(fields.get(key) != "0000000000000000" for key in ("CapInh", "CapAmb"))
            or _read(self.descriptor, "cgroup").decode().strip()
            != "0::/" + group.identity.relative_path
            or _read(self.descriptor, "cmdline")
            != b"\0".join(value.encode() for value in expected_argv) + b"\0"
            or _read(self.descriptor, "environ")
            or os.readlink("cwd", dir_fd=self.descriptor) != "/"
            or (lambda n: (n.st_dev, n.st_ino))(os.stat("ns/net", dir_fd=self.descriptor))
            != self.network
        ):
            raise ValueError("actual original network tool task or trace stop differs")
        root.verify_task_root(self.descriptor)
        executable = _inventory_file(root, expected)
        try:
            if _metadata(os.stat("exe", dir_fd=self.descriptor)) != _metadata(os.fstat(executable)):
                raise ValueError("actual network tool executable differs from the copied root")
        finally:
            os.close(executable)
        rows = _mappings(_read(self.descriptor, "maps", 262144))
        for address, mapping in rows.items():
            name, device, inode, _, _ = mapping
            key = name, device, inode
            if key not in self.handles:
                handle = os.open(
                    "map_files/" + address, os.O_RDONLY | os.O_CLOEXEC, dir_fd=self.descriptor
                )
                self.handles[key] = handle
            handle = self.handles[key]
            before = os.fstat(handle)
            entry = root.inventory.root.get(name)
            if (
                entry is None
                or entry.kind != "file"
                or (before.st_dev, before.st_ino) != (device, inode)
                or _metadata(os.stat("map_files/" + address, dir_fd=self.descriptor))
                != _metadata(before)
                or not stat.S_ISREG(before.st_mode)
                or before.st_uid != 0
                or before.st_gid != 0
                or before.st_mode & 0o7022
                or before.st_nlink != 1
                or before.st_size > 134217728
                or not os.fstatvfs(handle).f_flag & os.ST_RDONLY
            ):
                raise ValueError("network tool has an unlisted or writable mapped image")
            original = _inventory_file(root, name)
            try:
                if _metadata(os.fstat(original)) != _metadata(before):
                    raise ValueError("network tool loaded a host loader or plugin inode")
            finally:
                os.close(original)
            if key not in self.metadata:
                sha = hashlib.sha256()
                offset = 0
                while offset < before.st_size:
                    part = os.pread(handle, min(65536, before.st_size - offset), offset)
                    if not part:
                        raise ValueError("network mapped image readback is incomplete")
                    sha.update(part)
                    offset += len(part)
                if sha.hexdigest() != entry.sha256:
                    raise ValueError("network mapped loader or plugin bytes differ")
                self.metadata[key] = _metadata(before)
            if self.metadata[key] != _metadata(os.fstat(handle)):
                raise ValueError("network mapped image identity changed")
        if _mappings(_read(self.descriptor, "maps", 262144)) != rows:
            raise ValueError("network tool mapping set changed during readback")
        self.snapshots.append(
            {
                "phase": "helper" if initial else "tool",
                "files": sorted(
                    (name, device, inode, self.metadata[(name, device, inode)])
                    for name, device, inode in self.handles
                ),
                "root": root.identity,
            }
        )

    def close_known_terminal(self) -> None:
        if self.child.poll() is None or not _wait_ready([self.pidfd], [], [], 0)[0]:
            raise ValueError("network tool positive terminal wait remains unknown")
        for handle in {*self.handles.values(), self.descriptor, self.pidfd}:
            if handle >= 0:
                os.close(handle)
        self.closed = True


class LaneNetworkPlan(Contract):
    lane_id: str
    host_interface: str = Field(pattern=r"^cs[0-9a-f]{8}[123]h$")
    private_interface: str = Field(pattern=r"^cs[0-9a-f]{8}[123]p$")
    subnet: str

    @model_validator(mode="after")
    def finite(self) -> "LaneNetworkPlan":
        network = ipaddress.IPv4Network(self.subnet, strict=True)
        if self.lane_id not in LANE_IDS or network.prefixlen != 30 or not network.is_private:
            raise ValueError("exact private original lane subnet required")
        if self.host_interface[:-1] != self.private_interface[:-1]:
            raise ValueError("original paired interface names differ")
        return self

    @property
    def host_address(self) -> str:
        return str(ipaddress.IPv4Network(self.subnet).network_address + 1)

    @property
    def private_address(self) -> str:
        return str(ipaddress.IPv4Network(self.subnet).network_address + 2)


class ProviderNetworkPlan(Contract):
    configuration_source: Digest
    ip_binary: Digest
    nft_binary: Digest
    host_table: str = Field(pattern=r"^crewshal_[0-9a-f]{8}$")
    endpoints: dict[str, list[str]]
    lanes: list[LaneNetworkPlan]
    qualification_transport: Literal["original_two_lane_tls_v1"] | None = None

    @model_validator(mode="after")
    def finite(self) -> "ProviderNetworkPlan":
        if tuple(lane.lane_id for lane in self.lanes) != LANE_IDS:
            raise ValueError("three original network lanes required")
        if not self.endpoints or len(self.endpoints) > 16:
            raise ValueError("bounded audited provider hostname inventory required")
        count = 0
        for hostname, addresses in self.endpoints.items():
            if re.fullmatch(r"[a-z0-9](?:[a-z0-9.-]{0,251}[a-z0-9])?", hostname) is None:
                raise ValueError("exact provider hostname required")
            if not addresses or len(addresses) > 16 or len(set(addresses)) != len(addresses):
                raise ValueError("bounded unique provider endpoints required")
            for address in addresses:
                value = ipaddress.IPv4Address(address)
                if not value.is_global or value.is_multicast or value.is_reserved:
                    raise ValueError("public IPv4 provider endpoint required")
            count += len(addresses)
        if count > 64 or len({lane.host_interface for lane in self.lanes}) != 3:
            raise ValueError("provider endpoint or interface bound differs")
        networks = [ipaddress.IPv4Network(lane.subnet) for lane in self.lanes]
        if any(
            left.overlaps(right)
            for index, left in enumerate(networks)
            for right in networks[index + 1 :]
        ):
            raise ValueError("original lane networks overlap")
        return self

    @property
    def hosts_bytes(self) -> bytes:
        lines = ["127.0.0.1 localhost", "::1 localhost"]
        lines += [
            f"{address} {host}"
            for host, addresses in sorted(self.endpoints.items())
            for address in addresses
        ]
        return ("\n".join(lines) + "\n").encode("ascii")


def _match(left: object, right: object) -> dict[str, object]:
    return {"match": {"op": "==", "left": left, "right": right}}


def _meta(key: str) -> dict[str, object]:
    return {"meta": {"key": key}}


def _payload(protocol: str, field: str) -> dict[str, object]:
    return {"payload": {"protocol": protocol, "field": field}}


def nft_table(plan: ProviderNetworkPlan, lane: LaneNetworkPlan | None) -> list[dict[str, object]]:
    """Return exact finite rules. Ordinary tool and validator traffic stays denied."""
    table = plan.host_table if lane is None else "crewshal_provider"
    objects: list[dict[str, object]] = [{"table": {"family": "inet", "name": table}}]

    def chain(
        name: str, hook: str, policy: str, *, kind: str = "filter", priority: int = 0
    ) -> None:
        objects.append(
            {
                "chain": {
                    "family": "inet",
                    "table": table,
                    "name": name,
                    "type": kind,
                    "hook": hook,
                    "prio": priority,
                    "policy": policy,
                }
            }
        )

    def rule(name: str, expressions: list[object], verdict: str) -> None:
        objects.append(
            {
                "rule": {
                    "family": "inet",
                    "table": table,
                    "chain": name,
                    "expr": [*expressions, {verdict: None}],
                }
            }
        )

    endpoints = sorted({address for addresses in plan.endpoints.values() for address in addresses})
    provider_allowed = [
        _match(_payload("ip", "daddr"), {"set": endpoints}),
        _match(_payload("tcp", "dport"), 443),
    ]
    established = _match({"ct": {"key": "state"}}, {"set": ["established", "related"]})
    if lane is not None:
        qualification = (
            plan.qualification_transport == "original_two_lane_tls_v1"
            and lane.lane_id in ("qualification-1", "qualification-2")
        )
        allowed = provider_allowed
        if qualification:
            # Both synthetic lanes retain the same provider hostname inventory.
            # Only their declared network tables redirect HTTPS to the owned fixture.
            chain("fixture_route", "output", "accept", kind="nat", priority=-100)
            objects.append(
                {
                    "rule": {
                        "family": "inet",
                        "table": table,
                        "chain": "fixture_route",
                        "expr": [
                            _match(_meta("skuid"), 65534),
                            *provider_allowed,
                            {"dnat": {"addr": lane.host_address}},
                        ],
                    }
                }
            )
            allowed = [
                _match(_payload("ip", "daddr"), lane.host_address),
                _match(_payload("tcp", "dport"), 443),
            ]
        chain("output", "output", "drop")
        chain("input", "input", "drop")
        chain("forward", "forward", "drop")
        rule("output", [_match(_meta("oifname"), "lo")], "accept")
        rule("output", [_match(_meta("skuid"), 65534), *allowed], "accept")
        rule("input", [_match(_meta("iifname"), "lo")], "accept")
        rule("input", [established], "accept")
    else:
        chain("forward", "forward", "accept", priority=-10)
        chain("input", "input", "accept", priority=-10)
        chain("postrouting", "postrouting", "accept", kind="nat", priority=100)
        for item in plan.lanes:
            incoming = _match(_meta("iifname"), item.host_interface)
            outgoing = _match(_meta("oifname"), item.host_interface)
            qualification = (
                plan.qualification_transport == "original_two_lane_tls_v1"
                and item.lane_id in ("qualification-1", "qualification-2")
            )
            if qualification:
                rule(
                    "input",
                    [
                        incoming,
                        _match(_payload("ip", "saddr"), item.private_address),
                        _match(_payload("ip", "daddr"), item.host_address),
                        _match(_payload("tcp", "dport"), 443),
                    ],
                    "accept",
                )
            rule("input", [incoming], "drop")
            if not qualification:
                rule(
                    "forward",
                    [
                        incoming,
                        _match(_payload("ip", "saddr"), item.private_address),
                        *provider_allowed,
                    ],
                    "accept",
                )
            rule("forward", [incoming], "drop")
            rule("forward", [outgoing, established], "accept")
            rule("forward", [outgoing], "drop")
            if not qualification:
                rule(
                    "postrouting",
                    [_match(_payload("ip", "saddr"), item.private_address), *provider_allowed],
                    "masquerade",
                )
    return objects


def canonical_nft(raw: bytes) -> list[dict[str, object]]:
    """Keep every semantic field. Remove only kernel handles and version metadata."""
    value = json.loads(raw)
    if (
        not isinstance(value, dict)
        or set(value) != {"nftables"}
        or not isinstance(value["nftables"], list)
    ):
        raise ValueError("exact nft JSON readback required")
    objects: list[dict[str, object]] = []
    for item in value["nftables"]:
        if not isinstance(item, dict) or len(item) != 1:
            raise ValueError("nft object inventory differs")
        name, data = next(iter(item.items()))
        if name == "metainfo":
            continue
        if name not in {"table", "chain", "rule"} or not isinstance(data, dict):
            raise ValueError("unexpected nft policy object")
        objects.append({name: {key: content for key, content in data.items() if key != "handle"}})
    return objects


def _net_namespace(descriptor: int) -> tuple[int, int]:
    info = os.fstat(descriptor)
    if (
        fcntl.ioctl(descriptor, NS_GET_NSTYPE) != CLONE_NEWNET
        or fcntl.fcntl(descriptor, fcntl.F_GETFL) & os.O_ACCMODE != os.O_RDONLY
    ):
        raise ValueError("actual readonly network namespace FD required")
    return info.st_dev, info.st_ino


def _setns(descriptor: int) -> None:
    _net_namespace(descriptor)
    libc = ctypes.CDLL(None, use_errno=True)
    if libc.setns(descriptor, CLONE_NEWNET):
        raise OSError(ctypes.get_errno(), "original network namespace entry refused")


class NetworkRefusal(ValueError):
    def __init__(self, reason: str, owner: "OwnedProviderNetworks"):
        super().__init__(reason)
        self.owner = owner
        self.resources_reusable = False


class _NetworkTransfer:
    def __init__(self, owner: "OwnedProviderNetworks"):
        self.owner = owner
        self.parent, self.child = socket.socketpair(
            socket.AF_UNIX,
            socket.SOCK_SEQPACKET
            | getattr(socket, "SOCK_CLOEXEC")
            | getattr(socket, "SOCK_NONBLOCK"),
        )
        self.position = 0

    @property
    def descriptor(self) -> int:
        return self.parent.fileno()

    def transfer(self, lane: str, descriptor: int) -> None:
        deadline = self.owner.jobs.deadline
        if not _wait_ready([], [self.child], [], max(0, deadline - time.monotonic()))[1]:
            raise ValueError("original network transfer deadline expired")
        raw = lane.encode("ascii")
        if self.child.sendmsg(
            [raw], [(socket.SOL_SOCKET, socket.SCM_RIGHTS, array("i", [descriptor]))]
        ) != len(raw):
            raise ValueError("original network FD transfer incomplete")
        if (
            not _wait_ready([self.child], [], [], max(0, deadline - time.monotonic()))[0]
            or self.child.recv(2) != b"1"
        ):
            raise ValueError("original network custody acknowledgement unavailable")

    def pump(self) -> None:
        raw, ancillary, flags, _ = self.parent.recvmsg(
            128, socket.CMSG_SPACE(16 * array("i").itemsize), getattr(socket, "MSG_CMSG_CLOEXEC")
        )
        received: list[int] = []
        malformed = False
        for level, kind, value in ancillary:
            if level != socket.SOL_SOCKET or kind != socket.SCM_RIGHTS:
                malformed = True
                continue
            descriptors = array("i")
            if len(value) % descriptors.itemsize:
                malformed = True
            descriptors.frombytes(value[: len(value) - len(value) % descriptors.itemsize])
            for descriptor in descriptors:
                self.owner.received.append(descriptor)
                received.append(descriptor)
        if (
            malformed
            or flags & (socket.MSG_TRUNC | socket.MSG_CTRUNC)
            or len(received) != 1
            or self.position >= 3
            or raw != LANE_IDS[self.position].encode()
        ):
            raise ValueError("original network FD custody inventory differs")
        lane, descriptor = LANE_IDS[self.position], received[0]
        identity = _net_namespace(descriptor)
        if (
            identity == self.owner._host_identity
            or identity in self.owner._namespace_identities.values()
        ):
            raise ValueError("original provider namespace aliases another owner")
        self.owner.namespaces[lane] = descriptor
        self.owner._namespace_identities[lane] = identity
        self.owner.verify_custody()
        if self.parent.send(b"1") != 1:
            raise ValueError("original network custody acknowledgement refused")
        self.position += 1


class OwnedProviderNetworks:
    """Retain one finite three-network installation and every unknown partial result."""

    def __init__(
        self,
        reservation: OwnedStorageReservation,
        jobs: BoundedStorageJobs,
        plan: ProviderNetworkPlan,
        host_namespace: int,
        ip_binary: int,
        nft_binary: int,
        *,
        readback_jobs: BoundedStorageJobs | None = None,
        inventory: RetainedParentInventory | None = None,
    ):
        if (
            type(reservation) is not OwnedStorageReservation
            or type(jobs) is not BoundedStorageJobs
            or hasattr(reservation, "_provider_networks")
        ):
            raise ValueError("original provider network production is one-shot")
        self.reservation, self.jobs = reservation, jobs
        self.readback_jobs = jobs if readback_jobs is None else readback_jobs
        self.plan = ProviderNetworkPlan.model_validate_json(plan.model_dump_json())
        self._plan_digest = record_digest(self.plan)
        self.host_namespace, self.ip_binary, self.nft_binary = host_namespace, ip_binary, nft_binary
        self.inventory = inventory
        production = getattr(reservation, "_production", None)
        self.production_namespace = getattr(production, "handles", {}).get("namespace", -1)
        self._owners = (
            reservation,
            jobs,
            self.readback_jobs,
            host_namespace,
            ip_binary,
            nft_binary,
            inventory,
        )
        self._tool_owners: list[RetainedNetworkTool] = []
        self._tool_records: list[dict[str, object]] = []
        self.tool_readbacks: list[list[dict[str, object]]] = []
        self.received: list[int] = []
        self.namespaces: dict[str, int] = {}
        self._namespace_identities: dict[str, tuple[int, int]] = {}
        self._snapshots: bytes | None = None
        self.failed = False
        self.attempted = False
        setattr(reservation, "_provider_networks", self)
        try:
            self._host_identity = _net_namespace(host_namespace)
            if type(inventory) is not RetainedParentInventory:
                raise ValueError("original network tools require the complete copied readonly root")
            inventory.verify()
            if not os.fstatvfs(inventory.descriptor).f_flag & os.ST_RDONLY:
                raise ValueError("original network tool copied root is writable")
            helper = _inventory_file(inventory, "/bin/crewshal-bootstrap")
            try:
                _static_helper(helper)
            finally:
                os.close(helper)
            from crewshal.linux_production import OwnedBackingProduction

            if (
                type(production) is not OwnedBackingProduction
                or production.reservation is not reservation
            ):
                raise ValueError("network tools require their original production mount namespace")
            mount = os.fstat(self.production_namespace)
            self._production_namespace_identity = mount.st_dev, mount.st_ino
            self.verify_custody()
        except BaseException as error:
            self._refuse(error)

    def __reduce__(self) -> NoReturn:
        raise TypeError("original network custody cannot be exported or copied")

    def _refuse(self, error: BaseException) -> NoReturn:
        self.failed = True
        self.reservation._retain_installation_refusal(error)
        raise NetworkRefusal(str(error), self) from error

    def verify_custody(self) -> None:
        if (
            self.failed
            or getattr(self.reservation, "_provider_networks", None) is not self
            or self._owners
            != (
                self.reservation,
                self.jobs,
                self.readback_jobs,
                self.host_namespace,
                self.ip_binary,
                self.nft_binary,
                self.inventory,
            )
            or record_digest(self.plan) != self._plan_digest
        ):
            raise ValueError("original provider network owner changed")
        self.reservation.verify()
        timer = self.reservation._batch_timer
        for jobs in (self.jobs, self.readback_jobs):
            if (
                type(jobs) is not BoundedStorageJobs
                or jobs.observer is not self.reservation.observer
                or jobs.group is not self.reservation.observer_group
                or jobs.aggregate is not self.reservation.aggregate
                or jobs.batch_timer is not timer
                or jobs.execution_group is not timer.setup
                or jobs.deadline > self.reservation.batch_started + 570
            ):
                raise ValueError("provider network requires original bounded setup job")
        configuration = self.reservation._configuration
        bindings = configuration.linux_envelope
        if (
            bindings is None
            or self.inventory is None
            or bindings.parent_inventory_sha256 != record_digest(self.inventory.inventory)
            or (lambda info: (info.st_dev, info.st_ino))(os.fstat(self.inventory.descriptor))
            != self.inventory.identity
            or not os.fstatvfs(self.inventory.descriptor).f_flag & os.ST_RDONLY
            or bindings.network_policy_sha256 != self._plan_digest
            or digest(
                json.dumps(
                    configuration.source_sha256, sort_keys=True, separators=(",", ":")
                ).encode()
            )
            != self.plan.configuration_source
        ):
            raise ValueError("provider network plan differs from original dispatch binding")
        if _net_namespace(self.host_namespace) != self._host_identity:
            raise ValueError("original host network namespace changed")
        original_host = self.reservation.observer.spec.namespaces["net"]
        production = getattr(self.reservation, "_production", None)
        actual_mount = os.fstat(self.production_namespace)
        if (
            getattr(production, "handles", {}).get("namespace") != self.production_namespace
            or (actual_mount.st_dev, actual_mount.st_ino) != self._production_namespace_identity
            or fcntl.ioctl(self.production_namespace, NS_GET_NSTYPE) != 0x20000
            or fcntl.fcntl(self.production_namespace, fcntl.F_GETFL) & os.O_ACCMODE != os.O_RDONLY
        ):
            raise ValueError("original production mount namespace custody differs")
        if self._host_identity != (original_host.device, original_host.inode):
            raise ValueError("provider network must retain the original observer host namespace")
        for lane, descriptor in self.namespaces.items():
            if _net_namespace(descriptor) != self._namespace_identities[lane]:
                raise ValueError("original provider namespace identity changed")
        for descriptor, expected in (
            (self.ip_binary, self.plan.ip_binary),
            (self.nft_binary, self.plan.nft_binary),
        ):
            info = os.fstat(descriptor)
            if (
                not stat.S_ISREG(info.st_mode)
                or info.st_uid != 0
                or info.st_gid != 0
                or info.st_mode & 0o7022
                or not info.st_mode & 0o111
                or not 0 < info.st_size <= 16_777_216
            ):
                raise ValueError("original trusted network executable identity differs")
            value = hashlib.sha256()
            offset = 0
            while offset < info.st_size:
                part = os.pread(descriptor, min(65536, info.st_size - offset), offset)
                if not part:
                    raise ValueError("original network executable read incomplete")
                value.update(part)
                offset += len(part)
            if value.hexdigest() != expected or os.fstat(descriptor) != info:
                raise ValueError("original trusted network executable bytes changed")
            name = "/usr/sbin/ip" if descriptor == self.ip_binary else "/usr/sbin/nft"
            copied = _inventory_file(self.inventory, name)
            try:
                if _metadata(os.fstat(copied)) != _metadata(info):
                    raise ValueError(
                        "original network executable does not use the copied-root inode"
                    )
            finally:
                os.close(copied)

    def create(self) -> None:
        if self.attempted:
            raise ValueError("original provider network creation consumed; no retry")
        self.attempted = True
        self.transfer = _NetworkTransfer(self)
        try:
            self.verify_custody()
            keep = {
                self.host_namespace,
                self.ip_binary,
                self.nft_binary,
                self.transfer.child.fileno(),
                self.inventory.descriptor if self.inventory is not None else -1,
                self.production_namespace,
            }
            raw = self.jobs.run(self._create_child, keep, transfer=self.transfer)
            if self.transfer.position != 3 or set(self.namespaces) != set(LANE_IDS):
                raise ValueError("complete original provider namespace custody missing")
            self._snapshots = self._network_report(raw)
            self.verify_custody()
            self.readback()
        except BaseException as error:
            self._refuse(error)

    def verify_registered_job(self, jobs: BoundedStorageJobs) -> None:
        if jobs not in (self.jobs, self.readback_jobs):
            raise ValueError("original network readback job differs")
        self.verify_custody()

    def verify_registered_action(self, jobs: BoundedStorageJobs, action: object) -> None:
        if (
            jobs not in (self.jobs, self.readback_jobs)
            or getattr(action, "__self__", None) is not self
            or getattr(action, "__func__", None) is not OwnedProviderNetworks._readback_child
        ):
            raise ValueError("original provider network readback action differs")
        self.verify_custody()

    def _command(
        self,
        name: str,
        arguments: list[str],
        *,
        data: bytes | None = None,
        inherited: tuple[int, ...] = (),
    ) -> bytes:
        if (
            name not in ("ip", "nft")
            or self.inventory is None
            or len(inherited) > 1
            or len(self._tool_records) >= 128
        ):
            raise ValueError("fixed original readonly network tool route required")
        active = [
            jobs for jobs in {self.jobs, self.readback_jobs} if jobs._active_deadline is not None
        ]
        if len(active) != 1:
            raise ValueError("one original active network job required")
        deadline = active[0]._active_deadline
        if deadline is None or deadline > active[0].deadline or time.monotonic() >= deadline:
            raise ValueError("original active network job deadline required")
        arguments = list(arguments)
        if inherited:
            original = f"/proc/self/fd/{inherited[0]}"
            if name != "ip" or arguments[-2:] != ["netns", original]:
                raise ValueError("fixed network target FD requires exact ip namespace argument")
            _net_namespace(inherited[0])
            arguments[-1] = "/proc/fd/4"
        current_network = os.stat("/proc/self/ns/net")
        child = subprocess.Popen(
            [
                "/bin/crewshal-bootstrap",
                "--network-tool-root-fds",
                str(self.inventory.descriptor),
                str(inherited[0] if inherited else 0),
                str(self.production_namespace),
                "--",
                name,
                *arguments,
            ],
            executable=f"/proc/self/fd/{self.inventory.descriptor}/bin/crewshal-bootstrap",
            pass_fds=(self.inventory.descriptor, self.production_namespace, *inherited),
            stdin=subprocess.PIPE if data is not None else subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            env={},
            cwd="/",
            close_fds=True,
        )
        assert child.stdout is not None
        output = bytearray()
        retained: RetainedNetworkTool | None = None
        known_terminal = False
        try:
            # Bind before attachment. A partial refusal keeps every acquired FD.
            retained = object.__new__(RetainedNetworkTool)
            self._tool_owners.append(retained)
            RetainedNetworkTool.__init__(
                retained,
                self,
                child,
                name,
                arguments,
                (current_network.st_dev, current_network.st_ino),
                bool(inherited),
            )
            trace = LinuxTrace()

            def wait_status() -> int:
                while time.monotonic() < deadline:
                    waited, status = os.waitpid(child.pid, os.WNOHANG | 0x40000000)
                    if waited == child.pid:
                        return status
                    time.sleep(0.001)
                raise ValueError("original network tool trace deadline expired")

            initial = wait_status()
            if not os.WIFSTOPPED(initial) or os.WSTOPSIG(initial) != 19 or initial >> 16:
                raise ValueError("original network helper initial trace stop differs")
            retained.verify(initial=True)
            trace._call(0x4200, child.pid, ctypes.c_void_p(TRACEEXEC | 0x00100000 | 0x4E))
            trace.continue_exec(child.pid)
            executed = wait_status()
            if (
                not os.WIFSTOPPED(executed)
                or executed >> 16 != 4
                or trace.exec_pid(child.pid) != child.pid
            ):
                raise ValueError("original network tool exec stop differs")
            retained.verify(initial=False)
            trace.continue_exec(child.pid)
            os.set_blocking(child.stdout.fileno(), False)
            offset, ended, exited = 0, False, False
            exit_checked = False
            if data is not None:
                if len(data) > NETWORK_BOUND or child.stdin is None:
                    raise ValueError("fixed network tool input exceeds its bound")
                os.set_blocking(child.stdin.fileno(), False)
            while not (ended and exited):
                if time.monotonic() >= deadline:
                    raise ValueError("original network command deadline expired")
                if not exited:
                    waited, status = os.waitpid(child.pid, os.WNOHANG | 0x40000000)
                    if waited == child.pid:
                        if os.WIFSTOPPED(status):
                            if status >> 16 != 6 or exit_checked:
                                raise ValueError(
                                    "network tool created a descendant or unexpected trace event"
                                )
                            retained.verify(initial=False)
                            exit_checked = True
                            trace.continue_exec(child.pid)
                        elif os.WIFEXITED(status) or os.WIFSIGNALED(status):
                            child.returncode = os.waitstatus_to_exitcode(status)
                            exited = True
                        else:
                            raise ValueError("network tool terminal wait status differs")
                writing = (
                    [child.stdin]
                    if (data is not None and offset < len(data) and child.stdin is not None)
                    else []
                )
                ready, writable, _ = _wait_ready(
                    [] if ended else [child.stdout], writing, [], 0.001
                )
                if writable:
                    assert data is not None and child.stdin is not None
                    offset += os.write(child.stdin.fileno(), data[offset:])
                if data is not None and offset == len(data) and child.stdin is not None:
                    child.stdin.close()
                    child.stdin = None
                if ready:
                    chunk = os.read(
                        child.stdout.fileno(), min(65536, NETWORK_BOUND + 1 - len(output))
                    )
                    if not chunk:
                        ended = True
                    output += chunk
                    if len(output) > NETWORK_BOUND:
                        raise ValueError("original network command output exceeds its bound")
            if child.returncode != 0 or not exit_checked:
                raise ValueError("original network command refused")
            retained.close_known_terminal()
            known_terminal = True
            self._tool_records.append(
                {
                    "name": name,
                    "arguments": arguments,
                    "root": self.inventory.identity,
                    "inventory": record_digest(self.inventory.inventory),
                    "observed_images": digest(
                        json.dumps(retained.snapshots, sort_keys=True).encode()
                    ),
                    "mapping_stops": len(retained.snapshots),
                    "positive_wait_status": child.returncode,
                }
            )
            return bytes(output)
        finally:
            if not known_terminal:
                if retained is not None and retained.pidfd >= 0:
                    sender = getattr(signal, "pidfd_send_signal", None)
                    if sender is not None:
                        sender(retained.pidfd, 9, None, 0)
                else:
                    child.kill()
            child.stdout.close()

    def _install_table(self, lane: LaneNetworkPlan | None) -> None:
        objects = nft_table(self.plan, lane)
        payload = json.dumps(
            {
                "nftables": [
                    {"create" if index == 0 else "add": item} for index, item in enumerate(objects)
                ]
            },
            separators=(",", ":"),
        ).encode()
        self._command("nft", ["-j", "-f", "-"], data=payload)

    def _create_child(self) -> bytes:
        _setns(self.host_namespace)
        with open("/proc/sys/net/ipv4/ip_forward", "rb") as stream:
            if stream.read(8) != b"1\n":
                raise ValueError("preconfigured host forwarding is unavailable")
        addresses = json.loads(self._command("ip", ["-j", "-4", "address", "show"]))
        routes = json.loads(self._command("ip", ["-j", "-4", "route", "show", "table", "all"]))
        existing = []
        for item in addresses:
            for address in item.get("addr_info", []):
                existing.append(
                    ipaddress.IPv4Network(
                        f"{address['local']}/{address['prefixlen']}", strict=False
                    )
                )
        existing += [
            ipaddress.IPv4Network(item["dst"], strict=False)
            for item in routes
            if item.get("dst") not in (None, "default")
        ]
        if any(
            ipaddress.IPv4Network(lane.subnet).overlaps(network)
            for lane in self.plan.lanes
            for network in existing
        ):
            raise ValueError("original network subnet conflicts with host routes")
        self._install_table(None)
        libc = ctypes.CDLL(None, use_errno=True)
        for lane in self.plan.lanes:
            if libc.unshare(CLONE_NEWNET):
                raise OSError(ctypes.get_errno(), "private provider namespace creation refused")
            namespace = os.open("/proc/self/ns/net", os.O_RDONLY | os.O_CLOEXEC)
            self.transfer.transfer(lane.lane_id, namespace)
            self.namespaces[lane.lane_id] = namespace
            _setns(self.host_namespace)
            self._command(
                "ip",
                [
                    "link",
                    "add",
                    lane.host_interface,
                    "type",
                    "veth",
                    "peer",
                    "name",
                    lane.private_interface,
                ],
            )
            self._command(
                "ip",
                ["link", "set", lane.private_interface, "netns", f"/proc/self/fd/{namespace}"],
                inherited=(namespace,),
            )
            self._command(
                "ip", ["address", "add", lane.host_address + "/30", "dev", lane.host_interface]
            )
            self._command("ip", ["link", "set", lane.host_interface, "up"])
            _setns(namespace)
            self._install_table(lane)
            self._command(
                "ip",
                ["address", "add", lane.private_address + "/30", "dev", lane.private_interface],
            )
            self._command("ip", ["link", "set", lane.private_interface, "up"])
            self._command("ip", ["link", "set", "lo", "up"])
            self._command(
                "ip",
                [
                    "route",
                    "add",
                    "default",
                    "via",
                    lane.host_address,
                    "dev",
                    lane.private_interface,
                ],
            )
            _setns(self.host_namespace)
        return self._readback_child()

    def _readback_child(self) -> bytes:
        _setns(self.host_namespace)
        with open("/proc/sys/net/ipv4/ip_forward", "rb") as stream:
            if stream.read(8) != b"1\n":
                raise ValueError("original observed host forwarding changed")
        host_rules = canonical_nft(
            self._command("nft", ["-j", "list", "table", "inet", self.plan.host_table])
        )
        if host_rules != nft_table(self.plan, None):
            raise ValueError("actual original host provider nft rules differ")
        results: dict[str, object] = {"host_rules": host_rules}
        for lane in self.plan.lanes:
            _setns(self.host_namespace)
            host_links = json.loads(
                self._command("ip", ["-j", "-d", "link", "show", "dev", lane.host_interface])
            )
            host_addresses = json.loads(
                self._command("ip", ["-j", "-4", "address", "show", "dev", lane.host_interface])
            )
            if (
                len(host_links) != 1
                or host_links[0].get("linkinfo", {}).get("info_kind") != "veth"
                or "UP" not in host_links[0].get("flags", [])
            ):
                raise ValueError("actual original host veth identity differs")
            assigned_host = [
                (entry["local"], entry["prefixlen"])
                for item in host_addresses
                for entry in item.get("addr_info", [])
            ]
            if assigned_host != [(lane.host_address, 30)]:
                raise ValueError("actual original host veth address differs")
            _setns(self.namespaces[lane.lane_id])
            rules = canonical_nft(
                self._command("nft", ["-j", "list", "table", "inet", "crewshal_provider"])
            )
            if rules != nft_table(self.plan, lane):
                raise ValueError("actual original private provider nft rules differ")
            links = json.loads(self._command("ip", ["-j", "-d", "link", "show"]))
            routes = json.loads(self._command("ip", ["-j", "-4", "route", "show", "table", "all"]))
            addresses = json.loads(self._command("ip", ["-j", "-4", "address", "show"]))
            if {item["ifname"] for item in links} != {"lo", lane.private_interface} or not all(
                "UP" in item.get("flags", []) for item in links
            ):
                raise ValueError("actual original private provider interface inventory differs")
            peer = next(item for item in links if item["ifname"] == lane.private_interface)
            if (
                peer.get("linkinfo", {}).get("info_kind") != "veth"
                or peer.get("link_index") != host_links[0].get("ifindex")
                or host_links[0].get("link_index") != peer.get("ifindex")
            ):
                raise ValueError("actual original host and private veth peer identities differ")
            defaults = [item for item in routes if item.get("dst") == "default"]
            if (
                len(defaults) != 1
                or defaults[0].get("gateway") != lane.host_address
                or defaults[0].get("dev") != lane.private_interface
            ):
                raise ValueError("actual original provider default route differs")
            assigned = [
                (item["ifname"], entry["local"], entry["prefixlen"])
                for item in addresses
                for entry in item.get("addr_info", [])
            ]
            if sorted(assigned) != sorted(
                [("lo", "127.0.0.1", 8), (lane.private_interface, lane.private_address, 30)]
            ):
                raise ValueError("actual original provider address inventory differs")
            results[lane.lane_id] = {
                "rules": rules,
                "links": links,
                "routes": routes,
                "addresses": addresses,
                "host_links": host_links,
                "host_addresses": host_addresses,
            }
        _setns(self.host_namespace)
        raw = json.dumps(
            {"network": results, "tools": self._tool_records}, sort_keys=True, separators=(",", ":")
        ).encode()
        if len(raw) > NETWORK_BOUND:
            raise ValueError("original complete network readback exceeds its bound")
        return raw

    def _network_report(self, raw: bytes) -> bytes:
        if self.inventory is None or len(raw) > NETWORK_BOUND:
            raise ValueError("original bounded network and mapped-tool report required")
        report = json.loads(raw)
        if not isinstance(report, dict) or set(report) != {"network", "tools"}:
            raise ValueError("original complete network report framing differs")
        records = report["tools"]
        if not isinstance(records, list) or not 19 <= len(records) <= 128:
            raise ValueError("original complete mapped network tool readback missing")
        for record in records:
            if (
                not isinstance(record, dict)
                or set(record)
                != {
                    "name",
                    "arguments",
                    "root",
                    "inventory",
                    "observed_images",
                    "mapping_stops",
                    "positive_wait_status",
                }
                or record["name"] not in ("ip", "nft")
                or record["root"] != list(self.inventory.identity)
                or record["inventory"] != record_digest(self.inventory.inventory)
                or record["mapping_stops"] != 3
                or record["positive_wait_status"] != 0
                or re.fullmatch(r"[0-9a-f]{64}", str(record["observed_images"])) is None
                or not isinstance(record["arguments"], list)
                or len(record["arguments"]) > 16
                or any(
                    not isinstance(value, str) or "\x00" in value for value in record["arguments"]
                )
            ):
                raise ValueError("original mapped network tool evidence differs")
        # The original bounded child generated these records after actual kernel
        # checks. Parsed records cannot authorize a tool launch or namespace use.
        self.tool_readbacks.append(records)
        if len(json.dumps(self.tool_readbacks).encode()) > NETWORK_BOUND:
            raise ValueError("retained network tool evidence exceeds its original control bound")
        return json.dumps(report["network"], sort_keys=True, separators=(",", ":")).encode()

    def readback(self) -> None:
        try:
            self.verify_custody()
            if self._snapshots is None:
                raise ValueError("original provider network installation is incomplete")
            raw = self.readback_jobs.run(
                self._readback_child,
                {
                    self.host_namespace,
                    self.ip_binary,
                    self.nft_binary,
                    *self.namespaces.values(),
                    self.inventory.descriptor if self.inventory is not None else -1,
                    self.production_namespace,
                },
            )
            if self._network_report(raw) != self._snapshots:
                raise ValueError("actual original provider network readback changed")
            self.verify_custody()
        except BaseException as error:
            self._refuse(error)
