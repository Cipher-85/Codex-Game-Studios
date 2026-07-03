# Potential Context Optimization Plan

Status: proposed for later review, not approved for implementation.
Captured: 2026-07-03 Asia/Shanghai

## Summary

Optimize Stillcurrent first by adding a small tracked resume index that becomes
the default startup state for `$resume-from-handoff` and `$studio-next`. Keep
`src/README.md` as full slice history, but stop reading it in full during
ordinary resume and next-action routing.

## Key Changes

- Add tracked `production/resume-index.md`, target <=10 KB, maintained by
  `$handoff`.
- Index fields: current slice version, real/stubbed one-liner, last reported or
  verified boot/playtest, owed verification, best next action, top 2-3 lanes,
  blockers/gates, evidence pointers, and source freshness.
- Change `$resume-from-handoff` default to "light resume": read
  `resume-index.md`, `session-handoff.md`, sprint/stage/active state, and only
  a bounded top/current section of `src/README.md` for freshness checks.
- Add explicit deep mode for `$resume-from-handoff deep`, historical questions,
  missing/stale index, or user-requested full catch-up.
- Change `$studio-next` to read `production/resume-index.md` instead of full
  `src/README.md`.
- Update `$handoff` to refresh `production/resume-index.md` after live handoff
  updates, verify its byte size, and commit it with the handoff when commits are
  authorized.
- Update AGENTS/context docs to remove 1M/750k assumptions and use the observed
  practical budget: compact earlier, hard-handoff earlier, and keep default
  orchestration reads bounded.

## Behavior Rules

- `production/session-handoff.md` remains the canonical live narrative.
- `src/README.md` remains canonical full slice history, but is no longer default
  resume context.
- `production/session-archive.md` remains historical-only and is not read by
  default.
- If the index is stale or mismatches the bounded current README header, the
  skill reports that plainly and either uses bounded state or asks for explicit
  deep resume.
- If dirty local work has a newer slice header than the index, resume labels it
  as in-flight local state rather than silently treating the index as complete.

## Test Plan

- Confirm Stillcurrent branch is `codex-game-studios-deployment`.
- Verify `production/resume-index.md` and `production/session-handoff.md` stay
  under size targets with `wc -c`.
- Run Stillcurrent audits: `./.codex/audit.sh all --root "$PWD"` and
  `./.codex/audit.sh skills --root "$PWD"`.
- Search skill/docs text to confirm no default full-read instruction remains for
  `src/README.md`.
- Prompt smoke: `$resume-from-handoff` should report state from the index and
  bounded freshness checks, then offer structured lanes.
- Prompt smoke: "what should I do next?" should route through `$studio-next` and
  avoid full history loading.
- Stale-index scenario: simulate missing/stale index and verify the skill labels
  it and falls back only with explicit deep intent.

## Assumptions

- First rollout is Stillcurrent only.
- The index is tracked under `production/`, not ignored
  `production/session-state/`.
- Splitting `src/README.md` is deferred unless the lightweight resume path is
  still too expensive.
- No `.claude/` or `CLAUDE.md` dependency is introduced.
