# Team participation policy

Before a team pipeline chooses participants, run
`python3 .codex/lib/project_config.py team-policy` at the bound root (or use the
installed helper's absolute path with `--root`). Keep size/source and apply it
to the workflow's declared roles. Invalid configuration or missing tooling stops
that routing and is reported, never replaced with a smaller team.

| Size | Optional participation |
|---|---|
| compatibility | Existing workflow behavior; no inferred team size |
| individual | Required roles only |
| small | Required roles plus relevant declared optional advisors |
| studio | Required roles plus relevant declared optional specialist/review passes |

## Select roles without losing ownership

First identify the actual scope and the roles the invoked workflow names. Mark
each participation as required, conditional or explicitly optional. A conditional
role becomes required when its condition holds: AI work needs its declared AI
owner, for example. If the skill does not mark a role optional, do not remove it
merely to hit a smaller team size. User-requested named roles remain requested.
Then filter explicitly optional participation according to the table and explain
the resulting roster before dispatch. Unknown scope is a question, not evidence
that the domain is absent.

A programmer does not become a designer, artist or QA sign-off authority because
the team is small. Keep required domain owners and the existing separation of
implementation and independent review. When no implementation-capable role is
active, return an approved change proposal to the implementation workflow;
do not have an analyst silently implement it.

## Review mode and authorization

`director-gates.md` alone governs review-mode filtering. Apply it independently;
team size cannot suppress a required remaining reviewer or add a gate skipped by
review mode. Skill-specific review depth keeps its existing behavior. Studio
size is not permission to spawn undeclared agents or invent an adversarial pass.

Explicit invocation authorizes only the roles declared by that workflow under
the project's delegation contract. Keep its runtime role-identity check and
Jev/worker-routing requirements. Merely inspecting team-policy spawns nothing.
No team value authorizes writes, publication, scope changes or game-feel choices.
Keep runtime concurrency limits and existing independent-task scheduling; this
setting is not a session/worktree ownership mechanism.

Before accepting a role's result, verify the matching custom profile actually
loaded. An unavailable role is blocked/skipped with its missing obligation;
neither the coordinator nor another domain simulates its verdict.
