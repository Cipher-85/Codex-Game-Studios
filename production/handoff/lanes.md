# CCGS work lanes

Slot: `modules.lanes` in `.agent-continuity.toml`.

## Sources

- `production/sprint-status.yaml` for story status when present.
- The handoff's tracked open items, blockers, owed verification, and gates.
- `production/session-state/active.md` for same-session routing evidence only.
- `.codex/docs/director-gates.md` and the installed `project_config.py review-mode`
  result for gates that apply in the active review mode. Pass any per-run flag;
  retain value/source and stop routing on INVALID/NOT ASSESSED. Legacy
  `production/review-mode.txt` is a resolver fallback, not a direct read here.

## Lanes

Group candidates into the smallest useful set of selectable lanes:

- Playable-slice advances.
- Sprint stories that are in progress or ready for development.
- Required design, architecture, art, or QA inputs.
- Explicit carve-outs such as defects, tooling, release work, or maintenance.

Carry blocked stories with their blocker text instead of hiding them. Every
lane names its start command or workflow and its rough size in sessions.

Gates are conditions on lanes, not standalone work. Surface owed FIRST
verification, design-review gates, story-done and smoke-check requirements,
director gates, and stage gates before the user chooses. A lane selection only
enters that workflow; it does not authorize its writes, builds, design choices,
commits, pushes, or later forks.

Before ranking required work, apply `.codex/docs/workflow-modes.md`. Report its
tier/source and distinguish optional artifacts from blockers. Bindery still owns
execution; this module only supplies project routing context.
