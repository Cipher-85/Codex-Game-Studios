# Codex Game Studios

Codex Game Studios turns a game repository into a Codex-native indie studio
workflow: 49 declared role profiles, 77 repo-local skills, verification-first handoffs, and
Godot-first production guidance for small teams building playable slices.

Current package version: `0.6.0`.

This project is an unofficial Codex-native port of
[Donchitos/Claude-Code-Game-Studios](https://github.com/Donchitos/Claude-Code-Game-Studios),
pinned to upstream commit `984023ddac0d5e27624f2baacde6105e45de375f`. It keeps
the upstream studio shape and MIT attribution while replacing Claude runtime
surfaces with Codex-native agents, skills, hooks, rules, and install behavior.

## What Is Included

- 49 Codex custom-agent profiles in `.codex/agents/*.toml`
- 77 repo-local Codex skills in `.agents/skills/*/SKILL.md`
  - 73 upstream workflow skills ported to Codex
  - 4 Codex support skills: `studio-status`, `studio-next`, `handoff`, and
    `resume-from-handoff`
- Root `AGENTS.md` startup instructions and hidden path rules under `.codex/`
- Codex hooks, command rules, config, installer, uninstaller, and validators
- Manual release tooling in `.codex/release.sh` with CI-backed consistency
  checks
- Ported docs, templates, production scaffolding, source placeholders, and the
  CCGS Skill Testing Framework
- Coexistence rules for repositories that already contain Claude Code files

## Current Status

The current release line is `v0.6.0`. It includes:

- Verified custom-role activation through `gpt-5.5` V1 and the experimental
  Sol V2 user workaround in both CLI and desktop, with `fork_turns: "none"`
  and authoritative metadata checks kept fail closed.
- Interactive smoke validation that cross-checks raw parent, child, and
  SubagentStart JSONL against the selected role TOML instead of accepting
  task names, self-identification, or summary assertions as proof.
- Remote-aware release validation that compares installable changes against
  origin tags and fails closed when tag or diff truth is unavailable.

The `v0.5.0` release also includes:

- Strict root and nested `.env*` filesystem protection with validator coverage
  and documented template-name compatibility.
- Fail-closed, manifest-owned install and uninstall behavior, including all 38
  test assets, conflict preflight, explicit backup-first replacement, and
  state-proven cleanup.
- Transaction rollback, trust and activation reporting, backward-compatible
  uninstall dry-run parsing, and temporary-target integration coverage.
- Codex-native skill QA across all 77 shipped skills without restoring
  unsupported Claude frontmatter or delegation vocabulary.
- A canonical advisory path-rule router with user-visible runtime enforcement
  limitations.

The `v0.4.7` release also includes:

- A hard `$resume-from-handoff` selection boundary: focus arguments only bias
  ranking, multi-lane choices prefer structured input, single-lane choices wait
  for numeric `1`, and no unselected lane starts automatically.
- Resume FIRST-verification and follow-up-fork safeguards so choosing a lane
  cannot waive owed checks or pre-authorize later workflow decisions.
- An optional project-local `$gen-asset` contract for direct built-in image
  generation, scratch-only staging, semantic ACTIVE/STUB profile validation,
  and one contact-sheet approval before exact final paths are written.
- Installer allowlisting that keeps `.agents/skills/gen-asset/**` trackable while
  leaving it project-owned, outside the 77 shipped skills, and outside package
  install/uninstall ownership.
- Release validation that rejects drift between `.codex/VERSION` and the
  version summaries in both README surfaces.

- User-owned playtest focus routing: when owed verification or the next action
  is a manual playtest, closeouts include a `Playtest focus:` brief with the
  hypothesis, setup/build, observation prompts, and verdict/evidence to return.
- `$playtest-report` templates and follow-up routing now require concrete
  hypotheses before sending the user back to play, while preserving the user's
  ownership of game-feel and balance verdicts.
- Runtime validation keeps the playtest-focus contract present in root
  instructions, session-continuity docs, and the playtest-report workflow.
- Active session-state checkpoint updates: after the user approves the
  underlying workflow artifact or decision, skills may update only
  `production/session-state/active.md` without asking a second "May I write?"
  question.
- Runtime validation for active.md write instructions in skills and generated
  role-agent prompts, so checkpoint writes must be described as derived state
  and must not ask a separate active.md write/update prompt.
- Installer `.gitignore` handling that keeps
  `production/session-state/active.md` local-only while preserving the tracked
  `production/session-state/.gitkeep` scaffold.
- A central role-agent delegation contract: invoking a CCGS skill authorizes
  only the role-agent spawns declared by that skill for that run.
- Review-mode clarification for director gates: `full` runs declared gates,
  `lean` keeps PHASE-GATE directors active at `$gate-check`, and `solo` skips
  director gates.
- Runtime fallback rules for stricter Codex sessions: ask once for delegation
  consent if required, and never simulate specialist or director verdicts when
  delegation is denied, skipped, blocked, or unavailable.
- Numbered closeout routing for completed work units: final responses now end
  with a `Next action:` prompt and exactly one numeric `(Recommended)` option,
  even when only one valid lane remains.
- Runtime validation for closeout-enforced skills so stale plain-text
  "one recommended next action" contracts fail before install or release.
- Updated quick-design and continuity handoff language so installed packages
  preserve the same numeric closeout format in downstream projects.
- Continuity recommendations now route through the live `## Session Worklist`
  and `## Phase Guard` in `production/session-state/active.md` instead of
  automatically invoking `$studio-next`.
- `$resume-from-handoff` compiles the session worklist from the canonical
  handoff, sprint status, active state, stage file, workflow catalog, and slice
  state at session entry.
- `$studio-next` is retained as a deprecated manual compatibility reference for
  old handoffs or explicit user requests.
- `$handoff` treats explicit invocation as approval for the full Codex-native
  handoff workflow: continuity updates, relevant path-scoped staging, the
  standard handoff commit, and a normal push.
- Low-friction CCGS decision prompts that list real viable options, mark one
  recommendation, and support short numbered or `a. yes` / `b. no` replies.
- `.gitignore` allowlist generation that keeps shared project content roots
  trackable while still managing CCGS-owned runtime paths.
- Package versioning through `.codex/VERSION`, release checks, and patch-aware
  installs introduced in `v0.2.0`.
- Defensive `apply_patch` hook payload parsing for both current Codex JSON
  argument shapes and legacy raw patch payloads.
- Root `AGENTS.md` guidance aligned with the upstream workflow contract:
  role registration comes from `.codex/agents/*.toml`, Claude runtime files are
  not Codex dependencies, and context-management decisions use the active
  reported context percentage.

## Runtime Parity Limits

This is a faithful semantic port with documented runtime limits, not a claim
that every Claude enforcement primitive exists in Codex:

- Fifteen upstream roles that denied Bash still require file writes, and Codex
  has no verified per-agent "files allowed, shell denied" fence. Their shell
  boundary is instruction-, rule-, and hook-backed rather than an exact hard
  fence.
- Upstream per-skill model tiers and per-agent `maxTurns` are preserved as
  guidance only. Session model choice and global agent concurrency/depth limits
  remain the available Codex controls.
- Prototype/worktree isolation is explicit workflow guidance, not automatic
  subagent isolation.
- Root `AGENTS.md` routes edits to `.codex/instructions/path-rules/*.md`.
  Nested Codex instructions load from the session root-to-CWD chain, so they do
  not reproduce upstream per-edited-file rule triggering in root-launched
  sessions.
- Project hooks, rules, and config require project trust and normally a new
  Codex session after installation.
- Current Codex documentation supports project custom-agent TOML files. On
  Codex CLI `0.144.1`, `gpt-5.6-sol` selects MultiAgent V2 and its stock tool
  schema hides custom-role selection, producing `agent_type: default` with
  generic child instructions. A `gpt-5.5` V1 parent is the verified fallback.
  Sol can expose role selection with the experimental user-level
  `[features.multi_agent_v2]` override documented below, but V2 custom roles
  must use `fork_turns: "none"`. CCGS blocks role-dependent gates unless runtime
  metadata, role instructions, model, and reasoning effort all confirm the
  matching custom profile loaded.

## Install

Install Codex Game Studios into a game project:

```bash
./.codex/install.sh /path/to/game-project
```

Validate an already-installed project from inside the target repository:

```bash
./.codex/install.sh "$PWD"
```

Preview install or uninstall actions without writing:

```bash
./.codex/install.sh --dry-run /path/to/game-project
./.codex/uninstall.sh --dry-run /path/to/game-project
```

Patch an existing install explicitly:

```bash
./.codex/install.sh --patch incremental /path/to/game-project
./.codex/install.sh --patch full /path/to/game-project
```

Installation preflights the complete target before writing. An unowned
collision or locally modified package-owned file aborts without mutation. After
reviewing the dry-run and conflict, explicitly replace only state-proven
package files with backup-first behavior:

```bash
./.codex/install.sh --dry-run --replace-modified /path/to/game-project
./.codex/install.sh --replace-modified /path/to/game-project
```

`--replace-modified` never authorizes overwriting an unowned shared file.

Remove Codex Game Studios from a project:

```bash
./.codex/uninstall.sh /path/to/game-project
```

Uninstall requires valid `.codex/manifest/install-state.json` ownership data.
Missing, stale, malformed, path-traversing, or symlinked state fails closed
without removing project files.

The installer appends a marked Codex Game Studios block to existing `AGENTS.md`
files instead of replacing project instructions. It preserves `CLAUDE.md`,
`claude.md`, and `.claude/**` when they exist, and it records installed package
ownership in `.codex/manifest/install-state.json`.

Optional project-local extensions such as `.agents/skills/gen-asset/**` are
allowlisted for tracking but are never copied, owned, or deleted by the CCGS
installer or uninstaller.

The default `game_studios` permission profile denies all access to root and
nested `.env*` files. This protects secrets through Codex filesystem access as
well as through the existing command rules and hooks, but it can also prevent
Codex from creating or editing files such as `.env.example`. Use an
agent-editable name such as `config.example` for non-secret templates.

Default install behavior is patch-aware: a fresh target receives a full install,
while a target with valid schema-v2 install state receives an incremental patch
based on recorded package file hashes. Invalid, unsafe, or stale state aborts
before mutation instead of being treated as ownership evidence.

Installer success proves package deployment and static verification only. Trust
the target project and start a new Codex session before treating its hooks,
rules, permission profile, or agents as active.

## Release Workflow

`.codex/VERSION` is the package version source of truth. The installer reads it
but never decides or mutates the release number.

Maintainer commands:

```bash
./.codex/release.sh current
./.codex/release.sh bump patch|minor|major
./.codex/release.sh check
./.codex/release.sh publish --dry-run
./.codex/release.sh publish
./.codex/audit.sh release --root "$PWD"
```

The release sequence is manual: bump the version, edit changelog/docs, run
`check`, commit and push to `origin/main`, then run `publish`. `bump` does not
publish. `publish --dry-run` performs the same local and remote read checks but
does not create tags or GitHub releases.

Codex package releases use namespaced GitHub tags such as `codex-v0.3.0` to
avoid collisions with inherited upstream Claude tags. Release titles and
changelog headings keep the human-facing `Codex Game Studios vX.Y.Z` and
`## vX.Y.Z` forms. Before publishing, the release script compares the target
commit against the actual previous release tag ref instead of GitHub Release
branch metadata, and it targets the repository configured as `origin`
explicitly. Release validation verifies that release metadata, changelog
entries, Codex package tags, and changed installable files are consistent, but
it does not create commits, create tags, edit files, publish, or choose release
numbers. GitHub Actions keep release validation as the required
release-specific check. Integrity, headless smoke, and temporary-target
installer regression jobs begin as advisory checks; publishing is always an
explicit maintainer command.

## Validate This Package

Run the static, release, and headless checks:

```bash
./.codex/audit.sh release --root "$PWD"
./.codex/audit.sh all --root "$PWD"
./.codex/audit.sh smoke-headless --root "$PWD"
```

The optional interactive smoke command is a non-mutating reminder, not proof of
a live model-running check:

```bash
./.codex/audit.sh smoke-interactive --root "$PWD"
```

It reports `status: skipped` until a trusted session is run and recorded
separately. The current CLI and desktop role-selection evidence is in the
[source-repository trusted-session report](https://github.com/Cipher-85/Codex-Game-Studios/blob/main/docs/codex-conversion/trusted-session-smoke-2026-07-12.md).

Validate a separately captured role-activation record with:

```bash
./.codex/audit.sh smoke-interactive --root "$PWD" \
  --evidence /path/to/role-activation-evidence.json
```

For CLI-only Sol probes, pass ephemeral overrides rather than modifying project
configuration:

```bash
codex exec --strict-config -s read-only -m gpt-5.6-sol \
  -c 'features.multi_agent_v2.hide_spawn_agent_metadata=false' \
  -c 'features.multi_agent_v2.tool_namespace="agents"' \
  '<request a custom role with fork_turns set to none>'
```

These nested V2 keys are recognized by Codex `0.144.x` but are not documented
in the public configuration reference. Do not ship them in project
`.codex/config.toml`; treat them as a temporary user-level workaround and
re-verify them after every Codex update.

## Coexistence With Claude Code

Codex Game Studios is intentionally additive:

- It does not write to `.claude/`.
- It does not require or modify `CLAUDE.md`.
- It detects `codex_only`, `claude_present_no_ccgs`, and
  `claude_ccgs_coexist` separately.
- It keeps shared game state in neutral project paths such as `production/`,
  `design/`, `docs/architecture/`, and `src/`.

Root `LICENSE` belongs to this public source distribution. Installed target game
repositories receive the upstream license copy at
`.codex/docs/UPSTREAM-LICENSE.md` so their own root license is not overwritten.

## Attribution

Forked from
[Claude Code Game Studios](https://github.com/Donchitos/Claude-Code-Game-Studios)
by Donchitos and ported to Codex-native runtime surfaces. See
[ATTRIBUTION.md](ATTRIBUTION.md), [PORTING_NOTES.md](PORTING_NOTES.md), and
[docs/codex-conversion/](docs/codex-conversion/) for lineage, mapping evidence,
and conversion notes.

## Key Docs

- [.codex/docs/README.md](.codex/docs/README.md)
- [.codex/docs/VALIDATION.md](.codex/docs/VALIDATION.md)
- [.codex/docs/COEXISTENCE.md](.codex/docs/COEXISTENCE.md)
- [PORTING_NOTES.md](PORTING_NOTES.md)
- [CHANGELOG.md](CHANGELOG.md)
