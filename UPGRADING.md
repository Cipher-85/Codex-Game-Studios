# Upgrading Codex Game Studios

Use this guide when replacing an installed Codex Game Studios runtime in a game
project or updating this distribution repository.

## Before You Upgrade

1. Review the distribution's `CHANGELOG.md` for behavior changes.
2. Commit or stash user-owned game project work.
3. Confirm whether the target project also has legacy Claude Game Studios files.
   Codex Game Studios must not edit `.claude/**` or legacy Claude instruction
   files.
4. Confirm Agent Bindery has deployed the global `handoff`,
   `resume-from-handoff`, and `handoff-reviewer` assets if the project uses
   session continuity. CCGS no longer ships repo-local copies of that pair.

## Upgrade an Installed Project

From this repository, run:

```bash
./.codex/install.sh /path/to/game-project
```

Default upgrade behavior is patch-aware:

- Fresh targets without `.codex/manifest/install-state.json` receive a full
  install. Brownfield targets without state still fail closed on collisions.
- Targets with invalid, unsafe, or stale install state abort before mutation;
  restore valid schema-v2 state from backup or resolve ownership manually.
- Targets with modern install state receive an incremental patch based on the
  package file hashes recorded at the last install.

Use `--dry-run` first when the target has existing runtime files:

```bash
./.codex/install.sh --dry-run /path/to/game-project
```

Force a patch mode when needed:

```bash
./.codex/install.sh --patch incremental /path/to/game-project
./.codex/install.sh --patch full /path/to/game-project
```

Upgrades fail closed when a package-owned path was modified locally. Review the
dry-run, then opt into backup-first replacement only for paths proven by modern
install state:

```bash
./.codex/install.sh --dry-run --replace-modified /path/to/game-project
./.codex/install.sh --replace-modified /path/to/game-project
```

Pre-existing shared paths without package ownership state are never overwritten
by this option. Merge those files manually, then rerun the ordinary dry-run.

The installer backs up replaced Codex-owned files under `.codex/backups/` and
records target-local ownership state, package version, package commit, patch
mode, explicit package-owned paths, file hashes, preserved shared paths, and
marker-block hashes in
`.codex/manifest/install-state.json`.

Upgrading from `v0.7.1` removes the two former repo-local continuity skills and
their obsolete contract fixtures only when modern install state proves CCGS
owns their unchanged paths. Modified or unowned copies still fail closed. The
upgrade then installs
`.agent-continuity.toml` and `production/handoff/*.md`; it does not install or
modify Agent Bindery's global skills.

### The v0.7.4 package line

Game projects now receive `.github/workflows/ccgs-runtime-check.yml`, which
runs the runtime audit without requiring CCGS release tags or a package
changelog. The distribution's `.github/workflows/release-check.yml` is no
longer installed.

An old release workflow is retired only when valid install state proves
ownership and the file matches its recorded hash. If an owned copy was edited,
upgrade stops before mutation, even with `--replace-modified`. Review and move
project-specific jobs into a project-owned workflow, then remove or restore
the retired package file before retrying. An unowned workflow is preserved.
Dry-run reports removal of an unchanged owned workflow. Rollback restores it
if a later installation step fails.

Uninstall now backs up complete instruction files before removing managed or
migrated blocks. It prints the unique `.codex/backups/<timestamp>.<suffix>/`
location. A failed backup prevents removal of that instruction file, retains
install state, and returns failure. Dry-run previews the backup without writing.

Fresh installs start with unconfigured engine, language, and specialist
preferences. Existing customized settings still follow the ordinary modified
package-file conflict rules above; this patch does not migrate them to project
ownership.

## Upgrade This Distribution

Package versioning is manual and lives in `.codex/VERSION`.

```bash
./.codex/release.sh current
./.codex/release.sh bump patch
./.codex/release.sh check
```

CI verifies release consistency on push and pull request. It does not bump the
version, edit `CHANGELOG.md`, create commits, or create tags. Release
validation compares `.codex/VERSION` to Codex-port semver tags at or after
`v0.1.0`; upstream Claude release tags inherited from the pinned source history
are ignored.

Before tagging any release, update the root README, `.codex/README.md`,
`.codex/docs/README.md`, `CHANGELOG.md`, and any shared-path merge notes for the
new version. Release metadata does not merge downstream project-owned changes.

## Selective v1.2.0 adoption

The comparison target is upstream [v1.2.0 at
`05ad7c8a5b8aa2aa86bbd3439ae7cf7295cac418`](https://github.com/Donchitos/Claude-Code-Game-Studios/commit/05ad7c8a5b8aa2aa86bbd3439ae7cf7295cac418),
released on 2026-10-19. Its tree contains 638 files; the original port baseline
contains 417. `.codex/manifest/upstream-assets.json` remains the historical
inventory of `984023ddac0d5e27624f2baacde6105e45de375f`, not a claim that all
638 target files were ported. This working package is `0.7.4`; the selective
changes remain unreleased until an explicitly authorized release completes.

### Adoption matrix

| Upstream area | Disposition in this package |
| --- | --- |
| Test commands, evidence and review freshness | Adapted to Codex, supported runner discovery, required evidence and read-only hash receipts |
| Project configuration and rigor | Adapted with strict parsing, provenance, explicit compatibility and no inferred rigor for existing projects |
| Configuration migration | Separate approved preview/apply/recovery transaction; preserves existing YAML and custom prose |
| Review, workflow, density, stories and stage | Connected consumers; minimal brief path and source-aware single-target stage updates |
| QA, team and technical settings | Connected within shared contracts; strictness preserves evidence, team size changes only optional participation, performance needs measurements |
| Source-root procedure | Adapted to configured/observed engine and explicit custom scope; unknown scope stays unassessed |
| Story/ADR/GDD/bug facts | Read-only shared parser and graph observations; workflow quality and approval decisions stay with the skills |
| Automation and new upstream-only settings | Deferred/unsupported; parsing a candidate never grants action authority |
| Full role-prompt refresh | Deferred; selected prompts were adapted, all 49 model/effort settings are preserved |
| Engine-reference refresh | Deferred; 34 reference files differ upstream, while the package's actual pins/references are preserved |
| `studio-tests/` rename and wholesale template/reference split | Deferred; keep `CCGS Skill Testing Framework/` and current package ownership paths |
| Claude runtime hooks, bootstrap, command permissions and footer | Not imported as runtime dependencies; use Codex surfaces and retain documented capability gaps |
| Executable handoff/resume/rotation | Owned by Agent Bindery; CCGS retains its manifest and project modules |

The 35 new upstream helpers are accounted for below. Adapted/replaced means a
bounded Codex implementation or existing contract, not identical source parity.

| Helpers | Disposition / current implementation |
| --- | --- |
| `story-facts.sh`, `story-status.sh`, `adr-status.sh`, `adr-dep-graph.sh`, `gdd-structure-check.sh`, `bug-stats.sh` | Adapted as `artifact_facts.py`; no count-based readiness, automatic closure or next-story choice |
| `review-receipts.sh` | Adapted as the read-only Codex receipt helper |
| `migrate-v1-config.sh` | Replaced by the guarded `migrate_project_config.py` transaction |
| `yaml-get.awk` | Replaced by the restricted shared configuration parser |
| `config-set.sh` | Inspection/preview adapted through `$settings`; general assignment application remains deferred |
| `set-stage.sh` | Shared stage reader plus approved single-target update/readback; no automatic dual write |
| `project-state.sh`, `project-coherence.sh` | Partial: stage/source-root and configuration/pin observations; broader state inference, live-binary/render/export coherence deferred |
| `hook-input.sh`, `agent-check.sh`, `skill-lint.sh`, `compat-inventory.sh` | Existing Codex parser/validators cover applicable boundaries; broader upstream analyses not ported |
| `review-scope.sh` | Existing content-hash review scope retained; no Git/mtime-based replacement |
| `session-state.sh`, `rotate-session-state.sh` | Executable continuity remains Agent Bindery-owned |
| `read-guard.sh`, `write-guard.sh` | Deferred as upstream helpers; existing Codex permissions/path rules remain authoritative |
| `godot-parse-check.gd`, `test-run.sh`, `test-scaffold.sh` | Deferred; retain existing engine-specific workflow guidance and require native validation |
| `artifact-check.sh`, `asset-scan.sh`, `code-markers.sh`, `content-count.sh`, `debt-register.sh`, `flaky-stats.sh`, `inputs-check.sh`, `md-section.sh`, `plan-math.sh`, `registry.sh` | Deferred; no generic helper suite or additional mutation API introduced |

### Current contracts and acceptance

Use `project_config.py` for `resolve`, `preview`, `review-mode`, `workflow`,
`stage`, `qa-policy`, `team-policy`, `technical` and `code-root`. The authoritative
field registry and `operational_keys` come from `schema`. See
[configuration](.codex/docs/config-resolution.md),
[workflow tiers](.codex/docs/workflow-modes.md), [QA](.codex/docs/qa-policy.md),
[teams](.codex/docs/team-policy.md), [technical/source scope](.codex/docs/technical-config.md)
and [artifact inspection](.codex/docs/artifact-inspection.md).

Package inventory: 76 skills, 49 role profiles, 74 skill behavioral specs, 49 role
specs and 533 installed files. `studio-status` and the deprecated `studio-next`
have no separate skill behavioral specs. The executable helper fixtures are
separate from these native behavior specifications.

The recorded native matrix has **30/30 accepted cases for declared assertions**
across approved October 20-21 runs. This includes actual role loading and the
full/lean/solo routing checks, not just package fixtures. Source-root cases
remain discovery preflights; engine execution, visual/gameplay, performance and
platform acceptance are unassessed. See
[Validation](.codex/docs/VALIDATION.md#native-acceptance-for-the-selective-update)
for retained evidence, expected negative outcomes, scheduling and hook-trust
qualifications. Final package/release/headless/docs audits passed.

The selective integration is local and uncommitted. Version selection,
commit/push, tagging, publication and downstream deployment remain separate
user decisions; none is established by a passing audit or synthetic fixture.

## Optional Configuration Staging

Package installation never runs configuration migration or takes ownership of
root `project.yaml` / `project.local.yaml`. Existing valid YAML affects connected
review, workflow, density, story granularity, stage, QA, team and technical
consumers on subsequent invocations, even without a migration receipt.
Inspect the resolved values and sources before using updated workflows.

`resolve` and `preview` are read-only: `applied: false` does not make existing
YAML inert. `$settings` assignments remain previews, automation settings grant
no authority, and invalid configuration stops the affected workflow. The startup
status hook reports diagnostics without preventing repair. Preserve custom
technical prose, installed runners and actual engine pins.

After installation, `$settings migrate` or the following command provides a
read-only preview of mapped fields, unmapped prose, conflicts, exact changes
and backup/receipt paths:

```bash
python3 .codex/lib/migrate_project_config.py plan
```

Review and explicitly approve the full changeset before running the preview's
`apply --expect-plan <plan_id>` command. Installation approval does not cover
this transaction. The helper creates root YAML only if absent, preserves existing
YAML and legacy files, and adds a project-owned root local-file ignore rule
outside the installer block. It never guesses rigor or executes workflows;
staged operational values are read by subsequent invocations.
Backups and receipts survive upgrade and uninstall. See
[the migration contract](.codex/docs/config-migration.md) for requirements,
stale-plan handling, failure recovery and separately approved rollback.

## Verify After Upgrade

Run from the upgraded project:

```bash
python3 .codex/lib/validate_manifest.py --root "$PWD"
./.codex/audit.sh all --root "$PWD"
```

When updating the distribution itself, also run
`./.codex/audit.sh release --root "$PWD"` and
`./.codex/audit.sh coexistence --root "$PWD" --integration`.

If verification is blocked, keep the exact failing command and output with the
upgrade notes.

Installer success is static evidence only. Trust the upgraded project and start
a new Codex session before verifying hooks, rules, permissions, and agents.

## Compatibility Notes

- Repo-local Codex files are the active runtime.
- The `handoff` and `resume-from-handoff` commands are the global Agent Bindery
  skills configured by the repo-local `.agent-continuity.toml` manifest.
- `.claude/**` and legacy Claude instruction files are preserved but not used by
  this port.
- Project-specific stage, review mode, and active session state remain in
  neutral shared paths under `production/`.
- Hooks expect Python for reliable payload parsing; without Python they fail
  open with warnings, as described in `.codex/docs/setup-requirements.md`.
