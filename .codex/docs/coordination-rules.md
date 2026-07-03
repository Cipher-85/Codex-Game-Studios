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

**When to spawn in parallel**: If two subagents' inputs are independent (neither
needs the other's output to begin), spawn both subagent delegations simultaneously rather
than waiting. Example: `$review-all-gdds` Phase 1 (consistency) and Phase 2
(design theory) are independent — spawn both at the same time.

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
4. Always produce a partial report if some agents complete and others block
