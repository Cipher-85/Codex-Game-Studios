# CCGS orientation

Slot: `modules.orientation` in `.agent-continuity.toml`.

Orient the worklist against the CCGS development pipeline before recommending
work.

## Sources

- `production/stage.txt` for the recorded stage.
- `.codex/docs/workflow-catalog.yaml` for the phase sequence and required steps.
- The handoff's current-stage and next-action fields.
- The slice source named by the handoff's `Slice State Source` pointer.

## Phase guard

Report the recorded stage, matching catalog phase, first incomplete required
step, next gate, active milestone and sprint, and any disagreement between
those sources. Label disagreement as `unset stage`, `handoff drift`, or
`out-of-phase backlog`; do not silently choose which source is correct.

## Vertical-slice forcing function

Before ranking work, identify the current playable slice, the last successful
end-to-end boot or playtest with its provenance, and the smallest next playable
advance no larger than one session. Classify each candidate as:

- `extend` — directly enlarges or completes the playable slice.
- `feed` — supplies required design, art, QA, or architecture input.
- `carve-out` — useful work outside the slice path.

Owed verification, gates, and blockers come first. Otherwise prefer the
smallest `extend` candidate, then required `feed` work. Treat an unapproved
game-feel or balance choice as a blocker rather than choosing it for the user.
Size work in sessions, not calendar estimates.
