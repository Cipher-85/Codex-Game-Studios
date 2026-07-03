# Contributing

Codex Game Studios is a Codex-native fork of Claude Code Game Studios. Keep
contributions aligned with the porting contract and the repo's verification
model.

## Ground Rules

- Preserve upstream attribution and the pinned upstream mapping evidence.
- Do not add Claude runtime dependencies to the Codex install surface.
- Do not write package behavior that modifies `.claude/` or requires
  `CLAUDE.md`.
- Keep target project licenses and user-owned instructions intact.
- Make small, reviewable changes with focused validation evidence.

## Local Validation

Run the package audit before proposing a release-facing change:

```bash
./.codex/audit.sh all --root "$PWD"
./.codex/audit.sh smoke-headless --root "$PWD"
```

For installer or manifest changes, also inspect:

```bash
python3 .codex/lib/validate_manifest.py --root "$PWD"
```

## Documentation

Use [README.md](README.md) for release-facing usage, [PORTING_NOTES.md](PORTING_NOTES.md)
for lineage and conversion context, and `docs/codex-conversion/` for detailed
porting evidence.
