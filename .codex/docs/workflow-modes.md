# Workflow and artifact policy

Read this contract when authoring, reviewing, planning against, or checking the
presence of project artifacts. It controls required documentation, not permission
to act. Review routing remains in `director-gates.md`; evidence requirements
remain in `coding-standards.md`. Neither rigor nor a reduced workflow waives them.

## Resolve before applying a checklist

Run `python3 .codex/lib/project_config.py workflow` from the bound root, or pass
the installed helper's absolute path and `--root <bound-root>`. Store its tier,
source, project_tier, design_source, density and story granularity. INVALID or missing tooling stops the
affected workflow: report the diagnostic, never substitute a tier.

For a known system, add `--system <GDD-filename-stem>`. For example,
`design/gdd/forge-heat-system.md` means `forge-heat-system`, never the `forge`
alias from a TR-ID. Resolve per item in multi-system reviews and story batches.
A story/epic's explicit GDD path determines its system. With only a brief, use
the project tier; with an ambiguous system, report the ambiguity before applying
an override. A requested new GDD stem is valid before its file exists.

The resolver applies explicit workflow, then explicit rigor expansion. A system
override replaces GDD section requirements for that system only, in either
direction. Project artifact prerequisites and the brief/concept source come
from `project_tier` and `design_source`, never from a single-system override.
Thus minimal project + full combat uses the brief plus a full combat GDD; full
project + minimal inventory keeps full project architecture without requiring
an inventory GDD.
Unset returns `compatibility`: preserve the skill's established requirements;
this is not a new setting or an inferred full/minimal/standard value.

At gates, also run `workflow --check-systems`. It compares overrides with actual
GDD stems and explicit `design/gdd/<stem>.md` paths in the systems index, including
planned files. Report unmatched keys as CONCERNS with available stems; they are
not silently applied or corrected. Authoring does not perform this orphan check.

## Design requirements

| Tier | Required design input | System GDD sections |
|---|---|---|
| compatibility | Existing skill requirements | Existing eight-section standard |
| minimal | Filled `design/game-brief.md` and configured engine | No mandatory GDD |
| standard | Game concept and systems index | Resolver's five `required_sections`, plus Formulas when numeric rules exist |
| full | Game concept and systems index | All eight `required_sections` |

`Detailed Rules` and `Detailed Design` are equivalent headings. A heading alone,
placeholder or empty bullet does not satisfy a required section. Standard's
numeric-rule test includes rates, curves, thresholds, costs, damage and weights,
regardless of the system's category. Ask when that cannot be determined. Optional
sections with actual content are still reviewed for correctness; retain them.

The brief requires a pitch, core loop, player goal and fail/end state, MVP,
out-of-scope list and build order. Its player goal and numbered MVP features are
the requirements source. Optional audience/art/reference notes are useful but
do not become hidden requirements. A concept uses its own template, not the
system GDD's eight-section checklist. A brief uses the brief fields above.

All skills remain available at every tier. Optional artifacts are not automatic
gaps. When a voluntarily requested artifact has no applicable inputs, explain
what can be assessed and offer the smallest useful next step; do not fabricate
requirements, empty ADRs, registries, manifests, or a passing review.

## Architecture, art and UX

| Artifact | minimal | standard | full / compatibility |
|---|---|---|---|
| Architecture document | Optional | Required | Existing full requirements |
| ADRs | Optional | Critical Foundation decisions required; no arbitrary minimum count | Existing full requirements |
| TR registry / traceability report / control manifest | Optional | Advisory unless an existing reference makes it necessary | Existing skill requirements |
| Art bible | Optional | Required if visual-asset stories or approved visual-asset scope exist; use the gate's existing section depth | Existing full requirements |
| Separate UX/accessibility documents | Optional | Recommended; no fixed screen count | Existing full requirements |
| Separate epics / sprint plan | Optional | Existing planning flow | Existing planning flow |

Critical ADRs govern Foundation systems whose decisions constrain other systems,
such as state, saves and cross-system communication. An ambiguous layer needs
clarification, not an automatic waiver. At every tier an explicitly referenced
ADR must exist and be Accepted; constraints from existing accepted architecture
remain binding. Missing references, conflicts, stale declared manifest versions
and unresolved user-owned decisions remain findings even for optional artifacts.
Minimal/standard may use an explicit `N/A — <reason>` for an absent optional
artifact; never insert a fake TR-ID or an unsupported approval.

When checking whether standard needs an art bible, inspect the approved scope
and available stories. Unknown asset scope is an open question, not evidence that
no art is needed. Applying a per-system minimal override removes that system's
GDD requirement; its work still needs traceable, testable criteria from the brief
or another approved requirement source.

## Authoring and planning

At minimal, `$brainstorm` drafts the brief from `templates/game-brief.md` instead
of requiring a concept document. Other authoring skills accept the brief as
context. `$design-system` may author a voluntary GDD; show optional sections and
agree scope rather than forcing eight sections. Existing documents stay intact.

`$create-stories` accepts `design/game-brief.md` at minimal (or discovers it when
no epic exists). Read its MVP and build order. Propose one coherent story per MVP
feature in that order, with independently testable criteria from the player goal
and feature. Resolve ambiguity with the user. Use a user-approved slug and the
existing `production/epics/<slug>/story-NNN-<name>.md` layout. A small EPIC.md/index
may be proposed with the stories for tracking, but is not a prerequisite. Name
every proposed file in the write approval. Preserve existing stories and indexes;
append only uncovered work after checking existing IDs and dependencies.

Minimal stories cite `design/game-brief.md`, `Brief MVP feature N`, and explicit
N/A reasons for absent ADR/TR/manifest fields. Keep story type, files, criteria,
dependencies and evidence requirements. `$dev-story`, `$story-readiness` and
`$story-done` use that source instead of looking for a nonexistent TR registry.
An explicit existing TR/ADR reference still receives its normal validation.
Missing optional fields are N/A, not a fictitious successful check.

The minimal build order replaces a separate sprint plan. When selecting work
without a sprint, inspect existing story statuses/dependencies and the brief;
offer the first ready item, never re-open completed work. Sprint commands remain
available when explicitly requested. QA plans/regression audits can use the
same story criteria and brief instead of demanding system GDDs.

`docs.density` changes prose depth only: terse bullets; balanced short context
and actionable notes; thorough rationale, alternatives and examples. An unset
density preserves existing style. Keep required fields, formulas, criteria,
evidence, constraints and user decisions at every density.

`modes.story_granularity` groups work as coarse features, balanced focused tasks,
or fine acceptance-criterion units. An unset value preserves existing sizing.
Dependencies, coherent implementation and the skill's one-session scope limit
take precedence over target grouping; split an oversized feature. Never invent,
drop or weaken criteria to reach a count. Minimal still starts from MVP features;
explicit finer sizing can split them while retaining their source reference.

## Gates and routing

Apply this table to the existing gate; it changes documentation prerequisites,
not evidence, engine safety, publication authority or role routing:

| Target | minimal | standard | full / compatibility |
|---|---|---|---|
| Systems Design | Filled brief; concept/pillars/visual-anchor fields are optional | Existing concept checks | Existing checks |
| Technical Setup | Separate systems-design transition is not applicable | Required GDD sections by system; existing dependency/consistency checks | Existing checks |
| Pre-Production | Configured engine and filled brief | Architecture + critical ADRs; conditional art; traceability, separate UX/accessibility and test scaffolding recommended | Existing checks |
| Production | Brief, engine, ready work with traceable criteria; build order is the plan | Architecture, critical Accepted ADRs, tier-complete GDDs and planned work; separate manifest/traceability and fixed UX screen counts advisory | Existing checks |
| Polish / Release | Existing applicable implementation, test, smoke, playtest, bug and release evidence | Same evidence floor | Existing checks |

At minimal, replace GDD-based implementation/content comparisons with the brief's
approved MVP and story criteria. At standard, remove the fixed three-ADR minimum,
requiring actual critical decisions instead. Performance/engine constraints and QA/team settings use their shared Phase 4C
contracts; story-type evidence and smoke admission retain their mandatory floor. A built vertical slice retains its existing validation
rules at every tier; absent optional slices retain the existing CONCERNS policy.

Count applicable required checks. A transition marked not applicable is
`NOT APPLICABLE`, naming the tier; do not claim PASS, run its director panel, or
advance the stage from it. Any other empty/unassessable checklist is
`NOT ASSESSED`. Artifact presence is not quality approval or executed evidence.
Only an actual PASS may offer the existing approved stage update. The catalog is
routing guidance, never permission to bypass required evidence or relabel FAIL.

## Stage and continuity

Before reading or proposing a stage update, use
`python3 .codex/lib/project_config.py stage`. See `config-resolution.md` for the
single-target write/readback contract. Inference is allowed only for unset stage
and must be labelled inferred; conflicting handoff/artifact signals stay visible.
`Live` is terminal, with maintenance routing and no invented next phase.

Help, gap reports, adoption and continuity use the applicable requirements above
to rank actual playable work. Optional documentation does not displace a ready
playable advance. Changing a tier never deletes/regenerates documents, rewrites
stories or advances stage. Suggest `$content-audit` to inspect the changed scope.
Agent Bindery retains executable handoff/resume ownership.

Adapted selectively from upstream v1.2.0 at
`05ad7c8a5b8aa2aa86bbd3439ae7cf7295cac418`. Upstream default-minimal behavior,
automatic permissions, QA waivers and additional override flags are not adopted.
