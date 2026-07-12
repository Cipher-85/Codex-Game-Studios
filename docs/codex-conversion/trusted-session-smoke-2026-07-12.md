# Trusted-Session Smoke - 2026-07-12

## Scope

This evidence records a live trusted-session smoke against Codex Game Studios
`0.5.0` at `2a03159420fde03dcbe07ea27f878309752b9611` using Codex CLI
`0.144.1`. Sentinel files contained fake data only and were removed afterward.

## Verified

- Project discovery: `codex debug prompt-input` loaded root `AGENTS.md` and all
  77 repo-local skills from `.agents/skills`.
- Strict configuration: fresh `codex exec --strict-config` tasks loaded the
  project permission profile and hooks.
- Restart behavior: the already-running parent task, opened before the new
  permission profile existed, allowed the sentinel `apply_patch`; a fresh task
  denied it. This confirms the documented new-session activation requirement.
- Filesystem controls: a fresh task read and updated an ordinary control file,
  while reads and `apply_patch` writes to a root `.env.smoke` sentinel failed
  with `Operation not permitted`.
- Bash secret hook: root and nested reads/writes for `.env`, `.env.local`, and
  `.env.example` were denied by PreToolUse before execution.
- Hook activation: real payloads were captured for SessionStart, Bash
  PreToolUse, apply_patch PostToolUse, SubagentStart, SubagentStop, and Stop.
- Model routes: the bundled catalog contained `gpt-5.5`, `gpt-5.4`, and
  `gpt-5.4-mini`; one-message authenticated runs succeeded on all three.
- Footer: a fresh terminal TUI rendered model/reasoning, current directory,
  context used, and git branch (`main`).
- Project breadcrumb: startup context and `$studio-status` both reported Stage,
  review mode, and active session as `unset`, matching the absent state files.

## Failed Role-Agent Check

An ephemeral exact-name `producer` delegation failed with `no thread with id`.
A normal persisted task then completed a child path named `/root/producer`, but
the authoritative SubagentStart payload reported `agent_type: default`; session
metadata reported `agent_role: null`, and the child received generic base
instructions rather than `.codex/agents/producer.toml`.

Adding a temporary, officially supported `[agents.producer]` `config_file`
registration parsed under `--strict-config` but produced the same `default`
payload and generic child instructions. The ineffective registration was
removed. A task name or model-authored success statement is therefore not
accepted as evidence that a CCGS role profile loaded.

This conflicts with the documented custom-agent behavior at
<https://learn.chatgpt.com/docs/agent-configuration/subagents#custom-agents>, so
current-session evidence takes precedence for this environment.

## Follow-Up Activation A/B

Fresh read-only `codex exec` probes isolated the failure to the model-selected
delegation surface:

- Stock `gpt-5.6-sol` selected MultiAgent V2. Its model-visible spawn schema had
  no custom-role selector, and the `producer` task produced `agent_role: null`,
  inherited Sol settings, and generic instructions.
- A `gpt-5.5` V1 parent selected the existing `producer` and hyphenated
  `creative-director` profiles without renaming or additional registration.
  Child metadata, developer instructions, configured model, and reasoning
  effort matched their TOMLs.
- A Sol V2 parent exposed and forwarded custom-role selection when started with
  the ephemeral overrides
  `features.multi_agent_v2.hide_spawn_agent_metadata=false` and
  `features.multi_agent_v2.tool_namespace="agents"`.
- V2 custom-role/model overrides failed with the full-history fork default and
  succeeded with `fork_turns: "none"`, matching open upstream issue
  <https://github.com/openai/codex/issues/20077>.

The same override worked through the executable bundled with the desktop app.
A subsequent fresh task created by the actual desktop app exposed the custom
role selector and spawned `producer` with `fork_turns: "none"`. The parent tool
result did not expose authoritative role metadata and conservatively called the
result inconclusive, but post-run evidence closed that gap: the SubagentStart
payload recorded `agent_type: producer`; child session metadata recorded
`agent_role: producer`; the full producer developer instructions loaded; and
the child used its configured `gpt-5.5` model with `high` effort. The task label
was deliberately different (`desktop_producer_activation_probe`), confirming
again that task naming is not role selection.

Desktop evidence references:

- Parent desktop task: `019f556b-b39a-76f3-b965-4d08685fa7aa`
- Child task: `019f556b-d281-7381-8074-79e232075dae`
- SubagentStart payload: `production/session-logs/agents-start.jsonl`, line 15
- Child metadata and role instructions:
  `/Users/yongatron/.codex/sessions/2026/07/12/rollout-2026-07-12T16-22-37-019f556b-d281-7381-8074-79e232075dae.jsonl`,
  lines 1 and 3

The V2 keys are present in current Codex source and accepted by installed
`0.144.x` binaries, but they are not listed in the public configuration
reference. They are therefore recorded as an experimental user-level
workaround, not a distributable CCGS project setting.

## Interpretation

Trust activation, `.env*` protection, project skills, hooks, configured model
slugs, and built-in footer behavior are live-verified. CCGS custom roles are
verified under a `gpt-5.5` V1 parent and under the experimental Sol V2 override
in both CLI and a fresh desktop task. Stock Sol V2 without the override remains
blocked. Role-dependent gates require exact role metadata, matching developer
instructions, configured model and effort, and `fork_turns: "none"` for V2;
task names, task paths, nicknames, self-identification, and the parent tool
result alone are insufficient.

Desktop verification used a separately created fresh Codex task plus direct
inspection of its retained hook and child-session evidence; it did not use
Computer Use or infer activation from the UI response.
