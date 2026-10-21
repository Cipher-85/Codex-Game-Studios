# Skill Test Spec: $qa-plan

## Skill Summary

`$qa-plan` generates a structured QA test plan for a feature or sprint milestone.
It reads story files for the specified sprint, extracts acceptance criteria from
each story, cross-references test standards from `coding-standards.md` to assign
the appropriate test type (unit, integration, visual, UI, or config/data), and
produces a prioritized QA plan document.

The skill asks "May I write to `production/qa/qa-plan-sprint-NNN.md`?" before
persisting the output. If an existing test plan for the same sprint is found, the
skill offers to update rather than replace. The verdict is COMPLETE when the plan
is written. No director gates are used — gate-level story readiness is handled by
`$story-readiness`.

---

## Static Assertions (Structural)

Verified automatically by `$skill-test static` — no fixture needed.

- [ ] Has the Codex metadata contract: `name` and `description` in frontmatter; ported fields in `## Ported metadata`, or an explicit Codex-native support classification
- [ ] Has ≥2 phase headings
- [ ] Contains verdict keyword: COMPLETE
- [ ] Contains "May I write" collaborative protocol language before writing the plan
- [ ] Has a next-step handoff (e.g., `$smoke-check` or `$story-readiness`)

---

## Director Gate Checks

None. `$qa-plan` is a planning utility. Story readiness gates are separate.

---

## Test Cases

### Case 1: Happy Path — Sprint with 4 stories generates full test plan

**Fixture:**
- `production/sprints/sprint-003.md` lists 4 stories with defined acceptance criteria
- Stories span types: 1 logic (formula), 1 integration, 1 visual, 1 UI
- `coding-standards.md` is present with test evidence table

**Input:** `$qa-plan sprint-003`

**Expected behavior:**
1. Skill reads sprint-003.md and identifies 4 stories
2. Skill reads each story's acceptance criteria
3. Skill assigns test types per coding-standards.md table:
   - Logic story → Unit test (BLOCKING)
   - Integration story → Integration test (BLOCKING)
   - Visual story → Screenshot + lead sign-off (ADVISORY)
   - UI story → Manual walkthrough doc (ADVISORY)
4. Skill drafts QA plan with story-by-story test type breakdown
5. Skill asks "May I write to `production/qa/qa-plan-sprint-003.md`?"
6. File is written on approval; verdict is COMPLETE

**Assertions:**
- [ ] All 4 stories are included in the plan
- [ ] Test type is assigned per coding-standards.md (not guessed)
- [ ] Gate level (BLOCKING vs ADVISORY) is noted for each story
- [ ] "May I write" is asked with the correct file path
- [ ] Verdict is COMPLETE

---

### Case 2: Story With No Acceptance Criteria — Flagged as UNTESTABLE

**Fixture:**
- `production/sprints/sprint-004.md` lists 3 stories; one story has empty
  acceptance criteria section

**Input:** `$qa-plan sprint-004`

**Expected behavior:**
1. Skill reads all 3 stories
2. Skill detects the story with no AC
3. Story is flagged as `UNTESTABLE — Acceptance Criteria required` in the plan
4. Other 2 stories receive normal test type assignments
5. Plan is written with the UNTESTABLE story flagged; verdict is COMPLETE

**Assertions:**
- [ ] UNTESTABLE label appears for the story with no AC
- [ ] Plan is not blocked — the other stories are still planned
- [ ] Output suggests adding AC to the flagged story (next step)
- [ ] Verdict is COMPLETE (the plan is still generated)

---

### Case 3: Existing Test Plan Found — Offers update rather than replace

**Fixture:**
- `production/qa/qa-plan-sprint-003.md` already exists from a previous run
- Sprint-003 has 2 new stories added since the last plan

**Input:** `$qa-plan sprint-003`

**Expected behavior:**
1. Skill reads sprint-003.md and detects 2 stories not in the existing plan
2. Skill reports: "Existing QA plan found for sprint-003 — offering to update"
3. Skill presents the 2 new stories and their proposed test assignments
4. Skill asks "May I update `production/qa/qa-plan-sprint-003.md`?" (not overwrite)
5. Updated plan is written on approval

**Assertions:**
- [ ] Skill detects the existing plan file
- [ ] "update" language is used (not "overwrite")
- [ ] Only new stories are proposed for addition — existing entries preserved
- [ ] Verdict is COMPLETE

---

### Case 4: No Stories Found for Sprint — Error with guidance

**Fixture:**
- `production/sprints/sprint-007.md` does not exist
- No other sprint file matching sprint-007

**Input:** `$qa-plan sprint-007`

**Expected behavior:**
1. Skill attempts to read sprint-007.md — file not found
2. Skill outputs: "No sprint file found for sprint-007"
3. Skill suggests running `$sprint-plan` to create the sprint first
4. No plan is written; no "May I write" is asked

**Assertions:**
- [ ] Error message names the missing sprint file
- [ ] `$sprint-plan` is suggested as the remediation step
- [ ] No write tool is called
- [ ] Verdict is not COMPLETE (error state)

---

### Case 5: Director Gate Check — No gate; QA planning is a utility

**Fixture:**
- Sprint with valid stories and AC

**Input:** `$qa-plan sprint-003`

**Expected behavior:**
1. Skill generates and writes QA plan
2. No director agents are spawned
3. No gate IDs appear in output

**Assertions:**
- [ ] No director gate is invoked
- [ ] No gate skip messages appear
- [ ] Skill reaches COMPLETE without any gate check

---

## Protocol Compliance

- [ ] Reads coding-standards.md test evidence table before assigning test types
- [ ] Assigns BLOCKING or ADVISORY gate level per story type
- [ ] Flags stories with no AC as UNTESTABLE (does not silently skip them)
- [ ] Detects existing plan and offers update path
- [ ] Asks "May I write" before creating or updating the plan file
- [ ] Verdict is COMPLETE when plan is written

---

## Coverage Notes

- The case where `coding-standards.md` is missing (skill cannot assign test types)
  is not fixture-tested; behavior would follow the BLOCKED pattern with a note
  to restore the standards file.
- Multi-sprint planning (spanning 2 sprints) is not tested; the skill is designed
  for one sprint at a time.
- Config/data story type (balance tuning → smoke check) follows the same
  assignment pattern as other types in Case 1 and is not separately tested.

## Phase 1 Backport Regression Cases

These assertions require workflow evaluation; adding them is not a passing test run.

- [ ] Godot, Unity, and Unreal plans use actual engine-native test paths; Unity
  and Unreal do not require a top-level `tests/` folder.
- [ ] Playtest documents use `production/qa/playtests/`, not session logs.
- [ ] Plan authoring may finish with smoke execution missing, but entry criteria
  explicitly block QA execution/sign-off for FAIL or NOT ASSESSED.
- [ ] Required visual/manual checks retain explicit outcomes and evidence sources;
  advisory sign-off policy cannot make missing criterion verification pass.

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
