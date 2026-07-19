---
name: handoff
description: Use when the user wants to stop, pause, checkpoint, switch machines, or preserve current session state for a future Codex session.
---

# Handoff

Create a durable Codex session handoff for this project. This is the write-side
pair for `$resume-from-handoff`.

## Preconditions

- Respect the current branch. Never switch branches during handoff.
- Do not edit Claude-owned runtime files or legacy Claude instruction surfaces.
- Explicit invocation of `$handoff` authorizes this skill's declared handoff
  workflow without a second approval confirmation: update continuity files, stage
  relevant uncommitted changes by path, create the standard handoff commit, and
  push the current branch.
- Declared continuity files:
  `production/session-handoff.md`, `production/session-archive.md`, and
  `production/session-state/active.md`.
- Show the user the intended handoff label and concise update summary, then
  run the declared handoff workflow directly. Do not pause between the summary,
  continuity writes, commit, and push unless the work would leave the declared
  workflow.
- This authorization does not include making new source edits outside the
  continuity files, design decisions, game-feel/balance calls, writes outside
  declared continuity files, branch switching, force-pushes, or `--no-verify` /
  amend workarounds.
- Use evidence from the current turn for every status, count, and verification
  claim.
- If a command fails, use only the permission fallback or DNS retry declared
  below. If that exact fallback also fails, halt the current phase and report
  the exact final failure.

## Git And Remote Capability Gate

Before Phase 0, resolve the repository's actual Git metadata directory:

```bash
git rev-parse --absolute-git-dir
```

Run `test -w '<absolute-git-dir>'` against the exact returned path, shell-quoted,
using the user's active session permissions. If it is not writable because of
the sandbox and scoped escalation is available, repeat that exact check once
with `sandbox_permissions` set to `"require_escalated"`. If the active context
already reports the Git directory as read-only, request that scoped escalation
on the first attempt. This capability check must not run `chmod`, create a probe
file, delete lock files, or change command shape.

Also resolve the current branch, configured upstream, and exact push URL before
Phase 0:

```bash
git rev-parse --abbrev-ref HEAD
git rev-parse --abbrev-ref --symbolic-full-name '@{u}'
git remote get-url --push <upstream-remote>
git remote get-url --push origin
```

Treat a non-zero upstream lookup as the expected no-upstream case. Use the
upstream remote when present; otherwise use `origin`. Halt if the required
remote or push URL is missing. Never display embedded credentials; redact them
if the configured URL contains any.

Test the exact destination before review or continuity writes:

```bash
git ls-remote --heads '<verified-push-url>' 'refs/heads/<current-branch>'
```

An exit code of zero with no matching ref is valid for a new remote branch. Use
the user's active session permissions. If the active context explicitly reports
network access as unavailable, request scoped escalation on the first attempt
with `prefix_rule` set to `["git", "ls-remote"]`; otherwise run normally first.
If that normal attempt fails solely because sandboxed network access is
unavailable, repeat the exact command once with `sandbox_permissions` set to
`"require_escalated"`.
If the network-capable attempt returns the exact pre-contact DNS error
`Could not resolve host`, retry that same command once with the same permission
mode. Do not retry authentication, authorization, transport, or other errors.

If the Git metadata check or remote check still fails, halt before Phase 0 and
report the exact path, destination, command result, and permission fallback
attempted. Do not begin the review gate or rotate continuity files. The shipped
CCGS config selects the complete `game_studios` profile but does not override
the user's approval policy. The skill must not instruct the user to switch
`/permissions` modes.

## Phase 0: Review Gate

Before rotating continuity files or committing, run this mandatory two-round
gate over every file created or materially changed in this session. The gate can
halt the skill: if triage requires user direction, stop before Phase 1 and do
not rotate, commit, or push.

The review stays inside the current Codex session. A native cross-check is a
distinct native Codex review pass performed by this session after setting aside
its authoring conclusions and re-reading the deliverables with a reviewer lens.
Never invoke `codex review`, `codex exec`, `codex-companion`, the Claude
companion plugin, a subprocess reviewer, a subagent reviewer, or another model
service. Do not create an external data-egress approval path for this gate.

### Pure Design/Process-Document Exemption

If the entire session changed only pure design/process-document content,
self-review is sufficient and the native cross-check is skipped. This exemption
covers instruction/rule files, skills, `AGENTS.md`, ADRs with no runtime impact,
`design/gdd/**`, and memory files. Mixed code-and-document changes are not
exempt. Executable specifications, CI configuration, tools, tests, public API
contracts, and ADRs with runtime-behavioral requirements are not pure documents.

### Round 1

1. Self-review every touched file end-to-end, not just the diff. Check the
   applicable ADRs, GDDs, project rules, naming, test standards, design gates,
   verification claims, and recorded caveats.
2. Unless the pure-document exemption applies, select exactly one native tier:
   - `STANDARD` is the default for routine session work: individual ADR
     amendments, tool / lint additions, tests, GDD system authoring, doc edits,
     and CI tweaks.
   - `ADVERSARIAL` is reserved for this exact major-deliverable trigger list:
     Foundation ADR cluster closure, master architecture doc, control-manifest
     v1.0+ promotion, batch ADR Proposed→Accepted events, stage-gate advances,
     release candidates / gold masters, or explicit user `red-team / challenge`
     language.
   - If uncertain whether the work meets a major trigger, use `STANDARD`.
3. Perform the selected cross-check as a fresh reasoning pass by the current
   Codex session. Inspect the complete touched files and their relevant
   contracts. Report each finding as `HIGH`, `MEDIUM`, or `LOW` with an exact
   `path:line` reference, the violated contract or risk, and a concrete
   recommendation. If there are no findings, report `CLEAN`.
4. Triage every finding:
   - Agree and confident that the fix preserves approved intent: apply it only
     within files already created or materially modified during this session,
     then run the narrowest meaningful verification.
   - Agree but out of scope: do not apply it; record it in the handoff Deferred
     section with the native finding quoted verbatim.
   - Disagree, uncertain, disputed, design-changing, architectural,
     game-feel/balance-changing, or scope-changing: halt and surface the finding
     plus analysis to the user. Do not proceed to rotation or commit.

### Round 2

Run Round 2 only when Round 1 caused a fix.

1. Always self-review the complete Round 1 fix set against the original
   finding, surrounding behavior, and verification evidence.
2. Run a second native cross-check only when Round 1 included at least one
   `HIGH` finding or the fix changed cross-cutting executable behavior. This
   includes shared helpers, CI configuration, determinism-critical paths such
   as `src/core/sim/**`, public APIs, or ADR executable specifications. Use the
   same `STANDARD` or `ADVERSARIAL` tier selected in Round 1. Pure
   design/process-document fixes remain exempt from the second native
   cross-check.
3. Triage Round 2 with a stop bias because a new finding means the first fix was
   incomplete:
   - Trivial and confidently intent-preserving only: fix a typo, document-text
     error, off-by-one in a named constant, or one-line obvious syntax error;
     inline-self-review that exact edit, verify it, and record it in the
     handoff. Do not run a third pass for this trivial fix.
   - Any non-trivial fix, ambiguity, disagreement, scope change, design or
     architecture decision, balance/game-feel decision, or finding outside the
     Round 1 fix set: halt and surface it to the user before Phase 1.

### Pass Cap And Audit Trail

- Cap the gate at three native review passes total, counting Round 1, a
  conditional Round 2 cross-check, and any user-directed rerun after a scope
  extension. A fourth native review pass requires explicit user approval. When
  asking, report the active reported context percentage and the estimated
  additional percentage cost; never substitute fixed token-window or time
  estimates. If the active percentage is unavailable, say so explicitly.
- Record the review audit trail in `production/session-handoff.md`: exemption or
  tier, `CLEAN` or findings, fixes applied and verified, findings deferred with
  quotations, user-cleared findings, and any stopped pass.
- The gate passes only when every finding is fixed and verified, explicitly
  deferred as out of scope, or cleared by the user, with nothing blocking on
  user input. Only then proceed to Phase 1 and record the review gate verdict as
  `PASS`.

## Phase 1: Choose The Label

Use the user-provided argument as the handoff label. If none is provided, infer
a short noun phrase from the active work. If still ambiguous, use
`session-checkpoint`.

The standard commit subject is:

```text
WIP: <label> - CONTEXT HANDOFF
```

## Phase 2: Update Session State

Read these before editing when they exist:

- `production/session-handoff.md`
- `production/session-archive.md`
- `production/session-state/active.md`

Create `production/session-handoff.md` if it does not exist. Create
`production/session-archive.md` only when rotating a prior live session or when a
repo-local continuity rule requires it.

### Maintain The Slice Source Pointer

`production/session-handoff.md` is the contract consumed by
`$resume-from-handoff`. It must contain a project-specific pointer named:

```text
Playable/Slice State Source: <relative path or Not declared>
```

Do not hardcode a project path in this skill. Preserve the current value when it
is still supported by the files you read. Update it only when the user gives a
new path, an existing handoff/template already declares a better path, or the
current work created a clearly canonical playable-state document. If no source
is known, write `Playable/Slice State Source: Not declared`.

### Rotate The Prior Session

If `production/session-handoff.md` contains a `## Most Recent Session` entry,
move that prior session block to the top of `production/session-archive.md`
under `## Session Narratives`. Preserve the moved prose verbatim.

### Write The New Live Handoff

Update only the live sections that changed:

- Last updated pointer.
- Current Stage / Next Action.
- `Playable/Slice State Source`.
- Tracked Open Items.
- Director Gates / Architecture Registry / Systems Index when changed.
- Key Decisions Summary, appending durable decisions only.
- `## Most Recent Session`, with trigger, work completed, files touched,
  decisions, blockers, review outcome, deferred items, and next action.

If approved content exists only in conversation, stop and surface it. Do not hide
an approved-but-unpersisted state.

### Size Check

Run:

```bash
wc -c production/session-handoff.md
```

If the live handoff is over 25 KB, investigate rotation or bloated live sections
before continuing.

## Phase 2.5: Refresh Local Scratchpad

Overwrite `production/session-state/active.md` with a short pointer stub to
`production/session-handoff.md`. It is gitignored scratch state in many
projects; keep it coherent but do not stage it unless the repo explicitly tracks
it. This is a derived checkpoint authorized by explicit `$handoff` invocation.
Do not ask a separate "May I write?" for this file.

## Phase 3: Commit Handoff

Run:

```bash
git status --short
git diff
git log -5 --oneline
```

If there are no relevant uncommitted changes, skip the commit and say why.

Otherwise stage only the relevant paths by name. Avoid broad staging unless the
user explicitly asked for it. `$handoff` invocation is commit authorization for
the relevant handoff work. Run staging using the user's active session
permissions. If it fails solely because the sandbox denies Git metadata writes,
repeat the exact `git add` command once with `sandbox_permissions` set to
`"require_escalated"` and `prefix_rule` set to `["git", "add"]`. Do not broaden
the path set or use a different staging command.

Before committing, verify:

```bash
git diff --cached --name-status
```

Commit with the standard handoff subject using the active session permissions.
If it fails solely because the sandbox denies Git metadata writes, repeat that
exact `git commit` command once with `sandbox_permissions` set to
`"require_escalated"` and `prefix_rule` set to `["git", "commit"]`. Include a
Codex co-author trailer only if that is normal for this repo. Halt on any other
failure or if the exact permission fallback fails.

Never use `--no-verify`. Never amend as a workaround for a failed hook.

## Phase 4: Push Handoff

Recheck the branch and configured upstream:

```bash
git rev-parse --abbrev-ref HEAD
git rev-parse --abbrev-ref --symbolic-full-name '@{u}'
```

Treat a non-zero upstream lookup as the expected no-upstream case, not as a
Phase failure. Do not substitute a different branch. Verify that the branch,
upstream state, remote, and push URL still match the destination that passed the
preflight. If any changed, halt instead of pushing to an untested destination:

```bash
git remote get-url --push <upstream-remote>
git remote get-url --push origin
```

Run only the lookup that matches the detected upstream state. Halt if the
required push remote is missing.

Treat the resolved push URL, current branch/upstream, and explicit `$handoff`
invocation as the destination and user-authorization evidence. Show the push URL
and branch in commentary immediately before requesting the push. Do not require
`gh auth status`, `gh api user`, or `gh repo view` as push preconditions. Git and
GitHub CLI may use different credentials. A `gh auth status` failure under
network restriction is not evidence that the Git credential is invalid.

Optional GitHub CLI checks must be read-only, run with the network access they
require, and remain advisory. Never request or display a token. Do not halt
before the authorized push solely because a GitHub CLI check is unavailable,
network-blocked, unauthenticated, or inconclusive.

Push only if the handoff trigger or user instruction authorizes it. Use exactly
one of these command shapes:

- Existing upstream: `git push`.
- No upstream: `git push -u origin <branch>`.

Use the user's active session permissions. If the active context explicitly
reports network access as unavailable, request scoped escalation on the first
push attempt with `sandbox_permissions` set to `"require_escalated"` and
`prefix_rule` set to `["git", "push"]`; otherwise run the matching push command
normally first. If that normal attempt fails solely because sandboxed network
access is unavailable, repeat the exact push command once with the same scoped
escalation. The justification must state that this is the explicitly authorized,
non-force handoff push; name the verified push URL; and identify the current
branch/upstream. Do not claim an authenticated account or repository permission
unless it was actually verified. Explicit `$handoff` invocation is normal push
authorization for the standard handoff commit. Never force-push.

If the network-capable push attempt returns the exact pre-contact DNS error
`Could not resolve host`, retry that exact push command once with the same
permission mode. This retry is safe because name resolution failed before the
remote could be contacted. Do not retry authentication, authorization,
transport, hook, or ambiguous failures, and never change the push command.

The actual `git push` is the authoritative network and Git-authentication check.
If it fails, report Git's exact error and do not reinterpret a preceding GitHub
CLI result as proof of the cause.

If policy or automatic approval review rejects the push, halt Phase 4. Report
the exact rejection and do not retry with another command shape, indirect
execution, or workaround. Do not instruct the user to change the whole session's
permission mode; report the denied scoped action instead.

## Phase 5: Report And Stop

Before reporting, read or refresh the `## Session Worklist` and `## Phase Guard`
in `production/session-state/active.md` when present. If the scratchpad is only
a pointer stub, use the handoff document's recorded next action. Surface any
owed verification and finish with exactly one numbered recommendation:

```text
Next action:
1. (Recommended) [action label] - [brief reason / command]
```

Report in 15 lines or fewer:

- Label.
- Branch.
- Commit, or why commit was skipped.
- Push result, or why push was skipped.
- Handoff doc next action.
- Playable/slice source path, or `Not declared`.
- Open blockers or deferred items.

After reporting, stop. Do not start new feature work in the same turn.

## Ported metadata

This is a Codex-native support skill. It has no upstream Claude skill equivalent.
