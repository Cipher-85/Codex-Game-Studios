# Gameplay Code Rules

---
paths:
  - "src/gameplay/**"
---

- All gameplay values must come from external config or data files, never
  hardcoded values.
- Use delta time for all time-dependent calculations.
- Do not directly reference UI code; use events or signals for cross-system
  communication.
- Every gameplay system must implement a clear interface.
- State machines must have explicit transition tables with documented states.
- Write unit tests for all gameplay logic and separate logic from presentation.
- Document which design doc each feature implements in code comments.
- Avoid static singletons for game state; use dependency injection.
