# Coexistence

Codex Game Studios is designed to coexist with an existing Claude Code Game Studios setup in the same game project.

Rules:

- Do not modify the Claude-owned hidden runtime directory.
- Do not modify the legacy Claude instruction file.
- Keep shared neutral project state in `production/`, `design/`,
  `docs/architecture/`, `docs/engine-reference/`, and `src/`.
- Workflow-created shared folders such as `assets/`, `tests/`, `tools/`, and
  `prototypes/` are created lazily when needed.
- Package ownership is tracked in `.codex/manifest/installed-files.json`.
- Each target install writes `.codex/manifest/install-state.json` with schema
  version, installed CCGS version, package commit, timestamp, patch mode, file
  hashes, marker-block hashes, detected coexistence mode, Claude guardrail
  signals, shared CCGS signatures, shared paths created by Codex, and shared
  paths preserved because they already existed.
- Fresh targets and missing or old install-state schemas use full patch mode.
  Modern install state uses incremental patch mode by default.
- Install backs up changed target files under `.codex/backups/` before replacing
  package-owned assets.
- If the target repo has `.gitignore`, install writes a marker-managed allowlist
  for deployed CCGS paths and verifies those paths are not still ignored. Shared
  project-content roots such as `design/`, `docs/`, `production/`, and `src/`
  are not blanket-reignored by that allowlist, so new project docs and source
  files remain trackable under normal Git rules.
- Existing `AGENTS.md` content stays first, with the CCGS marker block appended
  after it. If a project has only a legacy Claude guardrail file, install creates
  `AGENTS.md` with a sanitized migrated project-instructions block first and
  CCGS appended after it.
- Claude guardrail files are never modified. If their content is migrated into
  `AGENTS.md`, the original `CLAUDE.md`, `claude.md`, and `.claude/**` files are
  preserved byte-for-byte.
- Uninstall removes only package-owned files, CCGS marker blocks, and CCGS
  migration blocks.

Install detects three modes:

- `codex_only`: no Claude guardrail runtime is detected. Install writes the full
  Codex CCGS package, and uninstall removes Codex-installed CCGS assets.
- `claude_present_no_ccgs`: `CLAUDE.md`, `claude.md`, or `.claude/` exists, but
  shared CCGS asset signatures are absent. Install preserves Claude runtime
  files, migrates sanitized guardrail text into `AGENTS.md` when needed, writes
  the full Codex CCGS package, and uninstall removes Codex-installed CCGS
  assets.
- `claude_ccgs_coexist`: Claude guardrails and shared CCGS asset signatures are
  both present. Install preserves preexisting shared visible CCGS assets, writes
  Codex-owned runtime files, and creates only missing shared scaffolds. Uninstall
  removes Codex runtime files and only the shared paths recorded as created by
  Codex. If `install-state.json` is missing, uninstall preserves shared visible
  CCGS assets as the safer fallback.

Patch modes:

- `incremental`: copies only package files whose current source hash differs
  from the hash recorded in modern install state.
- `full`: refreshes every CCGS-owned installable file using the existing
  backup-before-overwrite behavior.

Skill and agent names intentionally preserve upstream names for workflow ergonomics. If another active skill or custom agent has the same name, the audit/installer should report the exact competing path and require a manual decision rather than silently renaming this port.
