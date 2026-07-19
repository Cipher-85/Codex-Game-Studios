# Corrected Codex Architecture - Phase 3

Phase 3 status: complete.

This architecture supersedes the target layout in `PLAN.md` where the GLM plan conflicts with verified upstream inventory or current Codex mechanisms.

## Architecture Verdict

Use repo-local loose files as the base distribution. Do not make plugin packaging the primary port mechanism.

Rationale:
- The primary requirement is coexistence inside one game project with the Claude version. Loose files let the Codex runtime own `.codex/`, `.agents/`, and marker-managed `AGENTS.md` / docs blocks without touching `.claude/` or `CLAUDE.md`.
- Codex plugins are verified and useful for later distribution, but plugin installation writes to the user's Codex home/cache and has trust/marketplace behavior outside the target game repo. That is not the simplest coexistence base.
- The local cached `codex-game-studios` plugin is not authoritative; `codex plugin list` currently fails because this workspace lacks a supported marketplace manifest.

## Ownership Boundaries

Claude-owned paths:
- `.claude/**`
- `CLAUDE.md`
- Claude hook/settings behavior

Codex-owned paths:
- Root `AGENTS.md` CCGS marker block only, or the whole file only if created by the installer.
- Nested `AGENTS.md` CCGS marker blocks in rule-scope directories.
- `.agents/skills/<upstream-skill>/**` and `.agents/skills/studio-status/**`
- `.codex/agents/<upstream-agent>.toml`
- `.codex/agent-memory/<upstream-memory-agent>/MEMORY.md`
- `.codex/hooks/**`
- `.codex/rules/settings.rules`
- `.codex/hooks.json` only if absent or generated/merged by the installer with explicit ownership.
- `.codex/config.toml` only if absent or generated/merged by the installer with explicit ownership.
- `.codex/**`
- `production/session-logs/**` for Codex-only logs/handoffs
- `ATTRIBUTION.md` marker block or whole file if created by installer

Shared neutral studio paths:
- `production/stage.txt`
- `production/review-mode.txt`
- `production/session-state/active.md`
- `production/sprints/**`
- `production/milestones/**`
- `production/epics/**`
- `production/qa/**`
- `production/gate-checks/**`
- `production/playtests/**`
- `design/**`
- `docs/**`
- `docs/architecture/**`
- `docs/engine-reference/**`
- `src/**`
- `tests/**`
- `prototypes/**`

Shared neutral paths are intentionally shared with Claude. Installer and uninstaller must not remove them.

## Target Layout

```text
<game-project>/
├── AGENTS.md
├── src/
│   ├── ai/AGENTS.md
│   ├── core/AGENTS.md
│   ├── gameplay/AGENTS.md
│   ├── networking/AGENTS.md
│   └── ui/AGENTS.md
├── design/
│   ├── gdd/AGENTS.md
│   └── narrative/AGENTS.md
├── assets/
│   ├── data/AGENTS.md
│   └── shaders/AGENTS.md
├── prototypes/AGENTS.md
├── tests/AGENTS.md
├── .agents/
│   └── skills/
│       ├── adopt/SKILL.md
│       ├── architecture-decision/SKILL.md
│       ├── ... 73 upstream skills total ...
│       └── studio-status/SKILL.md
├── .codex/
│   ├── config.toml
│   ├── hooks.json
│   ├── rules/
│   │   └── settings.rules
│   ├── agents/
│   │   ├── accessibility-specialist.toml
│   │   ├── ... 49 upstream agents total ...
│   │   └── writer.toml
│   ├── agent-memory/
│   │   ├── art-director/MEMORY.md
│   │   ├── ... 17 upstream memory-scoped agents total ...
│   │   └── writer/MEMORY.md
│   ├── hooks/
│   │   ├── detect-gaps.sh
│   │   ├── ... converted hook scripts ...
│   │   └── studio-status-on-start.sh
│   ├── docs/
│   │   ├── README.md
│   │   ├── MIGRATION.md
│   │   ├── COEXISTENCE.md
│   │   ├── agent-coordination-map.md
│   │   ├── workflow-catalog.yaml
│   │   ├── ... rewritten upstream .claude/docs assets ...
│   │   └── templates/
│   │       └── ... 40 upstream templates ...
│   ├── install.sh
│   ├── uninstall.sh
│   ├── audit.sh
│   ├── models.toml
│   ├── manifest/
│   │   ├── upstream-assets.json
│   │   └── installed-files.json
│   ├── lib/
│   │   ├── agents.sh
│   │   ├── hooks.sh
│   │   ├── install.sh
│   │   ├── state.sh
│   │   └── validate.sh
│   ├── tests/
│   │   └── fixtures/
│   └── backups/
├── docs/
│   ├── WORKFLOW-GUIDE.md
│   ├── COLLABORATIVE-DESIGN-PRINCIPLE.md
│   ├── architecture/
│   ├── engine-reference/
│   ├── examples/
│   └── registry/
├── CCGS Skill Testing Framework/
│   ├── AGENTS.md
│   └── ... upstream testing framework assets ...
├── production/
│   ├── stage.txt
│   ├── review-mode.txt
│   ├── session-state/active.md
│   └── session-logs/
├── ATTRIBUTION.md
└── LICENSE
```

## Installation Collision Policy

Default installer behavior:
- Refuse to modify `.claude/**` or `CLAUDE.md`.
- Refuse to overwrite any existing Codex-owned target file that does not contain a CCGS ownership marker and is not listed in `.codex/manifest/installed-files.json`.
- Create new files with CCGS ownership markers where the format permits comments.
- For existing Markdown instruction files such as `AGENTS.md`, append or update a marker-managed block:

```markdown
<!-- BEGIN CCGS -->
...
<!-- END CCGS -->
```

- For JSON/TOML files where marker blocks are not safe, use structured merge only when the file is absent or previously owned. Otherwise refuse and print the exact manual merge requirement.
- Write `.codex/manifest/installed-files.json` with file path, ownership mode (`whole-file` or `marker-block`), and preinstall hash for every Codex-owned path.

`--force` behavior:
- May overwrite Codex-owned paths only after creating timestamped backups under `.codex/backups/<timestamp>/`.
- Must still refuse `.claude/**`, `CLAUDE.md`, and shared neutral state deletion.

Uninstaller behavior:
- Remove only files or marker blocks listed in the install manifest.
- Delete empty directories only if they are Codex-owned and empty after removal.
- Preserve shared neutral state under `production/`, `design/`, `docs/architecture/`, `docs/engine-reference/`, `src/`, `tests/`, and `prototypes/`.

## Instruction Architecture

Root `AGENTS.md`:
- If absent, create it with a CCGS marker block.
- If present, append or update only the CCGS marker block.
- Include the core studio protocol, phase lifecycle, shared state paths, and "run the `start` skill" onboarding instruction.
- Do not use `@` imports. Codex has no verified import syntax.
- Keep the root block compact enough to stay under `project_doc_max_bytes` when combined with common project instructions. Detailed docs live under `docs/` and are referenced by skills.

Nested `AGENTS.md`:
- Convert all 11 upstream `.claude/rules/*.md` path-scoped rules to directory-local Codex instructions.
- Use the most specific matching directory:
  - `.claude/rules/ai-code.md` -> `src/ai/AGENTS.md`
  - `.claude/rules/data-files.md` -> `assets/data/AGENTS.md`
  - `.claude/rules/design-docs.md` -> `design/gdd/AGENTS.md`
  - `.claude/rules/engine-code.md` -> `src/core/AGENTS.md`
  - `.claude/rules/gameplay-code.md` -> `src/gameplay/AGENTS.md`
  - `.claude/rules/narrative.md` -> `design/narrative/AGENTS.md`
  - `.claude/rules/network-code.md` -> `src/networking/AGENTS.md`
  - `.claude/rules/prototype-code.md` -> `prototypes/AGENTS.md`
  - `.claude/rules/shader-code.md` -> `assets/shaders/AGENTS.md`
  - `.claude/rules/test-standards.md` -> `tests/AGENTS.md`
  - `.claude/rules/ui-code.md` -> `src/ui/AGENTS.md`

## Skill Architecture

Target:
- `.agents/skills/<skill>/SKILL.md`

Naming:
- Use the upstream skill name unchanged for repo-local loose-file skills: folder `.agents/skills/start/`, frontmatter `name: start`, and equivalent for all 73 upstream skills.
- Preserve upstream invocation ergonomics. Users should be able to run `$start` / the `start` skill instead of a prefixed variant.
- Rationale: official docs verify repo skills are discovered from direct skill folders under `.agents/skills`; a nested namespace folder is not a verified discovery mechanism. Same-name skills are not merged by documented behavior, so the port must validate and report collisions instead of assuming project skills suppress user/system skills.
- Optional plugin packaging can later expose plugin-namespaced display names such as `start`, but the base port must be executable as loose repo files.

Conversion rules:
- Preserve all 73 upstream skills.
- Add deliberate Codex-native support skills only when they cover a Codex-specific workflow gap, such as `studio-status` for status breadcrumbs, `studio-next` for continuity routing, and the `$handoff` / `$resume-from-handoff` pair for durable session continuity.
- `skill-test` is ported from upstream, not new.
- Keep required Codex frontmatter: `name`, `description`.
- Move Claude-only metadata (`argument-hint`, `user-invocable`, `allowed-tools`, `model`) into a "Ported metadata" section in the body where useful.
- Rewrite `Task` delegation to Codex subagent delegation.
- Rewrite `AskUserQuestion` to numbered natural-language choices unless a deliberate MCP elicitation implementation is added.
- Rewrite `/skill` references to `run the `<skill>` skill` or `$<skill>` where that is the clearest Codex invocation surface. Optional plugin docs may also mention a future namespaced invocation surface.
- Add a skill-collision audit. If an active same-name non-CCGS skill is detected, the installer/validator must report the competing path(s) and tell the user to disable by exact path or accept selector ambiguity; it must not silently rename CCGS skills.
- Rewrite `.claude/` references to `docs/` or shared neutral paths.
- Preserve shared artifact paths in `production/`, `design/`, and `docs/architecture/`.

## Subagent Architecture

Target:
- `.codex/agents/<upstream-agent>.toml`

Schema:
- Required: `name`, `description`, `developer_instructions`.
- Optional: `model`, `model_reasoning_effort`, and only verified config fields.
- Avoid unsupported direct translations such as Claude `maxTurns`.
- Use direct project-scoped agent files under `.codex/agents/`, because official docs describe standalone TOML files there. Preserve upstream hyphenated agent names as both the filename stem and `name`, for example `.codex/agents/producer.toml` with `name = "producer"`.
- Add a custom-agent collision audit. Current documented Codex built-ins are `default`, `worker`, and `explorer`; if a target project or user config has a same-name custom agent, the installer must report/refuse rather than silently prefixing the CCGS agent.

Model mapping:
- `opus` -> `gpt-5.5`, `model_reasoning_effort = "high"` by default.
- `sonnet` -> `gpt-5.4`, `model_reasoning_effort = "medium"` by default.
- `haiku` -> `gpt-5.4-mini`, `model_reasoning_effort = "low"` by default.
- Keep this mapping in `.codex/models.toml` so users can rebind tiers.
- Phase 4 validation must compare generated model slugs against `codex debug models`.

## Agent Memory Architecture

Verified upstream memory scopes:
- `memory: user`: `creative-director`, `technical-director`, `producer`
- `memory: project`: `art-director`, `audio-director`, `economy-designer`, `game-designer`, `lead-programmer`, `level-designer`, `localization-lead`, `narrative-director`, `performance-analyst`, `qa-lead`, `systems-designer`, `ux-designer`, `world-builder`, `writer`

Upstream explicit memory files:
- `.claude/agent-memory/lead-programmer/MEMORY.md`

Codex target:
- `.codex/agent-memory/<agent>/MEMORY.md` for all 17 memory-scoped upstream agents.
- `lead-programmer/MEMORY.md` is a rewritten port of the upstream explicit memory file.
- The other 16 files are generated memory-contract files that preserve the upstream memory scope and define what durable repo-local context that role should consult or maintain. They must be clearly labeled as generated Codex memory contracts, not copied historical upstream memory.

Binding rule:
- Each corresponding `.codex/agents/<agent>.toml` must instruct the custom agent to read `.codex/agent-memory/<agent>/MEMORY.md` before role work, and especially before skill authoring, design/architecture rulings, production planning, review gates, and canonical path decisions.
- The agent TOML must include `Ported Claude memory scope: user` or `Ported Claude memory scope: project`.
- The installer must not write to `~/.codex/memories`; global Codex Memories are optional user-controlled behavior, not part of the repo-contained port.

Partial mappings:
- Claude `tools` and `disallowedTools` become instructions plus project command rules/hooks. No exact per-agent tool allow/deny parity is claimed.
- Claude `memory` has no direct documented Codex per-agent binding. Preserve every upstream `memory: user` or `memory: project` declaration in the generated agent instructions, create a repo-local `.codex/agent-memory/<agent>/MEMORY.md` file for each memory-scoped agent, and instruct each corresponding custom agent to read that file before role work. The installer must not write global Codex memories under `~/.codex/memories`.
- Claude `skills` become explicit role guidance. Only use Codex skill config after schema validation.
- Claude `isolation: worktree` becomes explicit worktree instructions for `prototyper`, `prototype`, and `vertical-slice`, with optional helper scripts.

## Hook and Config Architecture

Hooks:
- Primary hook wiring file: `.codex/hooks.json`.
- Hook scripts: `.codex/hooks/*.sh`.
- Supported event mappings:
  - `SessionStart`: `session-start.sh`, `detect-gaps.sh`, `studio-status-on-start.sh`
  - `PreToolUse` with matcher `Bash`: `validate-commit.sh`, `validate-push.sh`
  - `PreToolUse` with matcher `apply_patch|Edit|Write`: preflight asset validation where feasible
  - `PostToolUse` with matcher `apply_patch|Edit|Write`: advisory asset and skill validation
  - `PreCompact`: `pre-compact.sh`
  - `PostCompact`: `post-compact.sh`
  - `Stop`: `session-stop.sh`
  - `SubagentStart`: `log-agent.sh`
  - `SubagentStop`: `log-agent-stop.sh`
- Claude's `Notification` hook is not installed as a Codex hook because Codex has no matching lifecycle hook event. Preserve the behavior through documentation for native Codex notifications: user-level `notify`, `[tui].notifications`, `[tui].notification_method`, and `[tui].notification_condition`.

Permissions:
- Use Codex permission profiles as the primary config model.
- `.codex/config.toml` should define:
  - `default_permissions = "game_studios"` only when safe to set in an owned config.
  - `[permissions.game_studios] extends = ":workspace"`.
  - Explicit write rules for `.git`, `.agents`, and `.codex`; upstream permits
    ordinary Git and runtime-maintenance workflows, so inherited read-only
    carve-outs are not parity.
  - Deny sensitive env paths.
  - Network disabled by default unless a user explicitly enables it.
- Do not force a project-local `approval_policy`. Approval routing is
  user/session-owned; local staging and commits must work without escalation,
  while networked pushes follow the active session policy.
- Do not set `sandbox_mode` in the same distributable config when permission profiles are used.

Command rules:
- Use `.codex/rules/settings.rules` for allow/prompt/forbidden command prefix rules.
- Include inline `match` and `not_match` examples for destructive operations.
- Deny or prompt for:
  - `rm -rf`
  - `git push --force`
  - `git push -f`
  - `git reset --hard`
  - `git clean -f`
  - `sudo`
  - `chmod 777`
  - shell reads/writes of `.env` files where enforceable

Trust:
- Project `.codex/` config, hooks, and rules load only when the project is trusted.
- Installer and docs must include a trust verification step.
- CI/headless validation may use `--dangerously-bypass-hook-trust` only in a documented fixture after validating hook sources.

## Status and Lifecycle Architecture

Preserve exact shared lifecycle state:
- `production/stage.txt`
- `production/review-mode.txt`
- `production/session-state/active.md`
- `<!-- STATUS -->` block with `Epic:`, `Feature:`, and `Task:`

Port Claude statusline behavior through the closest Codex-native surfaces:
- `.codex/config.toml` `[tui].status_line` to preserve built-in footer items for model and context visibility. The default target should include Codex-supported item IDs such as `model-with-reasoning`, `context-remaining`, and `current-dir`, unless a target project already owns a different footer configuration.
- `SessionStart` hook `studio-status-on-start.sh`, which reads the same shared lifecycle state and adds current studio status as context.
- `studio-status` skill for on-demand stage/review/session breadcrumb rendering.

Known parity boundary:
- Claude supports `statusLine.command = "bash .claude/statusline.sh"` and can render arbitrary project state directly in the footer. The verified Codex surface is a built-in item list, not a project script footer item. Therefore model/context footer parity is native, while an actual footer `Stage:` item is blocked until Codex exposes a documented project custom footer item. The game-stage breadcrumb is preserved through context and skill output in the meantime.

Lifecycle parity:
- Preserve phases: concept, systems-design, technical-setup, pre-production, production, polish, release.
- Preserve review modes: full, lean, solo.
- Preserve director gate verdict tokens and "strictest verdict wins" semantics.
- Preserve director -> lead -> specialist delegation model through Codex subagents.

## Documentation and Templates Architecture

Neutral docs:
- Copy upstream `.claude/docs` content that skills or instructions need into `.codex/docs/`.
- Preserve upstream root `docs/**` as shared neutral project docs at `docs/**`.
- Rewrite runtime references away from `.claude/`.
- Keep provenance in `ATTRIBUTION.md` and `.codex/docs/MIGRATION.md`.

Templates:
- Copy all 40 files from `.claude/docs/templates/` to `.codex/docs/templates/`.
- Preserve subdirectories such as `collaborative-protocols/`.
- Account for template-like files outside that directory separately:
  - `.claude/docs/settings-local-template.md`
  - `.claude/docs/CLAUDE-local-template.md`
  - `CCGS Skill Testing Framework/templates/agent-test-spec.md`
  - `CCGS Skill Testing Framework/templates/skill-test-spec.md`

Testing framework:
- Port `CCGS Skill Testing Framework/**` to `CCGS Skill Testing Framework/**`.
- Preserve 49 agent specs and 72 upstream skill specs.
- Add a clearly labeled Codex-only `vertical-slice` skill spec to close coverage for PROCEED/PIVOT/KILL verdict behavior while preserving the upstream inventory as historical evidence of the inherited gap.

## Optional Plugin Package

Do not make plugin packaging part of the required port.

If added later:
- Use `.codex-plugin/plugin.json`.
- Bundle `skills/`, optional `hooks/`, and `assets/`.
- Provide a valid marketplace at `.agents/plugins/marketplace.json` if local install is required.
- Do not replace the loose-file installer unless the user explicitly chooses plugin distribution.

## Acceptance Criteria for Architecture

- No target path writes to `.claude/**`.
- No target path requires editing `CLAUDE.md`.
- All Codex-owned files use direct Codex-native paths, upstream-faithful shared paths, or marker-managed blocks with collision checks.
- All shared state is explicitly listed and preserved by uninstall.
- Every upstream agent, skill, hook, rule, template, config, lifecycle behavior, and doc category has a target disposition in `codex-mapping-matrix.md`.
- Every partial mapping has a risk entry in `risk-register.md`.
