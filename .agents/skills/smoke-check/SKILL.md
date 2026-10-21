---
name: smoke-check
description: "Run the critical path smoke test gate before QA hand-off. Executes the automated test suite, verifies core functionality, and produces a PASS / PASS WITH WARNINGS / FAIL / NOT ASSESSED report. Run after a sprint's stories are implemented and before manual QA begins. A failed smoke check means the build is not ready for QA for Codex Game Studios."
---

## Technical configuration

Before using engine, framework, platform or performance fields, read
`.codex/docs/technical-config.md` and run `project_config.py technical`. Use its
resolved values/provenance for typed fields; the technical-preferences reads
below still supply custom prose, policies and routing notes. Check conflicts
and field-specific readiness before affected work. Pin agreement is not an
engine run; runner availability needs actual metadata/help verification. Keep
estimates separate from measured evidence and preserve existing pins/runners.

## QA configuration

Before evidence planning or a QA verdict, read `.codex/docs/qa-policy.md` and run
`project_config.py qa-policy`. Keep level/source, effective type gates and any
active coverage threshold. Apply it to the checks and delegated briefs below.
Required evidence, known failures and unassessed criteria retain their existing
blocking behavior at every level. Strict false cannot waive that floor. Full QA
adds affected critical-path regression evidence; optional numeric coverage uses
an applicable measured report, never test counts. Report unrun checks honestly.


# Smoke Check

This skill is the gate between "implementation done" and "ready for QA
hand-off". It runs the automated test suite, checks for test coverage gaps,
verifies critical paths with explicit developer responses, and reports scoped
results with provenance.

The rule is simple: **a build that fails smoke check does not go to QA.**
Handing a broken build to QA wastes their time and demoralises the team.

**Output:** `production/qa/smoke-[date].md`

---

## Parse Arguments

Arguments can be combined: `$smoke-check sprint --platform console`

**Base mode** (first argument, default: `sprint`):
- `sprint` — full smoke check against the current sprint's stories
- `quick` — skip coverage scan (Phase 3) and Batch 3; use for rapid re-checks

**Platform flag** (`--platform`, default: none):
- `--platform pc` — add PC-specific checks (keyboard, mouse, windowed mode)
- `--platform console` — add console-specific checks (gamepad, TV safe zones,
  platform certification requirements)
- `--platform mobile` — add mobile-specific checks (touch, portrait/landscape,
  battery/thermal behaviour)
- `--platform all` — add all platform variants; output per-platform verdict table

If `--platform` is provided, Phase 4 adds platform-specific batches and
Phase 5 outputs a per-platform verdict table in addition to the overall verdict.

---

## Phase 1: Detect Test Setup

Before running anything, understand the environment:

1. **Engine detection**: read `.codex/docs/technical-preferences.md` and the
   pinned engine reference. Resolve code/test roots and executable using
   `.codex/docs/coding-standards.md`. Do not require a top-level `tests/`
   directory for Unity or Unreal.
2. **Test framework check**: inspect the resolved roots, installed framework,
   existing test README/CI commands, and the story's exact Test Evidence paths.
   Missing/unresolved infrastructure is NOT ASSESSED; name what must be set up.
3. **CI check**: note whether a test workflow exists. Existence is not a passing run.

4. **Smoke test list**: check whether `production/qa/smoke-tests.md` or
   `tests/smoke/` exists. If a smoke test list is found, load it for use in
   Phase 4. If neither exists, smoke tests will be drawn from the current QA
   plan (Phase 4 fallback).

5. **QA plan check**: glob `production/qa/qa-plan-*.md` and take the most
   recently modified file. If found, note the path — it will be used in
   Phase 3 and Phase 4. If not found, note: "No QA plan found. Run
   `$qa-plan sprint` before smoke-checking for best results."

Report findings before proceeding: "Environment: [engine]. Test directory:
[found / not found]. CI configured: [yes / no]. QA plan: [path / not found]."

---

## Phase 2: Run Automated Tests

Use the engine commands and result interpretation in
`.codex/docs/coding-standards.md` (Engine Test Execution Contract). Resolve the
installed runner and pinned engine first. Preserve existing custom commands.
Import a fresh Godot checkout; build Unreal's Editor target; run Unity through
its full Editor executable and read this run's NUnit XML. Use a fresh approved
output directory, record the exact command, version, exit code and report paths.

Read counts and error output, not just the process exit code:
- Executed, passed, failed, skipped and unmatched test counts.
- Compile errors, crashes, interrupted execution and missing result files.
- Each skipped required test and any result outside the requested scope.

A known test/compile/runtime failure is FAIL. With no known failure, missing
executables, zero executed tests, a timeout or unreadable/missing fresh results
are NOT ASSESSED. A supplied prior result is historical or user-reported until
its build, scope and applicability are established; it is never relabeled as a
current-turn run. Do not substitute the most recently modified report.

Manual gameplay confirmation cannot stand in for a required automated suite.
Missing required execution stays NOT ASSESSED; it never becomes PASS WITH WARNINGS.

---

## Phase 3: Check Test Coverage

Draw the story list from, in priority order:
1. The QA plan found in Phase 1 (its Test Summary table lists expected test
   file paths per story)
2. The current sprint plan from `production/sprints/` (most recently modified
   file)
3. If the `quick` argument was passed, skip this phase entirely and note:
   "Coverage scan skipped — run `$smoke-check sprint` for full coverage
   analysis."

For each story in scope:

1. Extract the system slug from the story's file path
   (e.g., `production/epics/combat/story-001.md` → `combat`)
2. Search the resolved engine test roots for the story
   (Godot `tests/`, Unity `Assets/Tests/`, Unreal compiled module tests)
3. Check the story file itself for a `Test file:` header field or a
   "Test Evidence" section

Assign a coverage status to each story:

| Status | Meaning |
|--------|---------|
| **PRESENT** | A test file exists; execution and criterion coverage are separate checks |
| **MANUAL** | Story type is Visual/Feel or UI; a test evidence document was found |
| **MISSING** | Logic or Integration story with no matching test file |
| **EXPECTED** | Config/Data story — no test file required; spot-check is sufficient |
| **UNKNOWN** | Story file missing or unreadable |

A missing required test/evidence entry is NOT ASSESSED unless an observed
failure already makes the verdict FAIL. File discovery alone cannot establish
coverage or satisfy the required test run. List advisory gaps separately.

---

## Phase 4: Run Manual Smoke Checks

Draw the smoke test checklist from, in priority order:
1. The QA plan's "Smoke Test Scope" section (if QA plan was found in Phase 1)
2. `production/qa/smoke-tests.md` (if it exists)
3. `tests/smoke/` directory contents (if it exists)
4. The standard fallback list below (used only when none of the above exist)

Tailor batches 2 and 3 to the actual systems identified from the sprint or QA
plan. Replace bracketed placeholders with real mechanic names from the current
sprint's stories.

Use explicit per-check responses, in batches of up to four:

```
Check: [observable criterion, build and setup]
1. Pass — I ran this check on this build
2. Fail — [describe actual behavior]
3. Not tested
4. Not applicable — [reason]
```

A skipped/dismissed/empty response is NOT ASSESSED, never a pass. Ask again in
plain text if a choice UI returns nothing. Record each response with its
provenance; accept N/A only when the check genuinely does not apply, with a reason.
Do not infer that no reported failures means the checks ran.

Required batches:
- **Core stability:** launch, start a session, navigate the relevant UI, and
  check for crashes/hangs.
- **Sprint changes:** the primary changed mechanic, another changed mechanic
  when applicable, and regression in a previously working feature.
- **Data/performance:** save/load if implemented, visible hitches, and any
  performance requirement in scope. Skip this batch only in `quick` mode and
  state that omission. Quantitative claims need measurements.

For `--platform pc`, add keyboard/mouse, window modes and resolution. For
`console`, add controller focus/navigation, suspend/resume and applicable display
checks. For `mobile`, add touch, orientation, lifecycle and applicable device
performance checks. `all` includes each target platform; untested target checks
remain NOT ASSESSED. Resolve precise checks from the QA plan and implemented
features before asking. Record failures and the user's observations verbatim.

For visible criteria follow `.codex/docs/verification-integrity.md`: run the
build, reach the relevant state and open retained screenshots. Keep interaction,
feel and performance proof separate. No visual access means NOT ASSESSED for
those criteria, with the specific user playtest/capture still owed.

---

## Phase 5: Generate Report

Assemble the full smoke check report:

````markdown
## Smoke Check Report
**Date**: [date]
**Sprint**: [sprint name / number, or "Not identified"]
**Engine**: [engine]
**QA Plan**: [path, or "Not found — run $qa-plan first"]
**Argument**: [sprint | quick | blank]

---

### Automated Tests

**Status**: [PASS ([N] tests, [N] passing) | FAIL ([N] failures) |
NOT ASSESSED ([reason: not run / zero tests / unavailable results])]
**Provenance**: [command, engine/framework version, build/ref, run time,
fresh result path, executed/passed/failed/skipped counts]

[If FAIL, list failing tests:]
- `[test name]` — [brief failure description from runner output]

[If NOT ASSESSED:]
"Required execution is unverified. Supply the applicable run and result artifact
or run the missing check. Label supplied results as user-reported until inspected."

---

### Test Coverage

| Story | Type | Test File | Coverage Status |
|-------|------|-----------|----------------|
| [title] | Logic | `tests/unit/[system]/[slug]_test.[ext]` | PRESENT |
| [title] | Visual/Feel | `production/qa/evidence/[slug]-evidence.md` | MANUAL |
| [title] | Logic | — | MISSING ⚠ |
| [title] | Config/Data | — | EXPECTED |

**Summary**: [N] present, [N] manual, [N] missing, [N] expected.

---

### Manual Smoke Checks

- [x] Game launches without crash — PASS
- [x] New game starts — PASS
- [x] [Core mechanic] — PASS
- [ ] [Other check] — FAIL: [user's description]
- [x] Save / load — PASS
- [?] Performance — NOT ASSESSED if required and not checked this session

---

### Missing Test Evidence

Stories that must have test evidence before they can be marked COMPLETE via
`$story-done`:

- **[story title]** (`[path]`) — Logic story has no test file.
  Expected location: `tests/unit/[system]/[story-slug]_test.[ext]`

[If none:] "All required test files were found; see execution and criterion results above."

---

### Platform-Specific Results *(only if `--platform` was provided)*

| Platform | Checks Run | Passed | Failed | Unassessed | Platform Verdict |
|----------|-----------|--------|--------|------------|-----------------|
| PC | [N] | [N] | [N] | [N] | PASS / FAIL / NOT ASSESSED |
| Console | [N] | [N] | [N] | [N] | PASS / FAIL / NOT ASSESSED |
| Mobile | [N] | [N] | [N] | [N] | PASS / FAIL / NOT ASSESSED |

**Platform notes**: [any platform-specific observations not captured in pass/fail]

Any platform with one or more FAIL checks contributes to the overall FAIL verdict.
Otherwise, an unassessed required platform check keeps the overall NOT ASSESSED.

---

### Verdict: [PASS | PASS WITH WARNINGS | FAIL | NOT ASSESSED]

[Verdict rules — first matching rule wins:]

**FAIL** if any executed required check failed, including compilation,
automated tests, launch, gameplay, data integrity or a requested platform check.

**NOT ASSESSED** if a required check has no applicable evidence: zero tests,
missing/unreadable fresh output, missing tooling, unanswered/not-tested manual
checks, missing required capture, or incomplete execution. List every gap.

**PASS WITH WARNINGS** only if every required check passed (or is justified N/A)
and advisory findings remain. Missing required evidence is not advisory.

**PASS** only if every required check passed (or is justified N/A) and no advisory
finding remains. Always state `Mode: sprint | quick`, assessed scope, build/ref,
run provenance and skipped phases. A quick pass is only a pass for quick scope.

````

---

## Phase 6: Write and Gate

Present the full report in conversation, then ask:

"May I write this smoke check report to `production/qa/smoke-[date].md`?"

Write only after approval.

After writing, deliver the gate verdict:

For a `quick` run, qualify any passing verdict as **quick scope only**. Replace
the full-QA readiness messages below with the remaining sprint/coverage checks
and recommend the full `$smoke-check sprint` before a full QA hand-off.

**If verdict is NOT ASSESSED:**

Report each unrun check and its exact next action. QA planning can continue, but
QA execution/sign-off must wait for applicable passing smoke evidence.

**If verdict is FAIL:**

"The smoke check failed. Do not hand off to QA until these failures are
resolved:

[List each failing automated test or smoke check with a one-line description]

Fix the failures and run `$smoke-check` again to re-gate before QA hand-off."

**If verdict is PASS WITH WARNINGS:**

"Smoke check passed with warnings. The build is ready for manual QA.

Advisory findings (all required checks passed):
[list warnings and their evidence]

QA hand-off: share `production/qa/qa-plan-[sprint].md` with the qa-tester
agent to begin manual verification."

**If verdict is PASS:**

"Smoke check passed cleanly. The build is ready for manual QA.

QA hand-off: share `production/qa/qa-plan-[sprint].md` with the qa-tester
agent to begin manual verification."

After the gate verdict, read or silently refresh the `## Session Worklist` in
`production/session-state/active.md`. The default best next action is usually
`$team-qa sprint` for PASS or PASS WITH WARNINGS, and fixing failures then
re-running `$smoke-check` for FAIL or NOT ASSESSED. A quick report cannot
satisfy a gate requiring sprint/coverage checks. If handoff or story closure is equally
plausible, use `request_user_input` when available.

---

## Collaborative Protocol

- **Never turn NOT RUN into a pass** — missing execution is NOT ASSESSED.
  Known failures remain FAIL; manual confirmation does not replace required automated tests.
- **Never auto-fix failures** — report them and state what must be resolved.
  Do not attempt to edit source code or test files.
- **PASS WITH WARNINGS permits QA only for its verified scope** — it records advisory
  gaps for `$story-done` to follow up on.
- **`quick` argument** skips Phase 3 (coverage scan) and Phase 4 Batch 3.
  Use it for rapid re-checks after fixing a specific failure.
- Use `numbered choice prompt` for all manual smoke check verification.
- **Never write the report without asking** — Phase 6 requires explicit
  approval before any file is created.

## Closeout Contract

Every final response from this skill must include completed work, verification
run or owed verification, and next-lane routing. Read or refresh the
`## Session Worklist` in `production/session-state/active.md` when present. End
with a numbered next-action prompt using numeric format only, even when there is
only one valid lane:

```md
Next action:
1. (Recommended) [action label] - [brief reason / command]
```

If multiple lanes are viable, add more numbered options and keep exactly one
`(Recommended)` option. The user can reply with `1`. Do not end with only a
static command list.

## Ported metadata

The following upstream metadata is preserved as context only; Codex does not enforce it from skill frontmatter.

- `argument-hint: "[sprint | quick | --platform pc|console|mobile|all]"`
- `user-invocable: true`
- `allowed-tools: Read, Glob, Grep, Bash, Write, numbered choice prompt`

## Codex Model Guidance

Suggested model: `gpt-5.6-sol`. This is guidance only; Codex does not enforce a model from skill frontmatter.
