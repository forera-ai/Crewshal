"""Offline fixture tests do not establish installed Linux acceptance."""

import base64
import json
import os
from pathlib import Path
from types import SimpleNamespace
import tempfile
import unittest
from unittest.mock import patch
from unittest.mock import Mock

from crewshal.linux_fixture_inputs import (
    ESCAPE_LINKS,
    OriginalFixtureInputs,
    SEED_ROLES,
    SyntheticQualificationAccount,
    _seed_files,
    qualification_auth_bytes,
    readonly_fixture_files,
    rebind_fixture_configuration,
)
from crewshal.linux_production import LANE_IDS
from crewshal.model import digest
from crewshal.runtime_batch import BEFORE, CHECK_SOURCE
import tests.acceptance.test_phase_2d_qualification_fixture as fixtures


class FixtureInputTests(unittest.TestCase):
    def seed_parent_transport(self, *, files_only=False):
        from crewshal import linux_fixture_inputs as seed
        from crewshal.linux_production import OwnedBackingProduction

        production = object.__new__(OwnedBackingProduction)
        production.reservation = SimpleNamespace(_retain_installation_refusal=Mock())
        production.handles = {
            "namespace": 99,
            **{
                "mounted:" + lane + "--" + role + "-upper": 100 + index
                for index, (lane, role) in enumerate(
                    (lane, role) for lane in LANE_IDS for role in SEED_ROLES
                )
            },
        }
        calls = []

        def run(action, keep, **kwargs):
            calls.append(action.__name__)
            owner = action.__self__
            if action.__name__ == "_seed_child":
                owner.channel.position = (
                    len(owner.files) if files_only else len(owner.channel.expected)
                )
                return b"original-fixtures-seeded"
            return b"original-fixtures-readback"

        production.jobs = SimpleNamespace(run=run)

        def open_channel(channel):
            channel.child = SimpleNamespace(fileno=lambda: 999)

        # Only this parent transport join runs. No child or kernel probe runs.
        with (
            patch.object(seed.OriginalFixtureInputs, "verify_custody"),
            patch.object(seed._SeedChannel, "open", open_channel),
        ):
            result = seed.OriginalFixtureInputs.seed(
                production, fixtures._plan(), SyntheticQualificationAccount()
            )
        return result, calls

    def test_seed_completion_counts_formatter_and_file_handoffs(self):
        result, calls = self.seed_parent_transport()
        self.assertEqual(len(result.files), 25)
        self.assertEqual(len(result.channel.expected), 40)
        self.assertEqual(result.channel.position, 40)
        self.assertTrue(result.complete)
        self.assertEqual(calls, ["_seed_child", "_readback_child"])

    def test_seed_file_count_alone_cannot_complete_all_original_handoffs(self):
        from crewshal.linux_production import ProductionRefusal

        with self.assertRaises(ProductionRefusal):
            self.seed_parent_transport(files_only=True)

    def test_seed_handoff_keeps_the_original_per_job_clock(self):
        from crewshal import linux_fixture_inputs as seed

        owner = SimpleNamespace(
            production=SimpleNamespace(deadline=220.0),
            jobs=SimpleNamespace(original_job_deadline=105.0),
        )
        channel = seed._SeedChannel(owner)
        channel.child = Mock()
        channel.child.sendmsg.return_value = len("file:0")
        channel.child.recv.return_value = b"1"
        with (
            patch.object(seed.time, "monotonic", side_effect=[100.0, 103.0]),
            patch.object(seed, "_wait_ready", side_effect=lambda r, w, e, t: (r, w, [])) as wait,
        ):
            channel.transfer("file:0", 42)
        self.assertEqual([call.args[3] for call in wait.call_args_list], [5.0, 2.0])

    def test_readonly_files_bind_exact_bytes_without_ambient_input(self) -> None:
        with patch.dict(os.environ, {"OPENAI_API_KEY": "must-not-enter-fixture"}):
            files = readonly_fixture_files()
        self.assertEqual(files["/input/check_fixture.py"][1], CHECK_SOURCE)
        for entry, raw in files.values():
            self.assertEqual(entry.mode, 0o444)
            self.assertEqual(entry.sha256, digest(raw))
            self.assertNotIn(b"must-not-enter-fixture", raw)
        self.assertNotIn("/root/.codex/auth.json", files)

    def test_synthetic_tokens_are_lane_bound_and_refuse_live(self) -> None:
        plan, account = fixtures._plan(), SyntheticQualificationAccount()
        values = []
        for lane in LANE_IDS[:2]:
            data = json.loads(qualification_auth_bytes(plan, account, lane))
            self.assertEqual(data["auth_mode"], "chatgpt")
            tokens = data["tokens"]
            self.assertEqual(tokens["account_id"], "crewshal-phase2d-synthetic")
            self.assertEqual(
                tokens["access_token"],
                "crewshal-phase2d-synthetic-" + lane + "-" + plan.synthetic_nonce,
            )
            claims = tokens["id_token"].split(".")[1]
            decoded = json.loads(base64.urlsafe_b64decode(claims + "=" * (-len(claims) % 4)))
            self.assertEqual(decoded["email"], "phase2d-synthetic@example.invalid")
            self.assertEqual(decoded["https://api.openai.com/auth"]["chatgpt_plan_type"], "plus")
            values.append(tokens["access_token"])
        self.assertNotEqual(*values)
        with self.assertRaisesRegex(ValueError, "refuses the live lane"):
            qualification_auth_bytes(plan, account, "live")

    def test_seed_manifest_cannot_seed_live_credentials_or_extra_candidate_paths(self) -> None:
        rows = _seed_files(fixtures._plan(), SyntheticQualificationAccount())
        live = [row for row in rows if row.lane == "live"]
        self.assertEqual(
            [(row.role, row.path, row.raw) for row in live], [("candidate", "README.md", BEFORE)]
        )
        for lane in LANE_IDS[:2]:
            names = {(row.role, row.path) for row in rows if row.lane == lane}
            self.assertIn(("scratch", "checkout/.git/hooks/pre-commit"), names)
            self.assertIn(("native-auth", "auth.json"), names)
            self.assertFalse(any(row.path in ("new", "patch-positive") for row in rows))

    def test_parsed_or_unowned_fixture_cannot_supply_creation_custody(self) -> None:
        with self.assertRaisesRegex(ValueError, "original production attempt"):
            OriginalFixtureInputs.seed(
                SimpleNamespace(), fixtures._plan(), SyntheticQualificationAccount()
            )  # type: ignore[arg-type]
        with self.assertRaisesRegex(ValueError, "exact original driver"):
            rebind_fixture_configuration(fixtures._plan(), SimpleNamespace())
        with self.assertRaisesRegex(ValueError, "original charged production"):
            OriginalFixtureInputs()

    def test_seed_effects_follow_retained_empty_files_and_formatter_directories(self) -> None:
        with tempfile.TemporaryDirectory() as location:
            root = Path(location)
            handles = {"namespace": -1}
            for lane in LANE_IDS:
                for role in SEED_ROLES:
                    directory = root / lane / role
                    directory.mkdir(parents=True)
                    (directory / "lost+found").mkdir(mode=0o700)
                    if role == "scratch":
                        (directory / "checkout").mkdir(mode=0o700)
                    handles["mounted:" + lane + "--" + role + "-upper"] = os.open(
                        directory, os.O_RDONLY | os.O_DIRECTORY
                    )
            owner = object.__new__(OriginalFixtureInputs)
            owner.production = SimpleNamespace(handles=handles)  # type: ignore[assignment]
            owner.files = _seed_files(fixtures._plan(), SyntheticQualificationAccount())
            transferred = []

            def transfer(name: str, descriptor: int) -> None:
                transferred.append(name)
                if name.startswith("formatter:"):
                    self.assertEqual(os.listdir(descriptor), [])
                else:
                    self.assertEqual(os.fstat(descriptor).st_size, 0)

            owner.channel = SimpleNamespace(transfer=transfer)  # type: ignore[assignment]
            real_fstat = os.fstat

            def fixture_fstat(descriptor: int) -> object:
                value = real_fstat(descriptor)
                return SimpleNamespace(st_uid=65534, st_gid=65534, st_mode=value.st_mode)

            try:
                with (
                    patch("crewshal.linux_fixture_inputs._enter_owned_namespace"),
                    patch("crewshal.linux_fixture_inputs.os.chown"),
                    patch("crewshal.linux_fixture_inputs.os.fchown"),
                    patch("crewshal.linux_fixture_inputs.os.fstat", side_effect=fixture_fstat),
                ):
                    # Transfer reads the real file metadata independently.
                    def transfer_checked(name: str, descriptor: int) -> None:
                        transferred.append(name)
                        if name.startswith("formatter:"):
                            self.assertEqual(os.listdir(descriptor), [])
                        else:
                            self.assertEqual(real_fstat(descriptor).st_size, 0)

                    owner.channel.transfer = transfer_checked
                    self.assertEqual(owner._seed_child(), b"original-fixtures-seeded")
                self.assertEqual(
                    transferred[:15],
                    ["formatter:" + lane + ":" + role for lane in LANE_IDS for role in SEED_ROLES],
                )
                self.assertEqual(len(transferred), 15 + len(owner.files))
                for row in owner.files:
                    self.assertEqual((root / row.lane / row.role / row.path).read_bytes(), row.raw)
                for lane in LANE_IDS:
                    for role in SEED_ROLES:
                        self.assertFalse((root / lane / role / "lost+found").exists())
                for lane in LANE_IDS[:2]:
                    for name, target in ESCAPE_LINKS:
                        self.assertEqual(os.readlink(root / lane / "scratch" / name), target)
                self.assertEqual(list((root / "live" / "native-auth").iterdir()), [])
            finally:
                for descriptor in handles.values():
                    if descriptor >= 0:
                        os.close(descriptor)


if __name__ == "__main__":
    unittest.main()
