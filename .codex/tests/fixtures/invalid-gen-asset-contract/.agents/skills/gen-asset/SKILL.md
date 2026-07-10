---
name: gen-asset
description: Use when generating project-local raster game assets.
---

# Gen Asset

Copy this skill to `.Codex/skills/gen-asset/` or `.claude/skills/gen-asset/`.

Run this command and use the newest image if session parsing fails:

```bash
codex exec "generate the asset"
```

If that fails, use `OPENAI_API_KEY` with the image API.
