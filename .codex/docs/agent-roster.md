# Agent Roster

The following agents are available. Each has a dedicated definition file in
`.codex/agents/`. Use the agent best suited to the task at hand. When a task
spans multiple domains, the coordinating agent (usually `producer` or the
domain lead) should delegate to specialists.

Model labels below are upstream Claude tier labels retained for parity. The
active Codex model and reasoning mapping is defined in `.codex/agents/*.toml`.

Some upstream roles declared `disallowedTools: Bash`. Codex custom-agent TOML
does not support that field, so those roles carry an explicit instruction-level
boundary instead: they must not run shell commands and should ask the parent
session for command evidence.

## Tier 1 -- Leadership Agents (Upstream Opus Tier)
| Agent | Domain | When to Use |
|-------|--------|-------------|
| `creative-director` | High-level vision | Major creative decisions, pillar conflicts, tone/direction |
| `technical-director` | Technical vision | Architecture decisions, tech stack choices, performance strategy |
| `producer` | Production management | Sprint planning, milestone tracking, risk management, coordination |

## Tier 2 -- Department Lead Agents (Upstream Sonnet Tier)
| Agent | Domain | When to Use |
|-------|--------|-------------|
| `game-designer` | Game design | Mechanics, systems, progression, economy, balancing |
| `lead-programmer` | Code architecture | System design, code review, API design, refactoring |
| `art-director` | Visual direction | Style guides, art bible, asset standards, UI/UX direction |
| `audio-director` | Audio direction | Music direction, sound palette, audio implementation strategy |
| `narrative-director` | Story and writing | Story arcs, world-building, character design, dialogue strategy |
| `qa-lead` | Quality assurance | Test strategy, bug triage, release readiness, regression planning |
| `release-manager` | Release pipeline | Build management, versioning, changelogs, deployment, rollbacks |
| `localization-lead` | Internationalization | String externalization, translation pipeline, locale testing |

## Tier 3 -- Specialist Agents (Upstream Sonnet or Haiku Tier)
| Agent | Domain | Upstream Tier | When to Use |
|-------|--------|-------|-------------|
| `systems-designer` | Systems design | Upstream Sonnet | Specific mechanic implementation, formula design, loops |
| `level-designer` | Level design | Upstream Sonnet | Level layouts, pacing, encounter design, flow |
| `economy-designer` | Economy/balance | Upstream Sonnet | Resource economies, loot tables, progression curves |
| `gameplay-programmer` | Gameplay code | Upstream Sonnet | Feature implementation, gameplay systems code |
| `engine-programmer` | Engine systems | Upstream Sonnet | Core engine, rendering, physics, memory management |
| `ai-programmer` | AI systems | Upstream Sonnet | Behavior trees, pathfinding, NPC logic, state machines |
| `network-programmer` | Networking | Upstream Sonnet | Netcode, replication, lag compensation, matchmaking |
| `tools-programmer` | Dev tools | Upstream Sonnet | Editor extensions, pipeline tools, debug utilities |
| `ui-programmer` | UI implementation | Upstream Sonnet | UI framework, screens, widgets, data binding |
| `technical-artist` | Tech art | Upstream Sonnet | Shaders, VFX, optimization, art pipeline tools |
| `sound-designer` | Sound design | Upstream Sonnet | SFX design docs, audio event lists, mixing notes |
| `writer` | Dialogue/lore | Upstream Sonnet | Dialogue writing, lore entries, item descriptions |
| `world-builder` | World/lore design | Upstream Sonnet | World rules, faction design, history, geography |
| `qa-tester` | Test execution | Upstream Haiku | Writing test cases, bug reports, test checklists |
| `performance-analyst` | Performance | Upstream Sonnet | Profiling, optimization recs, memory analysis |
| `devops-engineer` | Build/deploy | Upstream Haiku | CI/CD, build scripts, version control workflow |
| `analytics-engineer` | Telemetry | Upstream Sonnet | Event tracking, dashboards, A/B test design |
| `ux-designer` | UX flows | Upstream Sonnet | User flows, wireframes, accessibility, input handling |
| `prototyper` | Rapid prototyping | Upstream Sonnet | Throwaway prototypes, mechanic testing, feasibility validation |
| `security-engineer` | Security | Upstream Sonnet | Anti-cheat, exploit prevention, save encryption, network security |
| `accessibility-specialist` | Accessibility | Upstream Haiku | WCAG compliance, colorblind modes, remapping, text scaling |
| `live-ops-designer` | Live operations | Upstream Sonnet | Seasons, events, battle passes, retention, live economy |
| `community-manager` | Community | Upstream Haiku | Patch notes, player feedback, crisis comms, community health |

## Engine-Specific Agents (use the set matching your engine)

### Engine Leads

| Agent | Engine | Upstream Tier | When to Use |
| ---- | ---- | ---- | ---- |
| `unreal-specialist` | Unreal Engine 5 | Upstream Sonnet | Blueprint vs C++, GAS overview, UE subsystems, Unreal optimization |
| `unity-specialist` | Unity | Upstream Sonnet | MonoBehaviour vs DOTS, Addressables, URP/HDRP, Unity optimization |
| `godot-specialist` | Godot 4 | Upstream Sonnet | GDScript patterns, node/scene architecture, signals, Godot optimization |

### Unreal Engine Sub-Specialists

| Agent | Subsystem | Model | When to Use |
| ---- | ---- | ---- | ---- |
| `ue-gas-specialist` | Gameplay Ability System | Upstream Sonnet | Abilities, gameplay effects, attribute sets, tags, prediction |
| `ue-blueprint-specialist` | Blueprint Architecture | Upstream Sonnet | BP/C++ boundary, graph standards, naming, BP optimization |
| `ue-replication-specialist` | Networking/Replication | Upstream Sonnet | Property replication, RPCs, prediction, relevancy, bandwidth |
| `ue-umg-specialist` | UMG/CommonUI | Upstream Sonnet | Widget hierarchy, data binding, CommonUI input, UI performance |

### Unity Sub-Specialists

| Agent | Subsystem | Model | When to Use |
| ---- | ---- | ---- | ---- |
| `unity-dots-specialist` | DOTS/ECS | Upstream Sonnet | Entity Component System, Jobs, Burst compiler, hybrid renderer |
| `unity-shader-specialist` | Shaders/VFX | Upstream Sonnet | Shader Graph, VFX Graph, URP/HDRP customization, post-processing |
| `unity-addressables-specialist` | Asset Management | Upstream Sonnet | Addressable groups, async loading, memory, content delivery |
| `unity-ui-specialist` | UI Toolkit/UGUI | Upstream Sonnet | UI Toolkit, UXML/USS, UGUI Canvas, data binding, cross-platform input |

### Godot Sub-Specialists

| Agent | Subsystem | Model | When to Use |
| ---- | ---- | ---- | ---- |
| `godot-gdscript-specialist` | GDScript | Upstream Sonnet | Static typing, design patterns, signals, coroutines, GDScript performance |
| `godot-csharp-specialist` | C# / .NET | Upstream Sonnet | .NET patterns, [Signal] delegates, async, nullable types, type-safe node access |
| `godot-shader-specialist` | Shaders/Rendering | Upstream Sonnet | Godot shading language, visual shaders, particles, post-processing |
| `godot-gdextension-specialist` | GDExtension | Upstream Sonnet | C++/Rust bindings, native performance, custom nodes, build systems |
