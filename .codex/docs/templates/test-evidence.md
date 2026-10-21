# Test Evidence: [Story Title]

> **Story**: `[path to story file]`
> **Story Type**: [Visual/Feel | UI]
> **Date**: [date]
> **Tester**: [who performed the test]
> **Build / Commit**: [version or git hash]

---

## What Was Tested

[One paragraph describing the feature or behaviour that was validated. Include
the acceptance criteria numbers from the story that this evidence covers.]

**Acceptance criteria covered**: [AC-1, AC-2, AC-3]

---

## Acceptance Criteria Results

| # | Criterion (from story) | Result | Notes |
|---|----------------------|--------|-------|
| AC-1 | [exact criterion text] | PASS / FAIL / NOT ASSESSED | [any observations] |
| AC-2 | [exact criterion text] | PASS / FAIL / NOT ASSESSED | |
| AC-3 | [exact criterion text] | PASS / FAIL / NOT ASSESSED | |

---

## Screenshots / Video

List all captured evidence below. Store files in the same directory as this
document or in `production/qa/evidence/[story-slug]/`.

| # | Filename | What It Shows | Acceptance Criterion |
|---|----------|--------------|----------------------|
| 1 | `[filename.png]` | [brief description of what is visible] | AC-1 |
| 2 | `[filename.png]` | | AC-2 |

*If video: note the timestamp and what it demonstrates.*

---

## Capture Provenance and Freshness

- **Run observed by / when**: [person or tool and timestamp]
- **Build/ref and dirty files**: [identity and uncommitted changes]
- **Launch command/tool and scene/state**: [exact reproduction setup]
- **Images opened by reviewer**: [paths; not just file existence]
- **Receipt**: `production/qa/evidence/[story-slug]/stamp.json` or "no receipt"
- **Files covered / known omissions**: [source, scenes, data and assets]
- **Freshness**: [UNCHANGED / CHANGED / GONE / unknown, with affected paths]

Follow `.codex/docs/verification-integrity.md` to capture and compare receipts.
Hash only after a new observed capture; never restamp an old image. Matching
content does not establish a passing test. Record interaction/feel/performance
observations separately from the pictured state.

## Test Conditions

- **Game state at start**: [e.g., "fresh save, player at level 1, no items"]
- **Platform / hardware**: [e.g., "Windows 11, GTX 1080, 1080p"]
- **Framerate during test**: [measured FPS with method, or NOT ASSESSED; estimates do not prove compliance]
- **Any special setup required**: [e.g., "dev menu used to trigger specific state"]

---

## Observations

[Anything noteworthy that didn't cause a FAIL but should be recorded. Examples:
minor visual jitter, frame dip under load, behaviour that technically passes
but felt slightly off. These become candidates for polish work.]

- [Observation 1]
- [Observation 2]

If nothing notable: *No significant observations.*

---

## Sign-Off

All roles must sign off before the story can be marked COMPLETE via `$story-done`.
Visual/Feel stories require the designer or art-lead sign-off. UI stories require
the UX lead or designer sign-off.

**Solo developers**: all sign-offs may be by the same person in each role. The
intent is that someone deliberately reviews the evidence before marking complete —
not that three separate people must participate.

| Role | Name | Date | Signature |
|------|------|------|-----------|
| Developer (implemented) | | | [ ] Approved |
| Designer / Art Lead / UX Lead | | | [ ] Approved |
| QA Lead | | | [ ] Approved |

**Any sign-off can be marked "Deferred — [reason]"** if the person is
unavailable. Deferred sign-offs must be resolved before the story advances
past the sprint review.

---

*Template: `.codex/docs/templates/test-evidence.md`*
*Used for: Visual/Feel and UI story type evidence records*
*Location: `production/qa/evidence/[story-slug]-evidence.md`*

## Effective policy and scope

- QA level/source: [resolved value or compatibility]
- Effective strictness / constrained requests: [per relevant story type]
- Engine pin and verified runner: [identity, verification or NOT ASSESSED]
- Coverage: [inactive, or metric/report/build/scope/measured value/threshold]
- Performance: [budget/source; measured tool/report or estimate only]
- Unassessed required checks: [explicit list; never assumed passing]
