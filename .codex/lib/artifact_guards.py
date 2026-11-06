#!/usr/bin/env python3
"""Read-only warnings for supported apply_patch payloads; never grant or deny writes."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import sys

sys.dont_write_bytecode = True
from artifact_facts import MAX_BYTES, REGISTRIES, registry_records


def relative_path(root, name):
    """Reject escapes, secret paths and links before looking at target content."""
    path = Path(name)
    if path.is_absolute():
        try:
            path = path.relative_to(root)
        except ValueError as error:
            raise ValueError("path outside project") from error
    if not path.parts or any(p == ".." or p.startswith(".env") for p in path.parts):
        raise ValueError("unsafe or secret patch path")
    current = root
    for part in path.parts:
        current /= part
        if current.is_symlink():
            raise ValueError("symlink patch path")
    return path.as_posix()


def protected(path):
    return (Path(path).name in ("EPIC.md", "project.godot") or
            path.startswith("docs/engine-reference/"))


def updated_text(before, body):
    """Replay unambiguous literal hunks only; unknown syntax gets a warning."""
    lines, cursor, output = before.splitlines(), 0, []
    hunks, old, new = [], [], []
    for line in body:
        if line.startswith("@@"):
            if old or new:
                hunks.append((old, new))
            old, new = [], []
        elif line == "*** End of File":
            continue
        elif line.startswith(" "):
            old.append(line[1:]); new.append(line[1:])
        elif line.startswith("-"):
            old.append(line[1:])
        elif line.startswith("+"):
            new.append(line[1:])
        else:
            raise ValueError("unsupported patch hunk syntax")
    if old or new:
        hunks.append((old, new))
    if not hunks:
        raise ValueError("empty update patch")
    for old, new in hunks:
        if not old:
            raise ValueError("context-free insertion cannot be assessed")
        matches = [i for i in range(cursor, len(lines) - len(old) + 1)
                   if lines[i:i + len(old)] == old]
        if len(matches) != 1:
            raise ValueError("patch context is absent or ambiguous")
        at = matches[0]
        output.extend(lines[cursor:at]); output.extend(new)
        cursor = at + len(old)
    output.extend(lines[cursor:])
    return "\n".join(output) + ("\n" if before.endswith("\n") else "")


def inspect_patch(root, payload):
    """Return observations and limitations without modifying any project file."""
    root = Path(root).resolve()
    warnings, checked = [], []
    try:
        if not isinstance(payload, dict) or payload.get("tool_name") != "apply_patch":
            raise ValueError("unsupported tool payload; only apply_patch is assessed")
        arguments = payload.get("tool_input")
        patch = (arguments.get("patch") or arguments.get("command") or arguments.get("input")) if isinstance(arguments, dict) else arguments
        if not isinstance(patch, str) or len(patch.encode()) > MAX_BYTES:
            raise ValueError("missing or oversized patch text")
        lines = patch.splitlines()
        if not lines or lines[0] != "*** Begin Patch" or lines[-1] != "*** End Patch":
            raise ValueError("unsupported patch envelope")
        entries, current = [], None
        for line in lines[1:-1]:
            match = re.fullmatch(r"\*\*\* (Add|Update|Delete) File: (.+)", line)
            if match:
                current = {"action": match[1], "path": relative_path(root, match[2]), "body": []}
                entries.append(current)
            elif line.startswith("*** Move to: ") and current and current["action"] == "Update":
                current["move"] = relative_path(root, line[len("*** Move to: "):])
            elif current:
                current["body"].append(line)
            else:
                raise ValueError("patch content before a file header")
        seen = set()
        for entry in entries:
            path, action = entry["path"], entry["action"]
            if path in seen:
                warnings.append(path + ": repeated file operation is NOT ASSESSED")
                continue
            seen.add(path)
            target = root / path
            if protected(path) and target.exists():
                warnings.append(path + ": protected existing artifact; confirm the approved edit preserves its content")
            moved = entry.get("move")
            if moved and ((protected(moved) and (root / moved).exists()) or moved in REGISTRIES):
                warnings.append(moved + ": move into a protected/registry destination is NOT ASSESSED")
            if path not in REGISTRIES:
                continue
            if moved:
                warnings.append(path + ": registry move removes its canonical path")
            if target.exists() and (not target.is_file() or target.stat().st_size > MAX_BYTES):
                warnings.append(path + ": non-regular or oversized registry is NOT ASSESSED")
                continue
            before = target.read_text(encoding="utf-8-sig") if target.exists() else ""
            if action == "Delete":
                after = ""
            elif action == "Add":
                if any(not line.startswith("+") for line in entry["body"]):
                    raise ValueError("unsupported Add File content")
                after = "\n".join(line[1:] for line in entry["body"])
            else:
                try:
                    after = updated_text(before, entry["body"])
                except ValueError as error:
                    warnings.append(f"{path}: NOT ASSESSED: {error}")
                    continue
            old, new = registry_records(before, path), registry_records(after, path)
            warnings.extend(f"{path}: existing registry: {error}" for error in old["errors"])
            warnings.extend(f"{path}: proposed registry: {error}" for error in new["errors"])
            missing = {r["key"] for r in old["records"]} - {r["key"] for r in new["records"]}
            warnings.extend(f"{path}: entry deleted or renamed/renumbered: {key}" for key in sorted(missing))
            if action == "Delete":
                warnings.append(path + ": canonical registry deletion")
            checked.append(path)
    except (ValueError, OSError, UnicodeError) as error:
        warnings.append("NOT ASSESSED: " + str(error))
    return {"applied": False, "checked": checked, "warnings": warnings,
            "coverage": "Literal apply_patch operations only; shell writes and full schema validity are not assessed."}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True)
    args = parser.parse_args()
    try:
        raw = sys.stdin.read(MAX_BYTES + 1)
        if len(raw.encode()) > MAX_BYTES:
            raise ValueError("oversized hook payload")
        result = inspect_patch(args.root, json.loads(raw))
        warnings = result["warnings"]
    except (ValueError, RecursionError) as error:
        warnings = ["NOT ASSESSED: " + str(error)]
    if warnings:
        message = "\n".join("CCGS artifact warning: " + warning for warning in warnings)
        print(json.dumps({
            "systemMessage": message,
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "additionalContext": message,
            },
        }))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
