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
- The package version is `v0.6.0`.
- `v0.6.0` adds verified CLI/desktop custom-role activation guidance, raw
  parent/child/hook evidence validation, V2 no-fork enforcement, and
  remote-aware fail-closed release checks.
- `v0.5.0` adds strict `.env*` protection, fail-closed manifest ownership and
  installer transactions, backward-compatible uninstall parsing, Codex-native
  skill QA, and documented path-rule enforcement limitations.
- `v0.4.7` hardens resume lane selection, validates Codex-native optional
  `gen-asset` cores and ACTIVE/STUB profiles, and keeps that project-local skill
  trackable without adding it to package ownership.
- Release validation rejects stale package-version summaries in the root and
  runtime README files.
- `v0.4.6` restored the in-session two-round `$handoff` review gate without
  nested CLI, subagent-review, companion, or external-model fallbacks.
- `v0.2.0` added release versioning, release validation, schema-2 install
  state, and default patch-aware installs.
- `v0.3.0` documents the latest root workflow alignment and the hook parser fix
  for current Codex `apply_patch` JSON payloads and legacy raw patch payloads.
- Release validation compares against origin's `codex-vX.Y.Z` tags through a
  read-only remote query, plus the legacy `v0.1.0` initial Codex-port baseline,
  not stale local refs or upstream Claude release tags inherited through the
  pinned source history.

Coexistence rules:
- Do not write to `.claude/`.
- Do not require or modify `CLAUDE.md`.
- Keep neutral game project state such as `production/`, `design/`, `docs/architecture/`, `docs/engine-reference/`, `src/`, `tests/`, and `prototypes/` shared.
- Keep optional `.agents/skills/gen-asset/**` content project-owned; the
  installer only makes that subtree trackable and never adds it to the package
  manifest.
- The default permission profile denies all access to root and nested `.env*`
  files. Non-secret templates that Codex should edit must use a different name,
  such as `config.example`.

Install and release notes:
- Fresh targets receive a full install. Existing targets without ownership state
  still fail closed on collisions.
- Valid schema-v2 install state receives incremental patching by default;
  invalid, unsafe, or stale state aborts before mutation.
- Full patch mode can be forced with `install.sh --patch full`.
- Incremental patch mode can be forced with `install.sh --patch incremental`.
- Install preflights every manifest path and aborts before mutation on unowned
  collisions or locally modified package-owned paths. `--replace-modified`
  permits backup-first replacement only when modern install state proves
  package ownership.
- Uninstall requires valid install state and never infers ownership from file
  contents when state is missing or stale.
- Installer success is static package verification, not proof that project
  trust, hooks, rules, or config are active in the current Codex session.
- Standalone custom-agent files are validated as supported Codex profiles, but
  an exact role name, task path, nickname, or child self-identification is not
  accepted as activation proof. Codex `0.144.x` Sol parents select MultiAgent
  V2 and may hide the custom-role selector; use the verified `gpt-5.5` V1
  fallback or a separately verified user-level V2 workaround. V2 custom roles
  require `fork_turns: "none"`, and results remain blocked unless role metadata,
  instructions, model, and reasoning effort all match the selected profile.
- `audit.sh smoke-interactive` reports `skipped`; trusted model-running evidence
  must be recorded separately or supplied with `--evidence`; task-path-only or
  default-role evidence fails closed.
- `audit.sh release` validates `.codex/VERSION`, `CHANGELOG.md`, release tags,
  and changed installable files without mutating the checkout.
- Package publishing is `bump -> edit changelog/docs -> check -> commit/push ->
  publish`. The `bump` command never publishes, and GitHub Actions remain
  validation-only.
- Publish checks for new commits against the actual previous release tag ref,
  avoiding branch-shaped GitHub Release metadata such as `targetCommitish:
  main`.
- Publish targets the GitHub repository configured as `origin` explicitly, so
  an inherited `upstream` remote cannot receive release API calls.

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
- Per-agent Bash fences, per-skill model routing, `maxTurns`, and automatic
  worktree isolation have no exact verified Codex equivalents. The port uses
  instructions, rules, hooks, session model selection, and explicit worktree
  workflows and labels those mappings partial.
