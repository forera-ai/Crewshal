"""Read published synthetic evidence only; never grants execution or launches a guest."""

import hashlib
import json
from pathlib import Path
import stat

path = Path(__file__).with_name("phase-2c-local-storage-observed-v6.json")
assert path.stat().st_size <= 16777216
report = json.loads(path.read_text())
assert report["execution_allowed"] is False and report["native_start_allowed"] is False
assert report["errors"] == [] and len(report["fixtures"]) == 2
assert len({fixture["session_ring"] for fixture in report["fixtures"]}) == 2
matches = 0
for fixture in report["fixtures"]:
    assert fixture["errors"] == [] and len(fixture["cases"]) == 22
    boundary = fixture["boundary"]["result"]
    assert boundary["uid"] == boundary["gid"] == 65534
    assert boundary["file_size_limit"] == [-1, -1]
    assert all(item["denied"] for item in boundary["denials"].values())
    assert " - ecryptfs " in boundary["work_mount"][0]
    assert all("0000000000000000" in line for line in boundary["status"] if line.startswith("Cap"))
    for case in fixture["cases"]:
        assert case["failure"] is None and case["post_stop_pids"] == []
        result = case["result"]
        final = case["fd_samples"][-1]
        assert final["namespace_pids"][-1] == result["pid"]
        reported = {(item["device"], item["inode"]): item for item in result["files"].values()}
        for observed in final["files"]:
            expected = reported[(observed["device"], observed["inode"])]
            assert all(
                observed[key] == expected[key]
                for key in ("logical_bytes", "allocated_bytes", "links")
            )
        assert all(
            "crewshal-storage-local-v1.slice" in group for group in case["placement"].values()
        )
        assert case["after_case_cleanup"] == {"upper": [], "lower": []}
        assert all(
            item["allocated_bytes"] >= item["logical_bytes"]
            for item in case["lower"]
            if stat.S_ISREG(item["mode"])
        )
        if case["case"] in ("truncate", "seek-write", "pwrite", "mmap", "hardlink"):
            if case["requested_bytes"] == 8388608:
                assert result["status"] == "operation_completed"
                assert result["files"]["target"]["logical_bytes"] == 8388608
                assert result["files"]["target"]["allocated_bytes"] >= 8388608
            else:
                assert result["errno_name"] == "ENOSPC"
        if case["case"] == "deleted-open" and case["requested_bytes"] == 8388608:
            assert any(
                item["links"] == 0 and item["allocated_bytes"] >= 8388608 for item in final["files"]
            )
        matches += 1
    cleanup = fixture["cleanup"]
    assert cleanup["loop_detached"] and cleanup["owned_files_absent"]
    assert cleanup["new_session_after"] == "keyring is empty"
    assert all(item["revoked_unlinked"] for item in cleanup["keys"])
    assert all(item["unmounted"] for item in cleanup["unmounts"])
print(
    json.dumps(
        {
            "independent_final_fd_matches": matches,
            "observation_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            "execution_allowed": False,
            "native_start_allowed": False,
            "qualification_status": "limited diagnostic observations verified; runtime qualification unavailable",
        },
        sort_keys=True,
    )
)
