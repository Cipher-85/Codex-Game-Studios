# Skill Test Spec: $story-readiness

## Skill Summary

`$story-readiness` validates that a story file is ready for a developer to
pick up and implement. It checks four dimensions: Design (embedded GDD
requirements), Architecture (ADR references and status), Scope (clear
boundaries and DoD), and Definition of Done (testable criteria). It produces
a READY / NEEDS WORK / BLOCKED verdict. It is a read-only skill and runs
before any developer picks up a story.

---

## Static Assertions (Structural)

Verified automatically by `$skill-test static` — no fixture needed.

- [ ] Has the Codex metadata contract: `name` and `description` in frontmatter; ported fields in `## Ported metadata`, or an explicit Codex-native support classification
- [ ] Has ≥2 phase headings or numbered check sections
- [ ] Contains verdict keywords: READY, NEEDS WORK, BLOCKED
- [ ] Does NOT require "May I write" language (read-only skill)
- [ ] Has a next-step handoff (what to do after verdict)

---

## Test Cases

### Case 1: Happy Path — Fully ready story

**Fixture:**
- Story file exists at `production/epics/core/story-light-pickup.md`
- Story contains:
  - `TR-ID: TR-light-001` (GDD requirement reference)
  - `ADR: docs/architecture/adr-003-inventory.md`
  - Referenced ADR exists and has status `Accepted`
  - Referenced TR-ID exists in `docs/architecture/tr-registry.yaml`
  - Story has `## Acceptance Criteria` with ≥3 testable items
  - Story has `## Definition of Done` section
  - Story has `Status: Ready for Dev`
  - Manifest version in story header matches current `docs/architecture/control-manifest.md`

**Input:** `$story-readiness production/epics/core/story-light-pickup.md`

**Expected behavior:**
1. Skill reads the story file
2. Skill reads the referenced ADR — verifies status is `Accepted`
3. Skill reads `docs/architecture/tr-registry.yaml` — verifies TR-ID exists
4. Skill reads `docs/architecture/control-manifest.md` — verifies manifest version matches
5. Skill evaluates all 4 dimensions (Design, Architecture, Scope, DoD)
6. Skill outputs READY verdict with all checks passing

**Assertions:**
- [ ] Skill reads the referenced ADR file (not just the story)
- [ ] Skill verifies ADR status is `Accepted` (not `Proposed`)
- [ ] Skill reads `tr-registry.yaml` to verify TR-ID exists
- [ ] Output includes check results for all 4 dimensions
- [ ] Verdict is READY when all checks pass
- [ ] Skill does not write any files

---

### Case 2: Blocked Path — Referenced ADR is Proposed (not Accepted)

**Fixture:**
- Story file exists with `ADR: docs/architecture/adr-005-light-system.md`
- `adr-005-light-system.md` exists but has `Status: Proposed`
- All other story content is otherwise complete

**Input:** `$story-readiness production/epics/core/story-light-system.md`

**Expected behavior:**
1. Skill reads the story
2. Skill reads `adr-005-light-system.md` — finds `Status: Proposed`
3. Skill flags this as a BLOCKING issue (cannot implement against unaccepted ADR)
4. Skill outputs BLOCKED verdict
5. Skill recommends: accept or reject the ADR before picking up the story

**Assertions:**
- [ ] Verdict is BLOCKED (not NEEDS WORK or READY) when ADR is Proposed
- [ ] Output explicitly names the Proposed ADR as the blocker
- [ ] Output recommends resolving ADR status before proceeding
- [ ] Skill does not output READY regardless of other checks passing

---

### Case 3: Needs Work — Missing Acceptance Criteria

**Fixture:**
- Story file exists but has no `## Acceptance Criteria` section
- ADR reference exists and is `Accepted`
- TR-ID exists in registry
- Manifest version matches

**Input:** `$story-readiness production/epics/core/story-oxygen-drain.md`

**Expected behavior:**
1. Skill reads the story
2. Skill finds no Acceptance Criteria section
3. Skill flags this as a NEEDS WORK issue (story is incomplete, not blocked)
4. Skill outputs NEEDS WORK verdict
5. Skill names the missing section and suggests adding measurable criteria

**Assertions:**
- [ ] Verdict is NEEDS WORK (not BLOCKED or READY) when Acceptance Criteria section is absent
- [ ] Output identifies the missing Acceptance Criteria section specifically
- [ ] Output suggests adding testable/measurable criteria
- [ ] Skill distinguishes NEEDS WORK (fixable without external dependencies) from BLOCKED (requires outside action)

---

### Case 4: Edge Case — Stale manifest version

**Fixture:**
- Story file has `Manifest Version: 2026-01-15` in its header
- `docs/architecture/control-manifest.md` has `Manifest Version: 2026-03-10`
- Versions do not match (story was created before manifest was updated)

**Input:** `$story-readiness production/epics/core/story-mirror-rotation.md`

**Expected behavior:**
1. Skill reads the story and extracts manifest version `2026-01-15`
2. Skill reads control manifest header and extracts current version `2026-03-10`
3. Skill detects version mismatch
4. Skill flags this as an ADVISORY issue (not blocking, but worth noting)
5. Verdict is NEEDS WORK with manifest staleness noted

**Assertions:**
- [ ] Skill reads `docs/architecture/control-manifest.md` to get current version
- [ ] Skill compares story's embedded manifest version against current manifest version
- [ ] Stale manifest version results in NEEDS WORK (not BLOCKED, not READY)
- [ ] Output explains that the story's embedded guidance may be outdated

---

---

### Case 5: Director Gate — QL-STORY-READY behavior across review modes

**Fixture:**
- Story file exists and is READY (all 4 dimensions pass, ADR Accepted, criteria present)
- `production/review-mode.txt` exists

**Case 5a — full mode:**
- `review-mode.txt` contains `full`

**Input:** `$story-readiness production/epics/core/story-light-pickup.md` (full mode)

**Expected behavior:**
1. Skill reads review mode — determines `full`
2. After completing its own 4-dimension check, skill invokes QL-STORY-READY gate
3. QA lead reviews the story for readiness
4. If QA lead verdict is INADEQUATE → story verdict is BLOCKED regardless of 4-dimension result
5. If QA lead verdict is ADEQUATE → verdict proceeds normally

**Assertions (5a):**
- [ ] Skill reads review mode before deciding whether to invoke QL-STORY-READY
- [ ] QL-STORY-READY gate is invoked in full mode after the 4-dimension check completes
- [ ] A QA lead INADEQUATE verdict overrides a READY 4-dimension result → final verdict BLOCKED
- [ ] Gate invocation is noted in output: "Gate: QL-STORY-READY — [result]"

**Case 5b — lean or solo mode:**
- `review-mode.txt` contains `lean` or `solo`

**Expected behavior:**
1. Skill reads review mode — determines `lean` or `solo`
2. QL-STORY-READY gate is SKIPPED
3. Output notes the skip: "[QL-STORY-READY] skipped — Lean/Solo mode"
4. Verdict is based on 4-dimension check only

**Assertions (5b):**
- [ ] QL-STORY-READY gate does NOT spawn in lean or solo mode
- [ ] Skip is explicitly noted in output
- [ ] Verdict is based on 4-dimension check alone

---

## Protocol Compliance

- [ ] Does NOT use Write or Edit tools (read-only skill)
- [ ] Presents complete check results before verdict
- [ ] Does not ask for approval (no file writes)
- [ ] Ends with recommended next step (fix issues or proceed to implementation)
- [ ] Distinguishes three verdict levels clearly (READY vs NEEDS WORK vs BLOCKED)

---

## Coverage Notes

- Case where TR-ID is missing from the registry entirely is not explicitly
  tested here; it follows the same NEEDS WORK pattern as Case 3.
- The "no argument" path (skill auto-detecting the current story) is not
  tested because it depends on `production/session-state/active.md` content,
  which is hard to fixture reliably.
- Stories with multiple ADR references are not tested; behavior is assumed to
  be additive (all ADRs must be Accepted for READY verdict).

## Review routing coverage (Phase 4A)

Use the shared `review-mode` contract in `.codex/docs/director-gates.md`.
Legacy `production/review-mode.txt` fixtures below remain fallback cases; also
exercise project/local YAML, explicit rigor, and a per-run `--review` override.

- [ ] Observe actual declared director gates using the returned value/source;
      the flag wins over local YAML and is not persisted.
- [ ] Invalid configuration stops director routing with diagnostics. Missing
      tooling is NOT ASSESSED; neither case silently selects a review mode.
- [ ] Review settings preserve existing evidence requirements and write approvals.

These are native behavioral assertions. Resolver/hook/static audits alone do not
establish that this skill or a role agent executed.

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
