#!/usr/bin/env python3
"""Headless smoke checks for validator fixtures."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import validate_runtime as runtime
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
        "invalid-skill": (lambda p: validate_skills(p, require_present=True), ()),
        "invalid-agent": (lambda p: validate_agents(p, require_present=True), ()),
        "stale-claude-reference": (validate_forbidden_references, ()),
        "invalid-resume-contract": (
            lambda p: getattr(runtime, "validate_resume_contract", lambda _: [])(p),
            ("automatic lane startup",),
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
