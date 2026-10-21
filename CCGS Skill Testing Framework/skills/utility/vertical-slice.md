# Skill Test Spec: $vertical-slice

> **Category**: utility
> **Priority**: low
> **Spec written**: 2026-07-03
> **Coverage note**: Codex-added spec. The pinned upstream testing framework had
> no `vertical-slice` skill spec; this file closes that inherited coverage gap.

## Skill Summary

`$vertical-slice` runs late Pre-Production validation for one production-quality
end-to-end loop. It loads GDD, architecture, UX, and control-manifest context;
defines a falsifiable validation question; asks the user to confirm scope before
building; writes isolated slice files under `prototypes/[concept-name]-vertical-slice/`
only after approval; collects playtest observations; and generates a REPORT.md
with velocity data and a PROCEED/PIVOT/KILL recommendation.

---

## Static Assertions

- [ ] Has the Codex metadata contract: `name` and `description` in frontmatter; ported fields in `## Ported metadata`, or an explicit Codex-native support classification
- [ ] Has 2+ phase headings
- [ ] Contains verdict keywords: PROCEED, PIVOT, KILL
- [ ] Contains "May I create the vertical slice directory" before implementation files are created
- [ ] Requires report generation before final recommendation
- [ ] Contains Codex worktree guidance for isolated prototype/slice changes

---

## Director Gate Checks

- **Full mode**: Spawns `creative-director` using gate `CD-PLAYTEST` after REPORT.md exists and game pillars/core fantasy are available.
- **Lean mode**: Skips CD-PLAYTEST and states that lean mode does not run this phase gate.
- **Solo mode**: Skips CD-PLAYTEST and states that solo mode runs without director review.

---

## Test Cases

### Case 1: PROCEED — Full Loop Validated

**Fixture:**
- `design/gdd/game-concept.md` exists with core fantasy and game pillars
- `design/gdd/systems-index.md` lists MVP systems
- `docs/architecture/architecture.md` and `docs/architecture/control-manifest.md` exist
- Review mode: `lean`

**Input:** `$vertical-slice`

**Expected behavior:**
1. Skill reads required GDD and architecture context.
2. Skill defines a validation question covering player experience and build feasibility.
3. Skill presents a 3-5 minute slice scope and asks for confirmation before building.
4. Skill asks permission before creating `prototypes/[concept-name]-vertical-slice/`.
5. After playtest debrief, skill writes REPORT.md only after approval.
6. Final verdict is PROCEED when the full loop is completed without guidance and velocity supports Production.

**Assertions:**
- [ ] Scope includes start, challenge, and resolution
- [ ] REPORT.md includes core loop validation, feel assessment, technical findings, and velocity log
- [ ] Lean mode skips CD-PLAYTEST with an explicit skip note
- [ ] Final recommendation routes to `$create-epics`, `$create-stories`, `$sprint-plan`, and `$gate-check pre-production`
- [ ] Verdict is PROCEED

**Case Verdict**: PASS / FAIL / PARTIAL

---

### Case 2: PIVOT — Loop or Pipeline Needs Revision

**Fixture:**
- Same context as Case 1
- Playtest observations show one core system works but the full loop fails or pipeline velocity is unrealistic

**Input:** `$vertical-slice`

**Expected behavior:**
1. Skill records specific failed system, loop, architecture, or pipeline evidence.
2. Skill asks what worked and what failed before writing a PIVOT-NOTE.md.
3. Skill asks permission before writing `prototypes/[concept-name]-vertical-slice/PIVOT-NOTE.md`.
4. Final routing sends the project back to affected GDD or architecture revision before re-running `$vertical-slice`.

**Assertions:**
- [ ] Verdict is PIVOT
- [ ] PIVOT-NOTE.md content includes what worked, what failed, and what the next slice should prove differently
- [ ] Skill does not advance to Production
- [ ] Next steps include `$design-system [mechanic]` or `$architecture-decision` before re-running `$vertical-slice`

**Case Verdict**: PASS / FAIL / PARTIAL

---

### Case 3: KILL — Concept Fails Slice Validation

**Fixture:**
- Same context as Case 1
- Playtest observations show no emotional high point, repeated confusion, and major architecture rework

**Input:** `$vertical-slice`

**Expected behavior:**
1. Skill asks the KILL confirmation checklist before finalizing the verdict.
2. If 2+ checklist items apply, skill treats KILL as sound.
3. Skill asks permission before appending to `prototypes/GRAVEYARD.md`.
4. Final routing returns to `$brainstorm` or `$prototype [new-concept]`.

**Assertions:**
- [ ] Verdict is KILL
- [ ] At least two KILL checklist criteria are documented
- [ ] GRAVEYARD entry includes kill reason, what worked at slice quality, what failed, and next time
- [ ] Skill does not suggest Production planning

**Case Verdict**: PASS / FAIL / PARTIAL

---

### Case 4: Missing Pre-Production Context — Blocks Before Build

**Fixture:**
- `design/gdd/game-concept.md` exists
- `docs/architecture/control-manifest.md` is missing

**Input:** `$vertical-slice`

**Expected behavior:**
1. Skill reports missing architecture/control context.
2. Skill does not create `prototypes/`.
3. Skill routes to architecture completion before slice implementation.

**Assertions:**
- [ ] Missing context is surfaced before implementation planning
- [ ] No slice directory is created
- [ ] User receives a concrete next step such as `$create-architecture` or `$create-control-manifest`

**Case Verdict**: PASS / FAIL / PARTIAL

---

### Case 5: Full Review Mode — CD-PLAYTEST Gate

**Fixture:**
- Full Case 1 context exists
- `production/review-mode.txt` contains `full`
- REPORT.md exists with a preliminary PROCEED/PIVOT/KILL recommendation

**Input:** `$vertical-slice`

**Expected behavior:**
1. Skill spawns `creative-director` with gate `CD-PLAYTEST`.
2. Prompt includes REPORT.md content, validation question, game pillars, and core fantasy.
3. Creative director verdict is treated as final.
4. REPORT.md is updated if the director changes the recommendation.

**Assertions:**
- [ ] CD-PLAYTEST fires only after report evidence exists
- [ ] Gate receives pillars/core fantasy and the full report
- [ ] A director override updates the final recommendation
- [ ] Skill does not auto-advance past CONCERNS or a changed verdict

**Case Verdict**: PASS / FAIL / PARTIAL

---

## Protocol Compliance

- [ ] Confirms scope before building
- [ ] Asks before creating `prototypes/[concept-name]-vertical-slice/`
- [ ] Keeps slice code isolated from production source
- [ ] Requires playtest debrief before report generation
- [ ] Writes REPORT.md only after approval
- [ ] Ends with a clear PROCEED/PIVOT/KILL recommendation and next route

---

## Coverage Notes

This spec covers workflow behavior and verdict routing. It does not validate
engine-specific implementation quality, actual playtest feel, or real build
velocity without a live slice run.

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
