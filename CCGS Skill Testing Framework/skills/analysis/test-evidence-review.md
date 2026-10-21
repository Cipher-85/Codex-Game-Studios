# Skill Test Spec: $test-evidence-review

## Skill Summary

Reviews the quality and completeness of evidence for a story, sprint, or system.
Reads stories, resolves their engine-native evidence paths, and assesses test
quality, criterion linkage, sign-offs, visual artifacts, and content freshness.
Per-story verdicts are ADEQUATE / INCOMPLETE / MISSING / NOT ASSESSED. Source
quality review is separate from test execution. The optional report is written
only after approval. These cases specify behavior; they are not execution receipts.

## Static Assertions (Structural)

- [ ] Has the Codex metadata contract and multiple workflow phases.
- [ ] Contains ADEQUATE, INCOMPLETE, MISSING, and NOT ASSESSED.
- [ ] Requests approval before an optional report write.
- [ ] No director gates; quality findings may be referred to qa-lead.

## Test Cases

### Case 1: Adequate story evidence

**Fixture:** Logic story with exact Test Evidence path, tests satisfying shared
standards, complete criterion linkage, and an applicable passing execution log.
**Input:** `$test-evidence-review production/epics/combat/story-health.md`
**Assertions:**
- [ ] Loads the story, shared standards, and referenced evidence.
- [ ] Assesses quality and every required criterion, not merely file existence.
- [ ] Returns ADEQUATE for reviewed quality and separately labels the inspected
  run's build/ref, scope, results, and historical/current provenance.
- [ ] Does not claim it executed tests just because it inspected a result file.
- [ ] Does not write without approval.

### Case 2: Incomplete assertion/criterion coverage

**Fixture:** Logic story's test file exists but misses named edge cases and has
assertions with no acceptance-criterion linkage.
**Input:** `$test-evidence-review production/epics/combat/story-health.md`
**Assertions:**
- [ ] Returns INCOMPLETE with precise missing cases and criterion links.
- [ ] Separates blocking evidence gaps from advisory quality suggestions.
- [ ] Does not repair tests during review without an approved follow-up.

### Case 3: Missing required evidence

**Fixture:** Story references a required automated test or visual capture that
is absent; other stories in the same sprint have adequate evidence.
**Input:** `$test-evidence-review sprint`
**Assertions:**
- [ ] Names the absent artifact and returns MISSING for that story.
- [ ] Overall review cannot be ADEQUATE merely because other stories pass.
- [ ] Recommends creation/capture of the actual missing evidence rather than a
  blanket framework reset when infrastructure already exists.

### Case 4: Unreadable capture and changed input

**Fixture:** Visual story has a corrupt image or no image access; existing stamp
names a file changed since capture. Repeat with missing stamp and matching hashes.
**Input:** `$test-evidence-review production/epics/ui/story-hud.md`
**Assertions:**
- [ ] Attempts to open the image; unreadable evidence yields NOT ASSESSED.
- [ ] Names changed inputs and requests fresh capture without modifying the stamp.
- [ ] Missing stamp means freshness unknown, never unchanged.
- [ ] Hash matches alone never establish visual acceptance or passing execution.

### Case 5: Mixed sprint review and write boundary

**Fixture:** One ADEQUATE story, one INCOMPLETE, and one unassessed capture.
**Input:** `$test-evidence-review sprint`
**Assertions:**
- [ ] Overall quality verdict retains INCOMPLETE and lists unassessed items;
  unknown evidence cannot erase a known gap or produce ADEQUATE.
- [ ] Shows all story findings and next actions before offering report output.
- [ ] Asks "May I write" with the exact report path and writes only on approval.
- [ ] No simulated qa-lead/director verdict appears.

## Protocol Compliance

- [ ] Uses story/sprint/system scope rather than treating a test directory as a story.
- [ ] Preserves original artifacts and stamps during review.
- [ ] Separates test source quality, observed execution, and visual inspection.
- [ ] Flags missing evidence and provenance before recommending QA sign-off.

## Phase 1 Backport Regression Cases

These assertions require workflow evaluation; adding them is not a passing test run.

- [ ] Resolve test roots from the engine; test-code quality PASS is not a claim
  that the test executed or the feature passed.
- [ ] A referenced screenshot must be opened. Missing files are MISSING evidence;
  unreadable or unreviewed captures leave the visual check NOT ASSESSED.
- [ ] Read capture build/ref, command, time, covered input files, and omissions.
  Check the existing stamp without modifying it; changed/deleted inputs require
  fresh evidence. An absent stamp establishes no freshness guarantee.
- [ ] Unchanged hashes do not prove capture time, test execution, correct behavior,
  or inspection of the image; preserve those separate evidence requirements.
- [ ] Use `production/qa/playtests/` for playtests; never infer current results
  from historical notes alone.

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
