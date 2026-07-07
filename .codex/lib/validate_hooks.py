#!/usr/bin/env python3
"""Validate Codex hook configuration and fixture payload shape."""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path


ALLOWED_EVENTS = {
    "PreToolUse",
    "PermissionRequest",
    "PostToolUse",
    "PreCompact",
    "PostCompact",
    "SessionStart",
    "SubagentStart",
    "SubagentStop",
    "UserPromptSubmit",
    "Stop",
}


def emit(root: Path, errors: list[str], warnings: list[str]) -> int:
    status = "pass" if not errors else "fail"
    print(json.dumps({"check": "hooks", "root": str(root), "status": status, "errors": errors, "warnings": warnings}, indent=2, sort_keys=True))
    if errors:
        print(f"hooks: {len(errors)} validation failure(s)", file=sys.stderr)
        return 1
    print("hooks: pass")
    return 0


def load_payload(fixtures: Path, name: str) -> str:
    return (fixtures / name).read_text(encoding="utf-8")


def run_hook(root: Path, tmp_root: Path, script_name: str, payload: str) -> subprocess.CompletedProcess[str]:
    script = root / ".codex" / "hooks" / script_name
    env = os.environ.copy()
    env["CCGS_ROOT"] = str(tmp_root)
    return subprocess.run(
        [str(script)],
        input=payload,
        text=True,
        capture_output=True,
        cwd=tmp_root,
        env=env,
        check=False,
    )


def run_payload_paths(root: Path, tmp_root: Path, payload: str) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env["CCGS_ROOT"] = str(tmp_root)
    env["CCGS_REPO_ROOT"] = str(root)
    return subprocess.run(
        ["bash", "-lc", 'source "$CCGS_REPO_ROOT/.codex/lib/hooks.sh"; payload="$(cat)"; ccgs_payload_paths "$payload"'],
        input=payload,
        text=True,
        capture_output=True,
        cwd=tmp_root,
        env=env,
        check=False,
    )


def git_init(tmp_root: Path) -> None:
    subprocess.run(["git", "-C", str(tmp_root), "init", "-q"], check=True, capture_output=True, text=True)


def make_temp_project() -> tempfile.TemporaryDirectory[str]:
    return tempfile.TemporaryDirectory(prefix="ccgs-hook-fixture-")


def assert_result(
    errors: list[str],
    label: str,
    result: subprocess.CompletedProcess[str],
    expected_code: int,
    stdout_contains: str | None = None,
    stderr_contains: str | None = None,
    stderr_absent: str | None = None,
) -> None:
    if result.returncode != expected_code:
        errors.append(
            f"{label}: expected exit {expected_code}, got {result.returncode}; stdout={result.stdout!r}; stderr={result.stderr!r}"
        )
        return
    if stdout_contains and stdout_contains not in result.stdout:
        errors.append(f"{label}: stdout missing {stdout_contains!r}; stdout={result.stdout!r}")
    if stderr_contains and stderr_contains not in result.stderr:
        errors.append(f"{label}: stderr missing {stderr_contains!r}; stderr={result.stderr!r}")
    if stderr_absent and stderr_absent in result.stderr:
        errors.append(f"{label}: stderr unexpectedly contained {stderr_absent!r}; stderr={result.stderr!r}")


def run_behavioral_fixtures(root: Path, fixtures: Path, errors: list[str], warnings: list[str]) -> None:
    required = [
        "session-start.json",
        "pre-tool-use-bash-unrelated-push-text.json",
        "pre-tool-use-bash-push-develop.json",
        "pre-tool-use-bash-push-main.json",
        "pre-tool-use-bash-push-master.json",
        "pre-tool-use-bash-commit.json",
        "pre-tool-use-bash-env-safe.json",
        "pre-tool-use-bash-env-read.json",
        "pre-tool-use-bash-env-redirection.json",
        "post-tool-use-apply-patch-assets-naming.json",
        "post-tool-use-apply-patch-assets-invalid-json.json",
        "post-tool-use-apply-patch-skill.json",
        "post-tool-use-apply-patch-legacy-patch.json",
        "pre-compact.json",
        "post-compact.json",
        "subagent-start.json",
        "subagent-stop.json",
        "stop.json",
    ]
    missing = [name for name in required if not (fixtures / name).exists()]
    if missing:
        errors.append("hook fixtures missing: " + ", ".join(missing))
        return

    try:
        subprocess.run(["git", "--version"], check=True, capture_output=True, text=True)
    except (OSError, subprocess.CalledProcessError) as exc:
        warnings.append(f"git unavailable; skipped behavioral hook fixtures: {exc}")
        return

    with make_temp_project() as tmp:
        tmp_root = Path(tmp)
        result = run_payload_paths(root, tmp_root, load_payload(fixtures, "post-tool-use-apply-patch-assets-invalid-json.json"))
        assert_result(errors, "ccgs_payload_paths command field", result, 0, stdout_contains="assets/data/bad.json")
        result = run_payload_paths(root, tmp_root, load_payload(fixtures, "post-tool-use-apply-patch-legacy-patch.json"))
        assert_result(errors, "ccgs_payload_paths legacy patch field", result, 0, stdout_contains="assets/data/legacy.json")

    with make_temp_project() as tmp:
        tmp_root = Path(tmp)
        git_init(tmp_root)
        result = run_hook(root, tmp_root, "validate-push.sh", load_payload(fixtures, "pre-tool-use-bash-unrelated-push-text.json"))
        assert_result(errors, "validate-push unrelated text", result, 0, stderr_absent="Push to protected branch")

    with make_temp_project() as tmp:
        tmp_root = Path(tmp)
        result = run_hook(root, tmp_root, "validate-secrets.sh", load_payload(fixtures, "pre-tool-use-bash-env-safe.json"))
        assert_result(errors, "validate-secrets safe env command", result, 0, stderr_absent="BLOCKED:")

    for fixture_name, label in (
        ("pre-tool-use-bash-env-read.json", "validate-secrets env read"),
        ("pre-tool-use-bash-env-redirection.json", "validate-secrets env redirection"),
    ):
        with make_temp_project() as tmp:
            tmp_root = Path(tmp)
            result = run_hook(root, tmp_root, "validate-secrets.sh", load_payload(fixtures, fixture_name))
            assert_result(
                errors,
                label,
                result,
                2,
                stderr_contains="BLOCKED: Bash command attempts to read or write .env secret files",
            )

    for branch in ("develop", "main", "master"):
        with make_temp_project() as tmp:
            tmp_root = Path(tmp)
            git_init(tmp_root)
            result = run_hook(root, tmp_root, "validate-push.sh", load_payload(fixtures, f"pre-tool-use-bash-push-{branch}.json"))
            assert_result(errors, f"validate-push {branch}", result, 0, stderr_contains=f"protected branch '{branch}'")

    with make_temp_project() as tmp:
        tmp_root = Path(tmp)
        git_init(tmp_root)
        data_file = tmp_root / "assets" / "data" / "bad.json"
        data_file.parent.mkdir(parents=True, exist_ok=True)
        data_file.write_text("{bad json", encoding="utf-8")
        subprocess.run(["git", "-C", str(tmp_root), "add", "assets/data/bad.json"], check=True, capture_output=True, text=True)
        result = run_hook(root, tmp_root, "validate-commit.sh", load_payload(fixtures, "pre-tool-use-bash-commit.json"))
        assert_result(errors, "validate-commit invalid staged JSON", result, 2, stderr_contains="BLOCKED: assets/data/bad.json is not valid JSON")

    with make_temp_project() as tmp:
        tmp_root = Path(tmp)
        asset_file = tmp_root / "assets" / "Bad-Asset.json"
        asset_file.parent.mkdir(parents=True, exist_ok=True)
        asset_file.write_text("{}\n", encoding="utf-8")
        result = run_hook(root, tmp_root, "validate-assets.sh", load_payload(fixtures, "post-tool-use-apply-patch-assets-naming.json"))
        assert_result(errors, "validate-assets naming advisory", result, 0, stderr_contains="Asset Validation: Warnings")

    with make_temp_project() as tmp:
        tmp_root = Path(tmp)
        data_file = tmp_root / "assets" / "data" / "bad.json"
        data_file.parent.mkdir(parents=True, exist_ok=True)
        data_file.write_text("{bad json", encoding="utf-8")
        result = run_hook(root, tmp_root, "validate-assets.sh", load_payload(fixtures, "post-tool-use-apply-patch-assets-invalid-json.json"))
        assert_result(errors, "validate-assets invalid JSON", result, 2, stderr_contains="Asset Validation: ERRORS")

    with make_temp_project() as tmp:
        tmp_root = Path(tmp)
        skill_file = tmp_root / ".agents" / "skills" / "example-skill" / "SKILL.md"
        skill_file.parent.mkdir(parents=True, exist_ok=True)
        skill_file.write_text("---\nname: example-skill\ndescription: test\n---\n", encoding="utf-8")
        result = run_hook(root, tmp_root, "validate-skill-change.sh", load_payload(fixtures, "post-tool-use-apply-patch-skill.json"))
        assert_result(errors, "validate-skill-change advisory", result, 0, stderr_contains="$skill-test static example-skill")

    with make_temp_project() as tmp:
        tmp_root = Path(tmp)
        git_init(tmp_root)
        active = tmp_root / "production" / "session-state" / "active.md"
        active.parent.mkdir(parents=True, exist_ok=True)
        active.write_text("# Active\nCurrent task fixture\n", encoding="utf-8")
        src_keep = tmp_root / "src" / ".gitkeep"
        src_keep.parent.mkdir(parents=True, exist_ok=True)
        src_keep.write_text("", encoding="utf-8")
        result = run_hook(root, tmp_root, "session-start.sh", load_payload(fixtures, "session-start.json"))
        assert_result(errors, "session-start visible context", result, 0, stdout_contains="ACTIVE SESSION STATE DETECTED")

    with make_temp_project() as tmp:
        tmp_root = Path(tmp)
        result = run_hook(root, tmp_root, "detect-gaps.sh", load_payload(fixtures, "session-start.json"))
        assert_result(errors, "detect-gaps fresh project", result, 0, stdout_contains="$start")
        if "$project-stage-detect" not in result.stdout:
            errors.append(f"detect-gaps fresh project: stdout missing '$project-stage-detect'; stdout={result.stdout!r}")

    with make_temp_project() as tmp:
        tmp_root = Path(tmp)
        git_init(tmp_root)
        active = tmp_root / "production" / "session-state" / "active.md"
        active.parent.mkdir(parents=True, exist_ok=True)
        active.write_text("# Active\nCurrent task fixture\n", encoding="utf-8")
        result = run_hook(root, tmp_root, "pre-compact.sh", load_payload(fixtures, "pre-compact.json"))
        assert_result(errors, "pre-compact visible recovery", result, 0, stdout_contains="SESSION STATE BEFORE COMPACTION")
        result = run_hook(root, tmp_root, "post-compact.sh", load_payload(fixtures, "post-compact.json"))
        assert_result(errors, "post-compact visible recovery", result, 0, stdout_contains="Context Restored After Compaction")

    with make_temp_project() as tmp:
        tmp_root = Path(tmp)
        result = run_hook(root, tmp_root, "log-agent.sh", load_payload(fixtures, "subagent-start.json"))
        assert_result(errors, "log-agent start", result, 0)
        result = run_hook(root, tmp_root, "log-agent-stop.sh", load_payload(fixtures, "subagent-stop.json"))
        assert_result(errors, "log-agent stop", result, 0)
        audit_log = tmp_root / "production" / "session-logs" / "agent-audit.log"
        text = audit_log.read_text(encoding="utf-8") if audit_log.exists() else ""
        if "Agent invoked: technical-director" not in text or "Agent completed: technical-director" not in text:
            errors.append(f"agent audit log missing expected human-readable entries: {text!r}")

    with make_temp_project() as tmp:
        tmp_root = Path(tmp)
        git_init(tmp_root)
        active = tmp_root / "production" / "session-state" / "active.md"
        active.parent.mkdir(parents=True, exist_ok=True)
        active.write_text("# Active\nCurrent task fixture\n", encoding="utf-8")
        result = run_hook(root, tmp_root, "session-stop.sh", load_payload(fixtures, "stop.json"))
        assert_result(errors, "session-stop archive", result, 0)
        session_log = tmp_root / "production" / "session-logs" / "session-log.md"
        text = session_log.read_text(encoding="utf-8") if session_log.exists() else ""
        if "Archived Session State" not in text:
            errors.append(f"session-stop did not archive active session state: {text!r}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    args = parser.parse_args()
    root = Path(args.root).resolve()
    errors: list[str] = []
    warnings: list[str] = []

    hooks_json = root / ".codex" / "hooks.json"
    if hooks_json.exists():
        try:
            data = json.loads(hooks_json.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            return emit(root, [f".codex/hooks.json: invalid JSON: {exc}"], warnings)
        if not isinstance(data, dict):
            errors.append(".codex/hooks.json: expected object")
        elif "hooks" not in data:
            top_level_events = sorted(set(data.keys()) & ALLOWED_EVENTS)
            if top_level_events:
                errors.append(".codex/hooks.json: Codex requires a top-level hooks object; found top-level events " + ", ".join(top_level_events))
            else:
                errors.append(".codex/hooks.json: missing top-level hooks object")
        elif not isinstance(data.get("hooks"), dict):
            errors.append(".codex/hooks.json: hooks must be an object")
        else:
            for event, entries in data["hooks"].items():
                if event == "Notification":
                    errors.append(".codex/hooks.json: Notification event is not supported")
                if event not in ALLOWED_EVENTS:
                    errors.append(f".codex/hooks.json: unsupported event {event}")
                if not isinstance(entries, list):
                    errors.append(f".codex/hooks.json: {event} must be a list")
                    continue
                for group_index, group in enumerate(entries):
                    handlers = group.get("hooks") if isinstance(group, dict) else None
                    if not isinstance(handlers, list):
                        errors.append(f".codex/hooks.json: {event}[{group_index}] missing hooks list")
                        continue
                    for hook_index, hook in enumerate(handlers):
                        if not isinstance(hook, dict):
                            errors.append(f".codex/hooks.json: {event}[{group_index}].hooks[{hook_index}] must be an object")
                            continue
                        if hook.get("type") != "command":
                            errors.append(f".codex/hooks.json: {event}[{group_index}].hooks[{hook_index}] must set type = command")
                        command = hook.get("command")
                        if not command:
                            errors.append(f".codex/hooks.json: {event}[{group_index}].hooks[{hook_index}] missing command")
                            continue
                        if ".claude/" in command:
                            errors.append(f".codex/hooks.json: {event}[{group_index}].hooks[{hook_index}] references .claude")
                        if command.startswith(".codex/hooks/"):
                            errors.append(
                                f".codex/hooks.json: {event}[{group_index}].hooks[{hook_index}] uses current-directory-sensitive command {command}"
                            )
                            script = root / command
                            if not script.exists():
                                errors.append(f".codex/hooks.json: missing script {command}")
                        if ".codex/hooks/" in command and "CCGS_ROOT=" not in command:
                            errors.append(
                                f".codex/hooks.json: {event}[{group_index}].hooks[{hook_index}] must set CCGS_ROOT when dispatching hooks"
                            )
                        script_names = set(re.findall(r"\.codex/hooks/([A-Za-z0-9_.-]+\.sh)", command))
                        script_names.update(re.findall(r"\bn=([A-Za-z0-9_.-]+\.sh)\b", command))
                        for script_name in sorted(script_names):
                            script = root / ".codex" / "hooks" / script_name
                            if not script.exists():
                                errors.append(f".codex/hooks.json: missing script .codex/hooks/{script_name}")
                            elif not os.access(script, os.X_OK):
                                errors.append(f".codex/hooks.json: script is not executable .codex/hooks/{script_name}")
    else:
        warnings.append(".codex/hooks.json not present yet")

    hook_lib = root / ".codex" / "lib" / "hooks.sh"
    if hook_lib.exists():
        text = hook_lib.read_text(encoding="utf-8")
        if '"decision"' in text or "'decision'" in text:
            errors.append(".codex/lib/hooks.sh: hook helpers must not emit decision/message JSON on stdout")
        if "exit 2" not in text:
            errors.append(".codex/lib/hooks.sh: ccgs_hook_deny must exit 2 so PreToolUse blocks correctly")
        if ">&2" not in text:
            errors.append(".codex/lib/hooks.sh: hook warnings/denials must emit visible stderr")
    else:
        warnings.append(".codex/lib/hooks.sh not present yet")

    fixtures = root / ".codex" / "tests" / "fixtures" / "hook-payloads"
    if fixtures.exists():
        for payload in sorted(fixtures.glob("*.json")):
            try:
                data = json.loads(payload.read_text(encoding="utf-8"))
            except json.JSONDecodeError as exc:
                errors.append(f"{payload.relative_to(root)}: invalid JSON: {exc}")
                continue
            event = data.get("hook_event_name")
            if event and event not in ALLOWED_EVENTS:
                errors.append(f"{payload.relative_to(root)}: unsupported hook_event_name {event}")
        if not errors:
            run_behavioral_fixtures(root, fixtures, errors, warnings)

    return emit(root, errors, warnings)


if __name__ == "__main__":
    raise SystemExit(main())
