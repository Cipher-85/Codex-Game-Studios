# Latest Test Evidence

Date: 2026-07-22

Scope: Codex Game Studios `v0.7.1` patch release for hardened `$handoff`
review coverage, bounded `$resume-from-handoff` continuity, and supporting
lifecycle validation.

## Commands Run

```bash
git diff --check
python3 .codex/lib/validate_manifest.py --root "$PWD"
./.codex/audit.sh all --root "$PWD"
./.codex/release.sh check
./.codex/audit.sh coexistence --root "$PWD" --integration
./.codex/audit.sh smoke-interactive --root "$PWD"
```

## Result

- `git diff --check`: pass
- Standalone manifest validation: pass
- `audit.sh all`: pass
  - manifest: pass
  - runtime: pass
  - skills: pass
  - agents: pass
  - hooks: pass
  - config: pass
  - coexistence: pass
  - smoke-headless: pass
- `release.sh check`: pass with no errors or warnings
- Temporary-target installer integration matrix: pass in 7m24.72s
- `smoke-interactive`: skipped, with an explicit warning that a separately
  recorded trusted session with auth/model access is required

## Notes

- Verification ran in `/Users/yongatron/Development/codex-game-studios`.
- Release validation established `codex-v0.7.0` at `af8c42f` as the previous
  published baseline and accepted the `v0.7.1` package metadata for the two
  post-tag continuity commits.
- Static, headless, manifest, release, and installer-integration evidence is
  current-turn proof. A live trusted-session handoff/reviewer smoke was not run
  in this turn and must not be inferred from the skipped interactive check.
- This release-metadata changeset does not authorize or perform a commit, push,
  tag, or GitHub release publication.
