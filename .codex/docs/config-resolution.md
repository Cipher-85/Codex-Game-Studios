# Configuration Foundation

Phase 4C connects review, workflow, density, story granularity, stage, QA, team
and technical consumers. `operational_keys` names supported fields. Explicit
rigor supplies its six linked knobs; automation settings remain candidates. No rigor is inferred for an existing project.

`resolve`/`preview` are inspections. Their `activation: preview-only` and
`applied: false` mean this command ran no workflow, not that all YAML is inert.
The separate approved staging transaction is described in
[config-migration.md](config-migration.md).

## Read and preview

Run these commands from the bound Git root, or use the helper's absolute path
from any directory. The default project root is derived from the installed
helper's location, never from the current working directory. `--root` selects an
explicit project/fixture; put it before the subcommand.

```bash
python3 .codex/lib/project_config.py resolve
python3 .codex/lib/project_config.py resolve --key modes.review_mode
python3 .codex/lib/project_config.py resolve --system combat
python3 .codex/lib/project_config.py schema
python3 .codex/lib/project_config.py preview --set modes.rigor=full
python3 .codex/lib/project_config.py preview --local --set modes.review_mode=full
```

`resolve` reports candidate values with provenance. `schema` reports the exact
supported fields, types, enums, local whitelist, and rigor expansion.
`preview` resolves proposed assignments in memory and reports all resulting
value/source changes, including changes to rigor-derived knobs. It also names
project values shadowed by local overrides. Pass each assignment as one safely
quoted argument; never interpolate a supplied value as shell code.

The resolver has no `set`, `apply`, migration, or write command. Its commands
never create YAML, update legacy mirrors, change hooks, or record derived values.
Exit 0 means a valid candidate/preview, not a passing workflow. Exit 2 means
invalid input/configuration; `settings` is empty and `errors` names the problem.
Never use terminal defaults as a substitute after that error.

## Operational review routing

Run `python3 .codex/lib/project_config.py review-mode`, adding
`--review full|lean|solo` only when the invocation supplied that flag. Use the
installed absolute helper path and `--root <bound-root>` when outside the root.
JSON reports `status`, `value`, `source`, `configured`, `operational_keys`,
`activation: review-mode-only` and `applied: false`. No gate or workflow executes.
`--format text` is for the read-only status hook and emits `value (source)`.

The helper validates all inputs first, then selects:

`--review` → local YAML → project YAML → `production/review-mode.txt` →
explicit rigor expansion → `lean`.

A flag is applied after local/project resolution and never persisted; it is not
an assignment preview. Any invalid input, including an unrelated malformed
setting or locked local field, returns exit 2 with no mode/source, even with a
valid flag. Text errors emit `INVALID` and diagnostics on stderr. Missing tooling
is NOT ASSESSED at the caller. Gate routing stops on both states; neither may
substitute a mode or a hand-written fallback chain. The observational startup
hook displays the diagnostic while leaving the session available for repair.

`configured` is false only for the validated default. Onboarding and new-sprint
setup preserve configured values from YAML, legacy, rigor or run flags. When
unconfigured, they may show a proposed single-line legacy value and ask for
approval to write `production/review-mode.txt`; they then re-resolve. Assignment
writes to YAML remain deferred. Declining initialization leaves the validated
`lean` default in effect. See [director-gates.md](director-gates.md) for filtering
and the independent `$design-review --depth` behavior.

## Resolution and compatibility

For each supported field, use the first non-null value:

1. `project.local.yaml`, for fields on the local whitelist.
2. `project.yaml`.
3. Legacy fields: review mode from `production/review-mode.txt`, stage from
   `production/stage.txt`, and engine/language from
   `.codex/docs/technical-preferences.md`.
4. The explicitly configured `modes.rigor` expansion, for its six knobs.
5. Compatibility defaults: review `lean`, automation `collaborative`, and the
   existing scope/deletion/schema approval categories. Other values stay unset.

Absent `modes.rigor` never implies `standard` or `minimal`. The template recommends
`standard` for a new project; an existing project's policies require a preservation
review. An explicit or legacy review setting wins over the rigor expansion.
An explicit knob changes only that knob. A named system's
`workflow_overrides.system_overrides.<system>` replaces the effective workflow
tier only for that system; it is project-wide configuration, not a local override.

The expansion implemented in the helper is:

| Rigor | Workflow | Density | QA | Story granularity | Review | Team |
|-------|----------|---------|----|-------------------|--------|------|
| minimal | minimal | terse | minimal | coarse | solo | individual |
| standard | standard | balanced | standard | balanced | lean | individual |
| full | full | thorough | full | fine | full | studio |

`testing.strict.<type>` resolves each of logic, integration, visual, UI and
config independently. A project-level boolean `testing.strict` supplies types
without an explicit per-type value. Unset is null, never false. These resolved
values cannot waive a required acceptance check or change Phase 1's evidence
rules. QA consumers use `qa-policy.md` while preserving the existing evidence floor.
Workflow changes document requirements, not mandatory evidence.

The legacy Engine line is preserved verbatim as `engine.name` when needed. If it
contains a version, the resolver does not guess a separate version or edit pins.
`engine.version` remains unset until explicitly supplied. Forbidden patterns,
specialist routing, custom testing policies and other technical-preference prose
remain authoritative and unmigrated. Reading a few structured fields is not a
complete migration of that document.

## Supported schema and syntax

`schema_version: 1` is required in `project.yaml`. The local file may repeat it
and requires a valid base. The helper's `schema` command is the field registry;
unsupported keys are errors rather than silently inert settings. This foundation
covers project identity/stage, engine identity, rigor and its knobs, automation
preferences, testing policy, platform targets/input support, and performance
budgets. Further upstream settings need explicit schema/consumer work.

Python's standard library parses a deliberately restricted, data-only YAML
subset: indented mappings, scalar block lists, flat inline lists, quoted or
plain strings, decimal integers/numbers, lowercase true/false, and null/`~`.
Empty mapping values are unset. Quote versions, numeric-looking strings, and
strings with structural punctuation. Double-quoted strings use JSON escapes;
single quotes escape an apostrophe by doubling it. UTF-8 BOM, CRLF, and consistent
non-two-space indentation are accepted. Comments outside quoted values are
ignored. Metadata dates are strings, not implicitly typed dates.

This is not a general YAML implementation. It rejects duplicate leaves/blocks,
tab indentation, multiline scalars, anchors/aliases/tags, flow mappings, nested
flow collections, mixed mappings/lists, multiple documents, malformed quoting,
unknown keys, wrong shapes/types, unsupported schema versions, and invalid enums.
It does not merge repeated blocks, take a last duplicate value, or fall back from
an invalid value to a less strict one. Symlink inputs and files over 128 KiB are
rejected. Inputs are limited to 16 nested levels and 100-digit integer literals;
non-finite numbers and NUL bytes are invalid. Errors name the file/line for syntax problems and the field for schema
problems. An empty existing YAML file is invalid, distinct from an absent file.

Local overrides are limited to review mode, automation preferences, approval
categories, team size, the five per-type strictness flags, and performance
enforcement (`warn`, `block`, `off`). `schema` exposes the same whitelist used for reads and previews.
Locked keys are errors even when hand-written. Rigor, workflow, documentation
density, story granularity, engine/version, stage and performance budgets belong
to project configuration. Automation preferences never grant file-write,
delegation, publication or design authority; project/user instructions govern.

## Ownership and integration boundary

The package owns the resolver, skill, tests, this contract, and templates under
`.codex/docs/templates/`. Root `project.yaml` and `project.local.yaml` are always
project-owned, never installed from templates, overwritten on upgrade, or removed
on uninstall. An approved migration must preserve legacy files/custom prose and
add local-file ignore handling before activating overrides. Package installation
never copies templates to root or modifies project configuration automatically.
The separate migration helper previews exact changes, requires approval, and
stages mapped fields plus an outside-block ignore rule with backups and rollback.

`$settings` inspects and previews; its explicit migration branch stages only
approved paths. Ordinary assignments remain previews. Director-gate routing,
review status and the project-owned continuity lane module use the shared
`review-mode` contract. Workflow consumers follow `workflow-modes.md`; stage readers use the contract
below. QA/team/technical policy is defined by their shared contracts; automation remains
unconnected and cannot grant authority. Agent Bindery still owns executable continuity and its
reviewer ladder. A resolved candidate or matching content hash is not evidence
that a native workflow, role agent or engine check ran.

## Verification

Run `bash .codex/audit.sh project-config` for executable temporary-fixture tests
of parsing, precedence, operational review routing, preview isolation, root
independence, ownership and templates. The hook audit executes the real review
status hook against YAML/legacy/error fixtures. The runtime audit checks shared
contract bindings; these are static checks, not native skill execution.
`bash .codex/audit.sh all` includes those tests. Installer integration
checks that templates/helpers ship and project-owned YAML survives upgrade and
uninstall. Behavioral specifications describe additional native `$settings`
checks; static assertions are not observed skill invocation evidence.

Adapted from upstream CCGS v1.2.0 configuration semantics at
`05ad7c8a5b8aa2aa86bbd3439ae7cf7295cac418`. Codex uses explicit tool execution;
the upstream shell-preprocessing/permission bootstrap is not a runtime dependency.

## Operational workflow and stage reads

`python3 .codex/lib/project_config.py workflow [--system <GDD-stem>]` returns
`tier`, `source`, `project_tier`, `design_source`, `required_sections`, `formula_requirement`,
`density` and `story_granularity`. `compatibility` is a reported policy for an
unset workflow, not a persisted or inferred tier. Read `workflow-modes.md` for
artifact/section requirements and the independent companion knobs. Gate scans
add `--check-systems`; authoring accepts a future system before its file exists.

`python3 .codex/lib/project_config.py stage [--format text]` returns recorded
`value`, `source`, catalog `phase`, `terminal`, `configured`, `write_target` and
`write_key`. Values accept case-insensitive display names or hyphenated phase
keys for the seven phases and terminal Live. Unknown configured stages are
INVALID; they never trigger inference. Only unset stage may be inferred from
artifacts, explicitly labelled as such. Text output includes provenance.

### Approved stage update

1. Resolve stage immediately before proposing a change. INVALID or unavailable
   tooling stops the update. Keep its source and current contents for comparison.
2. Preview the exact new stage and diff. If an explicit non-null YAML stage owns
   the value, edit only its `project.stage` scalar in `project.yaml`, preserving
   comments and other settings. Otherwise write only `production/stage.txt`.
   Absent/null YAML stage does not require creating or extending YAML.
3. Ask "May I write this to [the exact write_target]?" The user must approve the
   stage value and path. A gate offers this only after actual PASS; initialization
   preserves an existing stage. Successful deployment may propose Live under
   its separately authorized release workflow. No generic settings write occurs.
4. Before editing, compare the source/contents to the preview. If changed,
   re-resolve and obtain approval for the changed diff rather than overwriting it.
5. Re-run `stage` and inspect the actual file. Report success only if the value
   and source match the approved change. Otherwise report the discrepancy and
   stop dependent routing. Declined updates leave the recorded value unchanged.

The resolver writes nothing. It reports `shadowed_legacy` when YAML differs from
an older stage file. That file is historical fallback, not a mirror to update;
show the discrepancy, and do not silently keep two authorities synchronized.
A later YAML removal can expose that older value and needs explicit review.
The observational status hook shows INVALID/NOT ASSESSED without blocking the
session needed to repair it; action workflows stop the affected routing.

## QA, team and technical readers

`project_config.py qa-policy`, `team-policy` and `technical` are read-only.
Read `qa-policy.md`, `team-policy.md` and `technical-config.md` for their usage.
The first two report requested settings and their effective constrained behavior;
none grant action authority. The technical result lists typed values, unmapped
legacy text, pin/config conflicts, field write targets and custom routing.
`engine_ready` means the declared engine/language agrees with its reference pin,
not that an executable/build was verified. `runner_status` remains NOT ASSESSED
until the calling workflow verifies the installed runner independently.

Supported literal legacy fields now include platform/input support, framework,
coverage target and performance budgets. Unsupported prose remains visible and
unmapped; it is never silently interpreted as zero, false or a guessed unit.
Migration can stage only these previewed literal mappings and still preserves
existing YAML byte-for-byte. The helper never edits settings or pin files.

QA level, coverage, strictness, team size, framework, engine identity, platform
fields and performance fields join the previously connected consumers in
`operational_keys`. Automation and other unconnected metadata remain inspectable
candidates. Inspect the schema rather than assuming every accepted key has a
runtime effect. Setup writes retain explicit diff/path approval and readback.
