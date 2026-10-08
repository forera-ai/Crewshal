"""Verify public mechanism observations, not a fresh Linux/native qualification."""

import hashlib
import json
from pathlib import Path


def main():
    root = Path(__file__).resolve().parents[2]
    folder = root / "docs/qualification"
    for version in range(1, 6):
        profile = json.loads(
            (folder / f"phase-2c-direct-linux-mechanism-profile-v{version}.json").read_text()
        )
        source = root / profile["source"]
        assert hashlib.sha256(source.read_bytes()).hexdigest() == profile["source_sha256"]
        binding_path = folder / f"phase-2c-direct-linux-bindings-v{version}.json"
        freeze = json.loads((folder / f"phase-2c-direct-linux-freeze-v{version}.json").read_text())
        assert hashlib.sha256(binding_path.read_bytes()).hexdigest() == freeze["bindings_sha256"]
        assert (
            hashlib.sha256(
                (folder / f"phase-2c-direct-linux-mechanism-profile-v{version}.json").read_bytes()
            ).hexdigest()
            == freeze["profile_sha256"]
        )
        observed = json.loads(
            (folder / f"phase-2c-direct-linux-observed-v{version}.json").read_text()
        )
        assert observed["manifest_sha256"] == freeze["bindings_sha256"]
        assert observed["execution_allowed"] is False
        assert observed["native_start_allowed"] is False
        if version < 4:
            continue
        assert len(observed["fixtures"]) == 2
        for fixture in observed["fixtures"]:
            assert fixture["aggregate"]["memory.max"] == "805306368"
            assert fixture["aggregate"]["memory.swap.max"] == "0"
            assert fixture["aggregate"]["cpu.max"] == "100000 100000"
            assert fixture["aggregate"]["pids.max"] == "128"
            assert fixture["worker"]["memory.max"] == "134217728"
            assert fixture["worker"]["memory.swap.max"] == "0"
            assert fixture["worker"]["cpu.max"] == "100000 100000"
            assert fixture["worker"]["pids.max"] == "32"
            assert fixture["bounds"]["exit"] == 0
            bounds = json.loads(fixture["bounds"]["stdout"])
            assert bounds["uid"] == 65534 and bounds["fsize"] == [65536, 65536]
            assert bounds["denials"] == {"readonly": True, "outside": True, "coordinator": True}
            assert bounds["/candidate/owned"]["created_before_inode_exhaustion"] == 127
            assert bounds["/scratch"]["created_before_inode_exhaustion"] == 255
            for mode in ("hold", "deadline", "allocation"):
                result = fixture[mode]
                assert result["killed"] and result["exit"] == -9
                assert result["stderr"] == "" and "populated 0" in result["terminal"]
            item = json.loads(fixture["hold"]["stdout"])
            rows = fixture["hold"]["deleted_open"]
            assert len(rows) == 1
            row = rows[0]
            assert all(item[k] == row[k] for k in ("inode", "device", "logical"))
            assert row["logical"] == 12 and row["allocated"] == 4096 and row["links"] == 0
            assert row["cgroup"].endswith("/worker")
            for name, allocated, logical, inodes in (
                ("candidate", 4194304, 16777216, 128),
                ("scratch", 8388608, 33554432, 256),
            ):
                oracle = fixture["allocation"][name]
                assert oracle["allocated"] == allocated
                assert oracle["logical"] <= logical and oracle["inodes"] <= inodes
            assert fixture["heartbeat_stopped"]
            assert fixture["cleanup"]["owned_mounts_removed"]
            assert "populated 0" in fixture["cleanup"]["worker"]
            assert fixture["seconds"] < 120
    assert (
        hashlib.sha256((folder / "phase-2c-v1.json").read_bytes()).hexdigest()
        == "fed4dde5e3fe459110a5fb0b2d4f6c75b16214c91aa823d3df640a7415e41563"
    )
    print(
        "Recorded direct Linux mechanism fixtures verified; native/broker qualification remains unavailable; execution denied."
    )


if __name__ == "__main__":
    main()
