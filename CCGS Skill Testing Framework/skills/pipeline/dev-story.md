# Skill Test Spec: $dev-story

## Skill Summary

Implements an approved story through the matching programmer role, then verifies
its actual artifacts and runs a separate engine-specialist review for code.
Implementation status and evidence are reported separately. Story closure belongs
to `$story-done`; this skill never marks a story Complete merely because a worker
returns. Config/Data follows its no-agent path and still needs applicable checks.

## Static Assertions (Structural)

These are specifications, not a record of native execution.

- [ ] Has Codex name/description metadata, multiple phases and bounded-read guidance.
- [ ] Loads linked `references/version-mismatch.md` and `references/engine-checks.md`
      when their phases apply. Missing support files are not silently skipped.
- [ ] Requires approved source, test, story and evidence paths before writes.
- [ ] Keeps implementation COMPLETE/INCOMPLETE/BLOCKED distinct from story closure.
- [ ] Routes to `$code-review` and `$story-done` after the implementation summary.

## Director Gate Checks

The post-implementation engine-specialist review is not a director gate and runs
for code stories in full, lean and solo. LP-CODE-REVIEW belongs to the separate
review/closure flow. A failed custom-role load is NOT ASSESSED, never a simulated
specialist verdict.

## Test Cases

### Case 1: Code story — verified artifacts and engine review

**Fixture:** Ready story with concrete criteria, approved source/test paths,
accepted named ADR, valid configured engine, and required tier-specific context.
**Input:** `$dev-story <story-path>` in each review mode.

- [ ] Reads the story and applicable context before delegating to the exact role.
- [ ] Includes tests and declared evidence in the approved implementation scope.
- [ ] On worker return, inspects existing files and the actual diff.
- [ ] Only then spawns the configured engine reviewer, with read-only authority.
- [ ] Reports current check commands/results and unverified criteria separately.
- [ ] Does not close the story; routes closure to `$story-done`.

### Case 2: Proposed ADR or ambiguous criterion

**Fixture:** A named governing ADR is Proposed, or a criterion is subjective and
has no agreed observable meaning.

- [ ] Names the blocking ADR before implementation begins.
- [ ] Surfaces unresolved design meaning to the user; does not invent acceptance.
- [ ] Does not perform unapproved story/status writes while reporting the blocker.

### Case 3: Worker output absent or engine review requires corrections

**Fixture:** Worker claims success but a file is missing; repeat with a real file
and a criterion-breaking engine review finding.

- [ ] Missing artifacts produce INCOMPLETE with exact owed outputs.
- [ ] Returns required corrections within approved scope to the programmer.
- [ ] Re-reads and re-reviews corrected files before claiming completion.
- [ ] Scope expansion requires approval; advisory findings remain visible.
- [ ] Unavailable role evidence remains NOT ASSESSED in every director mode.

### Case 4: No argument and mismatched manifest version

**Fixture:** Active checkpoint names an In Progress story with a stale manifest.

- [ ] Reads and confirms the selected story before implementation.
- [ ] Loads the version-mismatch support reference and presents its decision.
- [ ] Does not silently refresh the version or ignore changed layer constraints.
- [ ] Uses complete required sections; duplicate/missing headings are reported.

### Case 5: Config/Data and Visual/Feel evidence boundaries

- [ ] Config/Data edits use approved scope without unnecessary programmer or
      engine-review spawns; applicable smoke evidence is still owed.
- [ ] Visual/Feel uses the matching programmer and post-code engine review.
- [ ] Captures are opened and linked to criteria; no old capture is newly stamped.
- [ ] User-owned feel judgment stays unverified until the user supplies it.
- [ ] Implementation approval alone does not approve builds or additional writes.

## Protocol Compliance

- [ ] Delegates code to its owner and passes paths plus targeted reading instructions.
- [ ] A missing write approval returns a draft/question to the caller and ends
      the worker turn; the parent owns the user prompt.
- [ ] Existing scope approval carries forward without duplicate permission prompts.
- [ ] Story and sprint-status updates require their paths in the approved changeset.
- [ ] Only the derived active checkpoint uses the declared checkpoint exception.

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
