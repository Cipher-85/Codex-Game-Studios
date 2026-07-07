# Upstream Parity Audit - 2026-07-07

## Scope

Audit target: the live `/Users/yongatron/Development/Codex-Game-Studios`
workspace on `main`, including uncommitted local edits.

Baseline upstream: `upstream/main` at
`984023ddac0d5e27624f2baacde6105e45de375f`, extracted to:

`/private/tmp/ccgs-parity-audit-20260707/upstream-984023d.5UnXhO`

Current committed base: `cd39a3fb8484afdb9bb592f36106c8d326d10d13`.

Dirty overlay included in this audit:

- `.agents/skills/skill-test/SKILL.md`
- `.codex/docs/coordination-rules.md`
- `.codex/docs/director-gates.md`
- `.codex/lib/validate_runtime.py`
- `AGENTS.md`
- `CCGS Skill Testing Framework/skills/authoring/design-system.md`
- `CHANGELOG.md`
- `production/test-evidence/latest.md`

Non-goals for this pass:

- No runtime/source fixes.
- No metadata/version bump.
- No install/deploy/release work.
- No commit or push.

## Summary Verdict

The Codex tree is broadly mapped and validates cleanly against the manifest and
runtime checks. The role-agent delegation-consent edits in the live dirty
overlay are consistent with the current Codex contract: skill invocation
authorizes declared role-agent spawns after review-mode filtering, while file
writes, commits, pushes, design decisions, game-feel, and balance decisions
still require the normal approvals.

The highest-risk parity gap is not missing files. It is a workflow-boundary
regression: automatic read-only phases can be turned into user-selected "Next
action" prompts by the newer global closeout contract. Upstream and current
`design-system` both say self-checks, registry candidate scans, readbacks, and
status reads run automatically. They ask only before mutating registry/index
files. If the UI screenshots showed the agent asking the user to approve
"Self-Check" or "registry scan" as a next action, that is Codex closeout
friction, not upstream behavior.

## Comparison Matrix

| Surface | Upstream baseline | Current Codex target | Classification | Notes |
| --- | ---: | ---: | --- | --- |
| Role agents | 49 `.claude/agents/*.md` | 49 `.codex/agents/*.toml` | expected Codex adaptation | Exact hyphenated role names preserved. |
| Agent memory | 1 explicit upstream memory plus 16 memory metadata declarations | 17 `.codex/agent-memory/*/MEMORY.md` | intentional Codex extension | Repo-local memory contracts avoid writing global Codex memory. |
| Skills | 73 upstream skills | 73 ported skills plus 4 Codex-only support skills | expected adaptation + extension | New skills: `studio-status`, `studio-next`, `handoff`, `resume-from-handoff`. |
| Hooks | 12 upstream hooks | 11 ported hooks plus `studio-status-on-start.sh` | expected adaptation | `notify.sh` is not installed because Codex has no project `Notification` event. |
| Path rules | 11 upstream `.claude/rules/*.md` plus nested `CLAUDE.md` guidance | 15 `.codex/instructions/path-rules/*.md` plus `settings.rules` | expected adaptation | Path authoring rules are separated from command approval rules. |
| Docs/templates | 23 upstream non-template `.claude/docs`, 40 templates, shared root docs | `.codex/docs/**`, `.codex/docs/templates/**`, shared docs | expected adaptation | Runtime docs validate; shared provenance docs retain intentional Claude references. |
| Testing framework | 49 agent specs, 72 skill specs, 2 templates | 49 agent specs, 73 skill specs, 2 templates | intentional Codex extension | Current adds one skill spec beyond upstream and updates design-system gate expectations. |
| Continuity | Upstream Claude session files and statusline behavior | `active.md`, `$handoff`, `$resume-from-handoff`, `$studio-status`, status-line fallback | intentional Codex extension | Useful, but closeout routing needs sharper phase-boundary rules. |
| Install/release | Upstream package history | `.codex/install.sh`, `.codex/uninstall.sh`, `.codex/release.sh`, manifests | intentional Codex extension | Release flow is explicitly maintainer-run with namespaced tags. |
| Public docs | Shared upstream docs | Shared docs plus Codex docs | mostly expected, one stale term | `docs/COLLABORATIVE-DESIGN-PRINCIPLE.md` still says "Task subagent" once. |

Manifest counts observed:

- `upstream-assets.json`: 417 entries.
- `expected-targets.json`: 412 entries.
- Missing expected target files: 0.
- Upstream mappings without one physical path: 2 status/config mappings that
  intentionally split across `.codex/config.toml`, `.codex/rules/settings.rules`,
  and `$studio-status`.

## Findings

### P1 - Automatic Read-Only Phases Can Be Misrouted As User-Approved Next Actions

Classification: suspect behavior regression.

Upstream evidence:

- Upstream `design-system` Phase 5a says to read back the complete GDD and verify
  required sections, formulas, edge cases, dependencies, and acceptance criteria
  automatically.
- Upstream Phase 5b says to scan the completed GDD for registry candidates, grep
  the registry for existing candidates, and present a summary before asking for a
  registry write.
- The upstream permission prompt appears at:
  `Ask: "May I update design/registry/entities.yaml..."`.

Current Codex evidence:

- Current `design-system` preserves the same automatic self-check at
  `.agents/skills/design-system/SKILL.md:680`.
- Current registry candidate discovery and grep are still automatic at
  `.agents/skills/design-system/SKILL.md:706-728`.
- Current permission remains correctly placed at
  `.agents/skills/design-system/SKILL.md:730-731`.
- The global closeout contract requires every discrete work-unit final response
  to end with a numbered next action at `AGENTS.md:34-40` and again in the
  continuity epilogue at `AGENTS.md:237-243`.
- `design-system` itself now contains a local contradiction: Phase 5f says a
  single clear lane can be stated directly without an unnecessary prompt
  (`.agents/skills/design-system/SKILL.md:791-794`), but its Closeout Contract
  says every final response must use the numeric `Next action:` prompt even for
  one valid lane (`.agents/skills/design-system/SKILL.md:890-905`).

Interpretation:

The screenshot behavior where an agent asks the user to choose a read-only
"Self-Check" or registry-candidate scan is not faithful to upstream. Read-only
continuation phases inside an invoked workflow should run. Permission is needed
when the workflow reaches a mutation: registry write, systems-index write,
review-log append, durable artifact edit, commit, push, or branch operation.

Remediation target:

- Add an explicit "phase continuation vs work-unit closeout" rule to `AGENTS.md`
  and `.codex/docs/session-continuity.md`.
- In skills, say that automatic read-only phases are not valid final
  `Next action` options while the invoked workflow is still in progress.
- Add a validation fixture that rejects closeout menus offering internal
  read-only phases such as `Self-Check`, registry scan, candidate discovery,
  readback, or context gathering as user-approved next actions.

### P1 - Design-Review Post-Revision Flow Is Upstream-Faithful, But Vulnerable To Generic Closeout Injection

Classification: suspect behavior regression in orchestration, not in the direct
`design-review` port.

Upstream evidence:

- Upstream `design-review` uses a post-revision closing widget after blockers are
  resolved, with options to re-review in a new session, accept revisions and mark
  approved, move to the next system, or stop.
- Upstream then asks separately for tracking mutations: systems-index update and
  review-log append.
- The final widget is shown only after those tracking widgets are answered.

Current Codex evidence:

- Current `design-review` preserves that structure with Codex wording:
  `.agents/skills/design-review/SKILL.md:185-264`.
- The post-revision widget is at
  `.agents/skills/design-review/SKILL.md:202-212`.
- Systems-index and review-log permission prompts are at
  `.agents/skills/design-review/SKILL.md:226-232`.
- Final project-state read and dynamic next options are at
  `.agents/skills/design-review/SKILL.md:246-264`.
- No `Self-Check` text exists in current `design-review`.

Interpretation:

If a self-check lane appears after a design-review revision, it is not coming
from upstream `design-review` or the direct Codex port. The likely sources are
generic closeout routing, stale `production/session-state/active.md` worklist
content, or an agent applying another skill's validation phase after the
design-review widget. The fix should not remove the post-revision widget; it
should keep it authoritative until the review-log/systems-index prompts are
complete.

Remediation target:

- Mark `design-review` Phase 5 widgets as workflow-owned until tracking prompts
  finish.
- Ensure `Session Worklist` recommendations contain follow-on lanes or owed
  verification, not internal phases from the current skill.
- Add a targeted skill-test fixture for post-revision review closeout.

### P2 - Runtime Validators Prove Static Conversion, Not The Read/Write Boundary

Classification: testing gap.

Current evidence:

- `python3 .codex/lib/validate_manifest.py`: pass.
- `python3 .codex/lib/validate_runtime.py --kind docs`: pass.
- `python3 .codex/lib/validate_runtime.py --kind skills`: pass.
- `./.codex/audit.sh all`: pass.
- `validate_runtime.py` rejects raw `.claude/`, `CLAUDE.md`,
  `AskUserQuestion`, raw `Task`, and duplicate delegation-consent fallback
  patterns.

Interpretation:

The validation suite correctly catches many static porting errors, but it does
not yet model the behavioral contract that read-only phases run automatically
while mutating phases ask. That is why the screenshot friction can exist while
the audit suite stays green.

Remediation target:

- Extend `$skill-test` and `validate_runtime.py` with behavioral assertions for
  read-only phase continuity.
- Add focused fixtures for `design-system` Phase 5 and `design-review` Phase 5.

### P2 - Design-Review Does Not Inline The Codex Path-Rule Reminder Before Its Mutations

Classification: missing/stale Codex adaptation.

Current evidence:

- `AGENTS.md` requires reading path rules before creating or editing matching
  paths.
- `design-review` may mutate `design/gdd/systems-index.md` and
  `design/gdd/reviews/[doc-name]-review-log.md`.
- Unlike `design-system`, `design-review` does not start with a reminder to read
  `.codex/instructions/path-rules/design-directory.md` and
  `.codex/instructions/path-rules/design-docs.md`.

Interpretation:

This is partly covered by root instructions, but high-traffic mutation skills
should make their path-rule dependency explicit. It is not an upstream behavior
gap because upstream had no Codex path-rule surface.

Remediation target:

- Add a short preamble to `design-review` before Phase 1 or before Phase 5
  mutations instructing agents to read the relevant design path rules before
  writes.
- Consider adding the same validator check for every skill that writes into
  a path-scoped directory.

### P3 - Design-Review Retains An Inherited Option-Name Mismatch

Classification: inherited upstream behavior.

Evidence:

- Current `design-review` parses `--depth [full|lean|solo]` at
  `.agents/skills/design-review/SKILL.md:8-14`.
- The full-review notice still says "Use `--review lean`" at
  `.agents/skills/design-review/SKILL.md:205`.
- Upstream has the same mismatch: it parses `--depth` but says
  `/design-review ... --review lean`.

Interpretation:

This is not a Codex regression, but it can confuse users because `--review`
means global director-gate review mode in other skills, while `design-review`
uses `--depth` for its own analysis mode.

Remediation target:

- Change the notice to `--depth lean`.
- Add a testing-framework assertion that `design-review` user-facing examples
  use `--depth`, not `--review`.

### P3 - One Shared Public Doc Still Uses Claude-Era Delegation Vocabulary

Classification: stale port wording.

Evidence:

- `docs/COLLABORATIVE-DESIGN-PRINCIPLE.md:379` says "Task subagent".
- The same doc otherwise uses Codex-neutral `numbered choice prompt` wording.

Interpretation:

This is low risk because runtime skills and validators reject raw `Task` in the
active skill set. It is still worth cleaning because `AGENTS.md` points to this
doc as the full collaboration protocol.

Remediation target:

- Replace "Task subagent" with "Codex subagent delegation" or "subagent".

## Confirmed Expected Adaptations

- Claude `Task` delegation is normalized to Codex subagent delegation by exact
  hyphenated role name.
- Claude `AskUserQuestion` is normalized to numbered prompts or short-token
  fallback choices.
- `.claude` runtime paths are not runtime dependencies for Codex files.
- `notify.sh` is intentionally not wired because Codex lacks a project
  `Notification` lifecycle hook.
- The active dirty overlay correctly removes duplicate role-agent spawn-consent
  fallbacks and adds validation coverage for reintroductions.
- Handoff/resume exceptions are Codex-specific and intentionally authorize only
  their declared continuity file writes and, for `$handoff`, the standard
  handoff commit/push workflow.
- Release/install tooling is Codex-only extension work. It is outside upstream
  parity and should remain maintainer-explicit.

## Screenshot Behaviors

1. "Run Self-Check" offered as a user-selected next action:
   - Verdict: suspect Codex closeout regression.
   - Correct behavior: run the self-check automatically inside `design-system`
     Phase 5a, then proceed to the next workflow phase.
   - Do not ask until the workflow reaches a mutation or a genuine stop/next
     skill choice.

2. "Scan/update registry candidates" offered before candidate discovery:
   - Verdict: suspect Codex closeout regression if the prompt is for scanning;
     correct if the prompt is for writing.
   - Correct behavior: scan and summarize candidates automatically; ask
     "May I update `design/registry/entities.yaml`..." only after the summary.

## Priority Fix Queue

1. Fix closeout semantics:
   - Clarify that final `Next action` prompts apply at true pause/closeout
     boundaries, not before automatic read-only continuation phases in the
     active workflow.
   - Target files: `AGENTS.md`, `.codex/docs/session-continuity.md`, and
     high-traffic skill closeout sections.

2. Add behavioral closeout tests:
   - Target `design-system` Phase 5 self-check/registry scan and `design-review`
     Phase 5 post-revision tracking prompts.
   - Target files: `.agents/skills/skill-test/SKILL.md`,
     `.codex/lib/validate_runtime.py`, and relevant framework specs.

3. Make `design-review` path-rule handling explicit:
   - Add design path-rule reads before Phase 5 writes.

4. Clean inherited/stale wording:
   - `design-review`: `--review lean` -> `--depth lean`.
   - `docs/COLLABORATIVE-DESIGN-PRINCIPLE.md`: `Task subagent` -> Codex subagent
     wording.

## Verification

Pre-report validation:

```text
python3 .codex/lib/validate_manifest.py
status: pass

python3 .codex/lib/validate_runtime.py --kind docs
status: pass

python3 .codex/lib/validate_runtime.py --kind skills
status: pass

./.codex/audit.sh all
manifest: pass
runtime: pass
hooks: pass
config: pass
coexistence: pass
smoke-headless: pass
```

Post-report validation:

```text
python3 .codex/lib/validate_manifest.py
status: pass

python3 .codex/lib/validate_runtime.py --kind docs
status: pass

python3 .codex/lib/validate_runtime.py --kind skills
status: pass

./.codex/audit.sh all
manifest: pass
runtime: pass
hooks: pass
config: pass
coexistence: pass
smoke-headless: pass
```

## Scratch Evidence

Scratch directory:

`/private/tmp/ccgs-parity-audit-20260707/`

Key evidence artifacts:

- `upstream-984023d.5UnXhO/`: extracted upstream tree.
- `evidence-summary.md`: compact command/evidence summary for this audit.
