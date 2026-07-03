---
name: studio-status
description: "Render the Codex Game Studios project-stage, review-mode, and active-session breadcrumb from shared project state."
---

# Studio Status

Use this skill when the user asks for current Game Studios state, phase, review mode, active session context, or the project-specific breadcrumb that complements Codex native `[tui].status_line` built-in footer items.

Read these shared neutral files if they exist:
- `production/stage.txt`
- `production/review-mode.txt`
- `production/session-state/active.md`

If a file is missing, report it as `unset` rather than creating it. Do not write to project files from this status skill.

Return a concise status block:

```text
Stage: <stage or unset>
Review mode: <review mode or unset>
Active session: <first heading or summary from active.md, or unset>
```

This skill preserves the game-stage/review/session breadcrumb from the upstream
shell statusline as an on-demand Codex-native workflow. Codex built-in model,
context, current-directory, and git footer items remain configured separately
through `[tui].status_line` when project config is installed. A real footer
`Stage:` item is blocked until Codex documents support for project custom footer
items; do not add an unverified fake status-line entry.
