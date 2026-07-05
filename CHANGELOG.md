# Changelog

## v0.3.1 - 2026-07-05

- Added low-friction CCGS decision-prompt rules so next-step handoffs list real
  viable options, mark one recommendation, and use short numbered or `a. yes` /
  `b. no` responses when Codex has no clickable choice UI.
- Updated `$studio-next` to rank viable next actions instead of collapsing most
  situations to a single next step, while keeping mandatory gates as go/no-go
  prompts.
- Kept generated `.gitignore` allowlists from blanket-reignoring shared project
  content roots such as `design/`, `docs/`, `production/`, and `src/`, with
  validation coverage for trackability.

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
- Added an explicit `./.codex/release.sh publish` command for manual GitHub
  Release creation with clean-worktree, authenticated `gh`, `origin/main`,
  changelog, and tag-target checks.
- Made publish check for new commits against the actual previous release tag
  ref instead of relying on GitHub Release branch metadata.
- Made publish pass the `origin` repository explicitly to GitHub release calls
  instead of relying on `gh` repository auto-detection.
- Switched Codex package publishing and release validation to namespaced
  `codex-vX.Y.Z` tags while keeping the legacy `v0.1.0` baseline accepted and
  ignoring inherited upstream Claude release tags.

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
