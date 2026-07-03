# Design Document Rules

---
paths:
  - "design/gdd/**"
---

- Every design document must contain these eight sections: Overview, Player
  Fantasy, Detailed Rules, Formulas, Edge Cases, Dependencies, Tuning Knobs,
  Acceptance Criteria.
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
