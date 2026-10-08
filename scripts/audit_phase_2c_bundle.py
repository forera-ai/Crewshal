"""Audit a portable Phase 2C record bundle offline; no platform or runtime tests."""

import argparse
from pathlib import Path

from crewshal.qualification_bundle import audit_bundle


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory", type=Path)
    args = parser.parse_args()
    result = audit_bundle(args.directory)
    print(result.model_dump_json(indent=2))
    return 0 if result.status == "consistent_records" else 2


if __name__ == "__main__":
    raise SystemExit(main())
