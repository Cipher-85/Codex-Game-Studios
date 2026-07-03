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

Partial parity gaps are intentional:

- Scripted footer breadcrumb behavior is represented by `[tui].status_line`, `studio-status-on-start.sh`, and `$studio-status`.
- Structured choice prompts are written as numbered natural-language choices.
- Role delegation is written as Codex subagent delegation by upstream role name.
- Per-agent tool fences, max-turns, and worktree isolation are preserved as explicit instructions and policy checks rather than unsupported TOML fields.
