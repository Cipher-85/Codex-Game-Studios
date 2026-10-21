# Skill Test Spec: $test-setup

## Skill Summary

`$test-setup` scaffolds the test framework for the project based on the
configured engine. It resolves engine-native test roots from `coding-standards.md` and
generates the appropriate test runner configuration for the detected engine:
installed GdUnit4 CLI for Godot, test asmdefs under Assets for Unity, or a
compiled Unreal module with a platform-specific build/run command.

Each file or directory created is gated behind a "May I write" ask. If the test
framework already exists, the skill verifies the configuration rather than
reinitializing. No director gates apply. The verdict is COMPLETE when the
scaffold is in place.

---

## Static Assertions (Structural)

Verified automatically by `$skill-test static` — no fixture needed.

- [ ] Has the Codex metadata contract: `name` and `description` in frontmatter; ported fields in `## Ported metadata`, or an explicit Codex-native support classification
- [ ] Has ≥2 phase headings
- [ ] Contains verdict keyword: COMPLETE
- [ ] Contains "May I write" collaborative protocol language before creating files
- [ ] Has a next-step handoff (e.g., `$test-helpers` to generate helper utilities)

---

## Director Gate Checks

None. `$test-setup` is a scaffolding utility. No director gates apply.

---

## Test Cases

### Case 1: Happy Path — Godot project, scaffolds GdUnit4 test structure

**Fixture:**
- `technical-preferences.md` has engine set to Godot 4, language GDScript
- `tests/` directory does not exist yet

**Input:** `$test-setup`

**Expected behavior:**
1. Skill reads engine from `technical-preferences.md` → Godot 4 + GDScript
2. Skill drafts the test directory structure: tests/unit/, tests/integration/,
   tests/smoke/, production/qa/evidence/, production/qa/playtests/, and a README
   referencing the installed GdUnit4 CLI
3. Skill asks "May I write the tests/ directory structure?"
4. Directories and README created on approval; no fake runner is generated
5. Skill resolves the installed `bin/GdUnitCmdTool.gd` path and checks its options
   against the installed version; command uses quoted editor/project paths
6. Verdict is COMPLETE

**Assertions:**
- [ ] Only approved engine test directories and canonical manual evidence destinations are created
- [ ] Installed GdUnit4 CLI is discovered; no SceneTree wrapper can simply exit 0
- [ ] README and CI match the installed runner and shared command contract
- [ ] "May I write" is asked before creating any files
- [ ] Verdict is COMPLETE

---

### Case 2: Unity Project — Scaffolds Unity Test Runner with asmdef

**Fixture:**
- `technical-preferences.md` has engine set to Unity, language C#
- `tests/` directory does not exist

**Input:** `$test-setup`

**Expected behavior:**
1. Skill reads engine → Unity + C#
2. Skill previews `Assets/Tests/EditMode/` and `Assets/Tests/PlayMode/`
3. Skill drafts test asmdefs referencing the actual project assembly
4. EditMode and PlayMode test runner modes are configured
5. Skill asks "May I write the Assets/Tests/ directory structure?" before any writes
6. Verdict is COMPLETE

**Assertions:**
- [ ] Unity-specific `Assets/Tests/` structure is created (not the Godot structure)
- [ ] `.asmdef` files are generated
- [ ] EditMode and PlayMode runner config is present
- [ ] Verdict is COMPLETE

---

### Case 3: Test Framework Already Exists — Verifies config, not re-initialized

**Fixture:**
- `tests/unit/`, `tests/integration/` exist
- Installed GdUnit4 CLI exists (Godot project)

**Input:** `$test-setup`

**Expected behavior:**
1. Skill detects existing tests/ structure
2. Skill reports: "Test framework already exists — verifying configuration"
3. Skill checks: runner script path, directory completeness, CI command alignment
4. If all checks pass: reports "Configuration verified — no changes needed"
5. If checks fail (e.g., missing tests/integration/): reports specific gap and
   asks "May I add the missing directories?"

**Assertions:**
- [ ] Skill does NOT reinitialize when framework exists
- [ ] Verification checks are performed on existing structure
- [ ] Only missing parts trigger a "May I write" ask
- [ ] Verdict is COMPLETE whether everything was OK or gaps were fixed

---

### Case 4: No Engine Configured — Redirects to $setup-engine

**Fixture:**
- `technical-preferences.md` contains only placeholders (engine not set)

**Input:** `$test-setup`

**Expected behavior:**
1. Skill reads `technical-preferences.md` and finds engine placeholder
2. Skill reports: "Engine not configured — cannot scaffold engine-specific test framework"
3. Skill suggests running `$setup-engine` first
4. No directories or files are created

**Assertions:**
- [ ] Error message explicitly states engine is not configured
- [ ] `$setup-engine` is suggested as the next step
- [ ] No write tool is called
- [ ] Verdict is not COMPLETE (blocked state)

---

### Case 5: Director Gate Check — No gate; test-setup is a scaffolding utility

**Fixture:**
- Engine configured, tests/ does not exist

**Input:** `$test-setup`

**Expected behavior:**
1. Skill scaffolds and writes all test framework files
2. No director agents are spawned
3. No gate IDs appear in output

**Assertions:**
- [ ] No director gate is invoked
- [ ] No gate skip messages appear
- [ ] Verdict is COMPLETE without any gate check

---

## Protocol Compliance

- [ ] Reads engine from `technical-preferences.md` before generating any scaffold
- [ ] Generates engine-appropriate test runner config (not generic)
- [ ] Uses the resolved engine test root, not a universal tests/ assumption
- [ ] Asks "May I write" before creating files
- [ ] Detects existing framework and offers verification (not reinitialization)
- [ ] Verdict is COMPLETE when scaffold is in place

---

## Coverage Notes

- Unreal module/build discovery and null-RHI limitations require an engine fixture;
  no rendering claim can be established with `-nullrhi`.
- CI integration file generation (e.g., `.github/workflows/test.yml`) is
  referenced but not assertion-tested here — it may be a separate skill concern.
- The case where tests/ exists but is from a different engine (e.g., Unity tests
  in a now-Godot project) is not tested; the skill would detect the mismatch
  and offer to reconcile.

## Phase 1 Backport Regression Cases

- [ ] Godot: missing addon stops execution claims; no dependency installation
  without authority. Preserve addon casing, use the installed CLI, import first,
  and interpret failed/warning exit codes with actual test counts.
- [ ] Godot target setup: preview `production/.gdignore` with the scaffold; do not
  add it silently to this framework repository.
- [ ] Unity: use the full quoted editor path, both required modes, fresh XML/log
  destinations, and no `-quit`; asmdefs reference existing runtime assemblies.
- [ ] Unreal: place tests inside a compiled module, build its editor target with
  the host platform's tool, and reject zero discovered tests/stale reports.
- [ ] A scaffold may be COMPLETE while execution is explicitly NOT ASSESSED;
  completion of setup must never be reported as tests passing.
- [ ] CI permissions permit intended report publication and generated commands
  reject missing/empty results. All dependency/version choices remain explicit.

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
