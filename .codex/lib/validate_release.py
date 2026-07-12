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
CODEX_TAG_PREFIX = "codex-v"
LEGACY_BASELINE_TAG = "v0.1.0"


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


def validate_readme_versions(root: Path, version: str) -> list[str]:
    errors: list[str] = []
    surfaces = {
        "README.md": (
            ("Current package version", r"Current package version:\s*`v?([^`]+)`"),
            ("current release line", r"current release line is\s*`v?([^`]+)`"),
        ),
        ".codex/README.md": (
            ("package status version", r"The package version is\s*`v?([^`]+)`"),
        ),
    }
    for rel, checks in surfaces.items():
        path = root / rel
        try:
            text = path.read_text(encoding="utf-8")
        except FileNotFoundError:
            errors.append(f"{rel}: missing README version summary surface")
            continue
        for label, pattern in checks:
            match = re.search(pattern, text, re.IGNORECASE)
            if not match:
                errors.append(f"{rel}: missing {label} summary")
                continue
            reported = match.group(1)
            if reported != version:
                errors.append(
                    f"{rel}: {label} reports {reported}, expected package version {version}"
                )
    return errors


def origin_release_tags(root: Path) -> list[tuple[tuple[int, int, int], str, str]]:
    result = run_git(root, "ls-remote", "--tags", "origin")
    if result.returncode != 0:
        detail = result.stderr.strip() or "unknown git ls-remote failure"
        raise ValidationError(f"could not query origin release tags: {detail}")

    discovered: dict[str, tuple[tuple[int, int, int], str]] = {}
    for line in result.stdout.splitlines():
        parts = line.split()
        if len(parts) != 2 or not parts[1].startswith("refs/tags/"):
            continue
        commit, ref = parts
        tag = ref.removeprefix("refs/tags/")
        peeled = tag.endswith("^{}")
        if peeled:
            tag = tag[:-3]
        if tag == LEGACY_BASELINE_TAG:
            parsed = (0, 1, 0)
        elif tag.startswith(CODEX_TAG_PREFIX):
            try:
                parsed = parse_semver(tag.removeprefix(CODEX_TAG_PREFIX))
            except ValidationError:
                continue
        else:
            continue
        existing = discovered.get(tag)
        if existing is None or peeled:
            discovered[tag] = (parsed, commit)
    return sorted((parsed, tag, commit) for tag, (parsed, commit) in discovered.items())


def changed_paths_since(root: Path, base_ref: str, watched_paths: list[str]) -> list[str]:
    existing = [path for path in watched_paths if (root / path).exists()]
    if not existing:
        return []
    result = run_git(root, "diff", "--name-only", base_ref, "--", *existing)
    if result.returncode != 0:
        detail = result.stderr.strip() or "unknown git diff failure"
        raise ValidationError(f"could not compare release files against {base_ref}: {detail}")
    changed = set(result.stdout.splitlines())
    untracked = run_git(root, "ls-files", "--others", "--exclude-standard", "--", *existing)
    if untracked.returncode != 0:
        detail = untracked.stderr.strip() or "unknown git ls-files failure"
        raise ValidationError(f"could not inspect untracked release files: {detail}")
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
    errors.extend(validate_readme_versions(root, version))

    try:
        tags = origin_release_tags(root)
    except ValidationError as exc:
        errors.append(str(exc))
        return errors, warnings
    if not tags:
        errors.append("origin has no codex-vX.Y.Z release tags or legacy v0.1.0 baseline")
        return errors, warnings

    latest_tuple, latest_tag, latest_commit = tags[-1]
    if version_tuple < latest_tuple:
        errors.append(f".codex/VERSION {version} is older than latest tag {latest_tag}")
        return errors, warnings

    try:
        changed = changed_paths_since(root, latest_commit, watched_paths)
    except ValidationError as exc:
        errors.append(str(exc))
        return errors, warnings
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
