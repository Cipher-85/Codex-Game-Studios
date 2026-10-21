#!/usr/bin/env python3
"""Executable artifact-reader regressions; no skill or engine is invoked."""
from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


FACTS = None
PACKAGE = None


class ArtifactTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="ccgs artifact ")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def write(self, path, body):
        target = self.root / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(body, encoding="utf-8")
        return target

    def read(self, kind, paths=None, **kwargs):
        return FACTS.inspect_artifacts(self.root, kind, paths, **kwargs)

    def story(self, text="", path="production/epics/core/story-001-test.md"):
        return self.write(path, "# Story 001: Test\n\n> **Status**: Ready\n> **Type**: Logic\n" + text)

    def adr(self, number, deps="None", status="Accepted", path=None):
        return self.write(path or f"docs/architecture/adr-{number:04d}-test.md",
                          f"# ADR-{number:04d}: Test\n\n## Status\n{status}\n\n"
                          f"## ADR Dependencies\n| Field | Value |\n|---|---|\n| **Depends On** | {deps} |\n")

    def test_empty_default_scopes_are_not_passes(self):
        for kind in ("stories", "adrs", "gdds", "bugs"):
            data = self.read(kind)
            self.assertEqual(data["status"], "empty")
            self.assertEqual(data["files_read"], 0)
            self.assertFalse(data["applied"])
            self.assertEqual(data["assessment"], "NOT ASSESSED")

    def test_story_header_and_counts(self):
        self.story("\n## Acceptance Criteria\n- [ ] First\n- [x] Second\n\n## QA Test Cases\n- **AC-1**: Check\n")
        row = self.read("stories")["records"][0]
        self.assertEqual(row["fields"]["status"]["value"], "Ready")
        self.assertEqual(row["acceptance_criteria"]["total"], 2)
        self.assertEqual(row["acceptance_criteria"]["checked"], 1)
        self.assertEqual(row["qa_cases"]["total"], 1)
        self.assertEqual(row["fields"]["status"]["line"], 3)

    def test_story_evidence_status_does_not_replace_header(self):
        self.story("\n## Test Evidence\n**Status**: Complete\n")
        row = self.read("stories")["records"][0]
        self.assertEqual(row["fields"]["status"]["value"], "Ready")
        self.assertEqual(row["fields"]["test_evidence"]["value"], "Complete")

    def test_status_only_in_body_is_not_a_header(self):
        self.write("story.md", "# Story\n## Test Evidence\nStatus: Complete\n")
        row = self.read("stories", ["story.md"])["records"][0]
        self.assertEqual(row["fields"]["status"]["state"], "missing")

    def test_duplicate_metadata_remains_ambiguous(self):
        self.story("Status: Complete\n")
        data = self.read("stories")
        self.assertEqual(data["status"], "partial")
        self.assertEqual(data["records"][0]["fields"]["status"]["state"], "ambiguous")

    def test_fenced_and_commented_metadata_are_ignored(self):
        self.write("story.md", "# Story\n```text\nStatus: Complete\n```\n<!-- Status: Complete -->\nStatus: Ready\n")
        row = self.read("stories", ["story.md"])["records"][0]
        self.assertEqual(row["fields"]["status"]["value"], "Ready")

    def test_long_fence_is_not_closed_by_short_fence(self):
        self.write("story.md", "# Story\n````\n```\nStatus: Complete\n````\nStatus: Ready\n")
        self.assertEqual(self.read("stories", ["story.md"])["records"][0]["fields"]["status"]["value"], "Ready")

    def test_tilde_fence_and_multiline_comment(self):
        self.write("story.md", "# Story\n~~~\nStatus: Complete\n~~~\n<!--\nStatus: Complete\n-->\nStatus: Ready\n")
        self.assertEqual(self.read("stories", ["story.md"])["records"][0]["fields"]["status"]["value"], "Ready")

    def test_inline_code_comment_marker_does_not_hide_later_metadata(self):
        self.write("story.md", "# Story\nExample `<!--` marker\nStatus: Ready\n")
        self.assertEqual(self.read("stories", ["story.md"])["records"][0]["fields"]["status"]["value"], "Ready")

    def test_missing_tr_id_has_no_readiness_verdict(self):
        self.story("\n## Context\nRequirement: Brief MVP feature 1\n")
        data = self.read("stories")
        self.assertEqual(data["status"], "observed")
        self.assertEqual(data["records"][0]["references"], [])
        self.assertNotIn("verdict", data)

    def test_story_references_and_dependency_text(self):
        self.story("\n## Context\n**ADR Governing Implementation**: ADR-0002\nRequirement: TR-core-001\n\n## Dependencies\nDepends on: story-000-seed.md\n")
        row = self.read("stories")["records"][0]
        self.assertEqual({r["id"] for r in row["references"]}, {"ADR-2", "TR-core-001"})
        self.assertEqual(row["fields"]["depends_on"]["value"], "story-000-seed.md")

    def test_story_criteria_inside_fence_are_not_counted(self):
        self.story("\n## Acceptance Criteria\n```\n- [x] example\n```\n- [ ] actual\n")
        self.assertEqual(self.read("stories")["records"][0]["acceptance_criteria"]["total"], 1)

    def test_duplicate_criteria_sections_are_ambiguous(self):
        self.story("\n## Acceptance Criteria\n- [ ] one\n## Acceptance Criteria\n- [ ] two\n")
        ac = self.read("stories")["records"][0]["acceptance_criteria"]
        self.assertEqual(ac["state"], "ambiguous")
        self.assertIsNone(ac["total"])

    def test_adr_self_cycle_is_retained(self):
        self.adr(1, "ADR-0001")
        graph = self.read("adrs")["graph"]
        self.assertEqual(graph["cycles"], [["ADR-1"]])
        self.assertIsNone(graph["order"])

    def test_adr_cycle_and_blocked_dependants(self):
        self.adr(1, "ADR-0002")
        self.adr(2, "ADR-0001")
        self.adr(3, "ADR-0002")
        graph = self.read("adrs")["graph"]
        self.assertEqual(graph["cycles"], [["ADR-1", "ADR-2"]])
        self.assertEqual(graph["blocked_by_cycle"], ["ADR-3"])

    def test_adr_dependency_first_order_is_structural_only(self):
        self.adr(1, "ADR-0002", status="Proposed")
        self.adr(2)
        graph = self.read("adrs")["graph"]
        self.assertEqual(graph["order"], ["ADR-2", "ADR-1"])
        self.assertTrue(graph["complete"])
        self.assertNotIn("ready", graph)

    def test_missing_dependency_has_no_complete_order(self):
        self.adr(1, "ADR-9999")
        graph = self.read("adrs")["graph"]
        self.assertEqual(graph["missing"], ["ADR-9999"])
        self.assertFalse(graph["complete"])
        self.assertIsNone(graph["order"])

    def test_unfilled_dependency_is_not_none(self):
        self.adr(1, "[ADR-NNNN or None]")
        row = self.read("adrs")
        self.assertEqual(row["records"][0]["dependencies"]["state"], "placeholder")
        self.assertFalse(row["graph"]["complete"])

    def test_empty_dependency_is_not_none(self):
        self.adr(1, "")
        self.assertFalse(self.read("adrs")["graph"]["complete"])

    def test_duplicate_adr_ids_are_not_merged(self):
        self.adr(1)
        self.adr(1, path="docs/architecture/adr-1-duplicate.md")
        graph = self.read("adrs")["graph"]
        self.assertEqual(graph["duplicate_ids"], ["ADR-1"])
        self.assertFalse(graph["complete"])

    def test_adr_heading_and_filename_id_conflict(self):
        self.write("docs/architecture/adr-0001-test.md", "# ADR-0002: Other\n## Status\nAccepted\n")
        data = self.read("adrs")
        self.assertEqual(data["status"], "partial")
        self.assertIsNone(data["records"][0]["id"])

    def test_dependency_markdown_link_is_not_placeholder(self):
        self.adr(1, "[ADR-0002](adr-0002-test.md)")
        self.adr(2)
        self.assertTrue(self.read("adrs")["graph"]["complete"])

    def test_duplicate_dependency_rows_are_ambiguous(self):
        p = self.adr(1)
        p.write_text(p.read_text() + "| **Depends On** | ADR-0002 |\n")
        self.assertEqual(self.read("adrs")["records"][0]["dependencies"]["state"], "ambiguous")

    def test_adr_dates_are_calendar_validated(self):
        p = self.adr(1)
        p.write_text(p.read_text() + "\n## Date\n2026-02-30\n")
        row = self.read("adrs")["records"][0]
        self.assertEqual(row["fields"]["date"]["state"], "invalid")

    def test_adr_multiline_status_does_not_hide_contradiction(self):
        self.adr(1, status="Accepted\nProposed")
        row = self.read("adrs")["records"][0]
        self.assertEqual(row["fields"]["status"]["state"], "ambiguous")

    def test_adr_header_and_section_status_are_reconciled(self):
        p = self.adr(1)
        p.write_text(p.read_text().replace("## Status", "Status: Proposed\n## Status"))
        self.assertEqual(self.read("adrs")["records"][0]["fields"]["status"]["state"], "ambiguous")

    def test_partial_graph_does_not_assert_no_cycles(self):
        p = self.adr(1)
        p.write_text(p.read_text() + "\n<!-- unterminated\n")
        graph = self.read("adrs")["graph"]
        self.assertFalse(graph["complete"])
        self.assertEqual(graph["cycle_state"], "NOT ASSESSED")

    def test_small_graphs_against_reachability_oracle(self):
        nodes = ["ADR-1", "ADR-2", "ADR-3"]
        pairs = [(a, b) for a in range(3) for b in range(3)]
        for mask in range(1 << len(pairs)):
            edges = [(a, b) for bit, (a, b) in enumerate(pairs) if mask & (1 << bit)]
            records = [{"id": node, "dependencies": {"state": "value", "ids": [nodes[b] for a, b in edges if a == i]}}
                       for i, node in enumerate(nodes)]
            reachable = [[(a, b) in edges for b in range(3)] for a in range(3)]
            for mid in range(3):
                for a in range(3):
                    for b in range(3):
                        reachable[a][b] |= reachable[a][mid] and reachable[mid][b]
            graph = FACTS.dependency_graph(records)
            cyclic = {nodes[i] for i in range(3) if reachable[i][i]}
            self.assertEqual({n for group in graph["cycles"] for n in group}, cyclic)
            expected_groups = {frozenset(nodes[j] for j in range(3) if reachable[i][j] and reachable[j][i])
                               for i in range(3) if reachable[i][i]}
            self.assertEqual({frozenset(group) for group in graph["cycles"]}, expected_groups)
            blocked = {nodes[i] for i in range(3) if nodes[i] not in cyclic and any(reachable[i][j] for j in range(3) if nodes[j] in cyclic)}
            self.assertEqual(set(graph["blocked_by_cycle"]), blocked)
            if not cyclic:
                self.assertEqual(set(graph["order"]), set(nodes))
                for a, b in edges:
                    self.assertLess(graph["order"].index(nodes[b]), graph["order"].index(nodes[a]))

    def test_gdd_alias_and_exact_headings(self):
        self.write("design/gdd/combat.md", "# Combat\n## 1. Overview\nDescription\n## Detailed Design\nRules\n## Formulas extra\nNo\n")
        row = self.read("gdds")["records"][0]
        self.assertEqual(row["sections"]["Overview"]["state"], "present")
        self.assertEqual(row["sections"]["Detailed Rules"]["state"], "present")
        self.assertEqual(row["sections"]["Formulas"]["state"], "missing")

    def test_gdd_examples_and_comments_do_not_supply_headings(self):
        self.write("design/gdd/combat.md", "# Combat\n```\n## Overview\n```\n<!--\n## Formulas\n-->\n")
        sections = self.read("gdds")["records"][0]["sections"]
        self.assertEqual(sections["Overview"]["state"], "missing")
        self.assertEqual(sections["Formulas"]["state"], "missing")

    def test_gdd_empty_placeholder_and_code_content(self):
        self.write("design/gdd/combat.md", "# Combat\n## Overview\n## Player Fantasy\n[To be designed]\n## Detailed Rules\n```\nx = 1\n```\n")
        sections = self.read("gdds")["records"][0]["sections"]
        self.assertEqual(sections["Overview"]["state"], "empty")
        self.assertEqual(sections["Player Fantasy"]["state"], "placeholder")
        self.assertEqual(sections["Detailed Rules"]["state"], "present")

    def test_gdd_duplicate_aliases_are_ambiguous(self):
        self.write("design/gdd/combat.md", "## Detailed Rules\nOne\n## Detailed Design\nTwo\n")
        data = self.read("gdds")
        self.assertEqual(data["records"][0]["sections"]["Detailed Rules"]["state"], "ambiguous")
        self.assertEqual(data["status"], "partial")

    def test_setext_headings_and_literal_trailing_hash(self):
        self.write("design/gdd/combat.md", "Overview\n--------\nText\n## Formulas#\nNot the Formulas heading\n")
        sections = self.read("gdds")["records"][0]["sections"]
        self.assertEqual(sections["Overview"]["state"], "present")
        self.assertEqual(sections["Formulas"]["state"], "missing")

    def test_gdd_index_is_not_a_system(self):
        self.write("design/gdd/systems-index.md", "# Index\n")
        self.assertEqual(self.read("gdds")["files_read"], 0)

    def test_bug_closure_record_does_not_replace_missing_header(self):
        self.write("production/qa/bugs/BUG-0001.md", "# Bug\n## Summary\nSeverity: S1-Critical\n## Closure Record\nStatus: Closed\n")
        row = self.read("bugs")["records"][0]
        self.assertEqual(row["fields"]["status"]["state"], "missing")

    def test_bug_counts_and_age_are_facts(self):
        self.write("production/qa/bugs/BUG-1-slug.md", "# Bug\n## Summary\nID: BUG-0001\nStatus: Closed?\nSeverity: S2-Major\nReported: 2026-10-01\n")
        data = self.read("bugs", today="2026-10-20")
        self.assertEqual(data["summary"]["statuses"], {"Closed?": 1})
        self.assertEqual(data["records"][0]["age_days"], 19)
        self.assertEqual(data["records"][0]["severity"], "S2")
        self.assertEqual(data["summary"]["severities"], {"S2": 1})
        self.assertNotIn("closed", data["summary"])

    def test_bug_triage_reports_are_not_bugs(self):
        self.write("production/qa/bugs/bug-triage-2026-10-20.md", "Status: Open\n")
        self.assertEqual(self.read("bugs")["files_read"], 0)

    def test_placeholder_bug_severity_is_unknown(self):
        self.write("production/qa/bugs/BUG-1.md", "Severity: [S1 / S2]\n")
        self.assertIsNone(self.read("bugs")["records"][0]["severity"])

    def test_explicit_paths_with_spaces_and_crlf(self):
        self.write("custom path/story.md", "# Story\r\nStatus: Ready\r\n")
        data = self.read("stories", ["custom path/story.md", "custom path/story.md"])
        self.assertEqual(data["files_read"], 1)
        self.assertEqual(data["records"][0]["fields"]["status"]["value"], "Ready")

    def test_missing_explicit_path_is_not_an_empty_scan(self):
        self.assertEqual(self.read("stories", ["missing.md"])["status"], "invalid")

    def test_partial_read_does_not_drop_failure(self):
        self.story()
        data = self.read("stories", ["production/epics/core/story-001-test.md", "missing.md"])
        self.assertEqual(data["status"], "partial")
        self.assertEqual(len(data["errors"]), 1)

    def test_unsafe_paths_rejected_before_read(self):
        for path in ("../outside.md", "/tmp/file.md", ".env", "dir/.env.local", "C:\\secret.md"):
            self.assertEqual(self.read("stories", [path])["status"], "invalid", path)

    def test_symlink_file_and_parent_are_rejected(self):
        real = self.write("real/story.md", "Status: Ready\n")
        (self.root / "link.md").symlink_to(real)
        (self.root / "linked").symlink_to(real.parent, target_is_directory=True)
        for path in ("link.md", "linked/story.md"):
            self.assertEqual(self.read("stories", [path])["status"], "invalid")

    def test_default_discovery_does_not_follow_link(self):
        self.story()
        (self.root / "production/epics/linked").symlink_to(self.root / "production/epics", target_is_directory=True)
        self.assertEqual(self.read("stories")["status"], "partial")

    def test_oversized_and_non_utf8_inputs_report_errors(self):
        p = self.write("large.md", "x" * (FACTS.MAX_BYTES + 1))
        self.assertEqual(self.read("gdds", ["large.md"])["status"], "invalid")
        p.write_bytes(b"\xff\xfe\x00")
        self.assertEqual(self.read("gdds", ["large.md"])["status"], "invalid")

    def test_scope_limits_refuse_truncated_observations(self):
        self.story()
        self.story(path="production/epics/core/story-002-test.md")
        old_files, old_entries = FACTS.MAX_FILES, FACTS.MAX_ENTRIES
        try:
            FACTS.MAX_FILES = 1
            limited = self.read("stories")
            self.assertEqual(limited["status"], "invalid")
            self.assertEqual(limited["files_read"], 0)
            FACTS.MAX_FILES = old_files
            FACTS.MAX_ENTRIES = 1
            limited = self.read("stories")
            self.assertEqual(limited["status"], "invalid")
            self.assertEqual(limited["files_read"], 0)
        finally:
            FACTS.MAX_FILES, FACTS.MAX_ENTRIES = old_files, old_entries
    def test_observation_is_read_only_and_cwd_independent(self):
        self.story()
        before = {str(p): p.read_bytes() for p in self.root.rglob("*") if p.is_file()}
        nested = self.root / "other"
        nested.mkdir()
        command = [sys.executable, str(PACKAGE / ".codex/lib/artifact_facts.py"), "--root", str(self.root), "stories"]
        result = subprocess.run(command, cwd=nested, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["files_read"], 1)
        self.assertEqual(before, {str(p): p.read_bytes() for p in self.root.rglob("*") if p.is_file()})

    def test_consumer_binding_guard(self):
        import validate_runtime
        path = Path(".agents/skills/bug-triage/SKILL.md")
        valid = "Use .codex/docs/artifact-inspection.md and artifact_facts.py bugs."
        self.assertEqual(validate_runtime.validate_config_consumer_text(path, valid), [])
        self.assertTrue(validate_runtime.validate_config_consumer_text(path, "Read bugs."))


def main():
    global FACTS, PACKAGE
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    args = parser.parse_args()
    PACKAGE = Path(args.root).resolve()
    path = PACKAGE / ".codex/lib/artifact_facts.py"
    if not path.is_file():
        print(json.dumps({"check": "artifact-facts", "status": "fail", "errors": ["missing artifact_facts.py"]}))
        return 1
    sys.path.insert(0, str(path.parent))
    spec = importlib.util.spec_from_file_location("ccgs_artifact_facts", path)
    FACTS = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(FACTS)
    result = unittest.TestResult()
    unittest.defaultTestLoader.loadTestsFromTestCase(ArtifactTests).run(result)
    errors = [case.id() + ": " + detail for case, detail in result.failures + result.errors]
    print(json.dumps({"check": "artifact-facts", "status": "pass" if result.wasSuccessful() else "fail",
                      "tests": result.testsRun, "errors": errors}, indent=2))
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    raise SystemExit(main())
