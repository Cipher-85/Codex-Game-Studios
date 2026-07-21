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

ROLE_DELEGATION_EVIDENCE_PHRASES = (
    "agent_type: default",
    "agent_role: null",
    'fork_turns: "none"',
    "A task name, agent path, nickname",
    "do not simulate the specialist verdict",
)

PLAYTEST_FOCUS_CONTRACT = {
    "AGENTS.md": (
        "user-owned playtest",
        "Playtest focus:",
        "hypothesis",
        "setup/build",
        "2-4 observation",
        "verdict/evidence",
    ),
    ".codex/docs/session-continuity.md": (
        "user-owned playtest",
        "Playtest focus:",
        "hypothesis",
        "setup/build",
        "2-4 observation",
        "verdict/evidence",
        "Session Worklist",
    ),
    ".agents/skills/playtest-report/SKILL.md": (
        "user-owned playtest",
        "Playtest focus:",
        "hypothesis",
        "setup/build",
        "2-4 observation",
        "verdict/evidence",
    ),
}

BUG_LIFECYCLE_REQUIRED_PHRASES = {
    ".agents/skills/bug-report/SKILL.md": (
        "treat verification, closure, stale triage",
        "one deterministic bug lifecycle operation",
        "Do not stop after VERIFIED FIXED to offer `$bug-report close [BUG-ID]` as the",
        "refresh stale triage metadata under the same approval",
        "zero-open-bugs refresh",
        "derived checkpoint",
        'Do not ask a separate "May I write?" for `production/session-state/active.md`',
        "Do not bundle and stop for user decision if triage would require assigning",
    ),
    ".agents/skills/bug-triage/SKILL.md": (
        "zero-open-bugs closure refresh",
        "Treat it as metadata cleanup",
        "non-blocking follow-up",
        "Exception for bundled bug lifecycle cleanup",
        "deterministic metadata cleanup",
        "It must be explicitly marked non-blocking if it cannot be completed safely",
        "Do not bundle if the triage work would require assigning priorities",
    ),
}

BUG_LIFECYCLE_FORBIDDEN_PHRASES = (
    (
        ".agents/skills/bug-report/SKILL.md",
        'Bug [ID] is referenced in the triage report. Run `$bug-triage` to refresh the open bug count.',
        "bug close still defers deterministic triage refresh to a separate prompt",
    ),
    (
        ".agents/skills/bug-report/SKILL.md",
        "Run `$bug-report close [BUG-ID]` — write the closure record and update status",
        "verified-fixed still forces a separate close step",
    ),
    (
        ".agents/skills/bug-report/SKILL.md",
        "Run `$bug-triage` to refresh the open bug count and remove it from the active list",
        "verified-fixed still forces a separate triage cleanup step",
    ),
)

HANDOFF_REVIEW_REQUIRED_PHRASES = {
    ".agents/skills/handoff/SKILL.md": (
        "## Round 1",
        "## Round 2",
        "`STANDARD`",
        "`ADVERSARIAL`",
        "Foundation ADR cluster closure",
        "pure design/process-document",
        "self-review is sufficient and the native cross-check is skipped",
        "Mixed code-and-document changes are not exempt",
        "distinct native Codex review pass",
        "current Codex session",
        "`HIGH`, `MEDIUM`, or `LOW`",
        "`CLEAN`",
        "`path:line`",
        "If uncertain whether the work meets a major trigger, use `STANDARD`",
        "quoted verbatim",
        "stop before Phase 1",
        "second native cross-check",
        "`HIGH` finding",
        "cross-cutting executable behavior",
        "Trivial and confidently intent-preserving only",
        "Any non-trivial fix",
        "Do not run a third pass",
        "three native review passes",
        "fourth native review pass",
        "active reported context percentage",
        "review audit trail",
        "every finding",
        "Only then proceed to Phase 1",
    ),
    "AGENTS.md": (
        "files already created or materially modified during the session",
        "intent-preserving review fixes",
        "active Codex session",
        "Round-two non-trivial findings",
        "external data-egress approval",
        "new intent, architecture, game-feel, balance, or scope decisions",
    ),
}

HANDOFF_AUTHORIZATION_REQUIRED_PHRASES = {
    ".agents/skills/handoff/SKILL.md": (
        "equally explicit instruction to commit and push this handoff",
        "Generic requests to pause, stop, checkpoint",
        "they are not commit or push authority",
    ),
    "AGENTS.md": (
        "equally explicit instruction to commit and push the handoff",
        "Generic pause/stop wording does not",
    ),
}

HANDOFF_CAPACITY_REQUIRED_PHRASES = (
    "## Context Capacity Gate",
    "active reported context percentage",
    "estimated additional percentage cost",
    "hardcoded percentage threshold",
    "If the active percentage is unavailable",
)

HANDOFF_SCOPE_REQUIRED_PHRASES = (
    "production/session-logs/session-baseline.json",
    "starting HEAD",
    "git merge-base --is-ancestor <starting-head> HEAD",
    "git diff --name-only <starting-head>..HEAD",
    "git diff --cached --name-only",
    "git ls-files --others --exclude-standard",
    "files it records as touched or in progress",
    "filesystem file count",
    "tracked count",
    "staged count",
    "git check-ignore -v -- <path>",
    "not an independent reviewer",
)

HANDOFF_INDEX_REQUIRED_PHRASES = (
    "production/resume-index.md",
    "derived, disposable accelerator",
    "Generated date and source HEAD",
    "SHA-256 content hash",
    "Last reported or verified boot/playtest with provenance",
    "Owed verification",
    "two alternative lanes",
    "Blockers/gates",
    "at most 10 KB",
)

HANDOFF_GIT_CAPABILITY_REQUIRED_PHRASES = (
    "## Git And Remote Capability Gate",
    "Before Phase 0",
    "git rev-parse --absolute-git-dir",
    "test -w '<absolute-git-dir>'",
    "using the user's active session permissions",
    "repeat that exact check once",
    "`sandbox_permissions` set to `\"require_escalated\"`",
    "git ls-remote --heads",
    "An exit code of zero with no matching ref",
    "active context explicitly reports network access as unavailable",
    "`prefix_rule` set to `[\"git\", \"ls-remote\"]`",
    "Could not resolve host",
    "retry that same command once",
    "Never display embedded credentials",
    "selects the complete `game_studios` profile but does not override",
    "must not instruct the user to switch `/permissions` modes",
)

HANDOFF_PHASE3_GIT_WRITE_REQUIRED_PHRASES = (
    "stage only the relevant paths by name",
    "using the user's active session permissions",
    "repeat the exact `git add` command once",
    "`prefix_rule` set to `[\"git\", \"add\"]`",
    "repeat that exact `git commit` command once",
    "`prefix_rule` set to `[\"git\", \"commit\"]`",
    "Do not broaden the path set",
)

HANDOFF_PHASE4_PUSH_REQUIRED_PHRASES = (
    "Treat the resolved push URL, current branch/upstream, and explicit `$handoff` invocation",
    "Do not require `gh auth status`, `gh api user`, or `gh repo view` as push preconditions",
    "Git and GitHub CLI may use different credentials",
    "Do not halt before the authorized push solely because a GitHub CLI check",
    "name the verified push URL",
    "Do not claim an authenticated account or repository permission unless it was actually verified",
    "The actual `git push` is the authoritative network and Git-authentication check",
    "report Git's exact error",
    "active context explicitly reports network access as unavailable",
    "`sandbox_permissions` set to `\"require_escalated\"`",
    "`prefix_rule` set to `[\"git\", \"push\"]`",
    "repeat the exact push command once",
    "Could not resolve host",
    "retry that exact push command once",
    "name resolution failed before the remote could be contacted",
    "Do not retry authentication, authorization",
    "Do not instruct the user to change the whole session's permission mode",
)

HANDOFF_PHASE4_PUSH_FORBIDDEN_PHRASES = (
    (
        "Continue only when the authenticated account",
        "mandatory GitHub CLI identity gate blocks the actual authorized Git push",
    ),
    (
        "Otherwise halt and report the exact failed check",
        "mandatory GitHub CLI precheck failure still halts before Git push",
    ),
)

HANDOFF_REVIEW_FORBIDDEN_PATTERNS = (
    (
        re.compile(r"(?im)^\s*(?:\$\s*)?codex\s+(?:review|exec)\b"),
        "executable nested Codex CLI review command",
    ),
    (
        re.compile(r"(?im)^\s*(?:\$\s*)?node\s+[^\n]*codex-companion(?:\.mjs)?\b"),
        "executable codex-companion command",
    ),
    (
        re.compile(
            r"(?im)^\s*(?:export\s+)?[A-Z_][A-Z0-9_]*\s*=\s*[^\n]*"
            r"codex-companion(?:\.mjs)?\b"
        ),
        "executable codex-companion path assignment",
    ),
    (
        re.compile(
            r"(?i)(?<!never )(?<!do not )(?<!must not )"
            r"\b(?:call|run|use|invoke|launch|execute)\s+`?codex\s+(?:review|exec)\b"
        ),
        "instruction to launch a nested Codex CLI reviewer",
    ),
    (
        re.compile(
            r"(?i)(?<!never )(?<!do not )(?<!must not )"
            r"\b(?:call|run|use|invoke|launch|execute)\b[^.\n]{0,100}"
            r"\bcodex-companion(?:\.mjs)?\b"
        ),
        "instruction to launch codex-companion",
    ),
    (
        re.compile(
            r"(?i)(?<!never )(?<!do not )(?<!must not )"
            r"\b(?:call|run|use|invoke|launch|execute)\b[^.\n]{0,100}"
            r"\bClaude companion plugin\b"
        ),
        "instruction to launch the Claude companion plugin",
    ),
    (
        re.compile(
            r"(?i)(?<!never )(?<!do not )(?<!must not )"
            r"\b(?:call|use|invoke|launch)\b[^.\n]{0,120}"
            r"\banother model service\b"
        ),
        "instruction to launch another model service",
    ),
    (
        re.compile(r"(?i)\b(?:sandbox_permissions|require_escalated)\b"),
        "external-review escalation token",
    ),
    (
        re.compile(
            r"(?i)\b(?:request|seek)\s+(?:user\s+)?approval\b"
            r"[^.\n]{0,120}\bexternal review\b"
        ),
        "external-review approval instruction",
    ),
    (
        re.compile(r"(?i)\bescalat(?:e|ed|ion)\b[^.\n]{0,120}\bexternal review\b"),
        "escalated external-review instruction",
    ),
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

RESUME_SKILL_PATH = Path(".agents/skills/resume-from-handoff/SKILL.md")
RESUME_REQUIRED_PHRASES = (
    "A focus argument biases ranking; it does not select a lane.",
    "Never start an unselected lane.",
    "recommendation as the first option",
    "wait for the user to reply `1`",
    "Resume selection authorizes entering only the selected workflow",
    "FIRST verification cannot be waived by choosing another lane",
    "Follow-up fork",
    "request_user_input",
    "Playable/Slice State Source",
    "production/stage.txt",
    ".codex/docs/workflow-catalog.yaml",
    "production/session-state/active.md",
)

RESUME_BOUNDED_REQUIRED_PHRASES = (
    "$resume-from-handoff deep [focus]",
    "bounded current section",
    "at most 200 lines or 32 KiB",
    "Default resume must not read the entire slice source",
    "Missing or stale index state never activates deep mode automatically",
    "production/resume-index.md",
    "Mark an oversized index `oversized`",
    "SHA-256 content hash",
    "Compute the hash locally without loading the whole source into model context",
    "stale-hash",
)

RESUME_READBACK_REQUIRED_PHRASES = (
    "read `production/session-state/active.md` back in full",
    "## Source Freshness",
    "## Owed Before Starting",
    "recommended `## Session Worklist` lane",
    "Do not claim the session cache was updated until this readback passes",
)

RESUME_PRECEDENCE_REQUIRED_PHRASES = (
    "Use this source precedence",
    "durable narrative, decisions, blockers",
    "for current stage",
    "for story status",
    "fresh bounded current section",
    "derived accelerator",
    "lowest-priority same-session cache",
    "Surface conflicts; never silently normalize them",
)

GEN_ASSET_SKILL_PATH = Path(".agents/skills/gen-asset/SKILL.md")
GEN_ASSET_REQUIRED_PHRASES = (
    "Invoke the built-in `image_gen` tool directly",
    "If built-in image generation is unavailable, stop and report it",
    "returned output path",
    "created after the call began",
    "tmp/gen-asset",
    "at most 2 retries",
    "contact sheet",
    "exact final paths",
    "overwrite warnings",
    "adapter command",
    "Only contact-sheet approval authorizes",
    "regenerate only rejected candidates",
)

GEN_ASSET_ACTIVE_PROFILE_FIELDS = {
    "Taxonomy": ("taxonomy",),
    "Placement adapter": ("placement adapter",),
    "target_dir": ("target_dir", "target dir"),
    "Prompt boilerplate": ("prompt boilerplate", "boilerplate"),
    "Style/palette rules": ("style/palette", "palette"),
    "Background + chroma recipe": ("background + chroma", "background:", "chroma"),
    "Acceptance criteria": ("acceptance criteria",),
    "Corrective re-prompt": ("corrective re-prompt",),
    "Naming": ("naming",),
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


def ported_metadata(text: str) -> tuple[dict[str, str], bool]:
    match = re.search(r"(?ms)^## Ported metadata\s*$\n(.*?)(?=^##\s|\Z)", text)
    if not match:
        return {}, False
    section = match.group(1)
    fields: dict[str, str] = {}
    for field_match in re.finditer(r"(?m)^- `([a-z-]+):\s*(.*?)`\s*$", section):
        fields[field_match.group(1)] = field_match.group(2).strip()
    is_native_support = (
        "Codex-native support skill" in section
        and (
            "no upstream Claude skill equivalent" in section
            or (
                "Codex-native adaptation" in section
                and "project-local Claude analogue" in section
            )
        )
    )
    return fields, is_native_support


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


def validate_playtest_focus_contract(root: Path) -> list[str]:
    errors: list[str] = []
    for rel, required_phrases in PLAYTEST_FOCUS_CONTRACT.items():
        path = root / rel
        if not path.exists():
            errors.append(f"{rel}: missing playtest focus contract surface")
            continue
        text = path.read_text(encoding="utf-8").lower()
        missing = [phrase for phrase in required_phrases if phrase.lower() not in text]
        if missing:
            errors.append(f"{rel}: missing playtest focus contract phrase(s): {', '.join(missing)}")
    return errors


def contains_phrase(text: str, phrase: str) -> bool:
    normalized_text = re.sub(r"\s+", " ", text)
    normalized_phrase = re.sub(r"\s+", " ", phrase)
    return normalized_phrase in normalized_text


def validate_bug_lifecycle_contract(root: Path) -> list[str]:
    errors: list[str] = []
    for rel, required_phrases in BUG_LIFECYCLE_REQUIRED_PHRASES.items():
        path = root / rel
        if not path.exists():
            errors.append(f"{rel}: missing bug lifecycle contract surface")
            continue
        text = path.read_text(encoding="utf-8")
        missing = [phrase for phrase in required_phrases if not contains_phrase(text, phrase)]
        if missing:
            errors.append(f"{rel}: missing bug lifecycle contract phrase(s): {', '.join(missing)}")

    for rel, phrase, message in BUG_LIFECYCLE_FORBIDDEN_PHRASES:
        path = root / rel
        if not path.exists():
            continue
        if phrase in path.read_text(encoding="utf-8"):
            errors.append(f"{rel}: {message}")
    return errors


def validate_handoff_review_contract(root: Path) -> list[str]:
    errors: list[str] = []
    for rel, required_phrases in HANDOFF_REVIEW_REQUIRED_PHRASES.items():
        path = root / rel
        if not path.exists():
            errors.append(f"{rel}: missing handoff review contract surface")
            continue
        text = path.read_text(encoding="utf-8")
        missing = [phrase for phrase in required_phrases if not contains_phrase(text, phrase)]
        if missing:
            errors.append(f"{rel}: missing handoff review contract phrase(s): {', '.join(missing)}")

    for rel, required_phrases in HANDOFF_AUTHORIZATION_REQUIRED_PHRASES.items():
        path = root / rel
        if not path.exists():
            errors.append(f"{rel}: missing explicit handoff invocation boundary surface")
            continue
        text = path.read_text(encoding="utf-8")
        missing = [phrase for phrase in required_phrases if not contains_phrase(text, phrase)]
        if missing:
            errors.append(
                f"{rel}: missing explicit handoff invocation boundary phrase(s): "
                + ", ".join(missing)
            )

    skill_rel = ".agents/skills/handoff/SKILL.md"
    skill_path = root / skill_rel
    if skill_path.exists():
        skill_text = skill_path.read_text(encoding="utf-8")
        description = frontmatter(skill_text).get("description", "")
        if any(word in description.lower() for word in ("pause", "stop", "checkpoint", "resume later")):
            errors.append(
                f"{skill_rel}: explicit invocation boundary is ambiguous in frontmatter description"
            )

        for label, required_phrases in (
            ("context capacity gate", HANDOFF_CAPACITY_REQUIRED_PHRASES),
            ("review scope baseline contract", HANDOFF_SCOPE_REQUIRED_PHRASES),
            ("compact resume-index contract", HANDOFF_INDEX_REQUIRED_PHRASES),
        ):
            missing = [phrase for phrase in required_phrases if not contains_phrase(skill_text, phrase)]
            if missing:
                errors.append(
                    f"{skill_rel}: missing handoff {label} phrase(s): "
                    + ", ".join(missing)
                )

        missing = [
            phrase
            for phrase in HANDOFF_GIT_CAPABILITY_REQUIRED_PHRASES
            if not contains_phrase(skill_text, phrase)
        ]
        if missing:
            errors.append(
                f"{skill_rel}: missing handoff Git capability phrase(s): "
                + ", ".join(missing)
            )

        phase3_match = re.search(
            r"(?ms)^## Phase 3: Commit Handoff\s*$\n(.*?)(?=^## Phase 4: Push Handoff\s*$)",
            skill_text,
        )
        if not phase3_match:
            errors.append(f"{skill_rel}: missing bounded Phase 3 commit section")
        else:
            phase3_text = phase3_match.group(1)
            missing = [
                phrase
                for phrase in HANDOFF_PHASE3_GIT_WRITE_REQUIRED_PHRASES
                if not contains_phrase(phase3_text, phrase)
            ]
            if missing:
                errors.append(
                    f"{skill_rel}: Phase 3 missing direct Git-write phrase(s): "
                    + ", ".join(missing)
                )

        phase4_match = re.search(
            r"(?ms)^## Phase 4: Push Handoff\s*$\n(.*?)(?=^## Phase 5: Report And Stop\s*$)",
            skill_text,
        )
        if not phase4_match:
            errors.append(f"{skill_rel}: missing bounded Phase 4 push section")
        else:
            phase4_text = phase4_match.group(1)
            missing = [
                phrase
                for phrase in HANDOFF_PHASE4_PUSH_REQUIRED_PHRASES
                if not contains_phrase(phase4_text, phrase)
            ]
            if missing:
                errors.append(
                    f"{skill_rel}: Phase 4 missing direct push phrase(s): "
                    + ", ".join(missing)
                )
            for phrase, message in HANDOFF_PHASE4_PUSH_FORBIDDEN_PHRASES:
                if phrase in phase4_text:
                    errors.append(f"{skill_rel}: Phase 4 {message}: {phrase!r}")

        review_gate_match = re.search(
            r"(?ms)^## Phase 0: Review Gate\s*$\n(.*?)(?=^## Phase 1: Choose The Label\s*$)",
            skill_text,
        )
        for pattern, message in HANDOFF_REVIEW_FORBIDDEN_PATTERNS:
            if message == "external-review escalation token" and review_gate_match:
                search_text = review_gate_match.group(1)
                search_offset = review_gate_match.start(1)
            else:
                search_text = skill_text
                search_offset = 0
            match = pattern.search(search_text)
            if match:
                line_number = skill_text.count("\n", 0, search_offset + match.start()) + 1
                errors.append(f"{skill_rel}:{line_number}: {message}")
    return errors


def validate_resume_contract(root: Path) -> list[str]:
    path = root / RESUME_SKILL_PATH
    if not path.exists():
        return [f"{RESUME_SKILL_PATH}: missing resume selection contract surface"]

    text = path.read_text(encoding="utf-8")
    errors: list[str] = []
    missing = [phrase for phrase in RESUME_REQUIRED_PHRASES if not contains_phrase(text, phrase)]
    if missing:
        errors.append(
            f"{RESUME_SKILL_PATH}: missing resume selection contract phrase(s): "
            + ", ".join(missing)
        )

    for label, required_phrases in (
        ("bounded default slice-read contract", RESUME_BOUNDED_REQUIRED_PHRASES),
        ("cache readback contract", RESUME_READBACK_REQUIRED_PHRASES),
        ("source precedence contract", RESUME_PRECEDENCE_REQUIRED_PHRASES),
    ):
        missing = [phrase for phrase in required_phrases if not contains_phrase(text, phrase)]
        if missing:
            errors.append(
                f"{RESUME_SKILL_PATH}: missing resume {label} phrase(s): "
                + ", ".join(missing)
            )

    for line_number, line in enumerate(text.splitlines(), start=1):
        lower = line.lower()
        starts_lane = re.search(r"\b(?:start|begin|enter)\b", lower)
        bypasses_selection = any(
            phrase in lower
            for phrase in ("automatically", "immediately", "without waiting", "without selection")
        )
        explicitly_forbidden = any(
            phrase in lower for phrase in ("do not", "don't", "never", "must not", "cannot")
        )
        if starts_lane and bypasses_selection and not explicitly_forbidden:
            errors.append(
                f"{RESUME_SKILL_PATH}:{line_number}: automatic lane startup is forbidden; "
                "pause for the required selection boundary"
            )
        reads_full_slice = (
            re.search(r"\bread\b.*\b(?:entire|full|all)\b.*\b(?:slice|playable)[ -]?(?:source|history)?\b", lower)
            or re.search(r"\bread\b.*\b(?:slice|playable)[ -]?(?:source|history)?\b.*\b(?:entire|full|all)\b", lower)
            or re.search(r"\b(?:entire|full|all)\b.*\b(?:slice|playable)[ -]?(?:source|history)?\b.*\bread\b", lower)
        )
        deep_only = "deep" in lower
        explicitly_bounded = any(
            phrase in lower for phrase in ("do not", "must not", "never", "only explicit", "only in")
        )
        if reads_full_slice and not deep_only and not explicitly_bounded:
            errors.append(
                f"{RESUME_SKILL_PATH}:{line_number}: unbounded default slice read is forbidden; "
                "reserve the full slice history for explicit deep mode"
            )
    return errors


def validate_gen_asset_profile(profile_path: Path) -> list[str]:
    if not profile_path.exists():
        return [f"{profile_path}: missing gen-asset profile"]

    text = profile_path.read_text(encoding="utf-8")
    status_match = re.search(r"(?i)\*\*Status:\*\*\s*(ACTIVE|STUB)\b", text)
    if not status_match:
        return [f"{profile_path}: missing Status: ACTIVE or Status: STUB"]
    if status_match.group(1).upper() == "STUB":
        return []

    lower = text.lower()
    missing = [
        label
        for label, alternatives in GEN_ASSET_ACTIVE_PROFILE_FIELDS.items()
        if not any(alternative.lower() in lower for alternative in alternatives)
    ]
    if not missing:
        return []
    return [f"{profile_path}: ACTIVE profile missing semantic field(s): {', '.join(missing)}"]


def validate_gen_asset_contract(root: Path) -> list[str]:
    path = root / GEN_ASSET_SKILL_PATH
    if not path.exists():
        return []

    text = path.read_text(encoding="utf-8")
    errors: list[str] = []
    missing = [phrase for phrase in GEN_ASSET_REQUIRED_PHRASES if not contains_phrase(text, phrase)]
    if missing:
        errors.append(
            f"{GEN_ASSET_SKILL_PATH}: missing Codex-native generation contract phrase(s): "
            + ", ".join(missing)
        )

    forbidden_patterns = (
        (
            re.compile(r"(?im)^\s*(?:\$\s*)?codex\s+exec\b"),
            "nested Codex CLI generation command",
        ),
        (re.compile(r"\.Codex/"), "legacy Codex skill path"),
        (re.compile(r"\.claude/", re.IGNORECASE), "Claude runtime path"),
        (re.compile(r"\bOPENAI_API_KEY\b"), "API-key fallback"),
        (
            re.compile(r"(?i)\b(?:fallback|use)\b[^.\n]{0,100}\bnewest\b[^.\n]{0,80}\b(?:image|file|png)\b"),
            "unbounded newest-image fallback",
        ),
        (re.compile(r"(?i)\bcodex\s+doctor\b"), "nested Codex CLI precondition"),
        (re.compile(r"(?i)\bsession[ -]?id\b"), "nested Codex session-ID parsing"),
    )
    for pattern, message in forbidden_patterns:
        for match in pattern.finditer(text):
            line_number = text.count("\n", 0, match.start()) + 1
            errors.append(f"{GEN_ASSET_SKILL_PATH}:{line_number}: {message}")

    profile_root = path.parent / "profiles"
    if not profile_root.exists():
        errors.append(f"{profile_root.relative_to(root)}: missing gen-asset profiles directory")
        return errors
    profile_files = sorted(profile_root.glob("*.md"))
    if not profile_files:
        errors.append(f"{profile_root.relative_to(root)}: no gen-asset profiles found")
        return errors
    for profile_path in profile_files:
        errors.extend(validate_gen_asset_profile(profile_path))
    return errors


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
    errors.extend(validate_bug_lifecycle_contract(root))

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
        ported, is_native_support = ported_metadata(text)
        if not is_native_support:
            required_ported = {"argument-hint", "user-invocable", "allowed-tools"}
            missing_ported = sorted(required_ported - ported.keys())
            if missing_ported:
                errors.append(f"{rel}: missing Ported metadata {', '.join(missing_ported)}")
            elif not ported.get("argument-hint") or not ported.get("allowed-tools"):
                errors.append(f"{rel}: empty Ported metadata argument-hint or allowed-tools")
            if "user-invocable" in ported and ported.get("user-invocable") != "true":
                errors.append(f"{rel}: Ported metadata user-invocable must be true")
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
        if "subagent_type:" in text:
            errors.append(f"{rel}: stale Claude subagent_type delegation vocabulary remains")
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

    stale_framework_phrases = (
        "Has required frontmatter fields: `name`, `description`, `argument-hint`, `user-invocable`, `allowed-tools`",
        "`allowed-tools` frontmatter",
        "argument-hint format from frontmatter",
        "`context: fork` behavior",
    )
    framework_roots = (
        root / "CCGS Skill Testing Framework" / "skills",
        root / ".codex" / "docs" / "templates",
    )
    for framework_root in framework_roots:
        if not framework_root.exists():
            continue
        for spec_file in sorted(framework_root.rglob("*.md")):
            spec_text = spec_file.read_text(encoding="utf-8")
            for phrase in stale_framework_phrases:
                if phrase in spec_text:
                    errors.append(
                        f"{spec_file.relative_to(root)}: stale Claude skill-metadata assertion {phrase!r}"
                    )
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

    for phrase in ROLE_DELEGATION_EVIDENCE_PHRASES:
        if phrase not in text:
            errors.append(
                f"AGENTS.md: missing runtime role-delegation evidence boundary {phrase!r}"
            )

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
    framework_agents = root / "CCGS Skill Testing Framework" / "agents"
    if framework_agents.exists():
        stale_agent_reference = re.compile(r"\.codex/agents/[^`]+\.md` frontmatter")
        for spec_file in sorted(framework_agents.rglob("*.md")):
            if stale_agent_reference.search(spec_file.read_text(encoding="utf-8")):
                errors.append(
                    f"{spec_file.relative_to(root)}: stale Markdown/frontmatter custom-agent reference"
                )
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
        errors.extend(validate_playtest_focus_contract(root))
    if args.kind in {"runtime", "skills"}:
        errors.extend(validate_handoff_review_contract(root))
        errors.extend(validate_resume_contract(root))
        errors.extend(validate_gen_asset_contract(root))
    if args.kind == "skills":
        errors.extend(validate_skills(root, args.require_present))
    if args.kind == "agents":
        errors.extend(validate_agents(root, args.require_present))
    return emit(args.kind, root, errors, warnings)


if __name__ == "__main__":
    raise SystemExit(main())
