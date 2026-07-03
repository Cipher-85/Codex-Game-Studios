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

Use `--dry-run` first when the target has existing runtime files:

```bash
./.codex/install.sh --dry-run /path/to/game-project
```

The installer backs up replaced Codex-owned files under `.codex/backups/` and
records target-local ownership state in `.codex/manifest/install-state.json`.

## Verify After Upgrade

Run from the upgraded project:

```bash
python3 .codex/lib/validate_manifest.py --root "$PWD"
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
