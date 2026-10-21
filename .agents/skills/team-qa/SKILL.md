---
name: team-qa
description: "Orchestrate the QA team through a full testing cycle. Coordinates qa-lead (strategy + test plan) and qa-tester (test case writing + bug reporting) to produce a complete QA package for a sprint or feature. Covers: test plan generation, test case writing, smoke check gate, manual QA execution, and sign-off report for Codex Game Studios."
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

## Team participation

Before dispatch, read `.codex/docs/team-policy.md` and run
`project_config.py team-policy`. Identify required/conditional/explicitly optional
roles in this pipeline, then filter only optional participation by size. A role
whose condition holds stays required. Preserve domain ownership, review-mode
filtering and runtime role-identity checks; size authorizes no new roles or writes.
Show the resulting roster and any omitted optional advisors. Unavailable required
roles remain blocked rather than simulated by the coordinator.


## Workflow policy

Before artifact reads, apply `.codex/docs/workflow-modes.md` and run the shared
`project_config.py workflow` reader. Retain tier/source, density and granularity;
resolve an exact GDD stem per system when applicable. Use `project_tier` and
`design_source` for project inputs; `tier` selects only that system's GDD sections.
A system override does not waive project-wide architecture. INVALID/NOT ASSESSED stops
the affected workflow. The prerequisite lists below are the compatibility/full
baseline: apply the shared tier table to reads, required sections, findings and
next actions. Pass that policy and the actual requirement source to delegated
roles. Review-mode filtering and required verification remain independent.


When this skill is invoked, orchestrate the QA team through a structured testing cycle.

**Decision Points:** At each phase transition, use `numbered choice prompt` to present
the user with the subagent's proposals as selectable options. Write the agent's
full analysis in conversation, then capture the decision with concise labels.
The user must approve before moving to the next phase.

## Phase 0: Resolve Review Mode
Read and apply the shared `review-mode` contract in
`.codex/docs/director-gates.md` for this run. Pass any `--review` flag unchanged.
Stop review routing on INVALID/NOT ASSESSED; retain its value and source for all gate checks.

Modes:
- `full` — spawn all director and lead gates as described
- `lean` — skip director gates unless they are PHASE-GATE type (CD-PHASE-GATE, TD-PHASE-GATE, PR-PHASE-GATE, AD-PHASE-GATE)
- `solo` — skip all director gate spawning entirely; run the skill without any agent gates

Store the resolved mode for use in all subsequent phases.

## Team Composition

- **qa-lead** — QA strategy, test plan generation, story classification, sign-off report
- **qa-tester** — Test case writing, bug report writing, manual QA documentation

## How to Delegate

Use the Codex subagent delegation to spawn each team member as a subagent:
- Delegate to `qa-lead` — Strategy, planning, classification, sign-off
- Delegate to `qa-tester` — Test case writing and bug report writing

Always provide full context in each agent's prompt (story file paths, QA plan path, scope constraints). Launch independent qa-tester tasks in parallel where possible (e.g., multiple stories in Phase 4 can be scaffolded simultaneously).

## Pipeline

### Phase 1: Load Context

Before doing anything else, gather the full scope:

1. Detect the current sprint or feature scope from the argument:
   - If argument is a sprint identifier (e.g., `sprint-03`): Glob `production/sprints/` for files matching `*[sprint-identifier]*.md`. Read the matched file. If multiple match, use the most recently modified.
   - If argument is `feature: [system-name]`: glob story files tagged for that system
   - If no argument: read `production/session-state/active.md` and `production/sprint-status.yaml` (if present) to infer the active sprint

2. Resolve `project_config.py stage` to confirm the current phase and source.

3. Count stories found and report to the user:
   > "QA cycle starting for [sprint/feature]. Found [N] stories. Current stage: [stage]. Ready to begin QA strategy?"

### Phase 2: QA Strategy (qa-lead)

Spawn `qa-lead` via Codex subagent delegation to review all in-scope stories and produce a QA strategy.

Prompt the qa-lead to:
- Read each story file
- Classify each story by type: **Logic** / **Integration** / **Visual/Feel** / **UI** / **Config/Data**
- Identify which stories require automated test evidence vs. manual QA
- Flag any stories with missing acceptance criteria or missing test evidence that would block QA
- Estimate manual QA effort (number of test sessions needed)
- **Before assessing smoke status**, inspect `production/qa/smoke-*.md` for a
  report matching this build/ref, scope and target platforms. Read findings and
  skipped checks, not just its verdict or modification time. Keep prior results
  labeled historical. Missing/unreadable evidence, unresolved build identity,
  unrun required checks, or `quick` scope when full coverage is required means
  NOT ASSESSED. Never promote UNKNOWN to PASS WITH WARNINGS. An observed failure
  remains FAIL. Reuse applicable evidence without re-interviewing the user, but
  do not claim it ran in this turn.

- Produce a strategy summary table and smoke check result:

  | Story | Type | Automated Required | Manual Required | Blocker? |
  |-------|------|--------------------|-----------------|----------|

  **Smoke Check**: [PASS / PASS WITH WARNINGS / FAIL / NOT ASSESSED] — [source: `production/qa/smoke-[date].md` or "no report found"] — [details if not PASS]

List FAIL/NOT ASSESSED findings prominently. QA strategy and plan authoring may
continue, but QA execution/sign-off requires applicable passing smoke evidence.

Present the qa-lead's full strategy to the user, then use `numbered choice prompt`:

```
question: "QA Strategy Review"
options:
  - "Looks good — proceed to test plan"
  - "Adjust story types before proceeding"
  - "Skip blocked stories and proceed with the rest"
  - "Smoke check failed — fix issues and re-run $team-qa"
  - "Cancel — resolve blockers first"
```

For **FAIL** or **NOT ASSESSED**, offer to prepare the QA plan, resolve the
smoke blocker, or stop. Preparing a plan does not admit the build to QA. For
**PASS WITH WARNINGS**, confirm all required checks passed and the warnings are
advisory; list them for the eventual sign-off report.

### Phase 3: Test Plan Generation

Using the strategy from Phase 2, produce a structured test plan document.

The test plan should cover:
- **Scope**: sprint/feature name, story count, dates
- **Story Classification Table**: from Phase 2 strategy
- **Automated Test Requirements**: which stories need test files, expected paths in `tests/`
- **Manual QA Scope**: which stories need manual walkthrough and what to validate
- **Out of Scope**: what is explicitly not being tested this cycle and why
- **Entry Criteria**: what must be true before QA can begin. Always include: (1) Smoke check PASS or PASS WITH WARNINGS report exists at `production/qa/smoke-*.md`, (2) build is stable (no crashes on launch), (3) all Must Have stories have Status: in-progress or done in `production/sprint-status.yaml`. Add any sprint-specific criteria beyond these.
- **Exit Criteria**: what constitutes a completed QA cycle (all stories PASS or FAIL with bugs filed)

Ask: "May I write the QA plan to `production/qa/qa-plan-[sprint]-[date].md`?"

Write only after receiving approval.

### Phase 4: Test Case Writing (qa-tester)

> **Entry gate:** stop here on FAIL or NOT ASSESSED smoke evidence. Only an
> applicable PASS/PASS WITH WARNINGS report covering the required build, scope
> and platforms admits the build to QA execution and sign-off. A saved QA plan
> or a story marked Complete does not override this gate.

For each story requiring manual QA (Visual/Feel, UI, Integration without automated tests):

Spawn `qa-tester` via Codex subagent delegation for each story (run in parallel where possible), providing:
- The story file path
- The relevant section of the QA plan for that story
- The GDD acceptance criteria for the system being tested (if available)
- Instructions to write detailed test cases covering all acceptance criteria

Each test case set should include:
- **Preconditions**: game state required before testing begins
- **Steps**: numbered, unambiguous actions
- **Expected Result**: what should happen
- **Actual Result**: field left blank for the tester to fill in
- **Pass/Fail**: field left blank

Present the test cases to the user for review before execution. Group by story.

Use `numbered choice prompt` per story group (batched 3-4 at a time):

```
question: "Test cases ready for [Story Group]. Review before manual QA begins?"
options:
  - "Approved — begin manual QA for these stories"
  - "Revise test cases for [story name]"
  - "Skip manual QA for [story name] — not ready"
```

Retain skipped stories as BLOCKED/NOT ASSESSED in the requested scope and final
report. Do not silently drop them to obtain approval for the whole sprint.

### Phase 5: Manual QA Execution

Walk through each story in the approved manual QA list.

Batch stories into groups of 3-4 and use `numbered choice prompt` for each:

```
question: "Manual QA — [Story Title]\n[brief description of what to test]"
options:
  - "PASS — all acceptance criteria verified"
  - "PASS WITH NOTES — minor issues found (describe after)"
  - "FAIL — criteria not met (describe after)"
  - "BLOCKED — cannot test yet (reason)"
```

An empty/dismissed answer or a required criterion not tested is NOT ASSESSED,
recorded with the blocked stories and its owed action. A passing status requires
explicit results for all required criteria and applicable evidence provenance.

After each FAIL result: use `numbered choice prompt` to collect the failure description, then spawn `qa-tester` via Codex subagent delegation to write a formal bug report in `production/qa/bugs/`.

Bug report naming: `BUG-[NNN]-[short-slug].md` (increment NNN from existing bugs in the directory).

After collecting all results, summarize:
- Stories PASS: [count]
- Stories PASS WITH NOTES: [count]
- Stories FAIL: [count] — bugs filed: [IDs]
- Stories BLOCKED: [count]

### Phase 6: QA Sign-Off Report

Spawn `qa-lead` via Codex subagent delegation to produce the sign-off report using all results from Phases 2–5.

The sign-off report format:

```markdown
## QA Sign-Off Report: [Sprint/Feature]
**Date**: [date]
**Scope/build/platforms**: [what was assessed; omissions]
**Smoke evidence**: [applicable report and run provenance]
**Reviewed by**: [actual reviewer | user-reported review | self — no independent review]

### Test Coverage Summary
| Story | Type | Auto Test | Manual QA | Result |
|-------|------|-----------|-----------|--------|
| [title] | Logic | PASS | — | PASS |
| [title] | Visual | — | PASS | PASS |

### Bugs Found
| ID | Story | Severity | Status |
|----|-------|----------|--------|
| BUG-001 | [story] | S2 | Open |

### Verdict: APPROVED / APPROVED WITH CONDITIONS / NOT APPROVED

**Conditions** (if any): [list what must be fixed before the build advances]

### Next Step
[guidance based on verdict]
```

Verdict rules:
- **APPROVED**: applicable smoke evidence passes, all required story checks PASS
  or PASS WITH NOTES, no unassessed required checks, and no S1/S2 bugs open
- **APPROVED WITH CONDITIONS**: the same required evidence is complete, with
  only documented advisory findings/S3/S4 bugs; no S1/S2 bugs
- **NOT APPROVED**: Any required story check remains unassessed/blocked; any
  S1/S2 bugs open; or stories FAIL without a documented, verified workaround

Next step guidance by verdict:
- APPROVED: "Build is ready for the next phase. Run `$gate-check` to validate advancement."
- APPROVED WITH CONDITIONS: "Resolve conditions before advancing. S3/S4 bugs may be deferred to polish."
- NOT APPROVED: "Resolve S1/S2 bugs and re-run `$team-qa` or targeted manual QA before advancing."

Ask: "May I write this QA sign-off report to `production/qa/qa-signoff-[sprint]-[date].md`?"

Write only after receiving approval.

## Error Recovery Protocol

If any spawned agent (via Codex subagent delegation) returns BLOCKED, errors, or cannot complete:

1. **Surface immediately**: Report "[AgentName]: BLOCKED — [reason]" to the user before continuing to dependent phases
2. **Assess dependencies**: Check whether the blocked agent's output is required by subsequent phases. If yes, do not proceed past that dependency point without user input.
3. **Offer options** via numbered choice prompt with choices:
   - Skip this agent and note the gap in the final report
   - Retry with narrower scope
   - Stop here and resolve the blocker first
4. **Always produce a partial report** — output whatever was completed. Never discard work because one agent blocked.

Common blockers:
- Input file missing (story not found, GDD absent) → redirect to the skill that creates it
- ADR status is Proposed → do not implement; run `$architecture-decision` first
- Scope too large → split into two stories via `$create-stories`
- Conflicting instructions between ADR and story → surface the conflict, do not guess

## Output

A summary covering: stories in scope, smoke check result, manual QA results, bugs filed (with IDs and severities), and the final APPROVED / APPROVED WITH CONDITIONS / NOT APPROVED verdict.

Verdict: **COMPLETE** — QA cycle finished.
Verdict: **BLOCKED** — smoke check failed or critical blocker prevented cycle completion; partial report produced.

After the final verdict or BLOCKED partial report, read or silently refresh the
`## Session Worklist` in `production/session-state/active.md`. The default best
next action is usually `$gate-check` after APPROVED, resolving listed conditions
after APPROVED WITH CONDITIONS, or fixing blocking QA failures before re-running
`$team-qa`.

## Session State Update

After the final phase completes (sign-off report written or BLOCKED verdict
reached), silently append to `production/session-state/active.md` as a derived
checkpoint. Do not ask a separate "May I write?" for this file:

```
<!-- QA RUN: [date] | Sprint: [sprint identifier or "ad-hoc"] | Verdict: [PASS/FAIL/CONCERNS] | Report: production/qa/qa-[date].md -->
```

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

- `argument-hint: "[sprint | feature: system-name] [--review full|lean|solo]"`
- `user-invocable: true`
- `allowed-tools: Read, Glob, Grep, Write, Codex subagent delegation, numbered choice prompt`

## Codex Model Guidance

Suggested model: `gpt-5.6-sol`. This is guidance only; Codex does not enforce a model from skill frontmatter.
- `agent: qa-lead`
