#!/usr/bin/env python3
"""Validate CCGS package release versioning."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path


SEMVER_RE = re.compile(r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)$")


class ValidationError(Exception):
    pass


def run_git(root: Path, *args: str, check: bool = False) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-C", str(root), *args],
        check=check,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


def parse_semver(value: str) -> tuple[int, int, int]:
    match = SEMVER_RE.match(value)
    if not match:
        raise ValidationError(f".codex/VERSION must be X.Y.Z semver, got {value!r}")
    return tuple(int(part) for part in match.groups())


def read_version(root: Path) -> str:
    path = root / ".codex" / "VERSION"
    try:
        value = path.read_text(encoding="utf-8").strip()
    except FileNotFoundError as exc:
        raise ValidationError("missing .codex/VERSION") from exc
    parse_semver(value)
    return value


def read_manifest_paths(root: Path) -> list[str]:
    manifest_path = root / ".codex" / "manifest" / "installed-files.json"
    try:
        data = json.loads(manifest_path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ValidationError("missing .codex/manifest/installed-files.json") from exc
    except json.JSONDecodeError as exc:
        raise ValidationError(f".codex/manifest/installed-files.json: invalid JSON: {exc}") from exc
    if not isinstance(data, list):
        raise ValidationError(".codex/manifest/installed-files.json must be a list")

    paths = {
        ".codex/VERSION",
        ".codex/manifest/installed-files.json",
        "CHANGELOG.md",
    }
    for index, row in enumerate(data):
        if not isinstance(row, dict) or not row.get("path"):
            raise ValidationError(f"installed-files row {index}: missing path")
        paths.add(str(row["path"]))
    return sorted(paths)


def changelog_has_version(root: Path, version: str) -> bool:
    path = root / "CHANGELOG.md"
    try:
        text = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return False
    return re.search(rf"^## v{re.escape(version)}(?:\s+-\s+\d{{4}}-\d{{2}}-\d{{2}})?\s*$", text, re.MULTILINE) is not None


def semver_tags(root: Path) -> list[tuple[tuple[int, int, int], str]]:
    result = run_git(root, "tag", "--list", "v[0-9]*.[0-9]*.[0-9]*")
    tags: list[tuple[tuple[int, int, int], str]] = []
    if result.returncode != 0:
        return tags
    for tag in result.stdout.splitlines():
        raw = tag.removeprefix("v")
        try:
            tags.append((parse_semver(raw), tag))
        except ValidationError:
            continue
    return sorted(tags)


def changed_paths_since(root: Path, tag: str, watched_paths: list[str]) -> list[str]:
    existing = [path for path in watched_paths if (root / path).exists()]
    if not existing:
        return []
    result = run_git(root, "diff", "--name-only", tag, "--", *existing)
    changed = set(result.stdout.splitlines()) if result.returncode == 0 else set()
    untracked = run_git(root, "ls-files", "--others", "--exclude-standard", "--", *existing)
    if untracked.returncode == 0:
        changed.update(untracked.stdout.splitlines())
    return sorted(path for path in changed if path in set(watched_paths))


def validate_release(root: Path) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []

    try:
        version = read_version(root)
        version_tuple = parse_semver(version)
        watched_paths = read_manifest_paths(root)
    except ValidationError as exc:
        return [str(exc)], warnings

    if not changelog_has_version(root, version):
        errors.append(f"CHANGELOG.md is missing a section for v{version}")

    tags = semver_tags(root)
    if not tags:
        warnings.append("no vX.Y.Z git tags found; skipping tag-diff version-bump check")
        return errors, warnings

    latest_tuple, latest_tag = tags[-1]
    if version_tuple < latest_tuple:
        errors.append(f".codex/VERSION {version} is older than latest tag {latest_tag}")
        return errors, warnings

    changed = changed_paths_since(root, latest_tag, watched_paths)
    if version_tuple == latest_tuple and changed:
        errors.append(
            "installable or release files changed since "
            f"{latest_tag} without a version bump: {', '.join(changed[:20])}"
            + (" ..." if len(changed) > 20 else "")
        )

    return errors, warnings


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    errors, warnings = validate_release(root)
    status = "pass" if not errors else "fail"
    print(json.dumps({"check": "release", "root": str(root), "status": status, "errors": errors, "warnings": warnings}, indent=2, sort_keys=True))
    if errors:
        print(f"release: {len(errors)} validation failure(s)", file=sys.stderr)
        return 1
    print("release: pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
