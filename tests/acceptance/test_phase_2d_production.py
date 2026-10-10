"""Fresh synthetic custody seams; no fork, namespace, key, mount or device call."""

from array import array
from contextlib import ExitStack, contextmanager
import errno
import copy
import ctypes
import os
from pathlib import Path
import socket
import stat
import tempfile
import time
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

from crewshal import linux_production as production
from crewshal import linux_storage as storage
from crewshal import linux_inventory as inventory
from crewshal.model import digest
from tests.acceptance import test_phase_2d_inventory as inventory_fixtures


class Phase2DProduction(unittest.TestCase):
    def setUp(self):
        self.stack = ExitStack()
        self.addCleanup(self.stack.close)
        self.stack.enter_context(
            patch.object(production.os, "fork", side_effect=AssertionError("real fork forbidden"))
        )
        # Linux-only atomic flag is a synthetic seam on this macOS runner.
        self.stack.enter_context(patch.object(socket, "MSG_CMSG_CLOEXEC", 0x40000000, create=True))
        self.owner = SimpleNamespace(
            deadline=time.monotonic() + 20,
            received=[],
            handles={},
            verify=Mock(),
            _verify_transferred=Mock(),
        )
        self.channel = production._CreationChannel(self.owner)
        self.channel.expected = ["namespace"]
        self.channel.parent = Mock()
        self.channel.child = Mock()
        self.channel.parent.send.return_value = 1
        self.channel.child.sendmsg.return_value = len("namespace")
        self.channel.child.recv.return_value = b"1"
        self.stack.enter_context(
            patch.object(production.select, "select", side_effect=lambda r, w, e, t: (r, w, []))
        )

    def private_keys(self):
        # Fresh explicit kernel/credential seams, never a real keyctl/add_key.
        ring = object.__new__(storage.AnonymousKeyring)
        ring.serial, ring.creator, ring.previous = 333, os.getpid(), 0
        ring.complete, ring.claimed = True, False
        reservation = SimpleNamespace(verify=Mock(), _private_ring=ring)
        self.stack.enter_context(patch.object(production, "_key_state", return_value="present"))
        keys = production.PrivateEcryptfsKeys(reservation, ring)
        self.events = []
        self.secret_buffer = None

        def add(kind, description, payload, size, serial):
            self.assertIs(reservation._ecryptfs_keys, keys)
            self.assertIs(reservation._private_ring, ring)
            self.assertFalse(keys.complete)
            self.assertEqual(serial, 333)
            self.events.append(("add", kind))
            if kind == "user":
                self.secret_buffer = payload
                self.assertEqual(size, 32)
                self.assertEqual(len(payload.raw), 32)
                return 444
            self.assertEqual(
                payload.raw[:size], f"new ecryptfs user:{keys.master_description} 64".encode()
            )
            return 555

        def keyctl(operation, serial=0, buffer=None, size=0):
            self.events.append(("keyctl", operation, serial))
            if operation == 5:
                self.assertEqual(buffer.value, 0x003F0000)
                return 0
            if operation == 11:
                buffer.raw = array("i", [444, 555]).tobytes()
                return 8
            self.fail("unexpected key operation")

        self.add_key = self.stack.enter_context(
            patch.object(production, "_add_private_key", side_effect=add)
        )
        self.keyctl = self.stack.enter_context(
            patch.object(production, "_keyctl", side_effect=keyctl)
        )
        self.description = self.stack.enter_context(
            patch.object(production, "_private_key_description")
        )
        return keys, reservation

    def test_private_keys_pin_before_effects_and_exclude_possessor_rights(self):
        keys, reservation = self.private_keys()
        keys.create()
        self.assertEqual(
            self.events,
            [
                ("add", "user"),
                ("keyctl", 5, 444),
                ("add", "encrypted"),
                ("keyctl", 5, 555),
                ("keyctl", 11, 333),
            ],
        )
        self.assertEqual(self.description.call_count, 2)
        self.assertIs(reservation._ecryptfs_keys, keys)
        self.assertTrue(keys.complete)
        self.assertFalse(keys.operational_ready)
        self.assertFalse(keys.resources_reusable)
        self.assertEqual(self.secret_buffer.raw, bytes(32))
        with self.assertRaisesRegex(ValueError, "one-shot"):
            keys.create()
        with self.assertRaises(TypeError):
            copy.copy(keys)

    def test_unknown_key_add_keeps_ring_and_partial_owner_without_retry(self):
        keys, reservation = self.private_keys()
        self.add_key.side_effect = OSError(12, "synthetic key add refused")
        with self.assertRaises(OSError):
            keys.create()
        self.assertIs(reservation._ecryptfs_keys, keys)
        self.assertIs(reservation._private_ring, keys.ring)
        self.assertTrue(keys.failed)
        self.assertFalse(keys.complete)
        self.assertEqual(keys.serials, {})
        self.keyctl.assert_not_called()
        with self.assertRaisesRegex(ValueError, "one-shot"):
            keys.create()

    def test_permission_refusal_retains_master_and_never_creates_auth_key(self):
        keys, reservation = self.private_keys()
        self.keyctl.side_effect = OSError(1, "synthetic permission refusal")
        with self.assertRaises(OSError):
            keys.create()
        self.assertEqual(keys.serials, {"master": 444})
        self.assertIs(reservation._ecryptfs_keys, keys)
        self.add_key.assert_called_once()
        self.assertEqual(self.secret_buffer.raw, bytes(32))

    def test_ring_membership_cannot_be_asserted_by_successful_add_status(self):
        keys, _ = self.private_keys()
        original = self.keyctl.side_effect

        def changed_membership(operation, serial=0, buffer=None, size=0):
            if operation == 11:
                buffer.raw = array("i", [444, 777]).tobytes()
                return 8
            return original(operation, serial, buffer, size)

        self.keyctl.side_effect = changed_membership
        with self.assertRaisesRegex(ValueError, "membership differs"):
            keys.create()
        self.assertFalse(keys.complete)
        self.assertEqual(keys.serials, {"master": 444, "auth": 555})

    def test_reconstructed_credential_anchor_refuses_before_key_creation(self):
        keys, reservation = self.private_keys()
        reservation._private_ring = object()
        with self.assertRaisesRegex(ValueError, "ownership differs"):
            keys.create()
        self.add_key.assert_not_called()

    def test_unknown_ring_refuses_without_key_creation(self):
        keys, _ = self.private_keys()
        with (
            patch.object(production, "_key_state", return_value="unknown"),
            self.assertRaises(ValueError),
        ):
            keys.create()
        self.add_key.assert_not_called()

    def test_changed_description_refuses_before_key_creation(self):
        keys, _ = self.private_keys()
        keys.signature = "a" * 16
        with self.assertRaises(ValueError):
            keys.create()
        self.add_key.assert_not_called()

    def test_private_key_readback_requires_exact_root_permissions_and_terminator(self):
        raw = b"encrypted;0;0;003f0000;0123456789abcdef\0"
        for value in (raw, raw[:-1], raw.replace(b"003f0000", b"3f030000")):

            def describe(operation, serial, buffer, size):
                ctypes.memmove(buffer, value, len(value))
                return len(value)

            with patch.object(production, "_keyctl", side_effect=describe):
                if value == raw:
                    production._private_key_description(555, "encrypted", "0123456789abcdef")
                else:
                    with self.assertRaises(ValueError):
                        production._private_key_description(555, "encrypted", "0123456789abcdef")

    @contextmanager
    def copied_root_fixture(self):
        fixture = inventory_fixtures.Phase2DInventory()
        fixture.setUp()
        self.addCleanup(fixture.doCleanups)
        output = fixture.root.parent / (fixture.root.name + "-copied")
        output.mkdir(mode=0o700)
        import shutil

        self.addCleanup(shutil.rmtree, output)
        descriptors = {
            name: os.open(fixture.root / name.lstrip("/"), os.O_RDONLY) for name in fixture.raw
        }
        destination = os.open(output, os.O_RDONLY | os.O_DIRECTORY)
        for descriptor in [*descriptors.values(), destination]:
            self.addCleanup(os.close, descriptor)
        fstat, stat_call = os.fstat, os.stat

        def owned(info):
            return SimpleNamespace(
                **{
                    **{name: getattr(info, name) for name in dir(info) if name.startswith("st_")},
                    "st_uid": 0,
                    "st_gid": 0,
                }
            )

        with (
            patch.object(production.os, "fstat", side_effect=lambda fd: owned(fstat(fd))),
            patch.object(
                production.os, "stat", side_effect=lambda *a, **k: owned(stat_call(*a, **k))
            ),
            # Linux allocation geometry is synthetic; actual output bytes,
            # inode identities and allocated-file-block readback remain real.
            patch.object(
                production.os, "fstatvfs", return_value=SimpleNamespace(f_frsize=4096, f_bsize=4096)
            ),
        ):
            yield fixture, output, destination, descriptors

    def test_root_copy_uses_exclusive_files_and_independent_inventory_readback(self):
        with self.copied_root_fixture() as (fixture, output, destination, descriptors):
            production._copy_root_files(destination, fixture.spec, descriptors)
            retained = inventory.RetainedParentInventory(destination, fixture.spec)
            self.addCleanup(retained.close)
            retained.verify()
            for path, raw in fixture.raw.items():
                self.assertEqual((output / path.lstrip("/")).read_bytes(), raw)
            with self.assertRaises(FileExistsError):
                production._copy_root_files(destination, fixture.spec, descriptors)

    def test_root_copy_missing_input_never_creates_output_file(self):
        with self.copied_root_fixture() as (fixture, output, destination, descriptors):
            inputs = dict(descriptors)
            inputs.pop("/lib/libc.so")
            with self.assertRaisesRegex(ValueError, "exact root file"):
                production._copy_root_files(destination, fixture.spec, inputs)
            self.assertEqual(list(output.iterdir()), [])

    def test_root_copy_bad_input_hash_keeps_partial_bytes_and_source_fd(self):
        with self.copied_root_fixture() as (fixture, output, destination, descriptors):
            spec = fixture.spec.model_copy(deep=True)
            spec.root["/bin/trusted-parent"].sha256 = digest(b"wrong expected bytes")
            with self.assertRaisesRegex(ValueError, "bytes/identity changed"):
                production._copy_root_files(destination, spec, descriptors)
            self.assertTrue((output / "bin/trusted-parent").exists())
            os.fstat(descriptors["/bin/trusted-parent"])

    def test_root_copy_sparse_oversize_input_refuses_before_creation(self):
        with self.copied_root_fixture() as (fixture, output, destination, descriptors):
            path = fixture.root / "bin/trusted-parent"
            path.chmod(0o755)
            with path.open("r+b") as stream:
                stream.truncate(1073741824)
            path.chmod(0o555)
            with self.assertRaisesRegex(ValueError, "original logical/allocated"):
                production._copy_root_files(destination, fixture.spec, descriptors)
            self.assertEqual(list(output.iterdir()), [])

    def test_root_copy_wrong_allocation_geometry_refuses_before_creation(self):
        with self.copied_root_fixture() as (fixture, output, destination, descriptors):
            with patch.object(
                production.os, "fstatvfs", return_value=SimpleNamespace(f_frsize=8192, f_bsize=8192)
            ):
                with self.assertRaisesRegex(ValueError, "allocation geometry"):
                    production._copy_root_files(destination, fixture.spec, descriptors)
            self.assertEqual(list(output.iterdir()), [])

    def test_root_copy_source_mutation_during_read_keeps_output_and_refuses(self):
        with self.copied_root_fixture() as (fixture, output, destination, descriptors):
            source = descriptors["/bin/trusted-parent"]
            original = os.pread
            mutated = False

            def reading(fd, count, offset):
                nonlocal mutated
                chunk = original(fd, count, offset)
                if fd == source and not mutated:
                    mutated = True
                    path = fixture.root / "bin/trusted-parent"
                    path.chmod(0o755)
                    path.write_bytes(b"changed while copying")
                    path.chmod(0o555)
                return chunk

            with patch.object(production.os, "pread", side_effect=reading):
                with self.assertRaisesRegex(ValueError, "bytes/identity changed"):
                    production._copy_root_files(destination, fixture.spec, descriptors)
            self.assertTrue((output / "bin/trusted-parent").exists())

    def test_child_root_custody_precedes_first_copy_effect(self):
        with tempfile.TemporaryDirectory() as directory:
            parent = os.open(directory, os.O_RDONLY | os.O_DIRECTORY)
            self.addCleanup(os.close, parent)
            value = object.__new__(production.OwnedBackingProduction)
            value.handles = {"root-parent": parent, "namespace": 999}
            value._root_manifest, value._root_inputs = object(), {}
            value._root_channel = SimpleNamespace(transfer=Mock())

            def copy(destination, manifest, sources):
                value._root_channel.transfer.assert_called_once_with("readonly-root", destination)
                os.fstat(destination)

            with (
                patch.object(production, "_enter_owned_namespace"),
                patch.object(production, "_copy_root_files", side_effect=copy),
            ):
                self.assertEqual(value._copy_root_child(), b"root-copied")
            descriptor = value._root_channel.transfer.call_args.args[1]
            os.close(descriptor)

    def test_root_bind_custody_precedes_readonly_remount(self):
        value = object.__new__(production.OwnedBackingProduction)
        value.root = "/synthetic/owned"
        value.handles = {"namespace": 99, "readonly-root": 98}
        events = []
        value._root_mount_channel = SimpleNamespace(
            transfer=lambda name, descriptor: events.append(("pin", name, descriptor))
        )
        info = SimpleNamespace(st_dev=1, st_ino=2)
        with (
            patch.object(production, "_enter_owned_namespace"),
            patch.object(
                production,
                "_readonly_bind",
                side_effect=lambda path, *, remount: events.append(("mount", remount)),
            ),
            patch.object(production.os, "stat", return_value=info),
            patch.object(production.os, "fstat", return_value=info),
            patch.object(production.os, "open", return_value=97),
        ):
            self.assertEqual(value._readonly_root_child(), b"root-projected")
        self.assertEqual(
            events, [("mount", False), ("pin", "readonly-projection", 97), ("mount", True)]
        )

    def readonly_projection(self, flags):
        with self.copied_root_fixture() as (fixture, _, destination, descriptors):
            production._copy_root_files(destination, fixture.spec, descriptors)
            value = object.__new__(production.OwnedBackingProduction)
            value.failed = False
            value.verify = Mock()
            value._root_manifest = fixture.spec
            value.handles = {"namespace": 999, "readonly-root": destination}
            value.root_inventory = inventory.RetainedParentInventory(destination, fixture.spec)
            self.addCleanup(value.root_inventory.close)
            channel = SimpleNamespace(open=Mock(), child=Mock(), position=0)
            channel.child.fileno.return_value = 101

            def run(action, keep, *, transfer):
                self.assertIs(transfer, channel)
                descriptor = os.dup(destination)
                self.addCleanup(os.close, descriptor)
                value.handles["readonly-projection"] = descriptor
                channel.position = 1
                return b"root-projected"

            value.jobs = SimpleNamespace(run=run)
            with (
                patch.object(production, "_CreationChannel", return_value=channel),
                patch.object(production.os, "fstatvfs", return_value=SimpleNamespace(f_flag=flags)),
            ):
                try:
                    value.project_readonly_root()
                except production.ProductionRefusal as error:
                    self.assertIs(error.production, value)
                    self.assertFalse(error.resources_reusable)
                    self.assertTrue(value.failed)
                    os.fstat(value.handles["readonly-projection"])
                    raise
            self.addCleanup(value.projected_inventory.close)
            self.assertFalse(value.operational_ready)
            self.assertFalse(value.resources_reusable)
            with self.assertRaisesRegex(ValueError, "no retry"):
                value.project_readonly_root()

    def test_exact_retained_readonly_projection_is_independently_observed(self):
        self.readonly_projection(os.ST_RDONLY)

    def test_successful_mount_transport_cannot_assert_readonly_projection(self):
        with self.assertRaisesRegex(production.ProductionRefusal, "remains writable"):
            self.readonly_projection(0)

    @contextmanager
    def formatter_fixture(self, *, valid=True, wrong_size=False, wrong_hash=False, elf=True):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            executable = root / "usr/sbin/mkfs.ext4"
            executable.parent.mkdir(parents=True)
            raw = (b"\x7fELF" if elf else b"TEXT") + b"synthetic fixture, never executable"
            executable.write_bytes(raw)
            descriptor = os.open(root, os.O_RDONLY | os.O_DIRECTORY)
            self.addCleanup(os.close, descriptor)
            value = object.__new__(production.OwnedBackingProduction)
            value.failed = False
            value.verify = Mock()
            value.projected_inventory = SimpleNamespace(descriptor=descriptor, verify=Mock())
            value._root_manifest = SimpleNamespace(
                root={
                    "/usr/sbin/mkfs.ext4": inventory.RootEntry(
                        kind="file",
                        mode=0o555,
                        sha256=digest(b"wrong bytes") if wrong_hash else digest(raw),
                    )
                }
            )
            value.handles = {}
            for name, size in production.BACKING_SIZES.items():
                path = root / name
                fd = os.open(path, os.O_RDWR | os.O_CREAT | os.O_EXCL, 0o600)
                self.addCleanup(os.close, fd)
                os.ftruncate(fd, size)
                block = bytearray(1024)
                if valid:
                    block[56:58] = b"\x53\xef"
                block[4:8] = (size // 4096 + int(wrong_size)).to_bytes(4, "little")
                block[24:28] = (2).to_bytes(4, "little")
                os.pwrite(fd, block, 1024)
                value.handles[name] = fd
                value.handles["loop:" + name] = fd  # Explicit loop/kernel seam.
            value.jobs = SimpleNamespace(run=Mock(return_value=b"synthetic formatter exit"))
            with patch.object(
                production.os, "execve", side_effect=AssertionError("real exec forbidden")
            ):
                try:
                    yield value
                finally:
                    if "formatter" in value.handles:
                        os.close(value.handles["formatter"])

    def test_formatter_transport_requires_actual_owned_superblock_and_exact_size(self):
        with self.formatter_fixture() as value:
            value.format_filesystems()
            self.assertEqual(set(value._ext4_metadata), set(production.BACKING_SIZES))
            self.assertEqual(value.jobs.run.call_count, 2)
            for call in value.jobs.run.call_args_list:
                self.assertTrue(call.kwargs["_format_output"])
            self.assertFalse(value.operational_ready)
            self.assertFalse(value.resources_reusable)
            with self.assertRaisesRegex(ValueError, "no retry"):
                value.format_filesystems()

    def test_formatter_exit_cannot_supply_missing_ext4_superblock(self):
        with self.formatter_fixture(valid=False) as value:
            with self.assertRaisesRegex(production.ProductionRefusal, "superblock unavailable"):
                value.format_filesystems()
            self.assertTrue(value.failed)
            os.fstat(value.handles["formatter"])
            self.assertEqual(value.jobs.run.call_count, 1)

    def test_formatter_declared_geometry_cannot_exceed_owned_image(self):
        with self.formatter_fixture(wrong_size=True) as value:
            with self.assertRaisesRegex(production.ProductionRefusal, "declared size differs"):
                value.format_filesystems()
            self.assertTrue(value.failed)
            self.assertEqual(value.jobs.run.call_count, 1)

    def test_formatter_wrong_bytes_refuse_before_any_job(self):
        with self.formatter_fixture(wrong_hash=True) as value:
            with self.assertRaisesRegex(production.ProductionRefusal, "bytes/identity differ"):
                value.format_filesystems()
            value.jobs.run.assert_not_called()
            os.fstat(value.handles["formatter"])

    def test_formatter_script_refuses_before_any_job(self):
        with self.formatter_fixture(elf=False) as value:
            with self.assertRaisesRegex(production.ProductionRefusal, "ELF ext4 formatter"):
                value.format_filesystems()
            value.jobs.run.assert_not_called()

    def test_formatter_child_execs_fd_and_only_preserves_stdio_owned_loop(self):
        value = object.__new__(production.OwnedBackingProduction)
        value._format_name = "scratch.img"
        value.handles = {"loop:scratch.img": 7, "scratch.img": 8, "formatter": 9}
        expected = bytes(production.LOOP_INFO64.size)
        value._expected_loop = Mock(return_value=expected)
        info = SimpleNamespace(st_dev=1, st_ino=2)
        with (
            patch.object(production.os, "fstat", return_value=info),
            patch.object(production.fcntl, "ioctl"),
            patch.object(production.fcntl, "fcntl", side_effect=[11, 12]),
            patch.object(production.os, "dup2") as normalize,
            patch.object(
                production.os,
                "listdir",
                return_value=["0", "1", "2", "3", "7", "8", "9", "11", "12"],
            ),
            patch.object(production.os, "close") as close,
            patch.object(
                production.os, "execve", side_effect=RuntimeError("synthetic exec boundary")
            ) as execute,
        ):
            with self.assertRaisesRegex(RuntimeError, "synthetic exec boundary"):
                value._format_child()
        normalize.assert_called_once_with(11, 3)
        self.assertEqual([call.args[0] for call in close.call_args_list], [7, 8, 9, 11])
        execute.assert_called_once_with(
            12,
            ["/usr/sbin/mkfs.ext4", "-q", "-F", "-m", "0", "/proc/self/fd/3"],
            {"MKE2FS_CONFIG": "/dev/null"},
        )

    def test_encrypted_mount_child_retains_each_filesystem_before_role_mutation(self):
        value = object.__new__(production.OwnedBackingProduction)
        value.root = "/synthetic/owned"
        value.handles = {
            "namespace": 99,
            "root-parent": 98,
            "loop:scratch.img": 7,
            "scratch.img": 8,
            "loop:candidate.img": 9,
            "candidate.img": 10,
        }
        value._keys = SimpleNamespace(signature="0123456789abcdef")
        value.mounts = {
            role + suffix: "/synthetic/owned/" + role + suffix
            for role in ("scratch", "candidate")
            for suffix in ("-lower", "-upper")
        }
        expected = bytes(production.LOOP_INFO64.size)
        value._expected_loop = Mock(return_value=expected)
        events = []
        value._mount_channel = SimpleNamespace(
            transfer=lambda name, fd: events.append(("pin", name, fd))
        )
        with (
            patch.object(production, "_enter_owned_namespace"),
            patch.object(production.fcntl, "ioctl"),
            patch.object(production.os, "fstat", return_value=SimpleNamespace()),
            patch.object(production.os, "mkdir"),
            patch.object(production.os, "open", side_effect=[11, 12, 13, 14]),
            patch.object(
                production,
                "_mount_owned",
                side_effect=lambda source, target, fs, opts: events.append(("mount", fs, opts)),
            ),
            patch.object(production.os, "chown"),
            patch.object(
                production.os,
                "fchown",
                side_effect=lambda fd, uid, gid: events.append(("role", fd, uid, gid)),
            ),
            patch.object(production.os, "fchmod"),
        ):
            self.assertEqual(value._mount_views_child(), b"encrypted-views-mounted")
        self.assertEqual(
            [event[0] for event in events], ["mount", "pin", "mount", "pin", "role"] * 2
        )
        self.assertEqual(
            [event[1] for event in events if event[0] == "pin"],
            [
                "mounted:scratch-lower",
                "mounted:scratch-upper",
                "mounted:candidate-lower",
                "mounted:candidate-upper",
            ],
        )
        for event in events:
            if event[:2] == ("mount", "ecryptfs"):
                self.assertIn("ecryptfs_mount_auth_tok_only", event[2])
                self.assertIn("ecryptfs_sig=0123456789abcdef", event[2])

    def test_bad_owned_loop_prevents_any_mount_effect(self):
        value = object.__new__(production.OwnedBackingProduction)
        value.mounts = {"scratch-lower": "/synthetic/lower", "scratch-upper": "/synthetic/upper"}
        value.handles = {
            "namespace": 99,
            "root-parent": 98,
            "loop:scratch.img": 7,
            "scratch.img": 8,
        }
        value._keys = SimpleNamespace(signature="0123456789abcdef")
        value._expected_loop = Mock(return_value=b"rebound loop")
        with (
            patch.object(production, "_enter_owned_namespace"),
            patch.object(production.fcntl, "ioctl"),
            patch.object(production.os, "fstat", return_value=SimpleNamespace()),
            patch.object(production, "_mount_owned") as mounting,
            patch.object(production.os, "mkdir") as mkdir,
        ):
            with self.assertRaisesRegex(ValueError, "changed before mount"):
                value._mount_views_child()
        mounting.assert_not_called()
        mkdir.assert_not_called()

    def test_mount_custody_refusal_never_chowns_or_attempts_upper_mount(self):
        value = object.__new__(production.OwnedBackingProduction)
        value.root = "/synthetic"
        value.handles = {
            "namespace": 99,
            "root-parent": 98,
            "loop:scratch.img": 7,
            "scratch.img": 8,
        }
        value._keys = SimpleNamespace(signature="0123456789abcdef")
        value.mounts = {"scratch-lower": "/synthetic/lower", "scratch-upper": "/synthetic/upper"}
        value._expected_loop = Mock(return_value=bytes(production.LOOP_INFO64.size))
        value._mount_channel = SimpleNamespace(
            transfer=Mock(side_effect=ValueError("synthetic custody refusal"))
        )
        with (
            patch.object(production, "_enter_owned_namespace"),
            patch.object(production.fcntl, "ioctl"),
            patch.object(production.os, "fstat", return_value=SimpleNamespace()),
            patch.object(production.os, "mkdir"),
            patch.object(production.os, "open", return_value=11),
            patch.object(production, "_mount_owned") as mounting,
            patch.object(production.os, "fchown") as role,
        ):
            with self.assertRaisesRegex(ValueError, "custody refusal"):
                value._mount_views_child()
        mounting.assert_called_once()
        role.assert_not_called()

    def test_handoff_retains_original_creation_deadline_and_separate_bounded_readback(self):
        value = object.__new__(production.OwnedBackingProduction)
        value.failed = False
        value.verify = Mock()
        value._keys = SimpleNamespace(_verify=Mock(), ring=object())
        value._mount_channel = SimpleNamespace(position=4)
        value._ext4_metadata = {name: b"synthetic" for name in production.BACKING_SIZES}
        value.mounts = {
            role + suffix: "/synthetic/" + role + suffix
            for role in ("scratch", "candidate")
            for suffix in ("-lower", "-upper")
        }
        value.handles = {
            "namespace": 3,
            "directory": 4,
            "scratch.img": 5,
            "loop:scratch.img": 6,
            "candidate.img": 7,
            "loop:candidate.img": 8,
        }
        reservation = SimpleNamespace(
            observer=object(),
            observer_group=object(),
            aggregate=object(),
            batch_started=time.monotonic() - 2,
            _configuration=object(),
        )
        value.reservation = reservation
        value.jobs = object()
        captured = {}

        def construct(actual, **arguments):
            captured.update(arguments)

        with (
            patch.object(
                storage.LinuxPhysicalOwner, "__init__", autospec=True, side_effect=construct
            ),
            patch.object(storage.LinuxPhysicalOwner, "verify_retention", autospec=True) as verify,
        ):
            owner = value.handoff_storage_owner()
        self.assertIs(captured["jobs"], value.jobs)
        readback = captured["retention_readback_jobs"]
        self.assertIs(readback, value._readback_jobs)
        self.assertIs(readback.observer, reservation.observer)
        self.assertIs(readback.group, reservation.observer_group)
        self.assertIs(readback.aggregate, reservation.aggregate)
        self.assertEqual(readback.deadline, reservation.batch_started + 600)
        verify.assert_called_once_with(owner, reservation)

    def test_incomplete_mount_custody_cannot_handoff_owner(self):
        value = object.__new__(production.OwnedBackingProduction)
        value.failed = False
        value._mount_channel = SimpleNamespace(position=3)
        value.mounts = {name: "/synthetic" for name in range(4)}
        with (
            patch.object(storage.LinuxPhysicalOwner, "__init__") as owner,
            self.assertRaisesRegex(ValueError, "completed view custody"),
        ):
            value.handoff_storage_owner()
        owner.assert_not_called()

    def test_auxiliary_images_retain_original_namespace_and_charge_existing_allowances(self):
        value = object.__new__(production.OwnedBackingProduction)
        value.failed = False
        value.complete = True
        value.verify = Mock()
        value.handles = {"namespace": 9, "directory": 8, "loop-control": 7}
        value._expected_loop = Mock(return_value=bytes(4))
        channel = SimpleNamespace(open=Mock(), child=SimpleNamespace(fileno=lambda: 6), position=6)

        def run(action, handles, **options):
            if action.__name__ == "_create_auxiliary_child":
                self.assertEqual(handles, {9, 8, 7, 6})
                self.assertIs(options["transfer"], channel)
                for index, name in enumerate(production.ALL_BACKING_SIZES):
                    value.handles[name] = index + 20
                    value.handles["loop:" + name] = index + 30
                return b"auxiliary-backings-created"
            self.assertEqual(action.__name__, "_readback")
            return bytes(4 * 5)

        value.jobs = SimpleNamespace(run=Mock(side_effect=run))
        with (
            patch.object(production, "_CreationChannel", return_value=channel),
            patch.object(production.os, "fstat", return_value=SimpleNamespace()),
        ):
            value.create_auxiliary_backings()
        self.assertTrue(value._auxiliary_complete)
        self.assertEqual(len(channel.expected), 6)
        self.assertEqual(
            production.ROOT_COPY_BYTES + production.ADDITIONAL_BACKING_SIZES["native-auth.img"],
            1073741824,
        )
        self.assertEqual(production.ADDITIONAL_BACKING_SIZES["validator-scratch.img"], 33554432)
        self.assertEqual(production.ADDITIONAL_BACKING_SIZES["validator-candidate.img"], 16777216)
        self.assertFalse(value.operational_ready)
        with self.assertRaisesRegex(ValueError, "no retry"):
            value.create_auxiliary_backings()

    def test_auxiliary_success_text_without_complete_custody_retains_and_refuses(self):
        value = object.__new__(production.OwnedBackingProduction)
        value.failed = False
        value.complete = True
        value.verify = Mock()
        value.handles = {"namespace": 9, "directory": 8, "loop-control": 7}
        channel = SimpleNamespace(open=Mock(), child=SimpleNamespace(fileno=lambda: 6), position=5)
        value.jobs = SimpleNamespace(run=Mock(return_value=b"auxiliary-backings-created"))
        with patch.object(production, "_CreationChannel", return_value=channel):
            with self.assertRaisesRegex(
                production.ProductionRefusal, "custody incomplete"
            ) as error:
                value.create_auxiliary_backings()
        self.assertIs(error.exception.production, value)
        self.assertIs(value._auxiliary_channel, channel)
        self.assertTrue(value.failed)
        self.assertEqual(value.jobs.run.call_count, 1)
        self.assertFalse(value.resources_reusable)

    def test_private_auth_mount_allows_managed_helper_exec_only_in_fixed_auth_view(self):
        mount = Mock(return_value=0)
        with patch.object(production.ctypes, "CDLL", return_value=SimpleNamespace(mount=mount)):
            production._mount_owned(
                "/synthetic/lower", "/synthetic/auth", "ecryptfs", "sig", native_auth=True
            )
            production._mount_owned("/synthetic/lower", "/synthetic/candidate", "ecryptfs", "sig")
        self.assertEqual(mount.call_args_list[0].args[3].value, 2 | 4)
        self.assertEqual(mount.call_args_list[1].args[3].value, 2 | 4 | 8)

    def test_auxiliary_mount_child_pins_auth_and_validator_views_before_uid_change(self):
        value = object.__new__(production.OwnedBackingProduction)
        value.root = "/synthetic/owned"
        value.handles = {"namespace": 99, "root-parent": 98}
        for index, name in enumerate(production.ADDITIONAL_BACKING_SIZES):
            value.handles[name] = index + 10
            value.handles["loop:" + name] = index + 20
        value.mounts = {
            role + suffix: production._view_path(value.root, role, suffix)
            for role in ("native-auth", "validator-scratch", "validator-candidate")
            for suffix in ("-lower", "-upper")
        }
        value._keys = SimpleNamespace(signature="0123456789abcdef")
        value._expected_loop = Mock(return_value=bytes(production.LOOP_INFO64.size))
        events = []
        value._mount_channel = SimpleNamespace(
            transfer=lambda name, fd: events.append(("pin", name, fd))
        )
        with (
            patch.object(production, "_enter_owned_namespace"),
            patch.object(production.fcntl, "ioctl"),
            patch.object(production.os, "fstat", return_value=SimpleNamespace()),
            patch.object(production.os, "mkdir"),
            patch.object(production.os, "open", side_effect=range(40, 46)),
            patch.object(production, "_mount_owned") as mount,
            patch.object(
                production.os,
                "fchown",
                side_effect=lambda fd, uid, gid: events.append(("owner", fd, uid)),
            ),
            patch.object(production.os, "fchmod"),
        ):
            value._mount_views_child()
        self.assertEqual([event[2] for event in events if event[0] == "owner"], [65534, 65531, 0])
        self.assertEqual([event[0] for event in events], ["pin", "pin", "owner"] * 3)
        self.assertTrue(mount.call_args_list[1].kwargs["native_auth"])
        self.assertEqual(mount.call_args_list[1].args[1], value.root + "/native-auth")
        self.assertEqual(mount.call_args_list[5].args[1], value.root + "/validator-candidate")

    def test_auxiliary_backing_cannot_be_created_after_formatter_started(self):
        value = object.__new__(production.OwnedBackingProduction)
        value._format_attempted = True
        value.failed = False
        value.complete = True
        with patch.object(production, "_CreationChannel") as channel:
            with self.assertRaisesRegex(ValueError, "before format"):
                value.create_auxiliary_backings()
        channel.assert_not_called()

    def test_auxiliary_mount_targets_exist_in_original_owned_directory(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        value = object.__new__(production.OwnedBackingProduction)
        value.root = temporary.name
        parent = os.open(value.root, os.O_RDONLY | os.O_DIRECTORY)
        self.addCleanup(os.close, parent)
        value.handles = {"namespace": 9999, "root-parent": parent}
        roles = ("native-auth", "validator-scratch", "validator-candidate")
        for index, name in enumerate(production.ADDITIONAL_BACKING_SIZES):
            value.handles[name] = 10000 + index
            value.handles["loop:" + name] = 20000 + index
        value.mounts = {
            role + suffix: production._view_path(value.root, role, suffix)
            for role in roles
            for suffix in ("-lower", "-upper")
        }
        value._keys = SimpleNamespace(signature="0123456789abcdef")
        value._expected_loop = Mock(return_value=bytes(production.LOOP_INFO64.size))
        value._mount_channel = SimpleNamespace(
            transfer=lambda name, fd: self.addCleanup(os.close, fd)
        )
        original_stat = os.fstat

        def mount(source, target, filesystem, options, **kwargs):
            self.assertTrue(Path(target).is_dir(), f"mount target absent: {target}")

        with (
            patch.object(production, "_enter_owned_namespace"),
            patch.object(production.fcntl, "ioctl"),
            patch.object(
                production.os,
                "fstat",
                side_effect=lambda fd: SimpleNamespace() if fd >= 10000 else original_stat(fd),
            ),
            patch.object(production, "_mount_owned", side_effect=mount),
            patch.object(production.os, "fchown"),
        ):
            value._mount_views_child()
        self.assertFalse((Path(value.root) / "native-auth-upper").exists())
        self.assertFalse((Path(value.root) / "validator-candidate-upper").exists())

    def message(self, name=b"namespace", descriptors=(91,), flags=0):
        ancillary = [(socket.SOL_SOCKET, socket.SCM_RIGHTS, array("i", descriptors).tobytes())]
        self.channel.parent.recvmsg.return_value = (name, ancillary, flags, None)

    def test_actual_descriptor_pinned_before_independent_readback_and_ack(self):
        self.message()
        stages = []

        def verify(name, descriptor):
            self.assertEqual(self.owner.received, [91])
            self.assertEqual(self.owner.handles, {"namespace": 91})
            self.channel.parent.send.assert_not_called()
            stages.append("readback")

        self.owner._verify_transferred.side_effect = verify
        self.owner.verify.side_effect = lambda: stages.append("ownership")
        self.channel.parent.send.side_effect = lambda data: stages.append("ack") or 1
        self.channel.pump()
        self.assertEqual(stages, ["readback", "ownership", "ack"])
        self.assertEqual(self.channel.position, 1)

    def test_bad_order_retains_all_received_handles_without_ack_or_close(self):
        self.message(name=b"loop:scratch.img", descriptors=(91, 92))
        with patch.object(production.os, "close") as close, self.assertRaises(ValueError):
            self.channel.pump()
        self.assertEqual(self.owner.received, [91, 92])
        self.channel.parent.send.assert_not_called()
        close.assert_not_called()

    def test_truncated_message_keeps_unknown_descriptors_and_refuses(self):
        self.message(flags=socket.MSG_CTRUNC)
        with self.assertRaises(ValueError):
            self.channel.pump()
        self.assertEqual(self.owner.received, [91])
        self.channel.parent.send.assert_not_called()

    def test_metadata_refusal_keeps_handle_and_never_acknowledges(self):
        self.message()
        self.owner._verify_transferred.side_effect = ValueError("synthetic metadata refusal")
        with self.assertRaises(ValueError):
            self.channel.pump()
        self.assertEqual(self.owner.handles, {"namespace": 91})
        self.channel.parent.send.assert_not_called()

    def test_replayed_stage_refuses_without_overwriting_original_handle(self):
        self.message()
        self.channel.pump()
        self.message(descriptors=(92,))
        with self.assertRaises(ValueError):
            self.channel.pump()
        self.assertEqual(self.owner.received, [91, 92])
        self.assertEqual(self.owner.handles, {"namespace": 91})

    def test_missing_actual_fd_cannot_be_replaced_by_text(self):
        self.message(name=b"namespace:91", descriptors=())
        with self.assertRaises(ValueError):
            self.channel.pump()
        self.assertEqual(self.owner.handles, {})

    def test_child_requires_exact_parent_ack_before_next_effect(self):
        self.channel.child.recv.return_value = b"0"
        with self.assertRaisesRegex(ValueError, "acknowledgement refused"):
            self.channel.transfer("namespace", 91)
        self.channel.child.sendmsg.assert_called_once()

    def test_expired_origin_prevents_transfer(self):
        self.owner.deadline = time.monotonic() - 1
        with self.assertRaises(ValueError):
            self.channel.transfer("namespace", 91)
        self.channel.child.sendmsg.assert_not_called()

    def test_missing_atomic_received_fd_flag_refuses_without_receive(self):
        with patch.object(socket, "MSG_CMSG_CLOEXEC", None), self.assertRaises(ValueError):
            self.channel.pump()
        self.channel.parent.recvmsg.assert_not_called()

    def partial(self):
        value = object.__new__(production.OwnedBackingProduction)
        value.root = "/synthetic/owned"
        value.handles = {"directory": 99}
        value.directory_identity = (1, 2)
        value.channel = SimpleNamespace(transfer=Mock())
        return value

    def test_child_transfers_backing_and_loop_before_mutation(self):
        value = self.partial()
        events = []
        value.channel.transfer.side_effect = lambda name, fd: events.append(("pin", name))
        opens = iter([11, 12, 13, 14, 15, 16])
        info = SimpleNamespace(
            st_mode=stat.S_IFBLK | 0o600, st_rdev=os.makedev(7, 3), st_dev=1, st_ino=2
        )

        def ioctl(fd, operation, *args):
            events.append(("ioctl", operation))
            return 3 if operation == production.LOOP_CTL_GET_FREE else 0

        with (
            patch.object(
                production, "_unshare_mount_namespace", side_effect=lambda: events.append("unshare")
            ),
            patch.object(
                production, "_namespace_is_private", side_effect=lambda: events.append("private")
            ),
            patch.object(production.os, "open", side_effect=lambda *a, **k: next(opens)),
            patch.object(production.os, "fstat", return_value=info),
            patch.object(
                production.os,
                "ftruncate",
                side_effect=lambda fd, size: events.append(("truncate", size)),
            ),
            patch.object(production.fcntl, "ioctl", side_effect=ioctl),
        ):
            self.assertEqual(value._create_child(), b"partial-objects-created")
        self.assertLess(events.index(("pin", "namespace")), events.index("private"))
        self.assertLess(events.index(("pin", "scratch.img")), events.index(("truncate", 33554432)))
        self.assertLess(
            events.index(("pin", "loop:scratch.img")),
            events.index(("ioctl", production.LOOP_SET_FD)),
        )
        self.assertEqual(events.count(("ioctl", production.LOOP_SET_FD)), 2)

    def test_busy_loop_has_no_retry_or_cleanup(self):
        value = self.partial()
        info = SimpleNamespace(st_mode=stat.S_IFBLK | 0o600, st_rdev=os.makedev(7, 3))
        calls = []

        def ioctl(fd, operation, *args):
            calls.append(operation)
            if operation == production.LOOP_CTL_GET_FREE:
                return 3
            raise OSError(errno.EBUSY, "synthetic attached/rundown loop")

        with (
            patch.object(production, "_unshare_mount_namespace"),
            patch.object(production, "_namespace_is_private"),
            patch.object(production.os, "open", return_value=11),
            patch.object(production.os, "fstat", return_value=info),
            patch.object(production.os, "ftruncate"),
            patch.object(production.fcntl, "ioctl", side_effect=ioctl),
            self.assertRaises(OSError),
        ):
            value._create_child()
        self.assertEqual(calls, [production.LOOP_CTL_GET_FREE, production.LOOP_SET_FD])
        self.assertFalse(value.resources_reusable)
        self.assertFalse(value.operational_ready)

    def test_observer_loop_slot_check_uses_no_ioctl_or_release_inference(self):
        value = self.partial()
        with (
            patch.object(
                production.os,
                "fstat",
                return_value=SimpleNamespace(st_mode=stat.S_IFBLK, st_rdev=os.makedev(7, 3)),
            ),
            patch.object(production.fcntl, "fcntl", return_value=production.fcntl.FD_CLOEXEC),
            patch.object(
                production.fcntl, "ioctl", side_effect=AssertionError("observer ioctl forbidden")
            ),
        ):
            value._verify_transferred("loop:scratch.img", 91)

    def test_constructor_refusal_pins_original_reservation_before_any_duplication(self):
        reservation = SimpleNamespace(
            _configuration=object(),
            verify=Mock(side_effect=ValueError("synthetic claim refusal")),
        )
        jobs = SimpleNamespace(deadline=time.monotonic() + 20)
        with (
            patch.object(
                production,
                "prepare_linux_envelope",
                return_value=SimpleNamespace(owned_root="/synthetic/owned"),
            ),
            patch.object(production.os, "dup") as duplicate,
            self.assertRaises(production.ProductionRefusal) as caught,
        ):
            production.OwnedBackingProduction(reservation, 99, jobs)
        self.assertIs(reservation._production, caught.exception.production)
        self.assertTrue(caught.exception.production.failed)
        duplicate.assert_not_called()
        with self.assertRaisesRegex(ValueError, "one-shot"):
            production.OwnedBackingProduction(reservation, 99, jobs)

    def creation_transport(self, *, mismatch=False):
        value = self.partial()
        value.attempted = value.failed = value.complete = False
        value.verify = Mock()
        value.channel = SimpleNamespace(child=Mock(), expected=[], position=0)
        value.channel.child.fileno.return_value = 71
        value.handles.update(
            {
                "scratch.img": 11,
                "loop:scratch.img": 12,
                "candidate.img": 13,
                "loop:candidate.img": 14,
            }
        )
        calls = []

        def run(action, keep, **options):
            self.assertFalse(value.complete)
            calls.append(action.__name__)
            if action.__name__ == "_create_child":
                self.assertIs(options["transfer"], value.channel)
                self.assertIn(71, keep)
                value.channel.position = len(value.channel.expected)
                return b"partial-objects-created"
            self.assertEqual(keep, set(value.handles.values()))
            return b"unknown" if mismatch else b"observed-loop" * 2

        value.jobs = SimpleNamespace(run=run)
        with (
            patch.object(
                production.os,
                "fstat",
                side_effect=lambda fd: SimpleNamespace(
                    st_size=33554432 if fd == 11 else 16777216, st_blocks=1
                ),
            ),
            patch.object(value, "_expected_loop", return_value=b"observed-loop"),
            patch.object(
                production.fcntl, "ioctl", side_effect=AssertionError("observer ioctl forbidden")
            ),
        ):
            if mismatch:
                with self.assertRaises(production.ProductionRefusal):
                    value.create()
            else:
                value.create()
        return value, calls

    def test_loop_readback_is_separate_bounded_job_and_not_operational_readiness(self):
        value, calls = self.creation_transport()
        self.assertEqual(calls, ["_create_child", "_readback"])
        self.assertTrue(value.complete)
        self.assertFalse(value.operational_ready)
        self.assertFalse(value.resources_reusable)
        with self.assertRaisesRegex(ValueError, "one-shot"):
            value.create()

    def test_readback_mismatch_retains_all_handles_and_refuses_retry(self):
        value, calls = self.creation_transport(mismatch=True)
        self.assertEqual(calls, ["_create_child", "_readback"])
        self.assertFalse(value.complete)
        self.assertTrue(value.failed)
        self.assertEqual(len(value.handles), 5)
        with self.assertRaisesRegex(ValueError, "one-shot"):
            value.create()


class Phase2DCreationChild(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.descriptor = os.open(self.temporary.name, os.O_RDONLY)
        self.addCleanup(os.close, self.descriptor)
        self.observer = SimpleNamespace(spec=SimpleNamespace(boot_id="synthetic"))
        self.group = SimpleNamespace(identity=SimpleNamespace(relative_path="owned/observer"))
        self.jobs = storage.BoundedStorageJobs(
            self.observer, self.group, object(), time.monotonic() + 20
        )
        info = os.fstat(self.descriptor)
        self.jobs.pending = (999, 123)
        self.jobs._creation_child = (999, 123, self.descriptor, 42, info.st_dev, info.st_ino)
        self.jobs._active_deadline = self.jobs.deadline
        self.stat = (999, "S", os.getpid(), 42)
        self.status = f"Pid:\t999\nTgid:\t999\nPPid:\t{os.getpid()}\nTracerPid:\t0\nThreads:\t1\nNoNewPrivs:\t1\nUid:\t0 0 0 0\nGid:\t0 0 0 0\n".encode()
        self.cgroup = b"0::/owned/observer\n"
        self.stack = ExitStack()
        self.addCleanup(self.stack.close)
        self.stack.enter_context(
            patch.object(storage, "_proc_root", side_effect=lambda boot: os.dup(self.descriptor))
        )
        self.stack.enter_context(
            patch.object(storage, "_stat_identity", side_effect=lambda raw: self.stat)
        )
        self.stack.enter_context(patch.object(storage, "_read", side_effect=self.read))
        self.stack.enter_context(patch.object(storage.select, "select", return_value=([], [], [])))

    def read(self, descriptor, name):
        if name.startswith("self/fdinfo/"):
            return b"Pid:\t999\n"
        return {"stat": b"synthetic", "status": self.status, "cgroup": self.cgroup}[name]

    def test_exact_retained_pidfd_proc_start_parent_and_group_required(self):
        self.assertEqual(self.jobs.verify_creation_child(), 999)
        for stat_value in (
            (999, "S", os.getpid() + 1, 42),
            (999, "S", os.getpid(), 43),
            (999, "Z", os.getpid(), 42),
        ):
            self.stat = stat_value
            with self.subTest(stat=stat_value), self.assertRaises(ValueError):
                self.jobs.verify_creation_child()

    def test_same_pid_text_without_retained_proc_binding_refuses(self):
        self.jobs._creation_child = None
        with self.assertRaises(ValueError):
            self.jobs.verify_creation_child()

    def test_rebound_pidfd_or_added_thread_or_migrated_child_refuses(self):
        self.jobs.pending = (999, 124)
        with self.assertRaises(ValueError):
            self.jobs.verify_creation_child()
        self.jobs.pending = (999, 123)
        self.status = self.status.replace(b"Threads:\t1", b"Threads:\t2")
        with self.assertRaises(ValueError):
            self.jobs.verify_creation_child()
        self.status = self.status.replace(b"Threads:\t2", b"Threads:\t1")
        self.cgroup = b"0::/other/observer\n"
        with self.assertRaises(ValueError):
            self.jobs.verify_creation_child()

    def test_failed_or_expired_child_cannot_authorize_transfer(self):
        self.jobs.failed = True
        with self.assertRaises(ValueError):
            self.jobs.verify_creation_child()
        self.jobs.failed = False
        self.jobs.deadline = time.monotonic() - 1
        with self.assertRaises(ValueError):
            self.jobs.verify_creation_child()


if __name__ == "__main__":
    unittest.main()
