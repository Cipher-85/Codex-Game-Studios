#!/usr/bin/env python3
"""Read and preview CCGS configuration. No command applies or writes settings."""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
import re
import sys


RIGOR = {
    "minimal": dict(zip(("modes.workflow", "docs.density", "qa.level", "modes.story_granularity", "modes.review_mode", "team.size"),
                        ("minimal", "terse", "minimal", "coarse", "solo", "individual"))),
    "standard": dict(zip(("modes.workflow", "docs.density", "qa.level", "modes.story_granularity", "modes.review_mode", "team.size"),
                         ("standard", "balanced", "standard", "balanced", "lean", "individual"))),
    "full": dict(zip(("modes.workflow", "docs.density", "qa.level", "modes.story_granularity", "modes.review_mode", "team.size"),
                     ("full", "thorough", "full", "fine", "full", "studio"))),
}


def field(kind, sample, choices=None, local=False):
    return {"type": kind, "sample": sample, "choices": choices, "local": local}


# This is the sole field/enum/local-override registry. Unset values remain None.
SCHEMA = {
    "schema_version": field("integer", 1, [1]),
    "framework.version": field("string", "0.7.4"),
    "framework.last_upgraded": field("string", "2026-10-20"),
    "project.name": field("string", "Example game"),
    "project.stage": field("string", "Concept"),
    "project.kind": field("string", "game"),
    "engine.name": field("string", "Godot"),
    "engine.version": field("string", "4.6"),
    "engine.language": field("string", "GDScript"),
    "modes.rigor": field("string", "standard", list(RIGOR)),
    "modes.review_mode": field("string", "full", ["solo", "lean", "full"], True),
    "modes.workflow": field("string", "standard", list(RIGOR)),
    "modes.automation": field("string", "collaborative", ["collaborative", "guided", "autonomous"], True),
    "modes.automation_always_ask": field("strings", ["scope_changes", "file_deletions", "schema_changes"], local=True),
    "modes.story_granularity": field("string", "balanced", ["coarse", "balanced", "fine"]),
    "docs.density": field("string", "balanced", ["terse", "balanced", "thorough"]),
    "qa.level": field("string", "standard", list(RIGOR)),
    "qa.coverage_minimum": field("percentage", 80),
    "team.size": field("string", "individual", ["individual", "small", "studio"], True),
    "testing.framework": field("string", "GdUnit4"),
    "testing.strict": field("boolean", True),
    **{"testing.strict." + kind: field("boolean", True, local=True)
       for kind in ("logic", "integration", "visual", "ui", "config")},
    "platform.targets": field("strings", ["PC", "Web"]),
    "platform.primary_input": field("string", "Keyboard/Mouse"),
    "platform.gamepad_support": field("string", "Full", ["Full", "Partial", "None"]),
    "platform.touch_support": field("string", "None", ["Full", "Partial", "None"]),
    **{"performance." + key: field("positive-number", sample)
       for key, sample in (("target_framerate", 60), ("frame_budget_ms", 16.67),
                           ("draw_call_limit", 1000), ("memory_ceiling_mb", 512))},
    "performance.enforce": field("string", "warn", ["warn", "block", "off"], True),
}
LOCAL_KEYS = {key for key, rule in SCHEMA.items() if rule["local"]}
DEFAULTS = {
    "modes.review_mode": "lean",
    "modes.automation": "collaborative",
    "modes.automation_always_ask": ["scope_changes", "file_deletions", "schema_changes"],
}
SYSTEM_PREFIX = "workflow_overrides.system_overrides."
# Consumer support is explicit; inspection itself never executes a workflow.
OPERATIONAL_KEYS = ("modes.review_mode", "modes.workflow", "docs.density",
                    "modes.story_granularity", "project.stage", "qa.level",
                    "qa.coverage_minimum", "testing.strict", "team.size",
                    "testing.framework", "engine.name", "engine.version", "engine.language",
                    "platform.targets", "platform.primary_input", "platform.gamepad_support",
                    "platform.touch_support", "performance.target_framerate",
                    "performance.frame_budget_ms", "performance.draw_call_limit",
                    "performance.memory_ceiling_mb", "performance.enforce",
                    *("testing.strict." + kind for kind in ("logic", "integration", "visual", "ui", "config")))
GDD_SECTIONS = ("Overview", "Player Fantasy", "Detailed Rules", "Formulas",
                "Edge Cases", "Dependencies", "Tuning Knobs", "Acceptance Criteria")
STANDARD_SECTIONS = ("Overview", "Detailed Rules", "Edge Cases", "Dependencies", "Acceptance Criteria")
STAGES = {"concept": "Concept", "systems-design": "Systems Design",
          "technical-setup": "Technical Setup", "pre-production": "Pre-Production",
          "production": "Production", "polish": "Polish", "release": "Release", "live": "Live"}
PREFS = ".codex/docs/technical-preferences.md"
TECH_FIELDS = {
    "engine.name": ("Engine & Language", "Engine", None),
    "engine.language": ("Engine & Language", "Language", None),
    "testing.framework": ("Testing", "Framework", None),
    "qa.coverage_minimum": ("Testing", "Minimum Coverage", "%"),
    "platform.targets": ("Input & Platform", "Target Platforms", "list"),
    "platform.primary_input": ("Input & Platform", "Primary Input", None),
    "platform.gamepad_support": ("Input & Platform", "Gamepad Support", "enum"),
    "platform.touch_support": ("Input & Platform", "Touch Support", "enum"),
    "performance.target_framerate": ("Performance Budgets", "Target Framerate", "fps"),
    "performance.frame_budget_ms": ("Performance Budgets", "Frame Budget", "ms"),
    "performance.draw_call_limit": ("Performance Budgets", "Draw Calls", "draw calls"),
    "performance.memory_ceiling_mb": ("Performance Budgets", "Memory Ceiling", "MB"),
}
TECH_KEYS = tuple(k for k in OPERATIONAL_KEYS if k.startswith(("engine.", "platform.", "performance.")) or k in ("testing.framework", "qa.coverage_minimum"))


class ConfigError(ValueError):
    pass


def uncomment(text):
    """Remove comments outside quoted strings; keep delimiters for scalar parsing."""
    quote = None
    escape = False
    at_start = True
    for i, char in enumerate(text):
        if escape:
            escape = False
        elif char == "\\" and quote == '"':
            escape = True
        elif char == quote:
            quote = None
        elif quote is None and char in "\"'" and at_start:
            quote = char
        elif quote is None and char == "#" and (i == 0 or text[i - 1].isspace()):
            return text[:i].rstrip()
        elif quote is None and char in ":[,":
            at_start = True
        elif quote is None and not char.isspace():
            at_start = char == "-" and i == 0
    return text.rstrip()


def scalar(text):
    """Parse the documented data-only YAML subset; unsupported forms are errors."""
    text = text.strip()
    if text in ("", "null", "~"):
        return None
    if text.startswith(("|", ">")):
        raise ConfigError("multiline YAML values are unsupported; use a quoted single-line value")
    if text[0] in "&*!{":
        raise ConfigError("unsupported YAML anchor, alias, tag or flow mapping")
    if text.startswith('"'):
        try:
            value = json.loads(text)
        except json.JSONDecodeError as error:
            raise ConfigError("invalid double-quoted string") from error
        if not isinstance(value, str):
            raise ConfigError("expected a quoted string")
        return value
    if text.startswith("'"):
        if not re.fullmatch(r"'(?:[^']|'')*'", text):
            raise ConfigError("invalid single-quoted string")
        return text[1:-1].replace("''", "'")
    if text.startswith("["):
        if not text.endswith("]"):
            raise ConfigError("unterminated inline list")
        body = text[1:-1].strip()
        if not body:
            return []
        items, start, quote, escape = [], 0, None, False
        for i, char in enumerate(body):
            if escape:
                escape = False
            elif char == "\\" and quote == '"':
                escape = True
            elif char == quote:
                quote = None
            elif quote is None and char in "\"'":
                quote = char
            elif quote is None and char in "[]{}":
                raise ConfigError("nested flow collections are unsupported")
            elif quote is None and char == ",":
                items.append(body[start:i].strip())
                start = i + 1
        items.append(body[start:].strip())
        if quote or any(not item for item in items):
            raise ConfigError("invalid inline list")
        return [scalar(item) for item in items]
    if text in ("true", "false"):
        return text == "true"
    if re.fullmatch(r"-?(?:0|[1-9][0-9]*)", text):
        if len(text.lstrip("-")) > 100:
            raise ConfigError("integer exceeds configuration numeric limit")
        return int(text)
    if re.fullmatch(r"-?(?:0|[1-9][0-9]*)\.[0-9]+(?:[eE][+-]?[0-9]+)?", text):
        value = float(text)
        if not math.isfinite(value):
            raise ConfigError("non-finite number")
        return value
    if re.search(r":(?:\s|$)", text) or text.startswith(("- ", "? ", "]", "}")):
        raise ConfigError("unsupported YAML scalar or nested structure")
    return text


def parse_yaml(text, label):
    """Mappings and flat scalar lists only; duplicate blocks are never merged."""
    if "\x00" in text:
        raise ConfigError(f"{label}: NUL bytes are unsupported")
    lines = []
    for number, raw in enumerate(text.lstrip("\ufeff").splitlines(), 1):
        indent_text = raw[:len(raw) - len(raw.lstrip())]
        if "\t" in indent_text:
            raise ConfigError(f"{label}:{number}: tab indentation is unsupported")
        content = uncomment(raw.lstrip())
        if content:
            lines.append((len(indent_text), content, number))
    if not lines:
        raise ConfigError(f"{label}: empty configuration")
    if lines[0][0] != 0:
        raise ConfigError(f"{label}:{lines[0][2]}: root mapping must start at column 1")

    def block(index, indent, nesting=0):
        if nesting > 16:
            raise ConfigError(f"{label}: configuration nesting exceeds 16 levels")
        is_list = lines[index][1].startswith("- ")
        result = [] if is_list else {}
        while index < len(lines):
            depth, content, number = lines[index]
            if depth < indent:
                break
            if depth > indent:
                raise ConfigError(f"{label}:{number}: inconsistent indentation")
            try:
                if is_list:
                    if not content.startswith("- "):
                        raise ConfigError("mixed list and mapping")
                    result.append(scalar(content[2:]))
                    index += 1
                    continue
                match = re.fullmatch(r"([A-Za-z_][A-Za-z0-9_-]*):(?:\s+(.*))?", content)
                if not match:
                    raise ConfigError("expected a mapping key and value")
                key, raw_value = match.groups()
                if key in result:
                    raise ConfigError(f"duplicate key {key}")
                index += 1
                if not raw_value and index < len(lines) and lines[index][0] > indent:
                    result[key], index = block(index, lines[index][0], nesting + 1)
                else:
                    result[key] = scalar(raw_value or "")
            except ConfigError as error:
                raise ConfigError(f"{label}:{number}: {error}") from error
        return result, index

    data, end = block(0, 0)
    if not isinstance(data, dict) or end != len(lines):
        raise ConfigError(f"{label}: expected a single root mapping")
    return data


def flatten(data, prefix=""):
    result = {}
    for key, value in data.items():
        path = prefix + key
        if isinstance(value, dict):
            result.update(flatten(value, path + "."))
        else:
            result[path] = value
    return result


def validate_value(key, value):
    if key.startswith(SYSTEM_PREFIX) and re.fullmatch(r"[A-Za-z0-9_-]+", key[len(SYSTEM_PREFIX):]):
        rule = field("string", "standard", list(RIGOR))
    elif key in SCHEMA:
        rule = SCHEMA[key]
    else:
        raise ConfigError(f"unknown setting {key}")
    if value is None and key != "schema_version":
        return
    kind = rule["type"]
    valid = {
        "string": lambda: isinstance(value, str) and bool(value.strip()),
        "strings": lambda: isinstance(value, list) and all(isinstance(v, str) and bool(v.strip()) for v in value),
        "integer": lambda: type(value) is int,
        "boolean": lambda: type(value) is bool,
        "percentage": lambda: type(value) in (int, float) and math.isfinite(value) and 0 <= value <= 100,
        "positive-number": lambda: type(value) in (int, float) and math.isfinite(value) and value > 0,
    }[kind]()
    if not valid or (rule["choices"] is not None and value not in rule["choices"]):
        raise ConfigError(f"{key}: expected {kind}" + (f" in {rule['choices']}" if rule["choices"] else ""))


def read_file(root, relative):
    path = root
    for part in Path(relative).parts:
        path /= part
        if path.is_symlink():
            raise ConfigError(f"{relative}: symlink inputs are unsupported")
    if not path.exists():
        return None
    if not path.is_file() or path.stat().st_size > 131072:
        raise ConfigError(f"{relative}: expected a regular file of at most 128 KiB")
    try:
        return path.read_text(encoding="utf-8-sig")
    except (OSError, UnicodeError) as error:
        raise ConfigError(f"{relative}: cannot read UTF-8 text") from error


def load_config(root, relative, local=False):
    text = read_file(root, relative)
    if text is None:
        return {}, False
    data = flatten(parse_yaml(text, relative))
    if not local and data.get("schema_version") != 1:
        raise ConfigError(f"{relative}: schema_version: 1 is required")
    for key, value in data.items():
        validate_value(key, value)
        if local and key != "schema_version" and key not in LOCAL_KEYS:
            raise ConfigError(f"{relative}: {key} is not locally overridable")
    return data, True


def preference_fields(text):
    """Read named Markdown fields; prose and fenced examples stay untouched."""
    section, fenced, result = "", False, {}
    known = {(row[0], row[1]) for row in TECH_FIELDS.values()}
    known.update({("", "Engine"), ("", "Language")})
    for line in text.splitlines():
        if line.lstrip().startswith(("```", "~~~")):
            fenced = not fenced
            continue
        if fenced:
            continue
        if line.startswith("## "):
            section = line[3:].strip()
        match = re.fullmatch(r"- \*\*([^*]+)\*\*:\s*(.*)", line)
        if match:
            label, value = match.groups()
            key = (section, label)
            if key in result and (key in known or section == "Engine Specialists"):
                raise ConfigError(f"{PREFS}: ambiguous repeated {label} lines")
            result[key] = value.strip()
    return result


def technical_legacy(text):
    fields = preference_fields(text)
    mapped, unmapped = {}, []
    for key, (section, label, unit) in TECH_FIELDS.items():
        raw = fields.get((section, label))
        # Legacy Engine/Language reads predate standardized section headings.
        if raw is None and key in ("engine.name", "engine.language"):
            candidates = [value for (_, name), value in fields.items() if name == label]
            if len(candidates) > 1:
                raise ConfigError(f"{PREFS}: ambiguous repeated {label} lines")
            raw = candidates[0] if candidates else None
        if not raw or raw.startswith("[TO BE CONFIGURED"):
            continue
        value = raw
        if unit == "list":
            value = [item.strip() for item in raw.split(",")]
        elif unit == "enum":
            value = next((v for v in SCHEMA[key]["choices"] if v.casefold() == raw.casefold()), None)
        elif unit:
            match = re.fullmatch(r"(-?\d+(?:\.\d+)?)\s*(?:" + re.escape(unit) + r")?", raw, re.I)
            value = float(match[1]) if match else None
            if value is not None and value.is_integer():
                value = int(value)
        if value is None:
            unmapped.append({"key": key, "value": raw, "reason": "not a supported literal; preserve and review the original prose"})
            continue
        validate_value(key, value)
        mapped[key] = {"value": value, "source": PREFS}
    return mapped, unmapped


def legacy_values(root, include_notes=False):
    result = {}
    for key, path in (("modes.review_mode", "production/review-mode.txt"),
                      ("project.stage", "production/stage.txt")):
        text = read_file(root, path)
        if text and text.strip():
            value = text.strip()
            try:
                validate_value(key, value)
            except ConfigError as error:
                raise ConfigError(f"{path}: {error}") from error
            result[key] = {"value": value, "source": path}
    prefs = read_file(root, PREFS)
    unmapped = []
    if prefs:
        mapped, unmapped = technical_legacy(prefs)
        result.update(mapped)
    if include_notes:
        return result, bool(prefs), unmapped
    return result, bool(prefs)


def resolve(root, system=None, overrides=None, local=False):
    root = Path(root).resolve()
    output = {"root": str(root), "status": "invalid", "activation": "preview-only",
              "applied": False, "operational_keys": list(OPERATIONAL_KEYS),
              "settings": {}, "errors": [], "notes": []}
    try:
        if not root.is_dir():
            raise ConfigError("project root is not a directory")
        project, base_exists = load_config(root, "project.yaml")
        personal, local_exists = load_config(root, "project.local.yaml", local=True)
        if (local_exists or (local and overrides)) and not base_exists:
            raise ConfigError("project.local.yaml requires project.yaml")
        legacy, has_prose, unmapped = legacy_values(root, include_notes=True)
        if system is not None and not re.fullmatch(r"[A-Za-z0-9_-]+", system):
            raise ConfigError("system must be a single identifier")

        def effective(base, user):
            values = {}
            keys = set(SCHEMA) | set(base) | set(user)
            rigor = base.get("modes.rigor")
            for key in sorted(keys):
                if user.get(key) is not None:
                    values[key] = {"value": user[key], "source": "project.local.yaml"}
                elif base.get(key) is not None:
                    values[key] = {"value": base[key], "source": "project.yaml"}
                elif key in legacy:
                    values[key] = legacy[key]
                elif rigor and key in RIGOR[rigor]:
                    values[key] = {"value": RIGOR[rigor][key], "source": "rigor:" + rigor}
                elif key.startswith("testing.strict.") and base.get("testing.strict") is not None:
                    values[key] = {"value": base["testing.strict"], "source": "project.yaml:testing.strict"}
                else:
                    values[key] = {"value": DEFAULTS.get(key), "source": "default" if key in DEFAULTS else "unset"}
            override_key = SYSTEM_PREFIX + system if system else None
            if override_key and base.get(override_key) is not None:
                values["modes.workflow"] = {"value": base[override_key], "source": "project.yaml:" + override_key}
            return values

        before = effective(project, personal)
        if overrides:
            for key, value in overrides.items():
                if key in ("schema_version", "framework.version", "framework.last_upgraded"):
                    raise ConfigError(f"{key}: metadata cannot be changed through a settings preview")
                validate_value(key, value)
                if local and key not in LOCAL_KEYS:
                    raise ConfigError(f"{key} is not locally overridable")
            (personal if local else project).update(overrides)
        after = effective(project, personal)
        output.update(status="ready", settings=after)
        if overrides:
            output["preview_target"] = "project.local.yaml" if local else "project.yaml"
            output["changes"] = {key: {"before": before.get(key), "after": after.get(key)}
                                 for key in sorted(before.keys() | after.keys()) if before.get(key) != after.get(key)}
        output["notes"].append("Inspection only; operational_keys names supported consumers, not executed workflows. Automation and remaining project metadata do not grant actions.")
        if not base_exists:
            output["notes"].append("No project.yaml; no rigor tier is inferred. The new-project template recommends standard.")
        if has_prose:
            output["notes"].append("Custom legacy prose, required tests and specialist routing remain authoritative; no tier or separate engine version is inferred from prose.")
        output["notes"].extend("Unmapped technical field " + row["key"] + ": " + row["reason"] for row in unmapped)
        if overrides and not local and any(personal.get(key) is not None for key in overrides):
            output["notes"].append("A local override shadows at least one proposed project value.")
    except (ConfigError, OSError, UnicodeError) as error:
        output.update(status="invalid", settings={}, errors=[str(error)])
    return output


def review_mode(root, review=None):
    """Read operational review routing; validate config before applying a run flag."""
    resolved = resolve(root)
    result = {"root": resolved["root"], "status": resolved["status"],
              "activation": "review-mode-only", "applied": False,
              "operational_keys": list(OPERATIONAL_KEYS), "value": None,
              "source": None, "configured": False, "errors": resolved["errors"],
              "notes": resolved["notes"]}
    if resolved["status"] != "ready":
        return result
    try:
        if review is not None:
            validate_value("modes.review_mode", review)
            # Null is meaningful in YAML, but a supplied CLI flag must name a mode.
            if review not in ("full", "lean", "solo"):
                raise ConfigError("--review: expected full, lean or solo")
            entry = {"value": review, "source": "--review"}
        else:
            entry = resolved["settings"]["modes.review_mode"]
        result.update(entry, configured=entry["source"] != "default")
    except ConfigError as error:
        result.update(status="invalid", errors=[str(error)])
    return result


def workflow(root, system=None, check_systems=False):
    """Read workflow policy once per project or exact GDD filename stem."""
    resolved = resolve(root)
    result = {"root": resolved["root"], "status": resolved["status"],
              "activation": "workflow-policy", "applied": False,
              "operational_keys": list(OPERATIONAL_KEYS), "tier": None,
              "source": None, "project_tier": None, "system": system,
              "design_source": None,
              "required_sections": [], "formula_requirement": None,
              "density": None, "story_granularity": None,
              "known_systems": [], "unmatched_systems": [],
              "errors": resolved["errors"], "notes": resolved["notes"]}
    if resolved["status"] != "ready":
        return result
    if system is not None and not re.fullmatch(r"[A-Za-z0-9_-]+", system):
        result.update(status="invalid", errors=["system must be a single identifier"])
        return result
    values = resolved["settings"]
    project = values["modes.workflow"]
    selected = project
    if system:
        key = SYSTEM_PREFIX + system
        override = values.get(key)
        if override and override["value"] is not None:
            selected = {"value": override["value"], "source": "project.yaml:" + key}
    tier = selected["value"] or "compatibility"
    result.update(tier=tier, source=selected["source"],
                  project_tier=project["value"] or "compatibility",
                  design_source="design/game-brief.md" if project["value"] == "minimal" else "design/gdd/game-concept.md",
                  required_sections=list(() if tier == "minimal" else STANDARD_SECTIONS if tier == "standard" else GDD_SECTIONS),
                  formula_requirement="numeric_rules" if tier == "standard" else "optional" if tier == "minimal" else "required",
                  density=values["docs.density"], story_granularity=values["modes.story_granularity"])
    if check_systems:
        try:
            root = Path(resolved["root"])
            excluded = {"game-concept", "game-pillars", "systems-index"}
            known = {p.stem for p in (root / "design/gdd").glob("*.md")
                     if p.stem not in excluded and not p.stem.startswith("gdd-cross-review-") and not p.is_symlink()}
            # An override may name a declared GDD that has not been authored yet.
            index = read_file(root, "design/gdd/systems-index.md") or ""
            known.update(re.findall(r"design/gdd/([A-Za-z0-9_-]+)\.md", index))
            known.difference_update(excluded)
            keys = {key[len(SYSTEM_PREFIX):] for key, entry in values.items()
                    if key.startswith(SYSTEM_PREFIX) and entry["value"] is not None}
            result.update(known_systems=sorted(known), unmatched_systems=sorted(keys - known))
            if keys - known:
                result["notes"].append("Unmatched system overrides: " + ", ".join(sorted(keys - known)))
        except (ConfigError, OSError, UnicodeError) as error:
            result.update(status="invalid", tier=None, errors=[str(error)])
    return result


def stage(root):
    """Resolve recorded stage and its single approved-edit target; never write."""
    resolved = resolve(root)
    result = {"root": resolved["root"], "status": resolved["status"],
              "activation": "stage-read", "applied": False,
              "operational_keys": list(OPERATIONAL_KEYS), "value": None, "source": None,
              "phase": None, "terminal": False, "configured": False,
              "write_target": None, "write_key": None, "shadowed_legacy": None,
              "errors": resolved["errors"], "notes": resolved["notes"]}
    if resolved["status"] != "ready":
        return result
    entry = resolved["settings"]["project.stage"]
    raw = entry["value"]
    phase = re.sub(r"[\s_]+", "-", raw.strip().lower()) if raw else None
    if phase is not None and phase not in STAGES:
        result.update(status="invalid", errors=["Unrecognized project.stage: " + raw])
        return result
    result.update(value=STAGES.get(phase), source=entry["source"], phase=phase,
                  terminal=phase == "live", configured=raw is not None,
                  write_target="project.yaml" if entry["source"] == "project.yaml" else "production/stage.txt",
                  write_key="project.stage" if entry["source"] == "project.yaml" else None)
    if entry["source"] == "project.yaml":
        try:
            legacy = read_file(Path(resolved["root"]), "production/stage.txt")
            if legacy and legacy.strip() != raw:
                result["shadowed_legacy"] = legacy.strip()
        except (ConfigError, OSError, UnicodeError) as error:
            result.update(status="invalid", value=None, source=None, phase=None,
                          configured=False, terminal=False, write_target=None,
                          write_key=None, errors=[str(error)])
    return result


def policy_result(resolved, activation):
    return {"root": resolved["root"], "status": resolved["status"],
            "activation": activation, "applied": False,
            "operational_keys": list(OPERATIONAL_KEYS), "errors": resolved["errors"],
            "notes": list(resolved["notes"])}


def qa_policy(root):
    resolved = resolve(root)
    result = policy_result(resolved, "qa-policy")
    result.update(level=None, source=None, types={}, coverage=None, additional_regression=False)
    if resolved["status"] != "ready":
        return result
    values = resolved["settings"]
    level = values["qa.level"]
    result.update(level=level["value"] or "compatibility", source=level["source"],
                  additional_regression=level["value"] == "full")
    for kind in ("logic", "integration", "visual", "ui", "config"):
        strict = values["testing.strict." + kind]
        result["types"][kind] = {"requested_strict": strict["value"], "source": strict["source"],
                                  "gate": "blocking" if kind in ("logic", "integration") or strict["value"] is True else "advisory",
                                  "evidence_required": True, "known_failure_blocks": True}
    minimum = values["qa.coverage_minimum"]
    result["coverage"] = {"minimum": minimum["value"], "source": minimum["source"],
                          "active": level["value"] == "full" and minimum["value"] is not None,
                          "measurement": "NOT ASSESSED"}
    if minimum["value"] is not None and level["value"] != "full":
        result["notes"].append("coverage_minimum is configured but inactive outside qa.level full.")
    result["notes"].append("Required evidence and criterion failures always block completion; false strictness affects only otherwise-advisory findings.")
    return result


def team_policy(root):
    resolved = resolve(root)
    result = policy_result(resolved, "team-policy")
    result.update(size=None, source=None, optional_roles=None, required_roles="preserve",
                  review_mode_independent=True)
    if resolved["status"] == "ready":
        entry = resolved["settings"]["team.size"]
        result.update(size=entry["value"] or "compatibility", source=entry["source"],
                      optional_roles={None: "existing", "individual": "none", "small": "relevant", "studio": "declared"}[entry["value"]])
    return result


def engine_family(value):
    if not value:
        return None
    match = re.match(r"^(Godot|Unity|Unreal|UE[45])(?:\b|\d)", value, re.I)
    return ("unreal" if match and match[1].lower().startswith("ue") else match[1].lower()) if match else None


def technical(root):
    resolved = resolve(root)
    result = policy_result(resolved, "technical-read")
    result.update(settings={}, conflicts=[], shadowed_legacy=[], unmapped=[], write_targets={},
                  engine_family=None, engine_ready=False, pin=None,
                  engine_runtime="NOT ASSESSED", runner_status="NOT ASSESSED", routing={})
    if resolved["status"] != "ready":
        return result
    try:
        root = Path(resolved["root"])
        values = resolved["settings"]
        result["settings"] = {key: values[key] for key in TECH_KEYS}
        text = read_file(root, PREFS) or ""
        legacy, result["unmapped"] = technical_legacy(text)
        fields = preference_fields(text)
        family = engine_family(values["engine.name"]["value"])
        result["engine_family"] = family
        for key, old in legacy.items():
            if values[key]["source"] in ("project.yaml", "project.local.yaml") and values[key]["value"] != old["value"]:
                result["shadowed_legacy"].append({"key": key, "value": values[key]["value"], "legacy": old["value"]})
        for key in ("engine.name", "engine.language", "testing.framework"):
            if values[key]["source"] == "project.yaml" and key in legacy:
                current, old = values[key]["value"], legacy[key]["value"]
                equal = engine_family(current) == engine_family(old) if key == "engine.name" and family else current.casefold() == old.casefold()
                if not equal:
                    result["conflicts"].append({"key": key, "project": current, "legacy": old})
        for key in TECH_KEYS:
            if values[key]["source"] in ("project.yaml", "project.local.yaml"):
                result["write_targets"][key] = {"path": values[key]["source"], "field": key}
            elif key in TECH_FIELDS:
                section, label, _ = TECH_FIELDS[key]
                result["write_targets"][key] = {"path": PREFS, "section": section, "field": label}
            else:
                result["write_targets"][key] = {"path": None, "field": key,
                                                 "reason": "requires an explicit project configuration or engine-pin proposal"}
        if family:
            path = f"docs/engine-reference/{family}/VERSION.md"
            pin_text = read_file(root, path)
            matches = re.findall(r"^\|\s*\*\*Engine Version\*\*\s*\|\s*([^|]+)\|", pin_text or "", re.M)
            pinned = matches[0].strip().strip("`") if len(matches) == 1 else None
            if pinned and pinned.startswith("["):
                pinned = None
            result["pin"] = {"path": path, "version": pinned}
            requested = values["engine.version"]["value"]
            prefix = {"godot": "Godot ", "unity": "Unity ", "unreal": "Unreal Engine "}[family]
            pin_version = pinned.removeprefix(prefix) if pinned else None
            if requested and pinned and requested not in (pinned, pin_version):
                result["conflicts"].append({"key": "engine.version", "project": requested, "pin": pinned})
            result["engine_ready"] = bool(pinned and values["engine.language"]["value"] and
                                          not any(row["key"].startswith("engine.") for row in result["conflicts"]))
        registered = {p.stem for p in (root / ".codex/agents").glob("*.toml") if not p.is_symlink()}
        for (section, label), raw in fields.items():
            if section == "Engine Specialists" and label in ("Primary", "Language/Code Specialist", "Shader Specialist", "UI Specialist", "Additional Specialists") and raw and not raw.startswith("[TO BE CONFIGURED"):
                unannotated = re.sub(r"\([^)]*\)", "", raw)
                names = re.findall(r"\b(?:[a-z]+-)+(?:specialist|programmer|director|designer|tester|lead|artist|analyst|manager)\b", unannotated)
                roles = [name for name in names if name in registered]
                unknown = [name for name in names if name not in registered]
                wrong_engine = [name for name in roles if
                                (name.startswith("godot-") and family != "godot") or
                                (name.startswith("unity-") and family != "unity") or
                                (name.startswith(("unreal-", "ue-")) and family != "unreal")]
                if wrong_engine:
                    result["conflicts"].append({"key": "routing." + label, "roles": wrong_engine, "engine": family})
                result["routing"][label] = {"raw": raw, "roles": roles,
                                            "unknown": unknown,
                                            "status": "conflict" if wrong_engine else "NOT ASSESSED" if unknown or not roles else "registered"}
        result["notes"].append("Ready means configuration parsed, not engine/runner execution. Verify actual runner help, metadata and measurements before use.")
    except (ConfigError, OSError, UnicodeError) as error:
        result.update(status="invalid", settings={}, engine_ready=False, write_targets={}, errors=[str(error)])
    return result


def code_root(root, paths=None):
    """Resolve source scope without scanning, following links or creating folders."""
    resolved = resolve(root)
    result = policy_result(resolved, "code-root-read")
    result.update(resolution="unresolved", engine_family=None, source="unset",
                  roots=[], content_roots=[], evidence=[], conflicts=[],
                  scan_status="NOT ASSESSED", reason="Source scope is unresolved.")
    if resolved["status"] != "ready":
        return result
    try:
        root = Path(resolved["root"])

        def entry(relative):
            # Compare directory-entry spelling, even on case-insensitive hosts.
            # Reject links before inspecting the target, including parent links.
            relative = relative.replace("\\", "/")
            parts = relative.split("/")
            if (not relative or relative.startswith("/") or
                    any(p == ".." or p.startswith(".env") or ":" in p for p in parts) or
                    any(ord(c) < 32 or ord(c) == 127 for c in relative)):
                raise ConfigError("code-root: expected a non-secret, repository-relative path")
            current = root
            for part in Path(relative).parts:
                child = next((p for p in current.iterdir() if p.name == part), None)
                if child is None:
                    return None
                if child.is_symlink():
                    raise ConfigError(f"code-root: symlink scope is unsupported: {relative}")
                current = child
            if not (current.is_dir() or current.is_file()):
                raise ConfigError(f"code-root: unsupported entry: {relative}")
            return current

        markers = {"godot": [], "unity": [], "unreal": []}
        for family, relative in (("godot", "project.godot"),
                                 ("unity", "ProjectSettings/ProjectVersion.txt")):
            path = entry(relative)
            if path is not None and path.is_file():
                markers[family].append(relative)
        for path in sorted(root.iterdir()):
            if path.name.endswith(".uproject"):
                candidate = entry(path.name)
                if candidate is not None and candidate.is_file():
                    markers["unreal"].append(path.name)
        result["evidence"] = [path for group in markers.values() for path in group]
        engine = resolved["settings"]["engine.name"]
        family = engine_family(engine["value"])
        result["engine_family"] = family
        if engine["value"]:
            result["source"] = engine["source"] + ":engine.name"
            legacy, _ = technical_legacy(read_file(root, PREFS) or "")
            old = legacy.get("engine.name", {}).get("value")
            if old and engine["source"] == "project.yaml" and engine_family(old) != family:
                result["conflicts"].append("Configured and legacy engine families disagree.")
            if family is None:
                result["reason"] = "Configured engine has no supported source-layout mapping; resolve the scope explicitly with the user."
                return result
        found = [name for name, values in markers.items() if values]
        if len(found) > 1 or (family and any(name != family for name in found)):
            result["conflicts"].append("Project markers disagree with each other or the configured engine.")
        if len(markers["unreal"]) > 1:
            result["conflicts"].append("Multiple Unreal project files require explicit project selection.")
        if result["conflicts"]:
            result["reason"] = "Resolve conflicting engine evidence before selecting source scope."
            return result
        if not family and found:
            family = found[0]
            result.update(engine_family=family, source="project markers")

        content = {"godot": ("assets", "scenes"), "unity": ("Assets",),
                   "unreal": ("Content", "Plugins")}.get(family, ())
        for relative in content:
            path = entry(relative)
            if path is not None and path.is_dir():
                result["content_roots"].append(relative)
        if paths:
            selected = []
            for relative in paths:
                path = entry(relative)
                if path is None:
                    raise ConfigError(f"code-root: explicit scope does not exist: {relative}")
                name = path.relative_to(root).as_posix()
                if name not in selected:
                    selected.append(name)
            result.update(roots=selected, source="explicit scope", resolution="resolved")
        elif family:
            candidates = {"godot": ("src",), "unity": ("Assets", "Packages"),
                          "unreal": ("Source", "Plugins")}[family]
            primary = entry(candidates[0])
            if primary is None or not primary.is_dir():
                result["reason"] = "Conventional source directory is absent; inspect the project layout and supply its actual scope. Content-only projects need separate content assessment."
                return result
            selected = [candidates[0]]
            for relative in candidates[1:]:
                path = entry(relative)
                if path is not None and path.is_dir():
                    selected.append(relative)
            result.update(roots=selected, resolution="resolved")
        else:
            result["reason"] = "No configured engine or unambiguous project marker; directory names alone do not establish an engine."
            return result
        result["reason"] = "Paths resolved; no source, content or runtime check has run."
        result["notes"].append("Scope covers only the listed paths. Reconcile custom layouts, embedded packages and plugins before claiming whole-project coverage; exclude third-party/generated code explicitly, never silently.")
    except (ConfigError, OSError, UnicodeError) as error:
        result.update(status="invalid", resolution="unresolved", roots=[], content_roots=[], errors=[str(error)])
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    sub = parser.add_subparsers(dest="command", required=True)
    view = sub.add_parser("resolve")
    view.add_argument("--key")
    view.add_argument("--system")
    preview = sub.add_parser("preview")
    preview.add_argument("--set", action="append", required=True, dest="assignments")
    preview.add_argument("--local", action="store_true")
    preview.add_argument("--system")
    routing = sub.add_parser("review-mode")
    routing.add_argument("--review")
    routing.add_argument("--format", choices=("json", "text"), default="json")
    policy = sub.add_parser("workflow")
    policy.add_argument("--system")
    policy.add_argument("--check-systems", action="store_true")
    stage_view = sub.add_parser("stage")
    stage_view.add_argument("--format", choices=("json", "text"), default="json")
    for command in ("qa-policy", "team-policy", "technical"):
        sub.add_parser(command)
    scope = sub.add_parser("code-root")
    scope.add_argument("--path", action="append", dest="paths",
                       help="explicit existing repository-relative source scope; repeat for multiple paths")
    sub.add_parser("schema")
    args = parser.parse_args()
    if args.command == "schema":
        data = {"schema_version": 1, "fields": SCHEMA, "system_overrides": SYSTEM_PREFIX + "<system>",
                "rigor_expansion": RIGOR, "activation": "preview-only",
                "operational_keys": list(OPERATIONAL_KEYS)}
    elif args.command in ("qa-policy", "team-policy", "technical"):
        data = {"qa-policy": qa_policy, "team-policy": team_policy, "technical": technical}[args.command](args.root)
    elif args.command == "code-root":
        data = code_root(args.root, paths=args.paths)
    elif args.command == "workflow":
        data = workflow(args.root, system=args.system, check_systems=args.check_systems)
    elif args.command in ("review-mode", "stage"):
        data = review_mode(args.root, review=args.review) if args.command == "review-mode" else stage(args.root)
        if args.format == "text":
            if data["status"] != "ready":
                print("INVALID")
                print("; ".join(data["errors"]), file=sys.stderr)
                return 2
            print((data["value"] or "unset") + " (" + data["source"] + ")")
            return 0
    else:
        changes = {}
        try:
            for assignment in getattr(args, "assignments", []):
                if "=" not in assignment:
                    raise ConfigError("expected key=value")
                key, value = assignment.split("=", 1)
                if key in changes:
                    raise ConfigError("duplicate preview assignment: " + key)
                changes[key] = scalar(value)
            data = resolve(args.root, system=args.system, overrides=changes,
                           local=getattr(args, "local", False))
            key = getattr(args, "key", None)
            if key and data["status"] == "ready":
                if key not in data["settings"]:
                    raise ConfigError("unknown setting " + key)
                data["settings"] = {key: data["settings"][key]}
        except ConfigError as error:
            data = {"status": "invalid", "activation": "preview-only", "applied": False,
                    "operational_keys": list(OPERATIONAL_KEYS), "settings": {}, "errors": [str(error)]}
    print(json.dumps(data, indent=2, sort_keys=True))
    return 2 if data.get("status") == "invalid" else 0


if __name__ == "__main__":
    raise SystemExit(main())
