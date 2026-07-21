# Validation

Default validation is static and headless.

Required final gates:

```bash
./.codex/audit.sh release --root "$PWD"
./.codex/audit.sh all --root "$PWD"
./.codex/audit.sh smoke-headless --root "$PWD"
```

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
- `$resume-from-handoff` validation enforces the lane-selection pause, FIRST
  verification, structured follow-up forks, bounded-by-default slice reads,
  explicit deep mode, source precedence/freshness, cache readback, dynamic slice
  pointer, stage/catalog guards, and one-file session-cache boundary.
- `$handoff` validation enforces explicit transaction authorization, a reported
  context-capacity gate, session-baseline scope proof, bulk-directory
  trackability checks, and the compact resume-index contract.
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
