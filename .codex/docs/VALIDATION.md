# Validation

Default validation is static and headless.

Required final gates:

```bash
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
- Runtime files must not depend on Claude-owned paths.
- Generated skills must not retain raw structured-choice tool names, raw Claude task-delegation syntax, unsupported frontmatter, or bare custom slash commands.
- Generated agents must not use unsupported top-level fields such as `tools`, `disallowedTools`, `maxTurns`, `memory`, `skills`, or `isolation`.
- Hooks must not include a `Notification` event.
