"""Fresh FDs prove build derivation rules without compiler or policy execution."""

import os
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

from crewshal.contracts import record_digest
from crewshal.linux_bootstrap import prepare_linux_bootstrap
from crewshal.linux_inventory import RootEntry
from crewshal.linux_operational import (
    FrozenBuildFilesystem,
    FrozenHelperBuild,
    FrozenPolicyBuild,
)
from crewshal.linux_payload_storage import PROPOSED_POLICY, StorageSourceAudit
from crewshal.model import digest
from tests.acceptance import test_phase_2d_charged_build as fixtures


class BootstrapBuildClosure(unittest.TestCase):
    def setUp(self):
        self.f = fixtures.Phase2DChargedBuild()
        self.f.setUp()
        self.addCleanup(self.f.doCleanups)
        self.audit = StorageSourceAudit(
            review_record_sha256="1" * 64,
            policy_source_sha256=digest(PROPOSED_POLICY),
            policy_binary_sha256="2" * 64,
            policy_parser_executable_sha256="3" * 64,
            policy_parser_package_record_sha256="4" * 64,
            native_executable_sha256="5" * 64,
            native_sandbox_sha256="6" * 64,
            bubblewrap_executable_sha256="7" * 64,
            kernel_package="linux-image-synthetic",
            kernel_package_record_sha256="8" * 64,
            kernel_release="synthetic",
            kernel_notes_sha256="9" * 64,
            kernel_btf_sha256="a" * 64,
            source_files={"synthetic": "b" * 64},
        )
        self.policy = FrozenPolicyBuild(
            parser="/prepared/apparmor_parser",
            parser_sha256="3" * 64,
            source="/prepared/policy.source",
            source_sha256=digest(PROPOSED_POLICY),
            argv=[
                "/prepared/apparmor_parser",
                "--skip-kernel-load",
                "--stdout",
                "--skip-cache",
                "--skip-read-cache",
                "--config-file=/dev/null",
                "--base=/prepared/includes",
                "--jobs=1",
                "--max-jobs=1",
                "--zstd-compress-level=none",
                "--kernel-features=/prepared/includes/kernel.features",
                "--override-policy-abi=/prepared/includes/abi/4.0",
            ],
            environment={},
            files={"/prepared/apparmor_parser": "3" * 64},
            include_files={
                "/prepared/includes/abi/4.0": "c" * 64,
                "/prepared/includes/kernel.features": "e" * 64,
            },
            audit_template=self.audit,
        )
        base = self.f.initial.helper_build
        self.build = FrozenHelperBuild.model_validate(
            {
                **base.model_dump(),
                "policy_build": self.policy,
                "argv": [
                    base.compiler,
                    "-pipe",
                    "-static",
                    "-s",
                    "-O2",
                    "-std=c11",
                    "-Wall",
                    "-Wextra",
                    "-Werror",
                    "-nostdinc",
                    "-x",
                    "c",
                    "-o",
                    "@original-helper-output",
                    "-",
                ],
                "environment": {"TMPDIR": base.volume},
                "header_files": {"/prepared/includes/header.h": "d" * 64},
                "runtime_files": {base.compiler: base.compiler_sha256},
                "filesystem": FrozenBuildFilesystem(
                    volume_device=1,
                    volume_inode=2,
                    backing_device=3,
                    backing_inode=4,
                    loop_device=5,
                    loop_inode=6,
                    loop_rdev=7,
                    geometry_sha256="e" * 64,
                    inodes=128,
                ),
            }
        )

    def full_derivation(self):
        f = self.f
        spec = f.fixture.spec.model_copy(deep=True)
        for path, sha in {
            "/opt/crewshal/storage-audit.json": digest(self.audit.model_dump_json().encode()),
            "/opt/crewshal/storage-audit/policy.binary": self.audit.policy_binary_sha256,
            "/opt/crewshal/storage-audit/policy.source": self.policy.source_sha256,
            "/usr/sbin/apparmor_parser": self.policy.parser_sha256,
        }.items():
            spec.root[path] = RootEntry(kind="file", mode=0o444, sha256=sha)
            for parent in Path(path).parents:
                spec.root[str(parent)] = RootEntry(kind="directory", mode=0o755)
        f.fixture.spec = spec
        config = f.fixture.compile(
            build_recipe_sha256=record_digest(self.build),
            storage_policy_sha256=record_digest(self.audit),
        )
        initial = f.initial.model_copy(
            update={
                "inventory": spec,
                "configuration": config,
                "helper_build": self.build,
                "bootstrap": prepare_linux_bootstrap(
                    config, helper_binary=f.fixture.policy.helper_binary
                ),
            }
        )
        f.initial = initial
        f.driver.inputs = initial
        f.driver._charged_build_input_payload = initial.model_dump_json()
        observer = f.driver.observer
        observer.spec = observer.spec.model_copy(update={"configuration": record_digest(config)})
        # A new independent fixture journal supplies the one original charge.
        from crewshal.durable import CoordinatorStore

        store = CoordinatorStore(f.fixture.root / "policy-charged-state")
        self.addCleanup(store.close)
        f.driver.store = store
        claim = store.charge_storage_installation(
            "f" * 64,
            owner=record_digest(observer.spec),
            configuration=record_digest(config),
            batch_started_monotonic=f.driver.origin,
        )
        claim.bind_reservation(f.driver.reservation)
        f.driver.reservation._capacity_claim = claim
        f.driver.reservation._configuration = config
        f.driver.reservation._configuration_digest = record_digest(config)
        for name, raw in {"policy.binary": b"fresh independently read compiled policy"}.items():
            path = f.fixture.root / name
            path.write_bytes(raw)
            fd = os.open(path, os.O_RDONLY)
            self.addCleanup(os.close, fd)
            f.driver.handles["build-output:" + name] = fd
        policy_sha = digest(b"fresh independently read compiled policy")
        f.driver.derived_storage_audit = self.audit.model_copy(
            update={"policy_binary_sha256": policy_sha}
        )
        path = f.fixture.root / "storage-audit.json"
        path.write_bytes(f.driver.derived_storage_audit.model_dump_json().encode())
        fd = os.open(path, os.O_RDONLY)
        self.addCleanup(os.close, fd)
        f.driver.handles["build-output:storage-audit.json"] = fd
        f.driver._compiler_task_handles = (10, 11, 12, 13)
        f.driver._policy_task_handles = (20, 21, 22, 23)
        f.driver.timer = SimpleNamespace(
            verify=Mock(),
            verify_idle_retention=Mock(),
            end_ns=int((f.driver.origin + 600) * 1_000_000_000),
        )
        f.driver._bind_compiled_helper()
        return f.bind()

    def test_full_receipt_derives_exact_policy_and_audit_under_original_charge(self):
        receipt = self.full_derivation()
        receipt.verify()
        self.assertEqual(
            receipt.record.policy_binary, digest(b"fresh independently read compiled policy")
        )
        self.assertEqual(
            set(receipt.record.outputs),
            {"crewshal-bootstrap", "policy.binary", "storage-audit.json"},
        )
        self.assertEqual(set(receipt.record.processes), {"compiler", "policy"})
        self.assertEqual(receipt._claim.record.logical_bytes, 8589934592)
        self.assertEqual(
            receipt._claim.record.configuration, record_digest(self.f.initial.configuration)
        )

    def test_nonderived_audit_field_mutation_refuses_and_retains_original_outputs(self):
        receipt = self.full_derivation()
        path = self.f.fixture.root / "storage-audit.json"
        changed = self.f.driver.derived_storage_audit.model_copy(
            update={"kernel_release": "changed"}
        )
        path.write_bytes(changed.model_dump_json().encode())
        with self.assertRaisesRegex(ValueError, "bytes or retained identity"):
            receipt.verify()
        self.assertTrue(receipt.failed)
        for fd in receipt.outputs.values():
            os.fstat(fd)

    def test_policy_process_pointer_change_refuses(self):
        receipt = self.full_derivation()
        self.f.driver._policy_task_handles = (30, 31, 32, 33)
        with self.assertRaisesRegex(ValueError, "process custody"):
            receipt.verify()
        self.assertTrue(receipt.failed)

    def test_idle_readback_uses_original_terminal_timer_and_immutable_outputs(self):
        receipt = self.full_derivation()
        timer = self.f.driver.timer
        with (
            patch("crewshal.linux_charged_build.time.monotonic_ns", return_value=timer.end_ns),
            patch(
                "crewshal.linux_charged_build.os.fstatvfs",
                return_value=SimpleNamespace(f_flag=os.ST_RDONLY),
            ),
            patch(
                "crewshal.linux_operational._hash_file",
                side_effect=AssertionError("no active hash deadline"),
            ),
        ):
            receipt.verify()
        timer.verify_idle_retention.assert_called_once()
        self.assertFalse(receipt.failed)

    def test_idle_readback_refuses_changed_output_metadata_and_writable_mount(self):
        for changed in (False, True):
            with self.subTest(changed=changed):
                # Each original receipt is one-shot. Use a fresh fixture.
                fixture = BootstrapBuildClosure()
                fixture.setUp()
                self.addCleanup(fixture.doCleanups)
                receipt = fixture.full_derivation()
                timer = fixture.f.driver.timer
                if changed:
                    (fixture.f.fixture.root / "storage-audit.json").write_bytes(b"changed")
                with (
                    patch(
                        "crewshal.linux_charged_build.time.monotonic_ns", return_value=timer.end_ns
                    ),
                    patch(
                        "crewshal.linux_charged_build.os.fstatvfs",
                        return_value=SimpleNamespace(f_flag=os.ST_RDONLY if changed else 0),
                    ),
                ):
                    with self.assertRaisesRegex(ValueError, "immutable build output"):
                        receipt.verify()
                self.assertTrue(receipt.failed)

    def test_recipe_refuses_policy_kernel_cache_and_ambient_configuration_routes(self):
        for argument in (
            "--replace",
            "--write-cache",
            "--replace=other",
            "-r",
            "--config-file=/etc/apparmor/parser.conf",
        ):
            payload = self.policy.model_dump()
            payload["argv"].insert(-1, argument)
            with self.subTest(argument=argument), self.assertRaises(ValueError):
                FrozenPolicyBuild.model_validate(payload)
        payload = self.policy.model_dump()
        payload["environment"] = {"LD_PRELOAD": "other"}
        with self.assertRaises(ValueError):
            FrozenPolicyBuild.model_validate(payload)

    def test_policy_requires_exact_frozen_abi_and_kernel_feature_files(self):
        for prefix in ("--kernel-features=", "--override-policy-abi="):
            payload = self.policy.model_dump()
            argument = next(value for value in payload["argv"] if value.startswith(prefix))
            payload["include_files"].pop(argument.removeprefix(prefix))
            with (
                self.subTest(prefix=prefix),
                self.assertRaisesRegex(ValueError, "ABI or kernel feature"),
            ):
                FrozenPolicyBuild.model_validate(payload)

    def test_policy_accepts_the_parser_case_sensitive_include_option(self):
        payload = self.policy.model_dump()
        payload["argv"].insert(-1, "--Include=/prepared/includes")
        prepared = FrozenPolicyBuild.model_validate(payload)
        self.assertIn("--Include=/prepared/includes", prepared.argv)

    def test_policy_refuses_the_unrecognized_lowercase_include_option(self):
        payload = self.policy.model_dump()
        payload["argv"].insert(-1, "--include=/prepared/includes")
        with self.assertRaisesRegex(ValueError, "frozen policy compilation"):
            FrozenPolicyBuild.model_validate(payload)

    def test_policy_accepts_implicit_stdin_without_a_dash_filename(self):
        payload = self.policy.model_dump()
        payload["argv"] = [value for value in payload["argv"] if value != "-"]
        prepared = FrozenPolicyBuild.model_validate(payload)
        self.assertNotIn("-", prepared.argv)

    def test_policy_refuses_the_dash_filename_instead_of_stdin(self):
        payload = self.policy.model_dump()
        if "-" not in payload["argv"]:
            payload["argv"].append("-")
        with self.assertRaisesRegex(ValueError, "frozen policy compilation"):
            FrozenPolicyBuild.model_validate(payload)

    def test_policy_refuses_any_positional_profile_filename(self):
        for name in (self.policy.parser, "/ambient/other.policy"):
            payload = self.policy.model_dump()
            payload["argv"].insert(-1, name)
            with self.subTest(name=name), self.assertRaises(ValueError):
                FrozenPolicyBuild.model_validate(payload)

    def test_policy_requires_explicit_uncompressed_stdout(self):
        payload = self.policy.model_dump()
        payload["argv"] = [
            value for value in payload["argv"] if not value.startswith("--zstd-compress-level=")
        ]
        with self.assertRaisesRegex(ValueError, "frozen policy compilation"):
            FrozenPolicyBuild.model_validate(payload)

    def test_policy_accepts_one_uncompressed_option_and_refuses_conflicts(self):
        payload = self.policy.model_dump()
        payload["argv"] = [
            value for value in payload["argv"] if not value.startswith("--zstd-compress-level=")
        ]
        payload["argv"].append("--zstd-compress-level=none")
        self.assertIn("--zstd-compress-level=none", FrozenPolicyBuild.model_validate(payload).argv)
        for value in (
            "--zstd-compress-level=none",
            "--zstd-compress-level=10",
            "--zstd-compress-level=0",
        ):
            changed = {**payload, "argv": [*payload["argv"], value]}
            with (
                self.subTest(value=value),
                self.assertRaisesRegex(ValueError, "frozen policy compilation"),
            ):
                FrozenPolicyBuild.model_validate(changed)

    def test_recipe_refuses_missing_storage_header_or_runtime_closure(self):
        for name, value in (("filesystem", None), ("header_files", {}), ("runtime_files", {})):
            with self.subTest(name=name), self.assertRaises(ValueError):
                FrozenHelperBuild.model_validate({**self.build.model_dump(), name: value})

    def test_fresh_constructor_recipe_preserves_limits_without_predicted_kernel_inodes(self):
        from crewshal.linux_compiler_volume import FrozenCompilerVolumeRecipe

        construction = FrozenCompilerVolumeRecipe(
            formatter="/prepared/mkfs.ext4", formatter_sha256="1" * 64
        )
        actual = FrozenHelperBuild.model_validate(
            {
                **self.build.model_dump(),
                "filesystem": None,
                "volume_constructor": construction,
            }
        )
        self.assertIsNone(actual.filesystem)
        self.assertEqual(actual.volume_constructor.bytes, 16777216)
        for name, changed in (
            ("bytes", 33554432),
            ("maximum_inodes", 129),
            ("loop_allocator", "/dev/other"),
        ):
            with self.subTest(name=name), self.assertRaises(ValueError):
                FrozenCompilerVolumeRecipe.model_validate(
                    {**construction.model_dump(), name: changed}
                )

    def test_fresh_backing_handoff_requires_zero_bytes_before_original_growth(self):
        from crewshal.linux_compiler_volume import OriginalCompilerVolume

        path = self.f.fixture.root / "fresh-backing"
        path.write_bytes(b"")
        fd = os.open(path, os.O_RDWR)
        self.addCleanup(os.close, fd)
        owner = object.__new__(OriginalCompilerVolume)
        owner._identities = {}
        owner.handles = {}
        real_fstat = os.fstat

        def root_owned(handle):
            info = real_fstat(handle)
            fields = list(info)
            fields[4:6] = [0, 0]
            return os.stat_result(fields)

        with patch("crewshal.linux_compiler_volume.os.fstat", side_effect=root_owned):
            owner._verify_transferred("backing", fd)
            self.assertIn("backing", owner._identities)
            os.ftruncate(fd, 1)
            with self.assertRaisesRegex(ValueError, "before its first growth"):
                owner._verify_transferred("backing", fd)
        self.assertEqual(os.fstat(fd).st_size, 1)

    def test_nonempty_formatter_directory_refuses_without_removing_its_files(self):
        from crewshal.linux_compiler_volume import OriginalCompilerVolume

        path = self.f.fixture.root / "nonempty-formatter-directory"
        path.mkdir()
        (path / "unexpected").write_bytes(b"preserve")
        fd = os.open(path, os.O_RDONLY | os.O_DIRECTORY)
        self.addCleanup(os.close, fd)
        owner = object.__new__(OriginalCompilerVolume)
        owner._identities = {}
        owner.handles = {"volume": fd}
        real_fstat = os.fstat

        def root_owned(handle):
            info = real_fstat(handle)
            fields = list(info)
            fields[4:6] = [0, 0]
            return os.stat_result(fields)

        with patch("crewshal.linux_compiler_volume.os.fstat", side_effect=root_owned):
            with self.assertRaisesRegex(ValueError, "not empty"):
                owner._verify_transferred("lost+found", fd)
        self.assertEqual((path / "unexpected").read_bytes(), b"preserve")

    def test_original_charge_precedes_group_effects_and_timer_precedes_build(self):
        from crewshal.linux_operational import OriginalInstallationDriver, OperationalRefusal

        driver = OriginalInstallationDriver(self.f.initial)
        effects = []
        values = {
            "memory.max": "805306368",
            "memory.swap.max": "0",
            "pids.max": "128",
            "cpu.max": "100000 100000",
            "cgroup.subtree_control": "memory pids cpu",
        }
        aggregate = SimpleNamespace(descriptor=10, _read=lambda name: values[name])
        observer_group = SimpleNamespace(descriptor=11, sample=Mock())
        reservation = SimpleNamespace(
            observer=self.f.driver.observer, _retain_installation_refusal=Mock()
        )
        relative = self.f.initial.cgroup_parent + "/" + self.f.initial.batch_leaf
        observer_path = relative + "/" + self.f.initial.observer_name
        import io

        def original_charge(*args, **kwargs):
            effects.append("full-charge")
            return reservation

        def group(*args, **kwargs):
            self.assertIn("full-charge", effects)
            effects.append("group")
            role = args[1].split("--", 1)[0]
            values = {
                "memory.max": str(args[3]),
                "pids.max": str(args[4]),
                "memory.swap.max": "0",
                "cpu.max": "100000 100000",
                "cgroup.type": "domain",
                "memory.events": "max 0\noom 0\noom_kill 0",
                "pids.events": "max 0",
            }
            if role in {"setup", "supervisor"}:
                from crewshal.linux_setup import _role_controls

                _role_controls(SimpleNamespace(_verify=lambda: None, _read=values.__getitem__))
            elif role in {"worker", "validator"}:
                self.assertEqual((args[3], args[4]), (134217728, 32))
            elif role == "broker":
                self.assertEqual((args[3], args[4]), (67108864, 16))
            else:
                self.fail("The role has no original control contract.")
            created = SimpleNamespace(descriptor=12)
            driver.groups[args[1]] = created
            return created

        def timer(*args, **kwargs):
            self.assertEqual(effects.count("group"), 13)
            effects.append("original-timer")
            raise ValueError("stop before build effects")

        # The test observes effect order through the driver, without kernel mutation.
        with (
            patch("crewshal.linux_operational.sys.platform", "linux"),
            patch("crewshal.linux_operational.os.getuid", return_value=0),
            patch("crewshal.linux_operational.os.getgid", return_value=0),
            patch.dict("crewshal.linux_operational.os.environ", {}, clear=True),
            patch("crewshal.linux_operational.os.chdir"),
            patch("crewshal.linux_operational.os.setgroups"),
            patch("crewshal.linux_operational.resource.setrlimit"),
            patch(
                "crewshal.linux_operational.ctypes.CDLL",
                return_value=SimpleNamespace(prctl=Mock(return_value=0)),
            ),
            patch("crewshal.linux_operational._open_path", return_value=9),
            patch("crewshal.linux_operational._read", return_value=b"memory pids cpu"),
            patch.object(driver, "_attach_original_group", side_effect=[aggregate, observer_group]),
            patch.object(driver, "_retain_observer", return_value=self.f.driver.observer),
            patch.object(driver, "_group", side_effect=group),
            patch("crewshal.linux_operational.CoordinatorStore", return_value=self.f.driver.store),
            patch("crewshal.linux_operational.Path.exists", return_value=False),
            patch(
                "crewshal.linux_operational.reserve_storage_installation",
                side_effect=original_charge,
            ),
            patch("crewshal.linux_operational.create_owned_early_batch_timer", side_effect=timer),
            patch(
                "builtins.open", return_value=io.BytesIO(("0::/" + observer_path + "\n").encode())
            ),
            patch.object(driver, "_compile_helper") as compile_helper,
        ):
            from crewshal.linux_early_timer import FrozenEarlyTimerRuntime

            driver.inputs = driver.inputs.model_copy(
                update={
                    "early_timer": FrozenEarlyTimerRuntime(
                        interpreter="/prepared/python",
                        interpreter_sha256="1" * 64,
                        files={"/prepared/python": "1" * 64},
                    )
                }
            )
            driver.inputs.inventory.root["/usr/sbin"] = RootEntry(kind="directory", mode=0o755)
            driver.inputs.inventory.root["/usr/sbin/mkfs.ext4"] = RootEntry(
                kind="file", mode=0o555, sha256=driver.inputs.formatter_sha256
            )
            driver.inputs.sources["/usr/sbin/mkfs.ext4"] = driver.inputs.formatter
            driver._input_payload = driver.inputs.model_dump_json()
            with self.assertRaisesRegex(OperationalRefusal, "stop before build"):
                driver.install()
            compile_helper.assert_not_called()
        self.assertEqual(effects[0], "full-charge")
        self.assertEqual(effects[-1], "original-timer")
        self.assertIs(driver.reservation, reservation)
        self.assertTrue(driver.failed)
        reservation._retain_installation_refusal.assert_called_once()

    def test_original_compiler_volume_attempt_cannot_be_repeated(self):
        from crewshal.linux_compiler_volume import OriginalCompilerVolume

        owner = object.__new__(OriginalCompilerVolume)
        owner.attempted, owner.failed = True, False
        with patch("crewshal.linux_compiler_volume.os.mkdir") as create:
            with self.assertRaisesRegex(ValueError, "consumed"):
                owner.create()
            create.assert_not_called()

    def compiler_role_fixture(self):
        from tests.acceptance.test_phase_2d_early_timer import Phase2DEarlyTimer

        fixture = Phase2DEarlyTimer()
        fixture.setUp()
        self.addCleanup(fixture.doCleanups)
        group = fixture.groups["qualification-1"]["setup"]
        path = fixture.fixture.f.aggregate_path / "setup--qualification-1"
        return group, path

    def test_compiler_sealing_refuses_populated_setup_before_mount(self):
        from crewshal.linux_operational import OriginalInstallationDriver

        setup, path = self.compiler_role_fixture()
        path.joinpath("cgroup.procs").write_text("12345\n")
        path.joinpath("cgroup.events").write_text("populated 1\nfrozen 0\n")
        driver = object.__new__(OriginalInstallationDriver)
        driver.compiler_storage = SimpleNamespace(verify=Mock())
        mount = Mock(return_value=0)
        with patch(
            "crewshal.linux_operational.ctypes.CDLL", return_value=SimpleNamespace(mount=mount)
        ):
            with self.assertRaisesRegex(ValueError, "setup is not empty"):
                driver._seal_compiler_volume(self.build, setup)
        mount.assert_not_called()
        driver.compiler_storage.verify.assert_not_called()

    def test_compiler_sealing_checks_empty_role_before_readonly_transition(self):
        from crewshal.linux_operational import OriginalInstallationDriver

        setup, path = self.compiler_role_fixture()
        driver = object.__new__(OriginalInstallationDriver)
        driver.compiler_storage = SimpleNamespace(verify=Mock())

        def mount(*args):
            self.assertEqual(path.joinpath("cgroup.procs").read_text(), "")
            self.assertEqual(args[3].value, 1 | 2 | 4 | 32)
            return 0

        with patch(
            "crewshal.linux_operational.ctypes.CDLL",
            return_value=SimpleNamespace(mount=Mock(side_effect=mount)),
        ):
            driver._seal_compiler_volume(self.build, setup)
        driver.compiler_storage.verify.assert_called_once()

    def test_retained_compiler_role_keeps_controls_during_later_role_use(self):
        from crewshal.linux_operational import RetainedCompilerStorage

        setup, path = self.compiler_role_fixture()
        retained = object.__new__(RetainedCompilerStorage)
        retained.setup = setup
        path.joinpath("cgroup.procs").write_text("12345\n")
        path.joinpath("cgroup.events").write_text("populated 1\nfrozen 0\n")
        retained._verify_setup_role()
        path.joinpath("pids.max").write_text("129\n")
        with self.assertRaisesRegex(ValueError, "controls differ"):
            retained._verify_setup_role()
        path.joinpath("pids.max").write_text("128\n")
        path.joinpath("memory.events").write_text("max 1\noom 0\noom_kill 0\n")
        with self.assertRaisesRegex(ValueError, "refusal history"):
            retained._verify_setup_role()
        os.fstat(setup.descriptor)

    def test_compiler_mount_preserves_the_linked_formatter_directory(self):
        from crewshal.linux_compiler_volume import OriginalCompilerVolume

        volume = self.f.fixture.root / "linked-formatter-volume"
        volume.mkdir(mode=0o700)
        (volume / "lost+found").mkdir(mode=0o700)
        owner = object.__new__(OriginalCompilerVolume)
        owner.handles = {"mountpoint": 10, "loop": 11}
        owner.build = SimpleNamespace(volume=str(volume))

        def transfer(name, fd):
            owner.handles[name] = fd
            self.addCleanup(os.close, fd)

        owner.channel = SimpleNamespace(transfer=transfer)
        with patch(
            "crewshal.linux_compiler_volume.ctypes.CDLL",
            return_value=SimpleNamespace(mount=Mock(return_value=0)),
        ):
            self.assertEqual(owner._mount_child(), b"compiler-volume-mounted")
        retained = os.fstat(owner.handles["lost+found"])
        linked = (volume / "lost+found").stat()
        self.assertEqual((retained.st_dev, retained.st_ino), (linked.st_dev, linked.st_ino))
        self.assertGreater(retained.st_nlink, 0)
        self.assertEqual(os.listdir(owner.handles["lost+found"]), [])

    def test_formatter_readback_refuses_unlinked_replaced_or_nonempty_directory(self):
        from crewshal.linux_compiler_volume import OriginalCompilerVolume

        for change in ("none", "unlink", "replace", "content"):
            with self.subTest(change=change):
                volume = self.f.fixture.root / ("formatter-readback-" + change)
                volume.mkdir(mode=0o700)
                directory = volume / "lost+found"
                directory.mkdir(mode=0o700)
                owner = object.__new__(OriginalCompilerVolume)
                owner.handles = {}
                for name, path in (("volume", volume), ("lost+found", directory)):
                    fd = os.open(path, os.O_RDONLY | os.O_DIRECTORY)
                    self.addCleanup(os.close, fd)
                    owner.handles[name] = fd
                owner._identities = {
                    name: owner._identity(fd) for name, fd in owner.handles.items()
                }
                if change in {"unlink", "replace"}:
                    directory.rmdir()
                if change == "replace":
                    directory.mkdir(mode=0o700)
                if change == "content":
                    (directory / "unexpected").write_bytes(b"preserve")
                if change == "none":
                    owner.verify_formatter_directory()
                else:
                    with self.assertRaises((OSError, ValueError)):
                        owner.verify_formatter_directory()
                os.fstat(owner.handles["lost+found"])
                if change == "content":
                    self.assertEqual((directory / "unexpected").read_bytes(), b"preserve")

    def test_child_audit_write_preserves_original_readonly_output_custody(self):
        import fcntl
        import resource
        from crewshal.linux_operational import OriginalInstallationDriver

        path = self.f.fixture.root / "readonly-audit-custody"
        path.write_bytes(b"")
        fd = os.open(path, os.O_RDONLY)
        self.addCleanup(os.close, fd)
        driver = object.__new__(OriginalInstallationDriver)
        driver.handles = {"build-output:storage-audit.json": fd}
        driver._audit_bytes = b"independent bounded audit bytes"
        real_open = os.open

        def magic_alias(value, flags):
            self.assertEqual(value, "/proc/self/fd/" + str(fd))
            writer = real_open(path, flags)
            self.addCleanup(os.close, writer)
            return writer

        with (
            patch.object(resource, "setrlimit"),
            patch("crewshal.linux_operational.os.open", side_effect=magic_alias),
        ):
            self.assertEqual(driver._write_derived_audit_child(), b"derived-audit-written")
        self.assertEqual(fcntl.fcntl(fd, fcntl.F_GETFL) & os.O_ACCMODE, os.O_RDONLY)
        self.assertEqual(os.pread(fd, 100, 0), driver._audit_bytes)
        with (
            patch.object(resource, "setrlimit"),
            patch("crewshal.linux_operational.os.open", side_effect=magic_alias),
        ):
            with self.assertRaisesRegex(ValueError, "before its first write"):
                driver._write_derived_audit_child()

    def test_original_policy_compilation_attempt_cannot_be_repeated(self):
        self.f.driver._policy_attempted = True
        with patch("crewshal.linux_operational._open_path") as acquire:
            with self.assertRaisesRegex(ValueError, "policy compilation attempt consumed"):
                self.f.driver._compile_policy(self.build, object(), 123.0)
            acquire.assert_not_called()

    def test_shared_build_deadline_cannot_restart_for_second_process(self):
        self.f.driver._build_deadline = 123.0
        with patch("crewshal.linux_operational.os.fork") as fork:
            with self.assertRaisesRegex(ValueError, "changed or expired"):
                self.f.driver._run_build_process("policy", 1, 2, [], {}, object(), 124.0, {})
            fork.assert_not_called()
