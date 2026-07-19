# Validation Suite - Phase 4

Phase 4 status: complete.

This suite is the acceptance harness the implementation must satisfy. It is designed to be executable without relying on the pinned `/private/tmp` clone, and without invoking an LLM in the default path.

## Validation Principles

- Static and fixture checks are the default gate.
- Interactive Codex smoke tests are separate because they may require trust, auth, approvals, and model access.
- Do not depend on `.claude/**` or `CLAUDE.md` after install, except in source/provenance docs.
- Do not use PyYAML or other undeclared Python packages. Use Python 3.11+ standard library (`json`, `hashlib`, `tomllib`) plus a minimal frontmatter parser for simple `key: value` metadata.
- Do not use `/private/tmp` as an authoritative source. The implementation must commit a manifest derived from the pinned upstream commit.
- Every check must produce machine-readable JSON plus concise human output.

## Proposed Validator Files

These files are part of the future implementation plan, not Phase 4 edits:

| Target file | Purpose |
|---|---|
| `.codex/audit.sh` | Thin command dispatcher for all validation commands. |
| `.codex/lib/validate_manifest.py` | Inventory, coverage, target-count, and disposition checks. |
| `.codex/lib/validate_runtime.py` | Runtime reference scan, path-shape lint, metadata lint, TOML/JSON parse checks. |
| `.codex/lib/validate_hooks.py` | Hook config validation and hook stdin fixture runner. |
| `.codex/lib/validate_rules.py` | `.codex/rules/settings.rules` static lint plus command examples. |
| `.codex/lib/validate_install.py` | Install/uninstall/idempotence/coexistence fixtures. |
| `.codex/lib/validate_smoke.py` | Headless and interactive workflow smoke definitions. |
| `.codex/manifest/upstream-assets.json` | Committed upstream asset manifest for all 417 files. |
| `.codex/manifest/expected-targets.json` | Expected generated Codex paths and counts. |
| `.codex/tests/fixtures/**` | Static fixtures for collisions, hooks, invalid skills, invalid agents, and coexistence. |

## Canonical Commands

| Command | Default gate | Purpose |
|---|---:|---|
| `./.codex/audit.sh all --root "$PWD"` | yes | Run all static/headless checks. |
| `./.codex/audit.sh manifest --root "$PWD"` | yes | Verify upstream coverage and target mapping completeness. |
| `./.codex/audit.sh runtime --root "$PWD"` | yes | Scan for forbidden runtime references and path collisions. |
| `./.codex/audit.sh skills --root "$PWD"` | yes | Validate skill paths, names, metadata, rewrites, and counts. |
| `./.codex/audit.sh agents --root "$PWD"` | yes | Validate custom-agent TOML, names, models, and counts. |
| `./.codex/audit.sh config --root "$PWD"` | yes | Validate `.codex/config.toml`, hooks JSON, permission model, and command rules. |
| `./.codex/audit.sh hooks --root "$PWD"` | yes | Run hook schema and stdin fixture checks. |
| `./.codex/audit.sh coexistence --fixture .codex/tests/fixtures/coexistence` | yes | Install/uninstall with `.claude/**` and `CLAUDE.md` present. |
| `./.codex/audit.sh smoke-headless --root "$PWD"` | yes | Static workflow smoke without model calls. |
| `./.codex/audit.sh smoke-interactive --root "$PWD"` | no | Reports `skipped` when no live evidence is supplied. |
| `./.codex/audit.sh smoke-interactive --root "$PWD" --evidence /path/to/evidence.json` | no | Cross-checks raw parent, child, and hook JSONL for a recorded CLI or desktop activation; never launches a model in CI. |
| `codex --strict-config -C "$fixture" debug prompt-input "noop"` | optional | Confirm model-visible `AGENTS.md` layering in a trusted fixture. |
| `codex debug models > "$tmp/models.json"` | optional | Validate configured model slugs against the current local model catalog. |

## Manifest Checks

Input manifests:
- `upstream-assets.json`: one row per upstream file from commit `984023ddac0d5e27624f2baacde6105e45de375f`.
- `expected-targets.json`: one row per expected Codex runtime/doc target.

Required `upstream-assets.json` fields:
- `path`
- `sha256`
- `category`
- `disposition`
- `parity`
- `target`
- `rationale`

Checks:
- Exactly 417 upstream files are present.
- Category counts match the Phase 3 matrix: 49 agents, 73 skills, 12 hooks, 11 rules, 40 templates, 23 `.claude/docs` non-template docs, 1 upstream explicit agent-memory file, 17 generated Codex memory contract targets, 127 testing-framework assets, 62 upstream root/shared `docs/**` files, and remaining root/shared categories.
- Every row has one of `ported`, `replaced`, `shared`, `not_applicable`, or `blocked`.
- Every `not_applicable` and `blocked` row has a concrete rationale.
- Only one upstream testing-framework gap was inherited: missing `vertical-slice` skill spec. The Codex target distribution adds a clearly labeled spec for this skill.
- `notify.sh` is marked as replaced by native Codex notification setup documentation, not missing.
- Generated target counts match: 49 agents, 17 repo-local agent-memory files, 73 ported skills, 4 new Codex-native support skills (`studio-status`, `studio-next`, `handoff`, `resume-from-handoff`), 11 ported hooks plus 1 new status hook if implemented, 15 root-routed path-rule documents, 40 templates, 127 upstream testing-framework assets plus 1 Codex-added `vertical-slice` spec.

Acceptance:
- `audit manifest` exits 0 only when there are no uncategorized upstream files and no unexpected generated targets.

## Runtime Dependency Checks

Runtime paths to scan:
- `AGENTS.md`
- the framework-local `AGENTS.md` plus root-routed `.codex/instructions/path-rules/**`
- `.agents/skills/**`
- `.codex/**`
- `docs/**` except explicit provenance docs

Forbidden in runtime files:
- `.claude/`
- `CLAUDE.md`
- `Claude Code` when used as a runtime dependency rather than attribution
- bare custom slash commands such as `/start`, `/brainstorm`, `/gate-check`, `/dev-story`
- `AskUserQuestion`
- `Task` as a Claude tool invocation
- unsupported skill frontmatter fields used as enforcement: `allowed-tools`, `model`, `argument-hint`, `user-invocable`, `isolation`
- `prefix_rules` inside `.codex/config.toml`

Allowlist:
- `.codex/docs/MIGRATION.md`
- `.codex/docs/COEXISTENCE.md`
- `ATTRIBUTION.md`
- source/provenance comments in manifests

Acceptance:
- Runtime files have zero forbidden references outside the allowlist.
- Documentation can mention Claude only for provenance, migration, and coexistence explanation.

## Skill Validation

Path checks:
- Exactly 77 core skill directories exist under `.agents/skills/`.
- Exactly 73 directories match upstream skills as `.agents/skills/<upstream-name>/SKILL.md`.
- Exactly four new Codex-native support skills exist: `.agents/skills/studio-status/SKILL.md`, `.agents/skills/studio-next/SKILL.md`, `.agents/skills/handoff/SKILL.md`, and `.agents/skills/resume-from-handoff/SKILL.md`.
- No nested namespace layout exists under `.agents/skills/**`; CCGS skill directories must be direct children.

Metadata checks:
- Each `SKILL.md` starts with frontmatter.
- Required fields: `name`, `description`.
- `name` equals the folder name, for example `start`.
- `description` is nonempty and includes enough upstream alias context for discoverability.
- Unsupported Claude metadata is not present in frontmatter. If preserved, it appears under a body section titled `Ported metadata`.

Rewrite checks:
- No raw `AskUserQuestion` remains.
- No raw Claude `Task` invocation remains.
- No bare upstream slash-command handoff remains.
- All role references resolve to a generated upstream-named custom agent.
- All skill references use upstream skill names, such as `$start`, `start`, `prototype`, and `gate-check`, not artificial prefixed names.
- Skills with upstream worktree isolation (`prototype`, `vertical-slice`) contain explicit worktree instructions or a helper-script reference.
- Opus-tier skills (`architecture-review`, `gate-check`, `review-all-gdds`) contain explicit high-reasoning guidance or delegation to high-tier agents.

Collision checks:
- Compare generated CCGS skill names against active or discoverable non-CCGS skills when the local Codex CLI exposes that data, for example through `codex debug prompt-input`.
- Static fallback scans common configured skill roots only as a best-effort warning, not as CI truth.
- A same-name active skill is reported with all competing paths. The installer must not silently rename the CCGS skill; it must either refuse or require explicit user acceptance of selector ambiguity.

Acceptance:
- `audit skills` exits 0 when all required core skills pass metadata and rewrite checks, with only explicitly allowed project-local extras.

## Custom Agent Validation

Path checks:
- Exactly 49 files exist as `.codex/agents/<upstream-agent>.toml`.
- No nested namespace layout exists under `.codex/agents/**`; CCGS agent TOML files must be direct children.
- Exactly 17 repo-local memory contract files exist as `.codex/agent-memory/<agent>/MEMORY.md` for every upstream agent with `memory: user` or `memory: project`.
- `.codex/agent-memory/lead-programmer/MEMORY.md` is rewritten from upstream `.claude/agent-memory/lead-programmer/MEMORY.md`; the other 16 memory files are generated memory contracts and must be labeled as generated Codex memory contracts.

TOML checks:
- Parse each file with Python `tomllib`.
- Required fields: `name`, `description`, `developer_instructions`.
- `name` equals the upstream hyphenated role name and the filename stem, for example `producer`.
- `description` includes the upstream role name.
- `developer_instructions` includes role duties and any partial-mapping notes for tools, memory, pinned skills, or isolation.
- For every upstream memory-scoped agent, `developer_instructions` includes `Ported Claude memory scope: user` or `Ported Claude memory scope: project` and instructs the agent to read `.codex/agent-memory/<agent>/MEMORY.md` before role work.
- Unsupported Claude fields are not top-level TOML fields: `tools`, `disallowedTools`, `maxTurns`, `memory`, `skills`, `isolation`.
- Generated agents and installer scripts never write to `~/.codex/memories`; global Codex Memories are documented as optional user-controlled behavior only.

Collision checks:
- Current documented Codex built-ins are `default`, `worker`, and `explorer`.
- Existing project/user custom agents with the same name are reported with paths. The installer must not silently prefix or rename CCGS agents; it must refuse or require explicit user acceptance.

Model checks:
- Three Opus-tier upstream agents map to high-tier model settings: `creative-director`, `producer`, `technical-director`.
- Two Haiku-tier upstream agents map to low-tier settings: `community-manager`, `devops-engineer`.
- Remaining 44 agents map to medium-tier settings.
- If `codex debug models` is available, configured model slugs must appear in the current catalog.

Acceptance:
- `audit agents` exits 0 when all 49 TOML files parse, required fields exist, model-tier counts match, all 17 memory bindings resolve, and no global Codex memory write path exists.

## Config and Rules Validation

Config checks:
- `.codex/config.toml` is absent, installer-owned, or safely merged. Existing unowned config must cause installer refusal by default.
- If generated, `.codex/config.toml` parses as TOML.
- It sets `default_permissions = "game_studios"` and contains no project-local
  `approval_policy`, `sandbox_mode`, or `sandbox_workspace_write` override.
- It does not contain command `prefix_rules`.
- It does not set project-local `notify`.
- It defines a complete `game_studios` profile with exact Git/runtime writes,
  `.env*` denials, network enabled, and only `github.com` allowed.
- If it sets `[tui].status_line`, every item is a supported Codex built-in footer item for the installed Codex version.
- It does not write provider/auth secrets.

Codex CLI check:
- Optional fixture command: `codex --strict-config -C "$fixture" debug prompt-input "noop"`.
- This is optional because trust and user config can affect behavior; static parser results remain authoritative in CI.

Rules checks:
- `.codex/rules/settings.rules` exists when command policy is installed.
- Rules file includes documented allow/prompt/forbid examples.
- Destructive commands such as `rm -rf`, `git reset --hard`, `git clean -fdx`, force push, and secret reads are denied or require prompt.
- Safe read/test commands used by workflows are allowed or prompt according to the chosen permission posture.
- Rules are tested with positive and negative command examples stored beside the rules file.

Acceptance:
- `audit config` exits 0 when TOML parse, complete-profile boundaries,
  approval/sandbox-override prohibition, rules-file, and command-example checks
  pass.

## Hook Validation

Config checks:
- `.codex/hooks.json` parses as JSON.
- Only supported events are present: `PreToolUse`, `PermissionRequest`, `PostToolUse`, `PreCompact`, `PostCompact`, `SessionStart`, `SubagentStart`, `SubagentStop`, `UserPromptSubmit`, `Stop`.
- `Notification` is absent.
- Native notification behavior is documented in `.codex/docs/README.md` or `.codex/docs/COEXISTENCE.md`, including the project-local limitation for `notify`.
- Every referenced hook script exists and is executable.
- Hook script paths stay under `.codex/hooks/**`.

Script checks:
- Scripts use neutral/shared paths or Codex-owned paths only.
- Scripts do not read or write `.claude/**`.
- Scripts handle missing optional project files gracefully.
- Scripts accept Codex stdin JSON fields such as `hook_event_name`, `tool_name`, `tool_input`, `agent_type`, `agent_id`, and `cwd`.

Fixture checks:
- `SessionStart`: `session-start.sh`, `detect-gaps.sh`, `studio-status-on-start.sh`.
- `PreToolUse Bash`: `validate-commit.sh`, `validate-push.sh`.
- `PreToolUse apply_patch`: preflight asset validation where feasible.
- `PostToolUse apply_patch`: advisory asset and skill validation.
- `PreCompact` and `PostCompact`: handoff file behavior.
- `SubagentStart` and `SubagentStop`: log file behavior.
- `Stop`: session stop summary/log behavior.

Acceptance:
- `audit hooks` exits 0 when hooks JSON validates and every fixture returns the expected allow/deny/advisory shape.

## Coexistence and Install Validation

Fixtures:
- `empty-game`: no Claude or Codex files.
- `claude-existing`: contains `.claude/**`, `CLAUDE.md`, upstream shared state, and no Codex port.
- `codex-collisions`: contains existing `AGENTS.md`, `.agents/skills/start`, `.codex/agents/reviewer.toml`, `.codex/config.toml`, `.codex/hooks.json`.
- `shared-state-dirty`: contains preexisting `production/**`, `design/**`, and `docs/architecture/**` artifacts.

Install checks:
- Installer never writes to `.claude/**`.
- Installer never modifies `CLAUDE.md`.
- Existing Markdown files are marker-block merged only.
- Existing unowned JSON/TOML files cause refusal by default.
- `--force` writes timestamped backups before overwriting Codex-owned files, but still refuses `.claude/**`, `CLAUDE.md`, and shared neutral state deletion.
- Install is idempotent.

Uninstall checks:
- Uninstaller removes only manifest-owned files or marker blocks.
- Uninstaller preserves `.claude/**`, `CLAUDE.md`, shared neutral state, and unrelated Codex files.
- Empty directories are removed only when Codex-owned and empty.

Acceptance:
- `audit coexistence` exits 0 when before/after hashes for `.claude/**`, `CLAUDE.md`, and shared neutral state match expected behavior.

## Documentation and Template Validation

Checks:
- All 40 upstream templates exist at `.codex/docs/templates/**`.
- All `.claude/docs` non-template docs are copied or rewritten under `.codex/docs/**`.
- All upstream root/shared project docs are either shared at the same neutral `docs/**` path or copied with rationale.
- `.codex/docs/README.md`, `.codex/docs/MIGRATION.md`, `.codex/docs/COEXISTENCE.md`, and `ATTRIBUTION.md` exist.
- Documentation invocation examples use upstream skill names, such as `$start` or "run the `start` skill".
- `CCGS Skill Testing Framework/**` contains 127 upstream testing-framework assets plus the Codex-added `vertical-slice` skill spec.
- The validation report preserves the missing upstream `vertical-slice` spec as historical evidence and includes the Codex-added target spec.

Acceptance:
- `audit docs` exits 0 when counts, paths, and rewrite scans pass.

## Workflow Smoke Tests

Headless static smoke:
- `start`: verifies first-run onboarding references shared state and asks bounded questions.
- `project-stage-detect`: verifies it reads neutral project state.
- `gate-check`: verifies gate verdict terms and strictest-verdict semantics.
- `dev-story`: verifies story implementation lifecycle reads story/context and delegates to correct roles.
- `story-done`: verifies review/test evidence gate.
- `team-qa`: verifies team orchestration role references resolve.
- `skill-test`: verifies it points to the Codex testing framework.
- `studio-status`: verifies it reads stage/review/session-state files.
- `studio-next`: verifies it reads handoff/session/sprint/stage/workflow state and remains read-only.
- Statusline validation verifies `[tui].status_line` uses supported built-in item IDs and that the project-specific stage breadcrumb remains covered by `studio-status-on-start.sh` and `studio-status`.

Interactive smoke, optional:
- Run Codex in a trusted fixture and invoke `start`.
- Trigger a subagent delegation from a team skill.
- Require hook or transcript evidence that the exact custom role profile loaded;
  a task path plus `agent_type: default` is a failed role-agent smoke. A task
  name, agent path, nickname, or child self-identification is not activation
  proof.
- Record the client surface and point the evidence file at the raw parent
  rollout, child rollout, and SubagentStart log. The validator derives the
  runtime version, selected role, configured child model and effort, role
  instruction canary, and V2 fork mode from those sources plus the authoritative
  role TOML.
- Trigger a hook-protected git command in a fixture.
- Confirm prompt-input includes root `AGENTS.md` content with no Claude runtime dependency; separately verify the router names every shipped path rule.

Acceptance:
- `audit smoke-headless` must pass in CI.
- `audit smoke-interactive` must report `skipped`, not `pass`, when no trusted
  model-running evidence was executed. CI may skip it with an explicit reason.
- `audit smoke-interactive --evidence <json>` must fail closed on default/null
  roles, generic instructions, model/effort mismatches, self-report-only
  evidence, and incompatible V2 full-history forks.

Role-activation evidence uses this shape:

```json
{
  "surface": "desktop",
  "requested_role": "producer",
  "task_name": "desktop_producer_activation_probe",
  "parent_session_log": "/path/to/parent-rollout.jsonl",
  "child_session_log": "/path/to/child-rollout.jsonl",
  "hook_log": "/path/to/agents-start.jsonl"
}
```

Relative evidence paths resolve from the evidence JSON location. A passing
record requires one matching raw `spawn_agent` call, parent start event,
SubagentStart hook payload, child session identity, role metadata, configured
model/effort, and developer-instruction canary. Summary booleans, task paths,
and child self-identification are not accepted as substitutes.

## Required Reports

Every audit command should support:
- `--json` for machine-readable output.
- `--root <path>` for target project root.
- `--fixture <path>` for fixture checks.
- Exit code `0` for pass, `1` for validation failures, `2` for tool/environment setup errors.

Required report sections:
- `summary`
- `checks`
- `failures`
- `warnings`
- `skipped`
- `environment`
- `source_commit`

## Phase 5 Carry-Forward

The implementation plan must include tasks to:
1. Generate and commit `upstream-assets.json` for all 417 upstream files.
2. Generate `expected-targets.json` from the corrected matrix.
3. Implement the audit dispatcher and validators before or alongside generated runtime assets.
4. Add fixtures before running install/uninstall validation.
5. Make `audit all` the final acceptance command for the port.
