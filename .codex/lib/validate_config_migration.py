#!/usr/bin/env python3
"""Temporary-fixture tests for config staging; never migrate the package root."""
from __future__ import annotations

import argparse
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch


MIGRATION = None
PACKAGE = None


class MigrationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="ccgs migration ")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()

    def write(self, path, content):
        target = self.root / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(content.encode() if isinstance(content, str) else content)
        return target

    def plan(self):
        return MIGRATION.plan(self.root)

    def apply(self, plan=None):
        proposal = plan or self.plan()
        self.assertEqual(proposal["status"], "ready", proposal)
        return MIGRATION.apply(self.root, proposal["plan_id"])

    def staged(self):
        result = self.apply()
        self.assertEqual(result["status"], "staged", result)
        self.assertEqual(result["activation"], "preview-only")
        self.assertEqual(result["operational_keys"], list(MIGRATION.config.OPERATIONAL_KEYS))
        return result["transaction"]

    def rollback(self, transaction):
        proposal = MIGRATION.rollback_plan(self.root, transaction)
        self.assertEqual(proposal["status"], "ready", proposal)
        return MIGRATION.rollback(self.root, transaction, proposal["plan_id"])

    def test_preview_is_deterministic_and_writes_nothing(self):
        first = self.plan()
        self.assertEqual(first, self.plan())
        self.assertEqual(list(self.root.iterdir()), [])
        self.assertEqual([c["path"] for c in first["changes"]], ["project.yaml", ".gitignore"])
        self.assertIn("receipt.json", " ".join(first["transaction_files"]))
        self.assertFalse(first["applied"])
        self.assertEqual(first["operational_keys"], list(MIGRATION.config.OPERATIONAL_KEYS))

    def test_staging_preserves_operational_review_without_activating_other_knobs(self):
        self.write("production/review-mode.txt", "full\n")
        before = MIGRATION.config.review_mode(self.root)
        transaction = self.staged()
        after = MIGRATION.config.review_mode(self.root)
        self.assertEqual(before["value"], after["value"])
        self.assertEqual(after["source"], "project.yaml")
        self.assertIsNone(MIGRATION.config.resolve(self.root)["settings"]["modes.workflow"]["value"])
        self.assertEqual(self.rollback(transaction)["status"], "rolled_back")
        self.assertEqual(MIGRATION.config.review_mode(self.root)["source"], "production/review-mode.txt")

    def test_maps_legacy_without_inventing_rigor_or_version(self):
        originals = {
            "production/review-mode.txt": "full\n",
            "production/stage.txt": "Pre-Production\n",
            ".codex/docs/technical-preferences.md": "- **Engine**: Godot 4.6\n- **Language**: GDScript\nCustom testing policy.\n",
        }
        for path, content in originals.items():
            self.write(path, content)
        proposal = self.plan()
        self.assertTrue(proposal["unmapped"])
        self.staged()
        data, _ = MIGRATION.config.load_config(self.root, "project.yaml")
        self.assertEqual(data["engine.name"], "Godot 4.6")
        self.assertEqual(data["modes.review_mode"], "full")
        self.assertEqual(data["project.stage"], "Pre-Production")
        self.assertNotIn("modes.rigor", data)
        self.assertNotIn("engine.version", data)
        for path, content in originals.items():
            self.assertEqual((self.root / path).read_text(), content)

    def test_empty_project_keeps_rigor_unset(self):
        self.staged()
        result = MIGRATION.config.resolve(self.root)
        self.assertIsNone(result["settings"]["modes.rigor"]["value"])
        self.assertEqual(result["settings"]["modes.review_mode"]["value"], "lean")
        self.assertFalse((self.root / "project.local.yaml").exists())

    def test_literal_technical_fields_stage_without_removing_prose(self):
        text = ("## Input & Platform\n- **Target Platforms**: PC, Web\n"
                "## Performance Budgets\n- **Memory Ceiling**: 512 MB\n"
                "## Testing\n- **Framework**: Custom runner\n- **Minimum Coverage**: 75%\n"
                "Custom required tests and routing stay here.\n")
        prefs = self.write(".codex/docs/technical-preferences.md", text)
        self.staged()
        data, _ = MIGRATION.config.load_config(self.root, "project.yaml")
        self.assertEqual(data["platform.targets"], ["PC", "Web"])
        self.assertEqual(data["performance.memory_ceiling_mb"], 512)
        self.assertEqual(data["qa.coverage_minimum"], 75)
        self.assertEqual(prefs.read_text(), text)

    def test_existing_yaml_and_local_bytes_preserved(self):
        base = self.write("project.yaml", b"\xef\xbb\xbf# keep me\r\nschema_version: 1\r\nmodes:\r\n  rigor: full\r\n")
        local = self.write("project.local.yaml", "# personal\nmodes:\n  review_mode: solo\n")
        before = (base.read_bytes(), local.read_bytes())
        self.staged()
        self.assertEqual((base.read_bytes(), local.read_bytes()), before)

    def test_conflicting_base_and_legacy_blocks_without_writes(self):
        self.write("project.yaml", "schema_version: 1\nmodes:\n  review_mode: full\n")
        self.write("production/review-mode.txt", "lean\n")
        proposal = self.plan()
        self.assertEqual(proposal["status"], "blocked", proposal)
        self.assertIn("modes.review_mode", str(proposal["conflicts"]))
        self.assertEqual(proposal["changes"], [])
        self.assertEqual(MIGRATION.apply(self.root, proposal["plan_id"])["status"], "blocked")
        self.assertFalse((self.root / ".gitignore").exists())

    def test_invalid_config_and_ambiguous_engine_block(self):
        fixtures = [
            ("project.yaml", "schema_version: 2\n"),
            ("project.local.yaml", "modes:\n  review_mode: lean\n"),
            ("production/review-mode.txt", "fulll\n"),
            (".codex/docs/technical-preferences.md", "- **Engine**: Godot\n- **Engine**: Unity\n"),
        ]
        for path, text in fixtures:
            with self.subTest(path=path):
                target = self.write(path, text)
                self.assertEqual(self.plan()["status"], "blocked")
                target.unlink()

    def test_symlink_inputs_and_backup_parents_block(self):
        outside = self.write("outside", "schema_version: 1\n")
        for relative in ("project.yaml", ".codex/backups"):
            with self.subTest(path=relative):
                link = self.root / relative
                link.parent.mkdir(parents=True, exist_ok=True)
                link.symlink_to(outside)
                self.assertEqual(self.plan()["status"], "blocked")
                link.unlink()

    def test_nonregular_and_large_inputs_block(self):
        target = self.root / "project.yaml"
        target.mkdir()
        self.assertEqual(self.plan()["status"], "blocked")
        target.rmdir()
        self.write(".gitignore", b"x" * 131073)
        self.assertEqual(self.plan()["status"], "blocked")

    def test_stale_content_mode_or_new_input_rejects_before_mutation(self):
        for edit in ("content", "mode", "new"):
            with self.subTest(edit=edit):
                path = self.write(".gitignore", "cache/\n")
                os.chmod(path, 0o644)
                proposal = self.plan()
                if edit == "content":
                    path.write_text("new/\n")
                elif edit == "mode":
                    os.chmod(path, 0o600)
                else:
                    self.write("production/stage.txt", "Production\n")
                result = MIGRATION.apply(self.root, proposal["plan_id"])
                self.assertEqual(result["status"], "blocked", result)
                self.assertFalse((self.root / "project.yaml").exists())
                self.assertFalse((self.root / ".codex/backups").exists())

    def test_approval_fingerprint_is_bound_to_root(self):
        proposal = self.plan()
        with tempfile.TemporaryDirectory() as other:
            result = MIGRATION.apply(Path(other), proposal["plan_id"])
            self.assertEqual(result["status"], "blocked")
            self.assertEqual(list(Path(other).iterdir()), [])

    def test_ignore_preserves_crlf_and_managed_block(self):
        original = b"# mine\r\ncache/\r\n# BEGIN CCGS CODEX PORT GITIGNORE\r\n.codex/backups/\r\n# END CCGS CODEX PORT GITIGNORE\r\n"
        path = self.write(".gitignore", original)
        os.chmod(path, 0o640)
        self.staged()
        self.assertTrue(path.read_bytes().startswith(original))
        self.assertIn(b"/project.local.yaml\r\n", path.read_bytes())
        self.assertEqual(path.stat().st_mode & 0o777, 0o640)
        self.assertNotIn("\n", path.read_bytes().decode().replace("\r\n", ""))

    def test_ignore_rule_survives_later_negation_and_is_root_only(self):
        self.write(".gitignore", "/project.local.yaml\n!*.yaml\n")
        self.staged()
        self.assertEqual((self.root / ".gitignore").read_text().splitlines()[-1], "/project.local.yaml")
        subprocess.run(["git", "init", "-q", str(self.root)], check=True)
        result = subprocess.run(["git", "-C", str(self.root), "check-ignore", "--no-index", "project.local.yaml", ".codex/docs/templates/project.local.yaml"], capture_output=True, text=True)
        self.assertEqual(result.stdout.splitlines(), ["project.local.yaml"])

    def test_rule_inside_managed_block_does_not_count(self):
        self.write(".gitignore", "# BEGIN CCGS CODEX PORT GITIGNORE\n/project.local.yaml\n# END CCGS CODEX PORT GITIGNORE\n")
        self.staged()
        self.assertEqual((self.root / ".gitignore").read_text().count("/project.local.yaml"), 2)

    def test_malformed_managed_block_blocks(self):
        self.write(".gitignore", "# BEGIN CCGS CODEX PORT GITIGNORE\n")
        self.assertEqual(self.plan()["status"], "blocked")

    def test_repeated_staging_is_noop_without_another_transaction(self):
        self.staged()
        before = sorted(str(p) for p in self.root.rglob("*"))
        proposal = self.plan()
        self.assertEqual(proposal["status"], "noop", proposal)
        self.assertEqual(MIGRATION.apply(self.root, proposal["plan_id"])["status"], "noop")
        self.assertEqual(before, sorted(str(p) for p in self.root.rglob("*")))

    def test_backups_complete_before_first_target_write(self):
        self.write(".gitignore", "cache/\n")
        proposal = self.plan()
        real = MIGRATION.atomic_write

        def inspect(path, data, mode):
            if path.parent == self.root:
                receipt = self.root / proposal["transaction"] / "receipt.json"
                self.assertTrue(receipt.exists())
                self.assertEqual((receipt.parent / "before-1").read_bytes(), b"cache/\n")
            return real(path, data, mode)

        with patch.object(MIGRATION, "atomic_write", inspect):
            self.assertEqual(self.apply(proposal)["status"], "staged")

    def test_backup_failure_leaves_targets_untouched(self):
        path = self.write(".gitignore", "cache/\n")
        real = MIGRATION.atomic_write

        def fail(path, data, mode):
            if path.name.startswith("before-"):
                raise OSError("injected backup failure")
            return real(path, data, mode)

        with patch.object(MIGRATION, "atomic_write", fail):
            result = self.apply()
        self.assertEqual(result["status"], "failed_rolled_back", result)
        self.assertEqual(path.read_bytes(), b"cache/\n")
        self.assertFalse((self.root / "project.yaml").exists())

    def test_second_write_failure_restores_original_bytes_and_absence(self):
        path = self.write(".gitignore", "# old\r\ncache/")
        os.chmod(path, 0o640)
        real = MIGRATION.atomic_write

        def fail(path, data, mode):
            if path == self.root / ".gitignore":
                raise OSError("injected target failure")
            return real(path, data, mode)

        with patch.object(MIGRATION, "atomic_write", fail):
            result = self.apply()
        self.assertEqual(result["status"], "failed_rolled_back", result)
        self.assertFalse((self.root / "project.yaml").exists())
        self.assertEqual(path.read_bytes(), b"# old\r\ncache/")
        self.assertEqual(path.stat().st_mode & 0o777, 0o640)

    def test_incomplete_recovery_is_explicit_and_recoverable(self):
        original = self.write(".gitignore", "cache/\n")
        # Only .gitignore changes, so restoring it exercises atomic replacement.
        self.write("project.yaml", "schema_version: 1\n")
        real = MIGRATION.atomic_write

        def fail(path, data, mode):
            if path.name == "receipt.json" and b'"staged"' in data:
                raise OSError("injected final journal failure")
            if path == original and data == b"cache/\n":
                raise OSError("injected restore failure")
            return real(path, data, mode)

        with patch.object(MIGRATION, "atomic_write", fail):
            result = self.apply()
        self.assertEqual(result["status"], "recovery_required", result)
        self.assertIn("restore failure", str(result["errors"]))
        self.assertEqual(self.rollback(result["transaction"])["status"], "rolled_back")
        self.assertEqual(original.read_bytes(), b"cache/\n")

    def test_rollback_restores_existing_mode_and_absence(self):
        path = self.write(".gitignore", "# user\ncache/\n")
        os.chmod(path, 0o600)
        transaction = self.staged()
        self.assertEqual(self.rollback(transaction)["status"], "rolled_back")
        self.assertEqual(path.read_bytes(), b"# user\ncache/\n")
        self.assertEqual(path.stat().st_mode & 0o777, 0o600)
        self.assertFalse((self.root / "project.yaml").exists())
        self.assertEqual(MIGRATION.rollback_plan(self.root, transaction)["status"], "noop")
        # A fresh transaction can stage again after an approved rollback.
        self.staged()

    def test_rollback_refuses_later_content_mode_or_deletion(self):
        for edit in ("content", "mode", "delete"):
            with self.subTest(edit=edit), tempfile.TemporaryDirectory() as temp:
                root = Path(temp)
                result = MIGRATION.apply(root, MIGRATION.plan(root)["plan_id"])
                path = root / "project.yaml"
                if edit == "content":
                    path.write_text("schema_version: 1\n# later edit\n")
                elif edit == "mode":
                    os.chmod(path, 0o600)
                else:
                    path.unlink()
                self.assertEqual(MIGRATION.rollback_plan(root, result["transaction"])["status"], "blocked")
                self.assertTrue((root / ".gitignore").exists())

    def test_stale_rollback_preview_rejects_without_target_changes(self):
        transaction = self.staged()
        proposal = MIGRATION.rollback_plan(self.root, transaction)
        self.write(".gitignore", "# later edit\n")
        result = MIGRATION.rollback(self.root, transaction, proposal["plan_id"])
        self.assertEqual(result["status"], "blocked")
        self.assertTrue((self.root / "project.yaml").exists())

    def test_tampered_backup_receipt_and_transaction_path_block(self):
        self.write(".gitignore", "cache/\n")
        transaction = self.staged()
        backup = self.root / transaction / "before-1"
        original = backup.read_bytes()
        backup.write_text("tampered\n")
        self.assertEqual(MIGRATION.rollback_plan(self.root, transaction)["status"], "blocked")
        backup.write_bytes(original)
        receipt = self.root / transaction / "receipt.json"
        data = json.loads(receipt.read_text())
        data["plan"]["changes"][0]["path"] = "../../outside"
        receipt.write_text(json.dumps(data))
        self.assertEqual(MIGRATION.rollback_plan(self.root, transaction)["status"], "blocked")
        self.assertEqual(MIGRATION.rollback_plan(self.root, "../../outside")["status"], "blocked")

    def test_interrupted_transaction_can_be_recovered(self):
        real = MIGRATION.atomic_write

        def interrupt(path, data, mode):
            if path == self.root / ".gitignore":
                raise KeyboardInterrupt()
            return real(path, data, mode)

        proposal = self.plan()
        with patch.object(MIGRATION, "atomic_write", interrupt), self.assertRaises(KeyboardInterrupt):
            self.apply(proposal)
        self.assertTrue((self.root / "project.yaml").exists())
        self.assertEqual(self.plan()["status"], "blocked")
        self.assertEqual(self.rollback(proposal["transaction"])["status"], "rolled_back")
        self.assertFalse((self.root / "project.yaml").exists())

    def test_missing_journal_blocks_new_staging(self):
        directory = self.root / MIGRATION.BACKUPS / ("0" * 64)
        directory.mkdir(parents=True)
        self.assertEqual(self.plan()["status"], "blocked")
        self.assertEqual(MIGRATION.rollback_plan(self.root, str(directory.relative_to(self.root)))["status"], "blocked")

    def test_interruption_before_first_target_can_finalize_recovery(self):
        real = MIGRATION.atomic_write

        def interrupt(path, data, mode):
            if path == self.root / "project.yaml":
                raise KeyboardInterrupt()
            return real(path, data, mode)

        proposal = self.plan()
        with patch.object(MIGRATION, "atomic_write", interrupt), self.assertRaises(KeyboardInterrupt):
            self.apply(proposal)
        self.assertFalse((self.root / "project.yaml").exists())
        recovery = MIGRATION.rollback_plan(self.root, proposal["transaction"])
        self.assertEqual(recovery["status"], "ready", recovery)
        self.assertEqual(recovery["changes"], [])
        self.assertEqual(self.rollback(proposal["transaction"])["status"], "rolled_back")
        self.assertEqual(self.plan()["status"], "ready")

    def test_invalid_receipt_shapes_are_diagnostics(self):
        transaction = self.staged()
        receipt = self.root / transaction / "receipt.json"
        original = receipt.read_bytes()
        for content in (b"[]", b"null", b"{", b'{"schema_version":1,"status":"staged","plan":[]}'):
            with self.subTest(content=content):
                receipt.write_bytes(content)
                self.assertEqual(MIGRATION.rollback_plan(self.root, transaction)["status"], "blocked")
        receipt.write_bytes(original)

    def test_initial_journal_failure_keeps_original_targets(self):
        self.write(".gitignore", "cache/\n")
        real = MIGRATION.atomic_write

        def fail(path, data, mode):
            if path.name == "receipt.json" and b'"applying"' in data:
                raise OSError("injected journal failure")
            return real(path, data, mode)

        with patch.object(MIGRATION, "atomic_write", fail):
            result = self.apply()
        self.assertEqual(result["status"], "failed_rolled_back", result)
        self.assertFalse((self.root / "project.yaml").exists())
        self.assertEqual((self.root / ".gitignore").read_bytes(), b"cache/\n")

    def test_concurrent_user_edit_is_preserved_during_recovery(self):
        self.write(".gitignore", "cache/\n")
        real = MIGRATION.atomic_write

        def edit(path, data, mode):
            if path == self.root / ".gitignore":
                (self.root / "project.yaml").write_text("schema_version: 1\n# user edit\n")
                raise OSError("injected concurrent edit")
            return real(path, data, mode)

        with patch.object(MIGRATION, "atomic_write", edit):
            result = self.apply()
        self.assertEqual(result["status"], "recovery_required", result)
        self.assertIn("# user edit", (self.root / "project.yaml").read_text())
        self.assertEqual((self.root / ".gitignore").read_bytes(), b"cache/\n")

    def test_cli_stages_and_rolls_back_only_with_current_ids(self):
        command = [sys.executable, str(PACKAGE / ".codex/lib/migrate_project_config.py"), "--root", str(self.root)]
        proposal = json.loads(subprocess.check_output(command + ["plan"], text=True))
        result = json.loads(subprocess.check_output(command + ["apply", "--expect-plan", proposal["plan_id"]], text=True))
        transaction = result["transaction"]
        recovery = json.loads(subprocess.check_output(command + ["rollback-plan", transaction], text=True))
        result = json.loads(subprocess.check_output(command + ["rollback", transaction, "--expect-plan", recovery["plan_id"]], text=True))
        self.assertEqual(result["status"], "rolled_back")
        self.assertFalse((self.root / "project.yaml").exists())

    def test_backup_symlink_is_never_followed(self):
        self.write(".gitignore", "cache/\n")
        transaction = self.staged()
        backup = self.root / transaction / "before-1"
        backup.unlink()
        backup.symlink_to(self.write("outside", "cache/\n"))
        self.assertEqual(MIGRATION.rollback_plan(self.root, transaction)["status"], "blocked")

    def test_transaction_lock_rejects_concurrent_apply(self):
        import fcntl
        proposal = self.plan()
        parent = self.root / MIGRATION.BACKUPS
        parent.mkdir(parents=True)
        with (parent / "transaction.lock").open("wb") as lock:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
            result = self.apply(proposal)
        self.assertEqual(result["status"], "blocked", result)
        self.assertFalse((self.root / "project.yaml").exists())

    def test_cli_plan_is_independent_of_cwd_and_apply_requires_id(self):
        command = [sys.executable, str(PACKAGE / ".codex/lib/migrate_project_config.py"), "--root", str(self.root)]
        nested = self.root / "nested"
        nested.mkdir()
        first = subprocess.run(command + ["plan"], cwd=self.root, capture_output=True, text=True)
        second = subprocess.run(command + ["plan"], cwd=nested, capture_output=True, text=True)
        self.assertEqual(first.returncode, 0, first.stderr)
        self.assertEqual(first.stdout, second.stdout)
        self.assertNotEqual(subprocess.run(command + ["apply"], capture_output=True).returncode, 0)
        self.assertFalse((self.root / "project.yaml").exists())


def main():
    global MIGRATION, PACKAGE
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=".")
    args = parser.parse_args()
    PACKAGE = Path(args.root).resolve()
    module_path = PACKAGE / ".codex/lib/migrate_project_config.py"
    if not module_path.is_file():
        print(json.dumps({"check": "config-migration", "status": "fail", "errors": ["missing migrate_project_config.py"]}))
        return 1
    sys.path.insert(0, str(module_path.parent))
    spec = importlib.util.spec_from_file_location("ccgs_config_migration", module_path)
    MIGRATION = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(MIGRATION)
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(MigrationTests)
    result = unittest.TestResult()
    suite.run(result)
    errors = [name.id() + ": " + detail for name, detail in result.failures + result.errors]
    print(json.dumps({"check": "config-migration", "status": "pass" if result.wasSuccessful() else "fail",
                      "tests": result.testsRun, "errors": errors}, indent=2))
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    raise SystemExit(main())
