#!/usr/bin/env python3
"""Validate install/coexistence fixture structure before installer exists."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path


ALLOWED_CLAUDE_TEST_FIXTURES = {
    ".codex/tests/fixtures/claude-existing/.claude/settings.json",
    ".codex/tests/fixtures/claude-existing/CLAUDE.md",
}
EXPECTED_INSTALLED_FILE_COUNT = 509


def run_command(command: list[str], cwd: Path, env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        cwd=cwd,
        env=env,
        text=True,
        capture_output=True,
        check=False,
    )


def command_failure(result: subprocess.CompletedProcess[str]) -> str:
    return (result.stderr.strip() or result.stdout.strip() or f"exit {result.returncode}")[-1200:]


def validate_installer_integration(root: Path, errors: list[str]) -> None:
    install = root / ".codex" / "install.sh"
    uninstall = root / ".codex" / "uninstall.sh"

    with tempfile.TemporaryDirectory(prefix="ccgs-install-clean-") as temp:
        target = Path(temp)
        result = run_command([str(install), str(target)], root)
        if result.returncode != 0:
            errors.append(f"clean install failed: {command_failure(result)}")
            return

        state_path = target / ".codex" / "manifest" / "install-state.json"
        if not state_path.exists():
            errors.append("clean install did not write install-state.json")
            return
        state = json.loads(state_path.read_text(encoding="utf-8"))
        if len(state.get("installed_file_hashes", {})) != EXPECTED_INSTALLED_FILE_COUNT:
            errors.append("clean install state does not own all manifest paths")
        if len(state.get("package_owned_paths", [])) != EXPECTED_INSTALLED_FILE_COUNT:
            errors.append("clean install state does not explicitly own all manifest paths")

        legacy_state = dict(state)
        legacy_state.pop("package_owned_paths", None)
        state_path.write_text(json.dumps(legacy_state, indent=2, sort_keys=True) + "\n", encoding="utf-8")

        modified = target / ".codex" / "docs" / "MIGRATION.md"
        modified.write_text(modified.read_text(encoding="utf-8") + "\nlocal integration edit\n", encoding="utf-8")
        modified_text = modified.read_text(encoding="utf-8")
        result = run_command([str(install), str(target)], root)
        if result.returncode == 0 or "modified package-owned path" not in result.stderr:
            errors.append("default upgrade did not reject a modified package-owned path")
        if modified.read_text(encoding="utf-8") != modified_text:
            errors.append("failed upgrade changed the locally modified package file")

        result = run_command([str(install), "--replace-modified", str(target)], root)
        if result.returncode != 0:
            errors.append(f"explicit modified-file replacement failed: {command_failure(result)}")
        elif modified.read_bytes() != (root / ".codex" / "docs" / "MIGRATION.md").read_bytes():
            errors.append("--replace-modified did not restore package content")
        backup_matches = list((target / ".codex" / "backups").glob("*/.codex/docs/MIGRATION.md"))
        if not backup_matches:
            errors.append("--replace-modified did not retain a durable backup")

        project_profile = target / ".agents" / "skills" / "gen-asset" / "profiles" / "custom.md"
        project_profile.parent.mkdir(parents=True, exist_ok=True)
        project_profile.write_text("project-owned\n", encoding="utf-8")
        user_log = target / "production" / "session-logs" / "session-start.json"
        user_log.parent.mkdir(parents=True, exist_ok=True)
        user_log.write_text('{"hook_event_name":"user-data"}\n', encoding="utf-8")

        before = run_command([str(uninstall), "--dry-run", str(target)], root)
        after = run_command([str(uninstall), str(target), "--dry-run"], root)
        if before.returncode != 0 or after.returncode != 0 or before.stdout != after.stdout:
            errors.append("uninstall dry-run flag order is not backward compatible")
        result = run_command([str(uninstall), str(target)], root)
        if result.returncode != 0:
            errors.append(f"uninstall failed: {command_failure(result)}")
        if not project_profile.exists():
            errors.append("uninstall removed project-owned gen-asset content")
        if not user_log.exists():
            errors.append("uninstall removed unowned session-log content")

    with tempfile.TemporaryDirectory(prefix="ccgs-install-brownfield-") as temp:
        target = Path(temp)
        shared = target / "design" / "registry" / "entities.yaml"
        shared.parent.mkdir(parents=True)
        shared.write_text("user-owned: true\n", encoding="utf-8")
        user_log = target / "production" / "session-logs" / "session-start.json"
        user_log.parent.mkdir(parents=True)
        user_log.write_text('{"hook_event_name":"user-data"}\n', encoding="utf-8")
        empty_dir = target / "docs" / "user-empty"
        empty_dir.mkdir(parents=True)
        result = run_command([str(install), str(target)], root)
        if result.returncode == 0 or "refusing to overwrite unowned path design/registry/entities.yaml" not in result.stderr:
            errors.append("brownfield install did not fail closed on an unowned shared path")
        if shared.read_text(encoding="utf-8") != "user-owned: true\n" or not user_log.exists() or not empty_dir.exists():
            errors.append("failed brownfield preflight mutated user-owned content")
        unexpected = [path for path in target.rglob("*") if path.is_file() and path not in {shared, user_log}]
        if unexpected:
            errors.append("failed brownfield preflight created package files")

    with tempfile.TemporaryDirectory(prefix="ccgs-install-identical-unowned-") as temp:
        target = Path(temp)
        readme = target / "README.md"
        readme.write_bytes((root / "README.md").read_bytes())
        original = readme.read_bytes()
        result = run_command([str(install), "--replace-modified", str(target)], root)
        if result.returncode == 0 or "refusing to overwrite unowned path README.md" not in result.stderr:
            errors.append("installer adopted byte-identical unowned content as package-owned")
        if readme.read_bytes() != original or (target / ".codex" / "manifest" / "install-state.json").exists():
            errors.append("identical-unowned preflight mutated the target")

    with tempfile.TemporaryDirectory(prefix="ccgs-install-marker-") as temp:
        target = Path(temp)
        agents = target / "AGENTS.md"
        agents.write_text("# Existing project instructions\n", encoding="utf-8")
        result = run_command([str(install), str(target)], root)
        if result.returncode != 0:
            errors.append(f"marker-managed install failed: {command_failure(result)}")
        else:
            text = agents.read_text(encoding="utf-8")
            if not text.startswith("# Existing project instructions\n") or "<!-- BEGIN CCGS CODEX PORT -->" not in text:
                errors.append("marker-managed install did not preserve existing AGENTS.md content")

    with tempfile.TemporaryDirectory(prefix="ccgs-install-claude-migration-") as temp:
        target = Path(temp)
        legacy = target / "CLAUDE.md"
        legacy.write_text("# Existing legacy guardrail\nKeep player data safe.\n", encoding="utf-8")
        original = legacy.read_bytes()
        result = run_command([str(install), str(target)], root)
        if result.returncode != 0:
            errors.append(f"Claude guardrail migration install failed: {command_failure(result)}")
        else:
            agents_text = (target / "AGENTS.md").read_text(encoding="utf-8")
            if "<!-- BEGIN CCGS MIGRATED LEGACY INSTRUCTIONS -->" not in agents_text:
                errors.append("Claude guardrail migration block was not created")
            if legacy.read_bytes() != original:
                errors.append("Claude guardrail migration modified CLAUDE.md")

    with tempfile.TemporaryDirectory(prefix="ccgs-install-coexist-") as temp:
        target = Path(temp)
        legacy = target / "CLAUDE.md"
        legacy.write_text("# Existing legacy guardrail\n", encoding="utf-8")
        shared = target / "design" / "registry" / "entities.yaml"
        shared.parent.mkdir(parents=True)
        shared.write_text("user-owned: true\n", encoding="utf-8")
        result = run_command([str(install), str(target)], root)
        if result.returncode != 0:
            errors.append(f"coexistence install failed: {command_failure(result)}")
        else:
            state_path = target / ".codex" / "manifest" / "install-state.json"
            first_state = json.loads(state_path.read_text(encoding="utf-8"))
            created_before = set(first_state.get("shared_paths_created_by_codex", []))
            if "design/registry/entities.yaml" in first_state.get("installed_file_hashes", {}):
                errors.append("coexistence state recorded a preserved shared file hash as package-owned")
            if "design/registry/entities.yaml" in first_state.get("package_owned_paths", []):
                errors.append("coexistence state explicitly owned a preserved shared file")
            legacy_state = dict(first_state)
            legacy_state.pop("package_owned_paths", None)
            legacy_state["installed_file_hashes"] = dict(first_state.get("installed_file_hashes", {}))
            legacy_state["installed_file_hashes"]["design/registry/entities.yaml"] = hashlib.sha256(
                (root / "design" / "registry" / "entities.yaml").read_bytes()
            ).hexdigest()
            state_path.write_text(json.dumps(legacy_state, indent=2, sort_keys=True) + "\n", encoding="utf-8")
            result = run_command([str(install), str(target)], root)
            if result.returncode != 0:
                errors.append(f"coexistence upgrade failed: {command_failure(result)}")
            else:
                second_state = json.loads(state_path.read_text(encoding="utf-8"))
                if set(second_state.get("shared_paths_created_by_codex", [])) != created_before:
                    errors.append("coexistence upgrade lost created-shared ownership state")
            if shared.read_text(encoding="utf-8") != "user-owned: true\n":
                errors.append("coexistence install changed a preexisting shared file")
            legacy.unlink()
            result = run_command([str(install), "--replace-modified", str(target)], root)
            if result.returncode == 0 or "refusing to overwrite unowned path design/registry/entities.yaml" not in result.stderr:
                errors.append("mode transition allowed replacement of a preserved shared file")
            if shared.read_text(encoding="utf-8") != "user-owned: true\n":
                errors.append("mode transition changed a preserved shared file")

    with tempfile.TemporaryDirectory(prefix="ccgs-install-symlink-target-") as temp, tempfile.TemporaryDirectory(
        prefix="ccgs-install-symlink-outside-"
    ) as outside_temp:
        target = Path(temp)
        outside = Path(outside_temp)
        (target / ".codex").symlink_to(outside, target_is_directory=True)
        result = run_command([str(install), str(target)], root)
        if result.returncode == 0 or "refusing symlinked target path or parent" not in result.stderr:
            errors.append("installer did not reject a symlinked package target")
        if list(outside.iterdir()):
            errors.append("symlinked-target preflight mutated content outside the install root")

    with tempfile.TemporaryDirectory(prefix="ccgs-uninstall-missing-state-") as temp:
        target = Path(temp)
        sentinel = target / "src" / ".gitkeep"
        sentinel.parent.mkdir(parents=True)
        sentinel.write_bytes((root / "src" / ".gitkeep").read_bytes())
        for arguments in (["--dry-run", str(target)], [str(target)]):
            result = run_command([str(uninstall), *arguments], root)
            if result.returncode == 0 or not sentinel.exists():
                errors.append("uninstall without state did not fail closed")

    with tempfile.TemporaryDirectory(prefix="ccgs-uninstall-stale-state-") as temp:
        target = Path(temp)
        state_path = target / ".codex" / "manifest" / "install-state.json"
        state_path.parent.mkdir(parents=True)
        state_path.write_text('{"schema_version": 1}\n', encoding="utf-8")
        sentinel = target / "README.md"
        sentinel.write_text("user-owned\n", encoding="utf-8")
        result = run_command([str(uninstall), str(target)], root)
        if result.returncode == 0 or sentinel.read_text(encoding="utf-8") != "user-owned\n":
            errors.append("uninstall with stale state did not fail closed")
        result = run_command([str(install), str(target)], root)
        if result.returncode == 0 or sentinel.read_text(encoding="utf-8") != "user-owned\n":
            errors.append("install with stale state did not fail closed")

    with tempfile.TemporaryDirectory(prefix="ccgs-state-traversal-") as temp:
        base = Path(temp)
        target = base / "target"
        state_path = target / ".codex" / "manifest" / "install-state.json"
        state_path.parent.mkdir(parents=True)
        victim = base / "victim"
        victim.write_text("outside-target\n", encoding="utf-8")
        digest = hashlib.sha256(victim.read_bytes()).hexdigest()
        state_path.write_text(
            json.dumps(
                {
                    "schema_version": 2,
                    "detected_mode": "codex_only",
                    "installed_file_hashes": {"../victim": digest},
                    "marker_block_hashes": {},
                    "package_owned_paths": ["../victim"],
                    "shared_paths_created_by_codex": [],
                    "shared_paths_preserved_preexisting": [],
                }
            )
            + "\n",
            encoding="utf-8",
        )
        for command in ([str(uninstall), str(target)], [str(install), str(target)]):
            result = run_command(command, root)
            if result.returncode == 0 or victim.read_text(encoding="utf-8") != "outside-target\n":
                errors.append("unsafe install-state traversal was not rejected before mutation")

        outside = base / "outside"
        outside.mkdir()
        outside_file = outside / "WORKFLOW-GUIDE.md"
        outside_file.write_text("outside-symlink-target\n", encoding="utf-8")
        rel = "docs/WORKFLOW-GUIDE.md"
        digest = hashlib.sha256(outside_file.read_bytes()).hexdigest()
        state_path.write_text(
            json.dumps(
                {
                    "schema_version": 2,
                    "detected_mode": "codex_only",
                    "installed_file_hashes": {rel: digest},
                    "marker_block_hashes": {},
                    "package_owned_paths": [rel],
                    "shared_paths_created_by_codex": [],
                    "shared_paths_preserved_preexisting": [],
                }
            )
            + "\n",
            encoding="utf-8",
        )
        (target / "docs").symlink_to(outside, target_is_directory=True)
        for command in ([str(uninstall), str(target)], [str(install), str(target)]):
            result = run_command(command, root)
            if result.returncode == 0 or outside_file.read_text(encoding="utf-8") != "outside-symlink-target\n":
                errors.append("symlinked package path escaped the install root")

    with tempfile.TemporaryDirectory(prefix="ccgs-obsolete-symlink-") as temp:
        base = Path(temp)
        target = base / "target"
        state_path = target / ".codex" / "manifest" / "install-state.json"
        state_path.parent.mkdir(parents=True)
        outside = base / "outside"
        outside.mkdir()
        outside_file = outside / "session-start.json"
        outside_file.write_text("outside-obsolete-target\n", encoding="utf-8")
        rel = "production/session-logs/session-start.json"
        digest = hashlib.sha256(outside_file.read_bytes()).hexdigest()
        state_path.write_text(
            json.dumps(
                {
                    "schema_version": 2,
                    "detected_mode": "codex_only",
                    "installed_file_hashes": {rel: digest},
                    "marker_block_hashes": {},
                    "package_owned_paths": [rel],
                    "shared_paths_created_by_codex": [],
                    "shared_paths_preserved_preexisting": [],
                }
            )
            + "\n",
            encoding="utf-8",
        )
        (target / "production").mkdir()
        (target / "production" / "session-logs").symlink_to(outside, target_is_directory=True)
        result = run_command([str(install), str(target)], root)
        if result.returncode == 0 or outside_file.read_text(encoding="utf-8") != "outside-obsolete-target\n":
            errors.append("symlinked obsolete path escaped the install root")

    with tempfile.TemporaryDirectory(prefix="ccgs-install-obsolete-owned-") as temp:
        target = Path(temp)
        result = run_command([str(install), str(target)], root)
        if result.returncode != 0:
            errors.append(f"obsolete-owned setup install failed: {command_failure(result)}")
        else:
            obsolete = target / "production" / "session-logs" / "session-start.json"
            obsolete.parent.mkdir(parents=True, exist_ok=True)
            obsolete.write_text("old-package-log\n", encoding="utf-8")
            state_path = target / ".codex" / "manifest" / "install-state.json"
            state = json.loads(state_path.read_text(encoding="utf-8"))
            rel = "production/session-logs/session-start.json"
            state["installed_file_hashes"][rel] = hashlib.sha256(obsolete.read_bytes()).hexdigest()
            state["package_owned_paths"].append(rel)
            state_path.write_text(json.dumps(state, indent=2, sort_keys=True) + "\n", encoding="utf-8")
            result = run_command([str(install), str(target)], root)
            if result.returncode != 0 or obsolete.exists():
                errors.append("state-proven known obsolete asset was not removed safely")

    with tempfile.TemporaryDirectory(prefix="ccgs-uninstall-gitignore-symlink-") as temp:
        base = Path(temp)
        target = base / "target"
        target.mkdir()
        result = run_command([str(install), str(target)], root)
        if result.returncode != 0:
            errors.append(f"gitignore-symlink setup install failed: {command_failure(result)}")
        else:
            outside = base / "outside-gitignore"
            outside.write_text("# outside target\n", encoding="utf-8")
            (target / ".gitignore").symlink_to(outside)
            result = run_command([str(uninstall), str(target)], root)
            if result.returncode == 0:
                errors.append("uninstall accepted a symlinked .gitignore")
            if outside.read_text(encoding="utf-8") != "# outside target\n":
                errors.append("uninstall modified a symlinked .gitignore target")
            if not (target / ".codex" / "install.sh").exists():
                errors.append("symlinked .gitignore rejection occurred after partial uninstall")

    for failpoint in ("copy", "after-verify", "state-write"):
        with tempfile.TemporaryDirectory(prefix=f"ccgs-install-{failpoint}-") as temp:
            target = Path(temp)
            env = os.environ.copy()
            env["CCGS_TEST_FAILPOINT"] = failpoint
            result = run_command([str(install), str(target)], root, env)
            if result.returncode == 0:
                errors.append(f"installer failpoint {failpoint} unexpectedly succeeded")
            leftovers = list(target.iterdir())
            if leftovers:
                errors.append(f"installer failpoint {failpoint} left target mutations: {leftovers[:5]}")


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
        "!.agents/skills/gen-asset/",
        "!design/registry/entities.yaml",
        "!docs/WORKFLOW-GUIDE.md",
        "!production/session-state/.gitkeep",
        "!src/.gitkeep",
    ):
        if required not in lines:
            errors.append(f"gitignore allowlist missing expected pattern: {required}")

    if ".agents/skills/gen-asset/*" in lines:
        errors.append("gitignore allowlist must keep project-local gen-asset descendants trackable")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    parser.add_argument("--fixture")
    parser.add_argument("--integration", action="store_true")
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
                is_claude_path = (
                    path.startswith(".claude/")
                    or path == "CLAUDE.md"
                    or "/.claude/" in path
                    or path.endswith("/CLAUDE.md")
                )
                if is_claude_path and path not in ALLOWED_CLAUDE_TEST_FIXTURES:
                    errors.append(f"installed-files must not own Claude path {path}")
                if path == ".agents/skills/gen-asset" or path.startswith(".agents/skills/gen-asset/"):
                    errors.append(f"installed-files must not own project-local gen-asset path {path}")
                if not (root / path).exists():
                    errors.append(f"installed-files path missing on disk: {path}")
            if len(rows) != EXPECTED_INSTALLED_FILE_COUNT:
                errors.append(
                    f"installed-files expected {EXPECTED_INSTALLED_FILE_COUNT} rows, found {len(rows)}"
                )
            test_files = {
                str(path.relative_to(root))
                for path in (root / ".codex" / "tests").rglob("*")
                if path.is_file()
            }
            manifest_test_files = {path for path in seen if path.startswith(".codex/tests/")}
            missing_tests = sorted(test_files - manifest_test_files)
            extra_tests = sorted(manifest_test_files - test_files)
            if missing_tests:
                errors.append("installed-files missing test assets: " + ", ".join(missing_tests))
            if extra_tests:
                errors.append("installed-files has stale test assets: " + ", ".join(extra_tests))
            install_lib = (root / ".codex" / "lib" / "install.sh").read_text(encoding="utf-8")
            if "find .codex/tests" in install_lib:
                errors.append("installer must not deploy .codex/tests outside manifest ownership")
        validate_gitignore_allowlist(root, errors)
        if args.integration:
            validate_installer_integration(root, errors)

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
