# Session Continuity

Continuity keeps the next Codex session focused without depending on long chat
history. Prefer small, current, file-backed state over broad transcripts.

Agent Bindery owns the global `$handoff` and `$resume-from-handoff` skills and
their portable implementation. CCGS owns only `.agent-continuity.toml` and the
project modules under `production/handoff/`. Repo-local copies of either skill
are forbidden because they shadow the newer global pair.

## File Roles

- `.agent-continuity.toml`: authoritative mapping from Agent Bindery's generic
  continuity workflow to the CCGS paths and modules below.
- `production/session-state/active.md`: live working checkpoint and current
  session routing cache. Use for current task, progress checklist, decisions,
  files touched, open questions, owed verification, `## Session Worklist`, and
  `## Phase Guard`. It is derived local session state; once the underlying
  artifact or decision is approved, skills may update only this file without a
  separate write-approval prompt.
- `production/session-handoff.md`: canonical resume narrative when a session has
  enough state that another session should continue from it.
- `production/resume-index.md`: tracked accelerator derived by Agent Bindery's
  `$handoff`, capped at 10 KB, and disposable. Its slice hash may speed ordinary
  resume, but it never outranks the handoff, stage/sprint state, or current
  slice section.
- `production/session-archive.md`: historical record only. Do not read by default
  unless the user asks for older context or the handoff points there.
- `src/README.md`: slice history and real-versus-stubbed status when present.
  Use a handoff-declared path rather than assuming this filename. Ordinary
  resume reads at most the current 200-line/32-KiB section; only explicit
  `$resume-from-handoff deep [focus]` reads full slice history.
- `production/handoff/*.md`: project-specific phase/slice orientation, work
  lanes, verification integrity, and review-tier classification loaded through
  the manifest. These files configure the global skills; they do not implement
  them.

Missing files are unset state. Do not create continuity files unless the task or
skill calls for it.

The checkpoint exception is narrow. It never authorizes new design, game-feel,
balance, architecture, source, registry, index, status-file, commit, push,
branch, build, boot-smoke, mutating `gh`, or additional file changes.

## User-Owned Playtest Focus

When owed verification or the next valid lane is a user-owned playtest, preserve
a concrete focus brief in both the closeout and any `## Session Worklist` entry.
Use the label `Playtest focus:` and include:

- **Hypothesis**: what feeling, behavior, or evidence the playtest is probing.
- **Setup/build**: the build, command, save state, or scenario to use when
  known.
- **Observation prompts**: 2-4 observation prompts for specific things the
  user should watch for.
- **Verdict/evidence to return**: the user-owned pass/fail/needs-rethink
  verdict plus the notes, screenshots, logs, or playtest report path needed to
  make the evidence usable.

The brief narrows the test; it does not make the game-feel, balance, keep,
revert, or tune decision for the user.

## Pause Procedure

Before pausing a meaningful work unit, check whether the invoked workflow still
has automatic read-only phases remaining. Do not convert self-checks, readbacks,
scans, candidate discovery, context gathering, or validation summaries into
selectable `Next action` prompts. Keep going until a mutation prompt, design
decision, blocker, or true stop point.

1. Record what changed and what remains.
2. Record verification that passed, failed, was blocked, or was not run.
3. Read or silently refresh `## Session Worklist` in
   `production/session-state/active.md` and recommend the top valid lane.
   The final response must include completed work, verification or owed
   verification, and a numbered next-action prompt with exactly one
   `(Recommended)` option. Use this numeric fallback even when there is only one
   clear next lane:
   `Next action:` then `1. (Recommended) [action label] - [brief reason /
   command]`. The user can reply with `1`.
   If that lane is a user-owned playtest, include the preserved `Playtest
   focus:` brief before the next-action prompt.
4. Preserve exact next commands only when they are known to be useful.
5. Keep local-only notes out of tracked docs unless they are project state.
6. Suggest Agent Bindery's `$handoff [short-label]` when installed and the next
   session would otherwise need to reconstruct context.

Generic pause, stop, checkpoint, or resume-later wording authorizes this
recommendation only. The review-through-push transaction requires explicit
`$handoff` invocation or an equally explicit instruction to commit and push the
handoff.

The loaded Agent Bindery skill is authoritative for transaction scope,
preflight, review route, reviewer ladder, finding triage, rotation, staging,
commit, and push. The CCGS `production/handoff/review-tiers.md` module supplies
only the project-specific classification rules. Do not reproduce or override
the global workflow in project instructions.

## Resume Procedure

On resume:

1. Run Agent Bindery's `$resume-from-handoff` once. It resolves
   `.agent-continuity.toml`, validates index freshness, and loads the configured
   CCGS modules.
2. Treat `production/session-handoff.md` as canonical and
   `production/resume-index.md` plus `production/session-state/active.md` as
   derived aids. Surface disagreement rather than normalizing it silently.
3. Keep the default slice read bounded; only explicit `deep` mode expands the
   slice-history read.
4. Preserve owed verification and the CCGS phase/slice guard before ranking.
5. Stop at lane selection. A focus argument changes ranking but does not select
   work, and selecting a lane authorizes no later mutation.
6. When the manifest-declared scratchpad is written, require the global skill's
   readback before reporting it updated.

The detailed freshness states, source-read order, and cache format belong to the
global skill and may evolve independently of CCGS.

## Optional Asset-Generation Continuity

When a project provides `$gen-asset`, explicit invocation authorizes built-in
generation and scratch writes only under `tmp/gen-asset/**`. Preserve one
contact-sheet gate containing candidate verdicts, exact final paths, overwrite
warnings, and the adapter command. Approval authorizes only those listed final
paths and that adapter command; dependency installation, unrelated writes, and
placement before approval remain outside the invocation.

## Context Thresholds

Use the active reported context percentage, not hardcoded token math.

- Around 50%: prefer bounded reads and summarize decisions into files.
- Around 60-70%: compact or hand off after the current coherent unit.
- Above 70%: avoid starting broad multi-agent or multi-file work unless it is
  the only safe way to close the current unit.

## Threshold Handoff Phases

- Light handoff: one paragraph, files touched, owed verification, next action.
- Standard handoff: add decisions, open questions, and exact commands.
- Deep handoff: only for multi-day or cross-discipline work; include evidence
  pointers and why the next session should not restart planning.
