---
name: start
description: "First-time onboarding — asks where you are, then guides you to the right workflow. No assumptions for Codex Game Studios."
---

## Source scope

Before source/content inspection or source writes, apply **Source scope** in
`.codex/docs/technical-config.md` and run `project_config.py code-root`. Use its
listed paths, resolving verified custom paths with `--path`. Unresolved/invalid
scope leaves dependent checks NOT ASSESSED; continue independent work. A
resolved path is not an executed scan. Do not substitute or create `src/`.

## Technical configuration

Before using engine, framework, platform or performance fields, read
`.codex/docs/technical-config.md` and run `project_config.py technical`. Use its
resolved values/provenance for typed fields; the technical-preferences reads
below still supply custom prose, policies and routing notes. Check conflicts
and field-specific readiness before affected work. Pin agreement is not an
engine run; runner availability needs actual metadata/help verification. Keep
estimates separate from measured evidence and preserve existing pins/runners.


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

Use the shared stage reader before initialization. Preserve an existing stage;
for unset stage, show the proposed stage and the reader's exact write_target,
then follow its approval/readback procedure. Apply workflow to onboarding paths:
minimal uses brief and engine, standard the reduced design set. Do not create
root YAML or infer rigor. The template's standard recommendation is not a stored
selection and this workflow does not implement a general settings writer.


# Guided Onboarding

This skill can initialize the recorded stage through the shared `stage` contract and, only when review routing
is unconfigured, `production/review-mode.txt`. Show each proposed write and obtain
approval; preserve configured review settings from the shared resolver.

This skill is the entry point for new users. It does NOT assume you have a game idea, an engine preference, or any prior experience. It asks first, then routes you to the right workflow.

---

## Phase 1: Detect Project State

Before asking anything, silently gather context so you can tailor your guidance. Do NOT show these results unprompted — they inform your recommendations, not the conversation opener.

Check:
- **Engine configured?** Read `.codex/docs/technical-preferences.md`. If the Engine field contains `[TO BE CONFIGURED]`, the engine is not set.
- **Game concept exists?** Check for `design/gdd/game-concept.md`.
- **Source code exists?** Inspect source files in the resolved scope using the project's languages.
  If unresolved, record NOT ASSESSED and continue onboarding; do not infer an empty project.
- **Prototypes exist?** Check for subdirectories in `prototypes/`.
- **Design docs exist?** Count markdown files in `design/gdd/`.
- **Production artifacts?** Check for files in `production/sprints/` or `production/milestones/`.

Store these findings internally to validate the user's self-assessment and tailor recommendations.

---

## Phase 2: Ask Where the User Is

This is the first thing the user sees. Use `numbered choice prompt` with these exact options so the user can click rather than type:

- **Prompt**: "Welcome to Codex Game Studios! Before I suggest anything, I'd like to understand where you're starting from. Where are you at with your game idea right now?"
- **Options**:
  - `A) No idea yet` — I don't have a game concept at all. I want to explore and figure out what to make.
  - `B) Vague idea` — I have a rough theme, feeling, or genre in mind (e.g., "something with space" or "a cozy farming game") but nothing concrete.
  - `C) Clear concept` — I know the core idea — genre, basic mechanics, maybe a pitch sentence — but haven't formalized it into documents yet.
  - `D) Existing work` — I already have design docs, prototypes, code, or significant planning done. I want to organize or continue the work.

Wait for the user's selection. Do not proceed until they respond.

---

## Phase 3: Route Based on Answer

#### If A: No idea yet

The user needs creative exploration before anything else.

1. Acknowledge that starting from zero is completely fine
2. Briefly explain what `$brainstorm` does (guided ideation using professional frameworks — MDA, player psychology, verb-first design). Mention that it has two modes: `$brainstorm open` for fully open exploration, or `$brainstorm [hint]` if they have even a vague theme (e.g., "space", "cozy", "horror").
3. Recommend running `$brainstorm open` as the next step, but invite them to use a hint if something comes to mind
4. Show the recommended path:
   **Concept phase:**
   - `$brainstorm open` — discover your game concept
   - `$setup-engine` — configure the engine (brainstorm will recommend one)
   - `$prototype` — throwaway concept build: validate the core idea is fun before designing (1–3 days)
   - `$art-bible` — define visual identity (uses the Visual Identity Anchor brainstorm produces)
   - `$map-systems` — decompose the concept into systems
   - `$design-system` — author a GDD for each MVP system
   - `$review-all-gdds` — cross-system consistency check
   - `$gate-check` — validate readiness before architecture work
   **Architecture phase:**
   - `$create-architecture` — produce the master architecture blueprint and Required ADR list
   - `$architecture-decision (×N)` — record key technical decisions, following the Required ADR list
   - `$create-control-manifest` — compile decisions into an actionable rules sheet
   - `$architecture-review` — validate architecture coverage
   **Pre-Production phase:**
   - `$ux-design` — author UX specs for key screens (main menu, HUD, core interactions)
   - `$vertical-slice` — production-quality end-to-end build to validate the full game loop
   - `$playtest-report (×1+)` — document each vertical slice playtest session
   - `$create-epics` — map systems to epics
   - `$create-stories` — break epics into implementable stories
   - `$sprint-plan` — plan the first sprint
   **Production phase:** → pick up stories with `$dev-story`

#### If B: Vague idea

1. Ask them to share their vague idea — even a few words is enough
2. Validate the idea as a starting point (don't judge or redirect)
3. Recommend running `$brainstorm [their hint]` to develop it
4. Show the recommended path:
   **Concept phase:**
   - `$brainstorm [hint]` — develop the idea into a full concept
   - `$setup-engine` — configure the engine
   - `$prototype` — throwaway concept build: validate the core idea is fun before designing (1–3 days)
   - `$art-bible` — define visual identity (uses the Visual Identity Anchor brainstorm produces)
   - `$map-systems` — decompose the concept into systems
   - `$design-system` — author a GDD for each MVP system
   - `$review-all-gdds` — cross-system consistency check
   - `$gate-check` — validate readiness before architecture work
   **Architecture phase:**
   - `$create-architecture` — produce the master architecture blueprint and Required ADR list
   - `$architecture-decision (×N)` — record key technical decisions, following the Required ADR list
   - `$create-control-manifest` — compile decisions into an actionable rules sheet
   - `$architecture-review` — validate architecture coverage
   **Pre-Production phase:**
   - `$ux-design` — author UX specs for key screens (main menu, HUD, core interactions)
   - `$vertical-slice` — production-quality end-to-end build to validate the full game loop
   - `$playtest-report (×1+)` — document each vertical slice playtest session
   - `$create-epics` — map systems to epics
   - `$create-stories` — break epics into implementable stories
   - `$sprint-plan` — plan the first sprint
   **Production phase:** → pick up stories with `$dev-story`

#### If C: Clear concept

1. Ask them to describe their concept in one sentence — genre and core mechanic. Use plain text, not numbered choice prompt (it's an open response).
2. Acknowledge the concept, then use `numbered choice prompt` to offer two paths:
   - **Prompt**: "How would you like to proceed?"
   - **Options**:
     - `Formalize it first` — Run `$brainstorm [concept]` to structure it into a proper game concept document
     - `Jump straight in` — Go to `$setup-engine` now and write the GDD manually afterward
3. Show the recommended path:
   **Concept phase:**
   - `$brainstorm` or `$setup-engine` — (their pick from step 2)
   - `$prototype` — throwaway concept build: validate the core idea is fun before designing (1–3 days)
   - `$art-bible` — define visual identity (after brainstorm if run, or after concept doc exists)
   - `$design-review` — validate the concept doc
   - `$map-systems` — decompose the concept into individual systems
   - `$design-system` — author a GDD for each MVP system
   - `$review-all-gdds` — cross-system consistency check
   - `$gate-check` — validate readiness before architecture work
   **Architecture phase:**
   - `$create-architecture` — produce the master architecture blueprint and Required ADR list
   - `$architecture-decision (×N)` — record key technical decisions, following the Required ADR list
   - `$create-control-manifest` — compile decisions into an actionable rules sheet
   - `$architecture-review` — validate architecture coverage
   **Pre-Production phase:**
   - `$ux-design` — author UX specs for key screens (main menu, HUD, core interactions)
   - `$vertical-slice` — production-quality end-to-end build to validate the full game loop
   - `$playtest-report (×1+)` — document each vertical slice playtest session
   - `$create-epics` — map systems to epics
   - `$create-stories` — break epics into implementable stories
   - `$sprint-plan` — plan the first sprint
   **Production phase:** → pick up stories with `$dev-story`

#### If D: Existing work

1. Share what you found in Phase 1:
   - "I can see you have [X source files / Y design docs / Z prototypes]..."
   - "Your engine is [configured as X / not yet configured]..."

2. **Sub-case D1 — Early stage** (engine not configured or only a game concept exists):
   - Recommend `$setup-engine` first if engine not configured
   - Then `$project-stage-detect` for a gap inventory

   **Sub-case D2 — GDDs, ADRs, or stories already exist:**
   - Explain: "Having files isn't the same as the template's skills being able to use them. GDDs might be missing required sections. `$adopt` checks this specifically."
   - Recommend:
     1. `$project-stage-detect` — understand what phase and what's missing entirely
     2. `$adopt` — audit whether existing artifacts are in the right internal format

3. Show the recommended path for D2:
   - `$project-stage-detect` — phase detection + existence gaps
   - `$adopt` — format compliance audit + migration plan
   - `$setup-engine` — if engine not configured
   - `$design-system retrofit [path]` — fill missing GDD sections
   - `$architecture-decision retrofit [path]` — add missing ADR sections
   - `$architecture-review` — bootstrap the TR requirement registry
   - `$gate-check` — validate readiness for next phase

---

## Phase 3c: Offer Initial Stage

After confirming the starting path, resolve `project_config.py stage`. Preserve
an existing recorded stage. If unset, propose the mapped initial stage and
follow the exact-target approval/readback contract in `config-resolution.md`.

Stage mapping:
- **Path A, B, or C (starting from scratch)**: write `Concept`
- **Path D, existing project, engine not configured or only a game concept exists**: write `Concept`
- **Path D, existing project with GDDs but no architecture documents**: write `Systems Design`
- **Path D, existing project with full architecture (ADRs, architecture doc)**: write `Technical Setup`

Show the proposed stage and the resolver's write_target with the exact diff.
Ask "May I write this to [write_target]?" before initialization. Re-resolve after
an approved write and name its verified value/source. If declined, continue
orientation with recorded stage unset; do not claim it was saved.

---

## Phase 3b: Set Review Mode

Resolve through the shared `review-mode` contract in
`.codex/docs/director-gates.md`, passing any `--review` flag unchanged.
If configuration is INVALID/NOT ASSESSED, show the diagnostic and stop review
routing; do not initialize a fallback file.

If `configured: true`, show the returned value/source and continue. This includes
project/local YAML, legacy values, explicit rigor expansion, and per-run flags.
Preserve those files and skip review setup; a missing legacy file is not a reason
to create one that could shadow rigor or a YAML setting.

If `configured: false`, explain that the operational default is `lean` and offer:

1. Full — all declared director gates.
2. (Recommended) Lean — PHASE-GATE directors only.
3. Solo — no director gates; ordinary pipeline agents keep their declared roles.

After selection, show the exact single-line value (`full`, `lean`, or `solo`) and
ask "May I write this to `production/review-mode.txt`?" with `a. yes` / `b. no`.
Create its parent only after approval. Re-run the shared contract after writing;
a declined write leaves the validated default in use. Keep YAML assignments as
`$settings` previews; this setup does not edit YAML or persist a per-run flag.

---

## Phase 4: Confirm Before Proceeding

After presenting the recommended path, use `numbered choice prompt` to ask the user which step they'd like to take first. Never auto-run the next skill.

- **Prompt**: "Would you like to start with [recommended first step]?"
- **Options**:
  - `Yes, let's start with [recommended first step]`
  - `I'd like to do something else first`

---

## Phase 5: Hand Off

When the user confirms their next step, respond with a single short line: "Type `[skill command]` to begin." Nothing else. Do not re-explain the skill or add encouragement. The `$start` skill's job is done.

Verdict: **COMPLETE** — user oriented and handed off to next step.

---

## Edge Cases

- **User picks D but project is empty**: Gently redirect — "It looks like the project is a fresh template with no artifacts yet. Would Path A or B be a better fit?"
- **User picks A but project has code**: Mention what you found — "I noticed there's already code in `[actual source path]`. Did you mean to pick D (existing work)?"
- **User is returning (engine configured, concept exists)**: Skip onboarding entirely — "It looks like you're already set up! Your engine is [X] and you have a game concept at `design/gdd/game-concept.md`. Review mode: `[value and source from the shared review-mode result]`. Want to pick up where you left off? Try `$sprint-plan` or just tell me what you'd like to work on."
- **User doesn't fit any option**: Let them describe their situation in their own words and adapt.

---

## Collaborative Protocol

1. **Ask first** — never assume the user's state or intent
2. **Present options** — give clear paths, not mandates
3. **User decides** — they pick the direction
4. **No auto-execution** — recommend the next skill, don't run it without asking
5. **Adapt** — if the user's situation doesn't fit a template, listen and adjust

## Ported metadata

The following upstream metadata is preserved as context only; Codex does not enforce it from skill frontmatter.

- `argument-hint: "[no arguments]"`
- `user-invocable: true`
- `allowed-tools: Read, Glob, Grep, Write, numbered choice prompt`

## Codex Model Guidance

Suggested model: `gpt-5.6-sol`. This is guidance only; Codex does not enforce a model from skill frontmatter.
