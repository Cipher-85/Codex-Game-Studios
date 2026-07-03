# Engine Code Rules

---
paths:
  - "src/core/**"
---

- Zero allocations in hot paths such as update loops, rendering, and physics;
  pre-allocate, pool, and reuse.
- All engine APIs must be thread-safe or explicitly documented as
  single-thread-only.
- Profile before and after every optimization, then document measured numbers.
- Engine code must never depend on gameplay code. Dependency direction is
  engine <- gameplay.
- Every public API must have usage examples in its doc comment.
- Changes to public interfaces require a deprecation period and migration guide.
- Use deterministic cleanup for all resources.
- All engine systems must support graceful degradation.
- Before writing engine API code, consult `docs/engine-reference/` for the
  current engine version and verify APIs against the reference docs.
