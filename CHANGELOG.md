# Changelog

## v0.7.0 - 2026-07-20

- Completed the default `game_studios` permission profile with writable Git and
  Codex runtime directories, strict root and nested `.env*` denials, and network
  access limited to `github.com` without overriding the user's approval policy.
- Updated `$handoff` to preflight Git metadata and the exact push destination,
  use scoped permission fallbacks only when the active session needs them, and
  retry once only for a pre-contact DNS-resolution failure.
- Added config and runtime validation for the complete profile and handoff
  contract, then verified the workflow in a fresh Stillcurrent session that
  committed and pushed without a manual permission-mode switch.

## v0.6.1 - 2026-07-16

- Hardened `$handoff` push routing so existing-upstream branches use plain
  `git push`, while only branches without an upstream use
  `git push -u origin <branch>`.
- Added same-turn GitHub account, destination, and repository-permission checks
  before handoff pushes, avoiding false authentication conclusions from
  network-restricted sandbox failures.
- Scoped push escalation to `["git", "push"]` and made policy denials fail
  closed without alternate-command retries or workarounds.

## v0.6.0 - 2026-07-12

- Made `audit smoke-interactive` report an explicit skipped result instead of a
  false pass when no trusted model-running smoke occurred, and added raw parent,
  child, and SubagentStart evidence validation for recorded role activation.
- Verified existing custom-role profiles under a `gpt-5.5` V1 parent and the
  experimental Sol V2 user override in both CLI and desktop; documented
  `fork_turns: "none"`, authoritative metadata requirements, and the stock Sol
  limitation without renaming or re-registering role files.
- Added live trust, filesystem, hook, skill, model-route, footer, and
  custom-role evidence with fail-closed regression fixtures.
- Made release validation query origin tags read-only and fail closed when
  remote tag truth or the release diff cannot be established.
- Expanded `audit all` to include the shipped skill and custom-agent validators.

## v0.5.0 - 2026-07-12

- Added strict root and nested `.env*` filesystem denies with regression
  validation and documented template-name compatibility.
- Made install and uninstall manifest-owned and fail closed: all 38 test assets
  are now owned, brownfield conflicts preflight before mutation, modified
  package files require explicit backup-first replacement, and obsolete cleanup
  no longer infers ownership from file contents or empty directories.
- Added normalized install-state path validation, explicit package-owned paths,
  preserved-shared exclusion, and fail-closed missing/stale-state uninstall.
- Added transaction rollback, trust/activation messaging, backward-compatible
  uninstall dry-run parsing, and an opt-in temporary-target integration matrix.
- Corrected skill QA to validate Codex frontmatter plus Ported metadata, updated
  all 73 framework skill specs, and removed stale Claude delegation vocabulary.
- Recorded the root path-rule router as the canonical advisory architecture and
  exposed enforcement limitations in user-facing documentation.

## v0.4.7 - 2026-07-10

- Added a hard `$resume-from-handoff` lane-selection boundary: focus arguments
  no longer imply selection, multiple lanes use structured choice when
  available, single lanes wait for numeric `1`, and follow-up forks remain
  separate decisions.
- Kept FIRST verification mandatory across resume lane choices and clarified
  that entering a selected workflow grants no additional mutation authority.
- Added validation for optional project-local `$gen-asset` cores and profiles,
  rejecting nested Codex CLI/API fallbacks and allowing complete ACTIVE or
  minimal STUB profiles.
- Updated installer allowlisting so `.agents/skills/gen-asset/**` is trackable
  without becoming package-owned or changing the 77 shipped-skill count.
- Documented Claude-to-Codex project-local profile migration, scratch-only image
  generation authorization, and the contact-sheet placement gate.
- Corrected stale README version summaries and made release validation reject
  future README/package-version drift.

## v0.4.6 - 2026-07-10

- Restored `$handoff`'s mandatory two-round review gate, including
  standard/adversarial tier selection, pure-document exemptions, finding
  triage, conditional second review, pass caps, and an auditable handoff record.
- Kept the cross-check inside the active Codex session and explicitly removed
  nested Codex CLI, Claude companion, subprocess, subagent, and external model
  review paths.
- Expanded the `$handoff` authorization boundary for narrow intent-preserving
  fixes and added runtime validation to prevent the review contract or its
  no-egress safeguards from regressing.

## v0.4.5 - 2026-07-09

- Updated `$bug-report verify` so a VERIFIED FIXED result can complete
  verification evidence, closure, safe stale triage cleanup, and derived
  session-state routing under one approved changeset.
- Updated `$bug-report close` so already verified bugs can close and refresh
  stale triage metadata without handing the user a separate bookkeeping prompt.
- Clarified `$bug-triage` zero-open-bugs closure refreshes as deterministic
  metadata cleanup when they do not require priority, sprint-scope, severity, or
  Won't Fix decisions.
- Added runtime validation to keep the bug lifecycle contract from regressing
  back into forced verify -> close -> triage handoffs.

## v0.4.4 - 2026-07-09

- Added a user-owned playtest focus contract so closeouts and owed verification
  must include a `Playtest focus:` brief instead of generic playtest requests.
- Updated session continuity guidance to preserve the playtest hypothesis,
  setup/build, observation prompts, and requested verdict/evidence in
  `## Session Worklist` entries.
- Updated `$playtest-report` templates and routing so new reports and follow-up
  playtests carry a concrete hypothesis while leaving game-feel and balance
  verdicts with the user.
- Added runtime validation to keep the playtest-focus rule present in root
  instructions, continuity docs, and the playtest-report workflow.

## v0.4.3 - 2026-07-08

- Tightened the role-agent delegation contract so invoking a CCGS skill is the
  authorization for its declared role-agent spawns after review-mode filtering;
  duplicate spawn-consent prompts are no longer part of normal skill flow.
- Clarified director gate behavior: `full` runs declared gates immediately,
  `lean` skips non-PHASE-GATE reviews such as `CD-GDD-ALIGN`, and `solo` skips
  all director gates.
- Added runtime and skill validation coverage to reject reintroduced duplicate
  spawn-consent fallback wording.
- Fixed closeout-boundary wording so automatic read-only workflow phases
  continue without being offered as user-selected `Next action` prompts, while
  registry, index, review-log, durable artifact, commit, push, and branch
  mutations remain explicitly permission-gated.
- Restored upstream no-Bash role boundaries as explicit Codex instructions for
  the 15 affected agents, with runtime validation preventing regressions.
- Added a Bash PreToolUse `.env` secret guard that blocks reads, writes, and
  redirections from `tool_input.command`, plus fixtures, docs, and manifest
  coverage.
- Corrected mechanically corrupted task-tracking skill wording while preserving
  genuine Codex role-agent delegation instructions.

## v0.4.2 - 2026-07-07

- Added a narrow active session-state checkpoint exception: after the user
  approves the underlying workflow artifact or decision, skills may update only
  `production/session-state/active.md` without asking a second "May I write?"
  question.
- Updated high-traffic design, architecture, QA, story, and continuity skills,
  plus generated design role-agent prompts, to treat `active.md` writes as
  derived checkpoints while preserving normal approval gates for durable
  artifacts, source edits, commits, pushes, builds, and new decisions.
- Extended runtime validation so active.md write instructions in both skills and
  role-agent prompts must include no-extra-approval language and must not ask a
  separate active.md write/update prompt.
- Kept installed `production/session-state/active.md` local-only by updating
  package and installer `.gitignore` handling while preserving the tracked
  `production/session-state/.gitkeep` scaffold.

## v0.4.1 - 2026-07-06

- Added a central Role-Agent Delegation Authorization contract so explicit CCGS
  skill invocation authorizes only the role-agent spawns declared by that skill
  for the current run.
- Clarified director gate review-mode behavior: `full` runs declared gates,
  `lean` runs PHASE-GATE directors at `$gate-check`, and `solo` skips director
  gates.
- Added runtime-fallback wording that asks once for delegation consent when
  required and forbids simulated specialist or director verdicts when delegation
  is denied, skipped, blocked, or unavailable.
- Extended `$skill-test` behavioral checks so subagent-using skills must rely on
  the central delegation contract and report missing role-agent reviews instead
  of replacing them with internal simulation.

## v0.4.0 - 2026-07-06

- Required closeout-enforced skills and shared continuity docs to end completed
  work units with a numbered `Next action:` prompt, even when there is only one
  valid lane.
- Standardized the final-response format on a numeric-only
  `1. (Recommended)` option so users can reply with `1` instead of parsing a
  plain-text next-action sentence.
- Added runtime validation that rejects closeout-enforced skills retaining the
  older "one recommended next action" wording or missing numbered next-action
  routing language.
- Updated the quick-design handoff template and installed package outputs so
  downstream projects receive the same numeric closeout contract.

## v0.3.3 - 2026-07-05

- Reworked continuity routing so post-work recommendations read the live
  `## Session Worklist` and `## Phase Guard` in
  `production/session-state/active.md` instead of automatically routing through
  `$studio-next`.
- Made `$resume-from-handoff` the session-entry compiler that reads the
  canonical handoff, sprint status, active state, `production/stage.txt`, and
  `.codex/docs/workflow-catalog.yaml`, then writes the ranked session cache.
- Deprecated `$studio-next` to a manual compatibility reference while updating
  core closeout skills, phase help, and continuity docs to recommend the top
  valid lane from `active.md`.

## v0.3.2 - 2026-07-05

- Made explicit `$handoff` invocation authorize the Codex-native handoff workflow
  end to end: continuity-file updates, path-scoped staging, the standard
  handoff commit, and a normal push of the current branch.
- Kept the exception narrowly scoped to `$handoff` so upstream-style
  collaboration rules and other skills continue to require explicit write
  approval.
- Documented the `$handoff` safety bounds: no new source edits during handoff,
  no undeclared file writes, no branch switching, no force-pushes, and no
  `--no-verify` or amend workarounds.

## v0.3.1 - 2026-07-05

- Added low-friction CCGS decision-prompt rules so next-step handoffs list real
  viable options, mark one recommendation, and use short numbered or `a. yes` /
  `b. no` responses when Codex has no clickable choice UI.
- Updated `$studio-next` to rank viable next actions instead of collapsing most
  situations to a single next step, while keeping mandatory gates as go/no-go
  prompts.
- Kept generated `.gitignore` allowlists from blanket-reignoring shared project
  content roots such as `design/`, `docs/`, `production/`, and `src/`, with
  validation coverage for trackability.

## v0.3.0 - 2026-07-04

- Aligned root `AGENTS.md` with the upstream workflow contract, including
  authoritative role registration from `.codex/agents/*.toml`, exact
  hyphenated role names, resume and wrap-up routing, collaboration boundaries,
  path-rule routing, verification integrity, and context-management guidance.
- Fixed hook parsing for Codex `apply_patch` payloads by centralizing payload
  extraction in `.codex/lib/hooks.sh`, supporting current JSON argument shapes,
  and retaining a legacy raw-patch fixture for compatibility.
- Updated hook and setup documentation to reflect Python-backed parsing and
  jq's reduced role as an optional debugging aid.
- Updated workflow and conversion docs for PostToolUse `apply_patch` advisory
  timing and current Codex hook matcher behavior.
- Refreshed public status docs for the current package state after the v0.2.0
  release tooling and patch-install work.
- Added an explicit `./.codex/release.sh publish` command for manual GitHub
  Release creation with clean-worktree, authenticated `gh`, `origin/main`,
  changelog, and tag-target checks.
- Made publish check for new commits against the actual previous release tag
  ref instead of relying on GitHub Release branch metadata.
- Made publish pass the `origin` repository explicitly to GitHub release calls
  instead of relying on `gh` repository auto-detection.
- Switched Codex package publishing and release validation to namespaced
  `codex-vX.Y.Z` tags while keeping the legacy `v0.1.0` baseline accepted and
  ignoring inherited upstream Claude release tags.

## v0.2.0 - 2026-07-04

- Added `.codex/VERSION` as the CCGS package version source of truth.
- Added manual release tooling with `current`, `bump`, and `check` commands.
- Added schema-2 install state with package version, commit, patch mode, file
  hashes, and marker-block hashes.
- Added patch-aware installs with default full installs for fresh or old-state
  targets and incremental patching for modern install state.
- Added release validation to `.codex/audit.sh release` and GitHub Actions.

## v0.1.0 - 2026-07-03

Initial Codex Game Studios public fork release.

- Ported the Claude Code Game Studios role-agent and workflow-skill structure to
  Codex-native agents, skills, hooks, command rules, and startup instructions.
- Added install, uninstall, coexistence, and validation support for target game
  repositories.
- Preserved upstream MIT attribution and added an installed license copy at
  `.codex/docs/UPSTREAM-LICENSE.md`.
- Kept detailed conversion evidence under `docs/codex-conversion/` while moving
  release-facing usage docs to the root README and `.codex/docs/`.
