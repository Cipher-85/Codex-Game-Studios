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

- Targets without `.codex/manifest/install-state.json` receive a full install.
- Targets with old install-state schema receive a full patch and then get a
  modern state file.
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

The installer backs up replaced Codex-owned files under `.codex/backups/` and
records target-local ownership state, package version, package commit, patch
mode, file hashes, and marker-block hashes in
`.codex/manifest/install-state.json`.

## Upgrade This Distribution

Package versioning is manual and lives in `.codex/VERSION`.

```bash
./.codex/release.sh current
./.codex/release.sh bump patch
./.codex/release.sh check
```

CI verifies release consistency on push and pull request. It does not bump the
version, edit `CHANGELOG.md`, create commits, or create tags.

## Verify After Upgrade

Run from the upgraded project:

```bash
python3 .codex/lib/validate_manifest.py --root "$PWD"
./.codex/audit.sh release --root "$PWD"
./.codex/audit.sh all --root "$PWD"
```

If verification is blocked, keep the exact failing command and output with the
upgrade notes.

## Compatibility Notes

- Repo-local Codex files are the active runtime.
- `.claude/**` and legacy Claude instruction files are preserved but not used by
  this port.
- Project-specific stage, review mode, and active session state remain in
  neutral shared paths under `production/`.
