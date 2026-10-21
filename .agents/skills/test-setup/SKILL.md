---
name: test-setup
description: "Scaffold engine-native tests and the CI/CD pipeline for the project's engine. Creates the tests/ directory structure, engine-specific test runner configuration, and GitHub Actions workflow. Run once during Technical Setup phase before the first sprint begins for Codex Game Studios."
---

## Technical configuration

Before using engine, framework, platform or performance fields, read
`.codex/docs/technical-config.md` and run `project_config.py technical`. Use its
resolved values/provenance for typed fields; the technical-preferences reads
below still supply custom prose, policies and routing notes. Check conflicts
and field-specific readiness before affected work. Pin agreement is not an
engine run; runner availability needs actual metadata/help verification. Keep
estimates separate from measured evidence and preserve existing pins/runners.

**Setup write boundary:** Before the write phases below, use the approved-setup
procedure in `technical-config.md`. Preview one exact changeset including active
YAML/legacy targets, affected pins and runner files; preserve unrelated content.
A settings declaration alone does not install a framework or migrate an engine.
Re-read inputs before editing, re-resolve/read back afterward, and report unrun
engine/import/build/test checks separately. Existing custom runners are retained.

## QA configuration

Before evidence planning or a QA verdict, read `.codex/docs/qa-policy.md` and run
`project_config.py qa-policy`. Keep level/source, effective type gates and any
active coverage threshold. Apply it to the checks and delegated briefs below.
Required evidence, known failures and unassessed criteria retain their existing
blocking behavior at every level. Strict false cannot waive that floor. Full QA
adds affected critical-path regression evidence; optional numeric coverage uses
an applicable measured report, never test counts. Report unrun checks honestly.


# Test Setup

This skill scaffolds the automated testing infrastructure for the project.
It detects the configured engine, generates the appropriate test runner
configuration, creates the standard directory layout, and wires up CI/CD
so tests run on every push.

Run this once during the Technical Setup phase, before any implementation
begins. A test framework installed at sprint start costs 30 minutes.
A test framework installed at sprint four costs 3 sprints.

**Output:** `tests/` directory structure + `.github/workflows/tests.yml`

Before planning or writing `tests/**`, read
`.codex/instructions/path-rules/test-standards.md`. `tests/` is created lazily
by this workflow after the user approves the test setup plan.

---

## Phase 1: Detect Engine and Existing State

1. **Read engine config**:
   - Use the shared technical result for engine family, language and reference pin.
   - If required engine configuration is missing or conflicted, stop:
     "Engine not configured. Run `$setup-engine` first, then re-run `$test-setup`."

2. **Check for existing test infrastructure**:
   - Resolve the engine test roots from `.codex/docs/coding-standards.md`.
   - Inspect those roots and the installed framework/version before proposing files.
   - Glob `.github/workflows/` — does a CI workflow file exist?
   - Inspect existing custom commands, gdUnit4 addon runner (Godot),
     `Assets/Tests/` assemblies (Unity), or tests in a compiled module (Unreal).

3. **Report findings**:
   - "Engine: [engine]. Test directory: [found / not found]. CI workflow: [found / not found]."
   - If everything already exists AND `force` argument was not passed:
     "Test infrastructure appears to be in place. Re-run with `$test-setup force`
     to regenerate. Proceeding will not overwrite existing test files."

If the `force` argument is passed, skip the "already exists" early-exit and
proceed — but still do not overwrite files that already exist at a given path.
Only create files that are missing.

---

## Phase 2: Present Plan

Based on the engine detected and the existing state, present a plan:

```
## Test Setup Plan — [Engine]

I will create the following (skipping any that already exist):

[Resolved engine test root]/ — Automated tests and README
tests/smoke/                — Shared manual smoke checklist
production/qa/evidence/     — Approved visual evidence destinations
production/qa/playtests/    — Approved playtest report destinations

[Engine-specific files — see per-engine details below]

.github/workflows/tests.yml  — CI: run tests on every push to main

Estimated time: ~5 minutes to create all files.
```

Ask: "May I create these files? I will not overwrite any test files that
already exist at these paths."

Do not proceed without approval.

---

## Phase 3: Create Directory Structure

After approval, create only the resolved paths in the plan. The following
Godot README/layout is an example: substitute Unity/Unreal test roots before
showing the plan or writing it. Manual evidence always uses `production/qa/`.

### `tests/README.md`

```markdown
# Test Infrastructure

**Engine**: [engine name + version]
**Test Framework**: [GdUnit4 | Unity Test Framework | UE Automation]
**CI**: `.github/workflows/tests.yml`
**Setup date**: [date]

## Directory Layout

```
tests/
  unit/           # Isolated unit tests (formulas, state machines, logic)
  integration/    # Cross-system and save/load tests
  smoke/          # Critical path test list for $smoke-check gate
  # Screenshots/sign-off: production/qa/evidence/; playtests: production/qa/playtests/
```

## Running Tests

[Engine-specific command — see below]

## Test Naming

- **Files**: `[system]_[feature]_test.[ext]`
- **Functions**: `test_[scenario]_[expected]`
- **Example**: `combat_damage_test.gd` → `test_base_attack_returns_expected_damage()`

## Story Type → Test Evidence

| Story Type | Required Evidence | Location |
|---|---|---|
| Logic | Automated unit test — must pass | `tests/unit/[system]/` |
| Integration | Integration test OR playtest doc | `tests/integration/[system]/` |
| Visual/Feel | Screenshot + lead sign-off | `production/qa/evidence/` |
| UI | Manual walkthrough OR interaction test | `production/qa/evidence/` |
| Config/Data | Smoke check pass | `production/qa/smoke-*.md` |

## CI

Tests run automatically on every push to `main` and on every pull request.
A failed suite must block the test job. Requiring that job for merges needs
branch protection configured separately; do not claim the workflow enables it.
```
```

### Engine-specific files

#### Godot 4 (`Engine: Godot`)

Read the Godot execution contract in `.codex/docs/coding-standards.md`.
Record the installed gdUnit4 runner and exact command in `tests/README.md`.
Create `tests/unit/.gitkeep` and `tests/integration/.gitkeep` if needed.
Do not generate a replacement runner. If gdUnit4 is absent, report setup as
incomplete and present installation as a separate approval decision.

Include an empty `production/.gdignore` in the Godot setup preview when missing;
this excludes evidence images/audio from Godot imports and default exports.
Do not replace an existing file. This is Godot-only and requires the setup approval.

#### Unity (`Engine: Unity`)

Use `Assets/Tests/EditMode/` and `Assets/Tests/PlayMode/`, each with its test
assembly definition and README. Resolve the game's assembly references from
existing asmdefs. Prefer the Editor's test-assembly creation tools; otherwise
use the installed Test Framework's supported asmdef format and validate it in
the Editor. The plan must name the exact asmdef files and references. Preserve
existing assemblies, and report missing game/test assemblies instead of guessing.
Document both CLI commands from the coding standards. A README alone is not
working test infrastructure: confirm compilation and nonzero discovery.

#### Unreal Engine (`Engine: Unreal` or `Engine: UE5`)

Find the module's `.Build.cs` and Editor target. Put tests in the existing test
module or `Source/<Module>/Private/Tests/`, never an uncompiled standalone folder.
Create a README there describing the project's actual test filter, build command,
and automation command from the coding standards. Ask separately before changing
an existing module's build configuration. Each automation test needs a unique
class and an applicable context plus filter, for example
`EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter` for
Editor tests, guarded by `WITH_DEV_AUTOMATION_TESTS`.

---

## Phase 4: Create CI/CD Workflow

Keep existing CI and action pins unless a supported change is required and
included in the approved preview. For every engine, validate a fresh report with
nonzero executed tests, no failed required cases and no skipped required cases;
fail the job when results are missing or unassessed. Configure a report parser or
use a runner that enforces this, and validate it with an empty-suite case before
calling CI ready. Artifact-upload success alone is not a test verdict.

Godot's `version: installed` preserves the committed addon. Verify the selected
action supports its case-sensitive directory and exact engine/framework pair;
otherwise use the existing project's compatible CI runner. Never silently fetch
`latest`. Check the job result, not only a report-publishing check.

### Godot 4

Create `.github/workflows/tests.yml`:

```yaml
name: Automated Tests

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    name: Run GdUnit4 Tests
    runs-on: ubuntu-latest
    permissions:
      contents: read
      checks: write

    steps:
      - name: Checkout
        uses: actions/checkout@v4
        with:
          lfs: true

      - name: Run GdUnit4 Tests
        uses: MikeSchulze/gdUnit4-action@v1
        with:
          godot-version: '[FULL PINNED VERSION VERIFIED FROM THE EDITOR]'
          version: 'installed'
          paths: |
            tests/unit
            tests/integration
          report-name: test-results

      - name: Upload Test Results
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: test-results
          path: reports/
```

### Unity

Create `.github/workflows/tests.yml`:

```yaml
name: Automated Tests

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    name: Run Unity Tests
    runs-on: ubuntu-latest

    steps:
      - name: Checkout
        uses: actions/checkout@v4
        with:
          lfs: true

      - name: Run Edit Mode Tests
        uses: game-ci/unity-test-runner@v4
        env:
          UNITY_LICENSE: ${{ secrets.UNITY_LICENSE }}
        with:
          testMode: editmode
          artifactsPath: test-results/editmode

      - name: Run Play Mode Tests
        uses: game-ci/unity-test-runner@v4
        env:
          UNITY_LICENSE: ${{ secrets.UNITY_LICENSE }}
        with:
          testMode: playmode
          artifactsPath: test-results/playmode

      - name: Upload Test Results
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: test-results
          path: test-results/
```

Note: Unity CI requires a `UNITY_LICENSE` secret. Add to GitHub repository
secrets before the first CI run.

### Unreal Engine

Generate CI only after resolving the runner OS, engine executable, Editor target,
module and test prefix. Show the full resulting workflow in the setup preview.
Use an OS-specific self-hosted label (for example `[self-hosted, windows]`), build
the Editor target first, then run the automation command from
`.codex/docs/coding-standards.md` with absolute quoted paths and a fresh report
directory. On Windows use PowerShell and the installed `Build.bat`/Editor paths;
check `$LASTEXITCODE` after each process. On Linux use the corresponding build
script and command-line editor. Never assume a generic self-hosted runner is
Windows, or emit an unresolved `[ProjectName]` into a working workflow.

Retain logs and report artifacts even on failure. Validate actual executed test
counts and results: no matches/missing reports must fail the CI job as unassessed,
not produce a green job. If the needed runner is unavailable, leave CI execution
NOT ASSESSED and identify the exact setup/action still owed.

---

## Phase 5: Create Smoke Test Seed

Create `tests/smoke/critical-paths.md`:

```markdown
# Smoke Test: Critical Paths

**Purpose**: Run these 10-15 checks in under 15 minutes before any QA hand-off.
**Run via**: `$smoke-check` (which reads this file)
**Update**: Add new entries when new core systems are implemented.

## Core Stability (always run)

1. Game launches to main menu without crash
2. New game / session can be started from the main menu
3. Main menu responds to all inputs without freezing

## Core Mechanic (update per sprint)

<!-- Add the primary mechanic for each sprint here as it is implemented -->
<!-- Example: "Player can move, jump, and the camera follows correctly" -->
4. [Primary mechanic — update when first core system is implemented]

## Data Integrity

5. Save game completes without error (once save system is implemented)
6. Load game restores correct state (once load system is implemented)

## Performance

7. No visible frame rate drops on target hardware (60fps target)
8. No memory growth over 5 minutes of play (once core loop is implemented)
```

---

## Phase 6: Post-Setup Summary

After writing all files, report:

```
Test infrastructure created for [engine].

Files created:
- tests/README.md
- tests/unit/ (directory)
- tests/integration/ (directory)
- tests/smoke/critical-paths.md
- tests/evidence/ (directory)
[engine-specific files]
- .github/workflows/tests.yml

Next steps:
1. [Engine-specific install step, e.g., "Install GdUnit4 via AssetLib"]
2. Write your first test: create tests/unit/[first-system]/[system]_test.[ext]
3. Run `$qa-plan sprint` before your first sprint to classify stories and set
   test evidence requirements
4. `$smoke-check` before every QA hand-off

Gate note: $gate-check Technical Setup → Pre-Production now requires:
- tests/ directory with unit/ and integration/ subdirectories
- .github/workflows/tests.yml
- At least one example test file
Run $test-setup and write one example test before advancing.

Verdict: **COMPLETE** — test framework scaffolded and CI/CD wired up.
```

---

## Collaborative Protocol

- **Never overwrite existing test files** — only create files that are missing.
  If a test runner file exists, leave it as-is.
- **Always ask before creating files** — Phase 2 requires explicit approval.
- **Engine detection is non-negotiable** — if the engine is not configured,
  stop and redirect to `$setup-engine`. Do not guess.
- **`force` flag skips the "already exists" early-exit but never overwrites.**
  It means "create any missing files even if the directory already exists."
- For Unity CI, note that the `UNITY_LICENSE` secret must be configured
  manually. Do not attempt to automate license management.

## Ported metadata

The following upstream metadata is preserved as context only; Codex does not enforce it from skill frontmatter.

- `argument-hint: "[force]"`
- `user-invocable: true`
- `allowed-tools: Read, Glob, Grep, Bash, Write`

## Codex Model Guidance

Suggested model: `gpt-5.6-sol`. This is guidance only; Codex does not enforce a model from skill frontmatter.
