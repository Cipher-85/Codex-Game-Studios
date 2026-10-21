# Migration Notes

This port maps upstream workflows to Codex-native surfaces:

- Root startup instructions use an `AGENTS.md` marker block.
- Path-scoped authoring instructions live in
  `.codex/instructions/path-rules/*.md`.
- Skills live under `.agents/skills/<skill>/SKILL.md`.
- Custom agents live under `.codex/agents/<agent>.toml`.
- Agent memory contracts live under `.codex/agent-memory/<agent>/MEMORY.md`.
- Hooks live under `.codex/hooks/*.sh` and are wired by `.codex/hooks.json`.
- Command policy lives in `.codex/rules/settings.rules`.

The original 417-file upstream inventory remains pinned to
`984023ddac0d5e27624f2baacde6105e45de375f`. The selective v1.2.0 update uses
`05ad7c8a5b8aa2aa86bbd3439ae7cf7295cac418` as its comparison target, not a new
full-parity baseline. See [the adoption matrix](../../UPGRADING.md#selective-v120-adoption)
for limits, including retained test-directory layout and deferred reference
refreshes. Runtime model/effort settings and actual engine pins are preserved.

Configuration migration is a separate, explicitly approved transaction; package
installation does not create root game YAML. Connected consumers read existing
valid YAML without a migration receipt. See [config-migration.md](config-migration.md).

The continuity pair is the deliberate exception to repo-local skill ownership.
Agent Bindery supplies the global `handoff`, `resume-from-handoff`, and
`handoff-reviewer` assets. CCGS ships `.agent-continuity.toml` plus the
project-specific modules under `production/handoff/`; do not recreate the two
skills under `.agents/skills/`.

Optional project-local skills are migrated separately from the CCGS package.
For `gen-asset`, place the Codex-native direct-image-generation core at
`.agents/skills/gen-asset/SKILL.md` and copy the project's profile files
byte-for-byte from `.claude/skills/gen-asset/profiles/` only when the project
owner approves that migration. The installed runtime must not read or modify
the Claude-side copy. The `.agents/skills/gen-asset/**` subtree remains outside
`.codex/manifest/installed-files.json`, so CCGS install and uninstall do not own
it.

Partial parity gaps are intentional:

- Built-in footer items are represented by `[tui].status_line`; the upstream scripted Stage/session footer is blocked until Codex exposes a documented project custom footer item, with `studio-status-on-start.sh` and `$studio-status` as startup/on-demand fallbacks.
- Structured choice prompts are written as numbered natural-language choices.
- Role delegation is written as Codex subagent delegation by upstream role name.
- Per-agent tool fences, max-turns, and worktree isolation are preserved as explicit instructions and policy checks rather than unsupported TOML fields.
- Image generation extensions invoke Codex's built-in `image_gen` capability
  directly. Nested `codex exec`, session-ID parsing, CLI/API fallbacks, and
  legacy `.Codex/` skill paths are not part of the Codex-native contract.
