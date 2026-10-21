# Skill Test Spec: $help

## Skill Summary

`$help` analyzes what has been done and what comes next in the project workflow.
It runs on the Haiku model (read-only, formatting task) and reads `production/stage.txt`,
the active sprint file, and recent session state to produce a concise situational
guidance summary. The skill optionally accepts a context query (e.g., `$help testing`)
to surface relevant skills for a specific topic.

The output is always informational — no files are written and no director gates
are invoked. The verdict is always HELP COMPLETE. The skill serves as a workflow
navigator, suggesting 2-3 next skills based on the current project state.

---

## Static Assertions (Structural)

Verified automatically by `$skill-test static` — no fixture needed.

- [ ] Has the Codex metadata contract: `name` and `description` in frontmatter; ported fields in `## Ported metadata`, or an explicit Codex-native support classification
- [ ] Has ≥2 phase headings
- [ ] Contains verdict keyword: HELP COMPLETE
- [ ] Does NOT contain "May I write" language (skill is read-only)
- [ ] Has a next-step handoff (suggests 2-3 relevant skills based on state)

---

## Director Gate Checks

None. `$help` is a read-only navigation skill. No director gates apply.

---

## Test Cases

### Case 1: Happy Path — Production stage with active sprint

**Fixture:**
- `production/stage.txt` contains `Production`
- `production/sprints/sprint-004.md` exists with in-progress stories
- `production/session-state/active.md` has a recent checkpoint

**Input:** `$help`

**Expected behavior:**
1. Skill reads stage.txt and active sprint
2. Skill identifies current sprint number and in-progress story count
3. Skill outputs: current stage, sprint summary, and 3 suggested next skills
   (e.g., `$sprint-status`, `$dev-story`, `$story-done`)
4. Suggestions are ranked by relevance to current sprint state
5. Verdict is HELP COMPLETE

**Assertions:**
- [ ] Current stage is shown (Production)
- [ ] Active sprint number and story count are mentioned
- [ ] Exactly 2-3 next-skill suggestions are given (not a list of all skills)
- [ ] Suggestions are appropriate for Production stage
- [ ] Verdict is HELP COMPLETE
- [ ] No files are written

---

### Case 2: Concept Stage — Shows concept-to-systems-design workflow path

**Fixture:**
- `production/stage.txt` contains `Concept`
- No sprint files, no GDD files
- `technical-preferences.md` is configured (engine selected)

**Input:** `$help`

**Expected behavior:**
1. Skill reads stage.txt — detects Concept stage
2. Skill outputs the Concept-stage workflow: brainstorm → map-systems → design-system
3. Suggested skills are: `$brainstorm`, `$map-systems` (if concept exists)
4. Current progress is noted: "Engine configured, concept not yet created"

**Assertions:**
- [ ] Stage is identified as Concept
- [ ] Workflow path shows the expected sequence for this stage
- [ ] Suggestions do not include Production-stage skills (e.g., `$dev-story`)
- [ ] Verdict is HELP COMPLETE

---

### Case 3: No stage.txt — Shows full workflow overview

**Fixture:**
- No `production/stage.txt`
- No sprint files
- `technical-preferences.md` has placeholders

**Input:** `$help`

**Expected behavior:**
1. Skill cannot determine stage from stage.txt
2. Skill runs project-stage-detect logic to infer stage from artifacts
3. If stage cannot be inferred: outputs the full workflow overview from
   Concept through Release as a reference map
4. Primary suggestion is `$start` to begin configuration

**Assertions:**
- [ ] Skill does not crash when stage.txt is absent
- [ ] Full workflow overview is shown when stage cannot be determined
- [ ] `$start` or `$project-stage-detect` is a top suggestion
- [ ] Verdict is HELP COMPLETE

---

### Case 4: Context Query — User asks for help with testing

**Fixture:**
- `production/stage.txt` contains `Production`
- Active sprint has a story with `Status: In Review`

**Input:** `$help testing`

**Expected behavior:**
1. Skill reads context query: "testing"
2. Skill surfaces skills relevant to testing: `$qa-plan`, `$smoke-check`,
   `$regression-suite`, `$test-setup`, `$test-evidence-review`
3. Output is focused on testing workflow, not general sprint navigation
4. Currently in-review story is highlighted as a testing candidate

**Assertions:**
- [ ] Context query is acknowledged in output ("Help topic: testing")
- [ ] At least 3 testing-relevant skills are listed
- [ ] General sprint skills (e.g., `$sprint-plan`) are not the primary suggestions
- [ ] Verdict is HELP COMPLETE

---

### Case 5: Director Gate Check — No gate; help is read-only navigation

**Fixture:**
- Any project state

**Input:** `$help`

**Expected behavior:**
1. Skill produces workflow guidance summary
2. No director agents are spawned
3. No gate IDs appear in output
4. No write tool is called

**Assertions:**
- [ ] No director gate is invoked
- [ ] No write tool is called
- [ ] No gate skip messages appear
- [ ] Verdict is HELP COMPLETE without any gate check

---

## Protocol Compliance

- [ ] Reads stage, sprint, and session state before generating suggestions
- [ ] Suggestions are specific to the current project state (not generic)
- [ ] Context query (if provided) narrows the suggestion set
- [ ] Does not write any files
- [ ] Verdict is HELP COMPLETE in all cases

---

## Coverage Notes

- The case where the active sprint is complete (all stories Done) is not
  separately tested; the skill would suggest `$sprint-plan` for the next sprint.
- The `$help` skill does not validate whether suggested skills are available —
  it assumes standard skill catalog availability.
- Stage detection fallback (when stage.txt is absent) delegates to the same
  logic as `$project-stage-detect` and is not re-tested here in detail.

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
