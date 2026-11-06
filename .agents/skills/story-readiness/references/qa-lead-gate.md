## Phase 8: Director Gate — Story Readiness Review

Apply the review mode resolved in Phase 0 before spawning QL-STORY-READY:

- `solo` → skip. Note: "QL-STORY-READY skipped — Solo mode." Proceed to close.
- `lean` → skip. Note: "QL-STORY-READY skipped — Lean mode." Proceed to close.
- `full` → spawn as normal.

Spawn `qa-lead` via Codex subagent delegation using gate **QL-STORY-READY** (`.codex/docs/director-gates.md`).

Pass the following context:
- Story title
- Acceptance criteria list (all items from the story's acceptance criteria section)
- Dependency status (all dependencies listed and their current state: exist / DRAFT / missing)
- Overall verdict (READY / NEEDS WORK / BLOCKED) from Phase 4

Handle the verdict per standard rules in `director-gates.md`:
- **ADEQUATE** → story is cleared. Proceed to close.
- **GAPS [list]** → surface the specific gaps to the user via `numbered choice prompt`:
  options: `Update story with suggested gaps` / `Accept and proceed anyway` / `Discuss further`.
- **INADEQUATE** → report BLOCKED with the specific gaps. Offer revision or
  discussion; require revision and a cleared gate before sprint inclusion. An
  administrative override must retain BLOCKED and cannot establish readiness.

---
