# Design Directory Rules

---
paths:
  - "design/**"
---

Use this before authoring or editing design files outside more specific rules.

## GDD Files

Read `.codex/docs/workflow-modes.md` before authoring design artifacts. Use its
resolved section/artifact requirements, including the minimal brief and standard
numeric-formula condition. Existing optional content is preserved and reviewed.
A concept or brief uses its own template, not the system GDD section checklist.

- File naming: `[system-slug].md`, such as `movement-system.md`.
- Update an existing systems index after approval when adding a GDD; create a
  required index through its workflow. Minimal does not require a new index.
- Design order is Foundation, Core, Feature, Presentation, Polish.
- Run `$design-review [path]` after authoring any GDD.
- Run `$review-all-gdds` after completing related GDDs.

## Quick Specs

Use `design/quick-specs/` for tuning changes, minor mechanics, or balance
adjustments. Author through `$quick-design`.

## UX Specs

- Per-screen specs: `design/ux/[screen-name].md`
- HUD design: `design/ux/hud.md`
- Interaction patterns: `design/ux/interaction-patterns.md`
- Accessibility requirements: `design/ux/accessibility-requirements.md`

Use `$ux-design` to author. Validate with `$ux-review` before passing to
`$team-ui`.
