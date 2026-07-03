# Codex-Native Claude Code Game Studios

This directory contains the Codex-owned runtime, validation, and manifest assets for the Codex-native port of `Donchitos/Claude-Code-Game-Studios` pinned at upstream commit `984023ddac0d5e27624f2baacde6105e45de375f`.

Coexistence rules:
- Do not write to `.claude/`.
- Do not require or modify `CLAUDE.md`.
- Keep neutral game project state such as `production/`, `design/`, `docs/architecture/`, `docs/engine-reference/`, `src/`, `tests/`, and `prototypes/` shared.

Phase 1 notes:
- `.codex/manifest/upstream-assets.json` is the durable upstream inventory for all 417 pinned upstream files.
- `.codex/manifest/expected-targets.json` records the generated Codex targets used by the validators.
- `.claude/hooks/notify.sh` is intentionally replaced by documentation for native Codex notification settings instead of being installed as a project hook.
- The upstream testing framework was missing a `vertical-slice` skill spec. This port now includes a Codex-added spec while preserving the upstream inventory as historical evidence of the inherited gap.
- Codex currently supports `[tui].status_line` built-in footer items here, but no documented project custom footer command for rendering `Stage:` directly in the footer has been verified. Stage/review/session breadcrumbs are preserved through `studio-status-on-start.sh` and `$studio-status` until Codex exposes a real custom footer item.
