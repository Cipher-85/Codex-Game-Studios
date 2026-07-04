# Codex-Native Claude Code Game Studios

This directory contains the Codex-owned runtime, validation, release, and
manifest assets for the Codex-native port of
`Donchitos/Claude-Code-Game-Studios` pinned at upstream commit
`984023ddac0d5e27624f2baacde6105e45de375f`.

Current package version:
- `.codex/VERSION` is the source of truth.
- `install.sh` reads the version and records it in target install state.
- `release.sh` is the manual maintainer workflow for current, bump, check, and
  explicit publish operations.

Current status:
- The package version is `v0.3.0`.
- `v0.2.0` added release versioning, release validation, schema-2 install
  state, and default patch-aware installs.
- `v0.3.0` documents the latest root workflow alignment and the hook parser fix
  for current Codex `apply_patch` JSON payloads and legacy raw patch payloads.
- Release validation compares against `codex-vX.Y.Z` tags, plus the legacy
  `v0.1.0` initial Codex-port baseline, not upstream Claude release tags
  inherited through the pinned source history.

Coexistence rules:
- Do not write to `.claude/`.
- Do not require or modify `CLAUDE.md`.
- Keep neutral game project state such as `production/`, `design/`, `docs/architecture/`, `docs/engine-reference/`, `src/`, `tests/`, and `prototypes/` shared.

Install and release notes:
- Fresh targets and old install-state schemas receive a full install.
- Targets with modern install state receive incremental patching by default.
- Full patch mode can be forced with `install.sh --patch full`.
- Incremental patch mode can be forced with `install.sh --patch incremental`.
- `audit.sh release` validates `.codex/VERSION`, `CHANGELOG.md`, release tags,
  and changed installable files without mutating the checkout.
- Package publishing is `bump -> edit changelog/docs -> check -> commit/push ->
  publish`. The `bump` command never publishes, and GitHub Actions remain
  validation-only.
- Publish checks for new commits against the actual previous release tag ref,
  avoiding branch-shaped GitHub Release metadata such as `targetCommitish:
  main`.

Port status notes:
- `.codex/manifest/upstream-assets.json` is the durable upstream inventory for all 417 pinned upstream files.
- `.codex/manifest/expected-targets.json` records the generated Codex targets used by the validators.
- `.claude/hooks/notify.sh` is intentionally replaced by documentation for native Codex notification settings instead of being installed as a project hook.
- Root `AGENTS.md` is now the hot-path startup contract and points Codex to
  `.codex/agents/*.toml` for role registration, path rules under
  `.codex/instructions/path-rules/`, and continuity docs under `.codex/docs/`.
- Hook payload parsing is centralized in `.codex/lib/hooks.sh` and tested with
  current and legacy `apply_patch` fixtures so hooks can inspect changed paths
  without depending on a single payload shape.
- The upstream testing framework was missing a `vertical-slice` skill spec. This port now includes a Codex-added spec while preserving the upstream inventory as historical evidence of the inherited gap.
- Codex currently supports `[tui].status_line` built-in footer items here, but no documented project custom footer command for rendering `Stage:` directly in the footer has been verified. Stage/review/session breadcrumbs are preserved through `studio-status-on-start.sh` and `$studio-status` until Codex exposes a real custom footer item.
