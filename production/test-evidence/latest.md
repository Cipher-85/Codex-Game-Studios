# Latest Test Evidence

Date: 2026-09-04

Scope: Codex Game Studios `v0.7.2` migration from repo-local continuity skills
to Agent Bindery's global `handoff` / `resume-from-handoff` pair.

## Commands Run

```bash
python3 /Users/yongatron/Development/agent-bindery/skills/handoff/scripts/manifest.py
python3 /Users/yongatron/.codex/skills/.system/skill-creator/scripts/quick_validate.py .agents/skills/help
python3 /Users/yongatron/.codex/skills/.system/skill-creator/scripts/quick_validate.py .agents/skills/studio-next
git diff --check
python3 .codex/lib/validate_manifest.py --root "$PWD"
python3 .codex/lib/validate_install.py --root "$PWD" --integration
./.codex/audit.sh release --root "$PWD"
./.codex/audit.sh all --root "$PWD"
./.codex/audit.sh smoke-headless --root "$PWD"
```

A temporary upgrade fixture installed the package from local release commit
`f0c07c6`, added a user-owned `production/session-handoff.md`, upgraded it with
the working tree, and asserted the old skills were removed while the handoff and
new integration files remained.

## Result

- Agent Bindery manifest parse: pass with `declared: true`, `ok: true`, and no
  problems.
- Modified repo-local skills (`help`, `studio-next`): quick validation pass.
- `git diff --check`: pass.
- Standalone manifest validation: pass.
- Temporary-target installer integration matrix: pass with no errors or
  warnings.
- Continuity-shadow cases: unchanged state-owned copies were removed; unowned
  and locally modified copies caused a fail-closed install and were preserved.
- Focused `f0c07c6` to `v0.7.2` upgrade: pass; both obsolete repo-local skills
  were removed, all five integration files were installed, the user-owned
  handoff was preserved, and the resulting state owned 512 package paths.
- `audit.sh release`: pass with no errors or warnings.
- `audit.sh all`: pass:
  - manifest: pass
  - runtime: pass
  - skills: pass
  - agents: pass
  - hooks: pass
  - config: pass
  - coexistence: pass
  - smoke-headless: pass
- Separate `audit.sh smoke-headless`: pass.

## Notes

- Verification ran in `/Users/yongatron/Development/codex-game-studios`.
- The local `codex-v0.7.1` tag was unavailable, so the focused upgrade used the
  present `v0.7.1` release commit `f0c07c6` without a network fetch.
- No interactive model-running smoke was run; static and headless checks do not
  prove fresh-session global-skill discovery.
- No commit, push, tag, deployment, or GitHub release publication was performed.
