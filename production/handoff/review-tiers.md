# CCGS handoff review tiers

Slot: `gate.tiers` in `.agent-continuity.toml`.

## Standard

Use `STANDARD` for routine executable or mixed changes: source, tests, tools,
CI, runtime configuration, executable specifications, public API contracts,
and documentation mixed with any of those surfaces.

## Adversarial

Use `ADVERSARIAL` only for:

- Foundation architecture closure or a cross-cutting ADR that locks runtime
  behavior, determinism, replay, persistence, networking, or engine seams.
- Master architecture or control-manifest promotion.
- Batch ADR acceptance or stage-gate advancement.
- Release candidates, gold masters, launch gates, or explicit pre-release
  hardening.
- Explicit user requests to red-team, cross-examine, challenge, or perform an
  adversarial review.

When the scope is not clearly on this list, use `STANDARD`.

## Pure-document exemption

Use `PURE-DOCUMENT` only when every changed path is human- or agent-facing prose
and none is an executable specification, configuration file, test, public API
contract, or runtime-behavior requirement. This includes ordinary process docs,
agent instructions, non-runtime ADR prose, GDD prose, handoff files, and memory
files. Mixed scope is never exempt.

The exemption skips the independent reviewer, not self-review, scope evidence,
finding triage, or the rest of the handoff transaction.

For round-two escalation, treat shared helpers, CI configuration, public APIs,
engine-wide interfaces, and runtime-behavior specifications as cross-cutting
executable surfaces.
