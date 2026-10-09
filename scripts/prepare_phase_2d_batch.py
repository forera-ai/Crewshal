"""Offline-only Phase 2D preparation; no credential, runtime or host operation."""

import argparse
import json
from pathlib import Path

from crewshal.qualification_bundle import BoundArtifact, _json
from crewshal.runtime_batch import PreparationSelection, prepare_runtime_batch


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reference-root", type=Path, required=True)
    parser.add_argument(
        "--references",
        type=Path,
        required=True,
        help="coordinator-selected historical BoundArtifact array; no authority",
    )
    parser.add_argument("--output", type=Path, required=True, help="new external private directory")
    parser.add_argument(
        "--selection",
        type=Path,
        help="explicit project/session PreparationSelection JSON; choices are not authority",
    )
    args = parser.parse_args()
    try:
        with args.references.open("rb") as stream:
            raw = stream.read(65537)
        if len(raw) > 65536:
            raise ValueError("reference declaration exceeds 65536 bytes")
        data = _json(raw)
        if not isinstance(data, list):
            raise ValueError("references must be an array")
        references = [BoundArtifact.model_validate(item) for item in data]
        selection = None
        if args.selection is not None:
            with args.selection.open("rb") as stream:
                raw = stream.read(65537)
            if len(raw) > 65536:
                raise ValueError("selection declaration exceeds 65536 bytes")
            selection = PreparationSelection.model_validate(_json(raw))
        result = prepare_runtime_batch(
            args.reference_root, args.output, references, selection=selection
        )
        print(result.model_dump_json(indent=2))
        return 0
    except (ValueError, OSError) as error:
        print(json.dumps({"status": "denied", "reason": str(error), "execution_allowed": False}))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
