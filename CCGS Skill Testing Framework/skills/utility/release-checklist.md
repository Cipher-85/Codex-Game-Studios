# Skill Test Spec: $release-checklist

## Skill Summary

`$release-checklist` generates an internal release readiness checklist covering:
sprint story completion, open bug severity, QA sign-off status, build stability,
and changelog readiness. It is an internal gate — not a platform/store checklist
(that is `$launch-checklist`). When a previous release checklist exists, it shows
a delta of resolved and newly introduced issues.

The skill writes its checklist report to `production/releases/release-checklist-[date].md`
after a "May I write" ask. No director gates apply — `$gate-check` handles
formal phase gate logic. Verdicts: RELEASE READY, RELEASE BLOCKED, or CONCERNS.

---

## Static Assertions (Structural)

Verified automatically by `$skill-test static` — no fixture needed.

- [ ] Has the Codex metadata contract: `name` and `description` in frontmatter; ported fields in `## Ported metadata`, or an explicit Codex-native support classification
- [ ] Has ≥2 phase headings
- [ ] Contains verdict keywords: RELEASE READY, RELEASE BLOCKED, CONCERNS
- [ ] Contains "May I write" collaborative protocol language before writing the report
- [ ] Has a next-step handoff (e.g., `$launch-checklist` for external or `$gate-check` for phase)

---

## Director Gate Checks

None. `$release-checklist` is an internal audit utility. Formal phase advancement
is managed by `$gate-check`.

---

## Test Cases

### Case 1: Happy Path — All Sprint Stories Complete, QA Passed, RELEASE READY

**Fixture:**
- `production/sprints/sprint-008.md` — all stories are `Status: Done`
- No open bugs with severity HIGH or CRITICAL in `production/bugs/`
- `production/qa/qa-plan-sprint-008.md` has QA sign-off annotation
- Changelog entry for this version exists
- `production/stage.txt` contains `Polish`

**Input:** `$release-checklist`

**Expected behavior:**
1. Skill reads sprint-008: all stories Done
2. Skill reads bugs: no HIGH or CRITICAL open bugs
3. Skill confirms QA plan has sign-off
4. Skill confirms changelog entry exists
5. All checks pass; skill asks "May I write to
   `production/releases/release-checklist-2026-04-06.md`?"
6. Report written; verdict is RELEASE READY

**Assertions:**
- [ ] All 4 check categories are evaluated (stories, bugs, QA, changelog)
- [ ] All items appear with PASS markers
- [ ] Verdict is RELEASE READY
- [ ] "May I write" is asked before writing

---

### Case 2: Open HIGH Severity Bugs — RELEASE BLOCKED

**Fixture:**
- All sprint stories are Done
- `production/bugs/` contains 2 open bugs with severity HIGH

**Input:** `$release-checklist`

**Expected behavior:**
1. Skill reads sprint — stories complete
2. Skill reads bugs — 2 HIGH severity bugs open
3. Skill reports: "RELEASE BLOCKED — 2 open HIGH severity bugs must be resolved"
4. Both bug filenames are listed in the report
5. Verdict is RELEASE BLOCKED

**Assertions:**
- [ ] Verdict is RELEASE BLOCKED (not CONCERNS)
- [ ] Both bug filenames are listed explicitly
- [ ] Skill makes clear HIGH severity bugs are blocking (not advisory)

---

### Case 3: Changelog Not Generated — CONCERNS

**Fixture:**
- All stories Done, no HIGH/CRITICAL bugs
- No changelog entry found for the current version/sprint

**Input:** `$release-checklist`

**Expected behavior:**
1. Skill checks all items
2. Changelog check fails: no changelog entry found
3. Skill reports: "CONCERNS — Changelog not generated for this release"
4. Skill suggests running `$changelog` to generate it
5. Verdict is CONCERNS (advisory — not a hard block)

**Assertions:**
- [ ] Verdict is CONCERNS (not RELEASE BLOCKED — changelog is advisory)
- [ ] `$changelog` is suggested as the remediation
- [ ] Other passing checks are shown in the report
- [ ] Missing changelog is described as advisory, not blocking

---

### Case 4: Previous Release Checklist Exists — Delta From Last Release

**Fixture:**
- `production/releases/release-checklist-2026-03-20.md` exists
- Previous: 1 story was incomplete, 1 HIGH bug open
- Current: all stories Done, HIGH bug resolved, but now 1 MEDIUM bug appeared

**Input:** `$release-checklist`

**Expected behavior:**
1. Skill finds the previous checklist and loads it
2. New checklist is generated and compared:
   - Newly resolved: "Story [X] — was open, now Done"
   - Newly resolved: "HIGH bug [filename] — was open, now closed"
   - New item: "1 MEDIUM bug appeared (advisory)"
3. Delta section shows all changes prominently
4. Verdict is CONCERNS (MEDIUM bug is advisory, not blocking)

**Assertions:**
- [ ] Delta section appears in the report with resolved and new items
- [ ] Newly resolved items from the previous checklist are noted
- [ ] New items not present in the previous checklist are highlighted
- [ ] Verdict reflects current state (not previous state)

---

### Case 5: Director Gate Check — No gate; release-checklist is an internal audit

**Fixture:**
- Active sprint with stories and bug reports

**Input:** `$release-checklist`

**Expected behavior:**
1. Skill runs the full checklist and writes the report
2. No director agents are spawned
3. No gate IDs appear in output

**Assertions:**
- [ ] No director gate is invoked
- [ ] No gate skip messages appear
- [ ] Verdict is RELEASE READY, RELEASE BLOCKED, or CONCERNS — no gate verdict

---

## Protocol Compliance

- [ ] Checks sprint story completion status
- [ ] Checks open bug severity (CRITICAL/HIGH = BLOCKED; MEDIUM/LOW = CONCERNS)
- [ ] Checks QA plan sign-off status
- [ ] Checks changelog existence
- [ ] Compares against previous checklist when one exists
- [ ] Asks "May I write" before writing the report
- [ ] Verdict is RELEASE READY, RELEASE BLOCKED, or CONCERNS

---

## Coverage Notes

- Build stability verification (no failed CI runs) is listed as a check category
  but relies on external CI system state; the skill notes this as a MANUAL CHECK
  if CI integration is not configured.
- CRITICAL bugs always result in RELEASE BLOCKED regardless of other items;
  this is equivalent to the HIGH severity case in Case 2.
- Stories with `Status: In Review` (not Done) are treated as incomplete
  and result in RELEASE BLOCKED; this edge case follows the same pattern
  as the HIGH bug case.

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
