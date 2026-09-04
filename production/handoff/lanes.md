# CCGS work lanes

Slot: `modules.lanes` in `.agent-continuity.toml`.

## Sources

- `production/sprint-status.yaml` for story status when present.
- The handoff's tracked open items, blockers, owed verification, and gates.
- `production/session-state/active.md` for same-session routing evidence only.
- `.codex/docs/director-gates.md` and `production/review-mode.txt` for gates
  that apply in the active review mode.

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
