# Skill Test Spec: $dev-story

## Skill Summary

`$dev-story` reads a story file, loads all required context (referenced ADR,
TR-ID from the registry, control manifest, engine preferences), implements the
story, verifies that all acceptance criteria are met, and marks the story
Complete. The skill routes implementation to the correct specialist agent based
on the engine and file type — it does not write source code directly.

In `full` review mode, an LP-CODE-REVIEW gate runs before marking the story
Complete. In `lean` or `solo` mode, LP-CODE-REVIEW is skipped and the story is
marked Complete after the user confirms all criteria are met. The skill asks
"May I write" before updating story status and before writing code files.

---

## Static Assertions (Structural)

Verified automatically by `$skill-test static` — no fixture needed.

- [ ] Has the Codex metadata contract: `name` and `description` in frontmatter; ported fields in `## Ported metadata`, or an explicit Codex-native support classification
- [ ] Has ≥2 phase headings
- [ ] Contains verdict keywords: COMPLETE, BLOCKED, IN PROGRESS, NEEDS CHANGES
- [ ] Contains "May I write" collaborative protocol language (story status + code files)
- [ ] Has a next-step handoff at the end (`$story-done`)
- [ ] Documents LP-CODE-REVIEW gate: active in full mode, skipped in lean/solo
- [ ] Notes that implementation is delegated to specialist agents (not done directly)

---

## Director Gate Checks

In `full` mode: LP-CODE-REVIEW gate runs after implementation is complete and all
criteria are verified, before marking the story Complete.

In `lean` mode: LP-CODE-REVIEW is skipped. Output notes:
"LP-CODE-REVIEW skipped — lean mode". Story is marked Complete after user confirms.

In `solo` mode: LP-CODE-REVIEW is skipped with equivalent notes.

---

## Test Cases

### Case 1: Happy Path — Story implemented and marked Complete (full mode)

**Fixture:**
- A story file exists at `production/epics/[layer]/story-[name].md` with:
  - `Status: Ready`
  - A TR-ID referencing a registered requirement
  - At least 2 Given-When-Then acceptance criteria
  - A test evidence path
- Referenced ADR has `Status: Accepted`
- `docs/architecture/control-manifest.md` exists
- `.codex/docs/technical-preferences.md` has engine and language configured
- `production/session-state/review-mode.txt` contains `full`

**Input:** `$dev-story production/epics/[layer]/story-[name].md`

**Expected behavior:**
1. Skill reads the story file and all referenced context
2. Skill verifies the ADR is Accepted (no block)
3. Skill routes implementation to the correct specialist agent
4. All acceptance criteria are verified as met
5. LP-CODE-REVIEW gate spawns and returns APPROVED
6. Skill asks "May I update story status to Complete?"
7. Story status is updated to Complete

**Assertions:**
- [ ] Skill reads story before spawning any agent
- [ ] ADR status is checked before implementation begins
- [ ] Implementation is delegated to a specialist agent (not done inline)
- [ ] All acceptance criteria are confirmed before LP-CODE-REVIEW
- [ ] LP-CODE-REVIEW appears in output as a completed gate
- [ ] Story status is updated to Complete only after gate approval and user consent
- [ ] Test file is written as part of implementation (not deferred)

---

### Case 2: Failure Path — Referenced ADR is Proposed

**Fixture:**
- A story file exists with `Status: Ready`
- The story's TR-ID points to a requirement covered by an ADR with `Status: Proposed`

**Input:** `$dev-story production/epics/[layer]/story-[name].md`

**Expected behavior:**
1. Skill reads the story file
2. Skill resolves the TR-ID and reads the governing ADR
3. ADR status is Proposed — skill outputs a BLOCKED message
4. Skill names the specific ADR blocking the story
5. Skill recommends running `$architecture-decision` to advance the ADR
6. Implementation does NOT begin

**Assertions:**
- [ ] Skill does NOT begin implementation with a Proposed ADR
- [ ] BLOCKED message names the specific ADR number and title
- [ ] Skill recommends `$architecture-decision` as the next action
- [ ] Story status remains unchanged (not set to In Progress or Complete)

---

### Case 3: Ambiguous Acceptance Criteria — Skill asks for clarification

**Fixture:**
- A story file exists with `Status: Ready`
- Referenced ADR is Accepted
- One acceptance criterion is ambiguous (not Given-When-Then; uses subjective language like "feels responsive")

**Input:** `$dev-story production/epics/[layer]/story-[name].md`

**Expected behavior:**
1. Skill reads the story and identifies the ambiguous criterion
2. Before routing to the specialist, skill asks the user to clarify the criterion
3. User provides a concrete, testable restatement
4. Skill proceeds with implementation using the clarified criterion
5. Skill does NOT guess at the intended behavior

**Assertions:**
- [ ] Skill surfaces the ambiguous criterion before implementation starts
- [ ] Skill asks for user clarification (not auto-interpretation)
- [ ] Implementation begins only after clarification is provided
- [ ] Clarified criterion is used in the test (not the original vague version)

---

### Case 4: Edge Case — No argument; reads from session state

**Fixture:**
- No argument is provided
- `production/session-state/active.md` references an active story file
- That story file exists with `Status: In Progress`

**Input:** `$dev-story` (no argument)

**Expected behavior:**
1. Skill detects no argument is provided
2. Skill reads `production/session-state/active.md`
3. Skill finds the active story reference
4. Skill confirms with user: "Continuing work on [story title] — is that correct?"
5. After confirmation, skill proceeds with that story

**Assertions:**
- [ ] Skill reads session state when no argument is provided
- [ ] Skill confirms the active story with the user before proceeding
- [ ] Skill does NOT silently assume the active story without confirmation
- [ ] If session state has no active story, skill asks which story to implement

---

### Case 5: Director Gate — LP-CODE-REVIEW returns NEEDS CHANGES; lean mode skips gate

**Fixture (full mode):**
- Story is implemented and all criteria appear met
- `production/session-state/review-mode.txt` contains `full`
- LP-CODE-REVIEW gate returns NEEDS CHANGES with specific feedback

**Full mode expected behavior:**
1. LP-CODE-REVIEW gate spawns after implementation
2. Gate returns NEEDS CHANGES with 2 specific issues
3. Story status remains In Progress — NOT marked Complete
4. User is shown the gate feedback and asked how to proceed

**Assertions (full mode):**
- [ ] Story is NOT marked Complete when LP-CODE-REVIEW returns NEEDS CHANGES
- [ ] Gate feedback is shown to the user verbatim
- [ ] Story status stays In Progress until issues are resolved and gate passes

**Fixture (lean mode):**
- Same story, `production/session-state/review-mode.txt` contains `lean`

**Lean mode expected behavior:**
1. Implementation completes
2. LP-CODE-REVIEW gate is skipped — noted in output
3. User is asked to confirm all criteria are met
4. Story is marked Complete after user confirmation

**Assertions (lean mode):**
- [ ] "LP-CODE-REVIEW skipped — lean mode" appears in output
- [ ] Story is marked Complete after user confirms criteria (no gate required)
- [ ] Skill does NOT block on a gate that is skipped

---

## Protocol Compliance

- [ ] Does NOT write source code directly — delegates to specialist agents
- [ ] Reads all context (story, TR-ID, ADR, manifest, engine prefs) before implementation
- [ ] "May I write" asked before updating story status and before writing code files
- [ ] Skipped gates noted by name and mode in output
- [ ] Updates `production/session-state/active.md` after story completion
- [ ] Ends with next-step handoff: `$story-done`

---

## Coverage Notes

- Engine routing logic (Godot vs Unity vs Unreal) is not tested per engine —
  the routing pattern is consistent; engine selection is a config fact.
- Visual/Feel and UI story types (no automated test required) have different
  evidence requirements and are not covered in these cases.
- Integration story type follows the same pattern as Logic but with a different
  evidence path — not independently fixture-tested.

## Phase 1 Backport Regression Cases

These assertions require workflow evaluation; adding them is not a passing test run.

- [ ] Record the starting ref, pre-existing changes, approved file scope, and
  engine-native test roots before delegating implementation.
- [ ] When a worker claims completion but its artifact is absent, incomplete,
  outside scope, or untested, inspect the actual diff and report the gap; never
  infer success from its final message.
- [ ] Reconcile actual story files with the approved scope without attributing
  pre-existing user changes to the story. Ask for newly required scope only.
- [ ] Fresh execution records command, versions, result counts, and build/ref;
  missing tools or zero tests leave verification NOT ASSESSED.
- [ ] A new approved visual capture may save a successful `hash` result to its
  `stamp.json`; no stamp is generated for an old screenshot to hide staleness.
- [ ] Record delivered files and remaining verification in the derived checkpoint;
  implementation completion alone cannot set unverified criteria to passing.

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

## Phase 5A source-scope acceptance

Status: NOT RUN — requires an observed native skill invocation. Configuration
fixture results do not prove this workflow's behavior.

- Resolve the source scope before scans/writes and retain its provenance.
  Test Godot, Unity and Unreal layouts plus an existing custom script folder.
  Use actual paths; never create `src/` to satisfy an example.
- Test lowercase `assets/`, missing conventional roots, conflicting engine
  markers and invalid configuration. Unresolved dependent checks stay
  NOT ASSESSED; no empty scan, fresh-project inference or clean verdict follows.
- Keep source and content scope distinct. Inspect native scenes, local packages
  and plugins where applicable; show scan denominators and exclusions. A
  resolved directory alone supplies no scan, build, coverage or playtest proof.
- Preserve engine-native test locations, explicit target paths, custom layout,
  role ownership and existing write/engine approval gates. A mixed native/custom
  project must not silently omit a source location or follow an external link.

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
