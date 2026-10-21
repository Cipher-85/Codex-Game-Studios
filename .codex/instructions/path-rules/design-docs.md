# Design Document Rules

---
paths:
  - "design/gdd/**"
---

- Before authoring or checking a system GDD, read
  `.codex/docs/workflow-modes.md` and resolve the exact system stem. Author the
  effective required sections and user-selected optional sections; preserve
  existing content. Accept Detailed Design and Detailed Rules as aliases.
- Formulas must include variable definitions, expected value ranges, and example
  calculations.
- Edge cases must explicitly state what happens, not just "handle gracefully."
- Dependencies must be bidirectional; if system A depends on B, B's doc must
  mention A.
- Tuning knobs must specify safe ranges and what gameplay aspect they affect.
- Acceptance criteria must be testable by QA as pass/fail.
- No hand-waving: "the system should feel good" is not a valid specification.
- Balance values must link to their source formula or rationale.
- Design documents must be written incrementally: create the skeleton first,
  then fill each section one at a time with user approval between sections.
  Write each approved section immediately to persist decisions and manage
  context.
