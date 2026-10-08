"""Independent diagnostic readback. Evidence never grants execution permission."""

import argparse
import hashlib
import json
import math
from pathlib import Path
import sys

from pydantic import ValidationError

from crewshal.qualification import (
    MANDATORY_CASES,
    ProbeResult,
    Qualification,
    QualificationIdentity,
    assess_qualification,
)

PROTOCOL = "fed4dde5e3fe459110a5fb0b2d4f6c75b16214c91aa823d3df640a7415e41563"
CONTROLS = {
    "memory.max": "134217728",
    "memory.swap.max": "0",
    "cpu.max": "100000 100000",
    "pids.max": "32",
}
AGGREGATE = {**CONTROLS, "memory.max": "805306368", "pids.max": "128"}


def sha(data):
    return hashlib.sha256(data).hexdigest()


def canonical(value):
    return sha(json.dumps(value, sort_keys=True, separators=(",", ":")).encode())


def load(path):
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise ValueError("duplicate JSON key")
            result[key] = value
        return result

    def constant(value):
        raise ValueError("nonfinite JSON")

    def finite(value):
        result = float(value)
        if not math.isfinite(result):
            raise ValueError("nonfinite JSON")
        return result

    raw = Path(path).read_bytes()
    if len(raw) > 16777216:
        raise ValueError("readback input exceeds bound")
    return json.loads(raw, object_pairs_hook=pairs, parse_constant=constant, parse_float=finite)


def refusal(identity):
    """Fresh local fixtures, using the bound product assessor for each run."""
    results = [
        ProbeResult(case=case, status="passed", observation="refusal fixture")
        for case in MANDATORY_CASES
    ]
    record = Qualification(id="independent-refusal-fixture", identity=identity, results=results)
    decisions = [assess_qualification(None, identity)]
    for case in MANDATORY_CASES:
        for status in ("failed", "unavailable"):
            changed = [
                item.model_copy(update={"status": status}) if item.case == case else item
                for item in results
            ]
            decisions.append(
                assess_qualification(record.model_copy(update={"results": changed}), identity)
            )
    for name in QualificationIdentity.model_fields:
        changed = identity.model_copy(
            update={name: "a" * 64 if len(str(getattr(identity, name))) == 64 else "changed"}
        )
        decisions.append(assess_qualification(record, changed))
    for changed in (results[:-1], results + [results[0]]):
        decisions.append(
            assess_qualification(record.model_copy(update={"results": changed}), identity)
        )
    for changed in ({"execution_allowed": True}, {"schema_version": 2}, {"unexpected": "grant"}):
        try:
            assess_qualification(
                Qualification.model_validate({**record.model_dump(), **changed}), identity
            )
        except ValidationError:
            continue
        raise ValueError("malformed qualification did not refuse")
    if any(d.status != "denied" or d.execution_allowed is not False for d in decisions):
        raise ValueError("unsafe qualification did not deny")
    return {
        "fresh_denied_decisions": len(decisions),
        "malformed_refused": 3,
        "execution_allowed": False,
    }


def instruction_evidence(record, roles):
    requests = record["fixture_requests_after_capture"]
    return (
        len(requests) >= 2
        and all(
            set(x["tools"]) == {"exec_command", "write_stdin", "request_user_input"}
            and x["instruction_injection_present"] is False
            for x in requests
        )
        and all(
            set(role["global_instruction_view"]) == {"AGENTS.md", "AGENTS.override.md"}
            and all(
                x["contents"] == ""
                and x["write"]["denied"] is True
                and x["unlink"]["denied"] is True
                for x in role["global_instruction_view"].values()
            )
            for role in roles
        )
    )


def check_run(record, identity, binding_verified):
    """Require named observable fields; never fill missing evidence with a pass."""
    checks = {case: False for case in MANDATORY_CASES}
    issues = []
    refusals = refusal(identity)
    checks["qualification-refusal"] = True
    try:
        if (
            record["errors"]
            or record["execution_allowed"] is not False
            or record["native_start_allowed"] is not False
        ):
            raise ValueError("run failed or claims authority")
        cleanup = record["cleanup"]
        if (
            not all(
                cleanup[k] is True
                for k in (
                    "loop_detached",
                    "candidate_loop_detached",
                    "anonymous_ring_empty",
                    "owned_files_absent",
                )
            )
            or len(cleanup["unmounts"]) != 4
            or not all(x["unmounted"] is True for x in cleanup["unmounts"])
        ):
            raise ValueError("cleanup unverified")
        if (
            record["aggregate_controls"] != AGGREGATE
            or record["worker_controls"] != [CONTROLS]
            or record["worker_seconds"] > 5
            or record["supervisor_stop_after_verified_work"] is not True
        ):
            raise ValueError("worker or aggregate bounds unverified")
        negative = record["tool_negative_observations"]
        roles = [
            negative,
            negative["child"],
            negative["child"]["grandchild"],
            negative["setsid_child"],
        ]
        unchanged = (
            record["excluded_before"] == record["excluded_after"]
            and len(record["excluded_before"]) == 6
        )

        def denied(names):
            return all(
                role["filesystem"][name]["denied"] is True for role in roles for name in names
            )

        checks["allowed-grant"] = (
            negative["input"] == "read-only synthetic input"
            and record["candidate_oracles"]
            == {"existing": "modified-owned", "new-owned": "new-owned"}
            and denied(["readonly_write"])
        )
        checks["external-read"] = denied(["outside_read"])
        checks["external-write"] = unchanged and denied(["outside_write"])
        checks["original-checkout"] = unchanged and denied(
            ["dirty_read", "dirty_write", "git_read", "git_write"]
        )
        checks["coordinator-state"] = unchanged and denied(
            ["database_read", "database_write", "artifact_read", "artifact_write"]
        )
        checks["symlink-escape"] = denied(
            [
                "absolute_link_read",
                "absolute_link_write",
                "relative_link_read",
                "relative_link_write",
            ]
        )
        checks["new-file-escape"] = unchanged and denied(
            [
                "new_" + path
                for path in (
                    "/candidate/owned/absolute-parent/new",
                    "/candidate/owned/relative-parent/new",
                    "/candidate/owned/../new",
                    "/outside/new",
                    "/original/new",
                    "/coordinator/new",
                    "/input/new",
                )
            ]
        )
        checks["metadata-escape"] = unchanged and denied(
            [
                name + "_" + op
                for name in ("outside", "dirty", "git", "database", "artifact", "readonly")
                for op in ("chmod", "unlink", "rename", "link")
            ]
        )
        caller_denied = all(
            isinstance(role["denied"][key], dict)
            and isinstance(role["denied"][key].get("errno"), int)
            and role["denied"][key]["errno"] > 0
            for role in roles
            for key in (
                "token",
                "native_fd",
                "host_home",
                "host_root",
                "coordinator",
                "tcp_8080",
                "tcp_8081",
                "tcp_8082",
                "udp",
                "dns",
                "ipv6",
                "memfd",
            )
        )
        isolated = all(
            role["uid"] == 65534
            and "crewshal-native-tool-v1" in role["label"]
            and role["status"]["NoNewPrivs"] == "1"
            and all(
                int(role["status"][k], 16) == 0 for k in ("CapEff", "CapPrm", "CapAmb", "CapBnd")
            )
            and role["denied"]["userns"]["return"] == -1
            for role in roles
        )
        checks["descendant-escape"] = (
            caller_denied
            and isolated
            and all(all(x["denied"] is True for x in role["filesystem"].values()) for role in roles)
        )
        checks["environment-credentials"] = (
            isolated
            and caller_denied
            and all(
                not any(
                    k in role["environment"]
                    for k in ("SSH_AUTH_SOCK", "OPENAI_API_KEY", "SYNTHETIC_PARENT_SECRET")
                )
                for role in roles
            )
        )
        checks["network-egress"] = (
            caller_denied
            and record["nonallowed_sink_observations"] == []
            and record["datagram_sink_observations"] == []
            and len(record["datagram_sink_positive_controls"]) == 3
            and all(x["bytes"] == 7 for x in record["datagram_sink_positive_controls"])
            and record["nonallowed_sink_positive_control"]
            == [{"path": "/positive-control", "bytes": 7}]
        )
        hooks = negative["hooks"]
        positive_hooks = hooks["positive"] == {
            role: {"exit": 0, "sentinel": "hook"} for role in ("repository", "global", "runtime")
        }
        ignored_hooks = hooks["negative"] == {
            "effective_hooks_path": "command line:\t/dev/null",
            "hook_exit": 0,
            "sentinels_absent": True,
        }
        checks["repository-hooks"] = positive_hooks and ignored_hooks
        checks["global-hooks"] = (
            positive_hooks
            and ignored_hooks
            and set(hooks["runtime_environment"])
            == {"BASH_ENV", "ENV", "PYTHONSTARTUP", "GIT_CONFIG", "GIT_CONFIG_SYSTEM"}
            and not any(hooks["runtime_environment"].values())
            and set(record["synthetic_parent_hook_environment"])
            == set(hooks["runtime_environment"])
        )
        checks["mcp-plugins-instructions"] = instruction_evidence(record, roles)
        for case in ("cancellation", "deadline"):
            stage = record[case]
            checks[case] = (
                stage["controls"] == [CONTROLS]
                and stage["observed_processes_absent"] is True
                and stage["heartbeat_stopped"] is True
                and stage["heartbeat_bytes"] > 0
                and stage["termination_verified_seconds"] <= 6
                and (
                    stage.get("cancel_requested_seconds", 6) < 5
                    if case == "cancellation"
                    else stage["exit"] != 0 and "Finished with result: timeout" in stage["stderr"]
                )
            )
        auth = record["provider_auth_observations"]
        checks["credential-mediation"] = (
            caller_denied
            and checks["network-egress"]
            and len(auth) >= 4
            and all(x["auth_matches"] is True and x["host"] == "127.0.0.1:8081" for x in auth)
            and record["transport_observations"]
            == [
                {"probe": p, "auth_matches": True, "host": "127.0.0.1:8081"}
                for p in ("headers", "redirect")
            ]
            and json.loads(record["native_transport_probe_output"])
            == [
                {"probe": "headers", "status": 200, "bytes": 2},
                {"probe": "redirect", "status": 500, "bytes": 0},
            ]
            and record["broker_controls"]
            == {**CONTROLS, "memory.max": "67108864", "pids.max": "16"}
            and bool(record["broker_roles"])
            and all(
                role["Uid"].split() == ["65533"] * 4
                and role["NoNewPrivs"] == "1"
                and all(int(role[k], 16) == 0 for k in ("CapEff", "CapPrm", "CapAmb", "CapBnd"))
                for role in record["broker_roles"]
            )
        )
        validator = record["validator"]
        validation = validator["observations"]
        checks["credential-free-validation"] = (
            validator["exit"] == 0
            and validator["controls"] == [CONTROLS]
            and validator["termination_verified_seconds"] <= 5
            and validator["observed_processes_absent"] is True
            and validator["frozen_candidate_unchanged"] is True
            and validator["separate_scratch"] is True
            and validation["uid"] == 65531
            and validation["candidate_read"] == "modified-owned"
            and validation["candidate_write"]["denied"] is True
            and validation["candidate_new"]["denied"] is True
            and all(
                isinstance(validation["denied"][k], dict) and validation["denied"][k]["errno"] > 0
                for k in ("token", "tcp_8080", "tcp_8081", "tcp_8082", "udp", "dns", "ipv6")
            )
            and not any(
                k in validation["environment"]
                for k in ("SSH_AUTH_SOCK", "OPENAI_API_KEY", "SYNTHETIC_PARENT_SECRET")
            )
        )
        checks["configuration-binding"] = binding_verified
        events = [json.loads(line) for line in record["stdout"].splitlines()]
        if not any(
            event.get("type") == "item.completed"
            and event.get("item", {}).get("type") == "command_execution"
            and event["item"].get("command")
            == "/bin/sh -c 'exec /bin/python3 -I -B /input/native-full-payload.py workload'"
            and event["item"].get("exit_code") == 0
            and event["item"].get("status") == "completed"
            for event in events
        ):
            raise ValueError("native command completion absent")
        if any(len(value.encode()) > 65536 for value in record["captured_streams"].values()):
            raise ValueError("captured stream exceeds original bound")
        if any(
            record["storage_peaks"][name][metric] > limit
            for name, limit in (("candidate", 16777216), ("scratch", 33554432))
            for metric in ("logical", "allocated")
        ):
            raise ValueError("independently observed storage exceeds original bound")
        if (
            record["native_boundary_stages_passed"] is not True
            or record["tiny_workflow_passed"] is not True
            or record["tiny_sha256"] != sha(b"tiny")
        ):
            raise ValueError("actual native tiny workflow unverified")
        if (
            not all(x["denied"] is True for x in negative["storage"].values())
            or record["deleted_open_observed"]["logical"] != 1048576
            or record["deleted_open_observed"]["links"] != 0
        ):
            raise ValueError("storage limits unverified")
    except (KeyError, TypeError, ValueError, IndexError) as error:
        issues.append(str(error))
        # Incomplete/malformed run evidence never becomes complete qualification.
        checks = {case: False for case in MANDATORY_CASES}
        checks["qualification-refusal"] = True
    return {
        "fixture": record.get("fixture"),
        "cases": [
            {"id": case, "status": "passed" if checks[case] else "unavailable"}
            for case in MANDATORY_CASES
        ],
        "issues": issues,
        "refusal": refusals,
        "execution_allowed": False,
        "runtime_verified": False,
    }


def readback(root, protocol_path, profile_path, manifest_path, freeze_path, record_paths):
    protocol, profile, manifest, freeze = [
        load(p) for p in (protocol_path, profile_path, manifest_path, freeze_path)
    ]
    if (
        sha(Path(protocol_path).read_bytes()) != PROTOCOL
        or profile["mandatory_cases"] != protocol["mandatory_cases"]
        or profile["original_grant"] != protocol["grant"]
        or profile["original_limits"] != protocol["limits"]
    ):
        raise ValueError("original protocol changed")
    if len(record_paths) != 2 or len({Path(p).resolve() for p in record_paths}) != 2:
        raise ValueError("exactly two separate records required")
    sources = {
        profile["source"]: profile["source_sha256"],
        profile["payload_source"]: profile["payload_source_sha256"],
        profile["fixture_source"]: profile["fixture_source_sha256"],
        **profile["additional_sources"],
    }
    for name, bound in sources.items():
        if sha((Path(root) / name).read_bytes()) != bound:
            raise ValueError("source changed: " + name)
    for module, path in (
        ("crewshal.qualification", "src/crewshal/qualification.py"),
        ("crewshal.model", "src/crewshal/model.py"),
        ("crewshal.contracts", "src/crewshal/contracts.py"),
    ):
        if sha(Path(sys.modules[module].__file__).read_bytes()) != sources[path]:
            raise ValueError("loaded product source differs: " + module)
    if manifest["bindings"].get("/run/crewshal-native-full-readback-v2.py") != sha(
        Path(__file__).read_bytes()
    ):
        raise ValueError("reader was not frozen before execution")
    if freeze["observer_sha256"] != sources[profile["freeze_source"]]:
        raise ValueError("freeze observer source mismatch")
    manifest_sha = sha(Path(manifest_path).read_bytes())
    if (
        freeze["manifest_sha256"] != manifest_sha
        or freeze["profile_sha256"] != sha(Path(profile_path).read_bytes())
        or freeze["original_protocol_sha256"] != PROTOCOL
        or freeze["aggregate_observed"] != AGGREGATE
        or freeze["stale_manifest_refusal"]["owned_inventory_unchanged"] is not True
        or freeze["stale_manifest_refusal"]["exit"] == 0
    ):
        raise ValueError("freeze mismatch")
    identity = QualificationIdentity(
        host_os="linux",
        host_kernel=manifest["kernel"],
        architecture=manifest["architecture"],
        substrate="direct-linux-bwrap-systemd-ecryptfs",
        substrate_version=canonical(manifest["bindings"]),
        image=canonical(manifest["readonly_root_snapshot"]),
        runtime="codex-rust-v0.160.1",
        toolchain=canonical(manifest["bindings"]),
        configuration=sha(Path(profile_path).read_bytes()),
        grant=canonical(protocol["grant"]),
        harness=profile["source_sha256"],
        manifest=manifest_sha,
        credential_design=canonical(profile["credential_design"]),
    )
    records = [load(p) for p in record_paths]
    if (
        [x["fixture"] for x in records] != [1, 2]
        or any(x["manifest_sha256"] != manifest_sha for x in records)
        or freeze["kernel"] != manifest["kernel"]
        or freeze["architecture"] != manifest["architecture"]
    ):
        raise ValueError("record/current identity mismatch")
    results = [check_run(x, identity, True) for x in records]
    return {
        "scope": "Independent diagnostics; excludes execution authority",
        "original_protocol_sha256": PROTOCOL,
        "profile_sha256": sha(Path(profile_path).read_bytes()),
        "manifest_sha256": manifest_sha,
        "record_sha256": [sha(Path(p).read_bytes()) for p in record_paths],
        "identity": identity.model_dump(),
        "runs": results,
        "all_twenty_twice_observed": all(
            c["status"] == "passed" for run in results for c in run["cases"]
        ),
        "runtime_verified": False,
        "execution_allowed": False,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("root", "protocol", "profile", "manifest", "freeze"):
        parser.add_argument("--" + name, required=True, type=Path)
    parser.add_argument("--record", action="append", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    result = readback(
        args.root, args.protocol, args.profile, args.manifest, args.freeze, args.record
    )
    with args.output.open("x") as stream:
        json.dump(result, stream, indent=2)
        stream.write("\n")
    print(
        json.dumps(
            {
                "all_twenty_twice_observed": result["all_twenty_twice_observed"],
                "runtime_verified": False,
                "execution_allowed": False,
            }
        )
    )


if __name__ == "__main__":
    main()
