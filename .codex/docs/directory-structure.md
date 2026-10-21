# Directory Structure

```text
/
├── AGENTS.md                    # Master configuration
├── .codex/                      # Agent definitions, hooks, command rules, docs
│   └── instructions/path-rules/ # Hidden path-scoped authoring rules
├── .agents/                     # Codex skill definitions
├── src/                         # Conventional Godot source location only
├── design/                      # Game design documents (gdd, narrative, levels, balance)
├── docs/                        # Technical documentation (architecture, api, postmortems)
│   └── engine-reference/        # Curated engine API snapshots (version-pinned)
└── production/                  # Production management (sprints, milestones, releases)
    └── session-state/           # Ephemeral session state (active.md — gitignored)
```

Game source and content locations depend on the engine and existing project:

| Engine | Conventional source | Conventional content |
| --- | --- | --- |
| Godot | `src/`, or existing scripts elsewhere in the project | Existing scene/resource folders |
| Unity | `Assets/`, plus local source in `Packages/` | `Assets/` and package content |
| Unreal | `Source/`, plus project plugin source in `Plugins/` | `Content/` and plugin content |

Before scans or source writes, apply **Source scope** in
`.codex/docs/technical-config.md` and run `project_config.py code-root`.
Preserve custom layouts and engine-native test paths. Unresolved scope is
NOT ASSESSED; these conventions neither create folders nor prove an empty game.

Workflow-owned visible folders are created lazily:

- `assets/` appears when data, shader, art, audio, or VFX workflows need it.
- `tests/` appears when `$test-setup`, test helpers, or regression workflows need it.
- `tools/` appears when a tool workflow needs it.
- `prototypes/` appears when `$prototype` or `$vertical-slice` needs it.
