# Upgrading Codex Game Studios

Use this guide when replacing an installed Codex Game Studios runtime in a game
project or updating this distribution repository.

## Before You Upgrade

1. Review `CHANGELOG.md` for behavior changes.
2. Commit or stash user-owned game project work.
3. Confirm whether the target project also has legacy Claude Game Studios files.
   Codex Game Studios must not edit `.claude/**` or legacy Claude instruction
   files.

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
./.codex/audit.sh release --root "$PWD"
./.codex/audit.sh all --root "$PWD"
```

If verification is blocked, keep the exact failing command and output with the
upgrade notes.

Installer success is static evidence only. Trust the upgraded project and start
a new Codex session before verifying hooks, rules, permissions, and agents.

## Compatibility Notes

- Repo-local Codex files are the active runtime.
- `.claude/**` and legacy Claude instruction files are preserved but not used by
  this port.
- Project-specific stage, review mode, and active session state remain in
  neutral shared paths under `production/`.
- Hooks expect Python for reliable payload parsing; without Python they fail
  open with warnings, as described in `.codex/docs/setup-requirements.md`.
