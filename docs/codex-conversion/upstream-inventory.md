# Upstream Inventory - Phase 1

Phase 1 status: complete.

This file records verified upstream facts only. It does not yet validate the GLM plan's Codex mappings; that starts in Phase 2.

## Evidence

Upstream repository:
- URL: `https://github.com/Donchitos/Claude-Code-Game-Studios`
- Branch checked: `main`
- Commit checked: `984023ddac0d5e27624f2baacde6105e45de375f`
- Local evidence clone: `/private/tmp/ccgs-upstream-phase1`

Verification commands used:
- `git clone --depth 1 https://github.com/Donchitos/Claude-Code-Game-Studios.git /private/tmp/ccgs-upstream-phase1`
- `git rev-parse HEAD`
- `find .claude/agents -maxdepth 1 -type f -name '*.md' -print`
- `find .claude/skills -maxdepth 2 -type f -name 'SKILL.md' -print`
- `find .claude/hooks -maxdepth 1 -type f -print`
- `find .claude/rules -maxdepth 1 -type f -name '*.md' -print`
- `find .claude/docs/templates -type f -print`
- metadata parse of agent and skill frontmatter

## Top-Level Structure

Verified top-level project areas:
- `.claude/`
- `.github/`
- `CCGS Skill Testing Framework/`
- `design/`
- `docs/`
- `production/`
- `src/`
- `.gitignore`
- `CLAUDE.md`
- `CONTRIBUTING.md`
- `LICENSE`
- `README.md`
- `SECURITY.md`
- `UPGRADING.md`

Important root behavior:
- This is a Claude Code template, not an installer-driven package.
- Runtime configuration is rooted in `.claude/settings.json`, `.claude/agents`, `.claude/skills`, `.claude/hooks`, `.claude/rules`, `.claude/statusline.sh`, and `CLAUDE.md`.
- The generated or shared game-production state uses neutral paths such as `production/`, `design/`, `docs/architecture/`, `docs/engine-reference/`, `src/`, `tests/`, and `prototypes/`.

## Agents

Count: 49 files in `.claude/agents/*.md`.

Model distribution:
- `opus`: 3 agents
- `sonnet`: 44 agents
- `haiku`: 2 agents

Frontmatter patterns:
- Common fields: `name`, `description`, `tools`, `model`, `maxTurns`
- 15 agents define `disallowedTools: Bash`
- 17 agents define `memory`
- 6 agents pin skills
- 1 agent defines `isolation: worktree`

Agent files:
- `.claude/agents/accessibility-specialist.md`
- `.claude/agents/ai-programmer.md`
- `.claude/agents/analytics-engineer.md`
- `.claude/agents/art-director.md`
- `.claude/agents/audio-director.md`
- `.claude/agents/community-manager.md`
- `.claude/agents/creative-director.md`
- `.claude/agents/devops-engineer.md`
- `.claude/agents/economy-designer.md`
- `.claude/agents/engine-programmer.md`
- `.claude/agents/game-designer.md`
- `.claude/agents/gameplay-programmer.md`
- `.claude/agents/godot-csharp-specialist.md`
- `.claude/agents/godot-gdextension-specialist.md`
- `.claude/agents/godot-gdscript-specialist.md`
- `.claude/agents/godot-shader-specialist.md`
- `.claude/agents/godot-specialist.md`
- `.claude/agents/lead-programmer.md`
- `.claude/agents/level-designer.md`
- `.claude/agents/live-ops-designer.md`
- `.claude/agents/localization-lead.md`
- `.claude/agents/narrative-director.md`
- `.claude/agents/network-programmer.md`
- `.claude/agents/performance-analyst.md`
- `.claude/agents/producer.md`
- `.claude/agents/prototyper.md`
- `.claude/agents/qa-lead.md`
- `.claude/agents/qa-tester.md`
- `.claude/agents/release-manager.md`
- `.claude/agents/security-engineer.md`
- `.claude/agents/sound-designer.md`
- `.claude/agents/systems-designer.md`
- `.claude/agents/technical-artist.md`
- `.claude/agents/technical-director.md`
- `.claude/agents/tools-programmer.md`
- `.claude/agents/ue-blueprint-specialist.md`
- `.claude/agents/ue-gas-specialist.md`
- `.claude/agents/ue-replication-specialist.md`
- `.claude/agents/ue-umg-specialist.md`
- `.claude/agents/unity-addressables-specialist.md`
- `.claude/agents/unity-dots-specialist.md`
- `.claude/agents/unity-shader-specialist.md`
- `.claude/agents/unity-specialist.md`
- `.claude/agents/unity-ui-specialist.md`
- `.claude/agents/unreal-specialist.md`
- `.claude/agents/ui-programmer.md`
- `.claude/agents/ux-designer.md`
- `.claude/agents/world-builder.md`
- `.claude/agents/writer.md`

Agent-specific metadata to preserve in the port:
- Opus tier: `creative-director`, `producer`, `technical-director`
- Haiku tier: `community-manager`, `devops-engineer`
- Worktree isolation: `prototyper`
- Skill-pinned agents:
  - `creative-director`: `brainstorm`, `design-review`
  - `game-designer`: `design-review`, `balance-check`, `brainstorm`
  - `lead-programmer`: `code-review`, `architecture-decision`, `tech-debt`
  - `producer`: `sprint-plan`, `scope-check`, `estimate`, `milestone-review`
  - `qa-lead`: `bug-report`, `release-checklist`
  - `release-manager`: `release-checklist`, `changelog`, `patch-notes`
- Memory-tagged user agents: `creative-director`, `producer`, `technical-director`
- Memory-tagged project agents: `art-director`, `audio-director`, `economy-designer`, `game-designer`, `lead-programmer`, `level-designer`, `localization-lead`, `narrative-director`, `performance-analyst`, `qa-lead`, `systems-designer`, `ux-designer`, `world-builder`, `writer`

## Skills and Slash Commands

Count: 73 skill files in `.claude/skills/<name>/SKILL.md`.

Model distribution:
- `opus`: 3 skills
- `sonnet`: 63 skills
- `haiku`: 7 skills

Frontmatter patterns:
- All 73 define `name`, `description`, `argument-hint`, `user-invocable`, `allowed-tools`, and `model`.
- All 73 have `user-invocable: true`.
- 39 skills allow `Task`.
- 46 skills allow `AskUserQuestion`.
- 32 skills allow `Bash`.
- 64 skills allow `Write`.
- 28 skills allow `Edit`.
- 10 skills allow `TodoWrite`.
- 2 skills define `isolation: worktree`: `prototype`, `vertical-slice`.

Skill files:
- `.claude/skills/adopt/SKILL.md`
- `.claude/skills/architecture-decision/SKILL.md`
- `.claude/skills/architecture-review/SKILL.md`
- `.claude/skills/art-bible/SKILL.md`
- `.claude/skills/asset-audit/SKILL.md`
- `.claude/skills/asset-spec/SKILL.md`
- `.claude/skills/balance-check/SKILL.md`
- `.claude/skills/brainstorm/SKILL.md`
- `.claude/skills/bug-report/SKILL.md`
- `.claude/skills/bug-triage/SKILL.md`
- `.claude/skills/changelog/SKILL.md`
- `.claude/skills/code-review/SKILL.md`
- `.claude/skills/consistency-check/SKILL.md`
- `.claude/skills/content-audit/SKILL.md`
- `.claude/skills/create-architecture/SKILL.md`
- `.claude/skills/create-control-manifest/SKILL.md`
- `.claude/skills/create-epics/SKILL.md`
- `.claude/skills/create-stories/SKILL.md`
- `.claude/skills/day-one-patch/SKILL.md`
- `.claude/skills/design-review/SKILL.md`
- `.claude/skills/design-system/SKILL.md`
- `.claude/skills/dev-story/SKILL.md`
- `.claude/skills/estimate/SKILL.md`
- `.claude/skills/gate-check/SKILL.md`
- `.claude/skills/help/SKILL.md`
- `.claude/skills/hotfix/SKILL.md`
- `.claude/skills/launch-checklist/SKILL.md`
- `.claude/skills/localize/SKILL.md`
- `.claude/skills/map-systems/SKILL.md`
- `.claude/skills/milestone-review/SKILL.md`
- `.claude/skills/onboard/SKILL.md`
- `.claude/skills/patch-notes/SKILL.md`
- `.claude/skills/perf-profile/SKILL.md`
- `.claude/skills/playtest-report/SKILL.md`
- `.claude/skills/project-stage-detect/SKILL.md`
- `.claude/skills/propagate-design-change/SKILL.md`
- `.claude/skills/prototype/SKILL.md`
- `.claude/skills/qa-plan/SKILL.md`
- `.claude/skills/quick-design/SKILL.md`
- `.claude/skills/regression-suite/SKILL.md`
- `.claude/skills/release-checklist/SKILL.md`
- `.claude/skills/retrospective/SKILL.md`
- `.claude/skills/reverse-document/SKILL.md`
- `.claude/skills/review-all-gdds/SKILL.md`
- `.claude/skills/scope-check/SKILL.md`
- `.claude/skills/security-audit/SKILL.md`
- `.claude/skills/setup-engine/SKILL.md`
- `.claude/skills/skill-improve/SKILL.md`
- `.claude/skills/skill-test/SKILL.md`
- `.claude/skills/smoke-check/SKILL.md`
- `.claude/skills/soak-test/SKILL.md`
- `.claude/skills/sprint-plan/SKILL.md`
- `.claude/skills/sprint-status/SKILL.md`
- `.claude/skills/start/SKILL.md`
- `.claude/skills/story-done/SKILL.md`
- `.claude/skills/story-readiness/SKILL.md`
- `.claude/skills/team-audio/SKILL.md`
- `.claude/skills/team-combat/SKILL.md`
- `.claude/skills/team-level/SKILL.md`
- `.claude/skills/team-live-ops/SKILL.md`
- `.claude/skills/team-narrative/SKILL.md`
- `.claude/skills/team-polish/SKILL.md`
- `.claude/skills/team-qa/SKILL.md`
- `.claude/skills/team-release/SKILL.md`
- `.claude/skills/team-ui/SKILL.md`
- `.claude/skills/tech-debt/SKILL.md`
- `.claude/skills/test-evidence-review/SKILL.md`
- `.claude/skills/test-flakiness/SKILL.md`
- `.claude/skills/test-helpers/SKILL.md`
- `.claude/skills/test-setup/SKILL.md`
- `.claude/skills/ux-design/SKILL.md`
- `.claude/skills/ux-review/SKILL.md`
- `.claude/skills/vertical-slice/SKILL.md`

High-value lifecycle skills to preserve:
- `start`
- `brainstorm`
- `setup-engine`
- `prototype`
- `map-systems`
- `design-system`
- `review-all-gdds`
- `gate-check`
- `create-architecture`
- `architecture-decision`
- `create-control-manifest`
- `architecture-review`
- `ux-design`
- `vertical-slice`
- `create-epics`
- `create-stories`
- `sprint-plan`
- `dev-story`
- `story-done`

Team orchestration skills:
- `team-audio`
- `team-combat`
- `team-level`
- `team-live-ops`
- `team-narrative`
- `team-polish`
- `team-qa`
- `team-release`
- `team-ui`

## Hooks

Count: 12 scripts in `.claude/hooks/`.

Hook scripts:
- `.claude/hooks/detect-gaps.sh`
- `.claude/hooks/log-agent-stop.sh`
- `.claude/hooks/log-agent.sh`
- `.claude/hooks/notify.sh`
- `.claude/hooks/post-compact.sh`
- `.claude/hooks/pre-compact.sh`
- `.claude/hooks/session-start.sh`
- `.claude/hooks/session-stop.sh`
- `.claude/hooks/validate-assets.sh`
- `.claude/hooks/validate-commit.sh`
- `.claude/hooks/validate-push.sh`
- `.claude/hooks/validate-skill-change.sh`

Wiring in `.claude/settings.json`:
- `statusLine`: command `bash .claude/statusline.sh`
- `SessionStart`: `session-start.sh`, `detect-gaps.sh`
- `PreToolUse` matcher `Bash`: `validate-commit.sh`, `validate-push.sh`
- `PostToolUse` matcher `Write|Edit`: `validate-assets.sh`, `validate-skill-change.sh`
- `Notification`: `notify.sh`
- `PreCompact`: `pre-compact.sh`
- `PostCompact`: `post-compact.sh`
- `Stop`: `session-stop.sh`
- `SubagentStart`: `log-agent.sh`
- `SubagentStop`: `log-agent-stop.sh`

Hook behavior notes:
- `validate-commit.sh` parses `.tool_input.command`, checks staged files, blocks invalid staged JSON with exit 2, and emits advisory warnings for missing design sections, hardcoded gameplay values, and TODO format.
- `validate-assets.sh` parses `.tool_input.file_path`, checks only `assets/`, warns on naming convention issues, and exits 1 for invalid JSON in `assets/data/*.json`.
- `notify.sh` is Windows PowerShell-oriented and uses `powershell.exe`.
- Hook scripts use `jq` if present and fallback grep/sed parsing otherwise.

## Rules

Count: 11 files in `.claude/rules/*.md`.

Rules and path scopes:
- `.claude/rules/ai-code.md`: `src/ai/**`
- `.claude/rules/data-files.md`: `assets/data/**`
- `.claude/rules/design-docs.md`: `design/gdd/**`
- `.claude/rules/engine-code.md`: `src/core/**`
- `.claude/rules/gameplay-code.md`: `src/gameplay/**`
- `.claude/rules/narrative.md`: `design/narrative/**`
- `.claude/rules/network-code.md`: `src/networking/**`
- `.claude/rules/prototype-code.md`: `prototypes/**`
- `.claude/rules/shader-code.md`: `assets/shaders/**`
- `.claude/rules/test-standards.md`: `tests/**`
- `.claude/rules/ui-code.md`: `src/ui/**`

Each rule uses YAML frontmatter with a `paths:` list and a Markdown rule body.

## CLAUDE.md Files and Instruction Imports

Count: 5 `CLAUDE.md` files:
- `CLAUDE.md`
- `src/CLAUDE.md`
- `design/CLAUDE.md`
- `docs/CLAUDE.md`
- `CCGS Skill Testing Framework/CLAUDE.md`

Root `CLAUDE.md` imports:
- `@.claude/docs/directory-structure.md`
- `@docs/engine-reference/godot/VERSION.md`
- `@.claude/docs/technical-preferences.md`
- `@.claude/docs/coordination-rules.md`
- `@.claude/docs/coding-standards.md`
- `@.claude/docs/context-management.md`

Root instruction behavior:
- Defines 49 coordinated Claude Code subagents.
- Requires user-driven collaboration: "Question -> Options -> Decision -> Draft -> Approval".
- Requires write approval before `Write`/`Edit`.
- Directs first sessions to run `/start`.

## Settings and Permissions

File:
- `.claude/settings.json`

Verified setting categories:
- `$schema`
- `statusLine`
- `permissions.allow`
- `permissions.deny`
- `hooks`

Allowed command patterns:
- `Bash(git status*)`
- `Bash(git diff*)`
- `Bash(git log*)`
- `Bash(git branch*)`
- `Bash(git rev-parse*)`
- `Bash(ls *)`
- `Bash(dir *)`
- `Bash(python -m json.tool*)`
- `Bash(python -m pytest*)`
- `Bash(py -m pytest*)`

Denied command/read patterns:
- `Bash(rm -rf *)`
- `Bash(git push --force*)`
- `Bash(git push -f *)`
- `Bash(git reset --hard*)`
- `Bash(git clean -f*)`
- `Bash(sudo *)`
- `Bash(chmod 777*)`
- `Bash(*>.env*)`
- `Bash(cat *.env*)`
- `Bash(type *.env*)`
- `Read(**/.env*)`

## Statusline and Session State

Statusline file:
- `.claude/statusline.sh`

Behavior:
- Receives JSON on stdin.
- Extracts model, context usage, and CWD using `jq` or grep fallback.
- Reads `production/stage.txt` if present.
- Otherwise auto-detects stage using artifacts:
  - `design/gdd/game-concept.md`
  - `design/gdd/systems-index.md`
  - `.claude/docs/technical-preferences.md`
  - `src/` source-file count
  - `docs/architecture/adr-*.md`
- For Production, Polish, and Release, reads `production/session-state/active.md`.
- Parses a structured `<!-- STATUS -->` block with `Epic:`, `Feature:`, and `Task:`.
- Outputs one line: `ctx: <pct> | <model> | <stage> | <breadcrumb>`.

Seeded production state:
- `production/session-state/.gitkeep`

Shared runtime state paths used by skills:
- `production/stage.txt`
- `production/review-mode.txt`
- `production/session-state/active.md`
- `production/sprints/`
- `production/milestones/`
- `production/epics/`
- `production/qa/`
- `production/gate-checks/`
- `production/playtests/`

## Templates

Verified `.claude/docs/templates/` file count: 40.

Template files:
- `.claude/docs/templates/accessibility-requirements.md`
- `.claude/docs/templates/architecture-decision-record.md`
- `.claude/docs/templates/architecture-doc-from-code.md`
- `.claude/docs/templates/architecture-traceability.md`
- `.claude/docs/templates/art-bible.md`
- `.claude/docs/templates/changelog-template.md`
- `.claude/docs/templates/collaborative-protocols/design-agent-protocol.md`
- `.claude/docs/templates/collaborative-protocols/implementation-agent-protocol.md`
- `.claude/docs/templates/collaborative-protocols/leadership-agent-protocol.md`
- `.claude/docs/templates/concept-doc-from-prototype.md`
- `.claude/docs/templates/design-doc-from-implementation.md`
- `.claude/docs/templates/difficulty-curve.md`
- `.claude/docs/templates/economy-model.md`
- `.claude/docs/templates/faction-design.md`
- `.claude/docs/templates/game-concept.md`
- `.claude/docs/templates/game-design-document.md`
- `.claude/docs/templates/game-pillars.md`
- `.claude/docs/templates/hud-design.md`
- `.claude/docs/templates/incident-response.md`
- `.claude/docs/templates/interaction-pattern-library.md`
- `.claude/docs/templates/level-design-document.md`
- `.claude/docs/templates/milestone-definition.md`
- `.claude/docs/templates/narrative-character-sheet.md`
- `.claude/docs/templates/pitch-document.md`
- `.claude/docs/templates/player-journey.md`
- `.claude/docs/templates/post-mortem.md`
- `.claude/docs/templates/project-stage-report.md`
- `.claude/docs/templates/prototype-report.md`
- `.claude/docs/templates/release-checklist-template.md`
- `.claude/docs/templates/release-notes.md`
- `.claude/docs/templates/risk-register-entry.md`
- `.claude/docs/templates/skill-test-spec.md`
- `.claude/docs/templates/sound-bible.md`
- `.claude/docs/templates/sprint-plan.md`
- `.claude/docs/templates/systems-index.md`
- `.claude/docs/templates/technical-design-document.md`
- `.claude/docs/templates/test-evidence.md`
- `.claude/docs/templates/test-plan.md`
- `.claude/docs/templates/ux-spec.md`
- `.claude/docs/templates/vertical-slice-report.md`

Template-like files outside `.claude/docs/templates/`:
- `.claude/docs/settings-local-template.md`
- `.claude/docs/CLAUDE-local-template.md`
- `CCGS Skill Testing Framework/templates/agent-test-spec.md`
- `CCGS Skill Testing Framework/templates/skill-test-spec.md`

Count correction to carry forward:
- The upstream README advertises 41 document templates.
- The verified tree has 40 files under `.claude/docs/templates/`.
- Phase 2 must decide whether the README count includes a template-like file outside that directory or is stale.

## Documentation Artifacts

Root docs:
- `README.md`
- `UPGRADING.md`
- `CONTRIBUTING.md`
- `SECURITY.md`
- `LICENSE`

`.claude/docs/` files, excluding templates:
- `.claude/docs/CLAUDE-local-template.md`
- `.claude/docs/agent-coordination-map.md`
- `.claude/docs/agent-roster.md`
- `.claude/docs/coding-standards.md`
- `.claude/docs/context-management.md`
- `.claude/docs/coordination-rules.md`
- `.claude/docs/directory-structure.md`
- `.claude/docs/director-gates.md`
- `.claude/docs/hooks-reference.md`
- `.claude/docs/hooks-reference/hook-input-schemas.md`
- `.claude/docs/hooks-reference/post-merge-asset-validation.md`
- `.claude/docs/hooks-reference/post-sprint-retrospective.md`
- `.claude/docs/hooks-reference/pre-commit-code-quality.md`
- `.claude/docs/hooks-reference/pre-commit-design-check.md`
- `.claude/docs/hooks-reference/pre-push-test-gate.md`
- `.claude/docs/quick-start.md`
- `.claude/docs/review-workflow.md`
- `.claude/docs/rules-reference.md`
- `.claude/docs/settings-local-template.md`
- `.claude/docs/setup-requirements.md`
- `.claude/docs/skills-reference.md`
- `.claude/docs/technical-preferences.md`
- `.claude/docs/workflow-catalog.yaml`

Project docs:
- `docs/WORKFLOW-GUIDE.md`
- `docs/COLLABORATIVE-DESIGN-PRINCIPLE.md`
- `docs/CLAUDE.md`
- `docs/architecture/tr-registry.yaml`
- `docs/registry/architecture.yaml`
- `docs/examples/README.md`
- `docs/examples/reverse-document-workflow-example.md`
- `docs/examples/session-adopt-brownfield.md`
- `docs/examples/session-design-crafting-system.md`
- `docs/examples/session-design-system-skill.md`
- `docs/examples/session-gate-check-phase-transition.md`
- `docs/examples/session-implement-combat-damage.md`
- `docs/examples/session-scope-crisis-decision.md`
- `docs/examples/session-story-lifecycle.md`
- `docs/examples/session-ux-pipeline.md`
- `docs/examples/skill-flow-diagrams.md`
- `docs/engine-reference/README.md`
- `docs/engine-reference/godot/*`
- `docs/engine-reference/unity/*`
- `docs/engine-reference/unreal/*`

Engine reference count:
- 46 files under `docs/engine-reference/`
- Engines covered: Godot, Unity, Unreal

## Workflow Catalog and Lifecycle Behavior

Primary lifecycle catalog:
- `.claude/docs/workflow-catalog.yaml`

Verified phases:
- `concept`
- `systems-design`
- `technical-setup`
- `pre-production`
- `production`
- `polish`
- `release`

Important lifecycle behavior:
- `/help` uses the workflow catalog to determine current phase and next steps.
- Artifact checks include glob, pattern, `min_count`, note, required flag, and repeatable flag.
- The catalog explicitly says phase gates are advisory and the user decides whether to proceed.
- Review mode is stored in `production/review-mode.txt` and can be overridden per run with `--review full|lean|solo`.
- Stage advancement writes one line to `production/stage.txt`.
- `gate-check` handles phase transition readiness and writes gate reports under `production/gate-checks/`.

Verified lifecycle spine:
- `start`
- `brainstorm`
- `setup-engine`
- `art-bible`
- `map-systems`
- `design-system`
- `design-review`
- `review-all-gdds`
- `consistency-check`
- `create-architecture`
- `architecture-decision`
- `architecture-review`
- `create-control-manifest`
- `ux-design`
- `ux-review`
- `prototype`
- `create-epics`
- `create-stories`
- `test-setup`
- `sprint-plan`
- `vertical-slice`
- `story-readiness`
- `dev-story`
- `code-review`
- `story-done`
- `smoke-check`
- `qa-plan`
- `team-qa`
- `gate-check`
- `release-checklist`
- `launch-checklist`
- `changelog`
- `patch-notes`

Delegation model:
- Defined in `.claude/docs/agent-coordination-map.md`.
- Vertical delegation: directors -> leads -> specialists.
- Horizontal consultation is allowed when same-tier domains intersect.
- Conflict escalation routes to parent leads/directors and producer for schedule or scope conflicts.
- Team skills coordinate multi-agent workflows for combat, narrative, UI, release, polish, audio, level, live-ops, and QA.

Gate model:
- Defined in `.claude/docs/director-gates.md`.
- Review modes:
  - `full`: all gates active.
  - `lean`: phase gates only.
  - `solo`: all gates skipped.
- Standard verdicts:
  - `APPROVE` or `READY`
  - `CONCERNS`
  - `REJECT` or `NOT READY`
- Parallel gate behavior: issue all relevant `Task` calls before waiting; strictest verdict wins.

## Install and Upgrade Flow

Verified upstream install flow:
- No standalone installer script exists.
- README setup is clone/use-template, `cd`, launch `claude`, then run `/start`.
- `.claude/` and `CLAUDE.md` are the runtime installation.

Upgrade docs:
- `UPGRADING.md`
- `.claude/docs/settings-local-template.md`
- `.claude/docs/CLAUDE-local-template.md`

Port implication for later phases:
- A Codex port needs an installer/uninstaller or a clearly defined copy layout if coexistence is a hard requirement.
- The installer must not write `.claude/` or `CLAUDE.md`.

## Tests and Validation Assets

Primary in-template validation skill:
- `.claude/skills/skill-test/SKILL.md`

`skill-test` modes:
- `static`: seven structural checks per skill
- `spec`: behavior check against a test spec
- `category`: category rubric
- `audit`: coverage report

Separate framework directory:
- `CCGS Skill Testing Framework/`

Framework counts:
- 49 agent specs under `CCGS Skill Testing Framework/agents/**/*.md`
- 72 skill specs under `CCGS Skill Testing Framework/skills/**/*.md`
- 2 framework templates under `CCGS Skill Testing Framework/templates/*.md`
- 1 catalog: `CCGS Skill Testing Framework/catalog.yaml`
- 1 rubric: `CCGS Skill Testing Framework/quality-rubric.md`
- 1 framework-specific `CLAUDE.md`

Coverage gap:
- Upstream has 73 skills.
- The framework has 72 skill spec files.
- Missing framework spec: `vertical-slice`.

## Phase 1 Inventory-Level Corrections to Carry Forward

These are not the full GLM plan review; they are verified upstream facts that Phase 2 must use.

1. Agent model count correction:
   - Verified: 44 `sonnet`, 3 `opus`, 2 `haiku`.
   - `prototyper` is not missing a model; it has `model: sonnet` and `isolation: worktree`.

2. Template count correction:
   - Verified: 40 files under `.claude/docs/templates/`.
   - README says 41 document templates, so the plan must either account for a template-like file outside that directory or mark the README count as stale.

3. Testing framework coverage correction:
   - Verified: 72 framework skill specs for 73 upstream skills.
   - `vertical-slice` has no matching framework skill spec.

4. CLAUDE.md count correction:
   - Verified: 5 `CLAUDE.md` files, including `CCGS Skill Testing Framework/CLAUDE.md`.
   - Any port inventory must account for the framework-specific instructions too.

5. Coexistence-sensitive upstream paths:
   - Claude-owned runtime paths: `.claude/`, `CLAUDE.md`, nested `src/CLAUDE.md`, `design/CLAUDE.md`, `docs/CLAUDE.md`, and `CCGS Skill Testing Framework/CLAUDE.md`.
   - Shared game artifact paths: `production/`, `design/`, `docs/architecture/`, `docs/engine-reference/`, `src/`, `tests/`, `prototypes/`.

## Phase 1 Completion Checklist

- [x] Verified upstream repo exists and current tree can be cloned.
- [x] Captured commit hash and local evidence path.
- [x] Counted and listed agents.
- [x] Counted and listed skills.
- [x] Counted and listed hooks and hook event wiring.
- [x] Counted and listed rules and path scopes.
- [x] Counted and listed templates.
- [x] Identified documentation categories.
- [x] Identified statusline and session-state behavior.
- [x] Identified install/upgrade flow.
- [x] Identified tests and validation assets.
- [x] Captured inventory-level discrepancies for Phase 2 review.

