---
name: studio-status
description: "Render the Codex Game Studios project-stage, review-mode, and active-session breadcrumb from shared project state."
---

## Workflow policy

Before artifact reads, apply `.codex/docs/workflow-modes.md` and run the shared
`project_config.py workflow` reader. Retain tier/source, density and granularity;
resolve an exact GDD stem per system when applicable. Use `project_tier` and
`design_source` for project inputs; `tier` selects only that system's GDD sections.
A system override does not waive project-wide architecture. INVALID/NOT ASSESSED stops
the affected workflow. The prerequisite lists below are the compatibility/full
baseline: apply the shared tier table to reads, required sections, findings and
next actions. Pass that policy and the actual requirement source to delegated
roles. Review-mode filtering and required verification remain independent.


# Studio Status

Use this skill when the user asks for current Game Studios state, phase, review mode, active session context, or the project-specific breadcrumb that complements Codex native `[tui].status_line` built-in footer items.

Read stage through `project_config.py stage` and the active session from
`production/session-state/active.md` if present; missing values are `unset`.
Show stage provenance and any shadowed legacy value; invalid or unavailable
configuration is INVALID/NOT ASSESSED, never an inferred recorded stage. Resolve review mode using the shared
`review-mode` contract in `.codex/docs/director-gates.md` with the bound root.
Show its value and source, including `lean (default)` when no setting exists.
On invalid configuration display `INVALID` with the diagnostic; unavailable
Python/helper is `NOT ASSESSED`. Neither error substitutes a review mode.

Return a concise status block:

```text
Stage: <resolved stage (source), unset, INVALID, or NOT ASSESSED>
Review mode: <resolved value (source), INVALID, or NOT ASSESSED>
Active session: <first heading or summary from active.md, or unset>
```

Status is read-only. Workflow and recorded stage use their shared readers;
session text remains a local checkpoint. Stage is never changed by displaying it.

This skill preserves the game-stage/review/session breadcrumb from the upstream
shell statusline as an on-demand Codex-native workflow. Codex built-in model,
context, current-directory, and git footer items remain configured separately
through `[tui].status_line` when project config is installed. A real footer
`Stage:` item is blocked until Codex documents support for project custom footer
items; do not add an unverified fake status-line entry.

## Ported metadata

This is a Codex-native support skill. It has no upstream Claude skill equivalent.
