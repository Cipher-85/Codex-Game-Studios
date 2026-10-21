# CCGS Skill Testing Framework

Quality assurance infrastructure for the **Codex Game Studios** framework.
Tests the skills and agents themselves — not any game built with them.

This is a package-managed set of behavioral specifications. Executing native
behavioral tests is separate from ordinary game development, but the shipped
files are part of CCGS manifest and installation validation. Keep them in a
managed installation; deleting the folder makes those package checks fail.

The current tree has 74 skill specs and 49 role specs. The 76 packaged skills
include `studio-status` and deprecated `studio-next`, which have no separate
behavioral specs. Spec presence does not mean a native test has run. See
[validation and owed native evidence](../.codex/docs/VALIDATION.md#native-acceptance-for-the-selective-update).

---

## What's in here

```
CCGS Skill Testing Framework/
├── README.md              ← you are here
├── AGENTS.md              ← tells Codex how to use this framework
├── catalog.yaml           ← behavioral spec registry and recorded test coverage
├── quality-rubric.md      ← category-specific pass/fail metrics for $skill-test category
│
├── skills/                ← behavioral spec files for skills (one per skill)
│   ├── gate/              ← gate category specs
│   ├── review/            ← review category specs
│   ├── authoring/         ← authoring category specs
│   ├── readiness/         ← readiness category specs
│   ├── pipeline/          ← pipeline category specs
│   ├── analysis/          ← analysis category specs
│   ├── team/              ← team category specs
│   ├── sprint/            ← sprint category specs
│   └── utility/           ← utility category specs
│
├── agents/                ← behavioral spec files for agents (one per agent)
│   ├── directors/         ← creative-director, technical-director, producer, art-director
│   ├── leads/             ← lead-programmer, narrative-director, audio-director, etc.
│   ├── specialists/       ← engine/code/shader/UI specialists
│   ├── engine/            ← godot/, unity/ and unreal/ specialists
│   ├── operations/        ← production and operational roles
│   └── qa/                ← QA specialists
│
├── templates/             ← spec file templates for writing new specs
│   ├── skill-test-spec.md ← template for skill behavioral specs
│   └── agent-test-spec.md ← template for agent behavioral specs
│
└── results/               ← test run outputs (written by $skill-test spec, gitignored)
```

---

## Model Tier Labels

Some inherited specs use upstream Claude tier names such as Opus, Sonnet, and
Haiku. In this Codex port they are historical tier labels only. Runtime agent
configuration lives in `.codex/agents/*.toml` and maps those tiers to Codex
models; reasoning effort is left to the active runtime unless explicitly configured.

## How to use it

All testing is driven by two skills already in the framework:

### Check structural compliance

```
$skill-test static [skill-name]     # Check one skill (7 checks)
$skill-test static all              # Check all packaged skills
```

### Run a behavioral spec test

```
$skill-test spec gate-check         # Evaluate a skill against its written spec
$skill-test spec design-review
```

### Check against category rubric

```
$skill-test category gate-check     # Evaluate one skill against its category metrics
$skill-test category all            # Run rubric checks across all categorized skills
```

### See full coverage picture

```
$skill-test audit                   # Skills + agents: has-spec, last tested, result
```

### Improve a failing skill

```
$skill-improve gate-check           # Test → diagnose → propose fix → retest loop
```

---

## Skill categories

| Category | Skills | Key metrics |
|----------|--------|-------------|
| `gate` | gate-check | Review mode read, full/lean/solo director panel, no auto-advance |
| `review` | design-review, architecture-review, review-all-gdds | Tier-aware requirements, evidence, correct verdicts |
| `authoring` | design-system, quick-design, art-bible, create-architecture, … | Section-by-section May-I-write, skeleton-first |
| `readiness` | story-readiness, story-done | Blockers surfaced, director gate in full mode |
| `pipeline` | create-epics, create-stories, dev-story, map-systems, … | Upstream dependency check, handoff path clear |
| `analysis` | consistency-check, balance-check, code-review, tech-debt, … | Read-only report, verdict keyword, no writes |
| `team` | team-combat, team-narrative, team-audio, … | All required agents spawned, blocked surfaced |
| `sprint` | sprint-plan, sprint-status, milestone-review, … | Reads sprint data, status keywords present |
| `utility` | start, adopt, hotfix, localize, setup-engine, … | Passes static checks |

---

## Role specifications

Directories organize test cases; they do not select a model or establish role
activation. `.codex/agents/*.toml` is authoritative for all 49 role profiles.
Inherited tier labels are historical. Native results need actual role metadata
and matching instructions, as described in the validation contract.

---

## Updating the catalog

`catalog.yaml` tracks test coverage for every skill and agent. After running a test:

- `$skill-test spec [name]` will offer to update `last_spec` and `last_spec_result`
- `$skill-test category [name]` will offer to update `last_category` and `last_category_result`
- `last_static` and `last_static_result` are updated manually or via `$skill-improve`

---

## Writing a new spec

1. Find the spec template at `templates/skill-test-spec.md`
2. Copy it to `skills/[category]/[skill-name].md`
3. Update the `spec:` field in `catalog.yaml` to point to the new file
4. Run `$skill-test spec [skill-name]` to validate it

---

## Package lifecycle

The upstream v1.2.0 rename to `studio-tests/` is deferred. This package keeps
`CCGS Skill Testing Framework/` and its recorded ownership paths; see
[the adoption matrix](../UPGRADING.md#selective-v120-adoption).

Use the package installer/uninstaller under its normal approval contract for
managed assets. Manual removal leaves missing manifest paths and does not turn
an unrun behavioral test into an optional passing check. Project-specific tests
can live outside these owned files.
