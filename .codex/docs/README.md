# Codex Game Studios

This is the Codex-native port of Claude Code Game Studios.

Use repo-local skills by their upstream names, for example `$start`, `$prototype`, and `$gate-check`. Custom role agents keep upstream names such as `producer`, `writer`, and `game-designer`.

Core commands:

```bash
./.codex/audit.sh all --root "$PWD"
./.codex/audit.sh smoke-headless --root "$PWD"
./.codex/audit.sh release --root "$PWD"
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
Existing modern installs receive incremental patching by default. Use
`--patch full` or `--patch incremental` when the patch mode needs to be
explicit.
When a target repo already has `.gitignore`, install maintains a marker-managed
allowlist for the deployed paths and verifies they are not still ignored. Shared
project-content roots such as `design/`, `docs/`, `production/`, and `src/`
are not blanket-reignored by that allowlist, so new project docs and source
files remain trackable under normal Git rules.

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

Latest runtime notes:

- `.codex/VERSION` is the release source of truth; release tooling validates
  metadata and changed installable files without mutating the checkout.
- Codex package releases use `codex-vX.Y.Z` git tags. The legacy `v0.1.0` tag
  is accepted only as the initial Codex-port baseline, so inherited upstream
  Claude tags such as plain `v0.2.0` and `v0.3.0` do not force this port's
  package version.
- Release publishing is manual through `./.codex/release.sh publish`; GitHub
  Actions validate release metadata only and do not publish.
- `apply_patch` hooks use the shared parser in `.codex/lib/hooks.sh`, which
  accepts current JSON-argument payloads and legacy raw patch payloads.
- Root `AGENTS.md` is aligned with the upstream workflow contract while keeping
  Claude runtime files out of Codex dependencies.
