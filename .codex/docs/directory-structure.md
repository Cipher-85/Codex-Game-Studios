# Directory Structure

```text
/
├── AGENTS.md                    # Master configuration
├── .codex/                      # Agent definitions, hooks, command rules, docs
│   └── instructions/path-rules/ # Hidden path-scoped authoring rules
├── .agents/                     # Codex skill definitions
├── src/                         # Game source code
├── design/                      # Game design documents (gdd, narrative, levels, balance)
├── docs/                        # Technical documentation (architecture, api, postmortems)
│   └── engine-reference/        # Curated engine API snapshots (version-pinned)
└── production/                  # Production management (sprints, milestones, releases)
    └── session-state/           # Ephemeral session state (active.md — gitignored)
```

Workflow-owned visible folders are created lazily:

- `assets/` appears when data, shader, art, audio, or VFX workflows need it.
- `tests/` appears when `$test-setup`, test helpers, or regression workflows need it.
- `tools/` appears when a tool workflow needs it.
- `prototypes/` appears when `$prototype` or `$vertical-slice` needs it.
