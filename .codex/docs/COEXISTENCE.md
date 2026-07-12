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
- The optional `.agents/skills/gen-asset/**` subtree is project-owned. The
  installer allowlists it so its core and profiles are trackable, but it is
  deliberately absent from `installed-files.json`; install and uninstall never
  copy, replace, own, or delete it.
- Each target install writes `.codex/manifest/install-state.json` with schema
  version, installed CCGS version, package commit, timestamp, patch mode, file
  hashes, marker-block hashes, detected coexistence mode, Claude guardrail
  signals, shared CCGS signatures, shared paths created by Codex, and shared
  paths preserved because they already existed.
- Fresh targets use full patch mode. Existing brownfield targets without state
  still fail closed on collisions. Valid schema-v2 state uses incremental patch
  mode by default; invalid, unsafe, or stale state aborts before mutation.
- Install preflights all manifest paths before mutation. Unowned collisions and
  locally modified package-owned files abort by default. After explicit review,
  `--replace-modified` backs up and replaces only paths proven package-owned by
  modern install state; it never adopts an unowned shared path.
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
- Uninstall requires valid schema-v2 state. Missing, stale, malformed,
  path-traversing, or symlinked state fails closed without inferring ownership
  from file contents.
- Obsolete cleanup uses prior install-state ownership and hashes. File contents,
  emptiness, or a `hook_event_name` string are never treated as ownership proof,
  and pruning is limited to empty Codex runtime directories.

For a project that already has Claude-side `gen-asset` profiles, migrate only
after reviewing the target inventory: create the Codex-native core under
`.agents/skills/gen-asset/SKILL.md`, copy project-owned profiles byte-for-byte
from `.claude/skills/gen-asset/profiles/`, and keep the Codex runtime independent
of `.claude/**`. CCGS does not perform this project-specific migration itself.

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
  Codex. If `install-state.json` is missing or invalid, uninstall aborts without
  changing project files.

Patch modes:

- `incremental`: copies only package files whose current source hash differs
  from the hash recorded in modern install state.
- `full`: refreshes every CCGS-owned installable file after the same conflict
  preflight; modified state-owned files still require `--replace-modified`.

After install, trust the target project and start a new Codex session. Static
installation success does not prove that project hooks, rules, or config are
active.

Skill and agent names intentionally preserve upstream names for workflow ergonomics. If another active skill or custom agent has the same name, the audit/installer should report the exact competing path and require a manual decision rather than silently renaming this port.
