## Phase 8: Surface the Next Story

After completion, help the developer keep momentum:

1. Read the current sprint plan from `production/sprints/`.
2. Find stories that are:
   - Status: READY or NOT STARTED
   - Not blocked by other incomplete stories
   - In the Must Have or Should Have tier

Present:

```
### Next Up
The following stories are ready to pick up:
1. [Story name] — [1-line description] — Est: [X hrs]
2. [Story name] — [1-line description] — Est: [X hrs]

Run `$story-readiness [path]` to confirm a story is implementation-ready
before starting.
```

If all Must Have stories have passing completion evidence (none Blocked or NOT ASSESSED):

```
### Sprint Close-Out Sequence

All Must Have stories are complete. QA sign-off is required before advancing.
Run these in order:

1. `$smoke-check sprint` — verify the critical path still works end-to-end
2. `$team-qa sprint` — full QA cycle: test case execution, bug triage, sign-off report
3. `$retrospective` — capture what went well, what didn't, and action items for the next sprint
4. `$gate-check` — advance to the next phase once QA approves (only if advancing a phase)
5. `$sprint-plan new` — plan the next sprint, incorporating velocity data and retrospective action items

Do not run `$gate-check` until `$team-qa` returns APPROVED or APPROVED WITH CONDITIONS.
```

If Must Have stories remain Blocked or NOT ASSESSED, list those first and route
to their missing verification or fix; do not claim the sprint is complete.

If there are Should Have stories still unstarted, surface them alongside the close-out sequence so the user can choose: close the sprint now, or pull in more work first.

If no more stories are ready but Must Have stories are still In Progress (not Complete):
"No more stories ready to start — [N] Must Have stories still in progress. Continue implementing those before sprint close-out."

After surfacing the next-story or sprint close-out inventory, read or silently
refresh the `## Session Worklist` in `production/session-state/active.md`.
Recommend one
best next action across the ready-story, smoke-check, QA, gate, tech-debt, and
handoff lanes. Use `request_user_input` when available only if 2-3 lanes are
genuinely tied.

---
