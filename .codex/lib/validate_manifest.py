#!/usr/bin/env python3
"""Validate the Codex-native CCGS source and target manifests."""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path


REQUIRED_UPSTREAM_FIELDS = {
    "path",
    "sha256",
    "category",
    "disposition",
    "parity",
    "target",
    "rationale",
}

ALLOWED_DISPOSITIONS = {
    "ported",
    "replaced",
    "shared",
    "not_applicable",
    "blocked",
}

ALLOWED_PARITY = {
    "exact",
    "semantic_equivalent",
    "partial",
    "not_applicable",
    "blocked",
}

EXPECTED_UPSTREAM_COUNTS = {
    "claude_agents": 49,
    "claude_skills": 73,
    "claude_hooks": 12,
    "claude_rules": 11,
    "claude_docs_templates": 40,
    "claude_docs_non_templates": 23,
    "claude_config_status": 2,
    "claude_agent_memory": 1,
    "root_files": 7,
    "github": 5,
    "testing_framework": 127,
    "shared_docs": 62,
    "shared_design": 2,
    "shared_src": 2,
    "shared_production": 1,
}

EXPECTED_TARGET_COUNTS = {
    "codex_agents": 49,
    "codex_agent_memory": 17,
    "codex_skills_ported": 73,
    "codex_skills_new": 4,
    "codex_hooks_ported": 11,
    "codex_hooks_new": 2,
    "nested_agents_md": 1,
    "codex_path_rules": 15,
    "codex_docs_non_templates": 4,
    "codex_docs_templates": 40,
    "github": 5,
    "root_files": 2,
    "shared_docs": 61,
    "shared_src": 1,
    "testing_framework": 128,
}


def load_json(path: Path) -> object:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ValidationError(f"missing {path}") from exc
    except json.JSONDecodeError as exc:
        raise ValidationError(f"{path}: invalid JSON: {exc}") from exc


class ValidationError(Exception):
    pass


def validate_upstream_manifest(root: Path) -> list[str]:
    errors: list[str] = []
    manifest_path = root / ".codex" / "manifest" / "upstream-assets.json"
    data = load_json(manifest_path)
    if not isinstance(data, list):
        raise ValidationError(f"{manifest_path}: expected a JSON list")

    if len(data) != 417:
        errors.append(f"expected 417 upstream rows, found {len(data)}")

    seen_paths: set[str] = set()
    category_counts: Counter[str] = Counter()
    for index, row in enumerate(data):
        if not isinstance(row, dict):
            errors.append(f"row {index}: expected object")
            continue

        missing = sorted(REQUIRED_UPSTREAM_FIELDS - row.keys())
        if missing:
            errors.append(f"row {index}: missing fields {', '.join(missing)}")
            continue

        for field in REQUIRED_UPSTREAM_FIELDS:
            value = row.get(field)
            if value is None or value == "":
                errors.append(f"row {index}: empty {field}")

        path = str(row.get("path", ""))
        if path in seen_paths:
            errors.append(f"duplicate upstream path {path}")
        seen_paths.add(path)

        if row.get("disposition") not in ALLOWED_DISPOSITIONS:
            errors.append(f"{path}: invalid disposition {row.get('disposition')!r}")
        if row.get("parity") not in ALLOWED_PARITY:
            errors.append(f"{path}: invalid parity {row.get('parity')!r}")

        category = str(row.get("category", ""))
        category_counts[category] += 1

        if path == ".claude/hooks/notify.sh":
            if row.get("disposition") != "replaced" or "notification" not in str(row.get("rationale", "")).lower():
                errors.append("notify.sh must be marked replaced by Codex notification documentation")

    for category, expected in EXPECTED_UPSTREAM_COUNTS.items():
        actual = category_counts[category]
        if actual != expected:
            errors.append(f"category {category}: expected {expected}, found {actual}")

    return errors


def validate_expected_targets(root: Path) -> list[str]:
    errors: list[str] = []
    targets_path = root / ".codex" / "manifest" / "expected-targets.json"
    data = load_json(targets_path)
    if not isinstance(data, list):
        raise ValidationError(f"{targets_path}: expected a JSON list")

    seen_paths: set[str] = set()
    category_counts: Counter[str] = Counter()
    for index, row in enumerate(data):
        if not isinstance(row, dict):
            errors.append(f"target row {index}: expected object")
            continue
        for field in ("path", "category", "source", "owner", "rationale"):
            if not row.get(field):
                errors.append(f"target row {index}: empty {field}")
        path = str(row.get("path", ""))
        if path in seen_paths:
            errors.append(f"duplicate target path {path}")
        seen_paths.add(path)
        category_counts[str(row.get("category", ""))] += 1

    for category, expected in EXPECTED_TARGET_COUNTS.items():
        actual = category_counts[category]
        if actual != expected:
            errors.append(f"target category {category}: expected {expected}, found {actual}")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".", help="Repository root to validate")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    result = {
        "check": "manifest",
        "root": str(root),
        "status": "pass",
        "errors": [],
    }

    try:
        errors = validate_upstream_manifest(root)
        errors.extend(validate_expected_targets(root))
    except ValidationError as exc:
        result["status"] = "setup_error"
        result["errors"] = [str(exc)]
        print(json.dumps(result, indent=2, sort_keys=True))
        print(f"manifest: setup error: {exc}", file=sys.stderr)
        return 2

    if errors:
        result["status"] = "fail"
        result["errors"] = errors
        print(json.dumps(result, indent=2, sort_keys=True))
        print(f"manifest: {len(errors)} validation failure(s)", file=sys.stderr)
        return 1

    print(json.dumps(result, indent=2, sort_keys=True))
    print("manifest: pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
