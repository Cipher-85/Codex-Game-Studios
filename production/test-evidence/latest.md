# Latest Test Evidence

Date: 2026-07-05

Scope: Codex Game Studios v0.3.3 continuity-routing patch release.

## Commands Run

```bash
python3 .codex/lib/validate_manifest.py --root "$PWD"
./.codex/audit.sh all --root "$PWD"
./.codex/audit.sh release --root "$PWD"
./.codex/release.sh check
```

## Result

- `validate_manifest.py`: pass
- `.codex/audit.sh all`: pass
- `.codex/audit.sh release`: pass
- `.codex/release.sh check`: pass

## Notes

- Verification ran in `/Users/yongatron/Development/Codex-Game-Studios`.
- Release metadata, runtime files, hooks, config, coexistence checks, and
  headless smoke validation passed for the v0.3.3 patch.
- Static checks confirmed continuity routing now reads the `## Session Worklist`
  and `## Phase Guard` in `production/session-state/active.md`, with
  `$studio-next` retained only as a deprecated manual compatibility reference.
