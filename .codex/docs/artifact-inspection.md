# Artifact inspection

Use this contract when a workflow summarizes story, ADR, GDD or bug files.
`artifact_facts.py` supplies deterministic observations; the invoking workflow
owns quality judgments, required artifacts, readiness and action approval.

## Commands and scope

Run from the bound project, or use the installed helper's absolute path and
`--root <bound-root>` from another directory:

```bash
python3 .codex/lib/artifact_facts.py stories production/epics/core/story-001.md
python3 .codex/lib/artifact_facts.py adrs
python3 .codex/lib/artifact_facts.py gdds design/gdd/combat.md
python3 .codex/lib/artifact_facts.py bugs --today 2026-10-20
```

Pass exact repository-relative files for an already selected scope. With no
files, defaults are `production/epics/**/story-*.md`, top-level
`docs/architecture/adr-*.md`, system Markdown files directly in `design/gdd/`,
and top-level `production/qa/bugs/BUG-<number>[-slug].md`. Known GDD indexes and
cross-review reports are excluded. A sprint plan, incremental review or custom
layout determines its own file selection; do not replace that selection with
the defaults. Consolidated bug logs and QA report tables retain their existing
manual-reading fallback. Absence from these defaults does not prove absence
from the project.

The helper reads UTF-8 Markdown only, up to 1 MiB per file, 2,000 files and
20,000 discovery entries. It rejects absolute/traversal/secret paths and links,
including linked parents, without reading their targets. Recursive discovery
reports links it cannot inspect. It never runs commands from artifacts or
follows their references. It writes no cache, receipt, registry or artifact.
The filesystem must remain stable during a read; concurrent hostile path swaps
are outside this reader's boundary. Use the existing review receipts when a
workflow requires persistent content-change evidence.

## Read the result

JSON contains the selected scope, discovered/read counts, records, exclusions,
diagnostics and errors. Each record identifies its path, content hash and
relevant source lines. `applied` is always false and `assessment` is always
`NOT ASSESSED`: these are observations, not a completed workflow.

| Status | Meaning |
| --- | --- |
| `observed` | Selected files were read without parsing ambiguity; missing fields are still reported |
| `empty` | No matching files; inspect scope and existing workflow prerequisites |
| `partial` | Some observations exist, but a read error or parsing ambiguity needs attention |
| `invalid` | Scope/input failed; no usable complete inspection |

Exit 0 covers `observed` and `empty`; exit 2 covers `partial`, `invalid` and
command-line errors. Never derive a PASS or a complete graph from exit 0 alone.
Read field states (`value`, `missing`, `empty`, `placeholder`, `ambiguous`,
`invalid`, or `unknown`) and the errors. Keep unreadable or ambiguous values
unassessed; do not silently select the first duplicate. Resolve the ambiguity
from its source or report what remains unknown.

The reader understands ATX/setext headings, numbered section names, common
bold/bulleted metadata and the shipped tables. Fenced or indented code and HTML
comments do not supply metadata/headings. Code can still make a section
nonempty. This is not a full Markdown renderer or a substitute for reading
content and custom formats.

## Applying observations

- **Stories:** Header status is separate from Test Evidence status. Criterion
  and QA-case counts describe the text; they do not prove testability, coverage,
  completion or evidence. Missing TR/ADR references are facts, not automatic
  failures: apply `workflow-modes.md`, including brief-linked minimal stories.
- **ADRs:** Status text is reported as written. Graph nodes normalize numeric
  ADR IDs across padding, retain self-loops, and expose duplicate/missing IDs
  and unknown dependencies. `complete` means the dependency input was complete,
  not that ADRs were Accepted. `order` is available only for a complete acyclic
  graph and is structural ordering, not implementation authorization. Cycles
  are strongly connected groups; `blocked_by_cycle` names other dependants.
  Partial graphs cannot establish that no cycle exists.
- **GDDs:** Section states distinguish missing, empty, placeholder, present and
  ambiguous; Detailed Design aliases Detailed Rules. Present content is not
  quality approval. Apply per-system tier requirements and read the content to
  decide whether numeric rules require Formulas.
- **Bugs:** Counts preserve raw status text and unknown severity. Apply the
  invoking workflow's open/closed and priority rules; a closure-record status
  cannot replace the report header. Ages use Reported and the chosen date;
  malformed/future dates remain visible. Counts neither close nor prioritize
  bugs and cannot establish release readiness.

Keep existing read-only phases running until their normal decision point.
This helper adds no role dispatch, file-write approval, stage advancement,
continuity operation or automatic next-task selection. Actual skill and engine
acceptance remains separate from `audit.sh artifact-facts` fixture results.

Selectively adapted from upstream v1.2.0 at
`05ad7c8a5b8aa2aa86bbd3439ae7cf7295cac418`: story-facts, story-status,
adr-status, adr-dep-graph, gdd-structure-check and bug-stats. The upstream
shell scripts are not Codex runtime dependencies.
