# Codex-Native CCGS Implementation Plan

Phase 5 status: complete.

This is the executable plan for implementing the Codex-native port of `Donchitos/Claude-Code-Game-Studios` from pinned upstream commit `984023ddac0d5e27624f2baacde6105e45de375f`.

> Shipped-architecture correction (2026-07-12): the original Phase 3 nested
> `AGENTS.md` tasks below are historical planning evidence, not the current
> implementation contract. The shipped port keeps root `AGENTS.md` as the
> canonical router into `.codex/instructions/path-rules/*.md`. Nested
> instructions load from the session root-to-CWD chain and therefore do not
> reproduce upstream per-edited-file rule triggering for root-launched sessions.

Do not implement from `PLAN.md` directly. Use these artifacts as the source of truth:
- `docs/codex-conversion/upstream-inventory.md`
- `docs/codex-conversion/glm-plan-review.md`
- `docs/codex-conversion/corrected-architecture.md`
- `docs/codex-conversion/codex-mapping-matrix.md`
- `docs/codex-conversion/validation-suite.md`
- `docs/codex-conversion/risk-register.md`

## Non-Negotiable Constraints

- Do not write to or depend on `.claude/**`.
- Do not change or require `CLAUDE.md`.
- Do not read the local cached `codex-game-studios` plugin as source material.
- Use loose repo-local Codex files as the base distribution; plugin packaging is optional future work.
- Use direct repo skill paths with upstream names: `.agents/skills/<skill>/SKILL.md`.
- Use direct custom-agent paths with upstream names: `.codex/agents/<agent>.toml`.
- Keep Claude and Codex able to coexist in one game project.
- Default validation must be static/headless and pass without an LLM call.

## Target File Sets

Agent targets under `.codex/agents/`:
`accessibility-specialist.toml`, `ai-programmer.toml`, `analytics-engineer.toml`, `art-director.toml`, `audio-director.toml`, `community-manager.toml`, `creative-director.toml`, `devops-engineer.toml`, `economy-designer.toml`, `engine-programmer.toml`, `game-designer.toml`, `gameplay-programmer.toml`, `godot-csharp-specialist.toml`, `godot-gdextension-specialist.toml`, `godot-gdscript-specialist.toml`, `godot-shader-specialist.toml`, `godot-specialist.toml`, `lead-programmer.toml`, `level-designer.toml`, `live-ops-designer.toml`, `localization-lead.toml`, `narrative-director.toml`, `network-programmer.toml`, `performance-analyst.toml`, `producer.toml`, `prototyper.toml`, `qa-lead.toml`, `qa-tester.toml`, `release-manager.toml`, `security-engineer.toml`, `sound-designer.toml`, `systems-designer.toml`, `technical-artist.toml`, `technical-director.toml`, `tools-programmer.toml`, `ue-blueprint-specialist.toml`, `ue-gas-specialist.toml`, `ue-replication-specialist.toml`, `ue-umg-specialist.toml`, `ui-programmer.toml`, `unity-addressables-specialist.toml`, `unity-dots-specialist.toml`, `unity-shader-specialist.toml`, `unity-specialist.toml`, `unity-ui-specialist.toml`, `unreal-specialist.toml`, `ux-designer.toml`, `world-builder.toml`, `writer.toml`.

Agent memory targets under `.codex/agent-memory/`:
`art-director/MEMORY.md`, `audio-director/MEMORY.md`, `creative-director/MEMORY.md`, `economy-designer/MEMORY.md`, `game-designer/MEMORY.md`, `lead-programmer/MEMORY.md`, `level-designer/MEMORY.md`, `localization-lead/MEMORY.md`, `narrative-director/MEMORY.md`, `performance-analyst/MEMORY.md`, `producer/MEMORY.md`, `qa-lead/MEMORY.md`, `systems-designer/MEMORY.md`, `technical-director/MEMORY.md`, `ux-designer/MEMORY.md`, `world-builder/MEMORY.md`, `writer/MEMORY.md`.

Skill targets under `.agents/skills/`:
`adopt`, `architecture-decision`, `architecture-review`, `art-bible`, `asset-audit`, `asset-spec`, `balance-check`, `brainstorm`, `bug-report`, `bug-triage`, `changelog`, `code-review`, `consistency-check`, `content-audit`, `create-architecture`, `create-control-manifest`, `create-epics`, `create-stories`, `day-one-patch`, `design-review`, `design-system`, `dev-story`, `estimate`, `gate-check`, `help`, `hotfix`, `launch-checklist`, `localize`, `map-systems`, `milestone-review`, `onboard`, `patch-notes`, `perf-profile`, `playtest-report`, `project-stage-detect`, `propagate-design-change`, `prototype`, `qa-plan`, `quick-design`, `regression-suite`, `release-checklist`, `retrospective`, `reverse-document`, `review-all-gdds`, `scope-check`, `security-audit`, `setup-engine`, `skill-improve`, `skill-test`, `smoke-check`, `soak-test`, `sprint-plan`, `sprint-status`, `start`, `story-done`, `story-readiness`, `team-audio`, `team-combat`, `team-level`, `team-live-ops`, `team-narrative`, `team-polish`, `team-qa`, `team-release`, `team-ui`, `tech-debt`, `test-evidence-review`, `test-flakiness`, `test-helpers`, `test-setup`, `ux-design`, `ux-review`, `vertical-slice`, plus new `studio-status`.

Hook/status targets:
`.codex/hooks/session-start.sh`, `detect-gaps.sh`, `validate-commit.sh`, `validate-push.sh`, `validate-assets.sh`, `validate-skill-change.sh`, `pre-compact.sh`, `post-compact.sh`, `log-agent.sh`, `log-agent-stop.sh`, `session-stop.sh`, and new `studio-status-on-start.sh`. Do not install `notify.sh` as a project hook; replace its behavior with native Codex notification setup docs. Configure built-in footer status items through `.codex/config.toml` `[tui].status_line` when safe.

Nested instruction targets:
`AGENTS.md`, `src/AGENTS.md`, `design/AGENTS.md`, `docs/AGENTS.md`, `src/ai/AGENTS.md`, `assets/data/AGENTS.md`, `design/gdd/AGENTS.md`, `src/core/AGENTS.md`, `src/gameplay/AGENTS.md`, `design/narrative/AGENTS.md`, `src/networking/AGENTS.md`, `prototypes/AGENTS.md`, `assets/shaders/AGENTS.md`, `tests/AGENTS.md`, `src/ui/AGENTS.md`.

## Phase 1 - Source Manifest and Conversion Inputs

Goal: create durable source-of-truth manifests before generating runtime assets.

Files to create:
- `.codex/manifest/upstream-assets.json`
- `.codex/manifest/expected-targets.json`
- `.codex/models.toml`
- `.codex/README.md`

Tasks:
- Build `upstream-assets.json` from pinned upstream commit `984023ddac0d5e27624f2baacde6105e45de375f`.
- Include all 417 files with `path`, `sha256`, `category`, `disposition`, `parity`, `target`, and `rationale`.
- Build `expected-targets.json` from `codex-mapping-matrix.md`.
- Add model tier mappings in `models.toml`: `opus = gpt-5.5/high`, `sonnet = gpt-5.4/medium`, `haiku = gpt-5.4-mini/low`.
- Record that `notify.sh` is replaced by native Codex notification setup documentation, and missing `vertical-slice` framework spec is a known upstream gap.

Verification commands:
- `python3 .codex/lib/validate_manifest.py --root "$PWD"`
- `./.codex/audit.sh manifest --root "$PWD"` after the audit dispatcher exists.
- `codex debug models > /tmp/game-studios-models.json` as optional model slug check.

Acceptance criteria:
- Manifest has exactly 417 upstream rows.
- Counts match the Phase 3 matrix.
- No row has empty disposition/parity/rationale.

Rollback/coexistence:
- Manifest creation must not touch target project runtime files.
- Never use `/private/tmp` as the long-term source of truth after this manifest exists.

## Phase 2 - Validation Harness First

Goal: make the port testable before broad generation.

Files to create:
- `.codex/audit.sh`
- `.codex/lib/validate_manifest.py`
- `.codex/lib/validate_runtime.py`
- `.codex/lib/validate_hooks.py`
- `.codex/lib/validate_rules.py`
- `.codex/lib/validate_install.py`
- `.codex/lib/validate_smoke.py`
- `.codex/tests/fixtures/empty-game/**`
- `.codex/tests/fixtures/claude-existing/**`
- `.codex/tests/fixtures/codex-collisions/**`
- `.codex/tests/fixtures/shared-state-dirty/**`
- `.codex/tests/fixtures/hook-payloads/**`

Tasks:
- Implement `audit.sh` as a thin dispatcher for `all`, `manifest`, `runtime`, `skills`, `agents`, `config`, `hooks`, `coexistence`, `smoke-headless`, and `smoke-interactive`.
- Use only Python standard library modules for validators.
- Emit JSON and concise human output.
- Return exit code `0` for pass, `1` for validation failures, `2` for setup/tool errors.
- Add negative fixtures for invalid skill metadata, invalid agent TOML, stale `.claude` references, and config collisions.

Verification commands:
- `./.codex/audit.sh manifest --root "$PWD"`
- `./.codex/audit.sh runtime --root "$PWD"`
- `./.codex/audit.sh all --root "$PWD"`

Acceptance criteria:
- Validators fail on seeded bad fixtures and pass on empty or expected-good fixtures.
- No validator imports `yaml` or any non-stdlib module.

Rollback/coexistence:
- Validators must never modify project files unless running explicit install/uninstall fixture tests in temp copies.

## Phase 3 - Instructions, Rules, and Shared Docs

Historical note: this phase originally specified nested `AGENTS.md` targets.
The implemented router architecture described above supersedes those target
paths and is validated by the root router table and path-rule chain checks.

Goal: port root/nested instructions and neutral documentation without depending on Claude files.

Files to create/modify:
- Marker block in root `AGENTS.md`
- Marker blocks in all nested instruction targets listed above
- `.codex/docs/README.md`
- `.codex/docs/MIGRATION.md`
- `.codex/docs/COEXISTENCE.md`
- `.codex/docs/**`
- `.codex/docs/templates/**`
- `docs/**`
- `CCGS Skill Testing Framework/**`
- `ATTRIBUTION.md`

Tasks:
- Convert root `CLAUDE.md` guidance into a compact CCGS marker block in `AGENTS.md`; do not use imports.
- Convert `src/CLAUDE.md`, `design/CLAUDE.md`, `docs/CLAUDE.md`, and framework `CLAUDE.md` to Codex instructions/docs.
- Convert all 11 `.claude/rules/*.md` files to nested `AGENTS.md` marker blocks.
- Copy all 40 `.claude/docs/templates/**` templates to `.codex/docs/templates/**`, preserving the exact relative structure including `collaborative-protocols/**`.
- Copy the 23 `.claude/docs` non-template files to `.codex/docs/**` with runtime paths rewritten.
- Preserve upstream root/shared `docs/**` at direct `docs/**`; do not mix migrated `.claude/docs` assets into root `docs/templates/**`.
- Copy the 127 testing-framework assets to `CCGS Skill Testing Framework/**`; preserve the missing `vertical-slice` spec as a documented upstream gap unless adding a clearly labeled new Codex spec.
- Preserve MIT attribution.

Verification commands:
- `./.codex/audit.sh manifest --root "$PWD"`
- `./.codex/audit.sh runtime --root "$PWD"`
- `./.codex/audit.sh docs --root "$PWD"` if implemented as separate alias.
- `codex --strict-config -C "$fixture" debug prompt-input "noop"` optional prompt-input check.

Acceptance criteria:
- 11 nested rule targets exist.
- 40 templates exist.
- 127 testing-framework assets exist.
- Runtime docs have no forbidden `.claude/`, `CLAUDE.md`, or bare custom slash-command dependencies.

Rollback/coexistence:
- Existing `AGENTS.md` files are marker-merged, not overwritten.
- Uninstaller must remove only CCGS marker blocks, not unrelated instructions.

## Phase 4 - Custom Agents

Goal: port all 49 upstream role agents to Codex custom-agent TOML.

Files to create:
- The 49 `.codex/agents/<upstream-agent>.toml` files listed in Target File Sets.
- The 17 `.codex/agent-memory/<agent>/MEMORY.md` files listed in Target File Sets.

Tasks:
- Convert each upstream agent prompt into `developer_instructions`.
- Set `name = "<upstream-agent-name>"`, preserving the upstream hyphenated role name.
- Include the same upstream role name in `description`.
- Map model tiers from `models.toml`.
- Preserve pinned skill affinities as instructions, not unverified `skills.config`.
- Preserve every upstream `memory: user` and `memory: project` declaration. Add `Ported Claude memory scope: user` or `Ported Claude memory scope: project` to the relevant agent instructions.
- Port `.claude/agent-memory/lead-programmer/MEMORY.md` to `.codex/agent-memory/lead-programmer/MEMORY.md` and rewrite Claude paths/metadata expectations to Codex paths.
- Generate memory contract files for the other 16 memory-scoped agents under `.codex/agent-memory/<agent>/MEMORY.md`. Label these files as generated Codex memory contracts, not copied historical upstream memory.
- In every memory-scoped agent TOML, instruct the agent to read `.codex/agent-memory/<agent>/MEMORY.md` before role work, including design/architecture rulings, production planning, review gates, skill authoring, and canonical path decisions.
- Do not write global Codex memories under `~/.codex/memories`; global Codex Memories are optional user-controlled behavior only.
- Convert `prototyper` worktree isolation into explicit worktree workflow instructions.
- Add a custom-agent collision check against existing project/user agent TOML and documented built-ins; report/refuse collisions instead of renaming.
- Do not include unsupported top-level TOML fields: `tools`, `disallowedTools`, `maxTurns`, `memory`, `skills`, `isolation`.

Verification commands:
- `./.codex/audit.sh agents --root "$PWD"`
- `./.codex/audit.sh runtime --root "$PWD"`
- `codex debug models > /tmp/game-studios-models.json` optional.

Acceptance criteria:
- Exactly 49 TOML files parse.
- Exactly 17 repo-local memory files exist and every memory-scoped agent references its own file.
- Model distribution is 3 high, 44 medium, 2 low.
- All role references used by skills resolve to generated agent names.
- No installer, hook, or generated runtime file writes to `~/.codex/memories`.

Rollback/coexistence:
- Existing unowned `.codex/agents/*.toml` files must not be overwritten.
- Avoid any nested namespace layout under `.codex/agents/`; custom-agent files must be direct children.

## Phase 5 - Skills

Goal: port all 73 upstream skills plus one Codex-native status skill.

Files to create:
- 73 `.agents/skills/<upstream-skill>/SKILL.md` files listed in Target File Sets.
- `.agents/skills/studio-status/SKILL.md`

Tasks:
- Use the upstream skill name unchanged in every skill frontmatter, for example folder `.agents/skills/start/` with `name: start`.
- Preserve CCGS context in the description/body so these skills remain discoverable as Game Studios workflows.
- Move Claude-only metadata into a `Ported metadata` body section where useful.
- Rewrite `Task` delegation to named upstream role agents, for example `producer`, `writer`, and `game-designer`.
- Rewrite `AskUserQuestion` to numbered natural-language choices.
- Rewrite bare `/skill` references to `$<skill>` or "run the `<skill>` skill"; do not invent project slash commands.
- Rewrite `.claude/docs/**` paths to `.codex/docs/**`; rewrite other `.claude/` paths to Codex-owned paths or shared neutral paths as mapped.
- Add explicit worktree instructions for `prototype` and `vertical-slice`.
- Ensure `skill-test` points to `CCGS Skill Testing Framework/**`.
- Implement `studio-status` to read `production/stage.txt`, `production/review-mode.txt`, and `production/session-state/active.md`.
- Document that `studio-status` complements native `[tui].status_line` by rendering the project-specific game-stage breadcrumb that Claude's shell statusline put in the footer.
- Add skill collision detection. Report active same-name non-CCGS skills with exact paths and remediation, but do not automatically prefix or rename the CCGS skill.

Verification commands:
- `./.codex/audit.sh skills --root "$PWD"`
- `./.codex/audit.sh smoke-headless --root "$PWD"`
- `./.codex/audit.sh runtime --root "$PWD"`

Acceptance criteria:
- Exactly 74 skill directories exist.
- No unsupported Claude metadata appears in frontmatter.
- No raw `AskUserQuestion`, raw Claude `Task`, bare custom slash command, or runtime `.claude` reference remains.

Rollback/coexistence:
- Existing unowned `.agents/skills/*` directories must not be overwritten.
- Same-name skills are not assumed to suppress each other. Existing unowned collisions cause a clear audit warning or installer refusal unless the user explicitly accepts selector ambiguity.

## Phase 6 - Hooks, Config, Permissions, and Command Rules

Goal: port supported lifecycle hooks and Codex policy/config without claiming unavailable parity.

Files to create/modify:
- `.codex/hooks.json`
- `.codex/hooks/*.sh`
- `.codex/rules/settings.rules`
- `.codex/config.toml` only when absent or safely owned/merged
- `.codex/lib/hooks.sh`
- `.codex/lib/state.sh`

Tasks:
- Wire supported events only: `SessionStart`, `PreToolUse`, `PostToolUse`, `PreCompact`, `PostCompact`, `Stop`, `SubagentStart`, `SubagentStop`.
- Do not wire Claude's `Notification` event; Codex has no matching project lifecycle hook. Document native notification setup instead: user-level `notify`, `[tui].notifications`, `[tui].notification_method`, and `[tui].notification_condition`.
- Rewrite hook stdin parsing to Codex fields.
- Split blocking and advisory checks correctly: use `PreToolUse` where feasible, `PostToolUse` for after-the-fact advisories.
- Store hook logs under `production/session-logs/**`.
- Implement `.codex/rules/settings.rules` for command policy. Do not put `prefix_rules` in config.
- Select the complete `game_studios` permission profile through project-local
  `default_permissions`. Do not set project-local `approval_policy` or legacy
  sandbox settings; normal workflows must fit the profile without escalation.
- Do not set project-local `notify`, provider, auth, or secrets. Project config may set `[tui].status_line` because it is not on the verified project-config ignore list; merge/refuse safely if an existing project already owns that setting.

Verification commands:
- `./.codex/audit.sh config --root "$PWD"`
- `./.codex/audit.sh hooks --root "$PWD"`
- `codex --strict-config -C "$fixture" debug prompt-input "noop"` optional.

Acceptance criteria:
- Hooks JSON parses and contains no `Notification`.
- All hook scripts exist, are executable, and pass payload fixtures.
- Config parses, selects `game_studios`, and contains no project-level approval
  or legacy sandbox override.
- The `game_studios` profile explicitly grants write access to `.git`,
  `.agents`, and `.codex`, retains both `.env*` deny patterns, enables its
  bounded network policy, and allows exactly `github.com`.
- A fresh trusted session proves CCGS selected `game_studios` without replacing
  the user's approval policy, resolves the three runtime paths as writable,
  `.env*` as denied, and GitHub as reachable. Parser success alone is not
  permission-parity evidence.
- `$handoff` preflights the exact destination before continuity writes and uses
  only its declared scoped fallback or safe pre-contact DNS retry.
- If `[tui].status_line` is installed, all item IDs are Codex-supported built-ins and the project config parses under `--strict-config`.
- Rules file passes positive/negative command examples.

Rollback/coexistence:
- Existing unowned `.codex/config.toml` and `.codex/hooks.json` cause refusal by default.
- Hook scripts must not read/write `.claude/**`.

## Phase 7 - Installer, Uninstaller, and Ownership Manifest

Goal: make installation idempotent, reversible, and coexistence-safe.

Files to create:
- `.codex/install.sh`
- `.codex/uninstall.sh`
- `.codex/lib/install.sh`
- `.codex/lib/agents.sh`
- `.codex/lib/validate.sh`
- `.codex/manifest/installed-files.json`
- `.codex/backups/.gitkeep`

Tasks:
- Implement marker-block insertion for Markdown files.
- Implement manifest-owned whole-file writes for Codex-owned files.
- Refuse `.claude/**` and `CLAUDE.md` writes always.
- Refuse unowned JSON/TOML collisions by default.
- Implement `--force` only for Codex-owned files, with timestamped backups.
- Make install idempotent.
- Make uninstall remove only manifest-owned files or marker blocks.
- Preserve shared neutral state directories and files.

Verification commands:
- `./.codex/audit.sh coexistence --fixture .codex/tests/fixtures/claude-existing`
- `./.codex/audit.sh coexistence --fixture .codex/tests/fixtures/codex-collisions`
- `./.codex/audit.sh all --root "$PWD"`

Acceptance criteria:
- Hashes for `.claude/**`, `CLAUDE.md`, and shared neutral state remain unchanged unless a test intentionally writes shared state.
- Install/uninstall is idempotent.
- Collision fixtures refuse safely with clear manual merge instructions.

Rollback/coexistence:
- Backups are created only for Codex-owned forced overwrites.
- Uninstall never removes `production/**`, `design/**`, `docs/architecture/**`, `docs/engine-reference/**`, `src/**`, `tests/**`, or `prototypes/**`.

## Phase 8 - Final Documentation and Smoke

Goal: finish human-facing docs and prove the static acceptance gate.

Files to create/modify:
- `.codex/docs/README.md`
- `.codex/docs/MIGRATION.md`
- `.codex/docs/COEXISTENCE.md`
- `.codex/docs/VALIDATION.md`
- `docs/WORKFLOW-GUIDE.md`
- `ATTRIBUTION.md`

Tasks:
- Document install, uninstall, trust, validation, and coexistence.
- Document that upstream skill names are the repo-local Codex surface, e.g. `start`, `prototype`, and `gate-check`.
- Document the skill collision policy and how to disable a competing skill by exact path when needed.
- Document the agent-memory policy: repo-local `.codex/agent-memory/<agent>/MEMORY.md` files are authoritative role memory contracts; the installer does not write global Codex Memories.
- Document statusline parity: Codex `[tui].status_line` preserves built-in model/context footer items, while `studio-status-on-start.sh` and `studio-status` preserve the game-stage/review/session breadcrumb from shared lifecycle files.
- Document notification parity: `notify.sh` is not a Codex project hook; users can enable native Codex notifications or a user-level `notify` command.
- Document that optional plugin packaging is future work.
- Document partial parity gaps: custom script statusline breadcrumb, Claude `Notification` hook, AskUserQuestion, Task syntax, per-agent tool fences, memory, maxTurns, worktree isolation.
- Run final static validation.
- Run optional interactive smoke only if trust/auth/model access is available.

Verification commands:
- `./.codex/audit.sh all --root "$PWD"`
- `./.codex/audit.sh smoke-headless --root "$PWD"`
- `./.codex/audit.sh smoke-interactive --root "$PWD"` optional.
- `git status --short`

Acceptance criteria:
- `audit all` passes.
- `smoke-headless` passes.
- Any skipped interactive smoke has a recorded reason.
- Git diff contains no `.claude/**` or `CLAUDE.md` modifications.

Rollback/coexistence:
- If final audit fails, fix generated assets or validators. Do not loosen forbidden-reference checks to pass.

## Final Executable Task List

1. Verify the pinned upstream source at commit `984023ddac0d5e27624f2baacde6105e45de375f`; generate `.codex/manifest/upstream-assets.json` with all 417 upstream files and `expected-targets.json` from the Phase 3 matrix.
2. Create `.codex/audit.sh` and the standard-library-only validators under `.codex/lib/`; add fixtures for empty projects, Claude coexistence, Codex collisions, shared-state preservation, hook payloads, invalid skills, and invalid agents.
3. Port root and nested instructions to marker-managed `AGENTS.md` blocks; convert the 11 upstream `.claude/rules/*.md` files to their exact nested instruction targets.
4. Copy/rewrite docs: 40 templates to `.codex/docs/templates/**`, 23 `.claude/docs` non-template docs to `.codex/docs/**`, 127 testing-framework assets, shared root project docs under `docs/**`, migration/coexistence docs, and attribution.
5. Generate the 49 direct custom-agent TOML files under `.codex/agents/<agent>.toml` with upstream role names, model tier mapping, partial-mapping notes, and explicit memory-scope bindings.
6. Generate the 17 repo-local memory files under `.codex/agent-memory/<agent>/MEMORY.md`; port the upstream lead-programmer memory file and create generated memory contracts for the other 16 memory-scoped agents; verify no global `~/.codex/memories` writes.
7. Generate the 73 direct repo skills under `.agents/skills/<skill>/SKILL.md`; add the new `.agents/skills/studio-status/SKILL.md`; rewrite `Task`, `AskUserQuestion`, slash-command, and `.claude` references; add collision auditing for same-name active skills.
8. Port supported hooks into `.codex/hooks/*.sh` and `.codex/hooks.json`; replace `notify.sh` with native notification setup docs; add `studio-status-on-start.sh`.
9. Add `.codex/rules/settings.rules` and safe `.codex/config.toml` handling using permission profiles plus `[tui].status_line`; refuse unowned JSON/TOML collisions by default.
10. Implement `.codex/install.sh`, `uninstall.sh`, ownership markers, backups, and `installed-files.json`; prove install/uninstall idempotence and preservation of `.claude/**`, `CLAUDE.md`, and shared neutral state.
11. Run `./.codex/audit.sh all --root "$PWD"` and `./.codex/audit.sh smoke-headless --root "$PWD"`; run `smoke-interactive` only when trust/auth/model access is available; fix failures without weakening coexistence or forbidden-reference rules.
