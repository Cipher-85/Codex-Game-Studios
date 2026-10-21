# Technical configuration consumers

Before engine/framework selection, platform-dependent design, performance
comparison or technical-role dispatch, run
`python3 .codex/lib/project_config.py technical` at the bound root. Outside it,
use the installed helper's absolute path and `--root <bound-root>`. Preserve
values, provenance, conflicts, unmapped fields and readiness limits.

`status: ready` means configuration parsed. It does not mean the engine ran,
the runner exists or a benchmark passed. Invalid input stops affected work.
Use missing/ambiguous fields as NOT ASSESSED and ask only for what that operation
needs. Keep unrelated diagnostic and read-only work available.

## Sources and preservation

Supported values use the resolver's precedence: allowed local overrides,
explicit project YAML, exact supported legacy fields, then existing compatibility
behavior. No engine, version, framework, platform or budget is guessed from a
rigor level. The helper reads literal fields in `technical-preferences.md`:
Engine/Language, Framework/Minimum Coverage, Target Platforms/Primary Input/
Gamepad Support/Touch Support, and the four Performance Budgets. Supported units
are fps, ms, draw calls, MB and percent. Comma-separated targets form a list.
Unsupported prose/units remain unmapped and visible; they are not silently
converted. Duplicate known fields and invalid literal values fail validation.

All other prose remains authoritative, including naming conventions, required
tests, forbidden patterns, libraries, rendering/physics choices, input-method
details and custom specialist routing. Read that context as well as the typed
result. The reader never rewrites it. Root YAML and legacy documents stay
project-owned; package installation never creates a game configuration.

## Engine, pin, runner and roles

The engine family selects the corresponding existing reference directory.
The reader checks its explicit `Engine Version` field in `VERSION.md`; it does
not extract a separate version from a legacy Engine line. A YAML/pin mismatch,
conflicting engine family or language declaration stops dependent guidance until
the user resolves it. An unconfigured engine or missing pin is NOT ASSESSED.
Read the actual engine reference and executable version before relying on APIs.
`engine_ready` only describes reference/config agreement, never a launched build.

Preserve installed test frameworks and custom runners. Confirm the chosen
framework against project manifests, test README/CI and the installed runner's
help before generating helpers or running tests. The helper deliberately reports
`runner_status: NOT ASSESSED`; configuration cannot prove an installation.
A framework conflict requires a scoped choice, not automatic replacement or
dependency installation. Follow `coding-standards.md` for command/output evidence.

Keep custom specialist fields and route notes in technical-preferences. Resolve
their exact role names against `.codex/agents/*.toml`; an unknown or wrong-engine
role is not a successful routing result. Multiple listed alternatives require
selection by actual language/file scope. When unconfigured, propose the matching
registered engine role for approval under the existing skill flow; do not change
model/effort settings. Actual child-role identity still requires runtime proof.

## Source scope

Before source/content scans or source writes, run
`python3 .codex/lib/project_config.py code-root` from the bound root (or use the
installed helper's absolute path with `--root <bound-root>`). Keep `roots`,
`content_roots`, `source`, `evidence`, `resolution` and any conflicts in the
working context. This is path discovery only: `scan_status: NOT ASSESSED` stays
unchanged until the calling workflow actually scans its declared scope.

The reader uses the configured engine, including supported legacy declarations.
Without one, only an unambiguous root `project.godot`,
`ProjectSettings/ProjectVersion.txt`, or `*.uproject` supplies an inferred family.
Directory names alone are insufficient. Conflicting declarations/markers stop
resolution. Exact directory-entry spelling matters: `assets/` is not `Assets/`,
even on a case-insensitive filesystem.

Conventional source scopes are `src/` for Godot, `Assets/` plus existing
`Packages/` for Unity, and `Source/` plus existing `Plugins/` for Unreal. These
are discovery conventions, not exhaustive engine constraints. Inspect the
project's manifests, story paths and layout for scripts, local packages,
plugins, scenes or data elsewhere. Keep source scope separate from content
scope; returned content folders are hints, not proof of complete coverage.
Do not treat Blueprint-only projects as empty because `Source/` is absent.

For an existing custom layout or a narrower requested target, pass each verified
repository-relative file/folder as `code-root --path 'scripts' --path 'other'`.
This selects a scope; it never moves files or establishes engine API readiness.
It cannot override invalid configuration or conflicting engine evidence. Paths
outside the bound root, secret paths, missing explicit paths and symlink paths
are rejected. Before a recursive scan, identify nested links and generated or
third-party folders; do not traverse links or silently drop coverage. Report
exclusions, files actually checked and remaining unassessed scope.

When `resolution` is `unresolved`, or `status` is `invalid`, leave dependent
checks **NOT ASSESSED** with the reason. Continue independent orientation or
setup questions. Never default to `src/`, claim zero findings, infer a fresh
project, or mark a gate clean from an unscanned scope. Even a resolved but empty
directory needs an actual scan and a scoped report; it is not runtime proof.

Before source writes, read `source-code.md` and the discipline-specific rule for
the code's responsibility, irrespective of its directory name. Keep approved
custom paths and engine-native test locations; do not create `src/` or relocate
tests to match a generic example. Apply the existing approval and engine checks.

## Performance

Use the four resolved budgets in profiler, polish and phase-gate reports. Unset
is not zero or a default target. Separate measured values (with command/tool,
build/ref, hardware, scenario, metric and report/capture path) from code-based
estimates. Estimates guide investigation only and have no passing budget status.
Missing or inapplicable measurements are NOT ASSESSED/N/A with their reasons.
An applicable older report is explicitly file-reported historical evidence.

For optional budget enforcement, `warn` reports measured breaches as concerns;
`block` makes a breach or required unassessed measurement block its gate; `off`
keeps budget comparison informational. Unset preserves the existing skill's
enforcement. None of these values waives a performance acceptance criterion,
erases a known failure, changes a budget or authorizes an optimization.

## Approved setup updates

Ordinary `$settings` assignments remain previews. For an already authorized
engine/test setup workflow, present one exact changeset before writing:

1. Resolve the current values and their sources. Use `write_targets` for mapped
   fields: an allowed explicit local override belongs to that local scalar;
   otherwise a non-null project YAML value belongs to its scalar, and the
   named legacy section/field is the fallback target. An absent target is a new explicit
   configuration decision, never automatic YAML creation.
2. Include every actual pin/reference/runner file that setup must change, plus
   any affected custom routing. An engine version is not changed by editing a
   declaration alone. Preserve unrelated fields, comments and project choices.
3. Show the full diff and ask "May I write this to [exact paths]?" Re-read sources
   before the edit; changed inputs require a fresh preview/approval.
4. After the approved write, re-resolve and read back all affected files. Report
   configuration agreement separately from unrun engine, import, build, test and
   platform checks. Never claim setup complete from a config write alone.

Legacy shadows remain visible. Do not maintain hidden duplicate authorities or
use migration to erase custom prose. The separate migration transaction may stage
only the literal mappings shown in its approved preview; it keeps existing YAML
byte-for-byte and never starts consumers.
