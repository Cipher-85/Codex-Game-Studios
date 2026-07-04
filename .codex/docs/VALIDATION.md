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
```

Interactive smoke can depend on project trust, auth, approvals, and model access, so it is not required for the default acceptance gate.

Validator policy:

- Python validators use only the standard library.
- Release validation is non-mutating. It verifies `.codex/VERSION`,
  `CHANGELOG.md`, `codex-vX.Y.Z` package tags, and changed installable files,
  but it does not create tags, edit files, publish, or bump versions. The
  legacy `v0.1.0` tag is accepted only as the initial Codex-port baseline;
  inherited upstream Claude tags such as plain `v0.2.0`, `v0.3.0`, and
  `v1.0.0` are ignored.
- GitHub Actions are validation-only. Maintainers publish explicitly with
  `./.codex/release.sh publish` after the version bump, changelog/docs update,
  release check, commit, and push have completed.
- Runtime files must not depend on Claude-owned paths.
- Generated skills must not retain raw structured-choice tool names, raw Claude task-delegation syntax, unsupported frontmatter, or bare custom slash commands.
- Generated agents must not use unsupported top-level fields such as `tools`, `disallowedTools`, `maxTurns`, `memory`, `skills`, or `isolation`.
- Hooks must not include a `Notification` event.
