# Coding Standards

- All game code must include doc comments on public APIs
- Architecture requirements follow `.codex/docs/workflow-modes.md`: existing
  compatibility/full systems require ADRs; standard requires critical Foundation
  decisions; minimal may use the approved brief. Existing Accepted decisions remain binding.
- Gameplay values must be data-driven (external config), never hardcoded
- All public methods must be unit-testable (dependency injection over singletons)
- Commits must reference the relevant design document or task ID
- **Commit messages**: Use Conventional Commits format — `feat:`, `fix:`, `chore:`, `docs:`, `test:`, `refactor:`. Reference the story or task ID in the body (e.g., `Story: EPIC-001-S02`).
- **Verification-driven development**: Write tests first when adding gameplay systems.
  For UI changes, verify with screenshots. Compare expected output to actual output
  before marking work complete. Every implementation should have a way to prove it works.

# Design Document Standards

- All design docs use Markdown
- Resolve the effective workflow through `.codex/docs/workflow-modes.md` before
  authoring or checking design completeness. It defines the brief, tier-required
  system GDD sections, heading aliases and conditional numeric formulas.
- Retain existing optional content and review it for correctness.
- Balance values must link to their source formula or rationale

# Testing Standards

Read `.codex/docs/qa-policy.md` and the shared `qa-policy` result before applying
QA levels or strictness. The evidence requirements below remain the floor; false
strictness never waives a failed test or required unassessed criterion. Read
`.codex/docs/technical-config.md` for actual pins, runner validation and budgets.


## Test Evidence by Story Type

All stories must have appropriate test evidence before they can be marked Done:

| Story Type | Required Evidence | Location | Gate Level |
|---|---|---|---|
| **Logic** (formulas, AI, state machines) | Automated unit test — must pass | Engine test root below | BLOCKING |
| **Integration** (multi-system) | Integration test OR documented playtest | Engine test root or `production/qa/playtests/` | BLOCKING |
| **Visual/Feel** (animation, VFX, feel) | Opened screenshot + observed run + lead sign-off | `production/qa/evidence/` | ADVISORY |
| **UI** (menus, HUD, screens) | Observed walkthrough or interaction test; opened screenshot for visible criteria | `production/qa/evidence/` | ADVISORY |
| **Config/Data** (balance tuning) | Smoke check pass | `production/qa/smoke-[date].md` | ADVISORY |

## Automated Test Rules

- **Naming**: `[system]_[feature]_test.[ext]` for files; `test_[scenario]_[expected]` for functions
- **Determinism**: Tests must produce the same result every run — no random seeds, no time-dependent assertions
- **Isolation**: Each test sets up and tears down its own state; tests must not depend on execution order
- **No hardcoded data**: Test fixtures use constant files or factory functions, not inline magic numbers
  (exception: boundary value tests where the exact number IS the point)
- **Independence**: Unit tests do not call external APIs, databases, or file I/O — use dependency injection

## What NOT to Automate

- Visual fidelity (shader output, VFX appearance, animation curves)
- "Feel" qualities (input responsiveness, perceived weight, timing)
- Platform-specific rendering (test on target hardware, not headlessly)
- Full gameplay sessions (covered by playtesting, not automation)

## CI/CD Rules

- Automated test suite runs on every push to main and every PR
- No merge if tests fail — tests are a blocking gate in CI
- Never disable or skip failing tests to make CI pass — fix the underlying issue
- Branch protection is configured separately; creating a workflow does not enforce it.

## Engine Test Execution Contract

Keep the project's pinned engine and installed test-framework version. First read
`docs/engine-reference/<engine>/VERSION.md`, the project's test README/CI command,
and the installed runner's help. Preserve a custom runner when it is usable.
No workflow installs dependencies or replaces a runner without approval.

| Engine | Code root | Test root |
|---|---|---|
| Godot | `src/` or the project's declared layout | `tests/unit/`, `tests/integration/` |
| Unity | `Assets/` | `Assets/Tests/EditMode/`, `Assets/Tests/PlayMode/` with test assembly definitions |
| Unreal | `Source/<Module>/` | `Source/<Module>/Private/Tests/` in a compiled module, or an existing test module |

Resolve `<Module>` from the project and its `.Build.cs`; never create a literal
placeholder path. Prefer the exact Test Evidence path in the story. An unresolved
engine, module, executable, or test root is NOT ASSESSED, not an empty successful
search. Shared manual smoke lists may remain under `tests/smoke/` on every engine.

### Godot / gdUnit4

Use the project's quoted editor executable (full path when not on PATH). Import a
fresh checkout before running tests. Observe import errors; import is not a test
or visual run. gdUnit4 supplies `bin/GdUnitCmdTool.gd` and `runtest.sh`/`runtest.cmd`
in its installed addon. Discover the actual case-sensitive addon path; releases
use different casing. Use that version's runner/help and compatible engine.

Example after resolving the executable and addon path:

```bash
"$godot_editor" --headless --path "$project_root" --import
"$godot_editor" --headless --path "$project_root" --script "$gdunit_cli" -a tests/unit -a tests/integration
```

Stop if import fails or logs script errors. Verify that the installed runner
supports these options; use its supplied wrapper when required. Never synthesize
a SceneTree wrapper that calls `run_tests()` then exits successfully. Capture the
runner's status before any log-copy command. In versions documenting gdUnit4
codes 100/101, 100 means test failures and 101 means warnings: inspect counts and
warnings. A warning code can yield PASS WITH WARNINGS only when tests actually
ran, no required test was skipped, and no assertion/compile error occurred.

### Unity / Test Framework

Use the full Editor executable, not an assumed `Unity` CLI alias. Test assemblies
must reference the actual game assembly and test framework; EditMode assemblies
are Editor-only. Preserve existing asmdefs; do not fabricate an assembly name.
Generate them via the Editor's test-assembly tools or the installed package's
supported format, then confirm discovery.

```bash
"$unity_editor" -batchmode -projectPath "$project_root" -runTests -testPlatform EditMode -testResults "$run_dir/editmode.xml" -logFile "$run_dir/editmode.log"
"$unity_editor" -batchmode -projectPath "$project_root" -runTests -testPlatform PlayMode -testResults "$run_dir/playmode.xml" -logFile "$run_dir/playmode.log"
```

Use a fresh approved output directory per run. Do not add `-quit`: test execution
owns shutdown. Read this run's NUnit XML and compiler/log output; an exit code
alone is insufficient. No test cases or no fresh XML is NOT ASSESSED unless a
known compile/test failure already makes the result FAIL.

### Unreal / Automation

Build the actual Editor target with the platform's supported build tool before
testing a fresh checkout. Resolve executable, absolute `.uproject` path, module,
configuration, test prefix, and platform from the project. On Windows use the
matching `Build.bat`; on Linux/macOS use the installed engine's supported build
script. If a command-line editor is unavailable, report NOT ASSESSED and the
required Editor/CI action instead of inventing a binary path.

```bash
"$ue_editor" "$uproject" -unattended -nopause -nullrhi -nosound -log -stdout -FullStdOutLogOutput -ExecCmds="Automation RunTests $test_prefix; Quit" -ReportExportPath="$run_dir"
```

Confirm the pinned editor supports the command. Read the fresh automation report
and output, including the matched test count. A nonzero exit with failed tests
is FAIL; no matching tests is NOT ASSESSED. Report compile errors as FAIL.
`-nullrhi` tests cannot establish rendering or visual acceptance.

### Results and provenance (all engines)

Record command, engine/framework version, build/ref and dirty state, run time,
exit code, test counts, skipped cases, and the exact fresh report/log paths.
Do not reuse the newest old report as this run's output. Required tests must run;
zero tests, an interrupted run, missing/unreadable results, or missing tooling
are NOT ASSESSED. An observed failure outranks missing evidence. Follow
`.codex/docs/verification-integrity.md` for verdict and visual evidence rules.

Primary references (check the installed version before applying examples):
- [gdUnit4 command line](https://github.com/godot-gdunit-labs/gdUnit4/blob/master/documentation/doc/_advanced_testing/cmd.md)
- [Unity Test Framework command line](https://docs.unity3d.com/Packages/com.unity.test-framework@1.4/manual/reference-command-line.html)
- [Unreal automation execution](https://dev.epicgames.com/documentation/en-us/unreal-engine/run-automation-tests-in-unreal-engine)
