# Verification Integrity

Verification claims must describe evidence, not intent. A result is verified
only when the command or check ran in the current turn, or when the answer labels
the result as historical/file-reported and names the source.

## Hard Rules

- Do not say a build, test, lint, audit, smoke check, or playtest passed unless
  the result was observed.
- Do not convert "not run" into "passed" because the change was small.
- Do not treat CI badges, workflow names, or expected job behavior as logs.
- If a command fails because of environment, missing dependency, sandbox, or
  timeout, report that exact state and the owed command.
- If a check is skipped by design, say why it was skipped.

## Evidence Labels

Use precise labels in status reports:

- `verified this turn`: command/check was run and output inspected.
- `file-reported`: a repo file claims the result; not independently verified.
- `blocked`: could not run; include the blocker.
- `not run`: intentionally not run or out of scope.

## CI Read Handling

When using CI or hosted checks:

1. Open the concrete run, job, or log.
2. Confirm the status and the relevant failing/passing step.
3. Quote or summarize only the key line needed to support the claim.
4. If the run is queued, cancelled, expired, or inaccessible, report that state.

## Incident Examples

- Wrong: "Tests pass" after editing a test file but not running the suite.
- Right: "Tests not run; owed: `[resolved engine test command from coding-standards.md]`."
- Wrong: "CI is green" after seeing only a branch badge.
- Right: "CI file-reported green in `production/qa/...`; not verified this turn."

## Recovery Procedure

If a verification claim may be wrong:

1. Stop expanding scope.
2. Re-run or inspect the exact check if feasible.
3. Correct the status plainly in the next user-visible message.
4. Add the owed verification to the final response and continuity epilogue.
5. If the uncertainty affects implementation safety, recommend the verification
   as the next action before more feature work.

## Required checks and scope

A required check that did not run or could not be evaluated is NOT ASSESSED.
An observed failure takes precedence (FAIL for smoke/gates; BLOCKED for stories).
Only after all required checks pass may advisory findings produce a qualified
pass. Missing tooling, zero tests, an unanswered prompt, stale output, and a
missing required report are never PASS WITH WARNINGS. A user report is labeled
user-reported; a prior log is historical until its identity and applicability
are established. Neither becomes a current-turn execution claim.

A partial check names what it covered and skipped. `$smoke-check quick` cannot
satisfy a gate requiring the full sprint/coverage check. QA planning may continue
with missing smoke evidence; QA execution/sign-off and stage advancement may not.

## Run, observe, retain

For a visible acceptance criterion, launch the relevant build, reach the stated
scene/state, and open the retained screenshot. Record setup, platform, build/ref,
dirty files, observer, command/tool, and criterion-to-capture mapping. No capture
tool or launch access: report NOT ASSESSED with the owed action. Never infer a
visible pass from source code, a headless import, or someone else's description
of an image. A screenshot verifies the pictured state only; interaction, timing,
performance and feel require their own observed checks or explicit user verdict.

Preserve the existing `production/qa/evidence/<story>-evidence.md` format. Put new
captures and their `stamp.json` in `production/qa/evidence/<story>/`. Playtest
reports live in `production/qa/playtests/`; legacy paths may be read as labeled
historical evidence but are not new output destinations.

Before capture, include exact evidence destinations in the approved write scope.
After an observed capture, hash the source, scene, data and asset files that it
actually covers (from the story's Files section plus relevant dependencies):

```bash
bash .codex/lib/review-receipts.sh hash src/player.gd assets/data/player.json
bash .codex/lib/review-receipts.sh check production/qa/evidence/<story>/stamp.json
```

The helper only prints JSON. Save successful `hash` output to the approved stamp
path through the normal file-writing tools. A failed hash cannot produce a valid
stamp. Never stamp old evidence using today's files; recapture first. Keep the
input list and its limits in the evidence document; a partial list cannot prove
the whole build is unchanged.

`check` exits 0 for UNCHANGED, 1 for changed/deleted inputs, and 2 for unknown or
invalid evidence (NO_RECEIPT / NOT_ASSESSED). Treat every nonzero status as a
freshness warning, not a failed gameplay test. Name CHANGED/GONE files and request
recapture. Older evidence without a stamp is "freshness unknown". A matching
hash never proves a test passed or that a capture was opened. Existing results
stay historical; fresh acceptance claims need applicable observed evidence.

## Review provenance

Completion reports always include Reviewed by: the actual independently loaded
role when it ran; `user-reported review — not verified here` for a report supplied
by the user; or `self — no independent review`. A missing role or failed spawn
cannot be replaced with a simulated specialist verdict. Review mode and skipped
gates remain explicit.

## Configuration is not evidence

QA, team and technical readers expose policy and provenance only. Their success
never proves tests ran, a runner exists, coverage was measured, a role loaded or
an engine build passed. Preserve `qa-policy.md`'s mandatory evidence floor and
`technical-config.md`'s separation of estimates from measurements. Required
failures and NOT ASSESSED criteria cannot be waived by reduced QA/strictness or
an informational performance budget. Record policy/source alongside observed
results, with the build/ref and exact scope the evidence actually supports.
