# QA policy

Before planning tests, implementing a story, reviewing evidence or determining a
QA verdict, run `python3 .codex/lib/project_config.py qa-policy` at the bound root.
Outside it, use the installed helper's absolute path and `--root <bound-root>`.
Keep level/source, type rules, coverage settings and notes in the run's context.
Invalid configuration or missing tooling is INVALID/NOT ASSESSED; stop affected
QA routing rather than replacing the result with a permissive default.

## Evidence floor

`coding-standards.md` and `verification-integrity.md` remain authoritative for
story-type evidence and actual observation. Every level preserves that floor:

| Level | Scope above the evidence floor |
|---|---|
| compatibility | Existing skill requirements; no inferred level |
| minimal | Focused required evidence and acceptance criteria; no extra QA ceremony |
| standard | Structured criterion-to-evidence tracing, including existing required checks |
| full | Standard plus regression evidence for affected critical paths; explicit coverage threshold at phase gates |

Never infer that missing tests, unrun checks or screenshots pass. Failed required
tests, observed criterion failures and required unassessed criteria prevent
completion at every level. Build-health smoke remains required before QA handoff.
Existing project requirements may demand more; lower levels do not remove them.
Keep per-system workflow/documentation tiers independent from project QA level.

## Strictness

The reader reports each type's requested strictness and effective gate. A true
strict flag promotes otherwise-advisory evidence/sign-off findings to blockers.
False restores only the baseline advisory policy where one exists; it cannot
waive mandatory evidence, turn a failed test green or bypass smoke admission.
When false is constrained by the floor, state that limitation explicitly.
Null preserves the existing type policy. Local per-type values override the
project's type value or global boolean, without changing any sibling type.

The gate field describes otherwise-advisory findings, not permission to ignore a
failed criterion. Visual/Feel role sign-off can be advisory under the baseline;
the required observed run and opened image remain required even then.

## Coverage and regression

At full, require regression evidence for the critical paths affected by the
change, not unrelated project-wide work. Identify the paths and their tests or
observed checks. Missing applicable evidence is NOT ASSESSED and blocks closure
until verified. A genuinely inapplicable path is N/A with its reason.

`qa.coverage_minimum` is active only with full QA and a non-null threshold.
Otherwise show it as inactive, including a warning when a value was supplied.
There is no implicit 80 percent target. When active, the phase gate needs a
runner-generated coverage report for the relevant build, code scope and metric.
Record report path, build/ref, tool, metric (line/branch/etc.), numerator,
denominator when available, and measured percentage. An ambiguous metric or
scope, stale/missing report or uninstrumented run is NOT ASSESSED, not zero or
PASS. A test-file count or acceptance-criterion count is not code coverage.
Compare only like metrics; report the interpretation of an existing project's
coverage policy instead of inventing a new metric.

Coverage measurement never installs instrumentation or changes a runner without
separate approval. An applicable prior report remains file-reported evidence;
do not claim its tests ran in the current turn. Coverage above threshold does
not excuse an uncovered criterion or a failing test.

## Briefing, reports and next actions

Pass the resolved QA policy, story type, exact requirements source and required
evidence to programmers/reviewers. Reports record policy level/source, effective
strictness and any constrained request, criteria verified/deferred, scope and
build identity. Keep `NOT ASSESSED`, observed FAIL and advisory concerns distinct.
Only claim the scope actually checked. A quick smoke report cannot satisfy a
larger gate; QA level does not rewrite smoke arguments or review depth.

The reader is observational. It does not run tests, authorize edits, close a
story, start a role agent or approve QA. Native skill acceptance remains separate
from parser/static tests.
