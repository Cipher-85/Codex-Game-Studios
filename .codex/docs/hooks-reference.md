# Active Hooks

Hooks are configured in `.codex/hooks.json` and fire automatically after the
project is trusted by Codex. The scripts below preserve upstream hook behavior
with Codex adapter edits: `.codex` paths, `.agents/skills` paths, `$skill`
invocation text, `CCGS_ROOT` root-stable execution, and Codex hook payload
fields.

| Hook | Event | Trigger | Action |
| ---- | ----- | ------- | ------ |
| `validate-secrets.sh` | PreToolUse (Bash) | Bash commands | Blocks `.env` secret-file reads, writes, and redirections from `tool_input.command` |
| `validate-commit.sh` | PreToolUse (Bash) | `git commit` commands | Validates design doc sections, JSON data files, hardcoded values, TODO format |
| `validate-push.sh` | PreToolUse (Bash) | `git push` commands | Warns on pushes to protected branches (`develop`, `main`, `master`) |
| `validate-write.sh` | PreToolUse (`apply_patch`) | Supported literal patch payloads | Advises on registry identity/status changes and protected artifacts; never grants or blocks writes |
| `validate-assets.sh` | PostToolUse (`apply_patch`) | Asset file changes | Checks naming conventions and JSON validity for files in `assets/`; feedback is after the edit and does not roll back side effects |
| `session-start.sh` | SessionStart | Session begins | Records a local branch/HEAD/timestamp review baseline; previews the bounded canonical handoff before active state; recommends Agent Bindery's global `$resume-from-handoff` |
| `detect-gaps.sh` | SessionStart | Session begins | Detects fresh projects (suggests $start) and missing documentation when code/prototypes exist, suggests $reverse-document or $project-stage-detect |
| `pre-compact.sh` | PreCompact | Context compression | Shows substantive `active.md` first with a bounded handoff fallback; elevates handoff when active state is missing or pointer-only |
| `post-compact.sh` | PostCompact | After compaction | Restores the same active-first/handoff-fallback order and elevates canonical handoff when needed |
| `session-stop.sh` | Stop | Session ends | Summarizes accomplishments and updates session log |
| `log-agent.sh` | SubagentStart | Agent spawned | Audit trail start — logs subagent invocation with timestamp |
| `log-agent-stop.sh` | SubagentStop | Agent stops | Audit trail stop — completes subagent record |
| `validate-skill-change.sh` | PostToolUse (`apply_patch`) | Skill file changes | Advises running `$skill-test` after any `.agents/skills/` file is written or edited; feedback is after the edit |
| `studio-status-on-start.sh` | SessionStart | Session begins | Codex-additive status summary for stage, review mode, and active session state |

The asset and skill hooks intentionally remain PostToolUse hooks, matching the
upstream timing. A future PreToolUse `apply_patch` validator could add pre-edit
hardening, but it is not required for upstream parity.

`notify.sh` is intentionally not installed. Upstream used Claude's
`Notification` hook event, which Codex project hooks do not expose. Configure
native Codex notifications at user scope instead; project-local config must not
set notification keys.

Hook reference documentation: `.codex/docs/hooks-reference/`
Hook input schema documentation: `.codex/docs/hooks-reference/hook-input-schemas.md`

## Advisory artifact checks

`validate-write.sh` runs at PreToolUse for `apply_patch`, using
`.codex/lib/artifact_guards.py`. It warns before protected-artifact edits and about
canonical registry deletion, changed identities and invalid statuses in a
literal patch preview. Warnings use JSON on stdout: `systemMessage` surfaces
the warning in the UI, and `hookSpecificOutput.additionalContext` supplies the
same warning to the model for `PreToolUse`. Quiet checks emit nothing. The hook
exits zero without a permission decision or input rewrite; existing approval
and blocking rules still apply. It writes no log or source file. Missing Python
or a failed validator produces the same structured NOT ASSESSED advisory.

Malformed, oversized, ambiguous, out-of-root and symlink payloads report NOT
ASSESSED. It does not intercept general shell writes, establish full YAML schema
validity or prove a patch was applied. Restart/trust the project in a native
session before claiming the new hook is active there; fixture execution alone
proves only the handler behavior. Section-based reads are explicit workflow
calls, not a universal file-read hook. Claimed delegated artifacts are verified
by the parent against approved paths, then code receives the engine review.
