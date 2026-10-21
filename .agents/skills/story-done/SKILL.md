---
name: story-done
description: "End-of-story completion review. Reads the story file, verifies each acceptance criterion against the implementation, checks for GDD/ADR deviations, prompts code review, updates story status to Complete, and surfaces the next ready story from the sprint for Codex Game Studios."
---

## Artifact observations

Before summarizing selected artifacts, apply
`.codex/docs/artifact-inspection.md`. Run `python3 .codex/lib/artifact_facts.py stories`,
`python3 .codex/lib/artifact_facts.py adrs`
with the exact files selected by this workflow, from the bound root. Keep
errors, ambiguous/missing fields and source lines visible. Counts and graph order do not establish readiness,
quality, closure or evidence; apply the policies and source review below.

## Source scope

Before source/content inspection or source writes, apply **Source scope** in
`.codex/docs/technical-config.md` and run `project_config.py code-root`. Use its
listed paths, resolving verified custom paths with `--path`. Unresolved/invalid
scope leaves dependent checks NOT ASSESSED; continue independent work. A
resolved path is not an executed scan. Do not substitute or create `src/`.

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

Read the numbered brief requirement for minimal stories; use exact GDD sections
at standard when the optional registry is absent. Only read optional architecture
inputs that exist or are explicitly referenced. Missing referenced inputs and
stale declared versions remain findings. Keep every acceptance/evidence check
and completion gate below unchanged. Without a sprint, select the next ready
story by brief build order and dependencies; completed work stays completed.


# Story Done

This skill closes the loop between design and implementation. Run it at the end
of implementing any story. It ensures every acceptance criterion is verified
before the story is marked done, GDD and ADR deviations are explicitly
documented rather than silently introduced, code review is prompted rather than
forgotten, and the story file reflects actual completion status.

**Output:** Updated story file (Status: Complete) + surfaced next story.

---

## Phase 1: Find the Story

Resolve the review mode (once, store for all gate spawns this run):
Read and apply the shared `review-mode` contract in
`.codex/docs/director-gates.md` for this run. Pass any `--review` flag unchanged.
Stop review routing on INVALID/NOT ASSESSED; retain its value and source for all gate checks.

**If a file path is provided** (e.g., `$story-done production/epics/core/story-damage-calculator.md`):
read that file directly.

**If no argument is provided:**

1. Check `production/session-state/active.md` for the currently active story.
2. If not found there, read the most recent file in `production/sprints/` and
   look for stories marked IN PROGRESS.
3. If multiple in-progress stories are found, use `numbered choice prompt`:
   - "Which story are we completing?"
   - Options: list the in-progress story file names.
4. If no story can be found, ask the user to provide the path.

---

## Phase 2: Read the Story

Read the full story file. Extract and hold in context:

- **Story name and ID**
- **GDD Requirement TR-ID(s)** referenced (e.g., `TR-combat-001`)
- **Manifest Version** embedded in the story header (e.g., `2026-03-10`)
- **ADR reference(s)** referenced
- **Acceptance Criteria** — the complete list (every checkbox item)
- **Implementation files** — files listed under `## Files` (legacy "files to create/modify" is accepted)
- **Story Type** — the `Type:` field from the story header (Logic / Integration / Visual/Feel / UI / Config/Data)
- **Engine notes** — any engine-specific constraints noted
- **Definition of Done** — if present, the story-level DoD
- **Estimated vs actual scope** — if an estimate was noted

Read required/present or explicitly referenced inputs; at project minimal use the
numbered brief feature instead of an absent registry:
- `docs/architecture/tr-registry.yaml` — look up each TR-ID in the story.
  Read the *current* `requirement` text from the registry entry. This is the
  source of truth for what the GDD required — do not use any requirement text
  that may be quoted inline in the story (it may be stale).
- The referenced GDD section — just the acceptance criteria and key rules, not
  the full document. Use this to cross-check the registry text is still accurate.
- The referenced ADR(s) — just the Decision and Consequences sections
- `docs/architecture/control-manifest.md` header — extract the current
  `Manifest Version:` date (used in Phase 4 staleness check)

---

## Phase 3: Verify Acceptance Criteria

For each acceptance criterion in the story, attempt verification using one of
three methods:

### Automatic verification (run without asking)

- **File existence check**: `Glob` for files the story said would be created.
- **Test pass check**: if a test file path is mentioned, run it via `Bash`.
- **No hardcoded values check**: `Grep` for numeric literals in gameplay code
  paths that should be in config files.
- **No hardcoded strings check**: `Grep` for player-facing strings in the resolved source/content scope
  that should be in localization files.
- **Dependency check**: if a criterion says "depends on X", check that X exists.

### Manual verification with confirmation (use `numbered choice prompt`)

- Criteria about subjective qualities ("feels responsive", "animations play correctly")
- Criteria about gameplay behaviour ("player takes damage when...", "enemy responds to...")
- Performance criteria ("completes within Xms") — require measured results; never accept as assumed

Batch up to 4 manual verification questions into a single `numbered choice prompt` call:

```
question: "Does [criterion]?"
options: "Yes — passes", "No — fails", "Not tested yet"
```

### Unassessed criteria

- Unrun end-to-end/gameplay checks: `DEFERRED — requires playtest session`.
- "Not tested yet", an empty response, missing required evidence, unreadable
  captures or unavailable tooling: NOT ASSESSED.
- No such criterion counts as passed. Any required unassessed criterion prevents
  COMPLETE and COMPLETE WITH NOTES until applicable evidence is supplied.
- Test file existence is not execution. Follow the engine execution contract in
  `.codex/docs/coding-standards.md`; zero tests or an old output file is not a pass.

### Test-Criterion Traceability

After completing the pass/fail/deferred check above, map each acceptance
criterion to the test that covers it:

For each acceptance criterion in the story:

1. Ask: is there a test — unit, integration, or confirmed manual playtest — that
   directly verifies this criterion?
   - **Unit test**: check `tests/unit/` for a test file or function name that
     matches the criterion's subject (use `Glob` and `Grep`)
   - **Integration test**: check `tests/integration/` similarly
   - **Manual confirmation**: if the criterion was verified via `numbered choice prompt`
     above with a "Yes — passes" answer, count that as a manual test

2. Produce a traceability table:

```
| Criterion | Test | Status |
|-----------|------|--------|
| AC-1: [criterion text] | tests/unit/test_foo.gd::test_bar | COVERED |
| AC-2: [criterion text] | Manual playtest confirmation | COVERED |
| AC-3: [criterion text] | — | UNTESTED |
```

3. Distinguish test presence from observed execution. A criterion with a test
   file but no applicable passing run is UNTESTED, not COVERED. Resolve test roots
   per engine and record the exact run/report or explicit manual observation.
4. Any required UNTESTED criterion keeps the verdict NOT ASSESSED. An observed
   failure is BLOCKED. List advisory recommendations separately; percentages
   cannot waive a required acceptance criterion.

### Test Evidence Requirement

Resolve engine test roots using `.codex/docs/coding-standards.md`. The `tests/`
examples below apply to Godot; Unity uses `Assets/Tests/` assemblies and Unreal
uses tests in a compiled module. Search the story's exact paths first.
For visible criteria, the observed-run and opened-capture requirements in
`.codex/docs/verification-integrity.md` apply even if the table's role sign-off
policy is advisory. Missing required visual evidence is NOT ASSESSED.

Based on the Story Type extracted in Phase 2, check for required evidence:

| Story Type | Required Evidence | Gate Level |
|---|---|---|
| **Logic** | Automated unit test in `tests/unit/[system]/` — must exist and pass | BLOCKING |
| **Integration** | Integration test in `tests/integration/[system]/` OR playtest doc | BLOCKING |
| **Visual/Feel** | Screenshot + sign-off in `production/qa/evidence/` | ADVISORY |
| **UI** | Manual walkthrough doc OR interaction test in `production/qa/evidence/` | ADVISORY |
| **Config/Data** | Smoke check pass report in `production/qa/smoke-*.md` | ADVISORY |

**For Logic stories**: first read the story's **Test Evidence** section to extract the
exact required file path. Use `Glob` to check that exact path. If the exact path is not
found, also search `tests/unit/[system]/` broadly (the file may have been placed at a
slightly different location). If no test file is found at either location:
- Flag as **BLOCKING**: "Logic story has no unit test file. Story requires it at
  `[exact-path-from-Test-Evidence-section]`. Create and run the test before marking
  this story Complete."

**For Integration stories**: read the story's **Test Evidence** section for the exact
required path. Use `Glob` to check that exact path first, then search
`tests/integration/[system]/` broadly, then check `production/qa/playtests/` for a
playtest record referencing this story.
If none found: flag as **BLOCKING** (same rule as Logic).

**For Visual/Feel and UI stories**: open the referenced images and inspect criterion coverage;
file existence or a sign-off checkbox alone is not visual proof. Then glob `production/qa/evidence/` for a file
referencing this story.
- If none: flag as **ADVISORY** — "No manual test evidence found. Create `production/qa/evidence/[story-slug]-evidence.md` using the test-evidence template and obtain sign-off before final closure."
- If found: read the file and check the sign-off table for unchecked boxes. Grep for lines matching `| .* | .* | .* | \[ \] Approved` (a sign-off row with an unchecked checkbox). If any unchecked sign-off rows are found: flag as **ADVISORY** — "Evidence file found at `[path]` but [N] sign-off(s) are still pending (shown as `[ ] Approved` in the sign-off table). Obtain required sign-offs before final closure. Note: for solo developers, all roles may be signed off by the same person."
- If all sign-off rows show `[x] Approved` or equivalent: note "Evidence file found and all sign-offs complete — ADVISORY passed."

**Freshness:** run `bash .codex/lib/review-receipts.sh check
production/qa/evidence/<story-slug>/stamp.json`. Report CHANGED/GONE inputs and
request recapture; absent or invalid receipts mean freshness unknown. This is a
warning about applicability, not a new automatic test failure. Do not create a
stamp here for old evidence or turn matching hashes into a verification claim.

**For Config/Data stories**: read the smoke report for this build, scope and
platform. An unrelated, quick-only or stale report cannot verify the required
data check. Missing applicable evidence is NOT ASSESSED; an observed failure
is BLOCKED. Name the exact `$smoke-check` coverage still owed.

**If no Story Type is set**: flag as **ADVISORY** —
"Story Type not declared. Add `Type: [Logic|Integration|Visual/Feel|UI|Config/Data]`
to the story header to enable test evidence gate enforcement in future stories."

Any BLOCKING test evidence gap prevents the COMPLETE verdict in Phase 6.

---

## Phase 4: Check for Deviations

Compare the implementation against the design documents.

Run these checks automatically:

1. **GDD rules check**: Using the current requirement text from `tr-registry.yaml`
   (looked up by the story's TR-ID), check that the implementation reflects what
   the GDD actually requires now — not what it required when the story was written.
   `Grep` the implemented files for key function names, data structures, or class
   names mentioned in the current GDD section.

2. **Manifest version staleness check**: Compare the `Manifest Version:` date
   embedded in the story header against the `Manifest Version:` date in the
   current `docs/architecture/control-manifest.md` header.
   - If they match → pass silently.
   - If the story's version is older → flag as ADVISORY:
     `ADVISORY: Story was written against manifest v[story-date]; current manifest
     is v[current-date]. New rules may apply. Run $story-readiness to check.`
   - If control-manifest.md does not exist → skip this check.

3. **ADR constraints check**: Read the referenced ADR's Decision section. Check
   for forbidden patterns from `docs/architecture/control-manifest.md` (if it
   exists). `Grep` for patterns explicitly forbidden in the ADR.

4. **Hardcoded values check**: `Grep` the implemented files for numeric literals
   in gameplay logic that should be in data files.

5. **Scope check**: compare `## Files` with the verified story diff and the
   pre-implementation scope/baseline recorded by `$dev-story`. Retain any
   planned-versus-actual deviations. A legacy file list is accepted. If neither
   a story list nor a story-specific checkpoint supplies the scope, report
   `Scope: NOT ASSESSED — no file list`. A clean working tree does not prove
   scope: inspect the recorded commit range if available; otherwise report the
   comparison unassessed. Never label unrelated pre-existing edits out of scope
   for this story, and never infer that a worker's file list proves the diff.

For each deviation found, categorize:

- **BLOCKING** — implementation contradicts the GDD or ADR (must fix before
  marking complete)
- **ADVISORY** — implementation drifts slightly from spec but is functionally
  equivalent (document, user decides)
- **OUT OF SCOPE** — additional files were touched beyond the story's stated
  boundary (flag for awareness — may be valid or scope creep)

---

## Phase 4b: QA Coverage Gate

**Review mode check** — apply before spawning QL-TEST-COVERAGE:
- `solo` → skip. Note: "QL-TEST-COVERAGE skipped — Solo mode." Proceed to Phase 5.
- `lean` → skip (not a PHASE-GATE). Note: "QL-TEST-COVERAGE skipped — Lean mode." Proceed to Phase 5.
- `full` → spawn as normal.

After completing the deviation checks in Phase 4, spawn `qa-lead` via Codex subagent delegation using gate **QL-TEST-COVERAGE** (`.codex/docs/director-gates.md`).

Pass:
- The story file path and story type
- Test file paths found during Phase 3 (exact paths, or "none found")
- The story's `## QA Test Cases` section (the pre-written test specs from story creation)
- The story's `## Acceptance Criteria` list

The qa-lead reviews whether the tests actually cover what was specified — not just whether files exist.

Apply the verdict:
- **ADEQUATE** → proceed to Phase 5
- **GAPS** → flag as **ADVISORY**: "QA lead identified coverage gaps: [list]. Story can complete but gaps should be addressed in a follow-up story."
- **INADEQUATE** → flag as **BLOCKING**: "QA lead: critical logic is untested. Verdict cannot be COMPLETE until coverage improves. Specific gaps: [list]."

Skip this phase for Config/Data stories (no code tests required).

---

## Phase 5: Lead Programmer Code Review Gate

**Review mode check** — apply before spawning LP-CODE-REVIEW:
- `solo` → skip. Note: "LP-CODE-REVIEW skipped — Solo mode." Proceed to Phase 6 (completion report).
- `lean` → use `numbered choice prompt` before proceeding:
  - Prompt: "Code review is skipped in lean mode. Did you run `$code-review` on the implemented files?"
  - Options:
    - `Yes — $code-review passed or was approved with suggestions`
    - `No — skipping code review for this story`
    - `No — I'll run $code-review before the sprint close-out`
  - Record the answer in the completion notes (Phase 7). All three options proceed to Phase 6.
- `full` → spawn as normal.

Spawn `lead-programmer` via Codex subagent delegation using gate **LP-CODE-REVIEW** (`.codex/docs/director-gates.md`).

Pass: implementation file paths, story file path, relevant GDD section, governing ADR.

Present the verdict to the user. If CONCERNS, surface them via `numbered choice prompt`:
- Options: `Revise flagged issues` / `Accept and proceed` / `Discuss further`
If REJECT, do not proceed to Phase 6 verdict until the issues are resolved.

If the story has no implementation files yet (verdict is being run before coding is done), skip this phase and note: "LP-CODE-REVIEW skipped — no implementation files found. Run after implementation is complete."

---

## Phase 6: Present the Completion Report

Before updating any files, present the full report. Always include **Reviewed by**:
- the actual independently loaded reviewer when its gate ran;
- `user-reported review — not verified here` when the user reports one;
- `self — no independent review` when no independent reviewer ran.
Report unavailable/failed role activation as blocked, never as an independent pass.

```markdown
## Story Done: [Story Name]
**Story**: [file path]
**Date**: [today]

### Acceptance Criteria: [X/Y passing]
- [x] [Criterion 1] — auto-verified (test passes)
- [x] [Criterion 2] — confirmed
- [ ] [Criterion 3] — FAILS: [reason]
- [?] [Criterion 4] — DEFERRED: requires playtest

### Test-Criterion Traceability
| Criterion | Test | Status |
|-----------|------|--------|
| AC-1: [text] | [test file::test name] | COVERED |
| AC-2: [text] | Manual confirmation | COVERED |
| AC-3: [text] | — | UNTESTED |

### Test Evidence
**Story Type**: [Logic | Integration | Visual/Feel | UI | Config/Data | Not declared]
**Required evidence**: [unit test file | integration test or playtest | screenshot + sign-off | walkthrough doc | smoke check pass]
**Evidence found**: [YES — `[path]` | NO — BLOCKING | NO — ADVISORY]

### Deviations
[NONE] OR:
- BLOCKING: [description] — [GDD/ADR reference]
- ADVISORY: [description] — user accepted / flagged for tech debt

### Review
**Reviewed by**: [actual reviewer | user-reported review — not verified here | self — no independent review]

### Scope
[All changes within stated scope] OR:
- Extra files touched: [list] — [note whether valid or scope creep]

### Verdict: COMPLETE / COMPLETE WITH NOTES / NOT ASSESSED / BLOCKED
```

**Verdict definitions (first matching rule wins):**
- **BLOCKED**: a failing criterion or blocking deviation was observed.
- **NOT ASSESSED**: any required criterion/check lacks applicable evidence,
  including deferred playtests or failed/unavailable required review gates.
- **COMPLETE WITH NOTES**: all required criteria pass; advisory findings remain.
- **COMPLETE**: all required criteria pass; no advisory findings remain.

For BLOCKED or NOT ASSESSED, recommend leaving the story open and name what
would settle each gap. An explicit user choice to accept deviations may change
administrative status, but must retain the original verification verdict and
unverified criteria in Completion Notes. It never establishes acceptance or
satisfies a required QA/stage gate.

---

## Phase 7: Update Story Status

Use `numbered choice prompt` before writing anything:
For BLOCKED or NOT ASSESSED, recommend fixing/verifying first. Do not call the
verification complete or recommend closure. Offer administrative closure only
as an explicit override retaining the original verdict and every unresolved
criterion; ask before writing the named story/status files.

For COMPLETE or COMPLETE WITH NOTES, use:
- Prompt: "Verification complete. How do you want to proceed?"
- Options:
  - `Close the story — update file, mark Complete, log notes (Recommended)`
  - `Close and log advisory deviations as tech debt in docs/tech-debt-register.md`
  - `There are issues I want to fix first — don't close yet`
  - `Accept deviations as-is and close anyway`

If "Close", "Close and log tech debt", or "Accept deviations": edit the story file.
If "Close and log tech debt": after updating the story file, also append the advisory deviations to `docs/tech-debt-register.md` (create the file if it does not exist).
If "Fix first": stop here and list what the user flagged. Do not write any files.

1. Update the status field: `Status: Complete`
2. Update the `Last Updated:` field in the story header to today's date (format: `YYYY-MM-DD`). If the field does not exist, add it after the `Status:` line.
3. Add a `## Completion Notes` section at the bottom:

```markdown
## Completion Notes
**Verification verdict**: [original verdict, including any unverified criteria]
**Reviewed by**: [actual reviewer or explicit provenance]
**Completed**: [date]
**Criteria**: [X/Y passing] ([any deferred items listed])
**Deviations**: [None] or [list of advisory deviations]
**Test Evidence**: [Logic: test file at path | Visual/Feel: evidence doc at path | None required (Config/Data)]
**Code Review**: [Pending / Complete / Skipped]
```

4. If the user chose "Close and log tech debt": append each advisory deviation to `docs/tech-debt-register.md` in this format:
   ```
   - **[date]** ([story title]): [deviation description] — tracked from [story file path]
   ```
   Create the file with a `# Tech Debt Register` heading if it does not exist.

5. **Update `production/sprint-status.yaml`** (if it exists):
   - Find the entry matching this story's file path or ID
   - Set `status: done` and `completed: [today's date]`
   - Update the top-level `updated` field
   - This is a silent update — no extra approval needed (already approved in step above)

6. **Suggest a git commit**: Output a ready-to-use commit command covering the implementation files from the dev-story summary and the updated story file:

```
Suggested commit:
git add [actual source and native test files changed during implementation] [story-file-path]
git commit -m "feat: [story title] ([TR-ID])"
```

The `validate-commit.sh` hook will verify design doc references and check for hardcoded values automatically.

### Session State Update

After updating the story file, silently append to
`production/session-state/active.md` as a derived checkpoint. Do not ask a
separate "May I write?" for this file:

    ## Session Extract — $story-done [date]
    - Verdict: [COMPLETE / COMPLETE WITH NOTES / NOT ASSESSED / BLOCKED]
    - Story: [story file path] — [story title]
    - Tech debt logged: [N items, or "None"]
    - Next recommended: [next ready story title and path, or "None identified"]

If `active.md` does not exist, create it with this block as the initial content.
Confirm in conversation: "Session state updated."

---

## Phase 8: Surface the Next Story

After completion, help the developer keep momentum:

1. Read the current sprint plan from `production/sprints/`.
2. Find stories that are:
   - Status: READY or NOT STARTED
   - Not blocked by other incomplete stories
   - In the Must Have or Should Have tier

Present:

```
### Next Up
The following stories are ready to pick up:
1. [Story name] — [1-line description] — Est: [X hrs]
2. [Story name] — [1-line description] — Est: [X hrs]

Run `$story-readiness [path]` to confirm a story is implementation-ready
before starting.
```

If all Must Have stories have passing completion evidence (none Blocked or NOT ASSESSED):

```
### Sprint Close-Out Sequence

All Must Have stories are complete. QA sign-off is required before advancing.
Run these in order:

1. `$smoke-check sprint` — verify the critical path still works end-to-end
2. `$team-qa sprint` — full QA cycle: test case execution, bug triage, sign-off report
3. `$retrospective` — capture what went well, what didn't, and action items for the next sprint
4. `$gate-check` — advance to the next phase once QA approves (only if advancing a phase)
5. `$sprint-plan new` — plan the next sprint, incorporating velocity data and retrospective action items

Do not run `$gate-check` until `$team-qa` returns APPROVED or APPROVED WITH CONDITIONS.
```

If Must Have stories remain Blocked or NOT ASSESSED, list those first and route
to their missing verification or fix; do not claim the sprint is complete.

If there are Should Have stories still unstarted, surface them alongside the close-out sequence so the user can choose: close the sprint now, or pull in more work first.

If no more stories are ready but Must Have stories are still In Progress (not Complete):
"No more stories ready to start — [N] Must Have stories still in progress. Continue implementing those before sprint close-out."

After surfacing the next-story or sprint close-out inventory, read or silently
refresh the `## Session Worklist` in `production/session-state/active.md`.
Recommend one
best next action across the ready-story, smoke-check, QA, gate, tech-debt, and
handoff lanes. Use `request_user_input` when available only if 2-3 lanes are
genuinely tied.

---

## Collaborative Protocol

- **Never mark a story complete without user approval** — Phase 7 requires an
  explicit "yes" before any file is edited.
- **Never auto-fix failing criteria** — report them and ask what to do.
- **Deviations are facts, not judgments** — present them neutrally; the user
  decides if they are acceptable.
- **Status overrides do not change evidence** — preserve BLOCKED/NOT ASSESSED and unverified criteria even if the user explicitly closes the story
  anyway; document the risk explicitly if they do.
- Use `numbered choice prompt` for the code review prompt and for batching manual
  criteria confirmations.

---

## Recommended Next Steps

- Run `$story-readiness [next-story-path]` to validate the next story before starting implementation
- If all Must Have stories are complete: run `$smoke-check sprint` → `$team-qa sprint` → `$gate-check`
- If tech debt was logged: track it via `$tech-debt` to keep the register current
- Read the `## Session Worklist` in `production/session-state/active.md` to
  choose among competing sprint, QA, gate, and handoff lanes

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

- `argument-hint: "[story-file-path] [--review full|lean|solo]"`
- `user-invocable: true`
- `allowed-tools: Read, Glob, Grep, Bash, Write, Edit, numbered choice prompt, Codex subagent delegation`

## Codex Model Guidance

Suggested model: `gpt-5.6-sol`. This is guidance only; Codex does not enforce a model from skill frontmatter.
