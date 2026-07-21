#!/usr/bin/env python3
"""Headless smoke checks and explicit interactive-smoke status reporting."""

from __future__ import annotations

import argparse
import json
import re
import sys
import tomllib
from pathlib import Path

import validate_runtime as runtime
from validate_runtime import validate_agents, validate_forbidden_references, validate_skills


ROLE_NAME_RE = re.compile(r"^[a-z0-9][a-z0-9-]*$")


def load_jsonl(path: Path, label: str) -> tuple[list[dict[str, object]], list[str]]:
    records: list[dict[str, object]] = []
    errors: list[str] = []
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError as exc:
        return [], [f"could not read {label} {path}: {exc}"]
    for line_number, line in enumerate(lines, start=1):
        if not line.strip():
            continue
        try:
            record = json.loads(line)
        except json.JSONDecodeError as exc:
            errors.append(f"{label} {path}:{line_number}: invalid JSON: {exc}")
            continue
        if not isinstance(record, dict):
            errors.append(f"{label} {path}:{line_number}: record must be an object")
            continue
        records.append(record)
    if not records and not errors:
        errors.append(f"{label} {path}: no JSON records found")
    return records, errors


def parse_call_arguments(value: object) -> dict[str, object]:
    if isinstance(value, dict):
        return value
    if isinstance(value, str):
        try:
            parsed = json.loads(value)
        except json.JSONDecodeError:
            return {}
        return parsed if isinstance(parsed, dict) else {}
    return {}


def validate_role_activation_records(
    evidence: object,
    parent_records: object,
    child_records: object,
    hook_records: object,
    root: Path,
) -> list[str]:
    """Cross-check raw parent, child, hook, and role-profile evidence."""

    if not isinstance(evidence, dict):
        return ["role activation evidence must be a JSON object"]
    errors: list[str] = []
    surface = evidence.get("surface")
    requested_role = evidence.get("requested_role")
    task_name = evidence.get("task_name")
    if surface not in {"cli", "desktop"}:
        errors.append("role activation evidence surface must be cli or desktop")
    if not isinstance(requested_role, str) or not ROLE_NAME_RE.fullmatch(requested_role):
        errors.append("role activation evidence requested_role must be a safe role identifier")
        return errors
    if task_name is not None and (not isinstance(task_name, str) or not task_name.strip()):
        errors.append("role activation evidence task_name must be a non-empty string when provided")

    if not isinstance(parent_records, list) or not all(isinstance(row, dict) for row in parent_records):
        errors.append("parent session evidence must be a list of JSON objects")
        return errors
    if not isinstance(child_records, list) or not all(isinstance(row, dict) for row in child_records):
        errors.append("child session evidence must be a list of JSON objects")
        return errors
    if not isinstance(hook_records, list) or not all(isinstance(row, dict) for row in hook_records):
        errors.append("hook evidence must be a list of JSON objects")
        return errors

    role_path = root / ".codex" / "agents" / f"{requested_role}.toml"
    try:
        role_config = tomllib.loads(role_path.read_text(encoding="utf-8"))
    except (OSError, tomllib.TOMLDecodeError) as exc:
        errors.append(f"could not read authoritative role profile {role_path}: {exc}")
        return errors
    expected_model = role_config.get("model")
    expected_effort = role_config.get("model_reasoning_effort")
    instructions = role_config.get("developer_instructions")
    if not all(isinstance(value, str) and value.strip() for value in (expected_model, expected_effort, instructions)):
        errors.append(f"authoritative role profile {role_path} is missing model, effort, or instructions")
        return errors
    instruction_canary = next((line.strip() for line in instructions.splitlines() if line.strip()), "")

    parent_meta = next((row.get("payload") for row in parent_records if row.get("type") == "session_meta"), None)
    if not isinstance(parent_meta, dict) or not parent_meta.get("cli_version"):
        errors.append("parent session metadata is missing runtime version")
        parent_meta = {}

    current_context: dict[str, object] = {}
    spawn_candidates: list[tuple[dict[str, object], dict[str, object]]] = []
    started_events: list[dict[str, object]] = []
    for row in parent_records:
        payload = row.get("payload")
        if not isinstance(payload, dict):
            continue
        if row.get("type") == "turn_context":
            current_context = payload
        if row.get("type") == "response_item" and payload.get("type") == "function_call" and payload.get("name") == "spawn_agent":
            spawn_candidates.append((parse_call_arguments(payload.get("arguments")), current_context.copy()))
        if row.get("type") == "event_msg" and payload.get("type") == "sub_agent_activity" and payload.get("kind") == "started":
            started_events.append(payload)

    if task_name:
        spawn_candidates = [item for item in spawn_candidates if item[0].get("task_name") == task_name]
        started_events = [
            item for item in started_events if str(item.get("agent_path", "")).endswith(f"/{task_name}")
        ]
    if len(spawn_candidates) != 1:
        errors.append(f"expected exactly one matching spawn_agent call, found {len(spawn_candidates)}")
        spawn_args: dict[str, object] = {}
        parent_context: dict[str, object] = {}
    else:
        spawn_args, parent_context = spawn_candidates[0]
    if spawn_args.get("agent_type") != requested_role:
        errors.append("raw spawn call did not select the requested custom role")
    multi_agent_version = parent_context.get("multi_agent_version")
    if multi_agent_version not in {"v1", "v2"}:
        errors.append("parent turn context is missing a supported MultiAgent version")
    if multi_agent_version == "v2":
        if not task_name:
            errors.append("MultiAgent V2 evidence requires the recorded task_name")
        if spawn_args.get("fork_turns") != "none":
            errors.append('raw MultiAgent V2 spawn requires fork_turns "none"')
    if len(started_events) != 1:
        errors.append(f"expected exactly one matching subagent-start event, found {len(started_events)}")
        child_id = ""
    else:
        child_id = str(started_events[0].get("agent_thread_id", ""))
        if not child_id:
            errors.append("parent subagent-start event is missing the child thread id")

    child_meta = next((row.get("payload") for row in child_records if row.get("type") == "session_meta"), None)
    if not isinstance(child_meta, dict):
        errors.append("child session metadata is missing")
        child_meta = {}
    recorded_child_id = child_meta.get("id")
    if child_id and recorded_child_id != child_id:
        errors.append("child session id does not match the parent subagent-start event")
    if parent_meta.get("id") and child_meta.get("parent_thread_id") != parent_meta.get("id"):
        errors.append("child session parent id does not match the parent session")
    if parent_meta.get("cli_version") and child_meta.get("cli_version") != parent_meta.get("cli_version"):
        errors.append("parent and child runtime versions do not match")
    spawn_meta = child_meta.get("source", {})
    if isinstance(spawn_meta, dict):
        spawn_meta = spawn_meta.get("subagent", {})
    if isinstance(spawn_meta, dict):
        spawn_meta = spawn_meta.get("thread_spawn", {})
    observed_role = spawn_meta.get("agent_role") if isinstance(spawn_meta, dict) else None
    if observed_role != requested_role:
        errors.append("child session metadata does not identify the requested role")

    child_context = next((row.get("payload") for row in child_records if row.get("type") == "turn_context"), None)
    if not isinstance(child_context, dict):
        errors.append("child turn context is missing")
        child_context = {}
    if child_context.get("model") != expected_model:
        errors.append("child model does not match the authoritative role profile")
    if child_context.get("effort") != expected_effort:
        errors.append("child reasoning effort does not match the authoritative role profile")

    matching_hooks = [
        row
        for row in hook_records
        if row.get("hook_event_name") == "SubagentStart" and row.get("agent_id") == recorded_child_id
    ]
    if len(matching_hooks) != 1:
        errors.append(f"expected exactly one matching SubagentStart hook record, found {len(matching_hooks)}")
    else:
        hook = matching_hooks[0]
        if hook.get("agent_type") != requested_role:
            errors.append("SubagentStart hook did not identify the requested role")
        if hook.get("model") != expected_model:
            errors.append("SubagentStart hook model does not match the authoritative role profile")

    developer_texts: list[str] = []
    for row in child_records:
        payload = row.get("payload")
        if not isinstance(payload, dict) or row.get("type") != "response_item":
            continue
        if payload.get("type") != "message" or payload.get("role") != "developer":
            continue
        content = payload.get("content")
        if not isinstance(content, list):
            continue
        for item in content:
            if isinstance(item, dict) and isinstance(item.get("text"), str):
                developer_texts.append(item["text"])
    if not any(instruction_canary in text for text in developer_texts):
        errors.append("child developer messages do not contain the authoritative role instructions")

    return errors


def validate_role_activation_evidence(evidence: object, root: Path, evidence_path: Path) -> list[str]:
    """Load and validate raw role-activation records named by an evidence file."""

    if not isinstance(evidence, dict):
        return ["role activation evidence must be a JSON object"]
    records: dict[str, list[dict[str, object]]] = {}
    errors: list[str] = []
    for field, label in (
        ("parent_session_log", "parent session log"),
        ("child_session_log", "child session log"),
        ("hook_log", "SubagentStart hook log"),
    ):
        value = evidence.get(field)
        if not isinstance(value, str) or not value.strip():
            errors.append(f"role activation evidence missing non-empty {field}")
            continue
        path = Path(value).expanduser()
        if not path.is_absolute():
            path = evidence_path.parent / path
        loaded, load_errors = load_jsonl(path.resolve(), label)
        records[field] = loaded
        errors.extend(load_errors)
    if errors:
        return errors
    return validate_role_activation_records(
        evidence,
        records["parent_session_log"],
        records["child_session_log"],
        records["hook_log"],
        root,
    )


def validate_role_activation_fixtures(fixtures: Path) -> list[str]:
    path = fixtures / "role-activation-evidence.json"
    if not path.exists():
        return [f"missing role activation fixture {path}"]
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return [f"invalid role activation fixture {path}: {exc}"]

    cases = payload.get("cases") if isinstance(payload, dict) else None
    if not isinstance(cases, list) or not cases:
        return ["role activation fixture must contain a non-empty cases list"]

    errors: list[str] = []
    for index, case in enumerate(cases):
        if not isinstance(case, dict):
            errors.append(f"role activation fixture case {index} must be an object")
            continue
        name = case.get("name", f"case-{index}")
        expectation = case.get("expect")
        failures = validate_role_activation_records(
            case.get("evidence"),
            case.get("parent_records"),
            case.get("child_records"),
            case.get("hook_records"),
            fixtures.parents[2],
        )
        if expectation == "pass" and failures:
            errors.append(f"role activation fixture {name} unexpectedly failed: {'; '.join(failures)}")
        elif expectation == "fail" and not failures:
            errors.append(f"role activation fixture {name} unexpectedly passed")
        elif expectation not in {"pass", "fail"}:
            errors.append(f"role activation fixture {name} has invalid expectation {expectation!r}")
        for fragment in case.get("expected_errors", []):
            if not any(fragment in failure for failure in failures):
                errors.append(
                    f"role activation fixture {name} did not report expected error fragment: {fragment}"
                )
    return errors


def validate_role_delegation_contract(root: Path) -> list[str]:
    required = {
        root / "AGENTS.md": (
            'fork_turns: "none"',
            "A task name, agent path, nickname",
            "mismatched configured",
            "do not simulate the specialist verdict",
        ),
        root / ".codex" / "docs" / "director-gates.md": (
            'fork_turns: "none"',
            "task name, agent path, nickname",
            "configured model and reasoning effort",
            "mark the gate blocked",
        ),
    }
    errors: list[str] = []
    for path, phrases in required.items():
        if not path.exists():
            errors.append(f"missing role delegation contract {path.relative_to(root)}")
            continue
        text = path.read_text(encoding="utf-8")
        for phrase in phrases:
            if phrase not in text:
                errors.append(
                    f"{path.relative_to(root)}: missing role delegation contract phrase {phrase!r}"
                )
    return errors


def emit(
    mode: str,
    root: Path,
    errors: list[str],
    warnings: list[str] | None = None,
    status_override: str | None = None,
) -> int:
    warnings = warnings or []
    status = "fail" if errors else (status_override or "pass")
    print(json.dumps({"check": f"smoke-{mode}", "root": str(root), "status": status, "errors": errors, "warnings": warnings}, indent=2, sort_keys=True))
    if errors:
        print(f"smoke-{mode}: {len(errors)} validation failure(s)", file=sys.stderr)
        return 1
    print(f"smoke-{mode}: {status}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=["headless", "interactive"])
    parser.add_argument("--root", default=".")
    parser.add_argument("--evidence", help="recorded custom-role activation evidence JSON")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    if args.mode == "interactive":
        if args.evidence:
            evidence_path = Path(args.evidence).expanduser().resolve()
            try:
                evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError) as exc:
                return emit("interactive", root, [f"could not read role activation evidence: {exc}"])
            return emit(
                "interactive",
                root,
                validate_role_activation_evidence(evidence, root, evidence_path),
            )
        return emit(
            "interactive",
            root,
            [],
            ["interactive smoke requires a separately recorded trusted session with auth/model access"],
            status_override="skipped",
        )

    fixtures = root / ".codex" / "tests" / "fixtures"
    errors = validate_role_activation_fixtures(fixtures)
    errors.extend(validate_role_delegation_contract(root))
    expected_bad = {
        "invalid-skill": (lambda p: validate_skills(p, require_present=True), ()),
        "invalid-agent": (lambda p: validate_agents(p, require_present=True), ()),
        "stale-claude-reference": (validate_forbidden_references, ()),
        "invalid-resume-contract": (
            lambda p: getattr(runtime, "validate_resume_contract", lambda _: [])(p),
            (
                "unbounded default slice read",
                "automatic lane startup",
                "cache readback contract",
            ),
        ),
        "invalid-handoff-contract": (
            lambda p: getattr(runtime, "validate_handoff_review_contract", lambda _: [])(p),
            (
                "explicit invocation boundary",
                "context capacity gate",
                "review scope baseline contract",
                "fresh-context reviewer contract",
                "compact resume-index contract",
                "same-session reviewer substitution",
                "full-history reviewer fork",
                "silent reviewer fallback",
            ),
        ),
        "invalid-gen-asset-contract": (
            lambda p: getattr(runtime, "validate_gen_asset_contract", lambda _: [])(p),
            (
                "nested Codex CLI generation command",
                "legacy Codex skill path",
                "Claude runtime path",
                "API-key fallback",
                "unbounded newest-image fallback",
            ),
        ),
        "invalid-gen-asset-profile": (
            lambda p: getattr(runtime, "validate_gen_asset_profile", lambda _: [])(
                p / "profiles" / "building.md"
            ),
            ("ACTIVE profile missing",),
        ),
    }
    for name, (check, expected_fragments) in expected_bad.items():
        fixture = fixtures / name
        if not fixture.exists():
            errors.append(f"missing negative fixture {fixture.relative_to(root)}")
            continue
        failures = check(fixture)
        if not failures:
            errors.append(f"negative fixture {name} unexpectedly passed")
            continue
        for fragment in expected_fragments:
            if not any(fragment in failure for failure in failures):
                errors.append(
                    f"negative fixture {name} did not report expected failure fragment: {fragment}"
                )

    expected_good = {
        "valid-gen-asset-stub": lambda p: getattr(
            runtime,
            "validate_gen_asset_profile",
            lambda _: ["gen-asset profile validator unavailable"],
        )(p / "profiles" / "icon.md"),
    }
    for name, check in expected_good.items():
        fixture = fixtures / name
        if not fixture.exists():
            errors.append(f"missing positive fixture {fixture.relative_to(root)}")
            continue
        failures = check(fixture)
        if failures:
            errors.append(f"positive fixture {name} failed: {'; '.join(failures)}")

    return emit("headless", root, errors)


if __name__ == "__main__":
    raise SystemExit(main())
