# Validation

Default validation is static and headless.

`audit.sh all` includes configuration, migration, artifact-reader, hook and
installer fixtures. These checks validate package behavior in temporary trees;
they do not invoke a live skill, establish role loading, or run a game engine.
The artifact reader's graph tests include all 512 directed graphs on three
nodes. Counts, matching hashes and a successful package install remain distinct
from workflow acceptance and observed game behavior.

Required final gates:

```bash
./.codex/audit.sh release --root "$PWD"
./.codex/audit.sh all --root "$PWD"
./.codex/audit.sh smoke-headless --root "$PWD"
```

Run `audit.sh docs` for documentation links/contracts. Individual fixture suites
are available as `project-config`, `config-migration`, and `artifact-facts`.
`all` already includes headless smoke and the installer matrix; repeating them
is needed only for changed inputs, failures or a separately required gate.

## Native acceptance for the selective update

Recorded 2026-10-21: **30/30 cases accepted for their declared native
assertions.** This combines approved runs from October 20-21; each receipt keeps
its own runtime, scope and chronology. It is not an all-skills or engine/gameplay
acceptance claim. Expected fixture outcomes include NEEDS WORK, CONCERNS, FAIL
and NOT ASSESSED; a case passes when it preserves those findings correctly.

Local evidence is retained under
`/private/tmp/ccgs-native-validation-20261020/`: `cases.json` is the logical
matrix, `README.md` summarizes it, and the per-case `native/` receipts retain
raw output, approvals, identities, hashes/modes and closure checks. Earlier
PARTIAL attempts remain alongside their accepted replays. These local files are
evidence, not shipped runtime dependencies.

| Area | Accepted native scope and limits |
| --- | --- |
| Settings and migration: 3 | Inspection/preview, invalid-input refusal, declined-write preservation, explicitly approved staging/rollback, stale-plan refusal and bounded interruption/recovery. Process-kill and power-loss behavior remain untested. |
| Workflow and stage: 8 | Brief/tier/system-override behavior, recorded stage provenance, target confirmation, terminal/unset routing and honest quality/evidence verdicts. Passing assertions do not authorize stage advancement. |
| QA and teams: 8 | Missing/failed evidence remains blocking across QA levels and strictness settings. Individual/small/studio retain required owners; actual qa-lead strategy stops before approval, plan write and later qa-tester execution. |
| Role routing: 3 | Full runs ordinary qa-lead plus all four phase directors; lean runs the four phase directors; solo skips those gates. Raw child metadata, complete matching instructions, configured models and hooks corroborate actual loading. Capacity scheduling and limited overlap are recorded explicitly. |
| Source roots: 6 | Native/custom path-discovery preflights only. Unknown/conflicting scope stays unresolved; target-source scans and full code-review findings remain unassessed. |
| Artifacts: 2 | All four readers observed empty/adversarial inputs. Header/evidence separation, ambiguity, incomplete/cyclic graphs, placeholders and unknown bug fields remain visible. Default full design review ran five actual specialists then the senior reviewer, preserving disagreements. Unset primary-specialist routing left the architecture engine-consultation branch explicitly unassessed. |

The final batch used Codex CLI 0.163.0, gpt-6.1-sol/high, read-only sandbox and
on-request approval. All 49 configured role model/effort settings were preserved.
The approved validator correction accepts current typed subagent-start events
as well as legacy events, with ten regression fixtures and actual native role
packets checked; raw evidence was not rewritten to fit the validator.

After that correction, `release`, `all`, `smoke-headless` and `docs` audits
passed. These package results remain separate from native case acceptance.
Preservation receipts retain frozen inputs, approved runtime outputs and exact
authorized mutations; successful owned panes were captured and closed.

Hook trust was preauthorized. Two captured launches also included
`--dangerously-bypass-hook-trust`; installed hooks stayed unchanged and active,
with read-only/on-request retained. Those runs do not independently test manual
hook-trust gating without that flag.

**Still unassessed:** pinned Godot/Unity/Unreal runner execution, fresh game-test
results, imports/builds, opened visual captures, gameplay/performance and
platform acceptance. Source-root preflights and synthetic evidence do not
supply them. The package remains local, uncommitted and unreleased at 0.7.4.
Version selection, commit, push, tag, publication and downstream deployment
remain separate user decisions; a release-audit PASS performs none of them.

### Phase 6B fixture preparation

The following is the historical preparation record; dated native results above
now supersede its starting NOT RUN status.

The approved preparation scope is the two documentation corrections and
disposable inputs under `/private/tmp/ccgs-native-validation-20261020/`.
Preparation does not authorize native sessions, role spawns, engine execution,
or the migration/stage writes exercised by later cases. Those operations retain
their normal invocation and exact-path approval boundaries.

The scratch directory contains a copy installed from the current working
package, independent case projects, `cases.json`, input hashes and preparation
results. The source snapshot includes uncommitted changes: a worktree created
from HEAD would omit this migration. Preserve the snapshot and per-case baseline
hashes so a later run identifies the actual package and any changed inputs.
The scratch files are local evidence, not shipped runtime dependencies; copy
the evidence elsewhere only with authority for that destination.

| Case group | Prepared inputs and native assertions |
| --- | --- |
| Settings | Project/local/legacy precedence, assignment preview and invalid configuration; declined writes preserve hashes. Migration starts from legacy-only input, previews every path, and later tests approved staging, rollback and stale-plan refusal. |
| Workflow and stage | Minimal brief, standard numeric GDD, full GDD and per-system overrides; preserve project-wide prerequisites. YAML versus legacy stage, unset/terminal stage and empty inputs stay explicit. Only a real PASS can offer the exact-target write and readback. |
| QA and teams | Every QA level with missing or failed synthetic evidence and strictness disabled; an advisory-only strictness case; individual/small/studio participation. Mandatory evidence and required owners remain blocking/present. |
| Role routing | Full/lean/solo inputs exercise both ordinary and phase gates. Record the actual filtered roster, unavailable roles and raw activation evidence; a role name or coordinator-written verdict cannot prove loading. |
| Source roots | Godot, Unity and Unreal conventions, a custom path, unknown input and conflicting markers. Actual skill output retains unresolved/invalid scope and never invents an empty successful scan. |
| Artifacts | Distinct story/evidence status, ambiguous headers, incomplete/cyclic ADR graphs, GDD placeholders and unknown bug fields. Counts and helper exit codes cannot establish readiness, closure or a complete graph. |

Use `cases.json` for the exact input, planned skill invocation and assertions.
All cases start as **NOT RUN**. Read-only helper checks in preparation results
establish fixture shape only, even when their exit status is zero.
`$skill-test spec` evaluates written instructions and cannot substitute for
these native invocations.

Before a native case, bind the new session to its exact case project and verify
the package/input hashes. This task's native creation API inherits its working
directory; it cannot by itself prove a new task loaded a different fixture root.
Use a supported explicit-root launch, or leave the case blocked with the missing
launch step. Do not substitute a nested CLI or subagent for an independently
rooted session. Keep the source repository untouched by case mutations.

For each later result retain case ID, canonical root, package/input hashes,
runtime version, invocation, raw output, approvals/declines, before/after hashes
and observed verdict. Approved changes need exact-path readback. For role cases,
also retain parent/child IDs, raw rollouts and the matching SubagentStart record,
then run the interactive validator below against the same role TOML. Missing
raw records or mismatched identity leave role acceptance unverified.

Engine execution remains a separate readiness gate. The preparation inspection
observed Godot 4.7.2 while the shipped reference pins 4.6; that executable cannot
prove acceptance against the pin. Unity/Unreal executables were not found on
PATH or in the inspected application locations; this is not proof that no other
installation exists. Resolve the actual runner and version before an approved
engine case; preserve all shipped pins. No engine install, upgrade or launch is
part of fixture preparation.

## Runtime smoke evidence

Optional interactive smoke:

```bash
./.codex/audit.sh smoke-interactive --root "$PWD"
./.codex/audit.sh smoke-interactive --root "$PWD" \
  --evidence /path/to/role-activation-evidence.json
```

Without evidence, this command reports `status: skipped`; it does not claim
that a model-running smoke occurred. With evidence, it parses the raw parent
rollout, child rollout, and SubagentStart JSONL and cross-checks role metadata,
instructions, model, effort, child identity, and V2 fork mode against the
authoritative role TOML. Interactive smoke depends on project trust, auth,
approvals, and model access, so it is recorded separately from the default
acceptance gate. A trusted run should verify project skill discovery, strict config,
ordinary-file controls, `.env*` read/write denial, SessionStart/PreToolUse/
PostToolUse/SubagentStart/SubagentStop hooks, configured model routes, footer
items, and authoritative custom-agent type/instruction evidence. MultiAgent V2
custom-role evidence requires `fork_turns: "none"`.

Validator policy:

- Python validators use only the standard library.
- Release validation is non-mutating. It verifies `.codex/VERSION`,
  `CHANGELOG.md`, origin's `codex-vX.Y.Z` package tags, and changed installable
  files through read-only `git ls-remote`; unavailable remote tag truth fails
  closed. It does not create tags, edit files, publish, or bump versions. The
  legacy `v0.1.0` tag is accepted only as the initial Codex-port baseline;
  inherited upstream Claude tags such as plain `v0.2.0`, `v0.3.0`, and
  `v1.0.0` are ignored.
- GitHub Actions are validation-only. Maintainers publish explicitly with
  `./.codex/release.sh publish` after the version bump, changelog/docs update,
  release check, commit, and push have completed. Publish checks for new
  commits against the actual previous release tag ref, not mutable GitHub
  Release branch metadata.
- Runtime files must not depend on Claude-owned paths.
- CCGS does not validate Agent Bindery's global skill implementation. Runtime
  validation instead rejects repo-local copies of `handoff` and
  `resume-from-handoff`, validates `.agent-continuity.toml`, and checks that its
  four project modules preserve the CCGS phase/slice, lane, integrity, and
  review-tier contracts.
- Agent Bindery owns continuity bootstrap, freshness, review, rotation, commit,
  and push behavior. Validate that implementation in the Agent Bindery
  repository; CCGS audits only its integration surface.
- Hook fixtures cover handoff-only recovery, handoff plus substantive active
  state, pointer-only active state, compaction ordering, and baseline JSON.
- If an optional project-local `$gen-asset` skill exists, validation rejects
  nested Codex CLI generation, legacy runtime paths, API/CLI fallbacks, and
  unbounded newest-image discovery. ACTIVE profiles require the full semantic
  schema; minimal STUB profiles remain valid refusal markers.
- Coexistence validation requires `.agents/skills/gen-asset/**` to stay
  trackable while remaining absent from package ownership.
- Release validation requires the root and `.codex` README version summaries
  to match `.codex/VERSION`.
- Generated skills must not retain raw structured-choice tool names, raw Claude task-delegation syntax, unsupported frontmatter, or bare custom slash commands.
- Generated agents must not use unsupported top-level fields such as `tools`, `disallowedTools`, `maxTurns`, `memory`, `skills`, or `isolation`.
- Ported skills keep only `name` and `description` in Codex frontmatter and
  preserve documentary `argument-hint`, `user-invocable`, and `allowed-tools`
  in `## Ported metadata`. Codex-native support skills declare that status
  instead of inventing upstream fields.
- Run `./.codex/audit.sh coexistence --root "$PWD" --integration` for the
  temporary-target install, unowned/modified conflict, preserved-shared mode
  transition, missing/stale/unsafe state, path traversal, rollback failpoint,
  dry-run, known-obsolete, and uninstall matrix.
- Hooks must not include a `Notification` event.
- The Bash PreToolUse secret guard must block `.env` reads, writes, and
  redirections through `tool_input.command`; prefix rules only cover direct
  tokenized examples.
