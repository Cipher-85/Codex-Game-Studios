# UI Code Rules

---
paths:
  - "src/ui/**"
---

- UI must never own or directly modify game state. Display state and use
  commands or events to request changes.
- All UI text must go through the localization system.
- Support configured keyboard, mouse, gamepad, and touch targets as applicable.
- Animations must be skippable and respect motion and accessibility
  preferences.
- UI sounds trigger through the audio event system, not directly.
- UI must never block the game thread.
- Scalable text and colorblind modes are mandatory.
- Test all screens at minimum and maximum supported resolutions.

Resolve engine/platform/budget fields through `.codex/docs/technical-config.md`
before using them. Check actual pin/runner agreement; retain custom project
constraints and required evidence. Configuration never proves a runtime result.
