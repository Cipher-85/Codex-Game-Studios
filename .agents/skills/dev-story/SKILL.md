---
name: dev-story
description: "Read a story file and implement it. Loads the full context (story, GDD requirement, ADR guidelines, control manifest), routes to the right programmer agent for the system and engine, implements the code and test, and confirms each acceptance criterion. The core implementation skill — run after $story-readiness, before $code-review and $story-done for Codex Game Studios."
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

**Tier-specific context:** At project minimal, read the story's numbered brief feature
and player goal; absent optional registry/manifest/ADR fields with explicit N/A
reasons do not block. At standard use the cited GDD section when no registry
exists; require a governing ADR for critical Foundation decisions. At every
tier, validate any explicitly named TR/ADR/manifest, preserve existing rules and
block on missing/Proposed governing ADRs. Omit nonexistent optional inputs from
the programmer brief and name the omissions. The story, criteria, engine
verification and story-type test evidence always remain. The full-context table
and example briefing below apply only to inputs required/present at that tier.


# Dev Story

This skill bridges planning and code. It reads a story file in full, assembles
all the context a programmer needs, routes to the correct specialist agent, and
drives implementation to completion — including writing the test.

**The loop for every story:**
```
$qa-plan sprint           ← define test requirements before sprint begins
$story-readiness [path]   ← validate before starting
$dev-story [path]         ← implement it  (this skill)
$code-review [files]      ← review it
$story-done [path]        ← verify and close it
```

**After all sprint stories are done:** run `$team-qa sprint` to execute the full QA cycle and get a sign-off verdict before advancing the project stage.

**Output:** Source and test files in the resolved engine roots from
`.codex/docs/technical-config.md`, plus the approved story/evidence updates.

Before writing implementation files, read the matching path rule from
`.codex/instructions/path-rules/`: always `source-code.md` for game source, plus
`gameplay-code.md`, `engine-code.md`, `ai-code.md`, `network-code.md`, or
`ui-code.md` for the code's responsibility in the actual engine/custom path. Read `test-standards.md` before
creating or editing engine test files. Read `scene-files.md` for scenes/resources. Read `data-files.md`, `shader-code.md`, or
`tool-code.md` before a story writes `assets/data/**`, `assets/shaders/**`, or
`tools/**`.

---

## Phase 1: Find the Story

**If a path is provided**: read that file directly.

**If no argument**: check `production/session-state/active.md` for the active
story. If found, confirm: "Continuing work on [story title] — is that correct?"
If not found, ask: "Which story are we implementing?" Glob
`production/epics/**/*.md` and list stories with Status: Ready.

---

## Phase 2: Load Full Context

**Before loading any context, verify required files exist.** Extract the ADR path from the story's `ADR Governing Implementation` field, then check:

| File | Path | If missing |
|------|------|------------|
| TR registry (full/compatibility, or a named TR-ID) | `docs/architecture/tr-registry.yaml` | **STOP** — "TR registry not found at `docs/architecture/tr-registry.yaml`. Run `$architecture-review` to bootstrap the registry from your GDDs and ADRs." |
| Governing ADR (when named or critical at standard) | path from story's ADR field | **STOP** — "ADR file [path] not found. Run `$architecture-decision` to create it, or correct the filename in the story's ADR field." |
| Control manifest (optional below full) | `docs/architecture/control-manifest.md` | **WARN and continue** — "Control manifest not found — layer rules cannot be checked. Run `$create-control-manifest`." |

If a required TR registry or governing ADR is missing, set the story status to **BLOCKED** in the session state and do not spawn any programmer agent.

Read the applicable required/present inputs below simultaneously — these are independent reads. Do not start implementation until all context is loaded:

### The story file
Extract and hold:
- **Story title, ID, layer, type** (Logic / Integration / Visual/Feel / UI / Config/Data)
- **TR-ID** — the GDD requirement identifier
- **Governing ADR** reference
- **Manifest Version** embedded in story header
- **Acceptance Criteria** — every checkbox item, verbatim
- **Implementation Notes** — the ADR guidance section in the story
- **Files** — planned paths; preserve this list for comparison with actual edits
- **Out of Scope** boundaries
- **Test Evidence** — the required test file path
- **Dependencies** — what must be DONE before this story

### The TR registry (when required or explicitly referenced)
Read `docs/architecture/tr-registry.yaml`. Look up the story's TR-ID.
Read the current `requirement` text — this is the source of truth for what the
GDD requires now. Do not rely on any inline text in the story file (may be stale).

### The governing ADR (when named or required)
Read `docs/architecture/[adr-file].md`. Extract:
- The full Decision section
- The Implementation Guidelines section (this is what the programmer follows)
- The Engine Compatibility section (post-cutoff APIs, known risks)
- The ADR Dependencies section

### The control manifest (when present or explicitly referenced)
Read `docs/architecture/control-manifest.md`. Extract the rules for this story's layer:
- Required patterns
- Forbidden patterns
- Performance guardrails

Check: does the story's embedded Manifest Version match the current manifest header date?
If they differ, use `numbered choice prompt` before proceeding:
- Prompt: "Story was written against manifest v[story-date]. Current manifest is v[current-date]. New rules may apply. How do you want to proceed?"
- Options:
  - `[A] Update story manifest version and implement with current rules (Recommended)`
  - `[B] Implement with old rules — I accept the risk of non-compliance`
  - `[C] Stop here — I want to review the manifest diff first`

If [A]: edit the story file's `Manifest Version:` field to the current manifest date before spawning the programmer. Then read the manifest carefully for new rules.
If [B]: edit the story file's `Manifest Version:` field to the current manifest date AND add a `Manifest-Note: Proceeded with old manifest rules on [date] — non-compliance risk accepted.` line to the story header. Read the manifest for new rules anyway. Note the decision in the Phase 6 summary under "Deviations". `$story-done` will include the Manifest-Note in its deviations section without re-checking staleness.
If [C]: stop. Do not spawn any agent. Let the user review and re-run `$dev-story`.

### Dependency validation

After extracting the **Dependencies** list from the story file, validate each:

1. Glob `production/epics/**/*.md` to find each dependency story file.
2. Read its `Status:` field.
3. If any dependency has Status other than `Complete` or `Done`:
   - Use `numbered choice prompt`:
     - Prompt: "Story '[current story]' depends on '[dependency title]' which is currently [status], not Complete. How do you want to proceed?"
     - Options:
       - `[A] Proceed anyway — I accept the dependency risk`
       - `[B] Stop — I'll complete the dependency first`
       - `[C] The dependency is done but status wasn't updated — mark it Complete and continue`
   - If [B]: set story status to **BLOCKED** in session state and stop. Do not spawn any programmer agent.
   - If [C]: ask "May I update [dependency path] Status to Complete?" before continuing.
   - If [A]: note in Phase 6 summary under "Deviations": "Implemented with incomplete dependency: [dependency title] — [status]."

If a dependency file cannot be found: warn "Dependency story not found: [path]. Verify the path or create the story file."

---

### Engine reference
Read `.codex/docs/technical-preferences.md`:
- `Engine:` value — determines which programmer agents to use
- Naming conventions (class names, file names, signal/event names)
- Performance budgets (frame budget, memory ceiling)
- Forbidden patterns

### Mark Story In Progress

Silently update two things before spawning any agent:

1. **`production/sprint-status.yaml`** (if it exists): find the entry matching this story's file path and set `status: in_progress`. Update the top-level `updated` field to today's date. If the file does not exist, skip silently.

2. **The story file itself**: edit the `Last Updated:` field in the story header to today's date (format: `YYYY-MM-DD`). If the field does not exist in the story header, add it after the `Status:` line. This enables sprint-status staleness detection for this story.

---

## Phase 3: Route to the Right Programmer

Based on the story's **Layer**, **Type**, and **system name**, determine which
specialist to spawn via Codex subagent delegation.

**Config/Data stories — skip agent spawning entirely:**
If the story's Type is `Config/Data`, no programmer agent or engine specialist is needed. Jump directly to Phase 4 (Config/Data note). The implementation is a data file edit — no routing table evaluation, no engine specialist.

### Primary agent routing table

| Story context | Primary agent |
|---|---|
| Foundation layer — any type | `engine-programmer` |
| Any layer — Type: UI | `ui-programmer` |
| Any layer — Type: Visual/Feel | `gameplay-programmer` (implements) |
| Core or Feature — gameplay mechanics | `gameplay-programmer` |
| Core or Feature — AI behaviour, pathfinding | `ai-programmer` |
| Core or Feature — networking, replication | `network-programmer` |
| Config/Data — no code | No agent needed (see Phase 4 Config note) |

### Engine specialist — always spawn as secondary for code stories

Read the `Engine Specialists` section of `.codex/docs/technical-preferences.md`
to get the configured primary specialist. Spawn them alongside the primary agent
when the story involves engine-specific APIs, patterns, or the ADR has HIGH
engine risk.

| Engine | Specialist agents available |
|--------|----------------------------|
| Godot 4 | `godot-specialist`, `godot-gdscript-specialist`, `godot-shader-specialist` |
| Unity | `unity-specialist`, `unity-ui-specialist`, `unity-shader-specialist` |
| Unreal Engine | `unreal-specialist`, `ue-gas-specialist`, `ue-blueprint-specialist`, `ue-umg-specialist`, `ue-replication-specialist` |

**When engine risk is HIGH** (from the ADR or VERSION.md): always spawn the engine
specialist, even for non-engine-facing stories. High risk means the ADR records
assumptions about post-cutoff engine APIs that need expert verification.

---

## Phase 4: Implement

Resolve code/test roots using `.codex/docs/coding-standards.md`. Before delegating,
record the current ref and pre-existing changes in the active checkpoint, and
confirm the approved source/test paths. Include the story path if updating its
`## Files` section. Existing implementation approval carries forward only for
its named scope; ask before an unapproved story/evidence write or scope expansion.
For older stories without a Files section, propose the list before implementing.
Do not attribute unrelated working-tree changes to this story.

Spawn the chosen programmer agent(s) via Codex subagent delegation with the full context package:

Brief the agent with file paths and targeted reading instructions — do not serialize document content into the Codex subagent delegation prompt. The agent reads what it needs directly:

1. **Story file**: `[story-path]` — read in full
2. **GDD requirement**: look up TR-ID `[TR-XXX-NNN]` in `docs/architecture/tr-registry.yaml` — use the `requirement` field as source of truth
3. **ADR**: `docs/architecture/[adr-file].md` — read the **Decision** and **Implementation Guidelines** sections only
4. **Control manifest**: `docs/architecture/control-manifest.md` — read rules for the **[layer]** layer only
5. **Engine preferences**: resolved technical values and actual pin/runner evidence; read naming conventions and custom rules from `.codex/docs/technical-preferences.md`
6. **Test file path**: `[path from story's Test Evidence section]` — this file must be created as part of implementation
7. **Test requirement** (Logic and Integration stories only): The test file MUST be created at `[path from the story's Test Evidence section]`. Write the test alongside the implementation — do not defer it. The story cannot be closed via `$story-done` without this file present. Each acceptance criterion must have at least one test function covering it. Test file naming: `[system]_[feature]_test.[ext]`. Function naming: `test_[scenario]_[expected_outcome]`. No random seeds, no time-dependent assertions, no external I/O.
8. **Explicit instruction**: implement this story following the ADR guidelines, respect the manifest rules, stay within the story's Out of Scope boundaries. Write clean, doc-commented public APIs.

The agent should:
- Create or modify files only in the resolved engine code/test roots and approved paths
- Respect all Required and Forbidden patterns from the control manifest
- Stay within the story's Out of Scope boundaries (do not touch unrelated files)
- Write clean, doc-commented public APIs

### Config/Data stories (no agent needed)

For Type: Config/Data stories, no programmer agent is required. The implementation
is editing a data file. Read the story's acceptance criteria and make the specified
changes to the data file directly. Note which values were changed and what they
changed from/to.

### Visual/Feel stories

Spawn `gameplay-programmer` to implement the code/animation calls. Note that
Visual/Feel acceptance criteria cannot be auto-verified — the "does it feel right?"
check happens in `$story-done` via manual confirmation.

---

## Phase 5: Test Evidence Requirements

The test requirement was included in the Phase 4 programmer agent brief (item 7). This phase summarizes what evidence each story type requires — used when collecting the Phase 6 summary.

| Story Type | Required Evidence | Notes |
|---|---|---|
| **Logic** | Automated unit test at path from story's Test Evidence section | BLOCKING — included in Phase 4 agent brief |
| **Integration** | Integration test OR documented playtest record | BLOCKING — included in Phase 4 agent brief |
| **Visual/Feel** | Observed run, opened screenshot and sign-off in `production/qa/evidence/` | Required to claim the visual/feel criteria passed |
| **UI** | Observed walkthrough or interaction test; opened screenshot for visible criteria | Required to claim those criteria passed |
| **Config/Data** | None — smoke check serves as evidence | N/A |

For Visual/Feel and UI stories, include in the Phase 6 summary: "Manual evidence required at `production/qa/evidence/[slug]-evidence.md` before this story can be fully closed."

---

## Phase 6: Collect and Summarise

Verify each claimed artifact exists and inspect the actual diff against the
approved paths. A blocked, interrupted or incomplete agent result is INCOMPLETE,
not "Implementation Complete". Name missing outputs and owed actions.

Run the applicable approved engine/test checks using
`.codex/docs/coding-standards.md`; report their exact commands and results.
For visible criteria follow `.codex/docs/verification-integrity.md`: launch,
reach the required state, open retained screenshots, and record criterion-linked
observations. Build/import success alone is not visual proof. Missing access or
unrun criteria are NOT ASSESSED. Preserve existing checks and user-owned feel
judgments; never infer a subjective sign-off.

Include evidence doc, capture and `stamp.json` paths in the approved capture scope.
Only after a new observed capture run `bash .codex/lib/review-receipts.sh hash`
with the covered project-relative code/scene/data/asset paths and save its
successful JSON output to `production/qa/evidence/<story-slug>/stamp.json`.
Do not stamp an old capture or claim the receipt proves a test passed.

Update the story's `## Files` with verified actual paths only when that write was
approved. Preserve planned-versus-actual deviations in the summary/checkpoint;
otherwise report the proposed update without writing. Report missing scope
information explicitly rather than declaring all changes in scope.

After the programmer agent(s) complete, collect:

- Files created or modified (with paths)
- Test file created (path and number of test functions written)
- Any deviations from the story's Out of Scope boundary (flag these)
- Any questions or blockers the agent surfaced
- Any engine-specific risks the specialist flagged

Present a concise implementation summary:

```
## Implementation: [Story Title] — [COMPLETE / INCOMPLETE / BLOCKED]

**Files changed**:
- `[actual engine/custom source path]` — created / modified ([brief description])
- `tests/[path]` — test file ([N] test functions)

**Verification**: [command/tool, result, report/capture path; NOT ASSESSED where unrun]
**Run result**: [OBSERVED / NOT ASSESSED — setup and evidence]

**Acceptance criteria covered**:
- [ ] [criterion] — implemented in [file:function]; verification still owed
- [x] [criterion] — verified by [test_name], [current run/report]
- [ ] [criterion] — DEFERRED: requires playtest (Visual/Feel)

**Deviations from scope**: [None] or [list files touched outside story boundary]
**Engine risks flagged**: [None] or [specialist finding]
**Blockers**: [None] or [describe]

**Before running `$story-done`:** run your test suite locally and confirm the tests you wrote pass. `$story-done` will re-run them automatically, but a failing test discovered there means returning to implementation context.

Ready for: `$code-review [file1] [file2]` then `$story-done [story-path]`
```

---

## Phase 7: Update Session State

Silently append to `production/session-state/active.md` as a derived checkpoint.
Do not ask a separate "May I write?" for this file:

```
## Session Extract — $dev-story [date]
- Story: [story-path] — [story title]
- Files changed: [comma-separated list]
- Test written: [path, or "None — Visual/Feel/Config story"]
- Run result: [OBSERVED / NOT ASSESSED — command/tool, build, scene and evidence paths]
- Scope: [planned vs actual; pre-existing changes excluded; unknowns named]
- Blockers: [None, or description]
- Next: $code-review [files] then $story-done [story-path]
```

Create `active.md` if it does not exist. Confirm: "Session state updated."

---

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
- Manifest version mismatch → show diff to user, ask whether to proceed with old rules or update story first

## Collaborative Protocol

- **File writes are delegated** — all source code, test files, and evidence docs are written by sub-agents spawned via Codex subagent delegation. Each sub-agent enforces the "May I write to [path]?" protocol individually. This orchestrator does not write files directly.
- **Load before implementing** — do not start coding until all context is loaded
  (story, TR-ID, ADR, manifest, engine prefs). Incomplete context produces code
  that drifts from design.
- **The ADR is the law** — implementation must follow the ADR's Implementation
  Guidelines. If the guidelines conflict with what seems "better," flag it in the
  summary rather than silently deviating.
- **Stay in scope** — the Out of Scope section is a contract. If implementing
  the story requires touching an out-of-scope file, stop and surface it:
  "Implementing [criterion] requires modifying [file], which is out of scope.
  Shall I proceed or create a separate story?"
- **Test is not optional for Logic/Integration** — do not mark implementation
  complete without the test file existing
- **Visual/Feel criteria are deferred, not skipped** — mark them as DEFERRED
  in the summary; they will be manually verified in `$story-done`
- **Ask before large structural decisions** — if the story requires an
  architectural pattern not covered by the ADR, surface it before implementing:
  "The ADR doesn't specify how to handle [case]. My plan is [X]. Proceed?"

---

## Recommended Next Steps

- Run `$code-review [file1] [file2]` to review the implementation before closing the story
- Run `$story-done [story-path]` to verify acceptance criteria and mark the story complete
- After all sprint stories are done: run `$team-qa sprint` for the full QA cycle before advancing the project stage
- After the implementation summary, read or silently refresh the `## Session Worklist` in
  `production/session-state/active.md`. The default best next action is
  `$code-review`; if verification, story closure, QA, or handoff is equally
  plausible, use `request_user_input` when available.

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

- `argument-hint: "[story-path]"`
- `user-invocable: true`
- `allowed-tools: Read, Glob, Grep, Write, Bash, Codex subagent delegation, numbered choice prompt`

## Codex Model Guidance

Suggested model: `gpt-5.6-sol`. This is guidance only; Codex does not enforce a model from skill frontmatter.
