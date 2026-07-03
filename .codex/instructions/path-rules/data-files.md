# Data File Rules

---
paths:
  - "assets/data/**"
---

- All JSON files must be valid JSON; broken JSON blocks the entire build
  pipeline.
- File naming: lowercase with underscores only, following the
  `[system]_[name].json` pattern.
- Every data file must have a documented schema, either JSON Schema or a schema
  documented in the corresponding design doc.
- Numeric values must include comments or companion docs explaining what the
  numbers mean.
- Use consistent key naming: camelCase for keys within JSON files.
- No orphaned data entries; every entry must be referenced by code or another
  data file.
- Version data files when making breaking schema changes.
- Include sensible defaults for all optional fields.
