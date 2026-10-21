# Skill Test Spec: $smoke-check

## Skill Summary

Runs the applicable engine tests, maps evidence to sprint stories, and obtains
explicit per-check manual results before QA hand-off. A report is written to
`production/qa/smoke-[date].md` only after approval. These are behavioral test
specifications, not records that the workflows below have run.

Verdict precedence: observed required failure → FAIL; otherwise missing required
execution/evidence → NOT ASSESSED; otherwise advisory issues → PASS WITH WARNINGS;
otherwise PASS. Justified N/A is recorded with its reason and scope.

## Static Assertions (Structural)

- [ ] Has the Codex metadata contract and multiple phases.
- [ ] Contains PASS, PASS WITH WARNINGS, FAIL, and NOT ASSESSED.
- [ ] Asks "May I write" before the report and supplies a next action.
- [ ] Does not invoke director gates.

## Test Cases

### Case 1: Current complete evidence permits PASS

**Fixture:** Godot with an installed GdUnit4 CLI, 12 applicable tests, a QA plan,
all required story evidence, and explicit passing manual results for this build.
**Input:** `$smoke-check`
**Assertions:**
- [ ] Resolves the installed CLI and editor, quotes executable/project paths,
  and uses the command contract in `.codex/docs/coding-standards.md`.
- [ ] Reads fresh results: 12 executed, 12 passed, zero failed; records command,
  version, build/ref, run time, result path, and skipped count.
- [ ] Test-file presence is PRESENT, not proof that a criterion ran.
- [ ] Requests PASS / FAIL / Not tested / justified N/A for each manual check.
- [ ] All required evidence assessed and passing produces PASS.
- [ ] Writes the report only after showing it and obtaining approval.

### Case 2: Failure outranks incomplete evidence

**Fixture:** Ten tests executed, two failures, plus an unanswered manual check.
**Input:** `$smoke-check`
**Assertions:**
- [ ] Lists both failing test names and the unassessed manual check.
- [ ] Overall FAIL; does not hide failures behind NOT ASSESSED.
- [ ] Blocks QA execution/sign-off and recommends correction and rerun.

### Case 3: Zero tests, missing runner, and stale results

**Fixtures:** Independently exercise zero tests with exit 0; unavailable editor;
missing CLI; an old passing result with no current output; missing required
Logic-story test evidence despite eight other passing tests.
**Input:** `$smoke-check`
**Assertions:**
- [ ] Each variant yields NOT ASSESSED, never PASS WITH WARNINGS.
- [ ] Names the missing execution/evidence and remediation.
- [ ] A supplied prior result remains historical/user-reported until inspected
  and matched to the requested scope/build.
- [ ] Planning may continue, but missing execution cannot permit QA sign-off.

### Case 4: Engine-native roots

**Fixtures:** Unity tests under `Assets/Tests/` with test asmdefs; Unreal tests
inside a compiled project module; Godot with no installed framework.
**Input:** `$smoke-check`
**Assertions:**
- [ ] Unity/Unreal do not fail merely because top-level `tests/` is absent.
- [ ] Unity runs EditMode/PlayMode as required, omits `-quit`, reads fresh results.
- [ ] Unreal builds the editor target before tests and verifies module discovery.
- [ ] Missing Godot infrastructure is NOT ASSESSED and suggests `$test-setup`.

### Case 5: Dismissed and partial manual answers

**Fixture:** Automated checks pass; user skips, dismisses, or partially answers
core/sprint/data checks. Repeat with an explicit observed manual failure.
**Input:** `$smoke-check`
**Assertions:**
- [ ] Empty responses never mean all passed; unanswered required items are
  NOT ASSESSED and remain in the report.
- [ ] N/A requires a recorded reason; required items cannot be silently omitted.
- [ ] An observed required failure yields FAIL.
- [ ] Optional performance checks stay distinct from required core/data checks.

### Case 6: Quick and platform scope

**Fixture:** Quick run or two platforms, with only one platform actually tested.
**Input:** `$smoke-check quick` or `$smoke-check --platform pc,console`
**Assertions:**
- [ ] Quick report records omitted checks and cannot satisfy full QA entry.
- [ ] Required untested platform yields NOT ASSESSED overall unless FAIL applies.
- [ ] Report includes per-platform assessed and unassessed counts.

### Case 7: Advisory warnings only

**Fixture:** Every required check passes, and only a documented advisory gap remains.
**Input:** `$smoke-check`
**Assertions:**
- [ ] PASS WITH WARNINGS applies only to the verified build/platform/scope.
- [ ] Missing required coverage cannot be relabeled advisory to allow entry.

## Protocol Compliance

- [ ] Read and execute checks before claiming results; file existence is not execution.
- [ ] Keep user-reported, historical, and directly observed evidence distinct.
- [ ] No write without approval; no director delegation.
- [ ] Follow-up identifies failures or unassessed evidence before QA hand-off.

## Coverage Notes

These fixtures require an actual workflow evaluation with the stated engines
and manual responses. Static validators only detect selected unsafe instruction
patterns; they do not execute this specification or prove engine compatibility.

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
