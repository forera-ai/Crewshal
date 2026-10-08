"""Verify the immutable native setup failures and pending fixture policy proposal."""

import hashlib
import json
from pathlib import Path


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    root = Path(__file__).resolve().parents[2]
    folder = root / "docs/qualification"
    assert (
        digest(folder / "phase-2c-v1.json")
        == "fed4dde5e3fe459110a5fb0b2d4f6c75b16214c91aa823d3df640a7415e41563"
    )
    prefix = "phase-2c-direct-linux-native-compatibility"
    reasons = {
        2: "Failed to mount tmpfs",
        4: "setresuid failed",
        5: "Specifying --uid requires",
        6: "--permission-profile",
        7: "error building bubblewrap command",
        8: "overflowuid",
        9: "setting up uid map",
        10: "setting up uid map",
    }
    for version, reason in reasons.items():
        profile_path = folder / f"{prefix}-profile-v{version}.json"
        profile = json.loads(profile_path.read_text())
        freeze = json.loads((folder / f"{prefix}-freeze-v{version}.json").read_text())
        observed = json.loads((folder / f"{prefix}-observed-v{version}.json").read_text())
        assert digest(profile_path) == freeze["profile_sha256"]
        assert digest(root / profile["source"]) == profile["source_sha256"]
        assert digest(folder / freeze["manifest"]) == freeze["manifest_sha256"]
        assert observed["manifest_sha256"] == freeze["manifest_sha256"]
        assert len(observed["records"]) == 1
        record = observed["records"][0]
        assert record["exit"] != 0 and reason in record["stderr"]
        assert not record["stdout"] and record["seconds"] < 10
        assert all(len(record[s].encode()) <= 65536 for s in ("stdout", "stderr"))
        assert not observed["execution_allowed"] and not observed["native_start_allowed"]
        assert not observed["credential_mediation_qualified"]
    policies = [
        folder / f"phase-2c-direct-linux-native-apparmor-proposal-v{v}.profile" for v in (2, 3, 4)
    ]
    v2, v3, v4 = [p.read_text() for p in policies]
    assert v3.replace(" flags=(chroot_relative)", "") == v2
    assert v4.replace("chroot_relative,attach_disconnected", "chroot_relative") == v3
    assert "attach_disconnected" not in v4.split("profile crewshal-native-tool-v1", 1)[1]
    proposal = json.loads(
        (folder / "phase-2c-direct-linux-native-apparmor-proposal-v4.json").read_text()
    )
    assert digest(policies[2]) == proposal["profile_sha256"]
    assert "pending" in proposal["status"]
    future = json.loads((folder / f"{prefix}-profile-v11.json").read_text())
    assert digest(root / future["source"]) == future["source_sha256"]
    cleanup = json.loads(
        (folder / "phase-2c-direct-linux-native-cleanup-observed-v2.json").read_text()
    )
    for key in (
        "before_process_fd_references",
        "after_process_fd_references",
        "owned_fixture_paths_remaining",
        "owned_loaded_profiles_remaining",
    ):
        assert cleanup[key] == []
    assert cleanup["global_userns_restriction"] == "1"
    external = json.loads(
        (folder / "phase-2c-direct-linux-native-external-cleanup-v2.json").read_text()
    )
    for key in ("cgroup_present", "aggregate_unit_present", "fixture_present"):
        assert not external[key]
    for key in ("run_artifacts", "tmp_artifacts", "profiles", "owned_units"):
        assert external[key] == []
    print(
        "Eight native setup refusals preserved; scoped v4 pending; owned cleanup observed; 2C denied."
    )


if __name__ == "__main__":
    main()
