#!/usr/bin/env python3
"""Runtime, skill, agent, and docs static checks for the CCGS port."""

from __future__ import annotations

import argparse
import json
import re
import sys
import tomllib
from pathlib import Path


FORBIDDEN_RUNTIME = [
    (".claude/", "runtime dependency on .claude"),
    ("CLAUDE.md", "runtime dependency on CLAUDE.md"),
    ("AskUserQuestion", "raw Claude AskUserQuestion reference"),
]

DUPLICATE_DELEGATION_CONSENT_PATTERNS = (
    (
        re.compile(r"May I spawn[^?\n]{0,120}role agents", re.IGNORECASE),
        "duplicate role-agent spawn consent prompt",
    ),
    (
        re.compile(r"literal delegation consent", re.IGNORECASE),
        "duplicate role-agent spawn consent fallback",
    ),
    (
        re.compile(
            r"ask (?:once|one confirmation)[^.\n]{0,180}"
            r"(?:delegation consent|subagent spawn|role agents)",
            re.IGNORECASE,
        ),
        "duplicate role-agent spawn consent fallback",
    ),
)

UNSUPPORTED_SKILL_FRONTMATTER = {
    "allowed-tools",
    "model",
    "argument-hint",
    "user-invocable",
    "isolation",
}

UNSUPPORTED_AGENT_FIELDS = {
    "tools",
    "disallowedTools",
    "maxTurns",
    "memory",
    "skills",
    "isolation",
    "reasoning_effort",
}

ALLOWLIST_PATH_PARTS = {
    ".codex/lib/",
    ".codex/backups/",
    ".codex/tests/",
    ".codex/manifest/",
    ".codex/docs/MIGRATION.md",
    ".codex/docs/COEXISTENCE.md",
    ".codex/README.md",
    "ATTRIBUTION.md",
    "docs/codex-conversion/",
}

REQUIRED_CORE_SKILLS = {
    "adopt",
    "architecture-decision",
    "architecture-review",
    "art-bible",
    "asset-audit",
    "asset-spec",
    "balance-check",
    "brainstorm",
    "bug-report",
    "bug-triage",
    "changelog",
    "code-review",
    "consistency-check",
    "content-audit",
    "create-architecture",
    "create-control-manifest",
    "create-epics",
    "create-stories",
    "day-one-patch",
    "design-review",
    "design-system",
    "dev-story",
    "estimate",
    "gate-check",
    "handoff",
    "help",
    "hotfix",
    "launch-checklist",
    "localize",
    "map-systems",
    "milestone-review",
    "onboard",
    "patch-notes",
    "perf-profile",
    "playtest-report",
    "project-stage-detect",
    "propagate-design-change",
    "prototype",
    "qa-plan",
    "quick-design",
    "regression-suite",
    "release-checklist",
    "retrospective",
    "reverse-document",
    "resume-from-handoff",
    "review-all-gdds",
    "scope-check",
    "security-audit",
    "setup-engine",
    "skill-improve",
    "skill-test",
    "smoke-check",
    "soak-test",
    "sprint-plan",
    "sprint-status",
    "start",
    "story-done",
    "story-readiness",
    "studio-next",
    "studio-status",
    "team-audio",
    "team-combat",
    "team-level",
    "team-live-ops",
    "team-narrative",
    "team-polish",
    "team-qa",
    "team-release",
    "team-ui",
    "tech-debt",
    "test-evidence-review",
    "test-flakiness",
    "test-helpers",
    "test-setup",
    "ux-design",
    "ux-review",
    "vertical-slice",
}

ALLOWED_PROJECT_LOCAL_SKILLS = {
    "gen-asset",
}

REQUIRED_CLOSEOUT_ROUTING_SKILLS = {
    "architecture-decision",
    "architecture-review",
    "art-bible",
    "asset-spec",
    "brainstorm",
    "code-review",
    "consistency-check",
    "design-system",
    "dev-story",
    "gate-check",
    "help",
    "map-systems",
    "project-stage-detect",
    "quick-design",
    "smoke-check",
    "story-done",
    "story-readiness",
    "team-qa",
    "ux-design",
}

UPSTREAM_NO_BASH_AGENTS = {
    "art-director",
    "audio-director",
    "community-manager",
    "creative-director",
    "economy-designer",
    "game-designer",
    "level-designer",
    "live-ops-designer",
    "narrative-director",
    "sound-designer",
    "systems-designer",
    "ue-blueprint-specialist",
    "ux-designer",
    "world-builder",
    "writer",
}

NO_BASH_INSTRUCTION_PHRASE = (
    "Upstream role disallowed Bash; do not run shell commands in this role. "
    "Ask the parent session for command evidence instead."
)

TASK_LABEL_CORRUPTION_PATTERNS = (
    (re.compile(r"Phase 1: Understand the Codex subagent delegation"), "task heading"),
    (re.compile(r"Codex subagent delegation Estimate:"), "task estimate heading"),
    (re.compile(r"Codex subagent delegation Description"), "task description heading"),
    (re.compile(r"Feature/Codex subagent delegation tracking"), "production-stage task tracking label"),
    (re.compile(r"^\s*[-|]\s*(?:Story / )?Codex subagent delegation\b", re.MULTILINE), "task table label"),
    (re.compile(r"^\s*-\s+Codex subagent delegation:\s+(?:Designing|\[|Systems decomposition)", re.MULTILINE), "session-state task label"),
)

CLOSEOUT_MARKERS = (
    "Verdict: **COMPLETE**",
    "Verdict: COMPLETE",
    "**Verdict: COMPLETE**",
    "## Recommended Next Steps",
)

CLOSEOUT_REQUIRED_PHRASES = (
    "Session Worklist",
    "production/session-state/active.md",
    "completed work",
    "owed verification",
    "numbered next-action prompt",
    "Next action:",
    "1. (Recommended)",
    "(Recommended)",
)

CLOSEOUT_FORBIDDEN_PHRASES = (
    "one recommended next action",
    "numbered choice set",
)

INTERNAL_READONLY_CLOSEOUT_PATTERNS = (
    (re.compile(r"\bself[- ]check\b", re.IGNORECASE), "Self-Check"),
    (re.compile(r"\bregistry (?:candidate )?scan\b", re.IGNORECASE), "registry scan"),
    (re.compile(r"\bcandidate discovery\b", re.IGNORECASE), "candidate discovery"),
    (re.compile(r"\bregistry candidate discovery\b", re.IGNORECASE), "registry candidate discovery"),
    (re.compile(r"\bread ?backs?\b", re.IGNORECASE), "readback"),
    (re.compile(r"\bread back\b", re.IGNORECASE), "readback"),
    (re.compile(r"\bcontext gathering\b", re.IGNORECASE), "context gathering"),
    (re.compile(r"\bvalidation summar(?:y|ies)\b", re.IGNORECASE), "validation summary"),
)
CLOSEOUT_MENU_CONTEXT_RE = re.compile(
    r"\b(?:Next action|Recommended Next Steps|closeout|closing widget|what next|next steps)\b",
    re.IGNORECASE,
)
CLOSEOUT_OPTION_LINE_RE = re.compile(
    r"^\s*(?:[-*]\s*)?(?:\d+[.)]|\[[A-Z]\]|[A-Z][.)]|`?\[_\]`?)\s+"
)

ACTIVE_STATE_PATH = "production/session-state/active.md"
ACTIVE_STATE_WRITE_VERBS = r"(?:create|update|append|overwrite|write)"
ACTIVE_STATE_CHECKPOINT_REQUIRED_PHRASES = (
    "derived checkpoint",
    'Do not ask a separate "May I write?" for this file',
)
ACTIVE_STATE_NAMED_EXCEPTIONS = {
    "handoff",
    "resume-from-handoff",
}

STARTUP_AGENT_ROSTER_HEADING = "## Available Codex Role Agents"
AGENTS_MD_TARGET_BYTES = 16 * 1024
AGENTS_MD_MAX_BYTES = 20 * 1024
INSTRUCTION_CHAIN_MAX_BYTES = 28 * 1024
COMMON_PATH_RULE_CHAINS = (
    ("src", ("source-code.md",)),
    ("src/gameplay", ("source-code.md", "gameplay-code.md")),
    ("src/core", ("source-code.md", "engine-code.md")),
    ("src/ai", ("source-code.md", "ai-code.md")),
    ("src/networking", ("source-code.md", "network-code.md")),
    ("src/ui", ("source-code.md", "ui-code.md")),
    ("design/gdd", ("design-directory.md", "design-docs.md")),
    ("design/narrative", ("design-directory.md", "narrative.md")),
    ("docs", ("docs-directory.md",)),
    ("assets/data", ("data-files.md",)),
    ("assets/shaders", ("shader-code.md",)),
    ("tests", ("test-standards.md",)),
    ("tools", ("tool-code.md",)),
    ("prototypes", ("prototype-code.md",)),
)


def emit(check: str, root: Path, errors: list[str], warnings: list[str] | None = None) -> int:
    warnings = warnings or []
    status = "pass" if not errors else "fail"
    print(json.dumps({"check": check, "root": str(root), "status": status, "errors": errors, "warnings": warnings}, indent=2, sort_keys=True))
    if errors:
        print(f"{check}: {len(errors)} validation failure(s)", file=sys.stderr)
        return 1
    print(f"{check}: pass")
    return 0


def is_allowlisted(path: Path) -> bool:
    normalized = path.as_posix()
    return any(part in normalized or normalized == part for part in ALLOWLIST_PATH_PARTS)


def frontmatter(text: str) -> dict[str, str]:
    if not text.startswith("---\n"):
        return {}
    parts = text.split("---", 2)
    if len(parts) < 3:
        return {}
    data: dict[str, str] = {}
    for line in parts[1].splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if ":" in line:
            key, value = line.split(":", 1)
            data[key.strip()] = value.strip()
    return data


def runtime_files(root: Path) -> list[Path]:
    candidates: list[Path] = []
    for rel in ("AGENTS.md", ".agents", ".codex"):
        path = root / rel
        if path.is_file():
            candidates.append(path)
        elif path.is_dir():
            candidates.extend(p for p in path.rglob("*") if p.is_file())
    candidates.extend(p for p in root.glob("**/AGENTS.md") if ".git" not in p.parts)
    return sorted(set(candidates))


def validate_forbidden_references(root: Path) -> list[str]:
    errors: list[str] = []
    for path in runtime_files(root):
        rel = path.relative_to(root)
        if is_allowlisted(rel):
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for needle, label in FORBIDDEN_RUNTIME:
            if needle in text:
                errors.append(f"{rel}: {label}")
        errors.extend(validate_duplicate_delegation_consent_text(rel, text))
        if re.search(r"(?m)(^|\\s)/(start|brainstorm|gate-check|dev-story|prototype|vertical-slice)\\b", text):
            errors.append(f"{rel}: bare custom slash-command reference")
    return errors


def validate_duplicate_delegation_consent_text(rel: Path, text: str) -> list[str]:
    errors: list[str] = []
    for pattern, label in DUPLICATE_DELEGATION_CONSENT_PATTERNS:
        if pattern.search(text):
            errors.append(
                f"{rel}: {label}; skill invocation already authorizes declared role-agent spawns"
            )
    return errors


def validate_internal_readonly_closeout_options(rel: Path, text: str) -> list[str]:
    errors: list[str] = []
    context_lines_remaining = 0
    for line_number, line in enumerate(text.splitlines(), start=1):
        if CLOSEOUT_MENU_CONTEXT_RE.search(line):
            context_lines_remaining = 18

        matched_label = None
        for pattern, label in INTERNAL_READONLY_CLOSEOUT_PATTERNS:
            if pattern.search(line):
                matched_label = label
                break

        if matched_label:
            option_line = bool(CLOSEOUT_OPTION_LINE_RE.search(line))
            inline_options = "options:" in line.lower()
            if context_lines_remaining and (option_line or inline_options):
                errors.append(
                    f"{rel}:{line_number}: closeout/next-action menu offers internal read-only phase "
                    f"{matched_label!r}; run read-only workflow phases automatically until a mutation prompt, "
                    "design decision, blocker, or true stop point"
                )

        if context_lines_remaining:
            context_lines_remaining -= 1
    return errors


def validate_task_label_corruption(rel: Path, text: str) -> list[str]:
    errors: list[str] = []
    for pattern, label in TASK_LABEL_CORRUPTION_PATTERNS:
        for match in pattern.finditer(text):
            line_number = text.count("\n", 0, match.start()) + 1
            errors.append(
                f"{rel}:{line_number}: mechanical task-label corruption remains ({label}); "
                "use Task, Task Estimate, Story / Task, or Current task wording outside real delegation instructions"
            )
    return errors


def validate_instruction_budgets(root: Path) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    agents_md = root / "AGENTS.md"
    if not agents_md.exists():
        errors.append("AGENTS.md: missing startup instruction file")
        return errors, warnings

    root_size = len(agents_md.read_bytes())
    if root_size > AGENTS_MD_MAX_BYTES:
        errors.append(f"AGENTS.md: {root_size} bytes exceeds {AGENTS_MD_MAX_BYTES} byte startup guidance budget")
    elif root_size > AGENTS_MD_TARGET_BYTES:
        warnings.append(f"AGENTS.md: {root_size} bytes exceeds {AGENTS_MD_TARGET_BYTES} byte optimization target")

    rule_root = root / ".codex" / "instructions" / "path-rules"
    agents_text = agents_md.read_text(encoding="utf-8")
    for rel, rule_names in COMMON_PATH_RULE_CHAINS:
        chain = [agents_md]
        missing_rules: list[str] = []
        for rule_name in rule_names:
            rule_path = rule_root / rule_name
            if not rule_path.exists():
                missing_rules.append(rule_name)
            else:
                chain.append(rule_path)
            if rule_name not in agents_text:
                errors.append(f"AGENTS.md: missing path-rule router entry for {rule_name}")
        if missing_rules:
            errors.append(f"path-rule chain {rel}: missing {', '.join(missing_rules)}")
            continue
        size = sum(len(path.read_bytes()) for path in chain)
        if size > INSTRUCTION_CHAIN_MAX_BYTES:
            labels = " + ".join(str(path.relative_to(root)) for path in chain)
            errors.append(
                f"path-rule chain {rel}: {size} bytes exceeds {INSTRUCTION_CHAIN_MAX_BYTES} byte budget ({labels})"
            )
    return errors, warnings


def validate_active_state_checkpoint_text(rel: Path, text: str, exempt: bool = False) -> list[str]:
    if exempt or ACTIVE_STATE_PATH not in text:
        return []

    errors: list[str] = []
    normalized_text = re.sub(r"\s+", " ", text)
    normalized_lower = normalized_text.lower()
    normalized_path = re.escape(ACTIVE_STATE_PATH)
    write_verb_pattern = (
        rf"(?<!does not )(?<!do not )(?<!must not )\b{ACTIVE_STATE_WRITE_VERBS}\b"
        rf"(?!\s+(?:is|was|complete))"
    )
    active_write_pattern = (
        rf"(?is){write_verb_pattern}[^.!?;]{{0,180}}`?{normalized_path}`?"
        rf"|`?{normalized_path}`?[^.!?;]{{0,180}}{write_verb_pattern}"
    )
    if re.search(active_write_pattern, normalized_text):
        missing_active_phrases = [
            phrase
            for phrase in ACTIVE_STATE_CHECKPOINT_REQUIRED_PHRASES
            if phrase.lower() not in normalized_lower
        ]
        if missing_active_phrases:
            errors.append(
                f"{rel}: active.md checkpoint write missing no-extra-approval language: "
                + ", ".join(missing_active_phrases)
            )

    prompt_text = normalized_text
    for phrase in ACTIVE_STATE_CHECKPOINT_REQUIRED_PHRASES:
        prompt_text = re.sub(re.escape(phrase), "", prompt_text, flags=re.IGNORECASE)
    active_prompt_pattern = (
        rf"(?is)May I (?:write|update)\b(?:\s+[\w/-]+){{0,10}}\s+"
        rf"(?:to\s+|at\s+)?`?(?:{normalized_path}|active\.md)`?[^?]*\?"
    )
    if re.search(active_prompt_pattern, prompt_text):
        errors.append(f"{rel}: active.md checkpoint must not request a separate May I write/update prompt")
    return errors


def validate_skills(root: Path, require_present: bool = False) -> list[str]:
    errors: list[str] = []
    skill_root = root / ".agents" / "skills"
    if not skill_root.exists():
        return ["missing .agents/skills"] if require_present else []
    skill_files = sorted(skill_root.glob("*/SKILL.md"))
    skill_names = {p.parent.name for p in skill_files}
    missing_core = sorted(REQUIRED_CORE_SKILLS - skill_names)
    if missing_core:
        errors.append(f".agents/skills: missing required core skills: {', '.join(missing_core)}")
    unexpected = sorted(skill_names - REQUIRED_CORE_SKILLS - ALLOWED_PROJECT_LOCAL_SKILLS)
    if unexpected:
        errors.append(f".agents/skills: unexpected project-local skills: {', '.join(unexpected)}")

    for skill_file in skill_files:
        rel = skill_file.relative_to(root)
        text = skill_file.read_text(encoding="utf-8")
        meta = frontmatter(text)
        if not meta:
            errors.append(f"{rel}: missing frontmatter")
            continue
        folder = skill_file.parent.name
        if meta.get("name") != folder:
            errors.append(f"{rel}: frontmatter name must equal folder name {folder}")
        if not meta.get("description"):
            errors.append(f"{rel}: missing description")
        unsupported = sorted(UNSUPPORTED_SKILL_FRONTMATTER & meta.keys())
        if unsupported:
            errors.append(f"{rel}: unsupported skill frontmatter {', '.join(unsupported)}")
        if "AskUserQuestion" in text:
            errors.append(f"{rel}: raw AskUserQuestion reference remains")
        if ".claude/" in text or "CLAUDE.md" in text:
            errors.append(f"{rel}: runtime Claude path reference remains")
        errors.extend(validate_duplicate_delegation_consent_text(rel, text))
        errors.extend(validate_internal_readonly_closeout_options(rel, text))
        errors.extend(validate_task_label_corruption(rel, text))
        if skill_names:
            slash_pattern = r"(?m)(^|\\s)/(" + "|".join(re.escape(name) for name in sorted(skill_names, key=len, reverse=True)) + r")\\b"
            if re.search(slash_pattern, text):
                errors.append(f"{rel}: bare custom slash-command reference remains")
        if re.search(r"\\bTask\\b", text):
            errors.append(f"{rel}: raw Claude Task reference remains")
        if skill_file.parent.name in {"prototype", "vertical-slice"} and "worktree" not in text.lower():
            errors.append(f"{rel}: missing explicit worktree guidance")
        if skill_file.parent.name in {"architecture-review", "gate-check", "review-all-gdds"} and "high-reasoning" not in text:
            errors.append(f"{rel}: missing high-reasoning guidance")
        if folder in REQUIRED_CLOSEOUT_ROUTING_SKILLS and any(marker in text for marker in CLOSEOUT_MARKERS):
            missing_closeout = [phrase for phrase in CLOSEOUT_REQUIRED_PHRASES if phrase not in text]
            if missing_closeout:
                errors.append(
                    f"{rel}: completion closeout missing worklist-backed routing language: "
                    + ", ".join(missing_closeout)
                )
            forbidden_closeout = [phrase for phrase in CLOSEOUT_FORBIDDEN_PHRASES if phrase in text]
            if forbidden_closeout:
                errors.append(
                    f"{rel}: completion closeout still permits old non-numeric routing language: "
                    + ", ".join(forbidden_closeout)
                )
        errors.extend(validate_active_state_checkpoint_text(rel, text, folder in ACTIVE_STATE_NAMED_EXCEPTIONS))
    return errors


def validate_agent_startup_roster(root: Path, agent_names: set[str]) -> list[str]:
    errors: list[str] = []
    agents_md = root / "AGENTS.md"
    if not agents_md.exists():
        return ["AGENTS.md: missing startup instruction file"]

    text = agents_md.read_text(encoding="utf-8")
    size = len(text.encode("utf-8"))
    if size > AGENTS_MD_MAX_BYTES:
        errors.append(f"AGENTS.md: {size} bytes exceeds {AGENTS_MD_MAX_BYTES} byte startup guidance budget")

    if STARTUP_AGENT_ROSTER_HEADING not in text:
        return errors + [f"AGENTS.md: missing {STARTUP_AGENT_ROSTER_HEADING!r} section"]

    start = text.index(STARTUP_AGENT_ROSTER_HEADING)
    next_heading = text.find("\n## ", start + len(STARTUP_AGENT_ROSTER_HEADING))
    roster = text[start:] if next_heading == -1 else text[start:next_heading]

    missing = sorted(name for name in agent_names if f"`{name}`" not in roster)
    if missing:
        errors.append(f"AGENTS.md: startup role roster missing agents: {', '.join(missing)}")

    if len(agent_names) != 49 and "49 coordinated Codex subagents" in text:
        errors.append("AGENTS.md: stale 49-agent claim remains for project-local agent set")

    return errors


def validate_agents(root: Path, require_present: bool = False) -> list[str]:
    errors: list[str] = []
    agent_root = root / ".codex" / "agents"
    if not agent_root.exists():
        return ["missing .codex/agents"] if require_present else []
    agent_files = sorted(agent_root.glob("*.toml"))
    if len(agent_files) != 49:
        errors.append(f".codex/agents: expected 49 TOML files, found {len(agent_files)}")

    agent_names: set[str] = set()
    model_counts: dict[tuple[str, str], int] = {}
    memory_bound_agents: set[str] = set()
    for agent_file in agent_files:
        rel = agent_file.relative_to(root)
        try:
            data = tomllib.loads(agent_file.read_text(encoding="utf-8"))
        except tomllib.TOMLDecodeError as exc:
            errors.append(f"{rel}: invalid TOML: {exc}")
            continue
        unsupported = sorted(UNSUPPORTED_AGENT_FIELDS & data.keys())
        if unsupported:
            errors.append(f"{rel}: unsupported agent fields {', '.join(unsupported)}")
        name = data.get("name")
        if name != agent_file.stem:
            errors.append(f"{rel}: name must equal filename stem {agent_file.stem}")
        else:
            agent_names.add(str(name))
        for field in ("description", "developer_instructions"):
            if not data.get(field):
                errors.append(f"{rel}: missing {field}")
        if "model_reasoning_effort" not in data:
            errors.append(f"{rel}: missing model_reasoning_effort")
        model_key = (str(data.get("model", "")), str(data.get("model_reasoning_effort", "")))
        model_counts[model_key] = model_counts.get(model_key, 0) + 1
        instructions = str(data.get("developer_instructions", ""))
        errors.extend(validate_active_state_checkpoint_text(rel, instructions))
        if "Ported Claude memory scope:" in instructions:
            memory_path = f".codex/agent-memory/{agent_file.stem}/MEMORY.md"
            if memory_path not in instructions:
                errors.append(f"{rel}: memory-scoped agent does not reference {memory_path}")
            memory_bound_agents.add(agent_file.stem)
        if agent_file.stem in UPSTREAM_NO_BASH_AGENTS and NO_BASH_INSTRUCTION_PHRASE not in instructions:
            errors.append(
                f"{rel}: upstream disallowed Bash but Codex instructions lack the required no-Bash role boundary"
            )
        if "~/.codex/memories" in instructions:
            errors.append(f"{rel}: generated agent must not write global Codex memories")

    memory_files = sorted((root / ".codex" / "agent-memory").glob("*/MEMORY.md"))
    if len(memory_files) != 17:
        errors.append(f".codex/agent-memory: expected 17 MEMORY.md files, found {len(memory_files)}")
    memory_file_agents = {p.parent.name for p in memory_files}
    if memory_bound_agents != memory_file_agents:
        missing = sorted(memory_file_agents - memory_bound_agents)
        extra = sorted(memory_bound_agents - memory_file_agents)
        if missing:
            errors.append(f".codex/agent-memory: memory files not bound by agents: {', '.join(missing)}")
        if extra:
            errors.append(f".codex/agents: memory-bound agents without memory file: {', '.join(extra)}")
    errors.extend(validate_agent_startup_roster(root, agent_names))
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    parser.add_argument("--kind", choices=["runtime", "skills", "agents", "docs"], default="runtime")
    parser.add_argument("--require-present", action="store_true")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    errors: list[str] = []
    warnings: list[str] = []
    if args.kind in {"runtime", "docs"}:
        errors.extend(validate_forbidden_references(root))
        budget_errors, budget_warnings = validate_instruction_budgets(root)
        errors.extend(budget_errors)
        warnings.extend(budget_warnings)
    if args.kind == "skills":
        errors.extend(validate_skills(root, args.require_present))
    if args.kind == "agents":
        errors.extend(validate_agents(root, args.require_present))
    return emit(args.kind, root, errors, warnings)


if __name__ == "__main__":
    raise SystemExit(main())
