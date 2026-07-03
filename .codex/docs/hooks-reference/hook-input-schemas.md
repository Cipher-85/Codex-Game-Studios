# Hook Input/Output Schemas

This documents the Codex hook payload shapes used by this port. Fixtures live in
`.codex/tests/fixtures/hook-payloads/` and are the reference for behavioral hook
validation.

Every JSON fixture includes `hook_event_name`. Hooks should still be defensive
around optional fields because some lifecycle events do not need stdin to do
their work.

## PreToolUse

Fired before a tool is executed. PreToolUse hooks can allow the tool by exiting
0 or block by exiting 2 with a visible stderr message.

### PreToolUse: Bash

```json
{
  "hook_event_name": "PreToolUse",
  "tool_name": "Bash",
  "tool_input": {
    "command": "git commit -m 'feat: add player health system'",
    "description": "Commit changes with message",
    "timeout": 120000
  }
}
```

## PostToolUse

Fired after a tool completes. This port uses PostToolUse for `apply_patch`
advisories. Since the edit has already happened, these hooks can surface errors
or warnings but should not be documented as pre-edit prevention.

### PostToolUse: apply_patch

```json
{
  "hook_event_name": "PostToolUse",
  "tool_name": "apply_patch",
  "tool_input": {
    "patch": "*** Begin Patch\n*** Update File: assets/data/enemy_stats.json\n@@\n*** End Patch\n"
  }
}
```

## SubagentStart

Fired when a Codex subagent is spawned. Use `agent_type` for the registered
hyphenated role name.

```json
{
  "hook_event_name": "SubagentStart",
  "agent_id": "agent-fixture",
  "agent_type": "technical-director"
}
```

## SubagentStop

Fired when a Codex subagent stops. Use the same `agent_type` field as
SubagentStart.

```json
{
  "hook_event_name": "SubagentStop",
  "agent_id": "agent-fixture",
  "agent_type": "technical-director"
}
```

## SessionStart

Fired when a Codex session begins. CCGS startup hooks read project files directly
and do not require stdin; hook stdout is shown to Codex as session context.

## PreCompact

Fired before context window compression. CCGS compaction hooks read shared state
files directly and do not require stdin.

## PostCompact

Fired after context window compression. CCGS compaction hooks read shared state
files directly and do not require stdin.

## Stop

Fired when the Codex session ends. CCGS stop hooks read shared state files
directly and do not require stdin.

## Exit Code Reference

| Exit Code | Meaning | Applicable Events |
|-----------|---------|-------------------|
| 0 | Allow / Success | All events |
| 2 | Block | PreToolUse |
| Other | Hook error or advisory | All events |

## Notes

- JSON-capable hooks receive payloads on stdin. Use `INPUT=$(cat)` to capture.
- Parse with `jq` if available; fall back to portable shell parsing only where needed.
- File-change hooks should parse Codex `apply_patch` payloads, not legacy Write/Edit payloads.
- Subagent hooks should use `agent_type`; `agent_name` is a legacy Claude-style field.
- On Windows, `grep -P` is often unavailable. Use `grep -E` instead.
- Path separators may be `\` on Windows. Normalize with `sed 's|\\|/|g'` when comparing paths.
