# Codex Game Studios

Codex Game Studios turns a game repository into a Codex-native indie studio
workflow: 49 role agents, 77 repo-local skills, verification-first handoffs, and
Godot-first production guidance for small teams building playable slices.

Current package version: `0.4.4`.

This project is an unofficial Codex-native port of
[Donchitos/Claude-Code-Game-Studios](https://github.com/Donchitos/Claude-Code-Game-Studios),
pinned to upstream commit `984023ddac0d5e27624f2baacde6105e45de375f`. It keeps
the upstream studio shape and MIT attribution while replacing Claude runtime
surfaces with Codex-native agents, skills, hooks, rules, and install behavior.

## What Is Included

- 49 Codex custom agents in `.codex/agents/*.toml`
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

The current release line is `v0.4.4`. It includes:

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

Remove Codex Game Studios from a project:

```bash
./.codex/uninstall.sh /path/to/game-project
```

The installer appends a marked Codex Game Studios block to existing `AGENTS.md`
files instead of replacing project instructions. It preserves `CLAUDE.md`,
`claude.md`, and `.claude/**` when they exist, and it records installed package
ownership in `.codex/manifest/install-state.json`.

Default install behavior is patch-aware: a fresh target or old install-state
schema receives a full install, while a target with modern install state receives
an incremental patch based on recorded package file hashes.

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
numbers. GitHub Actions run release validation only; publishing is always an
explicit maintainer command.

## Validate This Package

Run the static, release, and headless checks:

```bash
./.codex/audit.sh release --root "$PWD"
./.codex/audit.sh all --root "$PWD"
./.codex/audit.sh smoke-headless --root "$PWD"
```

The optional interactive smoke command exists as a Codex environment check, not
as a CCGS workflow:

```bash
./.codex/audit.sh smoke-interactive --root "$PWD"
```

It may intentionally skip when the current Codex session lacks project trust,
auth, approvals, or model access.

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
