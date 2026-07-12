# GLM Plan Review - Phase 2

Phase 2 status: complete.

This review compares `PLAN.md` against the Phase 1 upstream inventory, the pinned upstream clone at `/private/tmp/ccgs-upstream-phase1`, local Codex CLI behavior, and current official Codex documentation.

> Shipped-architecture correction (2026-07-12): recommendations below to use
> nested `AGENTS.md` files predate the implemented root-router architecture.
> Root `AGENTS.md` now routes to `.codex/instructions/path-rules/*.md`; this is
> documented as advisory partial parity because Codex's nested instruction chain
> is selected from the session CWD, not dynamically per edited file.

## Executive Verdict

Verdict: usable with corrections.

The GLM plan has the right high-level intent: preserve behavioral parity, keep Codex assets self-contained, avoid `.claude/` and `CLAUDE.md`, use Codex-native skills/subagents/hooks, and support coexistence. It is not usable as-is. Several upstream counts are wrong, some Codex config details are non-executable, and a few parity claims overstate what Codex can represent directly.

The corrected plan should keep the GLM plan's loose-file coexistence direction, but must replace the incorrect inventory and config mechanics before implementation starts.

## Evidence Used

Saved Phase 1 artifacts:
- `docs/codex-conversion/session-summary.md`
- `docs/codex-conversion/phase-plan.md`
- `docs/codex-conversion/upstream-inventory.md`

Upstream evidence:
- Repository: `https://github.com/Donchitos/Claude-Code-Game-Studios`
- Commit: `984023ddac0d5e27624f2baacde6105e45de375f`
- Local pinned clone: `/private/tmp/ccgs-upstream-phase1`

Local Codex verification:
- `command -v codex` -> `/opt/homebrew/bin/codex`
- `codex --version` -> `codex-cli 0.142.5`
- `codex features list` confirms stable `hooks`, `multi_agent`, `plugins`, `plugin_sharing`, `shell_tool`, `goals`, and `tool_call_mcp_elicitation`.
- `codex debug models` current visible slugs: `gpt-5.5`, `gpt-5.4`, `gpt-5.4-mini`, `gpt-5.3-codex-spark`, `codex-auto-review`.
- `codex plugin list` currently fails because the configured `stillcurrent-local` marketplace points at this workspace, but this workspace has no supported marketplace manifest. Do not rely on the local cached `codex-game-studios` plugin as source of truth.

Official Codex docs checked:
- `https://developers.openai.com/codex/guides/agents-md`
- `https://developers.openai.com/codex/skills`
- `https://developers.openai.com/codex/subagents`
- `https://developers.openai.com/codex/hooks`
- `https://developers.openai.com/codex/permissions`
- `https://developers.openai.com/codex/rules`
- `https://developers.openai.com/codex/plugins`
- `https://developers.openai.com/codex/plugins/build`
- `https://developers.openai.com/codex/cli/slash-commands`
- `https://developers.openai.com/codex/config-reference`

## Codex Mechanisms Verified

`AGENTS.md`:
- Codex reads global and project `AGENTS.md` or `AGENTS.override.md` files, concatenating from project root down to the current working directory.
- Codex skips empty files and stops when `project_doc_max_bytes` is reached, default 32 KiB.
- No documented `@import` support was found. Inline Claude imports or split across nested `AGENTS.md`.

Skills:
- Codex skills are directories with `SKILL.md`; required metadata is `name` and `description`.
- Repo-scoped skills are discovered from `.agents/skills` from the current working directory up to the repo root.
- Skills can be explicitly selected via `/skills` or `$skill-name`, and implicitly by description matching.
- Claude skill metadata fields such as `allowed-tools`, `model`, `argument-hint`, and `user-invocable` are not 1:1 Codex skill metadata.

Subagents:
- Codex has built-in `default`, `worker`, and `explorer` agents.
- Custom agents live as standalone TOML files in `~/.codex/agents/` or project `.codex/agents/`.
- Required custom-agent fields are `name`, `description`, and `developer_instructions`.
- Optional fields include `model`, `model_reasoning_effort`, `sandbox_mode`, `mcp_servers`, and skill config inherited through the normal config mechanism.

Hooks:
- Project and plugin hooks use the same lifecycle event model; command hooks are supported.
- Supported events include `PreToolUse`, `PermissionRequest`, `PostToolUse`, `PreCompact`, `PostCompact`, `SessionStart`, `SubagentStart`, `SubagentStop`, `UserPromptSubmit`, and `Stop`.
- `Notification` is not a Codex lifecycle hook event.
- `PreToolUse` can deny supported tool calls. `PostToolUse` can add warnings/context and stop a hook run, but it is too late to prevent the already-completed file edit.
- Plugin hooks are possible, but they require plugin packaging and hook trust. The port does not need plugins for repo-local coexistence.

Config, permissions, and command rules:
- Project `.codex/` layers only load when the project is trusted.
- Permission profiles are beta and should not be mixed with older `sandbox_mode` settings in the same active config. Use one model consistently.
- Command approval rules are `.rules` files under a `rules/` folder next to an active config layer, for example `.codex/rules/settings.rules`, not `prefix_rules` entries inside `config.toml`.
- Codex "Rules" are command execution approval rules. They are unrelated to upstream `.claude/rules/*.md` path-scoped instruction files.
- Project-scoped config cannot override machine-local provider/auth/notification keys such as `notify`.

Slash commands and questions:
- `/plan`, `/goal`, `/skills`, `/import`, and other built-in slash commands exist.
- No repo-local slash-command mechanism was verified. CCGS workflow entry points should be skills, not custom slash commands.
- No direct Codex equivalent to Claude `AskUserQuestion` was verified. Workflow parity should be natural-language options, Plan-mode questions, or MCP elicitation where a connected MCP tool is deliberately introduced.

## Critical Corrections to the GLM Plan

### Upstream Inventory Corrections

The GLM plan's inventory table is not reliable as written.

Corrections:
- Agents: upstream has 49 agents with model distribution 44 `sonnet`, 3 `opus`, 2 `haiku`. `prototyper` has `model: sonnet` and `isolation: worktree`; it is not a no-model agent.
- Skills: upstream has 73 skills with model distribution 63 `sonnet`, 3 `opus`, 7 `haiku`. The Opus skills are `architecture-review`, `gate-check`, and `review-all-gdds`; `gate-check` is not the only Opus skill.
- `CLAUDE.md`: upstream has 5 files named `CLAUDE.md`: root, `src/`, `design/`, `docs/`, and `CCGS Skill Testing Framework/CLAUDE.md`. The GLM plan's "6" count is wrong and appears to mix templates with files actually named `CLAUDE.md`.
- Templates: upstream has 40 files under `.claude/docs/templates/`, not "36 + 3". There are additional template-like files outside that directory, including `.claude/docs/settings-local-template.md`, `.claude/docs/CLAUDE-local-template.md`, and two framework templates.
- Testing framework: upstream has 49 agent specs and 72 skill specs; the missing skill spec is `vertical-slice`. The framework itself, `catalog.yaml`, `quality-rubric.md`, its templates, and framework `CLAUDE.md` must all be mapped.
- Installed Codex skill count should include 73 ported upstream skills plus only deliberately new Codex-native support skills. `skill-test` already exists upstream and should be ported, not counted as new.

### Incorrect or Overstated Codex Assumptions

`prefix_rules` in `.codex/config.toml`:
- GLM proposes command `prefix_rules` inside `.codex/config.toml`.
- Verified Codex docs place these in `.rules` files under `rules/` next to an active config layer.
- Correction: use `.codex/rules/settings.rules` for command approvals/denies, and `.codex/config.toml` for permission profiles, hooks/config references, model defaults if needed, and approval policy.

Permission profiles plus `sandbox_mode`:
- GLM mixes `[permissions.studio]` with `sandbox_mode = "workspace-write"`.
- Verified Codex docs say permission profiles do not compose with older sandbox settings unless managed policy forces a profile path.
- Correction: use permission profiles as the primary mechanism for Codex 0.142.5: `default_permissions = "game_studios"` plus `[permissions.game_studios] extends = ":workspace"`. Avoid `sandbox_mode` in the distributable config unless a compatibility fallback is explicitly separated.

Codex rules vs upstream rules:
- GLM correctly wants to convert `.claude/rules/*.md` into nested `AGENTS.md`, but it also uses "rules" for command approvals in config.
- Correction: keep two distinct categories:
  - Upstream path-scoped instruction rules -> nested `AGENTS.md`.
  - Codex command approval rules -> `.codex/rules/*.rules`.

Skill-pinned agents:
- GLM says Claude `skills: [...]` maps exactly to `skills.config = [...]`.
- This is overstated. Custom agent TOML can inherit normal config fields, but Codex skill config is not a direct list of skill names equivalent to Claude agent-pinned skills.
- Correction: preserve skill affinity in `developer_instructions`, and only use `skills.config` if Phase 3 verifies the exact schema for enabling/disabling skill paths. Parity should be marked semantic or partial, not exact.

Per-agent tool fences:
- GLM correctly flags no granular "writes allowed, Bash denied" equivalent, but its target wording still implies agent-level sandbox can cover most cases.
- Correction: mark this partial. Use custom-agent instructions, permission profile limits, command rules, and hooks. Do not claim precise parity for Claude `tools` and `disallowedTools`.

Per-skill model pin:
- GLM says skill model pins are satisfied by spawned subagents.
- This is a reasonable substitute for delegation-heavy skills but not exact. Some skills are main-thread workflows and may not spawn a role for every model-sensitive step.
- Correction: mark as semantic/partial and add verification to identify skills whose frontmatter `model` materially changes behavior.

Statusline:
- GLM correctly identifies no scriptable statusline parity, but the plan must not imply `.codex/config.toml` can restore the upstream script. Codex `tui.status_line` is a built-in item list in local config, not a project-specific script hook.
- Correction: configure Codex `[tui].status_line` with supported built-in footer items when safe, then preserve the upstream game-stage/session breadcrumb through `SessionStart` context injection and a `studio-status` skill.

Notification:
- GLM says Codex has no `Notification` hook and proposes dropping or replacing it. This is correct for hooks.
- Correction: do not replace it with project-local `notify`, because official docs say project config cannot override notification keys. If a notification feature is kept, make it user-level optional documentation, not installed runtime behavior.

Plugin packaging:
- GLM chooses repo-local loose files, which matches the coexistence requirement when paired with marker ownership and collision checks. Plugin packaging is verified as possible but not required.
- Correction: do not rely on the local cached `codex-game-studios` plugin. The configured local marketplace currently fails `codex plugin list` because this workspace lacks a supported marketplace manifest. Treat plugins as optional distribution work, not the base port architecture.

### Weak Coexistence Handling

The GLM plan's coexistence goal is right, but the implementation must be stricter:
- No Codex runtime file may reference `.claude/`, `CLAUDE.md`, or Claude slash commands except attribution/provenance docs.
- Install/uninstall must have a manifest and must never remove shared neutral state such as `production/`, `design/`, `docs/architecture/`, or `docs/engine-reference/`.
- Project `.codex/` config only loads after trust. The install flow must include a trust step or a clear "hooks/config inactive until trusted" validation result.
- Existing `AGENTS.md` files in a target project are collision-prone. The installer must not blindly overwrite them; it should merge with markers or refuse unless `--force`/backup is used. Phase 3 must choose the exact strategy.
- A target project may already have `.agents/skills` or `.codex/agents`. The installer needs per-file manifest ownership, not whole-directory ownership.

### Vague or Non-Executable Steps

The GLM implementation phases are directionally useful but not yet executable:
- "Generate 49 agents" lacks the exact conversion schema for each frontmatter field and the exact validation command for TOML parsing.
- "Generate 73 skills" does not enumerate the rewrite rules that must be verified per skill, especially `Task`, `AskUserQuestion`, `/skill` references, `.claude` paths, model frontmatter, and allowed tools.
- "Copy 36+3 templates" is wrong and would miss upstream templates.
- "Audit inventory" must use a committed manifest, not live `/tmp`, because `/tmp` is not durable.
- "Smoke workflows via Codex non-interactive" may require hook trust and interaction handling. It must separate headless static checks from interactive/manual smoke tests.

### Missing Tests

Add or strengthen tests for:
- Inventory completeness against a committed upstream manifest.
- Zero `.claude/`, `CLAUDE.md`, and Claude slash-command references in Codex runtime files.
- `.codex/config.toml` strict parsing and no mixed permission/sandbox model.
- `.codex/rules/*.rules` parsing and inline `match`/`not_match` examples for all command policies.
- Hooks JSON schema, supported event names, command existence, and trust documentation.
- Skill metadata validity with only Codex-supported required metadata.
- Agent TOML validity with exact custom-agent required fields.
- Installer collision behavior for existing `AGENTS.md`, `.agents/skills`, `.codex/agents`, `.codex/hooks.json`, and `.codex/rules`.
- Coexistence fixture with a preexisting `.claude/` and `CLAUDE.md` hashed before/after install and uninstall.
- Testing framework coverage, including the known missing upstream `vertical-slice` spec.

## Corrections to Carry into Phase 3

1. Use the Phase 1 inventory as the upstream baseline, not the GLM counts.
2. Make `docs/codex-conversion/codex-mapping-matrix.md` authoritative and expand it to every upstream file/category.
3. Use permission profiles and `.codex/rules/*.rules`; do not mix profiles with `sandbox_mode`.
4. Count target skills as 73 ported plus only deliberately new Codex-native skills.
5. Treat plugin packaging as optional. The default target should remain repo-local loose files for coexistence.
6. Require an installer ownership manifest and collision policy for preexisting Codex files.
7. Add a committed upstream manifest in the eventual implementation plan so validation does not depend on `/tmp`.

## Phase 2 Open Items for Later Phases

These are not blockers for Phase 2, but Phase 3-5 must resolve them:
- Exact installer strategy for preexisting `AGENTS.md`: marker-managed merge, refusal, or backup-and-write.
- Exact per-agent conversion schema for Claude `tools`, `disallowedTools`, `memory`, `skills`, `maxTurns`, and `isolation`.
- Whether to introduce MCP elicitation for structured choices, or preserve `AskUserQuestion` as natural-language option lists only.
- Whether the distributable should include an optional plugin package in addition to loose files.
- Exact target location for the `CCGS Skill Testing Framework` assets.
