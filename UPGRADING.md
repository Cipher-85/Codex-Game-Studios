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

### Upgrading to v0.7.4

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
