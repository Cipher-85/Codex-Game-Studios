# AI Code Rules

---
paths:
  - "src/ai/**"
---

- AI update budget: 2ms per frame maximum; profile to verify.
- All AI parameters must be tunable from data files, including behavior tree
  weights, perception ranges, and timers.
- AI must be debuggable: implement visualization hooks for AI state such as
  paths, perception cones, and decision trees.
- AI should telegraph intentions so players have time to read and react.
- Prefer utility-based or behavior tree approaches over hard-coded if/else
  chains.
- Group AI must support formation, flanking, and role assignment from data.
- All AI state machines must log transitions for debugging.
- Never trust AI input from the network without validation.
