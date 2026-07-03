# Path-Specific Instructions

Path-specific authoring instructions live in
`.codex/instructions/path-rules/*.md`. Root `AGENTS.md` is the router: read the
matching rule before creating or editing the matching path.

`.codex/rules/*.rules` is reserved for Codex command approval policy. Do not put
prose authoring instructions there.

| Path Pattern | Rule File | Enforces |
| ---- | ---- | ---- |
| `src/**` | `source-code.md` | Code-turn discipline, engine API checks, source standards |
| `src/gameplay/**` | `gameplay-code.md` | Data-driven values, delta time, no UI references |
| `src/core/**` | `engine-code.md` | Zero allocations in hot paths, thread safety, API stability |
| `src/ai/**` | `ai-code.md` | Performance budgets, debuggability, data-driven params |
| `src/networking/**` | `network-code.md` | Server-authoritative messages, rollback, security |
| `src/ui/**` | `ui-code.md` | No game state ownership, localization, accessibility |
| `design/**` | `design-directory.md` | Design file structure and validation workflow |
| `design/gdd/**` | `design-docs.md` | Required sections, formulas, edge cases, acceptance criteria |
| `design/narrative/**` | `narrative.md` | Lore consistency, character voice, canon levels |
| `docs/**` | `docs-directory.md` | ADRs, traceability registry, control manifest, engine reference |
| `assets/data/**` | `data-files.md` | JSON validity, naming conventions, schema rules |
| `assets/shaders/**` | `shader-code.md` | Naming, performance targets, cross-platform shader rules |
| `tests/**` | `test-standards.md` | Test naming, deterministic fixtures, coverage expectations |
| `tools/**` | `tool-code.md` | Deterministic tool behavior and CLI compatibility |
| `prototypes/**` | `prototype-code.md` | Throwaway prototype isolation and relaxed standards |
