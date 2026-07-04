# Active Hooks

Hooks are configured in `.codex/hooks.json` and fire automatically after the
project is trusted by Codex. The scripts below preserve upstream hook behavior
with Codex adapter edits: `.codex` paths, `.agents/skills` paths, `$skill`
invocation text, `CCGS_ROOT` root-stable execution, and Codex hook payload
fields.

| Hook | Event | Trigger | Action |
| ---- | ----- | ------- | ------ |
| `validate-commit.sh` | PreToolUse (Bash) | `git commit` commands | Validates design doc sections, JSON data files, hardcoded values, TODO format |
| `validate-push.sh` | PreToolUse (Bash) | `git push` commands | Warns on pushes to protected branches (`develop`, `main`, `master`) |
| `validate-assets.sh` | PostToolUse (`apply_patch`) | Asset file changes | Checks naming conventions and JSON validity for files in `assets/`; feedback is after the edit and does not roll back side effects |
| `session-start.sh` | SessionStart | Session begins | Loads sprint context, milestone, git activity; detects and previews active session state file for recovery |
| `detect-gaps.sh` | SessionStart | Session begins | Detects fresh projects (suggests $start) and missing documentation when code/prototypes exist, suggests $reverse-document or $project-stage-detect |
| `pre-compact.sh` | PreCompact | Context compression | Dumps session state (active.md, modified files, WIP design docs) into conversation before compaction so it survives summarization |
| `post-compact.sh` | PostCompact | After compaction | Reminds Codex to restore session state from `active.md` checkpoint |
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
