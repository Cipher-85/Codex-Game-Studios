# Latest Test Evidence

Date: 2026-07-16

Scope: Codex Game Studios `v0.6.1` patch release for hardened `$handoff`
push routing and approval handling.

## Commands Run

```bash
./.codex/release.sh check
./.codex/audit.sh all --root /Users/yongatron/Development/Codex-Game-Studios
git diff --check
python3 .codex/lib/validate_manifest.py --root /Users/yongatron/Development/Codex-Game-Studios
```

## Result

- `release.sh check`: pass with no errors or warnings
- `audit.sh all`: pass
  - manifest: pass
  - runtime: pass
  - skills: pass
  - agents: pass
  - hooks: pass
  - config: pass
  - coexistence: pass
  - smoke-headless: pass
- `git diff --check`: pass
- Standalone manifest validation: pass

## Notes

- Verification ran in `/Users/yongatron/Development/Codex-Game-Studios`.
- Release validation established the previous published baseline from origin's
  `codex-v0.6.0` tag and validated the installable diff for `v0.6.1`.
- The release change is limited to the already-reviewed `$handoff` hardening,
  version metadata, release notes, README release summaries, and this evidence.
