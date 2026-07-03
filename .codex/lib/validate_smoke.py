#!/usr/bin/env python3
"""Headless smoke checks for validator fixtures."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from validate_runtime import validate_agents, validate_forbidden_references, validate_skills


def emit(mode: str, root: Path, errors: list[str], warnings: list[str] | None = None) -> int:
    warnings = warnings or []
    status = "pass" if not errors else "fail"
    print(json.dumps({"check": f"smoke-{mode}", "root": str(root), "status": status, "errors": errors, "warnings": warnings}, indent=2, sort_keys=True))
    if errors:
        print(f"smoke-{mode}: {len(errors)} validation failure(s)", file=sys.stderr)
        return 1
    print(f"smoke-{mode}: pass")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=["headless", "interactive"])
    parser.add_argument("--root", default=".")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    if args.mode == "interactive":
        return emit("interactive", root, [], ["interactive smoke intentionally skipped by default; requires trust/auth/model access"])

    fixtures = root / ".codex" / "tests" / "fixtures"
    errors: list[str] = []
    expected_bad = {
        "invalid-skill": lambda p: validate_skills(p, require_present=True),
        "invalid-agent": lambda p: validate_agents(p, require_present=True),
        "stale-claude-reference": validate_forbidden_references,
    }
    for name, check in expected_bad.items():
        fixture = fixtures / name
        if not fixture.exists():
            errors.append(f"missing negative fixture {fixture.relative_to(root)}")
            continue
        failures = check(fixture)
        if not failures:
            errors.append(f"negative fixture {name} unexpectedly passed")

    return emit("headless", root, errors)


if __name__ == "__main__":
    raise SystemExit(main())
