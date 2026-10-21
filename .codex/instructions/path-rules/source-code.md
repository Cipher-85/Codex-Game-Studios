# Source Code Rules

---
paths:
  - "src/**"
  - "Assets/**/*.cs"
  - "Packages/**/*.cs"
  - "Source/**"
  - "Plugins/**/Source/**"
---

Use this before editing game source in the resolved engine or custom source
scope. Apply **Source scope** in `.codex/docs/technical-config.md` and run
`project_config.py code-root` first. Also load `gameplay-code.md`,
`engine-code.md`, `ai-code.md`, `network-code.md` or `ui-code.md` according to the
code's responsibility; the `src/` subtrees in the root table are examples, not
a reason to omit those rules for Unity, Unreal or a custom layout.

## Code-Turn Discipline

1. Identify the behavior, owner node or resource, and smallest implementation
   surface before editing.
2. Define verifiable success: name the test, scene run, or manual check that
   proves the change.
3. Prefer idiomatic engine and language patterns already used in the repo.
4. Avoid unrelated refactors.

## Engine Version

The pinned engine may be newer than model training data. Check
`docs/engine-reference/` before using engine APIs.

## Coding Standards

- Public APIs require doc comments.
- Gameplay values must be data-driven, not hardcoded.
- Prefer dependency injection over singletons for testability.
- Resolve architecture prerequisites through `.codex/docs/workflow-modes.md`.
  Existing Accepted ADRs remain binding at every tier; minimal may use a brief
  and standard requires critical Foundation decisions.
- Source changes should reference the relevant story or design document when one
  exists.

Preserve the engine-native test layout: commonly `tests/` for Godot,
`Assets/Tests/` for Unity and tests within the owning Unreal module. Read
`test-standards.md` for every test edit. Run `$test-setup` when setup is needed;
never move existing tests to a generic folder to satisfy an example.

Resolve engine/platform/budget fields through `.codex/docs/technical-config.md`
before using them. Check actual pin/runner agreement; retain custom project
constraints and required evidence. Configuration never proves a runtime result.
