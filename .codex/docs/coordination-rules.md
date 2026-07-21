# Agent Coordination Rules

1. **Vertical Delegation**: Leadership agents delegate to department leads, who
   delegate to specialists. Never skip a tier for complex decisions.
2. **Horizontal Consultation**: Agents at the same tier may consult each other
   but must not make binding decisions outside their domain.
3. **Conflict Resolution**: When two agents disagree, escalate to the shared
   parent. If no shared parent, escalate to `creative-director` for design
   conflicts or `technical-director` for technical conflicts.
4. **Change Propagation**: When a design change affects multiple domains, the
   `producer` agent coordinates the propagation.
5. **No Unilateral Cross-Domain Changes**: An agent must never modify files
   outside its designated directories without explicit delegation.

## Codex Reasoning Assignment

Skills and agents use Codex sessions or subagents with reasoning depth based on
task complexity:

| Depth | When to use |
|-------|-------------|
| **Low** | Read-only status checks, formatting, simple lookups; no creative judgment needed |
| **Medium** | Implementation, design authoring, and analysis of individual systems; default for most work |
| **High** | Multi-document synthesis, high-stakes phase gate verdicts, cross-system holistic review |

Low-depth skills: `$help`, `$sprint-status`, `$story-readiness`, `$scope-check`,
`$project-stage-detect`, `$changelog`, `$patch-notes`, `$onboard`

High-depth skills: `$review-all-gdds`, `$architecture-review`, `$gate-check`

All other skills default to medium-depth Codex work. When creating new skills,
use low depth if the skill only reads and formats, high depth if it must
synthesize 5+ documents with high-stakes output, and medium depth otherwise.

## Subagents vs Parallel Sessions

This project uses two distinct multi-agent patterns:

### Subagents (current, always active)
Spawned via Codex subagent delegation within a single Codex session. Used by all `team-*` skills
and orchestration skills. Subagents share the session's permission context, run
sequentially or in parallel within the session, and return results to the parent.

Explicit invocation of a CCGS skill authorizes only the subagent spawns declared
by that skill's workflow for that run after review-mode filtering. The skill
invocation is already the user's request for those declared spawns; do not ask a
duplicate confirmation before spawning them. This authorization is limited to
delegation; normal approval rules still govern file writes, commits, pushes,
branch changes, design decisions, game-feel or balance decisions, and any agent
not named by the workflow.

**When to spawn in parallel**: If two subagents' inputs are independent (neither
needs the other's output to begin), spawn both subagent delegations simultaneously rather
than waiting. Example: `$review-all-gdds` Phase 1 (consistency) and Phase 2
(design theory) are independent — spawn both at the same time.

**Review-mode check**: Before spawning any director or lead gate, resolve the
active review mode using `.codex/docs/director-gates.md`. `solo` skips all
director gates, `lean` runs only PHASE-GATE director gates, and `full` runs
declared gates normally.

**Runtime fallback**: If the subagent delegation tool is unavailable or a hard
runtime gate prevents a declared spawn, do not invent, summarize, or simulate
specialist/director verdicts. Report the missing delegation as skipped or
blocked, then continue only where the workflow allows a partial result.

### Handoff Integrity Reviewer

For mixed or executable `$handoff` scope, the declared reviewer is one built-in
`explorer` spawned with `fork_turns: "none"`. It is a generic integrity
reviewer, not a custom role agent, director gate, or lead gate, and review mode
does not filter it. The parent supplies the exact review paths, Git baseline,
tier, approved behavioral contract, governing evidence, and verification
results, but no authoring conclusions.

The reviewer is instruction-read-only. The parent compares before-and-after
Git/index/worktree snapshots and scoped content hashes, owns all fixes, and
records the outcome. If the reviewer cannot run fresh, cannot be proven to use
`fork_turns: "none"`, fails, or changes repository state, the handoff stops
before continuity rotation. Do not simulate a reviewer or silently substitute
a same-session pass. A same-session downgrade requires an explicit user waiver.
Pure design/process-document sessions remain exempt unless the user requests a
reviewer.

### Parallel Codex Sessions (manual escalation)
Multiple independent Codex sessions can be coordinated manually through tracked
handoffs or sprint/story artifacts. Each session has its own context window and
budget.

**Use parallel sessions when**:
- Work spans multiple subsystems that will not touch the same files
- Each workstream would take >30 minutes and benefits from true parallelism
- A senior agent (technical-director, producer) needs to coordinate 3+ specialist
  sessions working on different epics simultaneously

**Do not use parallel sessions when**:
- One session's output is required as input for another (use sequential subagents)
- The task fits in a single session's context (use subagents instead)
- Cost is a concern — each team member burns tokens independently

**Current status**: Manual only. Document first usage here when adopted.

## Parallel Task Protocol

When an orchestration skill spawns multiple independent agents:

1. Issue all independent subagent delegations before waiting for any result
2. Collect all results before proceeding to dependent phases
3. If any agent is BLOCKED, surface it immediately — do not silently skip
4. Never replace a blocked or skipped agent with an internal simulated verdict
5. Always produce a partial report if some agents complete and others block
