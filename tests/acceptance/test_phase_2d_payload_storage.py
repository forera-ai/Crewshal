"""Test policy readback refusals with fresh files and a synthetic filesystem probe.

These tests do not load AppArmor or qualify Linux enforcement.
"""

import os
import struct
from dataclasses import replace
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

from crewshal import linux_payload_storage as storage
from crewshal.linux_production import OwnedBackingProduction
from crewshal.linux_inventory import RootEntry
from crewshal.contracts import record_digest


class Phase2DPayloadStorage(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        (self.root / "profiles").mkdir()
        (self.root / "revision").write_bytes(b"1\n")
        self.binary = b"independent synthetic compiled policy fixture"
        (self.root / "original-export").write_bytes(self.binary)
        self.roles = tuple((name, name + ".1") for name in storage.PROFILE_NAMES)
        for name, directory in self.roles:
            role = self.root / "profiles" / directory
            role.mkdir()
            (role / "name").write_text(name + "\n")
            (role / "mode").write_bytes(b"enforce\n")
            os.link(self.root / "original-export", role / "raw_data")
        self.namespace = os.open(self.root, os.O_RDONLY | os.O_DIRECTORY)
        self.addCleanup(os.close, self.namespace)
        self.synthetic_filesystem = patch.object(storage, "_require_apparmorfs")
        self.synthetic_filesystem.start()
        self.addCleanup(self.synthetic_filesystem.stop)

    def retain(self, **changes):
        arguments = dict(namespace=self.namespace, expected_binary=self.binary, roles=self.roles)
        arguments.update(changes)
        return storage.RetainedAppArmorExport.retain(**arguments)

    def role(self):
        return self.root / "profiles" / self.roles[0][1]

    def test_exact_export_checks_bytes_names_modes_and_original_revision(self):
        retained = self.retain()
        retained.check_policy()
        self.assertEqual(retained.namespace_revision, 1)
        self.assertEqual(len(retained.roles), 4)

    def test_matching_role_name_and_hash_cannot_replace_loaded_binary_bytes(self):
        retained = self.retain()
        (self.role() / "raw_sha256").write_text(storage.digest(self.binary))
        (self.role() / "raw_data").write_bytes(b"changed loaded policy")
        with self.assertRaisesRegex(ValueError, "binary policy differs"):
            retained.check_policy()

    def test_missing_raw_export_refuses_without_hash_fallback(self):
        (self.role() / "raw_data").unlink()
        (self.role() / "raw_sha256").write_text(storage.digest(self.binary))
        with self.assertRaises(FileNotFoundError):
            self.retain()

    def test_obsolete_open_export_cannot_hide_replaced_current_role(self):
        retained = self.retain()
        old = os.open(self.role() / "raw_data", os.O_RDONLY)
        self.addCleanup(os.close, old)
        self.role().rename(self.root / "retained-old-profile")
        self.role().mkdir()
        self.assertEqual(os.read(old, 256), self.binary)
        with self.assertRaisesRegex(ValueError, "role directory changed"):
            retained.check_policy()

    def test_revision_mutation_during_policy_readback_refuses(self):
        retained = self.retain()
        read = storage._read

        def changed(descriptor, path, limit, **kwargs):
            value = read(descriptor, path, limit, **kwargs)
            if path == "mode":
                (self.root / "revision").write_bytes(b"2\n")
            return value

        with patch.object(storage, "_read", changed):
            with self.assertRaisesRegex(ValueError, "changed during"):
                retained.check_policy()

    def test_retained_export_survives_open_denial_and_checks_current_target(self):
        retained = self.retain()
        opened = os.open

        def denied(path, *args, **kwargs):
            if str(path).endswith("raw_data"):
                raise PermissionError("policy view privilege is absent")
            return opened(path, *args, **kwargs)

        with patch.object(storage.os, "open", denied):
            inherited = storage.RetainedAppArmorExport.retain_inherited(
                self.namespace, self.binary, self.roles, retained.raw_export
            )
            inherited.check_policy()
        (self.role() / "raw_data").unlink()
        (self.role() / "raw_data").write_bytes(self.binary)
        with self.assertRaisesRegex(ValueError, "current AppArmor export target differs"):
            retained.check_policy()

    def test_malformed_revision_and_non_enforcing_roles_refuse(self):
        for raw in (b"", b"nan\n", b"1\n2\n", b"-1\n"):
            with self.subTest(raw=raw):
                (self.root / "revision").write_bytes(raw)
                with self.assertRaisesRegex(ValueError, "revision is malformed"):
                    self.retain()
        (self.root / "revision").write_bytes(b"1\n")
        (self.role() / "mode").write_bytes(b"complain\n")
        with self.assertRaisesRegex(ValueError, "not enforcing"):
            self.retain()

    def test_wrong_role_name_and_duplicate_role_refuse(self):
        (self.role() / "name").write_bytes(b"unconfined\n")
        with self.assertRaisesRegex(ValueError, "role name differs"):
            self.retain()
        with self.assertRaisesRegex(ValueError, "duplicate"):
            self.retain(roles=(self.roles[0], self.roles[0]))
        for directory in ("../outside", "/absolute", "a/b"):
            with self.subTest(directory=directory):
                with self.assertRaisesRegex(ValueError, "role directory required"):
                    self.retain(roles=((storage.PROFILE_NAMES[0], directory),))

    def test_oversized_binary_and_loaded_export_refuse(self):
        with self.assertRaisesRegex(ValueError, "bounded compiled"):
            self.retain(expected_binary=b"x" * (storage.POLICY_LIMIT + 1))
        (self.role() / "raw_data").write_bytes(b"x" * (storage.POLICY_LIMIT + 1))
        with self.assertRaisesRegex(ValueError, "exceeds its bound"):
            self.retain()

    def test_real_filesystem_probe_cannot_accept_fixture_directory(self):
        self.synthetic_filesystem.stop()
        with self.assertRaisesRegex(ValueError, "unavailable|filesystem type differs"):
            self.retain()

    def test_nonblocking_revision_read_does_not_wait_for_future_policy_load(self):
        sent = False

        def event_file(descriptor, length):
            nonlocal sent
            if sent:
                raise BlockingIOError(11, "no later policy revision")
            sent = True
            return b"1\n"

        with patch.object(storage.os, "read", event_file):
            self.assertEqual(storage.RetainedAppArmorExport._revision(self.namespace), 1)

    def test_exact_process_label_is_checked_against_current_policy(self):
        retained = self.retain()
        proc = self.root / "proc"
        (proc / "attr" / "apparmor").mkdir(parents=True)
        current = proc / "attr" / "apparmor" / "current"
        label = storage.PROFILE_NAMES[0]
        current.write_text(label + " (enforce)\n")
        descriptor = os.open(proc, os.O_RDONLY | os.O_DIRECTORY)
        self.addCleanup(os.close, descriptor)
        observed = retained.check_process(descriptor, label)
        self.assertEqual(observed.binary_sha256, storage.digest(self.binary))
        with self.assertRaisesRegex(ValueError, "retained AppArmor roles"):
            retained.check_process(descriptor, "unrelated-profile")
        current.write_bytes(b"unconfined\n")
        with self.assertRaisesRegex(ValueError, "label differs"):
            retained.check_process(descriptor, label)

    def test_proposal_exposes_missing_growth_and_compatibility_checks(self):
        with (
            patch("subprocess.Popen", side_effect=AssertionError("no process")),
            patch("subprocess.run", side_effect=AssertionError("no compiler or loader")),
            patch("socket.socket", side_effect=AssertionError("no network")),
        ):
            source, source_digest, unresolved = storage.proposed_policy()
        self.assertEqual(source_digest, storage.digest(source))
        self.assertIn(
            "trusted_native_and_bwrap_scaffold_logical_and_allocated_growth_bounds", unresolved
        )
        self.assertIn("all_zero_device_aliases_and_inherited_descriptor_exclusion", unresolved)


class Phase2DScaffoldKernel(unittest.TestCase):
    @staticmethod
    def btf(extension=8, inode=800):
        strings = b"\0slabobj_ext\0shmem_inode_info\0"
        types = struct.pack("<III", 1, 4 << 24, extension) + struct.pack("<III", 13, 4 << 24, inode)
        return (
            struct.pack("<HBBIIIII", 0xEB9F, 1, 0, 24, 0, len(types), len(types), len(strings))
            + types
            + strings
        )

    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        self.aggregate = self.root / "aggregate"
        self.proc = self.root / "proc"
        self.sysfs = self.root / "sys"
        self.cache = self.sysfs / "kernel/slab/shmem_inode_cache"
        for path in (
            self.aggregate,
            self.proc / "sys/kernel",
            self.cache,
            self.sysfs / "kernel/btf",
        ):
            path.mkdir(parents=True)
        for name, value in {
            "memory.max": "805306368",
            "memory.swap.max": "0",
            "pids.max": "128",
            "cgroup.type": "domain",
        }.items():
            (self.aggregate / name).write_text(value + "\n")
        (self.proc / "meminfo").write_bytes(b"MemTotal:       4194304 kB\nSwapTotal: 0 kB\n")
        (self.proc / "sys/kernel/osrelease").write_bytes(b"6.8.0-synthetic-fixture\n")
        (self.proc / "cmdline").write_bytes(b"quiet fixture\n")
        (self.cache / "object_size").write_bytes(b"800\n")
        (self.cache / "slab_size").write_bytes(b"808\n")
        (self.cache / "order").write_bytes(b"2\n")
        (self.cache / "total_objects").write_bytes(b"100 N0=100\n")
        (self.sysfs / "kernel/notes").write_bytes(b"synthetic build notes")
        (self.sysfs / "kernel/btf/vmlinux").write_bytes(self.btf())
        self.fds = tuple(
            os.open(path, os.O_RDONLY | os.O_DIRECTORY)
            for path in (self.aggregate, self.proc, self.sysfs, self.cache)
        )
        for descriptor in self.fds:
            self.addCleanup(os.close, descriptor)
        probe = patch.object(storage, "_require_filesystem")
        probe.start()
        self.addCleanup(probe.stop)
        page_size = patch.object(storage.os, "sysconf", return_value=4096)
        page_size.start()
        self.addCleanup(page_size.stop)

    def retain(self):
        return storage.RetainedScaffoldKernel.retain(*self.fds)

    def test_original_geometry_and_controller_readback_are_retained(self):
        retained = self.retain()
        observed = retained.check()
        self.assertEqual(observed.conditional_scaffold_logical_bytes, 154_155_372)
        self.assertEqual(observed.original_memory_max, 805_306_368)
        self.assertEqual(observed.original_task_max, 128)
        self.assertEqual(observed.kernel_btf_sha256, storage.digest(self.btf()))

    def test_changed_control_build_memory_or_inode_geometry_refuses(self):
        changes = (
            (self.aggregate / "memory.max", b"805306367\n"),
            (self.aggregate / "pids.max", b"129\n"),
            (self.sysfs / "kernel/notes", b"changed build"),
            (self.sysfs / "kernel/btf/vmlinux", b"changed BTF"),
            (self.proc / "meminfo", b"MemTotal: 4194305 kB\n"),
            (self.cache / "object_size", b"799\n"),
        )
        for path, value in changes:
            with self.subTest(path=path):
                original = path.read_bytes()
                retained = self.retain()
                path.write_bytes(value)
                with self.assertRaises(ValueError):
                    retained.check()
                path.write_bytes(original)

    def test_old_slab_slots_remain_charged_after_new_accounted_slabs_grow(self):
        retained = self.retain()
        (self.cache / "total_objects").write_bytes(b"200 N0=200\n")
        current = retained.check()
        self.assertEqual(current.original_legacy_inode_slots, 100)
        self.assertEqual(current.conditional_scaffold_logical_bytes, 154_155_372)

    def test_extension_allocation_failure_route_cannot_pass_geometry_gate(self):
        (self.cache / "object_size").write_bytes(b"760\n")
        (self.cache / "slab_size").write_bytes(b"768\n")
        (self.sysfs / "kernel/btf/vmlinux").write_bytes(self.btf(8, 760))
        observed = self.retain().check()
        self.assertEqual(observed.slab_extension_bytes, 8)
        self.assertEqual(observed.inode_slab_order, 2)
        (self.cache / "order").write_bytes(b"4\n")
        with self.assertRaisesRegex(ValueError, "embedded memory accounting"):
            self.retain()
        (self.cache / "order").write_bytes(b"2\n")
        (self.sysfs / "kernel/btf/vmlinux").write_bytes(self.btf(24, 760))
        with self.assertRaisesRegex(ValueError, "embedded memory accounting"):
            self.retain()

    def test_btf_bounds_and_initial_inode_slot_source_are_required(self):
        original = (self.sysfs / "kernel/btf/vmlinux").read_bytes()
        for raw in (b"", original[:24], original[:12] + b"\xff" * 12):
            with self.subTest(raw=raw):
                (self.sysfs / "kernel/btf/vmlinux").write_bytes(raw)
                with self.assertRaisesRegex(ValueError, "BTF"):
                    self.retain()
        (self.sysfs / "kernel/btf/vmlinux").write_bytes(original)
        (self.cache / "total_objects").write_bytes(b"unknown\n")
        with self.assertRaisesRegex(ValueError, "initial shmem inode slot count"):
            self.retain()

    def test_small_inode_missing_build_and_disabled_accounting_refuse(self):
        changes = (
            (self.cache / "object_size", b"587\n"),
            (self.cache / "slab_size", b"799\n"),
            (self.sysfs / "kernel/notes", b""),
            (self.sysfs / "kernel/btf/vmlinux", b""),
            (self.proc / "cmdline", b"cgroup.memory=nokmem\n"),
            (self.proc / "cmdline", b"cgroup_disable=memory\n"),
            (self.proc / "meminfo", b"MemTotal: 0 kB\n"),
        )
        for path, value in changes:
            with self.subTest(path=path, value=value):
                original = path.read_bytes()
                path.write_bytes(value)
                with self.assertRaises(ValueError):
                    self.retain()
                path.write_bytes(original)

    def test_different_cache_cannot_supply_a_large_object_size(self):
        other = self.root / "other-cache"
        other.mkdir()
        descriptor = os.open(other, os.O_RDONLY | os.O_DIRECTORY)
        self.addCleanup(os.close, descriptor)
        with self.assertRaisesRegex(ValueError, "inode cache identity differs"):
            storage.RetainedScaffoldKernel.retain(*self.fds[:3], descriptor)


class Phase2DFrozenAuditSource(unittest.TestCase):
    def matched_source(self):
        """Use real file bytes with explicit synthetic kernel and mount probes."""
        policy = Phase2DPayloadStorage()
        policy.setUp()
        self.addCleanup(policy.doCleanups)
        kernel = Phase2DScaffoldKernel()
        kernel.setUp()
        self.addCleanup(kernel.doCleanups)
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        root = Path(directory.name)
        files = {
            "/opt/crewshal/storage-audit/review.json": b"synthetic frozen source review",
            "/opt/crewshal/storage-audit/kernel-package.json": b"synthetic kernel package record",
            "/opt/crewshal/storage-audit/apparmor-parser-package.json": b"synthetic parser package record",
            "/opt/crewshal/storage-audit/policy.source": storage.PROPOSED_POLICY,
            "/opt/crewshal/storage-audit/policy.binary": policy.binary,
            "/usr/sbin/apparmor_parser": b"synthetic parser bytes",
            "/opt/codex/bin/codex": b"synthetic pinned native bytes",
            "/opt/codex/codex-resources/codex-linux-sandbox": b"synthetic pinned sandbox bytes",
            "/opt/codex/codex-resources/bwrap": b"synthetic pinned bubblewrap bytes",
            **{
                "/opt/crewshal/storage-audit/sources/" + name: name.encode()
                for name in storage.AUDIT_SOURCE_NAMES
            },
        }
        hashed = {name: storage.digest(value) for name, value in files.items()}
        audit = storage.StorageSourceAudit(
            review_record_sha256=hashed["/opt/crewshal/storage-audit/review.json"],
            policy_source_sha256=hashed["/opt/crewshal/storage-audit/policy.source"],
            policy_binary_sha256=storage.digest(policy.binary),
            policy_parser_executable_sha256=hashed["/usr/sbin/apparmor_parser"],
            policy_parser_package_record_sha256=hashed[
                "/opt/crewshal/storage-audit/apparmor-parser-package.json"
            ],
            native_executable_sha256=hashed["/opt/codex/bin/codex"],
            native_sandbox_sha256=hashed["/opt/codex/codex-resources/codex-linux-sandbox"],
            bubblewrap_executable_sha256=hashed["/opt/codex/codex-resources/bwrap"],
            kernel_package="linux-image-6.8.0-synthetic-fixture",
            kernel_package_record_sha256=hashed["/opt/crewshal/storage-audit/kernel-package.json"],
            kernel_release="6.8.0-synthetic-fixture",
            kernel_notes_sha256=storage.digest(b"synthetic build notes"),
            kernel_btf_sha256=storage.digest(kernel.btf()),
            source_files={
                name: hashed["/opt/crewshal/storage-audit/sources/" + name]
                for name in storage.AUDIT_SOURCE_NAMES
            },
        )
        files[storage.AUDIT_PATH] = audit.model_dump_json().encode()
        inventory = {}
        for path, raw in files.items():
            target = root / path.lstrip("/")
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(raw)
            target.chmod(0o444)
            inventory[path] = RootEntry(kind="file", mode=0o444, sha256=storage.digest(raw))
        descriptor = os.open(root, os.O_RDONLY | os.O_DIRECTORY)
        self.addCleanup(os.close, descriptor)
        owner = object.__new__(OwnedBackingProduction)
        owner.verify, owner.failed = Mock(), False
        owner.projected_inventory = SimpleNamespace(
            descriptor=descriptor, inventory=SimpleNamespace(root=inventory), verify=Mock()
        )
        aggregate = os.fstat(kernel.fds[0])
        owner.reservation = SimpleNamespace(
            aggregate=SimpleNamespace(
                descriptor=kernel.fds[0],
                identity=SimpleNamespace(device=aggregate.st_dev, inode=aggregate.st_ino),
            ),
            _configuration=SimpleNamespace(
                linux_envelope=SimpleNamespace(storage_policy_sha256=record_digest(audit))
            ),
            _production=owner,
            _retain_installation_refusal=Mock(),
        )
        actual_fstat, actual_stat = os.fstat, os.stat

        def root_owned(info):
            names = (
                "st_dev",
                "st_ino",
                "st_mode",
                "st_nlink",
                "st_size",
                "st_mtime_ns",
                "st_ctime_ns",
            )
            return SimpleNamespace(
                **{name: getattr(info, name) for name in names}, st_uid=0, st_gid=0
            )

        for probe in (
            patch.object(storage.os, "fstat", lambda fd: root_owned(actual_fstat(fd))),
            patch.object(storage.os, "stat", lambda *a, **k: root_owned(actual_stat(*a, **k))),
            patch.object(storage.os, "fstatvfs", return_value=SimpleNamespace(f_flag=os.ST_RDONLY)),
        ):
            probe.start()
            self.addCleanup(probe.stop)
        retained = owner.retain_payload_storage(
            policy.namespace, policy.binary, policy.roles, *kernel.fds[1:]
        )
        for value in retained.retained_sources.values():
            self.addCleanup(os.close, value)
        for value in retained.files.values():
            self.addCleanup(os.close, value.descriptor)
        return owner, retained, policy, kernel, root

    def test_matched_source_requires_current_policy_and_running_kernel_again(self):
        owner, retained, policy, kernel, _ = self.matched_source()
        observed = retained.check()
        self.assertEqual(observed.conditional_scaffold_logical_bytes, 154_155_372)
        self.assertFalse(owner.failed)
        (policy.role() / "raw_data").write_bytes(b"different loaded binary")
        with self.assertRaisesRegex(ValueError, "binary policy differs"):
            retained.check()
        self.assertTrue(retained.failed)
        self.assertTrue(owner.failed)

    def test_equal_policy_copy_cannot_replace_original_custody(self):
        owner, retained, _, _, _ = self.matched_source()
        retained.policy = replace(retained.policy)
        with self.assertRaisesRegex(ValueError, "custody differs"):
            retained.check()
        self.assertTrue(owner.failed)

    def test_vendor_alias_resolves_only_inside_the_original_root(self):
        source = "/opt/codex/codex-resources/codex-linux-sandbox"
        for alias in ("../bin/codex", "/opt/codex/bin/codex"):
            self.assertEqual(storage._vendor_target(source, alias), "/opt/codex/bin/codex")
        with self.assertRaisesRegex(ValueError, "escapes"):
            storage._vendor_target(source, "../../../../outside")

    def test_missing_original_manifest_retains_all_partial_custody_and_refuses_retry(self):
        with tempfile.TemporaryDirectory() as directory:
            descriptor = os.open(directory, os.O_RDONLY | os.O_DIRECTORY)
            self.addCleanup(os.close, descriptor)
            owner = object.__new__(OwnedBackingProduction)
            owner.reservation = SimpleNamespace(_retain_installation_refusal=Mock())
            owner.projected_inventory = SimpleNamespace(
                verify=Mock(), inventory=SimpleNamespace(root={}), descriptor=descriptor
            )
            owner.verify, owner.failed = Mock(), False
            with self.assertRaisesRegex(ValueError, "audit manifest missing"):
                owner.retain_payload_storage(
                    descriptor, b"synthetic compiled policy", (), descriptor, descriptor, descriptor
                )
            retained = owner._payload_storage
            self.assertTrue(owner.failed)
            self.assertTrue(retained.failed)
            self.assertEqual(
                set(retained.retained_sources), {"apparmor", "proc", "sysfs", "inode-cache"}
            )
            for value in retained.retained_sources.values():
                self.addCleanup(os.close, value)
                self.assertEqual(os.fstat(value).st_ino, os.fstat(descriptor).st_ino)
            owner.reservation._retain_installation_refusal.assert_called_once()
            with self.assertRaisesRegex(ValueError, "already consumed"):
                owner.retain_payload_storage(
                    descriptor, b"synthetic compiled policy", (), descriptor, descriptor, descriptor
                )

    def test_constructor_and_positive_caller_flags_cannot_supply_readback(self):
        with self.assertRaisesRegex(ValueError, "original producer"):
            storage.RetainedPayloadStorage()
        with self.assertRaisesRegex(ValueError, "producer.*differs"):
            storage.RetainedPayloadStorage.retain(
                SimpleNamespace(ready=True), 3, b"caller ready", (), 4, 5, 6
            )
        raw = {
            "review_record_sha256": "a" * 64,
            "policy_source_sha256": "b" * 64,
            "policy_binary_sha256": "c" * 64,
            "policy_parser_executable_sha256": "a" * 64,
            "policy_parser_package_record_sha256": "b" * 64,
            "native_executable_sha256": "d" * 64,
            "native_sandbox_sha256": "e" * 64,
            "bubblewrap_executable_sha256": "f" * 64,
            "kernel_package": "linux-image-6.8.0-synthetic",
            "kernel_package_record_sha256": "a" * 64,
            "kernel_release": "6.8.0-synthetic",
            "kernel_notes_sha256": "b" * 64,
            "kernel_btf_sha256": "c" * 64,
            "source_files": {},
        }
        storage.StorageSourceAudit.model_validate(raw)
        for change in ({"ready": True}, {"review_profile": True}, {"native_release": "other"}):
            with self.subTest(change=change):
                with self.assertRaises(ValueError):
                    storage.StorageSourceAudit.model_validate({**raw, **change})
