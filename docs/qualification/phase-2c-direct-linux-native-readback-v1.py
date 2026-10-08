"""Verify recorded native discovery failures/help; never full qualification."""

import hashlib
import json
from pathlib import Path


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    root = Path(__file__).resolve().parents[2]
    folder = root / "docs/qualification"
    integrity = json.loads(
        (folder / "phase-2c-direct-linux-native-observation-integrity-v1.json").read_text()
    )
    for item in integrity["observed"]:
        assert digest(folder / item["path"]) == item["sha256"]
    for stem, count in (("native-discovery", 4), ("native-compatibility", 1)):
        for version in range(1, count + 1):
            prefix = f"phase-2c-direct-linux-{stem}"
            profile_path = folder / f"{prefix}-profile-v{version}.json"
            profile = json.loads(profile_path.read_text())
            freeze = json.loads((folder / f"{prefix}-freeze-v{version}.json").read_text())
            assert digest(profile_path) == freeze["profile_sha256"]
            assert digest(root / profile["source"]) == profile["source_sha256"]
            binding = folder / freeze["manifest"]
            assert digest(binding) == freeze["manifest_sha256"]
            observed = json.loads((folder / f"{prefix}-observed-v{version}.json").read_text())
            assert observed["manifest_sha256"] == freeze["manifest_sha256"]
            assert not observed["execution_allowed"] and not observed["native_start_allowed"]
            assert not observed["credential_mediation_qualified"]
            if stem == "native-discovery" and version == 4:
                assert len(observed["records"]) == 8
                for record in observed["records"]:
                    assert record["exit"] == 0 and record["seconds"] < 10
                    assert record["controls"] == [
                        {
                            "memory.max": "134217728",
                            "memory.swap.max": "0",
                            "cpu.max": "100000 100000",
                            "pids.max": "32",
                        }
                    ]
                    assert all(
                        len(record[stream].encode()) <= 65536 for stream in ("stdout", "stderr")
                    )
                assert [r["fixture"] for r in observed["records"]] == [1] * 4 + [2] * 4
            if stem == "native-compatibility":
                assert len(observed["records"]) == 1
                record = observed["records"][0]
                assert record["exit"] == 1
                assert "Failed RTM_NEWADDR: Operation not permitted" in record["stderr"]
                assert not record["stdout"]
    print(
        "Recorded native help passes twice; sandbox startup refused; full Phase 2C remains denied."
    )


if __name__ == "__main__":
    main()
