"""Offline conservative accounting arithmetic; cannot enforce or qualify storage."""

import argparse
import json
from pathlib import Path

CEILING = 8589934592


def assess(plan: dict) -> dict:
    if (
        type(plan.get("schema_version")) is not int
        or plan["schema_version"] != 1
        or plan.get("execution_allowed") is not False
        or plan.get("native_start_allowed") is not False
        or plan.get("ceiling") != {"logical_bytes": CEILING, "allocated_bytes": CEILING}
        or not isinstance(plan.get("objects"), list)
        or not plan["objects"]
    ):
        raise ValueError("invalid accounting schema, original ceiling or denial flags")
    totals = {"logical_bytes": 0, "allocated_bytes": 0}
    reasons = []
    names = set()
    for item in plan["objects"]:
        if not isinstance(item, dict) or not isinstance(item.get("id"), str) or not item["id"]:
            raise ValueError("invalid accounting object")
        if item["id"] in names:
            raise ValueError("duplicate accounting object")
        names.add(item["id"])
        for dimension in totals:
            amount = item.get(dimension)
            if amount is None:
                reasons.append(f"{item['id']}: unresolved {dimension}")
            elif type(amount) is not int or amount < 0:
                raise ValueError("accounting byte counts must be nonnegative integers or null")
            else:
                totals[dimension] += amount
    for dimension, amount in totals.items():
        if amount > CEILING:
            reasons.append(f"{dimension}: exceeds original ceiling by {amount - CEILING}")
    return {
        "schema_version": 1,
        "status": "arithmetic_refused" if reasons else "arithmetic_within_ceiling_only",
        "totals": totals,
        "reasons": reasons,
        "execution_allowed": False,
        "native_start_allowed": False,
        "qualification_status": "denied; inventory completeness and enforcement unproved",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("plan", type=Path)
    arguments = parser.parse_args()
    try:
        with arguments.plan.open("rb") as source:
            raw = source.read(65537)
        if len(raw) > 65536:
            raise ValueError("accounting plan exceeds 65536 bytes")
        plan = json.loads(raw)
        if not isinstance(plan, dict):
            raise ValueError("accounting plan must be an object")
        result = assess(plan)
    except (OSError, ValueError) as error:
        parser.exit(2, f"accounting refused: {error}\n")
    print(json.dumps(result, sort_keys=True))
    return 2 if result["reasons"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
