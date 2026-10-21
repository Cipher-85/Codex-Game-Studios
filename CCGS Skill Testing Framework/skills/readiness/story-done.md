# Skill Test Spec: $story-done

## Skill Summary

`$story-done` closes the loop between design and implementation. Run at the
end of implementing a story, it reads the story file and verifies each
acceptance criterion against the implementation. It checks for GDD and ADR
deviations, prompts a code review, updates the story status to `Complete`,
logs any tech debt, and surfaces the next ready story from the sprint. It
produces a COMPLETE / COMPLETE WITH NOTES / NOT ASSESSED / BLOCKED verdict and writes to
the story file and optionally to `docs/tech-debt-register.md`.

---

## Static Assertions (Structural)

Verified automatically by `$skill-test static` — no fixture needed.

- [ ] Has the Codex metadata contract: `name` and `description` in frontmatter; ported fields in `## Ported metadata`, or an explicit Codex-native support classification
- [ ] Has multiple phases appropriate to its completion and review workflow
- [ ] Contains verdict keywords: COMPLETE, BLOCKED
- [ ] Contains "May I write" collaborative protocol language (writes to story file and tech-debt register)
- [ ] Has a next-step handoff (surfaces next story from sprint)

---

## Test Cases

### Case 1: Happy Path — All acceptance criteria met, no deviations

**Fixture:**
- Story file at `production/epics/core/story-light-pickup.md` with:
  - 3 acceptance criteria, all implemented as described
  - `TR-ID: TR-light-001` referencing a GDD requirement
  - `ADR: docs/architecture/adr-003-inventory.md` (Accepted)
  - `Status: In Progress`
- Implementation files listed in story exist in `src/`
- GDD requirement text at TR-light-001 matches how the feature was implemented
- ADR guidance was followed (no deviations)

**Input:** `$story-done production/epics/core/story-light-pickup.md`

**Expected behavior:**
1. Skill reads the story file and extracts all key fields
2. Skill reads the GDD requirement fresh from `tr-registry.yaml` (not from story's quoted text)
3. Skill reads the referenced ADR to understand implementation constraints
4. Skill evaluates each acceptance criterion (auto where possible, manual prompt where not)
5. Skill checks for GDD requirement deviations
6. Skill checks for ADR guideline deviations
7. Skill prompts user: "Please provide the code review outcome for this story"
8. Skill presents COMPLETE verdict
9. Skill asks "May I update story Status to Complete and add Completion Notes?"
10. If yes: skill updates the story file
11. Skill surfaces the next `Ready for Dev` story from the sprint

**Assertions:**
- [ ] Skill reads `docs/architecture/tr-registry.yaml` for TR-ID requirement text (not just story)
- [ ] Skill reads the referenced ADR file (not just the story reference)
- [ ] Each acceptance criterion is listed with VERIFIED / DEFERRED or UNTESTED (NOT ASSESSED) / FAILED status
- [ ] Skill prompts the user for code review outcome (does not skip this step)
- [ ] Verdict is COMPLETE when all criteria are verified and no deviations exist
- [ ] Skill asks "May I write" before updating the story file
- [ ] Skill does NOT auto-update story status without user confirmation
- [ ] After completion, skill surfaces the next ready story from `production/sprints/`

---

### Case 2: Blocked Path — Acceptance criterion cannot be verified

**Fixture:**
- Story file has an acceptance criterion: "Player sees correct animation on pickup"
- No automated test for this criterion exists
- Manual verification has not been performed
- All other criteria are met

**Input:** `$story-done production/epics/core/story-light-pickup.md`

**Expected behavior:**
1. Skill processes all acceptance criteria
2. Reaches the animation criterion — cannot auto-verify
3. Skill asks the user: "Acceptance criterion 'Player sees correct animation on
   pickup' cannot be auto-verified. Has this been manually tested?"
4. If user says No: criterion is marked DEFERRED, overall verdict remains NOT ASSESSED
5. Skill records the deferred criterion and owed playtest; story remains open
6. Offers a checkpoint or asks to record the missing evidence without marking verified completion

**Assertions:**
- [ ] Skill asks the user about unverifiable criteria rather than assuming PASS
- [ ] Required deferred criteria result in NOT ASSESSED; an observed failure still yields BLOCKED
- [ ] The deferred criterion is explicitly named in the completion notes
- [ ] Skill still asks "May I write" before updating the story file

---

### Case 3: Blocked Path — GDD deviation detected

**Fixture:**
- Story TR-ID points to requirement: "Player can carry max 3 light sources"
- Implementation in `src/` uses a variable `MAX_CARRIED_LIGHTS = 5`
- This is a deliberate deviation from the GDD

**Input:** `$story-done production/epics/core/story-light-pickup.md`

**Expected behavior:**
1. Skill reads the GDD requirement text (max 3)
2. Skill detects discrepancy between requirement and implementation value (5)
3. Skill flags this as a GDD deviation and asks the user to classify it:
   - INTENTIONAL: document the deviation and reason
   - ERROR: implementation must be fixed before story can be marked Complete
   - OUT OF SCOPE: requirement changed and GDD needs updating
4. If INTENTIONAL: skill records deviation in completion notes, verdict is COMPLETE WITH NOTES
5. If ERROR: verdict is BLOCKED until implementation is corrected

**Assertions:**
- [ ] Skill detects the mismatch between GDD requirement and implementation value
- [ ] Skill asks the user to classify the deviation (not auto-assumes either way)
- [ ] INTENTIONAL deviation → COMPLETE WITH NOTES (not BLOCKED)
- [ ] ERROR deviation → BLOCKED verdict until fixed
- [ ] Detected deviations are recorded in completion notes or tech debt register

---

### Case 4: Edge Case — No argument, auto-detect current story

**Fixture:**
- `production/session-state/active.md` contains a reference to
  `production/epics/core/story-oxygen-drain.md` as the active story
- That story file exists with `Status: In Progress`

**Input:** `$story-done` (no argument)

**Expected behavior:**
1. Skill reads `production/session-state/active.md`
2. Skill finds the active story reference
3. Skill reads that story file and proceeds normally
4. Output confirms which story was auto-detected

**Assertions:**
- [ ] Skill reads `production/session-state/active.md` when no argument is given
- [ ] Skill identifies and confirms the auto-detected story before proceeding
- [ ] If no story is found in session state, skill asks the user to provide a path

---

---

### Case 5: Director Gate — LP-CODE-REVIEW behavior across review modes

**Fixture:**
- Story file at `production/epics/core/story-light-pickup.md`
- All acceptance criteria verified, no GDD deviations
- `production/review-mode.txt` exists

**Case 5a — full mode:**
- `review-mode.txt` contains `full`

**Input:** `$story-done production/epics/core/story-light-pickup.md` (full mode)

**Expected behavior:**
1. Skill reads review mode — determines `full`
2. After implementation verification, skill invokes LP-CODE-REVIEW gate
3. Lead programmer reviews the implementation
4. If LP verdict is NEEDS CHANGES → story cannot be marked Complete
5. If LP verdict is APPROVED → skill proceeds to mark story Complete

**Assertions (5a):**
- [ ] Skill reads review mode before deciding whether to invoke LP-CODE-REVIEW
- [ ] LP-CODE-REVIEW gate is invoked in full mode after implementation check
- [ ] An LP NEEDS CHANGES verdict prevents story from being marked Complete
- [ ] Gate result is noted in output: "Gate: LP-CODE-REVIEW — [result]"
- [ ] Skill still asks "May I write" before updating story status even if LP approved

**Case 5b — lean or solo mode:**
- `review-mode.txt` contains `lean` or `solo`

**Expected behavior:**
1. Skill reads review mode — determines `lean` or `solo`
2. LP-CODE-REVIEW gate is SKIPPED
3. Output notes the skip: "[LP-CODE-REVIEW] skipped — Lean/Solo mode"
4. Story completion proceeds based on acceptance criteria check only

**Assertions (5b):**
- [ ] LP-CODE-REVIEW gate does NOT spawn in lean or solo mode
- [ ] Skip is explicitly noted in output
- [ ] Skill still requires "May I write" approval before marking story Complete

---

## Protocol Compliance

- [ ] Uses "May I write" before updating the story file
- [ ] Uses "May I write" before adding entries to `docs/tech-debt-register.md`
- [ ] Presents complete findings (criteria check, deviation check) before asking approval
- [ ] Ends by surfacing the next ready story from the sprint plan
- [ ] Does not mark a story Complete if any criteria are in ERROR state
- [ ] Does not skip the code review prompt

---

## Coverage Notes

- The full 8-phase flow of the skill is exercised across Cases 1-3; not all
  edge cases within each phase are covered.
- Tech debt logging (deferred items written to `docs/tech-debt-register.md`)
  is mentioned in Case 2 but not the primary assertion focus; dedicated
  coverage deferred.
- The `sprint-status.yaml` update (Phase 7 in the skill) is implied by Case 1
  but not the primary assertion; assumed to follow the same "May I write" pattern.
- Stories with multiple TR-IDs or multiple ADRs are not explicitly tested.

## Phase 1 Backport Regression Cases

- [ ] With no `## Files` or legacy implementation list and no reliable story
  diff baseline, report scope NOT ASSESSED. Unrelated dirty files are not owned
  by this story; a clean tree is not a completed scope review.
- [ ] Open each cited screenshot. Missing/unreadable images and unrun required
  playtests remain unassessed even when lead sign-off policy is advisory.
- [ ] Read canonical playtests from `production/qa/playtests/`.
- [ ] Check the existing capture stamp without rewriting it: CHANGED/GONE requires
  fresh evidence; NO_RECEIPT is unknown; UNCHANGED does not prove execution.
- [ ] Never mint a new stamp to make an old capture appear current.
- [ ] Every report identifies the actual reviewer, user-reported review, or
  `self — no independent review`; a skipped role gate is never a role verdict.
- [ ] Explicit administrative closure preserves BLOCKED/NOT ASSESSED and owed
  verification; it cannot count as passing evidence for sprint or phase gates.

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
