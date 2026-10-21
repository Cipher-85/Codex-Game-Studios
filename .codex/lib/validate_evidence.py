#!/usr/bin/env python3
"""Executable receipt regressions; these do not run skills or game engines."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import tempfile
from validate_runtime import validate_evidence_contract


def validate(root: Path) -> tuple[list[str], int]:
    errors: list[str] = []
    checks = 0
    helper = root / ".codex/lib/review-receipts.sh"
    if not helper.is_file():
        return ["missing review-receipts.sh"], checks
    with tempfile.TemporaryDirectory(prefix="ccgs-evidence-") as directory:
        project = Path(directory) / "project"
        project.mkdir()
        source = project / "src"
        source.mkdir()
        code = source / "player movement.gd"
        code.write_text("original\n")
        receipt = project / "stamp.json"

        def run(*args: str) -> subprocess.CompletedProcess[str]:
            return subprocess.run(
                ["bash", str(helper), "--root", str(project), *args],
                capture_output=True, text=True, check=False,
            )

        def expect(condition: bool, name: str) -> None:
            nonlocal checks
            checks += 1
            if not condition:
                errors.append(name)

        def result(*args: str) -> tuple[int, dict]:
            proc = run(*args)
            try:
                data = json.loads(proc.stdout)
            except json.JSONDecodeError:
                data = {}
            return proc.returncode, data

        proc = run("hash", "src/player movement.gd")
        expect(proc.returncode == 0, "hash handles paths with spaces")
        expect(not receipt.exists(), "hash does not write a receipt")
        try:
            baseline = json.loads(proc.stdout)
        except json.JSONDecodeError:
            return errors + ["hash did not emit JSON"], checks
        receipt.write_text(proc.stdout)
        before = {p.relative_to(project): p.read_bytes() for p in project.rglob("*") if p.is_file()}
        status, data = result("check", "stamp.json")
        expect(status == 0 and data.get("status") == "UNCHANGED", "unchanged bytes match")
        after = {p.relative_to(project): p.read_bytes() for p in project.rglob("*") if p.is_file()}
        expect(before == after, "check is read-only")
        code.write_text("changed\n")
        status, data = result("check", "stamp.json")
        expect(status == 1 and data.get("files", {}).get("src/player movement.gd") == "CHANGED",
               "changed content requires fresh evidence")
        code.unlink()
        status, data = result("check", "stamp.json")
        expect(status == 1 and data.get("files", {}).get("src/player movement.gd") == "GONE",
               "deleted input is reported")
        code.write_text("original\n")
        receipt.write_bytes(json.dumps(baseline, indent=2).replace("\n", "\r\n").encode())
        status, data = result("check", "stamp.json")
        expect(status == 0 and data.get("status") == "UNCHANGED", "CRLF receipts are portable")
        status, data = result("check", "absent.json")
        expect(status == 2 and data.get("status") == "NO_RECEIPT", "missing receipt is unknown")
        receipt.write_text("{}")
        expect(run("check", "stamp.json").returncode == 2, "empty receipt is not unchanged")
        receipt.write_text('{"schema":1,"algorithm":"sha256","files":{}}')
        expect(run("check", "stamp.json").returncode == 2, "empty file set is not proof")
        receipt.write_text(json.dumps({"schema": 1, "algorithm": "sha256",
                                       "files": {"../outside": "0" * 64}}))
        expect(run("check", "stamp.json").returncode == 2, "traversal receipt is rejected")
        expect(run("hash").returncode == 2, "empty hash input is rejected")
        expect(run("hash", "missing.gd").returncode == 2, "missing capture input is rejected")
        expect(run("hash", "src").returncode == 2, "directories are rejected")
        expect(run("hash", "src/player movement.gd", "missing.gd").returncode == 2,
               "partial capture is not successful")
        # No secret file is created or read; the path must be rejected before I/O.
        expect(run("hash", ".env.example").returncode == 2, "secret paths are rejected")
        outside = Path(directory) / "outside.txt"
        outside.write_text("outside\n")
        (project / "link").symlink_to(outside)
        expect(run("hash", "link").returncode == 2, "symlink escape is rejected")
        expect(run("hash", str(outside)).returncode == 2, "absolute external path is rejected")
        duplicate = ('{"schema":1,"algorithm":"sha256","files":'
                     '{"src/player movement.gd":"' + "0" * 64 + '",'
                     '"src/player movement.gd":"' + "1" * 64 + '"}}')
        receipt.write_text(duplicate)
        expect(run("check", "stamp.json").returncode == 2, "duplicate receipt keys are rejected")
    # Mutations recreate previously shipped unsafe instructions. Detecting these
    # is static regression coverage, not proof a model will follow a workflow.
    with tempfile.TemporaryDirectory(prefix="ccgs-workflow-guards-") as directory:
        fixture = Path(directory)
        cases = {
            "smoke-check": "NOT ASSESSED\nAutomated tests PASS or NOT RUN",
            "team-qa": "NOT ASSESSED\nUNKNOWN (treat as PASS WITH WARNINGS",
            "test-setup": "Create `Source/Tests/README.md`",
            "story-done": "NOT ASSESSED\nthen check `production/session-logs/`",
            "create-stories": "# Story\n## Acceptance Criteria\n",
            "architecture-review": "[A] Write all three files",
        }
        for name, content in cases.items():
            path = fixture / ".agents/skills" / name / "SKILL.md"
            path.parent.mkdir(parents=True)
            path.write_text(content)
            checks += 1
            if not validate_evidence_contract(fixture):
                errors.append(f"static guard missed old {name} behavior")
            path.unlink()
        path = fixture / ".agents/skills/story-done/SKILL.md"
        path.write_text("NOT ASSESSED\nask if profiled or accept as assumed")
        checks += 1
        if not validate_evidence_contract(fixture):
            errors.append("static guard missed assumed performance pass")
        path.write_text("NOT ASSESSED\nrequire measured results; never accept as assumed")
        checks += 1
        if validate_evidence_contract(fixture):
            errors.append("static guard rejected explicit prohibition on assumed passes")
    return errors, checks


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=".")
    args = parser.parse_args()
    errors, checks = validate(Path(args.root).resolve())
    print(json.dumps({"check": "evidence-receipts", "status": "fail" if errors else "pass",
                      "checks": checks, "errors": errors}, indent=2))
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
