## 4b. QA Lead Story Readiness Gate

**Review mode check** — apply before spawning QL-STORY-READY:
- `solo` → skip. Note: "QL-STORY-READY skipped — Solo mode." Proceed to Step 5 (present stories for review).
- `lean` → skip (not a PHASE-GATE). Note: "QL-STORY-READY skipped — Lean mode." Proceed to Step 5 (present stories for review).
- `full` → spawn as normal.

After decomposing all stories (Step 4 complete) but before presenting them for write approval, spawn `qa-lead` via Codex subagent delegation using gate **QL-STORY-READY** (`.codex/docs/director-gates.md`).

Pass: the full story list with acceptance criteria, story types, and TR-IDs; the epic's GDD acceptance criteria for reference.

Present the QA lead's assessment. For each story flagged as GAPS or INADEQUATE, revise the acceptance criteria before proceeding — stories with untestable criteria cannot be implemented correctly. Once all stories reach ADEQUATE, proceed.

**Before generating test specs**: Glob `production/qa/qa-plan-*.md` for the most recently modified file. If found, read it and check whether it contains test case specifications for the stories in this epic (look for story titles or slugs in the plan's Automated Tests Required section). If matching specs exist:
- Use `numbered choice prompt`:
  - Prompt: "A QA plan exists at [path] with test specs for some of these stories. How do you want to proceed?"
  - Options:
    - `Use existing specs from the QA plan — embed them into the story files (Recommended)`
    - `Ask qa-lead to generate fresh specs — override the QA plan`
    - `Skip test spec generation — I'll fill in ## QA Test Cases manually`
- If "Use existing specs": extract the test case specs from the qa-plan for each matching story and embed them directly into the `## QA Test Cases` section. No qa-lead spawn needed for those stories. Only spawn qa-lead for stories with no coverage in the qa-plan.
- If "Generate fresh": proceed with the qa-lead spawn below as normal.
- If "Skip": leave `## QA Test Cases` with a placeholder: `*Test cases not yet defined — run $qa-plan to generate them.*`

**After ADEQUATE** (or after qa-plan import): for every Logic and Integration story, ask the qa-lead to produce concrete test case specifications — one per acceptance criterion — in this format:

```
Test: [criterion text]
  Given: [precondition]
  When: [action]
  Then: [expected result / assertion]
  Edge cases: [boundary values or failure states to test]
```

For Visual/Feel and UI stories, produce manual verification steps instead:
```
Manual check: [criterion text]
  Setup: [how to reach the state]
  Verify: [what to look for]
  Pass condition: [unambiguous pass description]
```

These test case specs are embedded directly into each story's `## QA Test Cases` section. The developer implements against these cases. The programmer does not write tests from scratch — QA has already defined what "done" looks like.

---
