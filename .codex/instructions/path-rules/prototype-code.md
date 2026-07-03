# Prototype Code Standards

---
paths:
  - "prototypes/**"
---

Prototypes are throwaway code for validating ideas. Standards are intentionally
relaxed to maximize iteration speed. The goal is learning, not production
quality.

## Allowed In Prototypes

- Hardcoded values
- Minimal or no doc comments
- Simple architecture
- Singletons and global state
- Copy-pasted code
- Debug output
- Placeholder art and audio
- Quick solutions

## Still Required

- Each prototype lives in its own subdirectory: `prototypes/[name]/`.
- Each prototype documents the hypothesis, how to run it, current status, and
  findings.
- Production code may not reference or import from `prototypes/`.
- Prototypes must not modify files outside `prototypes/`.
- Prototypes must not be deployed or shipped.

## When A Prototype Succeeds

If a prototype validates a concept and the feature moves to production:

1. Rewrite the feature to production standards instead of migrating prototype
   code directly.
2. Use prototype findings to inform the production design document.
3. Preserve the prototype directory for reference, but do not extend it as
   production code.
