# Changelog

## v0.3.0 - 2026-07-04

- Aligned root `AGENTS.md` with the upstream workflow contract, including
  authoritative role registration from `.codex/agents/*.toml`, exact
  hyphenated role names, resume and wrap-up routing, collaboration boundaries,
  path-rule routing, verification integrity, and context-management guidance.
- Fixed hook parsing for Codex `apply_patch` payloads by centralizing payload
  extraction in `.codex/lib/hooks.sh`, supporting current JSON argument shapes,
  and retaining a legacy raw-patch fixture for compatibility.
- Updated hook and setup documentation to reflect Python-backed parsing and
  jq's reduced role as an optional debugging aid.
- Updated workflow and conversion docs for PostToolUse `apply_patch` advisory
  timing and current Codex hook matcher behavior.
- Refreshed public status docs for the current package state after the v0.2.0
  release tooling and patch-install work.
- Scoped release validation to Codex-port tags at or after `v0.1.0` so
  inherited upstream Claude release tags do not block Codex package versioning.

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
