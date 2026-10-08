"""Human-facing offline initialization; no execution, approval or runtime launcher."""

import argparse
from pathlib import Path
import sys
import sqlite3
from typing import TextIO

from crewshal.discovery import Limits, discover
from crewshal.model import (
    DecisionBatch,
    HumanDecision,
    ProjectModel,
    decide,
    model_digest,
    reconcile,
)
from crewshal.state import MAX_RECORD_BYTES, ModelStore, default_state, export_model, load_model


def interact(model: ProjectModel, source: TextIO, output: TextIO) -> ProjectModel:
    result = model
    for proposal in model.facts:
        if proposal.decision != "pending":
            continue
        locations = ", ".join(f"{s.path} [{s.location}]" for s in proposal.sources) or "no source"
        print(f"{proposal.id}: {proposal.value!r} ({proposal.origin}; {locations})", file=output)
        print(
            "confirm / reject / correct <literal value> / skip: ", end="", file=output, flush=True
        )
        answer = source.readline()
        if not answer:
            raise ValueError("interaction ended before explicit decisions; state not saved")
        answer = answer.strip()
        if not answer or answer == "skip":
            continue
        if answer.startswith("correct "):
            decision = HumanDecision(
                fact_id=proposal.id,
                action="correct",
                value=answer[8:],
                reason="interactive human correction",
            )
            result = decide(result, [decision])
            print("confirm corrected value / skip: ", end="", file=output, flush=True)
            confirmation = source.readline()
            if not confirmation:
                raise ValueError("interaction ended before confirmation; state not saved")
            if confirmation.strip() == "confirm":
                result = decide(
                    result,
                    [
                        HumanDecision(
                            fact_id=proposal.id,
                            action="confirm",
                            reason="interactive human confirmation",
                        )
                    ],
                )
            elif confirmation.strip() not in {"", "skip"}:
                raise ValueError("expected confirm or skip")
        elif answer in {"confirm", "reject"}:
            result = decide(
                result,
                [
                    HumanDecision.model_validate(
                        {
                            "fact_id": proposal.id,
                            "action": answer,
                            "reason": "interactive human decision",
                        }
                    )
                ],
            )
        else:
            raise ValueError("expected confirm, reject, correct <value>, or skip")
    return result


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(prog="crewshal", description="Offline project discovery")
    commands = result.add_subparsers(dest="command", required=True)
    initialize = commands.add_parser(
        "init", help="discover, optionally correct/confirm, save externally"
    )
    initialize.add_argument("repository", type=Path)
    initialize.add_argument("--state-dir", type=Path, default=default_state())
    initialize.add_argument(
        "--migrate-state",
        action="store_true",
        help="explicit supported state migration with backup",
    )
    choices = initialize.add_mutually_exclusive_group()
    choices.add_argument("--interactive", action="store_true", help="read explicit human decisions")
    choices.add_argument(
        "--decisions", type=Path, help="replay an explicit digest-bound decision batch"
    )
    initialize.add_argument(
        "--export", metavar="RELATIVE_FILE", help="explicit new repository export"
    )
    initialize.add_argument("--max-files", type=int, default=2000)
    initialize.add_argument("--max-file-bytes", type=int, default=262144)
    initialize.add_argument("--max-total-bytes", type=int, default=2097152)
    initialize.add_argument("--max-depth", type=int, default=12)
    show = commands.add_parser(
        "show", help="inspect stored model; does not refresh source validity"
    )
    show.add_argument("repository", type=Path)
    show.add_argument("--state-dir", type=Path, default=default_state())
    show.add_argument(
        "--migrate-state",
        action="store_true",
        help="explicit supported state migration with backup",
    )
    show.add_argument("--digest", action="store_true", help="digest for explicit decision replay")
    validate = commands.add_parser("validate", help="refuse malformed or unsupported model records")
    validate.add_argument("model", type=Path)
    return result


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    try:
        if args.command == "validate":
            print(load_model(args.model).public_json(), end="")
            return 0
        root = args.repository.resolve(strict=True)
        store = ModelStore(root, args.state_dir, migrate=args.migrate_state)
        previous = store.load()
        if args.command == "show":
            if previous is None:
                raise ValueError("no stored model; run init first")
            print(
                model_digest(previous) if args.digest else previous.public_json(),
                end="\n" if args.digest else "",
            )
            return 0
        limits = Limits(
            files=args.max_files,
            file_bytes=args.max_file_bytes,
            total_bytes=args.max_total_bytes,
            depth=args.max_depth,
        )
        raw = discover(root, limits)
        fingerprint = model_digest(raw)
        model = reconcile(raw, previous)
        if args.interactive:
            model = interact(model, sys.stdin, sys.stderr)
        elif args.decisions:
            with args.decisions.open("rb") as stream:
                data = stream.read(MAX_RECORD_BYTES + 1)
            if len(data) > MAX_RECORD_BYTES:
                raise ValueError("decision batch exceeds size limit")
            batch = DecisionBatch.model_validate_json(data)
            if batch.model_digest != model_digest(model):
                raise ValueError("decision batch is stale or belongs to another model")
            model = decide(model, batch.decisions)
        if fingerprint != model_digest(discover(root, limits)):
            raise ValueError("discovery inputs changed during interaction; repeat init")
        if args.export:
            export_model(root, args.export, model)
        store.save(model)
        print(model.public_json(), end="")
        print(
            f"{len(model.unresolved)} unresolved facts; no execution authority granted",
            file=sys.stderr,
        )
        return 0
    except (OSError, ValueError, RecursionError, sqlite3.Error) as error:
        print(f"crewshal: {error}", file=sys.stderr)
        return 2
