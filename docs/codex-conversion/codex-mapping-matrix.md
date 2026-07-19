# Codex Mapping Matrix

Phase 3 status: complete.

This matrix maps the pinned upstream repository at commit `984023ddac0d5e27624f2baacde6105e45de375f` to the corrected Codex-native architecture. It supersedes the initial Phase 2 matrix.

Verified upstream file coverage ledger: 417 files total.

| Source category | Count | Disposition |
|---|---:|---|
| `.claude/agents/*.md` | 49 | Port to Codex custom agents |
| `.claude/skills/*/SKILL.md` | 73 | Port to Codex repo skills with upstream names |
| `.claude/hooks/*` | 12 | Port 11 lifecycle hooks; replace `notify.sh` behavior with Codex native notification guidance |
| `.claude/rules/*.md` | 11 | Port path-scoped guidance into the root-routed `.codex/instructions/path-rules/` library; keep command policy separate |
| `.claude/docs/templates/**` | 40 | Copy to `.codex/docs/templates/**` |
| `.claude/docs/**` excluding templates | 23 | Copy or rewrite to neutral Codex docs |
| `.claude/settings.json`, `.claude/statusline.sh` | 2 | Replace with Codex config/rules/hooks/native status-line/status skill |
| `.claude/agent-memory/lead-programmer/MEMORY.md` | 1 | Port to repo-local Codex agent memory and bind from custom agent instructions |
| Root files | 7 | Port docs/license where relevant; replace `CLAUDE.md` with `AGENTS.md` block |
| `.github/**` | 5 | Copy as optional distribution/community docs only |
| `CCGS Skill Testing Framework/**` | 127 | Copy to Codex testing framework docs |
| `docs/**` | 62 | Preserve shared neutral docs; route documentation guidance through root `AGENTS.md` to `docs-directory.md` |
| `design/**` | 2 | Preserve shared registry; route design guidance through root `AGENTS.md` to `design-directory.md` |
| `src/**` | 2 | Preserve placeholder; route source guidance through root `AGENTS.md` to `source-code.md` and matching specialist rules |
| `production/**` | 1 | Preserve shared neutral state placeholder |

Disposition key:
- `ported`: converted into a Codex runtime or documentation asset.
- `replaced`: behavior retained through a different Codex-native mechanism.
- `shared`: retained at the same neutral project path.
- `not applicable`: intentionally omitted with rationale.
- `blocked`: cannot be completed without new data or a user decision.

Parity key:
- `exact`: same behavior and same or equivalent native capability.
- `semantic equivalent`: same workflow/artifact behavior through a different Codex primitive.
- `partial`: important behavior preserved, but some Claude feature has no exact Codex equivalent.
- `not applicable`: intentionally omitted with rationale.
- `blocked`: cannot be mapped without a new capability or user decision.

## Verified Codex Target Primitives

| Codex primitive | Verified target path or mechanism | Notes |
|---|---|---|
| Project instructions | Root `AGENTS.md` router plus `.codex/instructions/path-rules/*.md`; framework-local `AGENTS.md` only where separately useful | Codex loads the root-to-CWD instruction chain at session start, not rules selected per edited file. The shipped router is therefore the canonical CCGS path-rule mechanism; nested files are optional supplements, not parity enforcement. |
| Repo skills | `.agents/skills/<skill>/SKILL.md` | Official docs describe direct skill folders under `.agents/skills`. Use upstream folder/name values for CCGS parity and add collision auditing instead of relying on undocumented suppression. |
| Custom subagents | `.codex/agents/<agent>.toml` | Official docs describe standalone TOML files under `.codex/agents`. Preserve upstream hyphenated role names for filenames and `name` fields; add collision auditing rather than artificial prefixes. |
| Hooks | `.codex/hooks.json` plus `.codex/hooks/*` scripts | Project hooks require project trust. Supported lifecycle events do not include Claude's `Notification` hook event. |
| Command rules | `.codex/rules/settings.rules` | Codex command approval rules, not path-scoped content rules. |
| Permission profiles | `.codex/config.toml` with `default_permissions` and `[permissions.<name>]` | Do not mix with legacy `sandbox_mode` in the same distributable config. |
| TUI status line | `.codex/config.toml` `[tui].status_line` | Verified Codex-native footer configuration for built-in items such as model/context/current-dir/git. No verified project script item equivalent to Claude `statusLine.command`. |
| Notifications | user-level `notify`, `[tui].notifications`, `[tui].notification_method`, `[tui].notification_condition` | Codex has native notification settings, but project-local config cannot set `notify`; document user-level setup instead of installing `notify.sh` as a hook. |
| Plugins | Optional `.codex-plugin/plugin.json` package | Optional later distribution mechanism. Not the base architecture because loose repo files are simpler for coexistence. |
| MCP elicitation | Optional MCP tool prompt/elicitation support | Only use if a real MCP server is introduced. Default plan rewrites `AskUserQuestion` as numbered natural-language choices. |

Official docs used: `https://developers.openai.com/codex/guides/agents-md`, `https://developers.openai.com/codex/skills`, `https://developers.openai.com/codex/subagents`, `https://developers.openai.com/codex/hooks`, `https://developers.openai.com/codex/permissions`, `https://developers.openai.com/codex/rules`, `https://developers.openai.com/codex/plugins`, `https://developers.openai.com/codex/config-reference`.

## Core Runtime Mapping

| Upstream path/component | Upstream behavior | Claude Code mechanism | Codex target mechanism | Target path/name | Disposition | Parity | Implementation notes | Verification method |
|---|---|---|---|---|---|---|---|---|
| `CLAUDE.md` | Root studio operating instructions, lifecycle guidance, startup nudge | Root Claude instruction file with imported docs | Marker-managed root Codex instructions | `AGENTS.md` CCGS block | replaced | semantic equivalent | Inline critical guidance; remove `.claude/`, `CLAUDE.md`, and bare Claude slash-command references; tell users to run `start`. | Grep runtime docs for forbidden refs; `wc -c AGENTS.md`; prompt-input/manual instruction check. |
| `src/CLAUDE.md` | Source-code scope guidance | Nested Claude instructions | Root-routed Codex path guidance | `.codex/instructions/path-rules/source-code.md` plus specialist rule files | replaced | partial | Root `AGENTS.md` requires reading the matching rules before edits; this is advisory rather than upstream path-trigger enforcement. | Router-chain validation and instruction-budget check. |
| `design/CLAUDE.md` | Design-document scope guidance | Nested Claude instructions | Root-routed Codex path guidance | `.codex/instructions/path-rules/design-directory.md` | replaced | partial | Preserve design and registry guidance; keep `design/registry/entities.yaml` shared. | Router-chain validation; no runtime `.claude` refs. |
| `docs/CLAUDE.md` | Documentation scope guidance | Nested Claude instructions | Root-routed Codex path guidance | `.codex/instructions/path-rules/docs-directory.md` | replaced | partial | Preserve docs standards without depending on Claude imports. | Router-chain validation; instruction-budget check. |
| `CCGS Skill Testing Framework/CLAUDE.md` | Test-framework specific guidance | Nested Claude instructions | Testing-framework docs/instructions | `CCGS Skill Testing Framework/AGENTS.md` or README section | replaced | semantic equivalent | Preserve the upstream framework path; replace Claude-specific guidance with Codex guidance. | File existence; no runtime `.claude` dependency. |
| `.claude/settings.json` permissions | Allow/deny command and path policy | Claude permissions in settings JSON | Codex permission profile plus command rules | `.codex/config.toml`, `.codex/rules/settings.rules` | replaced | semantic equivalent | Use `[permissions.game_studios] extends = ":workspace"`, then explicitly restore workspace writes to `.git`, `.agents`, and `.codex`; the inherited read-only carve-outs are stricter than upstream and break Git and CCGS maintenance workflows. Deny sensitive env paths; command policies go in `.rules`, not config. | TOML parse; rules lint; forbidden command fixture; fresh trusted session resolves `.git`, `.agents`, and `.codex` as writable while `.env*` remains denied. |
| `.claude/settings.json` hooks | Hook event wiring | Claude settings hook blocks | Codex hooks config | `.codex/hooks.json` | replaced | semantic equivalent | Map supported lifecycle events only. Do not include Claude's `Notification` event; map notification behavior separately through user-level Codex notification docs. | JSON parse; event allowlist; command-path existence. |
| `.claude/statusline.sh` | Always-on context/model/stage/session breadcrumb | Claude scriptable status line command | Codex native footer config plus startup/on-demand studio status | `.codex/config.toml` `[tui].status_line`, `.codex/hooks/studio-status-on-start.sh`, `.agents/skills/studio-status/SKILL.md` | replaced | partial; `Stage:` footer blocked | Preserve context/model visibility with Codex built-in `status_line` items. Preserve stage/review/session breadcrumb through shared-state parsing in `studio-status-on-start.sh` and `studio-status`; actual footer `Stage:` parity is blocked until Codex exposes a documented project custom footer item. | Config parse; status_line item allowlist; hook fixture; `studio-status` smoke reads `production/session-state/active.md`; no fake custom footer key. |
| `.claude/agent-memory/lead-programmer/MEMORY.md` | Lead-programmer project memory seed | Claude agent memory file plus `memory: project` metadata | Repo-local Codex memory contract read by custom agent instructions | `.codex/agent-memory/lead-programmer/MEMORY.md` plus `.codex/agents/lead-programmer.toml` binding | ported | semantic equivalent | Rewrite Claude skill paths to `.agents/skills/<name>/SKILL.md` and keep canonical paths. Agent TOML must instruct `lead-programmer` to read the memory file before skill authoring, path canonicalization, and convention work. Do not write `~/.codex/memories`. | File existence; TOML binding scan; static scan: no writes to `~/.codex/memories`; content rewrite scan. |
| `production/session-state/.gitkeep` | Keeps shared session-state directory in template | Neutral placeholder | Shared neutral state | same path | shared | exact | Installer may create directory if absent, but uninstaller must not remove shared state. | Install/uninstall fixture; shared-state hash unchanged except intentional writes. |
| `design/registry/entities.yaml` | Entity registry used by design consistency workflows | Neutral YAML data | Shared neutral data | same path | shared | exact | Codex and Claude can both read/write this. | YAML parse; coexistence write/read smoke. |
| `src/.gitkeep` | Placeholder source directory | Neutral placeholder | Shared neutral placeholder | same path | shared | exact | Do not remove on uninstall. | Install/uninstall fixture. |

## Hook Mapping

The installed Codex hooks are upstream behavior with Codex adapter edits, not
freeform rewrites. Adapter edits are limited to Codex-owned paths, `$skill`
invocation text, `CCGS_ROOT` root-stable execution, `git -C "$ccgs_root"` calls,
and Codex hook payload parsing through `.codex/lib/hooks.sh`.

| Upstream hook | Upstream behavior | Claude event | Codex target | Disposition | Parity | Implementation notes | Verification method |
|---|---|---|---|---|---|---|---|
| `.claude/hooks/session-start.sh` | Session startup context | `SessionStart` | `.codex/hooks/session-start.sh` | ported | semantic equivalent | Rewrite stdin JSON fields to Codex hook schema. | Fixture stdin test; hooks.json event check. |
| `.claude/hooks/detect-gaps.sh` | Startup gap detection | `SessionStart` | `.codex/hooks/detect-gaps.sh` | ported | semantic equivalent | Must read neutral `production/`, `design/`, `docs/architecture/` paths. | Fixture with missing/complete project state. |
| `.claude/hooks/validate-commit.sh` | Git commit gate | `PreToolUse` on Bash | `.codex/hooks/validate-commit.sh` plus `.codex/rules/settings.rules` | ported | semantic equivalent | Blocking command policy belongs primarily in `.rules`; hook can add context-specific checks. | Bash fixture; command-rule `match`/`not_match` tests. |
| `.claude/hooks/validate-push.sh` | Git push protected-branch warning | `PreToolUse` on Bash | `.codex/hooks/validate-push.sh` plus `.codex/rules/settings.rules` | ported | semantic equivalent | Warn, do not block, for explicit or current-branch pushes to `develop`, `main`, or `master`. | Bash fixture; protected push advisory smoke. |
| `.claude/hooks/validate-assets.sh` | Asset validation after edits | `PostToolUse` on Write/Edit | `.codex/hooks/validate-assets.sh` | ported | semantic equivalent | Parse Codex `apply_patch` payload paths from `tool_input.command` with legacy `tool_input.patch` fallback; keep naming advisory and invalid JSON feedback after the edit. Exit 2 on PostToolUse reports feedback but does not roll back side effects. | apply_patch command-field fixture with naming warning and invalid JSON feedback; legacy patch fallback assertion. |
| `.claude/hooks/validate-skill-change.sh` | Skill metadata/content guard | `PostToolUse` on Write/Edit | `.codex/hooks/validate-skill-change.sh` | ported | semantic equivalent | Parse Codex `apply_patch` payload paths from `tool_input.command` with legacy fallback and advise `$skill-test static <name>` for `.agents/skills/<name>/SKILL.md` after the edit. | Fixture modifies sample skill through command-field payload; lint output. |
| `.claude/hooks/pre-compact.sh` | Preserve session notes before compaction | `PreCompact` | `.codex/hooks/pre-compact.sh` | ported | semantic equivalent | Codex matcher values are manual/auto. | PreCompact fixture. |
| `.claude/hooks/post-compact.sh` | Reload session notes after compaction | `PostCompact` | `.codex/hooks/post-compact.sh` | ported | semantic equivalent | Read/write only Codex-owned logs plus shared neutral handoff docs. | PostCompact fixture. |
| `.claude/hooks/log-agent.sh` | Log agent start | `SubagentStart` | `.codex/hooks/log-agent.sh` | ported | semantic equivalent | Codex fields include `agent_id` and `agent_type`. | SubagentStart fixture; log assertion. |
| `.claude/hooks/log-agent-stop.sh` | Log agent stop | `SubagentStop` | `.codex/hooks/log-agent-stop.sh` | ported | semantic equivalent | Same log namespace as start. | SubagentStop fixture; log assertion. |
| `.claude/hooks/session-stop.sh` | End-session summary/logging | `Stop` | `.codex/hooks/session-stop.sh` | ported | semantic equivalent | Use common fields only; no Claude matcher assumptions. | Stop fixture. |
| `.claude/hooks/notify.sh` | Desktop notification when Claude emits a notification | `Notification` hook event | Native Codex notifications documented for user-level setup; no project hook | `.codex/docs/COEXISTENCE.md` / `.codex/docs/README.md` notification section | replaced | partial | Codex has native TUI notifications and user-level `notify`, but no Claude-style `Notification` hook event, and project config cannot set user-level `notify`. Upstream script is Windows-oriented, so the faithful Codex port documents native notification setup rather than installing this script as a project hook. | Assert `Notification` absent from hooks.json; docs mention `notify`, `[tui].notifications`, and project-local limitation. |
| n/a | Codex startup status summary | `SessionStart` | `.codex/hooks/studio-status-on-start.sh` | added | Codex-additive | Not upstream parity; preserves status visibility using Codex-native shared state reads. | Fixture stdin test; documentation marks additive. |

## Rule Mapping

Upstream `.claude/rules/*.md` files are path-scoped instruction rules. CCGS
ships them as `.codex/instructions/path-rules/*.md` and makes root `AGENTS.md`
the canonical router. Codex's nested instruction chain is selected from the
session working directory, not dynamically for every edited file, so nested
`AGENTS.md` files do not restore upstream path-trigger semantics for a
root-launched session. This is an intentional, advisory partial-parity mapping.
Codex command `.rules` remain reserved for shell command approval policy.

| Upstream rule | Codex target | Disposition | Parity | Verification |
|---|---|---|---|---|
| `.claude/rules/ai-code.md` | `.codex/instructions/path-rules/ai-code.md` | replaced | partial | Root-router chain validation. |
| `.claude/rules/data-files.md` | `.codex/instructions/path-rules/data-files.md` | replaced | partial | Root-router chain validation. |
| `.claude/rules/design-docs.md` | `.codex/instructions/path-rules/design-docs.md` | replaced | partial | Root-router chain validation. |
| `.claude/rules/engine-code.md` | `.codex/instructions/path-rules/engine-code.md` | replaced | partial | Root-router chain validation. |
| `.claude/rules/gameplay-code.md` | `.codex/instructions/path-rules/gameplay-code.md` | replaced | partial | Root-router chain validation. |
| `.claude/rules/narrative.md` | `.codex/instructions/path-rules/narrative.md` | replaced | partial | Root-router chain validation. |
| `.claude/rules/network-code.md` | `.codex/instructions/path-rules/network-code.md` | replaced | partial | Root-router chain validation. |
| `.claude/rules/prototype-code.md` | `.codex/instructions/path-rules/prototype-code.md` | replaced | partial | Root-router chain validation. |
| `.claude/rules/shader-code.md` | `.codex/instructions/path-rules/shader-code.md` | replaced | partial | Root-router chain validation. |
| `.claude/rules/test-standards.md` | `.codex/instructions/path-rules/test-standards.md` | replaced | partial | Root-router chain validation. |
| `.claude/rules/ui-code.md` | `.codex/instructions/path-rules/ui-code.md` | replaced | partial | Root-router chain validation. |

## Agent Mapping

Common mapping for all rows: upstream behavior is a role persona for delegation; Claude mechanism is a `.claude/agents/*.md` Task subagent; Codex mechanism is a project custom agent TOML. Tool fences, memory, `maxTurns`, and worktree isolation are partial and covered in the risk register.

| Upstream agent | Model tier | Codex target file | Codex agent name | Disposition | Parity | Notes | Verification |
|---|---|---|---|---|---|---|---|
| `.claude/agents/accessibility-specialist.md` | sonnet | `.codex/agents/accessibility-specialist.toml` | `accessibility-specialist` | ported | semantic equivalent | model map: `gpt-5.4`, medium | TOML parse; field check; role smoke. |
| `.claude/agents/ai-programmer.md` | sonnet | `.codex/agents/ai-programmer.toml` | `ai-programmer` | ported | semantic equivalent | model map: `gpt-5.4`, medium | TOML parse; field check; role smoke. |
| `.claude/agents/analytics-engineer.md` | sonnet | `.codex/agents/analytics-engineer.toml` | `analytics-engineer` | ported | semantic equivalent | model map: `gpt-5.4`, medium | TOML parse; field check; role smoke. |
| `.claude/agents/art-director.md` | sonnet | `.codex/agents/art-director.toml` | `art-director` | ported | semantic equivalent | preserve project-memory intent in instructions | TOML parse; field check; role smoke. |
| `.claude/agents/audio-director.md` | sonnet | `.codex/agents/audio-director.toml` | `audio-director` | ported | semantic equivalent | preserve project-memory intent in instructions | TOML parse; field check; role smoke. |
| `.claude/agents/community-manager.md` | haiku | `.codex/agents/community-manager.toml` | `community-manager` | ported | semantic equivalent | model map: `gpt-5.4-mini`, low | TOML parse; field check; role smoke. |
| `.claude/agents/creative-director.md` | opus | `.codex/agents/creative-director.toml` | `creative-director` | ported | partial | preserve pinned skills `brainstorm`, `design-review` as guidance; model map `gpt-5.5`, high | TOML parse; pinned-skill guidance scan; role smoke. |
| `.claude/agents/devops-engineer.md` | haiku | `.codex/agents/devops-engineer.toml` | `devops-engineer` | ported | semantic equivalent | model map: `gpt-5.4-mini`, low | TOML parse; field check; role smoke. |
| `.claude/agents/economy-designer.md` | sonnet | `.codex/agents/economy-designer.toml` | `economy-designer` | ported | semantic equivalent | preserve project-memory intent in instructions | TOML parse; field check; role smoke. |
| `.claude/agents/engine-programmer.md` | sonnet | `.codex/agents/engine-programmer.toml` | `engine-programmer` | ported | semantic equivalent | model map: `gpt-5.4`, medium | TOML parse; field check; role smoke. |
| `.claude/agents/game-designer.md` | sonnet | `.codex/agents/game-designer.toml` | `game-designer` | ported | partial | preserve pinned skills `design-review`, `balance-check`, `brainstorm` as guidance | TOML parse; pinned-skill guidance scan; role smoke. |
| `.claude/agents/gameplay-programmer.md` | sonnet | `.codex/agents/gameplay-programmer.toml` | `gameplay-programmer` | ported | semantic equivalent | model map: `gpt-5.4`, medium | TOML parse; field check; role smoke. |
| `.claude/agents/godot-csharp-specialist.md` | sonnet | `.codex/agents/godot-csharp-specialist.toml` | `godot-csharp-specialist` | ported | semantic equivalent | engine specialist role | TOML parse; field check; role smoke. |
| `.claude/agents/godot-gdextension-specialist.md` | sonnet | `.codex/agents/godot-gdextension-specialist.toml` | `godot-gdextension-specialist` | ported | semantic equivalent | engine specialist role | TOML parse; field check; role smoke. |
| `.claude/agents/godot-gdscript-specialist.md` | sonnet | `.codex/agents/godot-gdscript-specialist.toml` | `godot-gdscript-specialist` | ported | semantic equivalent | engine specialist role | TOML parse; field check; role smoke. |
| `.claude/agents/godot-shader-specialist.md` | sonnet | `.codex/agents/godot-shader-specialist.toml` | `godot-shader-specialist` | ported | semantic equivalent | engine specialist role | TOML parse; field check; role smoke. |
| `.claude/agents/godot-specialist.md` | sonnet | `.codex/agents/godot-specialist.toml` | `godot-specialist` | ported | semantic equivalent | engine specialist role | TOML parse; field check; role smoke. |
| `.claude/agents/lead-programmer.md` | sonnet | `.codex/agents/lead-programmer.toml` | `lead-programmer` | ported | partial | preserve pinned skills `code-review`, `architecture-decision`, `tech-debt`; bind `.codex/agent-memory/lead-programmer/MEMORY.md` | TOML parse; memory/guidance scan; role smoke. |
| `.claude/agents/level-designer.md` | sonnet | `.codex/agents/level-designer.toml` | `level-designer` | ported | semantic equivalent | preserve project-memory intent in instructions | TOML parse; field check; role smoke. |
| `.claude/agents/live-ops-designer.md` | sonnet | `.codex/agents/live-ops-designer.toml` | `live-ops-designer` | ported | semantic equivalent | model map: `gpt-5.4`, medium | TOML parse; field check; role smoke. |
| `.claude/agents/localization-lead.md` | sonnet | `.codex/agents/localization-lead.toml` | `localization-lead` | ported | semantic equivalent | preserve project-memory intent in instructions | TOML parse; field check; role smoke. |
| `.claude/agents/narrative-director.md` | sonnet | `.codex/agents/narrative-director.toml` | `narrative-director` | ported | semantic equivalent | preserve project-memory intent in instructions | TOML parse; field check; role smoke. |
| `.claude/agents/network-programmer.md` | sonnet | `.codex/agents/network-programmer.toml` | `network-programmer` | ported | semantic equivalent | model map: `gpt-5.4`, medium | TOML parse; field check; role smoke. |
| `.claude/agents/performance-analyst.md` | sonnet | `.codex/agents/performance-analyst.toml` | `performance-analyst` | ported | semantic equivalent | preserve project-memory intent in instructions | TOML parse; field check; role smoke. |
| `.claude/agents/producer.md` | opus | `.codex/agents/producer.toml` | `producer` | ported | partial | preserve pinned skills `sprint-plan`, `scope-check`, `estimate`, `milestone-review`; model map `gpt-5.5`, high | TOML parse; pinned-skill guidance scan; role smoke. |
| `.claude/agents/prototyper.md` | sonnet | `.codex/agents/prototyper.toml` | `prototyper` | ported | partial | upstream has `isolation: worktree`; make worktree creation explicit | TOML parse; worktree workflow smoke/manual check. |
| `.claude/agents/qa-lead.md` | sonnet | `.codex/agents/qa-lead.toml` | `qa-lead` | ported | partial | preserve pinned skills `bug-report`, `release-checklist` | TOML parse; pinned-skill guidance scan; role smoke. |
| `.claude/agents/qa-tester.md` | sonnet | `.codex/agents/qa-tester.toml` | `qa-tester` | ported | semantic equivalent | model map: `gpt-5.4`, medium | TOML parse; field check; role smoke. |
| `.claude/agents/release-manager.md` | sonnet | `.codex/agents/release-manager.toml` | `release-manager` | ported | partial | preserve pinned skills `release-checklist`, `changelog`, `patch-notes` | TOML parse; pinned-skill guidance scan; role smoke. |
| `.claude/agents/security-engineer.md` | sonnet | `.codex/agents/security-engineer.toml` | `security-engineer` | ported | semantic equivalent | model map: `gpt-5.4`, medium | TOML parse; field check; role smoke. |
| `.claude/agents/sound-designer.md` | sonnet | `.codex/agents/sound-designer.toml` | `sound-designer` | ported | semantic equivalent | model map: `gpt-5.4`, medium | TOML parse; field check; role smoke. |
| `.claude/agents/systems-designer.md` | sonnet | `.codex/agents/systems-designer.toml` | `systems-designer` | ported | semantic equivalent | preserve project-memory intent in instructions | TOML parse; field check; role smoke. |
| `.claude/agents/technical-artist.md` | sonnet | `.codex/agents/technical-artist.toml` | `technical-artist` | ported | semantic equivalent | model map: `gpt-5.4`, medium | TOML parse; field check; role smoke. |
| `.claude/agents/technical-director.md` | opus | `.codex/agents/technical-director.toml` | `technical-director` | ported | semantic equivalent | model map: `gpt-5.5`, high; preserve user-memory intent as docs only | TOML parse; field check; role smoke. |
| `.claude/agents/tools-programmer.md` | sonnet | `.codex/agents/tools-programmer.toml` | `tools-programmer` | ported | semantic equivalent | model map: `gpt-5.4`, medium | TOML parse; field check; role smoke. |
| `.claude/agents/ue-blueprint-specialist.md` | sonnet | `.codex/agents/ue-blueprint-specialist.toml` | `ue-blueprint-specialist` | ported | semantic equivalent | engine specialist role | TOML parse; field check; role smoke. |
| `.claude/agents/ue-gas-specialist.md` | sonnet | `.codex/agents/ue-gas-specialist.toml` | `ue-gas-specialist` | ported | semantic equivalent | engine specialist role | TOML parse; field check; role smoke. |
| `.claude/agents/ue-replication-specialist.md` | sonnet | `.codex/agents/ue-replication-specialist.toml` | `ue-replication-specialist` | ported | semantic equivalent | engine specialist role | TOML parse; field check; role smoke. |
| `.claude/agents/ue-umg-specialist.md` | sonnet | `.codex/agents/ue-umg-specialist.toml` | `ue-umg-specialist` | ported | semantic equivalent | engine specialist role | TOML parse; field check; role smoke. |
| `.claude/agents/ui-programmer.md` | sonnet | `.codex/agents/ui-programmer.toml` | `ui-programmer` | ported | semantic equivalent | model map: `gpt-5.4`, medium | TOML parse; field check; role smoke. |
| `.claude/agents/unity-addressables-specialist.md` | sonnet | `.codex/agents/unity-addressables-specialist.toml` | `unity-addressables-specialist` | ported | semantic equivalent | engine specialist role | TOML parse; field check; role smoke. |
| `.claude/agents/unity-dots-specialist.md` | sonnet | `.codex/agents/unity-dots-specialist.toml` | `unity-dots-specialist` | ported | semantic equivalent | engine specialist role | TOML parse; field check; role smoke. |
| `.claude/agents/unity-shader-specialist.md` | sonnet | `.codex/agents/unity-shader-specialist.toml` | `unity-shader-specialist` | ported | semantic equivalent | engine specialist role | TOML parse; field check; role smoke. |
| `.claude/agents/unity-specialist.md` | sonnet | `.codex/agents/unity-specialist.toml` | `unity-specialist` | ported | semantic equivalent | engine specialist role | TOML parse; field check; role smoke. |
| `.claude/agents/unity-ui-specialist.md` | sonnet | `.codex/agents/unity-ui-specialist.toml` | `unity-ui-specialist` | ported | semantic equivalent | engine specialist role | TOML parse; field check; role smoke. |
| `.claude/agents/unreal-specialist.md` | sonnet | `.codex/agents/unreal-specialist.toml` | `unreal-specialist` | ported | semantic equivalent | engine specialist role | TOML parse; field check; role smoke. |
| `.claude/agents/ux-designer.md` | sonnet | `.codex/agents/ux-designer.toml` | `ux-designer` | ported | semantic equivalent | preserve project-memory intent in instructions | TOML parse; field check; role smoke. |
| `.claude/agents/world-builder.md` | sonnet | `.codex/agents/world-builder.toml` | `world-builder` | ported | semantic equivalent | preserve project-memory intent in instructions | TOML parse; field check; role smoke. |
| `.claude/agents/writer.md` | sonnet | `.codex/agents/writer.toml` | `writer` | ported | semantic equivalent | preserve project-memory intent in instructions | TOML parse; field check; role smoke. |

## Skill Mapping

Common mapping for all rows: upstream behavior is a user-invocable Claude skill or slash-command equivalent; Claude mechanism is `.claude/skills/<name>/SKILL.md`; Codex mechanism is a repo skill at `.agents/skills/<name>/SKILL.md` with `name: <name>`. Claude-only metadata is moved into the body as ported metadata. `Task`, `AskUserQuestion`, bare `/skill` references, and `.claude/` paths must be rewritten. Same-name skill collisions must be reported; the port must not silently prefix or rename skills.

| Upstream skill | Model tier | Codex target | Codex skill name | Disposition | Parity | Notes | Verification |
|---|---|---|---|---|---|---|---|
| `.claude/skills/adopt/SKILL.md` | sonnet | `.agents/skills/adopt/SKILL.md` | `adopt` | ported | semantic equivalent | Brownfield onboarding workflow | Metadata lint; rewrite scan; smoke as needed. |
| `.claude/skills/architecture-decision/SKILL.md` | sonnet | `.agents/skills/architecture-decision/SKILL.md` | `architecture-decision` | ported | semantic equivalent | ADR authoring | Metadata lint; rewrite scan; smoke as needed. |
| `.claude/skills/architecture-review/SKILL.md` | opus | `.agents/skills/architecture-review/SKILL.md` | `architecture-review` | ported | partial | High-reasoning skill; delegate to high-tier agents or instruct model choice | Metadata lint; model-tier check; smoke. |
| `.claude/skills/art-bible/SKILL.md` | sonnet | `.agents/skills/art-bible/SKILL.md` | `art-bible` | ported | semantic equivalent | Art bible authoring | Metadata lint; rewrite scan. |
| `.claude/skills/asset-audit/SKILL.md` | sonnet | `.agents/skills/asset-audit/SKILL.md` | `asset-audit` | ported | semantic equivalent | Asset compliance audit | Metadata lint; rewrite scan. |
| `.claude/skills/asset-spec/SKILL.md` | sonnet | `.agents/skills/asset-spec/SKILL.md` | `asset-spec` | ported | semantic equivalent | Asset visual spec generation | Metadata lint; rewrite scan. |
| `.claude/skills/balance-check/SKILL.md` | sonnet | `.agents/skills/balance-check/SKILL.md` | `balance-check` | ported | semantic equivalent | Balance analysis | Metadata lint; rewrite scan. |
| `.claude/skills/brainstorm/SKILL.md` | sonnet | `.agents/skills/brainstorm/SKILL.md` | `brainstorm` | ported | partial | Structured questions rewritten as numbered options | Metadata lint; `AskUserQuestion` rewrite scan; smoke. |
| `.claude/skills/bug-report/SKILL.md` | sonnet | `.agents/skills/bug-report/SKILL.md` | `bug-report` | ported | semantic equivalent | Bug report workflow | Metadata lint; rewrite scan. |
| `.claude/skills/bug-triage/SKILL.md` | sonnet | `.agents/skills/bug-triage/SKILL.md` | `bug-triage` | ported | semantic equivalent | Bug triage workflow | Metadata lint; rewrite scan. |
| `.claude/skills/changelog/SKILL.md` | haiku | `.agents/skills/changelog/SKILL.md` | `changelog` | ported | partial | Low-tier model hint is advisory in main-thread skill | Metadata lint; model note scan. |
| `.claude/skills/code-review/SKILL.md` | sonnet | `.agents/skills/code-review/SKILL.md` | `code-review` | ported | semantic equivalent | Review workflow | Metadata lint; rewrite scan. |
| `.claude/skills/consistency-check/SKILL.md` | sonnet | `.agents/skills/consistency-check/SKILL.md` | `consistency-check` | ported | semantic equivalent | Registry/GDD consistency | Metadata lint; rewrite scan. |
| `.claude/skills/content-audit/SKILL.md` | sonnet | `.agents/skills/content-audit/SKILL.md` | `content-audit` | ported | semantic equivalent | Content-count audit | Metadata lint; rewrite scan. |
| `.claude/skills/create-architecture/SKILL.md` | sonnet | `.agents/skills/create-architecture/SKILL.md` | `create-architecture` | ported | partial | Structured authoring questions rewritten as numbered options | Metadata lint; smoke. |
| `.claude/skills/create-control-manifest/SKILL.md` | sonnet | `.agents/skills/create-control-manifest/SKILL.md` | `create-control-manifest` | ported | semantic equivalent | Control manifest generation | Metadata lint; rewrite scan. |
| `.claude/skills/create-epics/SKILL.md` | sonnet | `.agents/skills/create-epics/SKILL.md` | `create-epics` | ported | semantic equivalent | Epic creation | Metadata lint; rewrite scan. |
| `.claude/skills/create-stories/SKILL.md` | sonnet | `.agents/skills/create-stories/SKILL.md` | `create-stories` | ported | semantic equivalent | Story breakdown | Metadata lint; rewrite scan. |
| `.claude/skills/day-one-patch/SKILL.md` | sonnet | `.agents/skills/day-one-patch/SKILL.md` | `day-one-patch` | ported | semantic equivalent | Launch patch workflow | Metadata lint; rewrite scan. |
| `.claude/skills/design-review/SKILL.md` | sonnet | `.agents/skills/design-review/SKILL.md` | `design-review` | ported | semantic equivalent | Design review | Metadata lint; rewrite scan. |
| `.claude/skills/design-system/SKILL.md` | sonnet | `.agents/skills/design-system/SKILL.md` | `design-system` | ported | partial | Structured GDD authoring questions rewritten | Metadata lint; smoke. |
| `.claude/skills/dev-story/SKILL.md` | sonnet | `.agents/skills/dev-story/SKILL.md` | `dev-story` | ported | semantic equivalent | Story implementation lifecycle | Metadata lint; smoke. |
| `.claude/skills/estimate/SKILL.md` | sonnet | `.agents/skills/estimate/SKILL.md` | `estimate` | ported | semantic equivalent | Effort estimate | Metadata lint; rewrite scan. |
| `.claude/skills/gate-check/SKILL.md` | opus | `.agents/skills/gate-check/SKILL.md` | `gate-check` | ported | partial | High-reasoning gate; preserve verdict contracts | Metadata lint; model-tier check; smoke. |
| `.claude/skills/help/SKILL.md` | haiku | `.agents/skills/help/SKILL.md` | `help` | ported | partial | Low-tier hint advisory | Metadata lint; rewrite scan. |
| `.claude/skills/hotfix/SKILL.md` | sonnet | `.agents/skills/hotfix/SKILL.md` | `hotfix` | ported | semantic equivalent | Emergency fix workflow | Metadata lint; rewrite scan. |
| `.claude/skills/launch-checklist/SKILL.md` | sonnet | `.agents/skills/launch-checklist/SKILL.md` | `launch-checklist` | ported | semantic equivalent | Launch readiness | Metadata lint; rewrite scan. |
| `.claude/skills/localize/SKILL.md` | sonnet | `.agents/skills/localize/SKILL.md` | `localize` | ported | semantic equivalent | Localization workflow | Metadata lint; rewrite scan. |
| `.claude/skills/map-systems/SKILL.md` | sonnet | `.agents/skills/map-systems/SKILL.md` | `map-systems` | ported | semantic equivalent | System decomposition | Metadata lint; rewrite scan. |
| `.claude/skills/milestone-review/SKILL.md` | sonnet | `.agents/skills/milestone-review/SKILL.md` | `milestone-review` | ported | semantic equivalent | Milestone review | Metadata lint; rewrite scan. |
| `.claude/skills/onboard/SKILL.md` | haiku | `.agents/skills/onboard/SKILL.md` | `onboard` | ported | partial | Low-tier hint advisory | Metadata lint; rewrite scan. |
| `.claude/skills/patch-notes/SKILL.md` | haiku | `.agents/skills/patch-notes/SKILL.md` | `patch-notes` | ported | partial | Low-tier hint advisory | Metadata lint; rewrite scan. |
| `.claude/skills/perf-profile/SKILL.md` | sonnet | `.agents/skills/perf-profile/SKILL.md` | `perf-profile` | ported | semantic equivalent | Performance profiling | Metadata lint; rewrite scan. |
| `.claude/skills/playtest-report/SKILL.md` | sonnet | `.agents/skills/playtest-report/SKILL.md` | `playtest-report` | ported | semantic equivalent | Playtest report generation | Metadata lint; rewrite scan. |
| `.claude/skills/project-stage-detect/SKILL.md` | haiku | `.agents/skills/project-stage-detect/SKILL.md` | `project-stage-detect` | ported | partial | Low-tier hint advisory; stage detection must stay neutral-path based | Metadata lint; smoke. |
| `.claude/skills/propagate-design-change/SKILL.md` | sonnet | `.agents/skills/propagate-design-change/SKILL.md` | `propagate-design-change` | ported | semantic equivalent | Design-change propagation | Metadata lint; rewrite scan. |
| `.claude/skills/prototype/SKILL.md` | sonnet | `.agents/skills/prototype/SKILL.md` | `prototype` | ported | partial | Upstream `isolation: worktree`; make worktree setup explicit | Metadata lint; worktree smoke/manual check. |
| `.claude/skills/qa-plan/SKILL.md` | sonnet | `.agents/skills/qa-plan/SKILL.md` | `qa-plan` | ported | semantic equivalent | QA plan | Metadata lint; rewrite scan. |
| `.claude/skills/quick-design/SKILL.md` | sonnet | `.agents/skills/quick-design/SKILL.md` | `quick-design` | ported | partial | Structured options rewritten | Metadata lint; rewrite scan. |
| `.claude/skills/regression-suite/SKILL.md` | sonnet | `.agents/skills/regression-suite/SKILL.md` | `regression-suite` | ported | semantic equivalent | Regression plan | Metadata lint; rewrite scan. |
| `.claude/skills/release-checklist/SKILL.md` | sonnet | `.agents/skills/release-checklist/SKILL.md` | `release-checklist` | ported | semantic equivalent | Release readiness | Metadata lint; rewrite scan. |
| `.claude/skills/retrospective/SKILL.md` | sonnet | `.agents/skills/retrospective/SKILL.md` | `retrospective` | ported | semantic equivalent | Retro workflow | Metadata lint; rewrite scan. |
| `.claude/skills/reverse-document/SKILL.md` | sonnet | `.agents/skills/reverse-document/SKILL.md` | `reverse-document` | ported | semantic equivalent | Reverse documentation | Metadata lint; rewrite scan. |
| `.claude/skills/review-all-gdds/SKILL.md` | opus | `.agents/skills/review-all-gdds/SKILL.md` | `review-all-gdds` | ported | partial | High-reasoning review; preserve multi-GDD gate semantics | Metadata lint; model-tier check; smoke. |
| `.claude/skills/scope-check/SKILL.md` | haiku | `.agents/skills/scope-check/SKILL.md` | `scope-check` | ported | partial | Low-tier hint advisory | Metadata lint; rewrite scan. |
| `.claude/skills/security-audit/SKILL.md` | sonnet | `.agents/skills/security-audit/SKILL.md` | `security-audit` | ported | semantic equivalent | Security audit | Metadata lint; rewrite scan. |
| `.claude/skills/setup-engine/SKILL.md` | sonnet | `.agents/skills/setup-engine/SKILL.md` | `setup-engine` | ported | partial | Structured engine questions rewritten | Metadata lint; smoke. |
| `.claude/skills/skill-improve/SKILL.md` | sonnet | `.agents/skills/skill-improve/SKILL.md` | `skill-improve` | ported | semantic equivalent | Skill improvement loop | Metadata lint; rewrite scan. |
| `.claude/skills/skill-test/SKILL.md` | sonnet | `.agents/skills/skill-test/SKILL.md` | `skill-test` | ported | semantic equivalent | Upstream skill, not new | Metadata lint; testing-framework reference scan. |
| `.claude/skills/smoke-check/SKILL.md` | sonnet | `.agents/skills/smoke-check/SKILL.md` | `smoke-check` | ported | semantic equivalent | Smoke gate | Metadata lint; smoke. |
| `.claude/skills/soak-test/SKILL.md` | sonnet | `.agents/skills/soak-test/SKILL.md` | `soak-test` | ported | semantic equivalent | Soak protocol | Metadata lint; rewrite scan. |
| `.claude/skills/sprint-plan/SKILL.md` | sonnet | `.agents/skills/sprint-plan/SKILL.md` | `sprint-plan` | ported | semantic equivalent | Sprint planning | Metadata lint; smoke. |
| `.claude/skills/sprint-status/SKILL.md` | haiku | `.agents/skills/sprint-status/SKILL.md` | `sprint-status` | ported | partial | Low-tier hint advisory | Metadata lint; smoke. |
| `.claude/skills/start/SKILL.md` | sonnet | `.agents/skills/start/SKILL.md` | `start` | ported | semantic equivalent | First-time onboarding entry point | Metadata lint; end-to-end onboarding smoke. |
| `.claude/skills/story-done/SKILL.md` | sonnet | `.agents/skills/story-done/SKILL.md` | `story-done` | ported | semantic equivalent | End-of-story review | Metadata lint; smoke. |
| `.claude/skills/story-readiness/SKILL.md` | sonnet | `.agents/skills/story-readiness/SKILL.md` | `story-readiness` | ported | semantic equivalent | Story readiness gate | Metadata lint; smoke. |
| `.claude/skills/team-audio/SKILL.md` | sonnet | `.agents/skills/team-audio/SKILL.md` | `team-audio` | ported | semantic equivalent | Team orchestration | Metadata lint; delegation reference check. |
| `.claude/skills/team-combat/SKILL.md` | sonnet | `.agents/skills/team-combat/SKILL.md` | `team-combat` | ported | semantic equivalent | Team orchestration | Metadata lint; delegation reference check. |
| `.claude/skills/team-level/SKILL.md` | sonnet | `.agents/skills/team-level/SKILL.md` | `team-level` | ported | semantic equivalent | Team orchestration | Metadata lint; delegation reference check. |
| `.claude/skills/team-live-ops/SKILL.md` | sonnet | `.agents/skills/team-live-ops/SKILL.md` | `team-live-ops` | ported | semantic equivalent | Team orchestration | Metadata lint; delegation reference check. |
| `.claude/skills/team-narrative/SKILL.md` | sonnet | `.agents/skills/team-narrative/SKILL.md` | `team-narrative` | ported | semantic equivalent | Team orchestration | Metadata lint; delegation reference check. |
| `.claude/skills/team-polish/SKILL.md` | sonnet | `.agents/skills/team-polish/SKILL.md` | `team-polish` | ported | semantic equivalent | Team orchestration | Metadata lint; delegation reference check. |
| `.claude/skills/team-qa/SKILL.md` | sonnet | `.agents/skills/team-qa/SKILL.md` | `team-qa` | ported | semantic equivalent | Team orchestration | Metadata lint; delegation reference check. |
| `.claude/skills/team-release/SKILL.md` | sonnet | `.agents/skills/team-release/SKILL.md` | `team-release` | ported | semantic equivalent | Team orchestration | Metadata lint; delegation reference check. |
| `.claude/skills/team-ui/SKILL.md` | sonnet | `.agents/skills/team-ui/SKILL.md` | `team-ui` | ported | semantic equivalent | Team orchestration | Metadata lint; delegation reference check. |
| `.claude/skills/tech-debt/SKILL.md` | sonnet | `.agents/skills/tech-debt/SKILL.md` | `tech-debt` | ported | semantic equivalent | Tech debt tracking | Metadata lint; rewrite scan. |
| `.claude/skills/test-evidence-review/SKILL.md` | sonnet | `.agents/skills/test-evidence-review/SKILL.md` | `test-evidence-review` | ported | semantic equivalent | Test evidence review | Metadata lint; rewrite scan. |
| `.claude/skills/test-flakiness/SKILL.md` | sonnet | `.agents/skills/test-flakiness/SKILL.md` | `test-flakiness` | ported | semantic equivalent | Flakiness triage | Metadata lint; rewrite scan. |
| `.claude/skills/test-helpers/SKILL.md` | sonnet | `.agents/skills/test-helpers/SKILL.md` | `test-helpers` | ported | semantic equivalent | Test helper generation | Metadata lint; rewrite scan. |
| `.claude/skills/test-setup/SKILL.md` | sonnet | `.agents/skills/test-setup/SKILL.md` | `test-setup` | ported | semantic equivalent | Test/CI scaffold | Metadata lint; rewrite scan. |
| `.claude/skills/ux-design/SKILL.md` | sonnet | `.agents/skills/ux-design/SKILL.md` | `ux-design` | ported | partial | Structured UX authoring questions rewritten | Metadata lint; smoke. |
| `.claude/skills/ux-review/SKILL.md` | sonnet | `.agents/skills/ux-review/SKILL.md` | `ux-review` | ported | semantic equivalent | UX review | Metadata lint; rewrite scan. |
| `.claude/skills/vertical-slice/SKILL.md` | sonnet | `.agents/skills/vertical-slice/SKILL.md` | `vertical-slice` | ported | partial | Upstream `isolation: worktree`; framework spec missing upstream | Metadata lint; worktree smoke/manual check; missing spec check. |
| New Codex status skill | n/a | `.agents/skills/studio-status/SKILL.md` | `studio-status` | ported | new Codex-native support | Complements native `tui.status_line` by rendering the game-stage/review/session breadcrumb on demand | Metadata lint; reads shared state. |
| New Codex continuity skill | n/a | `.agents/skills/studio-next/SKILL.md` | `studio-next` | ported | new Codex-native support | Reads handoff, active session, sprint, stage, workflow, and slice state to recommend the single best next action after discrete work | Metadata lint; read-only state routing smoke. |

## Agent Memory Mapping

Codex has global/thread Memories under `~/.codex/memories`, but no documented direct equivalent of Claude's per-agent `memory: user` or `memory: project` binding. The port therefore preserves memory scope as repo-local agent memory contracts and explicit custom-agent instructions. The installer must not write global Codex memories.

| Upstream memory source | Scope | Codex target | Disposition | Parity | Implementation notes | Verification |
|---|---|---|---|---|---|---|
| `.claude/agents/creative-director.md` `memory: user` | user | `.codex/agent-memory/creative-director/MEMORY.md` plus `.codex/agents/creative-director.toml` binding | replaced | semantic equivalent | Generated memory contract for durable creative taste, vision preferences, pillar rulings, and recurring user-level creative constraints. Label as generated; do not invent historical upstream memories. | Agent TOML includes `Ported Claude memory scope: user`; memory file exists; no `~/.codex/memories` writes. |
| `.claude/agents/technical-director.md` `memory: user` | user | `.codex/agent-memory/technical-director/MEMORY.md` plus `.codex/agents/technical-director.toml` binding | replaced | semantic equivalent | Generated memory contract for durable engine/tooling preferences, architecture principles, platform constraints, and recurring technical standards. | TOML binding scan; memory file exists. |
| `.claude/agents/producer.md` `memory: user` | user | `.codex/agent-memory/producer/MEMORY.md` plus `.codex/agents/producer.toml` binding | replaced | semantic equivalent | Generated memory contract for planning style, scope tolerance, schedule/risk preferences, and recurring production constraints. | TOML binding scan; memory file exists. |
| `.claude/agents/art-director.md` `memory: project` | project | `.codex/agent-memory/art-director/MEMORY.md` plus TOML binding | replaced | semantic equivalent | Generated project memory contract for visual identity, art bible decisions, asset constraints, and art pipeline preferences. | TOML binding scan; memory file exists. |
| `.claude/agents/audio-director.md` `memory: project` | project | `.codex/agent-memory/audio-director/MEMORY.md` plus TOML binding | replaced | semantic equivalent | Generated project memory contract for audio identity, mix rules, middleware, and sound bible decisions. | TOML binding scan; memory file exists. |
| `.claude/agents/economy-designer.md` `memory: project` | project | `.codex/agent-memory/economy-designer/MEMORY.md` plus TOML binding | replaced | semantic equivalent | Generated project memory contract for balance, economy formulas, progression rules, and monetization constraints. | TOML binding scan; memory file exists. |
| `.claude/agents/game-designer.md` `memory: project` | project | `.codex/agent-memory/game-designer/MEMORY.md` plus TOML binding | replaced | semantic equivalent | Generated project memory contract for mechanics, GDD conventions, system boundaries, and gameplay pillars. | TOML binding scan; memory file exists. |
| `.claude/agents/lead-programmer.md` plus `.claude/agent-memory/lead-programmer/MEMORY.md` | project | `.codex/agent-memory/lead-programmer/MEMORY.md` plus `.codex/agents/lead-programmer.toml` binding | ported | semantic equivalent | Rewrite the explicit upstream memory file for Codex paths and metadata expectations. | Content rewrite scan; TOML binding scan. |
| `.claude/agents/level-designer.md` `memory: project` | project | `.codex/agent-memory/level-designer/MEMORY.md` plus TOML binding | replaced | semantic equivalent | Generated project memory contract for level layout conventions, pacing, encounter grammar, and spatial constraints. | TOML binding scan; memory file exists. |
| `.claude/agents/localization-lead.md` `memory: project` | project | `.codex/agent-memory/localization-lead/MEMORY.md` plus TOML binding | replaced | semantic equivalent | Generated project memory contract for locale policy, string pipeline, glossary, and translation memory conventions. | TOML binding scan; memory file exists. |
| `.claude/agents/narrative-director.md` `memory: project` | project | `.codex/agent-memory/narrative-director/MEMORY.md` plus TOML binding | replaced | semantic equivalent | Generated project memory contract for canon, voice, story constraints, and narrative bible decisions. | TOML binding scan; memory file exists. |
| `.claude/agents/performance-analyst.md` `memory: project` | project | `.codex/agent-memory/performance-analyst/MEMORY.md` plus TOML binding | replaced | semantic equivalent | Generated project memory contract for frame budgets, profiling baselines, memory ceilings, and known bottlenecks. | TOML binding scan; memory file exists. |
| `.claude/agents/qa-lead.md` `memory: project` | project | `.codex/agent-memory/qa-lead/MEMORY.md` plus TOML binding | replaced | semantic equivalent | Generated project memory contract for quality gates, test strategy, defect policy, and release criteria. | TOML binding scan; memory file exists. |
| `.claude/agents/systems-designer.md` `memory: project` | project | `.codex/agent-memory/systems-designer/MEMORY.md` plus TOML binding | replaced | semantic equivalent | Generated project memory contract for system taxonomy, dependencies, balance constraints, and design consistency rules. | TOML binding scan; memory file exists. |
| `.claude/agents/ux-designer.md` `memory: project` | project | `.codex/agent-memory/ux-designer/MEMORY.md` plus TOML binding | replaced | semantic equivalent | Generated project memory contract for UX patterns, accessibility choices, HUD conventions, and interaction decisions. | TOML binding scan; memory file exists. |
| `.claude/agents/world-builder.md` `memory: project` | project | `.codex/agent-memory/world-builder/MEMORY.md` plus TOML binding | replaced | semantic equivalent | Generated project memory contract for world rules, factions, locations, lore constraints, and setting continuity. | TOML binding scan; memory file exists. |
| `.claude/agents/writer.md` `memory: project` | project | `.codex/agent-memory/writer/MEMORY.md` plus TOML binding | replaced | semantic equivalent | Generated project memory contract for character voice, dialogue style, terminology, and narrative continuity. | TOML binding scan; memory file exists. |

## Template Mapping

All 40 upstream files under `.claude/docs/templates/**` are copied to `.codex/docs/templates/**` with the same relative path. Parity is exact unless the template text contains Claude command references, in which case those references are rewritten while preserving the artifact schema.

| Upstream template | Target | Disposition | Verification |
|---|---|---|---|
| `accessibility-requirements.md` | `.codex/docs/templates/accessibility-requirements.md` | ported | Manifest diff; content rewrite scan. |
| `architecture-decision-record.md` | `.codex/docs/templates/architecture-decision-record.md` | ported | Manifest diff; content rewrite scan. |
| `architecture-doc-from-code.md` | `.codex/docs/templates/architecture-doc-from-code.md` | ported | Manifest diff; content rewrite scan. |
| `architecture-traceability.md` | `.codex/docs/templates/architecture-traceability.md` | ported | Manifest diff; content rewrite scan. |
| `art-bible.md` | `.codex/docs/templates/art-bible.md` | ported | Manifest diff; content rewrite scan. |
| `changelog-template.md` | `.codex/docs/templates/changelog-template.md` | ported | Manifest diff; content rewrite scan. |
| `collaborative-protocols/design-agent-protocol.md` | `.codex/docs/templates/collaborative-protocols/design-agent-protocol.md` | ported | Manifest diff; content rewrite scan. |
| `collaborative-protocols/implementation-agent-protocol.md` | `.codex/docs/templates/collaborative-protocols/implementation-agent-protocol.md` | ported | Manifest diff; content rewrite scan. |
| `collaborative-protocols/leadership-agent-protocol.md` | `.codex/docs/templates/collaborative-protocols/leadership-agent-protocol.md` | ported | Manifest diff; content rewrite scan. |
| `concept-doc-from-prototype.md` | `.codex/docs/templates/concept-doc-from-prototype.md` | ported | Manifest diff; content rewrite scan. |
| `design-doc-from-implementation.md` | `.codex/docs/templates/design-doc-from-implementation.md` | ported | Manifest diff; content rewrite scan. |
| `difficulty-curve.md` | `.codex/docs/templates/difficulty-curve.md` | ported | Manifest diff; content rewrite scan. |
| `economy-model.md` | `.codex/docs/templates/economy-model.md` | ported | Manifest diff; content rewrite scan. |
| `faction-design.md` | `.codex/docs/templates/faction-design.md` | ported | Manifest diff; content rewrite scan. |
| `game-concept.md` | `.codex/docs/templates/game-concept.md` | ported | Manifest diff; content rewrite scan. |
| `game-design-document.md` | `.codex/docs/templates/game-design-document.md` | ported | Manifest diff; content rewrite scan. |
| `game-pillars.md` | `.codex/docs/templates/game-pillars.md` | ported | Manifest diff; content rewrite scan. |
| `hud-design.md` | `.codex/docs/templates/hud-design.md` | ported | Manifest diff; content rewrite scan. |
| `incident-response.md` | `.codex/docs/templates/incident-response.md` | ported | Manifest diff; content rewrite scan. |
| `interaction-pattern-library.md` | `.codex/docs/templates/interaction-pattern-library.md` | ported | Manifest diff; content rewrite scan. |
| `level-design-document.md` | `.codex/docs/templates/level-design-document.md` | ported | Manifest diff; content rewrite scan. |
| `milestone-definition.md` | `.codex/docs/templates/milestone-definition.md` | ported | Manifest diff; content rewrite scan. |
| `narrative-character-sheet.md` | `.codex/docs/templates/narrative-character-sheet.md` | ported | Manifest diff; content rewrite scan. |
| `pitch-document.md` | `.codex/docs/templates/pitch-document.md` | ported | Manifest diff; content rewrite scan. |
| `player-journey.md` | `.codex/docs/templates/player-journey.md` | ported | Manifest diff; content rewrite scan. |
| `post-mortem.md` | `.codex/docs/templates/post-mortem.md` | ported | Manifest diff; content rewrite scan. |
| `project-stage-report.md` | `.codex/docs/templates/project-stage-report.md` | ported | Manifest diff; content rewrite scan. |
| `prototype-report.md` | `.codex/docs/templates/prototype-report.md` | ported | Manifest diff; content rewrite scan. |
| `release-checklist-template.md` | `.codex/docs/templates/release-checklist-template.md` | ported | Manifest diff; content rewrite scan. |
| `release-notes.md` | `.codex/docs/templates/release-notes.md` | ported | Manifest diff; content rewrite scan. |
| `risk-register-entry.md` | `.codex/docs/templates/risk-register-entry.md` | ported | Manifest diff; content rewrite scan. |
| `skill-test-spec.md` | `.codex/docs/templates/skill-test-spec.md` | ported | Manifest diff; content rewrite scan. |
| `sound-bible.md` | `.codex/docs/templates/sound-bible.md` | ported | Manifest diff; content rewrite scan. |
| `sprint-plan.md` | `.codex/docs/templates/sprint-plan.md` | ported | Manifest diff; content rewrite scan. |
| `systems-index.md` | `.codex/docs/templates/systems-index.md` | ported | Manifest diff; content rewrite scan. |
| `technical-design-document.md` | `.codex/docs/templates/technical-design-document.md` | ported | Manifest diff; content rewrite scan. |
| `test-evidence.md` | `.codex/docs/templates/test-evidence.md` | ported | Manifest diff; content rewrite scan. |
| `test-plan.md` | `.codex/docs/templates/test-plan.md` | ported | Manifest diff; content rewrite scan. |
| `ux-spec.md` | `.codex/docs/templates/ux-spec.md` | ported | Manifest diff; content rewrite scan. |
| `vertical-slice-report.md` | `.codex/docs/templates/vertical-slice-report.md` | ported | Manifest diff; content rewrite scan. |

## Documentation and Config Asset Mapping

| Upstream files | Count | Target | Disposition | Parity | Notes | Verification |
|---|---:|---|---|---|---|---|
| `.claude/docs/*.md`, `.claude/docs/hooks-reference/*.md`, `.claude/docs/workflow-catalog.yaml` excluding templates | 23 | `.codex/docs/**` with rewritten runtime paths | ported | semantic equivalent | Includes `agent-coordination-map.md`, `agent-roster.md`, `coding-standards.md`, `context-management.md`, `coordination-rules.md`, `director-gates.md`, `directory-structure.md`, `hooks-reference*.md`, `quick-start.md`, `review-workflow.md`, `rules-reference.md`, `setup-requirements.md`, `skills-reference.md`, `technical-preferences.md`, `workflow-catalog.yaml`, plus local template docs. | Manifest path diff; YAML parse; no runtime `.claude` refs except provenance allowlist. |
| `README.md`, `UPGRADING.md`, `CONTRIBUTING.md`, `SECURITY.md` | 4 | `.codex/docs/README.md`, `.codex/docs/MIGRATION.md`, `.codex/docs/CONTRIBUTING.md`, `.codex/docs/SECURITY.md` | ported | semantic equivalent | Rewrite Claude invocation/install instructions to Codex; preserve upstream attribution. | Docs grep; link check. |
| `LICENSE` | 1 | `LICENSE` and `ATTRIBUTION.md` | shared/ported | exact | Preserve MIT license and source attribution. | License text present; attribution present. |
| `.gitignore` | 1 | Optional documented additions only | not applicable | not applicable | Do not overwrite a target game's `.gitignore`; installer may suggest Codex log/backups ignores. | Install fixture asserts `.gitignore` unchanged unless user opts in. |
| `.github/CODEOWNERS`, `.github/FUNDING.yml`, `.github/PULL_REQUEST_TEMPLATE.md`, issue templates | 5 | `docs/github/**` or optional distribution files | ported | semantic equivalent | Not runtime Codex assets; useful for source distribution and contribution docs. | Manifest coverage; no install overwrite by default. |
| `docs/COLLABORATIVE-DESIGN-PRINCIPLE.md`, `docs/WORKFLOW-GUIDE.md`, `docs/architecture/tr-registry.yaml`, `docs/registry/architecture.yaml` | 4 | same neutral paths under `docs/**` | shared | exact | These are project docs/data, not Claude runtime files. | Path existence; YAML parse. |
| `docs/engine-reference/**` | 46 | same neutral paths | shared | exact | Engine references remain shared for Claude and Codex workflows. | Count 46; path diff. |
| `docs/examples/**` | 11 | `docs/examples/**` or same neutral paths | ported | semantic equivalent | Rewrite command examples to upstream Codex skill names such as `start` and `prototype`. | Count 11; grep for bare Claude slash commands. |

## Testing Framework Mapping

Target root: `CCGS Skill Testing Framework/**`.

| Upstream testing asset | Count | Target | Disposition | Parity | Notes | Verification |
|---|---:|---|---|---|---|---|
| `CCGS Skill Testing Framework/README.md`, `catalog.yaml`, `quality-rubric.md` | 3 | same relative names under target root | ported | semantic equivalent | Rewrite Claude path/runtime references only. | Count/path diff; YAML parse. |
| `CCGS Skill Testing Framework/CLAUDE.md` | 1 | `CCGS Skill Testing Framework/AGENTS.md` or README section | replaced | semantic equivalent | Framework guidance becomes Codex instructions/docs. | No `.claude` dependency. |
| `CCGS Skill Testing Framework/agents/**/<agent>.md` | 49 | same relative tree under target root | ported | semantic equivalent | Agent spec names match all 49 upstream agents. | Agent-spec vs agent manifest diff. |
| `CCGS Skill Testing Framework/skills/**/<skill>.md` | 72 | same relative tree under target root | ported | semantic equivalent | Specs exist for all upstream skills except `vertical-slice`. | Skill-spec vs 73-skill manifest diff; inherited missing `vertical-slice` remains historical evidence. |
| Missing upstream `vertical-slice` skill spec | 1 expected spec absent upstream | `CCGS Skill Testing Framework/skills/utility/vertical-slice.md` | ported as Codex-added coverage | partial | Upstream gap, not a Codex conversion miss. This port adds a clearly labeled Codex spec covering PROCEED/PIVOT/KILL expectations. | Validation includes the Codex-added spec while upstream inventory remains historical evidence of the inherited gap. |
| `CCGS Skill Testing Framework/templates/agent-test-spec.md`, `skill-test-spec.md` | 2 | same relative names under target root | ported | semantic equivalent | Rewrite command examples to Codex naming. | Count/path diff. |

## Shared Lifecycle and Install Mapping

| Behavior/component | Upstream behavior | Claude mechanism | Codex target mechanism | Target | Disposition | Parity | Verification |
|---|---|---|---|---|---|---|---|
| Phase/stage state | Tracks project lifecycle phase | Shared files read by Claude skills/hooks/statusline | Same neutral files read by Codex skills/hooks | `production/stage.txt`, `production/review-mode.txt`, `production/session-state/active.md` | shared | exact | Byte-level fixture; no Codex namespace fork. |
| Review gates | Gate readiness and director verdicts | Skills plus director docs | `gate-check`, `review-all-gdds`, high-tier agents | Skills/agents plus `docs/director-gates.md` | ported | semantic equivalent | Smoke gate workflow; verdict token check. |
| Delegation model | Team/role routing | Claude `Task` to named agents | Codex custom agents with upstream role names | `.codex/agents/*.toml` plus skill rewrites | ported | semantic equivalent | Role reference resolver; sample subagent smoke. |
| Structured choices | Guided option questions | Claude `AskUserQuestion` | Numbered natural-language choices; optional MCP later | Skill bodies | replaced | partial | Grep `AskUserQuestion`; interactive workflow review. |
| Slash-command workflows | `/start`, `/brainstorm`, etc. | Claude slash commands via skills | Codex skills named `start`, `brainstorm`, etc. | `.agents/skills/<skill>/SKILL.md` | replaced | semantic equivalent | Grep for bare custom slash commands; skill selector smoke plus collision audit. |
| Install/upgrade | Upstream is a Claude template, not coexistence installer | Manual clone/template | Idempotent Codex installer/uninstaller | `.codex/install.sh`, `uninstall.sh`, `audit.sh`, manifests | new Codex-native support | new support | Fixture install/uninstall; hash `.claude/**`, `CLAUDE.md`, shared state. |
| Optional plugin package | Not upstream behavior | none | Optional later package | optional `.codex-plugin/plugin.json` | not applicable for base port | not applicable | Base validation must not depend on plugin cache/marketplace. |
| MCP | Not upstream behavior | none | Optional only for elicitation or external services | none by default | not applicable | not applicable | No MCP config unless a future phase adds a documented rationale. |

## Phase 4 Validation Hooks From This Matrix

Phase 4 must turn this matrix into checks for:
- 417 upstream files categorized by manifest.
- 49 generated custom agent TOML files.
- 73 ported skills plus 4 new Codex-native support skills: `studio-status`, `studio-next`, `handoff`, and `resume-from-handoff`.
- 11 ported hook scripts plus `notify.sh` replaced by native notification setup documentation.
- 15 root-routed Codex path-rule documents, including the 11 upstream rule mappings.
- 40 copied templates.
- 127 upstream testing-framework assets plus 1 Codex-added skill spec for `vertical-slice`.
- Zero runtime dependency on `.claude/`, `CLAUDE.md`, or bare upstream slash commands.
