---
name: playtest-report
description: "Generates a structured playtest report template or analyzes existing playtest notes into a structured format. Use this to standardize playtest feedback collection and analysis for Codex Game Studios."
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

Use `design/game-brief.md` as concept/requirement context at project minimal; otherwise
use the concept and applicable GDDs. Read optional architecture/art/index inputs
when present, but their absence alone is not a blocker for the lighter tier.
Preserve explicit constraints, engine checks, user decisions and actual observed
playtest/evidence requirements. Route follow-ups using the effective workflow.


## Phase 1: Parse Arguments

Resolve the review mode (once, store for all gate spawns this run):
Read and apply the shared `review-mode` contract in
`.codex/docs/director-gates.md` for this run. Pass any `--review` flag unchanged.
Stop review routing on INVALID/NOT ASSESSED; retain its value and source for all gate checks.

Determine the mode:

- `new` → generate a blank playtest report template
- `analyze [path]` → read raw notes and fill in the template with structured findings

---

## Phase 2A: New Template Mode

Generate this template and output it to the user:

```markdown
# Playtest Report

## Session Info
- **Date**: [Date]
- **Build**: [Version/Commit]
- **Duration**: [Time played]
- **Tester**: [Name/ID]
- **Platform**: [PC/Console/Mobile]
- **Input Method**: [KB+M / Gamepad / Touch]
- **Session Type**: [First time / Returning / Targeted test]

## Test Focus
- **Hypothesis**: [What feeling, behavior, or evidence this playtest is probing]
- **Setup/build**: [Build, commit, command, save state, or scenario if known]
- **Observation prompts**:
  1. [Specific thing to watch for]
  2. [Specific thing to watch for]
  3. [Optional specific thing to watch for]
  4. [Optional specific thing to watch for]
- **Verdict/evidence to return**: [User-owned pass/fail/needs-rethink verdict plus notes, screenshots, logs, or report path]

## First Impressions (First 5 minutes)
- **Understood the goal?** [Yes/No/Partially]
- **Understood the controls?** [Yes/No/Partially]
- **Emotional response**: [Engaged/Confused/Bored/Frustrated/Excited]
- **Notes**: [Observations]

## Gameplay Flow
### What worked well
- [Observation 1]

### Pain points
- [Issue 1 -- Severity: High/Medium/Low]

### Confusion points
- [Where the player was confused and why]

### Moments of delight
- [What surprised or pleased the player]

## Bugs Encountered
| # | Description | Severity | Reproducible |
|---|-------------|----------|-------------|

## Feature-Specific Feedback
### [Feature 1]
- **Understood purpose?** [Yes/No]
- **Found engaging?** [Yes/No]
- **Suggestions**: [Tester suggestions]

## Quantitative Data (if available)
- **Deaths**: [Count and locations]
- **Time per area**: [Breakdown]
- **Items used**: [What and when]
- **Features discovered vs missed**: [List]

## Overall Assessment
- **Would play again?** [Yes/No/Maybe]
- **Difficulty**: [Too Easy / Just Right / Too Hard]
- **Pacing**: [Too Slow / Good / Too Fast]
- **Session length preference**: [Shorter / Good / Longer]

## Top 3 Priorities from this session
1. [Most important finding]
2. [Second priority]
3. [Third priority]
```

---

## Phase 2B: Analyze Mode

Read the raw notes at the provided path. Cross-reference with existing design documents. Fill in the template above with structured findings. Flag any playtest observations that conflict with design intent.

If the notes omit a specific hypothesis or focus, state that gap before
analysis and ask for or infer only a provisional `Playtest focus:` from the
notes. Do not route the user to another manual playtest without a concrete
hypothesis, setup/build if known, 2-4 observation prompts, and the
verdict/evidence the user should return.

---

## Phase 3: Action Routing

Categorize all findings into four buckets:

- **Design changes needed** — fun issues, player confusion, broken mechanics, observations that conflict with the GDD's intended experience
- **Balance adjustments** — numbers feel wrong, difficulty too spiked or too flat
- **Bug reports** — clear implementation defects that are reproducible
- **Polish items** — not blocking progress, but friction or feel issues for later

Present the categorized list, then route:

- **Design changes:** "Run `$propagate-design-change [path]` on the affected design document to find downstream impacts before making changes."
- **Balance adjustments:** "Run `$balance-check [system]` to verify the full balance picture before tuning values."
- **Bugs:** "Use `$bug-report` to formally track these."
- **Polish items:** "Add to the polish backlog in `production/` when the team reaches that phase."

---

## Phase 3b: Creative Director Player Experience Review

**Review mode check** — apply before spawning CD-PLAYTEST:
- `solo` → skip. Note: "CD-PLAYTEST skipped — Solo mode." Proceed to Phase 4 (save the report).
- `lean` → skip (not a PHASE-GATE). Note: "CD-PLAYTEST skipped — Lean mode." Proceed to Phase 4 (save the report).
- `full` → spawn as normal.

After categorising findings, spawn `creative-director` via Codex subagent delegation using gate **CD-PLAYTEST** (`.codex/docs/director-gates.md`).

Pass: the structured report content, game pillars and core fantasy (from `design/gdd/game-concept.md`), the specific hypothesis being tested.

Present the creative director's assessment before saving the report. If CONCERNS or REJECT, add a `## Creative Director Assessment` section to the report capturing the verdict and feedback. If APPROVE, note the approval in the report.

---

## Phase 4: Save Report

Ask: "May I write this playtest report to `production/qa/playtests/playtest-[date]-[tester].md`?"

If yes, write the file, creating the directory if needed.

---

## Phase 5: Next Steps

Verdict: **COMPLETE** — playtest report generated.

- Act on the highest-priority finding category first.
- After addressing design changes: re-run `$design-review` on the updated GDD.
- After fixing bugs: re-run `$bug-triage` to update priorities.
- If another user-owned playtest is the routed next step, include `Playtest
  focus:` with the specific hypothesis, setup/build if known, 2-4 observation
  prompts, and the verdict/evidence the user should return. The focus brief
  narrows the test but leaves game-feel and balance decisions to the user.

## Ported metadata

The following upstream metadata is preserved as context only; Codex does not enforce it from skill frontmatter.

- `argument-hint: "[new|analyze path-to-notes] [--review full|lean|solo]"`
- `user-invocable: true`
- `allowed-tools: Read, Glob, Grep, Write, Codex subagent delegation, numbered choice prompt`

## Codex Model Guidance

Suggested model: `gpt-5.6-sol`. This is guidance only; Codex does not enforce a model from skill frontmatter.
