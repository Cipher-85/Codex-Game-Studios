# CCGS reporting integrity

Slot: `modules.integrity` in `.agent-continuity.toml`.

## Claims and observations

Treat test, build, boot, CI, and playtest results recorded in the handoff as
historical claims. State their provenance and do not present them as current.
Only a check run in the current turn is verified evidence. If a required check
cannot run, state the blocker and exact command or action still owed.

## Owed verification

An owed check remains attached to every lane it affects and cannot be bypassed
by selecting a different lane. Do not run builds, tests, boot smoke, playtests,
or mutating external checks during resume unless current project instructions
or the user separately authorize them.

When the owed check is a user-owned playtest, preserve a `Playtest focus:` brief
with the hypothesis, setup or build, two to four observation prompts, and the
verdict or evidence the user should return. Never make the game-feel, balance,
keep, revert, or tune decision for the user.

## Persistence and review findings

Surface approved content that has no backing artifact before lane selection or
handoff completion. Preserve deferred reviewer findings verbatim with their
source; a paraphrase is not an auditable deferral.
