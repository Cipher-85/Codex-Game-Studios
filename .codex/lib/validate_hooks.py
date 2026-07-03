#!/usr/bin/env python3
"""Validate Codex hook configuration and fixture payload shape."""

from __future__ import annotations

import argparse
import json
import re
import sys
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
    else:
        warnings.append(".codex/hooks.json not present yet")

    hook_lib = root / ".codex" / "lib" / "hooks.sh"
    if hook_lib.exists():
        text = hook_lib.read_text(encoding="utf-8")
        if '"decision"' in text or "'decision'" in text:
            errors.append(".codex/lib/hooks.sh: hook helpers must not emit decision/message JSON on stdout")
        if "exit 2" not in text:
            errors.append(".codex/lib/hooks.sh: ccgs_hook_deny must exit 2 so PreToolUse blocks correctly")
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

    return emit(root, errors, warnings)


if __name__ == "__main__":
    raise SystemExit(main())
