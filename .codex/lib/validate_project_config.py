#!/usr/bin/env python3
"""Executable configuration regressions; does not run interactive skills."""
from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


CONFIG = None
PACKAGE = None


class ConfigTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="ccgs config ")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def write(self, relative, content):
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        return path

    def base(self, content=""):
        return self.write("project.yaml", "schema_version: 1\n" + content)

    def resolve(self, **kwargs):
        return CONFIG.resolve(self.root, **kwargs)

    def value(self, result, key):
        self.assertEqual(result["status"], "ready", result)
        return result["settings"][key]["value"]

    def invalid(self, fragment):
        result = self.resolve()
        self.assertEqual(result["status"], "invalid", result)
        self.assertEqual(result["settings"], {})
        self.assertIn(fragment, " ".join(result["errors"]))

    def test_absent_files_do_not_adopt_a_rigor_tier(self):
        result = self.resolve()
        self.assertIsNone(self.value(result, "modes.rigor"))
        self.assertIsNone(self.value(result, "modes.workflow"))
        self.assertEqual(self.value(result, "modes.review_mode"), "lean")
        self.assertEqual(result["activation"], "preview-only")

    def test_legacy_values_and_prose_are_preserved(self):
        self.write("production/review-mode.txt", "full\n")
        self.write("production/stage.txt", "Pre-Production\n")
        prefs = self.write(".codex/docs/technical-preferences.md",
                           "- **Engine**: Godot 4.6\n- **Language**: GDScript\n"
                           "## Testing\nCustom required playtest policy.\n")
        before = prefs.read_bytes()
        result = self.resolve()
        self.assertEqual(self.value(result, "modes.review_mode"), "full")
        self.assertEqual(self.value(result, "project.stage"), "Pre-Production")
        self.assertEqual(self.value(result, "engine.name"), "Godot 4.6")
        self.assertIsNone(self.value(result, "engine.version"))
        self.assertIn("prose", " ".join(result["notes"]))
        self.assertEqual(prefs.read_bytes(), before)

    def test_local_project_legacy_and_rigor_precedence(self):
        self.base("modes:\n  rigor: minimal\n  review_mode: lean\n")
        self.write("production/review-mode.txt", "full\n")
        self.write("project.local.yaml", "modes:\n  review_mode: full\n")
        result = self.resolve()
        self.assertEqual(self.value(result, "modes.review_mode"), "full")
        self.assertEqual(result["settings"]["modes.review_mode"]["source"], "project.local.yaml")
        self.assertEqual(self.value(result, "qa.level"), "minimal")

    def test_legacy_review_beats_rigor(self):
        self.base("modes:\n  rigor: minimal\n")
        self.write("production/review-mode.txt", "full\n")
        self.assertEqual(self.value(self.resolve(), "modes.review_mode"), "full")

    def test_explicit_knob_beats_rigor(self):
        self.base("modes:\n  rigor: full\ndocs:\n  density: terse\n")
        result = self.resolve()
        self.assertEqual(self.value(result, "docs.density"), "terse")
        self.assertEqual(self.value(result, "team.size"), "studio")
        self.assertEqual(result["settings"]["qa.level"]["source"], "rigor:full")

    def test_all_three_rigor_rows(self):
        for tier, review in [("minimal", "solo"), ("standard", "lean"), ("full", "full")]:
            with self.subTest(tier=tier):
                self.base("modes:\n  rigor: " + tier + "\n")
                result = self.resolve()
                self.assertEqual(self.value(result, "modes.workflow"), tier)
                self.assertEqual(self.value(result, "modes.review_mode"), review)

    def test_system_override_is_scoped(self):
        self.base("modes:\n  rigor: standard\nworkflow_overrides:\n"
                  "  system_overrides:\n    combat: full\n")
        self.assertEqual(self.value(self.resolve(system="combat"), "modes.workflow"), "full")
        self.assertEqual(self.value(self.resolve(system="inventory"), "modes.workflow"), "standard")

    def test_null_uses_next_source(self):
        self.base("modes:\n  rigor: standard\n  review_mode: null\n")
        self.assertEqual(self.value(self.resolve(), "modes.review_mode"), "lean")

    def test_strict_boolean_and_per_type_override(self):
        self.base("testing:\n  strict: true\n")
        self.write("project.local.yaml", "testing:\n  strict:\n    visual: false\n")
        result = self.resolve()
        self.assertIs(self.value(result, "testing.strict.logic"), True)
        self.assertIs(self.value(result, "testing.strict.visual"), False)

    def test_unset_strictness_is_not_false(self):
        self.base()
        self.assertIsNone(self.value(self.resolve(), "testing.strict.logic"))

    def test_local_requires_base(self):
        self.write("project.local.yaml", "modes:\n  review_mode: solo\n")
        self.invalid("requires project.yaml")

    def test_locked_local_key_is_error(self):
        self.base()
        self.write("project.local.yaml", "modes:\n  rigor: minimal\n")
        self.invalid("not locally overridable")

    def test_local_read_and_preview_whitelists_agree(self):
        self.base()
        for key in CONFIG.LOCAL_KEYS:
            value = CONFIG.SCHEMA[key]["sample"]
            with self.subTest(key=key):
                result = self.resolve(overrides={key: value}, local=True)
                self.assertEqual(self.value(result, key), value)
                parts = key.split(".")
                lines = ["  " * i + part + ":" for i, part in enumerate(parts[:-1])]
                lines.append("  " * (len(parts) - 1) + parts[-1] + ": " + json.dumps(value))
                self.write("project.local.yaml", "\n".join(lines) + "\n")
                self.assertEqual(self.value(self.resolve(), key), value)
                (self.root / "project.local.yaml").unlink()

    def test_duplicate_leaf_is_rejected(self):
        self.base("modes:\n  review_mode: full\n  review_mode: solo\n")
        self.invalid("duplicate key")

    def test_duplicate_block_is_rejected(self):
        self.base("modes:\n  review_mode: full\nmodes:\n  rigor: minimal\n")
        self.invalid("duplicate key")

    def test_invalid_enum_does_not_fall_back(self):
        self.base("modes:\n  review_mode: fulll\n")
        self.invalid("modes.review_mode")

    def test_wrong_shape_does_not_fall_back(self):
        self.base("modes:\n  rigor:\n    - standard\n")
        self.invalid("modes.rigor")

    def test_unknown_key_is_rejected(self):
        self.base("modes:\n  rigour: full\n")
        self.invalid("unknown setting")

    def test_empty_file_is_error(self):
        self.write("project.yaml", "# truncated\n")
        self.invalid("empty")

    def test_schema_is_required_and_versioned(self):
        for content in ["modes:\n  rigor: full\n", "schema_version: 2\n", "schema_version: true\n"]:
            with self.subTest(content=content):
                self.write("project.yaml", content)
                self.invalid("schema_version")

    def test_tabs_are_rejected(self):
        self.base("modes:\n\trigor: full\n")
        self.invalid("tab")

    def test_crlf_bom_and_three_space_indent(self):
        self.write("project.yaml", "\ufeffschema_version: 1\r\nmodes:\r\n   rigor: standard\r\n")
        self.assertEqual(self.value(self.resolve(), "modes.rigor"), "standard")

    def test_quotes_comments_and_lists(self):
        self.base("project:\n  name: 'Pilot #1: test' # comment\nplatform:\n"
                  "  targets: [PC, 'Web']\nmodes:\n  automation_always_ask:\n"
                  "    - scope_changes\n    - file_deletions\n")
        result = self.resolve()
        self.assertEqual(self.value(result, "project.name"), "Pilot #1: test")
        self.assertEqual(self.value(result, "platform.targets"), ["PC", "Web"])

    def test_plain_apostrophe_does_not_swallow_comment(self):
        self.base("project:\n  name: Pilot's game # comment\n")
        self.assertEqual(self.value(self.resolve(), "project.name"), "Pilot's game")

    def test_multiline_is_rejected_explicitly(self):
        self.base("project:\n  name: |\n    Two lines\n    here\n")
        self.invalid("multiline")

    def test_unsupported_yaml_is_rejected(self):
        for value in ["&shared full", "*shared", "!!str full", "{nested: full}", '"unterminated']:
            with self.subTest(value=value):
                self.base("modes:\n  review_mode: " + value + "\n")
                self.assertEqual(self.resolve()["status"], "invalid")

    def test_invalid_legacy_review_is_error(self):
        self.write("production/review-mode.txt", "fulll\n")
        self.invalid("review-mode.txt")

    def test_engine_field_fallback_is_per_field(self):
        self.write(".codex/docs/technical-preferences.md",
                   "- **Engine**: Godot\n- **Language**: GDScript\n")
        self.base("engine:\n  version: '4.6'\n")
        result = self.resolve()
        self.assertEqual(self.value(result, "engine.name"), "Godot")
        self.assertEqual(self.value(result, "engine.version"), "4.6")
        self.assertEqual(self.value(result, "engine.language"), "GDScript")

    def test_numeric_boolean_confusion_is_rejected(self):
        self.base("performance:\n  target_framerate: true\n")
        self.invalid("performance.target_framerate")

    def test_excessive_numbers_and_nesting_return_diagnostics(self):
        self.base("performance:\n  target_framerate: " + "9" * 5000 + "\n")
        self.invalid("numeric limit")
        self.base("performance:\n  target_framerate: 1.0e9999\n")
        self.invalid("non-finite")
        self.base("".join("  " * i + "nested:\n" for i in range(20)))
        self.invalid("nesting")

    def test_large_and_non_utf8_files_are_rejected(self):
        self.write("project.yaml", "#" * 131073)
        self.invalid("128 KiB")
        (self.root / "project.yaml").write_bytes(b"schema_version: 1\n\xff")
        self.invalid("UTF-8")

    def test_invalid_cli_config_emits_no_resolved_values(self):
        self.base("modes:\n  review_mode: fulll\n")
        result = subprocess.run([sys.executable, str(PACKAGE / ".codex/lib/project_config.py"),
                                 "--root", str(self.root), "resolve"], capture_output=True, text=True)
        self.assertEqual(result.returncode, 2)
        self.assertEqual(json.loads(result.stdout)["settings"], {})

    def test_cli_rejects_duplicate_assignments_and_locked_local_key(self):
        self.base()
        command = [sys.executable, str(PACKAGE / ".codex/lib/project_config.py"), "--root", str(self.root), "preview"]
        for args in [["--set", "modes.rigor=full", "--set", "modes.rigor=minimal"],
                     ["--local", "--set", "modes.rigor=minimal"]]:
            with self.subTest(args=args):
                result = subprocess.run(command + args, capture_output=True, text=True)
                self.assertEqual(result.returncode, 2)
                self.assertEqual(json.loads(result.stdout)["settings"], {})

    def test_shadowed_project_preview_is_reported(self):
        self.base("modes:\n  review_mode: lean\n")
        self.write("project.local.yaml", "modes:\n  review_mode: full\n")
        result = self.resolve(overrides={"modes.review_mode": "solo"})
        self.assertEqual(self.value(result, "modes.review_mode"), "full")
        self.assertEqual(result["changes"], {})
        self.assertIn("shadows", " ".join(result["notes"]))

    def test_performance_enforcement_uses_upstream_enum(self):
        for mode in ("warn", "block", "off"):
            with self.subTest(mode=mode):
                self.base("performance:\n  enforce: " + mode + "\n")
                self.assertEqual(self.value(self.resolve(), "performance.enforce"), mode)
        self.base("performance:\n  enforce: false\n")
        self.invalid("performance.enforce")

    def test_preview_has_no_writes_and_preserves_originals(self):
        self.base("modes:\n  rigor: standard\n")
        before = {str(p.relative_to(self.root)): p.read_bytes() for p in self.root.rglob("*") if p.is_file()}
        result = self.resolve(overrides={"modes.rigor": "full"})
        self.assertEqual(self.value(result, "qa.level"), "full")
        self.assertEqual(result["changes"]["qa.level"]["before"]["value"], "standard")
        self.assertFalse(result["applied"])
        self.assertEqual(before, {str(p.relative_to(self.root)): p.read_bytes() for p in self.root.rglob("*") if p.is_file()})

    def test_symlink_input_is_rejected(self):
        external = self.root / "external.yaml"
        external.write_text("schema_version: 1\n")
        (self.root / "project.yaml").symlink_to(external)
        self.invalid("symlink")

    def test_cli_root_and_nested_cwd_agree(self):
        self.base("modes:\n  rigor: standard\n")
        nested = self.root / "src/deep"
        nested.mkdir(parents=True)
        command = [sys.executable, str(PACKAGE / ".codex/lib/project_config.py"),
                   "--root", str(self.root), "resolve"]
        first = subprocess.run(command, cwd=self.root, capture_output=True, text=True)
        second = subprocess.run(command, cwd=nested, capture_output=True, text=True)
        self.assertEqual(first.returncode, 0, first.stderr)
        self.assertEqual(first.stdout, second.stdout)

    def test_cli_default_root_is_package_location(self):
        command = [sys.executable, str(PACKAGE / ".codex/lib/project_config.py"), "resolve"]
        result = subprocess.run(command, cwd=self.root, capture_output=True, text=True)
        self.assertEqual(json.loads(result.stdout)["root"], str(PACKAGE.resolve()))

    def test_cli_preview_and_unsupported_mutation(self):
        self.base("modes:\n  rigor: standard\n")
        command = [sys.executable, str(PACKAGE / ".codex/lib/project_config.py"), "--root", str(self.root)]
        result = subprocess.run(command + ["preview", "--set", "modes.rigor=full"], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse(json.loads(result.stdout)["applied"])
        self.assertNotEqual(subprocess.run(command + ["set", "modes.rigor=full"], capture_output=True).returncode, 0)

    def test_templates_are_valid_and_do_not_pin_derived_knobs(self):
        self.write("project.yaml", (PACKAGE / ".codex/docs/templates/project.yaml").read_text())
        self.write("project.local.yaml", (PACKAGE / ".codex/docs/templates/project.local.yaml").read_text())
        result = self.resolve()
        self.assertEqual(self.value(result, "qa.level"), "standard")
        for key in CONFIG.RIGOR["standard"]:
            self.assertEqual(result["settings"][key]["source"], "rigor:standard")

    def test_operational_review_precedence_and_provenance(self):
        cases = [
            (None, None, None, None, "lean", "default"),
            (None, None, "full", None, "full", "production/review-mode.txt"),
            ("modes:\n  rigor: minimal\n", None, None, None, "solo", "rigor:minimal"),
            ("modes:\n  rigor: minimal\n", None, "full", None, "full", "production/review-mode.txt"),
            ("modes:\n  rigor: full\n  review_mode: lean\n", None, "full", None, "lean", "project.yaml"),
            ("modes:\n  rigor: full\n  review_mode: lean\n", "solo", "full", None, "solo", "project.local.yaml"),
            ("modes:\n  review_mode: lean\n", "solo", "lean", "full", "full", "--review"),
        ]
        for base, local, legacy, override, expected, source in cases:
            with self.subTest(source=source):
                for path in ("project.yaml", "project.local.yaml", "production/review-mode.txt"):
                    (self.root / path).unlink(missing_ok=True)
                if base is not None:
                    self.base(base)
                if local is not None:
                    self.write("project.local.yaml", "modes:\n  review_mode: " + local + "\n")
                if legacy is not None:
                    self.write("production/review-mode.txt", legacy + "\n")
                before = {str(p): p.read_bytes() for p in self.root.rglob("*") if p.is_file()}
                result = CONFIG.review_mode(self.root, review=override)
                self.assertEqual(result["status"], "ready", result)
                self.assertEqual((result["value"], result["source"]), (expected, source))
                self.assertEqual(result["configured"], source != "default")
                self.assertEqual(result["operational_keys"], list(CONFIG.OPERATIONAL_KEYS))
                self.assertFalse(result["applied"])
                self.assertEqual(before, {str(p): p.read_bytes() for p in self.root.rglob("*") if p.is_file()})

    def test_operational_review_validates_all_rigor_rows(self):
        for rigor, expected in (("minimal", "solo"), ("standard", "lean"), ("full", "full")):
            with self.subTest(rigor=rigor):
                self.base("modes:\n  rigor: " + rigor + "\n")
                result = CONFIG.review_mode(self.root)
                self.assertEqual(result["value"], expected)
                self.assertEqual(result["source"], "rigor:" + rigor)

    def test_review_override_does_not_bypass_invalid_configuration(self):
        fixtures = [
            ("project.yaml", "schema_version: 2\n"),
            ("project.yaml", "schema_version: 1\nmodes:\n  review_mode: fulll\n"),
            ("project.local.yaml", "modes:\n  review_mode: full\n"),
            ("production/review-mode.txt", "none\n"),
        ]
        for path, content in fixtures:
            with self.subTest(path=path):
                target = self.write(path, content)
                result = CONFIG.review_mode(self.root, review="full")
                self.assertEqual(result["status"], "invalid", result)
                self.assertIsNone(result["value"])
                self.assertIsNone(result["source"])
                self.assertFalse(result["configured"])
                self.assertTrue(result["errors"])
                target.unlink()

    def test_invalid_review_override_never_defaults(self):
        self.write("production/review-mode.txt", "full\n")
        for override in ("", "none", "Full", True, ["solo"]):
            with self.subTest(override=override):
                result = CONFIG.review_mode(self.root, review=override)
                self.assertEqual(result["status"], "invalid", result)
                self.assertIsNone(result["value"])

    def test_review_null_is_unconfigured_and_does_not_adopt_rigor(self):
        self.base("modes:\n  review_mode: null\n")
        result = CONFIG.review_mode(self.root)
        self.assertEqual(result["value"], "lean")
        self.assertFalse(result["configured"])
        self.assertIsNone(self.resolve()["settings"]["modes.rigor"]["value"])

    def test_review_consumer_does_not_apply_assignment_preview(self):
        self.base("modes:\n  review_mode: lean\n")
        preview = self.resolve(overrides={"modes.review_mode": "solo"})
        self.assertEqual(self.value(preview, "modes.review_mode"), "solo")
        self.assertEqual(CONFIG.review_mode(self.root)["value"], "lean")

    def test_consumer_support_is_explicit_in_inspection_schema_and_preview(self):
        self.base("modes:\n  rigor: minimal\n  automation: autonomous\n")
        for result in (self.resolve(), self.resolve(overrides={"modes.rigor": "full"})):
            self.assertEqual(result["operational_keys"], list(CONFIG.OPERATIONAL_KEYS))
            self.assertFalse(result["applied"])
            self.assertEqual(result["activation"], "preview-only")
        command = [sys.executable, str(PACKAGE / ".codex/lib/project_config.py"), "schema"]
        schema = json.loads(subprocess.check_output(command, text=True))
        self.assertEqual(schema["operational_keys"], list(CONFIG.OPERATIONAL_KEYS))
        self.assertIsNone(self.resolve()["settings"]["testing.strict.logic"]["value"])

    def test_review_cli_formats_and_nested_root(self):
        self.base("modes:\n  review_mode: solo\n")
        nested = self.root / "nested"
        nested.mkdir()
        command = [sys.executable, str(PACKAGE / ".codex/lib/project_config.py"), "--root", str(self.root), "review-mode"]
        result = subprocess.run(command, cwd=nested, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["value"], "solo")
        result = subprocess.run(command + ["--review", "full", "--format", "text"], cwd=nested, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.strip(), "full (--review)")

    def test_review_cli_failure_is_visible_without_fallback(self):
        self.base("schema_version: 2\n")
        command = [sys.executable, str(PACKAGE / ".codex/lib/project_config.py"), "--root", str(self.root), "review-mode", "--review", "full"]
        result = subprocess.run(command, capture_output=True, text=True)
        self.assertEqual(result.returncode, 2)
        self.assertIsNone(json.loads(result.stdout)["value"])
        result = subprocess.run(command + ["--format", "text"], capture_output=True, text=True)
        self.assertEqual(result.returncode, 2)
        self.assertEqual(result.stdout.strip(), "INVALID")
        self.assertIn("schema_version", result.stderr)

    def test_review_cli_rejects_depth_and_setting_assignments(self):
        command = [sys.executable, str(PACKAGE / ".codex/lib/project_config.py"), "--root", str(self.root), "review-mode"]
        for option in (["--depth", "solo"], ["--set", "modes.review_mode=full"]):
            with self.subTest(option=option):
                self.assertNotEqual(subprocess.run(command + option, capture_output=True).returncode, 0)
        self.assertEqual(list(self.root.iterdir()), [])

    def test_runtime_guard_rejects_legacy_review_shortcuts(self):
        spec = importlib.util.spec_from_file_location("ccgs_review_runtime", PACKAGE / ".codex/lib/validate_runtime.py")
        runtime = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(runtime)
        path = Path(".agents/skills/brainstorm/SKILL.md")
        valid = "Use the shared `review-mode` contract in `.codex/docs/director-gates.md`."
        self.assertEqual(runtime.validate_review_routing_text(path, valid), [])
        for text in ("Read production/review-mode.txt", valid + "\n2. Else read `production/review-mode.txt`"):
            with self.subTest(text=text):
                self.assertTrue(runtime.validate_review_routing_text(path, text))

    def test_runtime_guard_rejects_missing_workflow_binding_and_legacy_stage_write(self):
        spec = importlib.util.spec_from_file_location("workflow_runtime", PACKAGE / ".codex/lib/validate_runtime.py")
        runtime = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(runtime)
        path = Path(".agents/skills/gate-check/SKILL.md")
        valid = "Read `.codex/docs/workflow-modes.md`; run `project_config.py workflow`."
        self.assertEqual(runtime.validate_workflow_routing_text(path, valid), [])
        self.assertTrue(runtime.validate_workflow_routing_text(path, "Use the usual workflow."))
        self.assertTrue(runtime.validate_workflow_routing_text(path, valid + '\necho -n Production > production/stage.txt'))


    def test_workflow_unconfigured_keeps_compatibility_policy(self):
        result = CONFIG.workflow(self.root)
        self.assertEqual(result["status"], "ready")
        self.assertEqual(result["tier"], "compatibility")
        self.assertEqual(result["source"], "unset")
        self.assertEqual(len(result["required_sections"]), 8)
        self.assertIsNone(self.value(self.resolve(), "modes.workflow"))

    def test_workflow_tiers_and_independent_companions(self):
        for tier, count in (("minimal", 0), ("standard", 5), ("full", 8)):
            with self.subTest(tier=tier):
                self.base("modes:\n  rigor: " + tier + "\n")
                result = CONFIG.workflow(self.root)
                self.assertEqual(result["tier"], tier)
                self.assertEqual(len(result["required_sections"]), count)
                self.assertEqual(result["source"], "rigor:" + tier)
        self.base("modes:\n  rigor: full\n  story_granularity: coarse\ndocs:\n  density: terse\n")
        result = CONFIG.workflow(self.root)
        self.assertEqual(result["tier"], "full")
        self.assertEqual(result["density"]["value"], "terse")
        self.assertEqual(result["story_granularity"]["value"], "coarse")

    def test_workflow_system_override_is_exact_stem_and_not_global(self):
        self.base("modes:\n  rigor: standard\nworkflow_overrides:\n  system_overrides:\n    forge-heat-system: full\n")
        self.assertEqual(CONFIG.workflow(self.root, system="forge-heat-system")["tier"], "full")
        self.assertEqual(CONFIG.workflow(self.root, system="forge")["tier"], "standard")
        self.assertEqual(CONFIG.workflow(self.root)["tier"], "standard")
        self.assertEqual(CONFIG.workflow(self.root, system="forge-heat-system")["project_tier"], "standard")
        self.assertEqual(CONFIG.workflow(self.root, system="forge-heat-system")["source"],
                         "project.yaml:workflow_overrides.system_overrides.forge-heat-system")

    def test_system_override_does_not_change_project_design_source(self):
        for project, system, expected in (("minimal", "full", "design/game-brief.md"),
                                          ("full", "minimal", "design/gdd/game-concept.md")):
            with self.subTest(project=project):
                self.base("modes:\n  workflow: " + project + "\nworkflow_overrides:\n  system_overrides:\n    combat: " + system + "\n")
                result = CONFIG.workflow(self.root, system="combat")
                self.assertEqual(result["design_source"], expected)
                self.assertEqual(result["tier"], system)
                self.assertEqual(result["project_tier"], project)

    def test_stage_invalid_legacy_and_workflow_bad_system_fail_closed(self):
        self.write("production/stage.txt", "no-such-stage\n")
        self.assertEqual(CONFIG.stage(self.root)["status"], "invalid")
        self.assertIsNone(CONFIG.stage(self.root)["write_target"])
        self.assertEqual(CONFIG.workflow(self.root, system="../combat")["status"], "invalid")

    def test_workflow_authoring_accepts_future_system_but_gate_reports_orphan(self):
        self.base("modes:\n  rigor: standard\nworkflow_overrides:\n  system_overrides:\n    future: full\n    typo: minimal\n")
        self.assertEqual(CONFIG.workflow(self.root, system="future")["tier"], "full")
        self.write("design/gdd/systems-index.md", "| Future | design/gdd/future.md | MVP |\n")
        result = CONFIG.workflow(self.root, check_systems=True)
        self.assertEqual(result["unmatched_systems"], ["typo"])
        self.assertIn("future", result["known_systems"])

    def test_workflow_rejects_invalid_configuration_without_fallback(self):
        self.base("modes:\n  workflow: typo\n")
        result = CONFIG.workflow(self.root)
        self.assertEqual(result["status"], "invalid")
        self.assertIsNone(result["tier"])

    def test_stage_precedence_and_single_write_target(self):
        self.write("production/stage.txt", "Concept\n")
        self.assertEqual(CONFIG.stage(self.root)["write_target"], "production/stage.txt")
        self.base("project:\n  stage: Production\n")
        result = CONFIG.stage(self.root)
        self.assertEqual((result["value"], result["phase"]), ("Production", "production"))
        self.assertEqual((result["write_target"], result["write_key"]), ("project.yaml", "project.stage"))
        self.assertEqual(result["shadowed_legacy"], "Concept")
        self.base("project:\n  stage: null\n")
        self.assertEqual(CONFIG.stage(self.root)["write_target"], "production/stage.txt")

    def test_stage_unset_and_terminal_live(self):
        result = CONFIG.stage(self.root)
        self.assertIsNone(result["value"])
        self.assertFalse(result["configured"])
        self.assertEqual(result["write_target"], "production/stage.txt")
        self.base("project:\n  stage: Live\n")
        result = CONFIG.stage(self.root)
        self.assertTrue(result["terminal"])
        self.assertEqual(result["phase"], "live")

    def test_stage_aliases_and_invalid_configured_stage(self):
        self.base("project:\n  stage: pre-production\n")
        self.assertEqual(CONFIG.stage(self.root)["value"], "Pre-Production")
        self.base("project:\n  stage: Prodution\n")
        result = CONFIG.stage(self.root)
        self.assertEqual(result["status"], "invalid")
        self.assertIsNone(result["write_target"])
        self.assertTrue(result["errors"])

    def test_qa_policy_preserves_mandatory_evidence_at_every_level(self):
        for level in (None, "minimal", "standard", "full"):
            with self.subTest(level=level):
                self.base(("qa:\n  level: " + level + "\n") if level else "")
                result = CONFIG.qa_policy(self.root)
                self.assertEqual(result["status"], "ready")
                self.assertEqual(result["level"], level or "compatibility")
                for rule in result["types"].values():
                    self.assertTrue(rule["evidence_required"])
                    self.assertTrue(rule["known_failure_blocks"])
                self.assertEqual(result["additional_regression"], level == "full")

    def test_strict_false_cannot_waive_mandatory_evidence(self):
        self.base("testing:\n  strict: false\n")
        result = CONFIG.qa_policy(self.root)
        self.assertEqual(result["types"]["logic"]["gate"], "blocking")
        self.assertFalse(result["types"]["logic"]["requested_strict"])
        self.assertTrue(result["types"]["config"]["known_failure_blocks"])
        self.write("project.local.yaml", "testing:\n  strict:\n    visual: true\n")
        self.assertEqual(CONFIG.qa_policy(self.root)["types"]["visual"]["gate"], "blocking")

    def test_coverage_threshold_is_explicit_and_full_only(self):
        self.base("qa:\n  level: standard\n  coverage_minimum: 80\n")
        self.assertFalse(CONFIG.qa_policy(self.root)["coverage"]["active"])
        self.base("qa:\n  level: full\n  coverage_minimum: 80\n")
        result = CONFIG.qa_policy(self.root)
        self.assertTrue(result["coverage"]["active"])
        self.assertEqual(result["coverage"]["minimum"], 80)
        self.base("qa:\n  level: full\n")
        self.assertFalse(CONFIG.qa_policy(self.root)["coverage"]["active"])

    def test_team_policy_never_weakens_required_roles_or_review(self):
        for size, optional in ((None, "existing"), ("individual", "none"),
                               ("small", "relevant"), ("studio", "declared")):
            with self.subTest(size=size):
                self.base(("team:\n  size: " + size + "\n") if size else "")
                result = CONFIG.team_policy(self.root)
                self.assertEqual(result["optional_roles"], optional)
                self.assertEqual(result["required_roles"], "preserve")
                self.assertTrue(result["review_mode_independent"])
        self.write("project.local.yaml", "team:\n  size: individual\n")
        self.assertEqual(CONFIG.team_policy(self.root)["source"], "project.local.yaml")

    def test_technical_legacy_fields_keep_units_and_provenance(self):
        text = ("## Engine & Language\n- **Engine**: Godot 4.6\n- **Language**: GDScript\n"
                "## Input & Platform\n- **Target Platforms**: PC, Web\n- **Primary Input**: Gamepad\n"
                "- **Gamepad Support**: Full\n- **Touch Support**: None\n"
                "## Performance Budgets\n- **Target Framerate**: 60 fps\n- **Frame Budget**: 16.67 ms\n"
                "- **Draw Calls**: 1000\n- **Memory Ceiling**: 512 MB\n"
                "## Testing\n- **Framework**: GdUnit4\n- **Minimum Coverage**: 80%\n")
        prefs = self.write(".codex/docs/technical-preferences.md", text)
        result = self.resolve()
        for key, value in (("platform.targets", ["PC", "Web"]), ("performance.frame_budget_ms", 16.67),
                           ("performance.memory_ceiling_mb", 512), ("qa.coverage_minimum", 80),
                           ("testing.framework", "GdUnit4")):
            self.assertEqual(self.value(result, key), value)
            self.assertEqual(result["settings"][key]["source"], ".codex/docs/technical-preferences.md")
        self.assertIsNone(self.value(result, "engine.version"))
        self.assertEqual(prefs.read_text(), text)

    def test_technical_unmapped_prose_is_not_a_guessed_number(self):
        self.write(".codex/docs/technical-preferences.md", "## Performance Budgets\n- **Memory Ceiling**: about half a GB\n")
        self.assertIsNone(self.value(self.resolve(), "performance.memory_ceiling_mb"))
        self.assertTrue(CONFIG.technical(self.root)["unmapped"])

    def test_technical_conflicts_and_pin_readiness(self):
        self.base("engine:\n  name: Godot\n  version: '4.6'\n  language: GDScript\ntesting:\n  framework: GdUnit4\n")
        self.assertFalse(CONFIG.technical(self.root)["engine_ready"])
        self.write("docs/engine-reference/godot/VERSION.md", "| **Engine Version** | 4.6 |\n")
        result = CONFIG.technical(self.root)
        self.assertTrue(result["engine_ready"])
        self.assertEqual(result["runner_status"], "NOT ASSESSED")
        self.write(".codex/docs/technical-preferences.md", "## Engine & Language\n- **Engine**: Unity\n")
        result = CONFIG.technical(self.root)
        self.assertFalse(result["engine_ready"])
        self.assertTrue(result["conflicts"])

    def test_technical_shipped_pins_accept_versions_without_engine_labels(self):
        cases = (
            ("godot", "Godot", "GDScript", "4.6", "Godot 4.6"),
            ("unity", "Unity", "C#", "6.3 LTS", "Unity 6.3 LTS"),
            ("unreal", "Unreal Engine", "C++", "5.7", "Unreal Engine 5.7"),
        )
        for family, name, language, version, displayed in cases:
            for requested in (version, displayed):
                with self.subTest(engine=family, requested=requested):
                    self.base("engine:\n  name: " + json.dumps(name) +
                              "\n  version: " + json.dumps(requested) +
                              "\n  language: " + json.dumps(language) + "\n")
                    relative = f"docs/engine-reference/{family}/VERSION.md"
                    pin = self.write(relative, (PACKAGE / relative).read_text(encoding="utf-8"))
                    before = pin.read_bytes()
                    result = CONFIG.technical(self.root)
                    self.assertEqual(result["conflicts"], [], result)
                    self.assertTrue(result["engine_ready"], result)
                    self.assertEqual(result["settings"]["engine.version"]["value"], requested)
                    self.assertEqual(result["pin"]["version"], displayed)
                    self.assertEqual(result["engine_runtime"], "NOT ASSESSED")
                    self.assertEqual(pin.read_bytes(), before)

    def test_technical_labeled_wrong_pins_remain_conflicts(self):
        self.base("engine:\n  name: Godot\n  version: '4.6'\n  language: GDScript\n")
        for displayed in ("Godot 4.5", "Godot 4.6.1", "Godot 4.6 beta", "Unity 4.6"):
            with self.subTest(pin=displayed):
                pin = self.write("docs/engine-reference/godot/VERSION.md",
                                 "| **Engine Version** | " + displayed + " |\n")
                before = pin.read_bytes()
                result = CONFIG.technical(self.root)
                self.assertFalse(result["engine_ready"], result)
                self.assertTrue(any(row["key"] == "engine.version"
                                    for row in result["conflicts"]), result)
                self.assertEqual(pin.read_bytes(), before)

    def test_technical_wrong_pin_never_gets_replaced(self):
        self.base("engine:\n  name: Godot\n  version: '4.6'\n")
        pin = self.write("docs/engine-reference/godot/VERSION.md", "| **Engine Version** | 4.5 |\n")
        result = CONFIG.technical(self.root)
        self.assertFalse(result["engine_ready"])
        self.assertTrue(result["conflicts"])
        self.assertIn("4.5", pin.read_text())

    def test_technical_duplicate_fields_and_negative_numbers_fail_closed(self):
        self.write(".codex/docs/technical-preferences.md", "## Performance Budgets\n- **Draw Calls**: 0\n")
        self.assertEqual(self.resolve()["status"], "invalid")
        self.write(".codex/docs/technical-preferences.md", "## Testing\n- **Framework**: GUT\n- **Framework**: GdUnit4\n")
        self.assertEqual(self.resolve()["status"], "invalid")

    def test_technical_write_targets_follow_owner_without_writing(self):
        self.base("platform:\n  primary_input: Gamepad\n")
        result = CONFIG.technical(self.root)
        self.assertEqual(result["write_targets"]["platform.primary_input"]["path"], "project.yaml")
        self.assertEqual(result["write_targets"]["performance.target_framerate"]["path"], ".codex/docs/technical-preferences.md")
        self.assertIsNone(result["write_targets"]["engine.version"]["path"])

    def test_technical_wrong_engine_and_unknown_role_are_not_accepted(self):
        self.base("engine:\n  name: Godot\n  language: GDScript\n")
        self.write(".codex/agents/unity-specialist.toml", "# fixture role\n")
        self.write(".codex/docs/technical-preferences.md", "## Engine Specialists\n- **Primary**: unity-specialist\n- **UI Specialist**: invented-specialist\n")
        result = CONFIG.technical(self.root)
        self.assertEqual(result["routing"]["Primary"]["status"], "conflict")
        self.assertEqual(result["routing"]["UI Specialist"]["status"], "NOT ASSESSED")

    def test_unrelated_custom_sections_do_not_become_typed_fields(self):
        self.write(".codex/docs/technical-preferences.md", "## Custom Notes\n- **Framework**: first idea\n- **Framework**: second idea\n")
        self.assertEqual(self.resolve()["status"], "ready")
        self.assertIsNone(self.value(self.resolve(), "testing.framework"))

    def test_old_engine_section_heading_preserves_legacy_identity(self):
        self.write(".codex/docs/technical-preferences.md", "## Project Engine\n- **Engine**: Godot 4.6\n- **Language**: GDScript\n")
        result = self.resolve()
        self.assertEqual(self.value(result, "engine.name"), "Godot 4.6")
        self.assertEqual(self.value(result, "engine.language"), "GDScript")
        self.assertIsNone(self.value(result, "engine.version"))

    def test_technical_local_owner_and_shadowed_budget_are_visible(self):
        self.base("performance:\n  target_framerate: 120\n")
        self.write("project.local.yaml", "performance:\n  enforce: block\n")
        self.write(".codex/docs/technical-preferences.md", "## Performance Budgets\n- **Target Framerate**: 60 fps\n")
        result = CONFIG.technical(self.root)
        self.assertEqual(result["write_targets"]["performance.enforce"]["path"], "project.local.yaml")
        self.assertEqual(result["shadowed_legacy"][0]["key"], "performance.target_framerate")
        self.assertEqual(result["engine_runtime"], "NOT ASSESSED")

    def test_framework_conflict_does_not_replace_either_source(self):
        base = self.base("testing:\n  framework: GdUnit4\n")
        prefs = self.write(".codex/docs/technical-preferences.md", "## Testing\n- **Framework**: GUT\n")
        before = (base.read_bytes(), prefs.read_bytes())
        result = CONFIG.technical(self.root)
        self.assertEqual(result["conflicts"][0]["key"], "testing.framework")
        self.assertEqual(before, (base.read_bytes(), prefs.read_bytes()))

    def test_qa_and_technical_readers_reject_invalid_local_override(self):
        self.base()
        self.write("project.local.yaml", "qa:\n  level: minimal\n")
        for reader in (CONFIG.qa_policy, CONFIG.team_policy, CONFIG.technical):
            self.assertEqual(reader(self.root)["status"], "invalid")

    def test_consumer_guard_rejects_missing_bindings_and_estimate_pass(self):
        spec = importlib.util.spec_from_file_location("config_runtime", PACKAGE / ".codex/lib/validate_runtime.py")
        runtime = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(runtime)
        path = Path(".agents/skills/perf-profile/SKILL.md")
        valid = "Use .codex/docs/technical-config.md and project_config.py technical."
        self.assertEqual(runtime.validate_config_consumer_text(path, valid), [])
        self.assertTrue(runtime.validate_config_consumer_text(path, "Use current budgets."))
        self.assertTrue(runtime.validate_config_consumer_text(path, valid + " Estimated Current"))

    def test_code_root_unconfigured_is_not_an_empty_successful_scan(self):
        (self.root / "src").mkdir()
        result = CONFIG.code_root(self.root)
        self.assertEqual(result["resolution"], "unresolved")
        self.assertEqual(result["roots"], [])
        self.assertEqual(result["scan_status"], "NOT ASSESSED")

    def test_code_root_engine_conventions(self):
        for engine, directory in (("Godot", "src"), ("Unity", "Assets"), ("Unreal Engine 5", "Source")):
            with self.subTest(engine=engine):
                self.base(f"engine:\n  name: {engine}\n")
                (self.root / directory).mkdir(exist_ok=True)
                result = CONFIG.code_root(self.root)
                self.assertEqual(result["resolution"], "resolved", result)
                self.assertEqual(result["roots"], [directory])
                self.assertEqual(result["source"], "project.yaml:engine.name")
                self.assertFalse(result["applied"])

    def test_code_root_uses_legacy_engine(self):
        self.write(".codex/docs/technical-preferences.md", "- **Engine**: Unity 6\n")
        (self.root / "Assets").mkdir()
        result = CONFIG.code_root(self.root)
        self.assertEqual(result["roots"], ["Assets"])
        self.assertIn("technical-preferences.md", result["source"])

    def test_code_root_infers_only_from_unambiguous_project_markers(self):
        self.write("ProjectSettings/ProjectVersion.txt", "m_EditorVersion: 6000.0\n")
        (self.root / "Assets").mkdir()
        result = CONFIG.code_root(self.root)
        self.assertEqual(result["engine_family"], "unity")
        self.assertEqual(result["source"], "project markers")
        self.write("project.godot", "config_version=5\n")
        self.assertEqual(CONFIG.code_root(self.root)["resolution"], "unresolved")

    def test_code_root_case_sensitive_entries(self):
        self.base("engine:\n  name: Unity\n")
        (self.root / "assets").mkdir()
        result = CONFIG.code_root(self.root)
        self.assertEqual(result["resolution"], "unresolved")
        self.assertEqual(result["roots"], [])

    def test_code_root_missing_convention_preserves_custom_layout(self):
        self.base("engine:\n  name: Godot\n")
        self.write("scripts/player.gd", "extends Node\n")
        automatic = CONFIG.code_root(self.root)
        self.assertEqual(automatic["resolution"], "unresolved")
        result = CONFIG.code_root(self.root, paths=["scripts"])
        self.assertEqual(result["roots"], ["scripts"])
        self.assertEqual(result["source"], "explicit scope")
        self.assertFalse((self.root / "src").exists())

    def test_code_root_explicit_files_and_spaces(self):
        self.write("custom code/a.cs", "// source\n")
        result = CONFIG.code_root(self.root, paths=["custom code/a.cs", "custom code/a.cs"])
        self.assertEqual(result["resolution"], "resolved")
        self.assertEqual(result["roots"], ["custom code/a.cs"])

    def test_code_root_rejects_escape_secret_and_missing_scopes(self):
        for path in ("../outside", "/tmp", ".env", "src/.env.local", "missing", "C:\\outside", "bad\npath"):
            with self.subTest(path=path):
                result = CONFIG.code_root(self.root, paths=[path])
                self.assertEqual(result["status"], "invalid", result)
                self.assertEqual(result["roots"], [])

    def test_code_root_rejects_symlink_scopes_and_markers(self):
        self.write("real/source.cs", "// source\n")
        (self.root / "linked").symlink_to(self.root / "real", target_is_directory=True)
        self.assertEqual(CONFIG.code_root(self.root, paths=["linked/source.cs"])["status"], "invalid")
        (self.root / "project.godot").symlink_to(self.root / "real/source.cs")
        self.assertEqual(CONFIG.code_root(self.root)["status"], "invalid")

    def test_code_root_configuration_and_marker_conflicts_stop_resolution(self):
        self.base("engine:\n  name: Godot\n")
        self.write("ProjectSettings/ProjectVersion.txt", "fixture\n")
        (self.root / "src").mkdir()
        result = CONFIG.code_root(self.root)
        self.assertEqual(result["resolution"], "unresolved")
        self.assertTrue(result["conflicts"])
        self.assertEqual(result["roots"], [])

    def test_code_root_legacy_engine_conflict_cannot_be_bypassed_by_scope(self):
        self.base("engine:\n  name: Godot\n")
        self.write(".codex/docs/technical-preferences.md", "- **Engine**: Unity 6\n")
        (self.root / "src").mkdir()
        result = CONFIG.code_root(self.root, paths=["src"])
        self.assertEqual(result["resolution"], "unresolved")
        self.assertTrue(result["conflicts"])

    def test_code_root_invalid_config_cannot_be_bypassed_by_scope(self):
        self.base("engine:\n  name: Godot\n  name: Unity\n")
        (self.root / "src").mkdir()
        self.assertEqual(CONFIG.code_root(self.root, paths=["src"])["status"], "invalid")

    def test_code_root_includes_native_packages_and_plugins(self):
        for engine, directories in (("Unity", ("Assets", "Packages")), ("Unreal", ("Source", "Plugins"))):
            self.base(f"engine:\n  name: {engine}\n")
            for directory in directories:
                (self.root / directory).mkdir(exist_ok=True)
            result = CONFIG.code_root(self.root)
            self.assertEqual(result["roots"], list(directories))
            self.assertEqual(result["scan_status"], "NOT ASSESSED")

    def test_code_root_empty_native_source_is_not_created(self):
        self.base("engine:\n  name: Unreal\n")
        self.write("Game.uproject", "{}\n")
        (self.root / "Content").mkdir()
        result = CONFIG.code_root(self.root)
        self.assertEqual(result["resolution"], "unresolved")
        self.assertEqual(result["content_roots"], ["Content"])
        self.assertFalse((self.root / "Source").exists())

    def test_code_root_unknown_engine_does_not_guess(self):
        self.base("engine:\n  name: Custom Engine\n")
        (self.root / "src").mkdir()
        self.assertEqual(CONFIG.code_root(self.root)["resolution"], "unresolved")

    def test_code_root_rejects_symlink_native_root(self):
        self.base("engine:\n  name: Unity\n")
        (self.root / "real").mkdir()
        (self.root / "Assets").symlink_to(self.root / "real", target_is_directory=True)
        self.assertEqual(CONFIG.code_root(self.root)["status"], "invalid")

    def test_code_root_partial_explicit_scope_is_not_returned(self):
        (self.root / "src").mkdir()
        result = CONFIG.code_root(self.root, paths=["src", "missing"])
        self.assertEqual(result["status"], "invalid")
        self.assertEqual(result["roots"], [])

    def test_source_consumer_guard_rejects_missing_binding_and_wrong_scan(self):
        spec = importlib.util.spec_from_file_location("scope_runtime", PACKAGE / ".codex/lib/validate_runtime.py")
        runtime = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(runtime)
        path = Path(".agents/skills/onboard/SKILL.md")
        valid = "Use .codex/docs/technical-config.md and project_config.py code-root."
        self.assertEqual(runtime.validate_config_consumer_text(path, valid), [])
        self.assertTrue(runtime.validate_config_consumer_text(path, "Scan the source."))
        self.assertTrue(runtime.validate_config_consumer_text(path, valid + "\nScan `src/` for all code."))

    def test_workflow_and_stage_are_read_only_from_nested_cwd(self):
        self.base("modes:\n  rigor: minimal\nproject:\n  stage: Production\n")
        before = {str(p): p.read_bytes() for p in self.root.rglob("*") if p.is_file()}
        nested = self.root / "nested"
        nested.mkdir()
        for command in ("workflow", "stage", "qa-policy", "team-policy", "technical", "code-root"):
            result = subprocess.run([sys.executable, str(PACKAGE / ".codex/lib/project_config.py"),
                                     "--root", str(self.root), command], cwd=nested,
                                    text=True, capture_output=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertFalse(json.loads(result.stdout)["applied"])
        self.assertEqual(before, {str(p): p.read_bytes() for p in self.root.rglob("*") if p.is_file()})


def main():
    global CONFIG, PACKAGE
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=".")
    args = parser.parse_args()
    PACKAGE = Path(args.root).resolve()
    module_path = PACKAGE / ".codex/lib/project_config.py"
    if not module_path.is_file():
        print(json.dumps({"check": "project-config", "status": "fail", "errors": ["missing project_config.py"]}))
        return 1
    spec = importlib.util.spec_from_file_location("ccgs_project_config", module_path)
    CONFIG = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(CONFIG)
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(ConfigTests)
    result = unittest.TestResult()
    suite.run(result)
    errors = [name.id() + ": " + detail for name, detail in result.failures + result.errors]
    print(json.dumps({"check": "project-config", "status": "pass" if result.wasSuccessful() else "fail",
                      "tests": result.testsRun, "errors": errors}, indent=2))
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    raise SystemExit(main())
