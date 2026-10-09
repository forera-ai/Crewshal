"""Fresh copied-root bytes; no parent program, loader or host setup is executed."""

from contextlib import contextmanager
import os
from pathlib import Path
import stat
import tempfile
import unittest
from unittest.mock import patch

from crewshal import linux_inventory as inventory
from crewshal import linux_setup as setup
from crewshal.contracts import record_digest
from crewshal.dispatch import prepare_dispatch_configuration
from crewshal.linux_bootstrap import bootstrap_policy, prepare_linux_bootstrap
from crewshal.linux_envelope import LinuxEnvelopeBindings
from crewshal.model import digest
from tests.acceptance import test_phase_2d_envelope as envelope_fixtures


class Phase2DInventory(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.root.chmod(0o755)
        self.raw = {
            "/bin/trusted-parent": b"synthetic parent bytes",
            "/bin/crewshal-bootstrap": b"synthetic helper bytes",
            "/bin/setpriv": b"synthetic privilege tool bytes",
            "/usr/bin/env": b"synthetic environment tool bytes",
            "/lib/libc.so": b"synthetic library bytes",
        }
        entries = {"/": inventory.RootEntry(kind="directory", mode=0o755)}
        for name, raw in self.raw.items():
            path = self.root / name.lstrip("/")
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(raw)
            path.chmod(0o555)
            entries[name] = inventory.RootEntry(kind="file", mode=0o555, sha256=digest(raw))
            for parent in Path(name).parents:
                entries[str(parent)] = inventory.RootEntry(kind="directory", mode=0o755)
        self.spec = inventory.TrustedParentInventory(
            root=entries,
            parent_argv=["/bin/trusted-parent"],
            entry_path="/bin/trusted-parent",
            helper_libraries={
                name: digest(self.raw[name]) for name in ("/bin/crewshal-bootstrap", "/lib/libc.so")
            },
        )
        envelope = envelope_fixtures.Phase2DEnvelope()
        envelope.setUp()
        self.addCleanup(envelope.doCleanups)
        self.f = envelope
        self.policy = bootstrap_policy(digest(self.raw["/bin/crewshal-bootstrap"]))
        self.configuration = self.compile()
        self.bootstrap = prepare_linux_bootstrap(
            self.configuration, helper_binary=self.policy.helper_binary
        )

    def compile(self, **changes):
        values = dict(
            context=record_digest(self.f.selection),
            root_inventory_sha256=inventory.root_inventory_digest(self.spec),
            helper_library_inventory_sha256=inventory.helper_library_inventory_digest(self.spec),
            parent_inventory_sha256=record_digest(self.spec),
            bootstrap_policy_sha256=record_digest(self.policy),
        )
        values.update(changes)
        return prepare_dispatch_configuration(
            self.f.selection,
            task=self.f.task,
            binding=self.f.binding,
            linux_envelope=LinuxEnvelopeBindings(**values),
        )

    def retain(self):
        handle = os.open(self.root, os.O_RDONLY | os.O_DIRECTORY)
        try:
            retained = inventory.RetainedParentInventory(handle, self.spec)
        finally:
            os.close(handle)
        self.addCleanup(retained.close)
        return retained

    @contextmanager
    def synthetic_root_owner(self):
        # Only UID/GID kernel observations are synthetic. Enumeration, bytes,
        # links, modes and descriptor identities use real fresh temporary files.
        fstat, stat_call = os.fstat, os.stat

        def owned(info):
            values = list(info)
            values[4:6] = [0, 0]
            return os.stat_result(values)

        with (
            patch.object(inventory.os, "fstat", side_effect=lambda handle: owned(fstat(handle))),
            patch.object(
                inventory.os, "stat", side_effect=lambda *a, **k: owned(stat_call(*a, **k))
            ),
        ):
            yield

    def bind(self, **changes):
        values = dict(
            configuration=self.configuration,
            inventory=self.spec,
            parent_argv=self.spec.parent_argv,
            parent_executable=digest(self.raw["/bin/trusted-parent"]),
            helper_binary=self.policy.helper_binary,
        )
        values.update(changes)
        return inventory.bind_parent_inventory(**values)

    def test_bound_inventory_remains_passive_and_unqualified(self):
        with patch("subprocess.Popen", side_effect=AssertionError("no startup")):
            bound = self.bind()
            plan = setup.prepare_namespace_setup(
                self.configuration,
                self.bootstrap,
                self.spec.parent_argv,
                digest(self.raw["/bin/trusted-parent"]),
                parent_inventory=bound,
            )
        self.assertEqual(plan.parent_inventory, self.spec)
        self.assertFalse(plan.execution_allowed)
        self.assertFalse(bound.profile_qualified)

    def test_full_root_file_mode_and_bytes_readback(self):
        retained = self.retain()
        with self.synthetic_root_owner():
            retained.verify()

    def test_extra_file_refused(self):
        retained = self.retain()
        (self.root / "unlisted").write_bytes(b"unlisted source")
        with self.synthetic_root_owner(), self.assertRaisesRegex(ValueError, "contents differ"):
            retained.verify()

    def test_changed_entry_bytes_refused(self):
        retained = self.retain()
        (self.root / "bin/trusted-parent").chmod(0o755)
        (self.root / "bin/trusted-parent").write_bytes(b"changed parent bytes")
        (self.root / "bin/trusted-parent").chmod(0o555)
        with self.synthetic_root_owner(), self.assertRaisesRegex(ValueError, "contents differ"):
            retained.verify()

    def test_missing_library_refused(self):
        retained = self.retain()
        (self.root / "lib/libc.so").unlink()
        with self.synthetic_root_owner(), self.assertRaisesRegex(ValueError, "contents differ"):
            retained.verify()

    def test_mode_change_refused(self):
        retained = self.retain()
        (self.root / "bin/trusted-parent").chmod(0o777)
        with self.synthetic_root_owner(), self.assertRaisesRegex(ValueError, "contents differ"):
            retained.verify()

    def test_hardlink_refused(self):
        retained = self.retain()
        os.link(self.root / "lib/libc.so", self.root / "lib/alias")
        with self.synthetic_root_owner(), self.assertRaisesRegex(ValueError, "hardlinks"):
            retained.verify()

    def test_special_file_refused_without_blocking(self):
        retained = self.retain()
        os.mkfifo(self.root / "pipe")
        with self.synthetic_root_owner(), self.assertRaisesRegex(ValueError, "special files"):
            retained.verify()

    def test_kernel_task_root_must_match_retained_copied_root(self):
        retained = self.retain()
        proc = self.root.parent / (self.root.name + "-proc")
        proc.mkdir()
        self.addCleanup(lambda: proc.rmdir())
        (proc / "root").symlink_to(self.root)
        self.addCleanup(lambda: (proc / "root").unlink())
        handle = os.open(proc, os.O_RDONLY | os.O_DIRECTORY)
        self.addCleanup(os.close, handle)
        retained.verify_task_root(handle)
        (proc / "root").unlink()
        (proc / "root").symlink_to(proc)
        with self.assertRaisesRegex(ValueError, "task root differs"):
            retained.verify_task_root(handle)

    def test_digest_mismatch_refused_for_each_binding(self):
        for field in (
            "root_inventory_sha256",
            "helper_library_inventory_sha256",
            "parent_inventory_sha256",
        ):
            with self.subTest(field=field), self.assertRaisesRegex(ValueError, "binding differs"):
                self.bind(configuration=self.compile(**{field: digest(b"different binding")}))

    def test_parent_executable_and_helper_mismatch_refused(self):
        for field in ("parent_executable", "helper_binary"):
            with self.subTest(field=field), self.assertRaisesRegex(ValueError, "binding differs"):
                self.bind(**{field: digest(b"different binary")})

    def test_manifest_mutation_cannot_inherit_bindings(self):
        self.spec.root["/lib/libc.so"].sha256 = digest(b"new library")
        self.spec.helper_libraries["/lib/libc.so"] = digest(b"new library")
        with self.assertRaisesRegex(ValueError, "binding differs"):
            self.bind()

    def test_canonical_paths_and_real_parent_directories_required(self):
        for name in ("/../escape", "/bin//bad", "/missing/parent/entry"):
            spec = self.spec.model_copy(deep=True)
            spec.root[name] = inventory.RootEntry(kind="file", mode=0o555, sha256=digest(b"x"))
            with self.subTest(name=name), self.assertRaises(ValueError):
                inventory.audit_parent_inventory(spec)

    def test_symlink_escape_and_chain_refused(self):
        for target in ("../../outside", "/absent", "/lib/alias"):
            spec = self.spec.model_copy(deep=True)
            spec.root["/lib/alias"] = inventory.RootEntry(kind="symlink", mode=0o777, target=target)
            with self.subTest(target=target), self.assertRaises(ValueError):
                inventory.audit_parent_inventory(spec)

    def test_safe_inventory_symlink_readback(self):
        (self.root / "lib/alias").symlink_to("libc.so")
        self.spec.root["/lib/alias"] = inventory.RootEntry(
            kind="symlink",
            mode=stat.S_IMODE((self.root / "lib/alias").lstat().st_mode),
            target="libc.so",
        )
        retained = self.retain()
        with self.synthetic_root_owner():
            retained.verify()

    def test_python_parent_requires_isolated_exact_entry(self):
        spec = self.spec.model_copy(deep=True)
        spec.entry_kind = "python"
        spec.entry_path = "/bin/parent.py"
        spec.root[spec.entry_path] = inventory.RootEntry(
            kind="file", mode=0o444, sha256=digest(b"pass")
        )
        spec.parent_argv = ["/bin/trusted-parent", "-I", "-S", "-B", spec.entry_path]
        inventory.audit_parent_inventory(spec)
        for argv in (
            ["/bin/trusted-parent", spec.entry_path],
            ["/bin/trusted-parent", "-c", "import os"],
        ):
            spec.parent_argv = argv
            with self.subTest(argv=argv), self.assertRaises(ValueError):
                inventory.audit_parent_inventory(spec)

    def test_bound_inventory_cannot_be_omitted_or_closed_as_authority(self):
        with self.assertRaisesRegex(ValueError, "cannot be omitted"):
            setup.prepare_namespace_setup(
                self.configuration,
                self.bootstrap,
                self.spec.parent_argv,
                digest(self.raw["/bin/trusted-parent"]),
            )
        retained = self.retain()
        retained.close()
        with self.assertRaises(OSError):
            retained.verify()

    def test_inventory_limits_and_writable_mode_refused(self):
        spec = self.spec.model_copy(deep=True)
        spec.root["/bin/trusted-parent"].mode = 0o4755
        with self.assertRaisesRegex(ValueError, "special modes"):
            inventory.audit_parent_inventory(spec)
        spec.root = {}
        with self.assertRaisesRegex(ValueError, "count bound"):
            inventory.audit_parent_inventory(spec)

    def test_bound_setup_refuses_missing_retained_root_before_startup(self):
        plan = setup.prepare_namespace_setup(
            self.configuration,
            self.bootstrap,
            self.spec.parent_argv,
            digest(self.raw["/bin/trusted-parent"]),
            parent_inventory=self.spec,
        )
        with patch("subprocess.Popen", side_effect=AssertionError("no startup")) as startup:
            with self.assertRaisesRegex(ValueError, "retained trusted root inventory"):
                setup.create_namespace_setup(
                    None,
                    None,
                    None,
                    None,
                    None,
                    None,
                    self.configuration,
                    self.bootstrap,
                    plan,
                )
        startup.assert_not_called()

    def test_bound_setup_reads_actual_root_before_startup(self):
        retained = self.retain()
        plan = setup.prepare_namespace_setup(
            self.configuration,
            self.bootstrap,
            self.spec.parent_argv,
            digest(self.raw["/bin/trusted-parent"]),
            parent_inventory=self.spec,
        )
        (self.root / "unlisted").write_bytes(b"untrusted root addition")
        with (
            self.synthetic_root_owner(),
            patch("subprocess.Popen", side_effect=AssertionError("no startup")) as startup,
        ):
            with self.assertRaisesRegex(ValueError, "contents differ"):
                setup.create_namespace_setup(
                    None,
                    None,
                    None,
                    None,
                    None,
                    None,
                    self.configuration,
                    self.bootstrap,
                    plan,
                    inventory=retained,
                )
        startup.assert_not_called()
