#!/usr/bin/env python3
"""Validate install/coexistence fixture structure before installer exists."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path


def emit(root: Path, errors: list[str], warnings: list[str]) -> int:
    status = "pass" if not errors else "fail"
    print(json.dumps({"check": "coexistence", "root": str(root), "status": status, "errors": errors, "warnings": warnings}, indent=2, sort_keys=True))
    if errors:
        print(f"coexistence: {len(errors)} validation failure(s)", file=sys.stderr)
        return 1
    print("coexistence: pass")
    return 0


def validate_gitignore_allowlist(root: Path, errors: list[str]) -> None:
    env = os.environ.copy()
    env["CCGS_SOURCE_ROOT"] = str(root)
    env["CCGS_INSTALL_ROOT"] = str(root)
    env["CCGS_DRY_RUN"] = "0"
    result = subprocess.run(
        ["bash", "-c", 'source "$1/.codex/lib/install.sh"; ccgs_gitignore_allowlist_block', "ccgs-gitignore-test", str(root)],
        cwd=root,
        env=env,
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        errors.append(f"gitignore allowlist generator failed: {result.stderr.strip() or result.stdout.strip()}")
        return

    lines = set(result.stdout.splitlines())
    for forbidden in (
        ".github/*",
        ".github/workflows/*",
        "design/*",
        "design/registry/*",
        "docs/*",
        "docs/architecture/*",
        "docs/engine-reference/*",
        "production/*",
        "production/session-state/*",
        "src/*",
    ):
        if forbidden in lines:
            errors.append(f"gitignore allowlist must not blanket-ignore shared content path: {forbidden}")

    for required in (
        ".codex/*",
        ".agents/*",
        "!design/registry/entities.yaml",
        "!docs/WORKFLOW-GUIDE.md",
        "!production/session-state/.gitkeep",
        "!src/.gitkeep",
    ):
        if required not in lines:
            errors.append(f"gitignore allowlist missing expected pattern: {required}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    parser.add_argument("--fixture")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    fixture = (root / args.fixture).resolve() if args.fixture else root / ".codex" / "tests" / "fixtures"
    errors: list[str] = []
    warnings: list[str] = []

    if not fixture.exists():
        warnings.append(f"{fixture}: fixture path not present yet")
        return emit(root, errors, warnings)

    if fixture == root / ".codex" / "tests" / "fixtures":
        required = [
            ".codex/install.sh",
            ".codex/uninstall.sh",
            ".codex/lib/install.sh",
            ".codex/lib/agents.sh",
            ".codex/lib/validate.sh",
            ".codex/manifest/installed-files.json",
            ".codex/backups/.gitkeep",
        ]
        for rel in required:
            path = root / rel
            if not path.exists():
                errors.append(f"missing installer asset {rel}")
            elif path.suffix == ".sh" and not (path.stat().st_mode & 0o111):
                errors.append(f"installer script is not executable: {rel}")
        manifest = root / ".codex" / "manifest" / "installed-files.json"
        if manifest.exists():
            try:
                rows = json.loads(manifest.read_text(encoding="utf-8"))
            except json.JSONDecodeError as exc:
                errors.append(f".codex/manifest/installed-files.json: invalid JSON: {exc}")
                rows = []
            seen: set[str] = set()
            for index, row in enumerate(rows):
                path = row.get("path") if isinstance(row, dict) else None
                owner = row.get("owner") if isinstance(row, dict) else None
                if not path or not owner:
                    errors.append(f"installed-files row {index}: missing path/owner")
                    continue
                if path in seen:
                    errors.append(f"installed-files duplicate path {path}")
                seen.add(path)
                if path.startswith(".claude/") or path == "CLAUDE.md" or "/.claude/" in path or path.endswith("/CLAUDE.md"):
                    errors.append(f"installed-files must not own Claude path {path}")
                if not (root / path).exists():
                    errors.append(f"installed-files path missing on disk: {path}")
        validate_gitignore_allowlist(root, errors)

    if fixture.name == "claude-existing":
        for required in (".claude", "CLAUDE.md"):
            if not (fixture / required).exists():
                errors.append(f"{fixture.relative_to(root)}: missing {required}")
    if fixture.name == "codex-collisions":
        for required in ("AGENTS.md", ".agents/skills/start/SKILL.md", ".codex/config.toml", ".codex/hooks.json"):
            if not (fixture / required).exists():
                errors.append(f"{fixture.relative_to(root)}: missing collision {required}")

    return emit(root, errors, warnings)


if __name__ == "__main__":
    raise SystemExit(main())
