#!/usr/bin/env python3
"""Validate Codex config and command-rule files."""

from __future__ import annotations

import argparse
import json
import re
import sys
import tomllib
from pathlib import Path


LEGACY_STATUS_LINE_ITEMS = {
    "context": "context-used or context-remaining",
    "current_dir": "current-dir",
    "git_branch": "git-branch",
}

REQUIRED_WORKSPACE_RULES = {
    ".git": "write",
    ".agents": "write",
    ".codex": "write",
    ".env*": "deny",
    "**/.env*": "deny",
}

REQUIRED_FORBIDDEN_COMMAND_EXAMPLES = (
    "rm -rf",
    "git reset --hard",
    "git clean -f",
    "git clean -fd",
    "git clean -fx",
    "git clean -fdx",
    "git push --force",
    "git push -f",
    "sudo",
    "chmod 777",
    "cat ~/.ssh",
    "cat .env",
    "cat *.env",
    "cat ~/.env",
    "type .env",
    "type *.env",
    "type ~/.env",
)


def emit(root: Path, errors: list[str], warnings: list[str]) -> int:
    status = "pass" if not errors else "fail"
    print(json.dumps({"check": "config", "root": str(root), "status": status, "errors": errors, "warnings": warnings}, indent=2, sort_keys=True))
    if errors:
        print(f"config: {len(errors)} validation failure(s)", file=sys.stderr)
        return 1
    print("config: pass")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    args = parser.parse_args()
    root = Path(args.root).resolve()
    errors: list[str] = []
    warnings: list[str] = []

    config = root / ".codex" / "config.toml"
    if config.exists():
        text = config.read_text(encoding="utf-8")
        try:
            data = tomllib.loads(text)
        except tomllib.TOMLDecodeError as exc:
            errors.append(f".codex/config.toml: invalid TOML: {exc}")
            data = {}
        if "prefix_rules" in text:
            errors.append(".codex/config.toml: prefix_rules belongs in .codex/rules/*.rules")
        if "sandbox_mode" in data and ("default_permissions" in data or "permissions" in data):
            errors.append(".codex/config.toml: do not mix sandbox_mode with permission profiles")
        if "notify" in data:
            errors.append(".codex/config.toml: project config must not set user-level notify")
        permissions = data.get("permissions")
        profile = permissions.get("game_studios") if isinstance(permissions, dict) else None
        filesystem = profile.get("filesystem") if isinstance(profile, dict) else None
        workspace_rules = filesystem.get(":workspace_roots") if isinstance(filesystem, dict) else None
        if not isinstance(workspace_rules, dict):
            errors.append(
                '.codex/config.toml: missing [permissions.game_studios.filesystem.":workspace_roots"]'
            )
        else:
            incorrect_workspace_rules = sorted(
                f"{path}={workspace_rules.get(path)!r} (expected {access!r})"
                for path, access in REQUIRED_WORKSPACE_RULES.items()
                if workspace_rules.get(path) != access
            )
            if incorrect_workspace_rules:
                errors.append(
                    ".codex/config.toml: incorrect game_studios workspace rule(s): "
                    + ", ".join(incorrect_workspace_rules)
                )
        tui = data.get("tui")
        if isinstance(tui, dict) and "status_line" in tui:
            status_line = tui["status_line"]
            if not isinstance(status_line, list):
                errors.append(".codex/config.toml: tui.status_line must be a list under [tui], not a table")
            else:
                for index, item in enumerate(status_line):
                    if not isinstance(item, str):
                        errors.append(f".codex/config.toml: tui.status_line[{index}] must be a string")
                        continue
                    if item in LEGACY_STATUS_LINE_ITEMS:
                        errors.append(
                            ".codex/config.toml: tui.status_line uses legacy item "
                            f"{item!r}; use {LEGACY_STATUS_LINE_ITEMS[item]!r}"
                        )
    else:
        warnings.append(".codex/config.toml not present yet")

    rules = root / ".codex" / "rules" / "settings.rules"
    rules_dir = root / ".codex" / "rules"
    if rules_dir.exists():
        for rule_file in sorted(p for p in rules_dir.iterdir() if p.is_file()):
            text = rule_file.read_text(encoding="utf-8", errors="ignore")
            rel = rule_file.relative_to(root)
            if rule_file.suffix != ".rules":
                errors.append(f"{rel}: .codex/rules is command-policy only; put authoring instructions in .codex/instructions/path-rules/")
            if "paths:" in text or "Path-Specific" in text or "Code Rules" in text:
                errors.append(f"{rel}: appears to contain path authoring prose; .codex/rules is command-policy only")
    if rules.exists():
        text = rules.read_text(encoding="utf-8")
        if "prefix_rules" in text:
            errors.append(".codex/rules/settings.rules: use prefix_rule syntax, not prefix_rules")
        if "match(" in text:
            errors.append(".codex/rules/settings.rules: match is a prefix_rule field, not a top-level function")
        if 'decision = "deny"' in text:
            errors.append('.codex/rules/settings.rules: use decision = "forbidden", not "deny"')
        if 'decision = "forbidden"' not in text:
            errors.append('.codex/rules/settings.rules: missing decision = "forbidden" for denied command policy')
        quoted_examples = set(re.findall(r'"([^"]*)"', text))
        missing_forbidden_examples = [
            example for example in REQUIRED_FORBIDDEN_COMMAND_EXAMPLES if example not in quoted_examples
        ]
        if missing_forbidden_examples:
            errors.append(
                ".codex/rules/settings.rules: missing parity-critical forbidden command coverage for "
                + ", ".join(missing_forbidden_examples)
            )
    else:
        warnings.append(".codex/rules/settings.rules not present yet")

    return emit(root, errors, warnings)


if __name__ == "__main__":
    raise SystemExit(main())
