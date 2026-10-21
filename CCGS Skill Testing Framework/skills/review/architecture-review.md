# Skill Test Spec: $architecture-review

## Skill Summary

`$architecture-review` is an Opus-tier skill that validates a technical architecture
document against the project's 8 required architecture sections and checks that it
is internally consistent, non-contradictory with existing ADRs, and correctly
targeting the pinned engine version. It produces a verdict of APPROVED /
NEEDS REVISION / MAJOR REVISION NEEDED.

In `full` review mode, the skill spawns two director gate agents in parallel:
TD-ARCHITECTURE (technical-director) and LP-FEASIBILITY (lead-programmer). In
`lean` or `solo` mode, both gates are skipped and noted. Review is read-only until the user approves a specific systems-index or
registry/RTM update preview. Single-GDD writes remain scoped to that system.

---

## Static Assertions (Structural)

Verified automatically by `$skill-test static` — no fixture needed.

- [ ] Has the Codex metadata contract: `name` and `description` in frontmatter; ported fields in `## Ported metadata`, or an explicit Codex-native support classification
- [ ] Has ≥2 phase headings
- [ ] Contains verdict keywords: APPROVED, NEEDS REVISION, MAJOR REVISION NEEDED
- [ ] Requires approval before optional index/registry/RTM writes
- [ ] Has a next-step handoff at the end
- [ ] Documents gate behavior: TD-ARCHITECTURE + LP-FEASIBILITY in full mode; skipped in lean/solo

---

## Director Gate Checks

In `full` mode: TD-ARCHITECTURE (technical-director) and LP-FEASIBILITY
(lead-programmer) are spawned in parallel after the skill reads the architecture doc.

In `lean` mode: both gates are skipped. Output notes:
"TD-ARCHITECTURE skipped — lean mode" and "LP-FEASIBILITY skipped — lean mode".

In `solo` mode: both gates are skipped with equivalent notes.

---

## Test Cases

### Case 1: Happy Path — Complete architecture doc in full mode

**Fixture:**
- `docs/architecture/architecture.md` exists with all 8 required sections populated
- All sections reference the correct engine version from `docs/engine-reference/`
- No contradictions with existing Accepted ADRs in `docs/architecture/`
- `production/session-state/review-mode.txt` contains `full`

**Input:** `$architecture-review docs/architecture/architecture.md`

**Expected behavior:**
1. Skill reads the architecture document
2. Skill reads existing ADRs for cross-reference
3. Skill reads engine version reference
4. TD-ARCHITECTURE and LP-FEASIBILITY gate agents spawn in parallel
5. Both gates return APPROVED
6. Skill outputs section-by-section completeness check (8/8 sections present)
7. Verdict: APPROVED

**Assertions:**
- [ ] All 8 required sections are checked and reported
- [ ] TD-ARCHITECTURE and LP-FEASIBILITY spawn in parallel (not sequentially)
- [ ] Verdict is APPROVED when all sections are present and no conflicts exist
- [ ] Skill does NOT write any files without approval
- [ ] Next-step handoff to `$create-control-manifest` or `$create-epics` is present

---

### Case 2: Failure Path — Missing required sections

**Fixture:**
- `docs/architecture/architecture.md` exists but is missing at least 2 required sections
  (e.g., no data model section, no error handling section)
- `production/session-state/review-mode.txt` contains `full`

**Input:** `$architecture-review docs/architecture/architecture.md`

**Expected behavior:**
1. Skill reads the document and identifies missing sections
2. Section completeness shows fewer than 8/8 sections present
3. Missing sections are listed by name with specific remediation guidance
4. Verdict: MAJOR REVISION NEEDED (≥2 missing sections)

**Assertions:**
- [ ] Verdict is MAJOR REVISION NEEDED (not APPROVED or NEEDS REVISION) for ≥2 missing sections
- [ ] Each missing section is named explicitly in the output
- [ ] Remediation guidance is specific (what to add, not just "add missing sections")
- [ ] Skill does NOT pass a document missing required sections

---

### Case 3: Partial Path — Architecture contradicts an existing ADR

**Fixture:**
- `docs/architecture/architecture.md` exists with all 8 sections present
- One Accepted ADR in `docs/architecture/` establishes a constraint that the architecture doc contradicts
  (e.g., ADR-001 mandates ECS pattern; architecture.md describes a different pattern for the same system)

**Input:** `$architecture-review docs/architecture/architecture.md`

**Expected behavior:**
1. Skill reads the architecture doc and all existing ADRs
2. Conflict is detected between the architecture doc and the named ADR
3. Conflict entry names: the ADR number/title, the contradicting sections, and impact
4. Verdict: NEEDS REVISION (conflict exists but structure is otherwise sound)

**Assertions:**
- [ ] Verdict is NEEDS REVISION (not MAJOR REVISION NEEDED for a single contradiction)
- [ ] The specific ADR number and title are named in the conflict entry
- [ ] The contradicting sections in both documents are identified
- [ ] Skill does NOT auto-resolve the contradiction

---

### Case 4: Edge Case — File not found

**Fixture:**
- The path provided does not exist in the project

**Input:** `$architecture-review docs/architecture/nonexistent.md`

**Expected behavior:**
1. Skill attempts to read the file
2. File not found
3. Skill outputs a clear error naming the missing file
4. Skill suggests checking `docs/architecture/` or running `$create-architecture`
5. Skill does NOT produce a verdict

**Assertions:**
- [ ] Skill outputs a clear error when the file is not found
- [ ] No verdict is produced (APPROVED / NEEDS REVISION / MAJOR REVISION NEEDED)
- [ ] Skill suggests a corrective action
- [ ] Skill does NOT crash or produce a partial report

---

### Case 5: Director Gate — Full mode spawns both gates; solo mode skips both

**Fixture (full mode):**
- `docs/architecture/architecture.md` exists with all 8 sections
- `production/session-state/review-mode.txt` contains `full`

**Full mode expected behavior:**
1. TD-ARCHITECTURE gate spawns
2. LP-FEASIBILITY gate spawns in parallel with TD-ARCHITECTURE
3. Both gates complete before verdict is issued

**Assertions (full mode):**
- [ ] TD-ARCHITECTURE and LP-FEASIBILITY both appear in the output as completed gates
- [ ] Both gates spawn in parallel (not one after the other)
- [ ] Verdict reflects gate feedback

**Fixture (solo mode):**
- Same architecture doc
- `production/session-state/review-mode.txt` contains `solo`

**Solo mode expected behavior:**
1. Skill reads the architecture doc
2. Gates are NOT spawned
3. Output notes: "TD-ARCHITECTURE skipped — solo mode" and "LP-FEASIBILITY skipped — solo mode"
4. Verdict is based on structural checks only

**Assertions (solo mode):**
- [ ] Neither TD-ARCHITECTURE nor LP-FEASIBILITY appears as an active gate
- [ ] Both skipped gates are noted in the output
- [ ] Verdict is still produced based on the structural check alone

---

## Protocol Compliance

- [ ] Does NOT write any files without an approved update preview
- [ ] Presents section completeness check before issuing verdict
- [ ] TD-ARCHITECTURE and LP-FEASIBILITY spawn in parallel in full mode
- [ ] Skipped gates are noted by name and mode in lean/solo output
- [ ] Verdict is one of exactly: APPROVED, NEEDS REVISION, MAJOR REVISION NEEDED
- [ ] Ends with next-step handoff appropriate to verdict

---

## Coverage Notes

- The 8 required architecture sections are project-specific; tests use the
  section list defined in the skill body — not re-enumerated here.
- Engine version compatibility checking (cross-referencing `docs/engine-reference/`)
  is part of Case 1's happy path but not independently fixture-tested.
- RTM (requirement traceability matrix) mode is a separate concern covered by
  the `$architecture-review` skill's own `rtm` argument mode, not tested here.

## Phase 1 Backport Regression Cases

These assertions require workflow evaluation; adding them is not a passing test run.

- [ ] Given `single-gdd combat` with inventory registry/index/RTM rows present,
  preview and update only combat rows after approval. Preserve inventory content,
  comments, ordering, and existing identifiers.
- [ ] Re-read all target files immediately before applying the approved patch;
  drift requires a revised preview rather than overwriting intervening changes.
- [ ] New IDs exceed the highest ever allocated ID, including deprecated rows.
  Never recycle identifiers or deprecate unrelated requirements.
- [ ] A safe bounded patch that cannot be identified results in report-only
  output; it does not fall back to rebuilding the shared files.
- [ ] The report identifies `single-gdd` scope and cannot satisfy a full-system
  architecture gate merely because its local verdict passes.

## Phase 4B workflow and stage acceptance

Status: NOT RUN — native skill behavior requires a separate observed invocation.
The executable project-config/hook tests verify resolution, not this skill run.

- Run with no selected rigor/workflow: retain compatibility requirements and show
  the unset source; do not select minimal or standard implicitly.
- Run with explicit minimal, standard and full fixtures. Apply
  `.codex/docs/workflow-modes.md` before required-artifact checks, report source,
  and preserve existing optional documents. Standard numeric rules require
  Formulas; Detailed Design and Detailed Rules are aliases.
- For named systems, resolve the GDD filename stem per item. A future authoring
  stem is valid; a gate reports unmatched keys without silently applying them.
- When this skill plans or implements minimal work, use the brief's numbered MVP
  requirements. Do not demand optional registry/ADR/sprint artifacts, invent IDs,
  or waive concrete criteria and current story-type evidence requirements.
- When this skill reads/updates stage, use the shared reader and approved target.
  Test YAML overriding a stale legacy stage, unset stage, invalid configuration,
  and terminal Live. A declined write changes nothing; success needs readback.
- A no-input or zero-required-check review is NOT ASSESSED or explicitly NOT
  APPLICABLE, never evidence of a passing review or permission to advance.

## Phase 4C consumer acceptance

Status: NOT RUN — these cases need an observed native skill invocation.
The executable configuration tests validate resolution, not this workflow.

- Verify `technical` values/sources against YAML, legacy literals and actual pin
  files. Unmapped custom prose remains visible; wrong/missing pins and runners
  are not successful setup. Preserve custom routing and actual installed tools.
- For QA consumers, run every level with missing/failed required evidence and
  false strictness: closure/admission stays blocked. Check true strictness on
  an otherwise-advisory finding. Full adds affected-path regression evidence;
  an active coverage target needs an applicable measured report, not test counts.
- For team consumers, compare individual/small/studio and unconfigured rosters.
  Only explicitly optional participation changes. Required owners, conditional
  owners whose conditions hold, and surviving review gates remain present.
- Verify optional performance enforcement with measured data, missing data and
  estimates. Estimates never pass compliance. Off does not waive an acceptance
  criterion or erase an observed failure.
- Verify setup previews name every affected file, retain approval across the
  unchanged scope, reject stale previews, and re-read actual writes. No config
  reader installs, migrates, spawns, commits or changes root YAML by itself.

## Phase 5B artifact-reader acceptance

Status: NOT RUN — requires an observed native skill invocation. Parser/graph
fixtures alone do not establish this skill's behavior.

- Keep the workflow's selected scope and call the applicable artifact readers.
  Verify source paths/lines and read incomplete or ambiguous values as unknown.
- Exercise absent files, duplicate metadata, code/comment examples, empty
  sections and nonstandard layouts. Empty discovery cannot establish a PASS,
  zero open bugs, a ready story or a completed quality review.
- Apply existing tier and evidence rules after reading facts. Missing optional
  TR/ADR/GDD artifacts in minimal workflows remain N/A where permitted; named
  broken references and actual missing evidence keep their existing effect.
- For ADR graphs retain self-loops, multi-node cycles, missing/duplicate IDs and
  unknown dependencies. A partial graph yields no complete implementation order.
- Preserve incremental-review receipts, sprint scope, consolidated-bug fallbacks
  and source header status versus evidence/closure status. Counts do not
  authorize edits, closure, new priorities, stage changes or role dispatch.
