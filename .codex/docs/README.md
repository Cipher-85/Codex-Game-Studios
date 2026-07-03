# Codex Game Studios

This is the Codex-native port of Claude Code Game Studios.

Use repo-local skills by their upstream names, for example `$start`, `$prototype`, and `$gate-check`. Custom role agents keep upstream names such as `producer`, `writer`, and `game-designer`.

Core commands:

```bash
./.codex/audit.sh all --root "$PWD"
./.codex/audit.sh smoke-headless --root "$PWD"
./.codex/install.sh /path/to/game-project
./.codex/uninstall.sh /path/to/game-project
```

Use `./.codex/install.sh "$PWD"` inside an installed project as an idempotent
presence check. Add `--dry-run` to install or uninstall commands to preview
changes, including detected mode, Claude guardrail signals, shared CCGS
signatures, preserved shared paths, and Codex-created shared paths. Installs
write target-local state to `.codex/manifest/install-state.json` so uninstall
can distinguish Codex-created shared scaffolds from preexisting Claude CCGS
assets.
When a target repo already has `.gitignore`, install maintains a marker-managed
allowlist for the deployed paths and verifies they are not still ignored.

Existing `AGENTS.md` content stays first, with the CCGS marker block appended
after it. If a project has only a legacy Claude guardrail file, install creates
`AGENTS.md` with a sanitized migrated project-instructions block first and CCGS
appended after it; uninstall removes that generated file when no user-owned
content remains. The original legacy guardrail files and hidden Claude runtime
directory are preserved even when their text is migrated into `AGENTS.md`.

Notifications: the upstream notification hook is not installed as a Codex project hook. Users can configure native Codex notifications in user-level settings with `notify`, `[tui].notifications`, `[tui].notification_method`, and `[tui].notification_condition`.

Optional plugin packaging is future work. This repo uses loose project-local Codex files as the base distribution.

Path-scoped authoring instructions live in
`.codex/instructions/path-rules/*.md`; root `AGENTS.md` routes Codex to the
right file before work starts. `.codex/rules/*.rules` remains command-policy
only.
