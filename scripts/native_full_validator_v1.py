"""Credential-free readonly validator attempts; parent validates every observation."""

import importlib.util
import json
from pathlib import Path

spec = importlib.util.spec_from_file_location("hostile", "/input/native-full-payload.py")
hostile = importlib.util.module_from_spec(spec)
spec.loader.exec_module(hostile)
result = hostile.observe()
result["candidate_read"] = (Path("/candidate/owned") / "existing").read_bytes().decode()
result["candidate_write"] = hostile.deny(
    lambda: (Path("/candidate/owned") / "existing").write_bytes(b"validator escape")
)
result["candidate_new"] = hostile.deny(
    lambda: (Path("/candidate/owned") / "validator-new").write_bytes(b"validator escape")
)
print(json.dumps(result), flush=True)
