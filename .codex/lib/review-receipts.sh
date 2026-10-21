#!/usr/bin/env bash
# Read-only content receipts. Printing a hash is not evidence of a passing test.
# Requires Python 3, already required by the package audit/installer.
set -euo pipefail
exec python3 - "$0" "$@" <<'PY'
import argparse
import hashlib
import json
from pathlib import Path
import re
import sys

script = Path(sys.argv.pop(1)).resolve()
parser = argparse.ArgumentParser(description="Read-only SHA-256 evidence receipts")
parser.add_argument("--root", type=Path, default=script.parents[2])
sub = parser.add_subparsers(dest="command", required=True)
sub.add_parser("hash").add_argument("files", nargs="+")
sub.add_parser("check").add_argument("receipt")
args = parser.parse_args()
root = args.root.resolve()


def emit(data, code=0):
    print(json.dumps(data, indent=2, sort_keys=True))
    sys.exit(code)


def safe_path(name):
    path = Path(name)
    if path.is_absolute() or ".." in path.parts or not path.parts:
        raise ValueError("expected a project-relative path: " + name)
    if any(part.lower().startswith(".env") for part in path.parts):
        raise ValueError("secret path is not an evidence input")
    candidate = root
    for part in path.parts:
        candidate = candidate / part
        if candidate.is_symlink():
            raise ValueError("symlink is not an evidence input: " + name)
    candidate.resolve().relative_to(root)
    return candidate


def digest(path):
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def unique_pairs(pairs):
    values = {}
    for key, value in pairs:
        if key in values:
            raise ValueError("duplicate receipt key: " + key)
        values[key] = value
    return values


try:
    if args.command == "hash":
        files = {}
        for name in args.files:
            path = safe_path(name)
            files[path.relative_to(root).as_posix()] = digest(path)
        emit({"schema": 1, "algorithm": "sha256", "files": files})
    receipt = safe_path(args.receipt)
    if not receipt.exists():
        emit({"status": "NO_RECEIPT", "files": {}}, 2)
    data = json.loads(receipt.read_text(encoding="utf-8"), object_pairs_hook=unique_pairs)
    if not isinstance(data, dict) or data.get("schema") != 1 or data.get("algorithm") != "sha256":
        raise ValueError("unsupported receipt schema or algorithm")
    files = data.get("files")
    if not isinstance(files, dict) or not files:
        raise ValueError("receipt must name at least one file")
    # Validate the entire record before reading any of its inputs.
    paths = {}
    for name, expected in files.items():
        if not isinstance(expected, str) or not re.fullmatch(r"[0-9a-f]{64}", expected):
            raise ValueError("invalid SHA-256 for " + name)
        paths[name] = safe_path(name)
    states = {}
    for name, path in paths.items():
        if not path.exists():
            states[name] = "GONE"
        else:
            states[name] = "UNCHANGED" if digest(path) == files[name] else "CHANGED"
    changed = any(state != "UNCHANGED" for state in states.values())
    emit({"status": "CHANGED" if changed else "UNCHANGED", "files": states}, 1 if changed else 0)
except (OSError, ValueError, TypeError) as error:
    emit({"status": "NOT_ASSESSED", "error": str(error)}, 2)
PY
