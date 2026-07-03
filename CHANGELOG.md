# Changelog

## v0.2.0 - 2026-07-04

- Added `.codex/VERSION` as the CCGS package version source of truth.
- Added manual release tooling with `current`, `bump`, and `check` commands.
- Added schema-2 install state with package version, commit, patch mode, file
  hashes, and marker-block hashes.
- Added patch-aware installs with default full installs for fresh or old-state
  targets and incremental patching for modern install state.
- Added release validation to `.codex/audit.sh release` and GitHub Actions.

## v0.1.0 - 2026-07-03

Initial Codex Game Studios public fork release.

- Ported the Claude Code Game Studios role-agent and workflow-skill structure to
  Codex-native agents, skills, hooks, command rules, and startup instructions.
- Added install, uninstall, coexistence, and validation support for target game
  repositories.
- Preserved upstream MIT attribution and added an installed license copy at
  `.codex/docs/UPSTREAM-LICENSE.md`.
- Kept detailed conversion evidence under `docs/codex-conversion/` while moving
  release-facing usage docs to the root README and `.codex/docs/`.
