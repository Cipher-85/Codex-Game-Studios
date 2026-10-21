#!/usr/bin/env python3
"""Read CCGS artifact facts as JSON; never write files or decide workflow verdicts."""
from __future__ import annotations

import argparse
from collections import Counter
from datetime import date
import hashlib
import json
from pathlib import Path
import re
import sys

# Import the existing section vocabulary without writing an import cache.
sys.dont_write_bytecode = True
from project_config import GDD_SECTIONS


MAX_BYTES = 1024 * 1024
MAX_FILES = 2000
MAX_ENTRIES = 20000
DEFAULTS = {
    "stories": ("production/epics", True, r"story-.*\.md"),
    "adrs": ("docs/architecture", False, r"adr-[0-9]+.*\.md"),
    "gdds": ("design/gdd", False, r".*\.md"),
    "bugs": ("production/qa/bugs", False, r"bug-[0-9]+(?:[-_].*)?\.md"),
}
NON_SYSTEM_GDDS = {"game-concept.md", "systems-index.md", "game-pillars.md",
                   "gameplay-tags.md", "fixture-swap-ledger.md", "entity-registry.md",
                   "sound-bible.md"}


class InputError(ValueError):
    pass


def normalize(value):
    value = re.sub(r"[*_`]", "", value).strip().casefold()
    value = re.sub(r"^\d+[.)]?\s+", "", value)
    return " ".join(value.split())


def placeholder(value):
    value = value.strip()
    return bool(re.fullmatch(r"\[[^\]]*\]", value)) or normalize(value) in {
        "tbd", "todo", "to be designed", "unresolved"}


def safe_path(root, relative):
    """Check path spelling and every parent before any file read."""
    relative = str(relative).replace("\\", "/")
    if (not relative or relative.startswith("/") or
            any(p == ".." or p.startswith(".env") or ":" in p for p in relative.split("/")) or
            any(ord(c) < 32 or ord(c) == 127 for c in relative)):
        raise InputError("expected a non-secret repository-relative path")
    current = root
    for part in Path(relative).parts:
        current = next((p for p in current.iterdir() if p.name == part), None)
        if current is None:
            raise InputError("path does not exist")
        if current.is_symlink():
            raise InputError("symlink paths are unsupported")
    return current


def uncomment(line, inside):
    """Remove HTML comments while preserving literal comment syntax in code spans."""
    output = []
    while line:
        if inside:
            end = line.find("-->")
            if end < 0:
                return "".join(output), True
            line, inside = line[end + 3:], False
            continue
        if line.startswith("<!--"):
            line, inside = line[4:], True
        elif line.startswith("`"):
            run = re.match(r"`+", line)[0]
            end = re.search(r"(?<!`)" + re.escape(run) + r"(?!`)", line[len(run):])
            length = len(run) + end.end() if end else len(run)
            output.append(line[:length])
            line = line[length:]
        else:
            positions = [p for p in (line.find("<!--"), line.find("`")) if p >= 0]
            end = min(positions) if positions else len(line)
            output.append(line[:end])
            line = line[end:]
    return "".join(output), inside


class Markdown:
    """Small reader for CCGS headings/fields, not a Markdown renderer."""
    def __init__(self, path, text):
        self.path = path
        self.rows, self.sections, self.diagnostics = [], {}, []
        fence, inside = None, False
        for number, raw in enumerate(text.splitlines(), 1):
            # Quoted fences are examples too; quoted metadata in the preamble is valid.
            probe = re.sub(r"^ {0,3}> ?", "", raw)
            if fence:
                closing = re.fullmatch(r" {0,3}" + re.escape(fence[0]) + "{" + str(fence[1]) + r",}\s*", probe)
                if closing:
                    fence = None
                self.rows.append({"line": number, "text": "" if closing else raw,
                                  "code": True, "heading": None})
                continue
            line, inside = uncomment(raw, inside)
            probe = re.sub(r"^ {0,3}> ?", "", line)
            opening = re.match(r"^ {0,3}(`{3,}|~{3,})", probe)
            if opening:
                run = opening[1]
                fence = (run[0], len(run))
            self.rows.append({"line": number, "text": "" if opening else line,
                              "code": bool(opening or line.startswith(("    ", "\t"))),
                              "heading": None})
        if fence or inside:
            self.note("unterminated_fence" if fence else "unterminated_comment", len(self.rows))
        current, preamble = None, True
        for i, row in enumerate(self.rows):
            if not row["code"]:
                heading = re.match(r"^ {0,3}(#{1,6})(?:[ \t]+(.*?)|\s*)$", row["text"])
                level, title = (len(heading[1]), heading[2] or "") if heading else (None, None)
                if title is not None:
                    title = re.sub(r"[ \t]+#+[ \t]*$", "", title).rstrip()
                # Setext headings are accepted as well as the shipped ATX form.
                if level is None and row["text"].strip() and i + 1 < len(self.rows):
                    following = self.rows[i + 1]
                    underline = re.fullmatch(r" {0,3}(=+|-+)\s*", following["text"])
                    if underline and not following["code"] and len(underline[1]) >= 3:
                        level, title = (1 if underline[1][0] == "=" else 2), row["text"].strip()
                        following["text"] = ""
                if level:
                    row["heading"] = level
                    row["title"] = title
                    if level <= 2:
                        current = None
                    if level == 2:
                        preamble = False
                        key = normalize(title)
                        current = {"line": row["line"], "title": title, "body": []}
                        self.sections.setdefault(key, []).append(current)
            row["preamble"] = preamble
            row["section"] = normalize(current["title"]) if current else None
            if current and not row["heading"]:
                current["body"].append(row)

    def note(self, kind, line=None, **details):
        self.diagnostics.append({"path": self.path, "kind": kind, "line": line, **details})

    def field(self, label, sections=None, preamble=False):
        keys = {normalize(x) for x in (label if isinstance(label, tuple) else (label,))}
        occurrences = []
        for row in self.rows:
            if row["code"] or row["heading"]:
                continue
            if not ((preamble and row["preamble"]) or
                    (sections is not None and row["section"] in sections)):
                continue
            text = re.sub(r"^\s*(?:>\s*)?(?:[-*]\s+)?", "", row["text"]).replace("**", "")
            if text.startswith("|"):
                cells = re.split(r"(?<!\\)\|", text)
                key, value = (cells[1], cells[2]) if len(cells) >= 4 else ("", "")
            elif ":" in text:
                key, value = text.split(":", 1)
            else:
                continue
            if normalize(key) in keys:
                occurrences.append({"value": value.strip().strip("*"), "line": row["line"]})
        return self.values(occurrences, next(iter(keys)))

    def values(self, occurrences, label):
        if len(occurrences) > 1:
            self.note("ambiguous_field", occurrences[0]["line"], field=label)
            state, value = "ambiguous", None
        elif not occurrences:
            state, value = "missing", None
        else:
            value = occurrences[0]["value"]
            state = "empty" if not value else "placeholder" if placeholder(value) else "value"
        return {"state": state, "value": value,
                "line": occurrences[0]["line"] if occurrences else None, "occurrences": occurrences}

    def section_field(self, name):
        groups = self.sections.get(normalize(name), [])
        occurrences = []
        for group in groups:
            body = [r for r in group["body"] if not r["code"] and r["text"].strip()]
            joined = "\n".join(r["text"].strip() for r in body)
            if len(body) > 1 and not placeholder(joined):
                occurrences.extend({"value": r["text"].strip(), "line": r["line"]} for r in body)
            else:
                occurrences.append({"value": joined, "line": group["line"]})
        return self.values(occurrences, name)


def calendar_field(doc, field):
    if field["state"] == "value":
        match = re.match(r"^(\d{4}-\d{2}-\d{2})(?:\s|$)", field["value"])
        try:
            field["date"] = date.fromisoformat(match[1]).isoformat() if match else None
            if field["date"] is None:
                raise ValueError()
        except ValueError:
            field["state"] = "invalid"
            doc.note("invalid_date", field["line"])
    return field


def references(doc):
    found = []
    for row in doc.rows:
        if row["code"]:
            continue
        for match in re.finditer(r"\bADR-([0-9]{1,9})(?![0-9])", row["text"], re.I):
            found.append({"id": "ADR-" + str(int(match[1])), "line": row["line"]})
        for match in re.finditer(r"\bTR-[A-Za-z0-9][A-Za-z0-9-]*-[0-9]+\b", row["text"]):
            found.append({"id": match[0], "line": row["line"]})
    return found


def identity(doc, prefix, metadata=None):
    pattern = r"\b" + prefix + r"-([0-9]{1,9})(?![0-9])"
    values = re.findall(pattern, Path(doc.path).name, re.I)
    for row in doc.rows:
        if row["heading"] == 1:
            values.extend(re.findall(pattern, row["title"], re.I))
    if metadata and metadata["state"] == "value":
        values.extend(re.findall(pattern, metadata["value"], re.I))
    ids = {prefix + "-" + str(int(x)) for x in values}
    if len(ids) != 1:
        doc.note("ambiguous_id" if ids else "missing_id", ids=sorted(ids))
        return None
    return next(iter(ids))


def counted_section(doc, name, pattern):
    groups = doc.sections.get(normalize(name), [])
    if len(groups) != 1:
        if groups:
            doc.note("ambiguous_section", groups[0]["line"], section=name)
        return {"state": "ambiguous" if groups else "missing", "line": None, "total": None, "checked": None}
    group = groups[0]
    matches = [re.match(pattern, r["text"].strip()) for r in group["body"] if not r["code"]]
    matches = [m for m in matches if m]
    return {"state": "present", "line": group["line"], "total": len(matches),
            "checked": sum(m[1].casefold() == "x" for m in matches) if name == "Acceptance Criteria" else None}


def story_record(doc):
    fields = {key: doc.field(label, preamble=True) for key, label in
              (("status", "Status"), ("type", "Type"), ("layer", "Layer"), ("estimate", "Estimate"))}
    fields["governing_adrs"] = doc.field(("ADR Governing Implementation", "Governing ADRs", "ADR"),
                                         sections={"context"}, preamble=True)
    fields["depends_on"] = doc.field("Depends on", sections={"dependencies"})
    fields["test_evidence"] = doc.field("Status", sections={"test evidence"})
    return {"fields": fields, "references": references(doc),
            "acceptance_criteria": counted_section(doc, "Acceptance Criteria", r"^[-*] \[([ xX])\]"),
            "qa_cases": counted_section(doc, "QA Test Cases", r"^[-*] \*\*AC-([0-9]+)\*\*")}


def adr_record(doc):
    fields = {"status": doc.section_field("Status"),
              "date": calendar_field(doc, doc.section_field("Date")),
              "last_verified": calendar_field(doc, doc.section_field("Last Verified")),
              "layer": doc.field("Layer", sections=set(doc.sections), preamble=True)}
    # Older ADRs may use a header field instead of a Status section.
    header_status = doc.field("Status", preamble=True)
    if header_status["state"] != "missing":
        fields["status"] = doc.values(fields["status"]["occurrences"] + header_status["occurrences"], "status")
    dep = doc.field("Depends On", sections={"adr dependencies", "dependencies"})
    ids = None
    if dep["state"] == "value":
        ids = sorted({r["id"] for r in references(Markdown(doc.path, dep["value"])) if r["id"].startswith("ADR-")})
        if not ids and normalize(dep["value"]).rstrip(".") not in {"none", "no dependencies", "n/a"}:
            dep["state"] = "unknown"
            doc.note("unknown_dependencies", dep["line"])
            ids = None
    return {"id": identity(doc, "ADR"), "fields": fields,
            "dependencies": {**dep, "ids": ids}, "headings": sorted(doc.sections)}


def gdd_record(doc):
    sections = {}
    for label in GDD_SECTIONS:
        aliases = (label, "Detailed Design") if label == "Detailed Rules" else (label,)
        groups = [group for alias in aliases for group in doc.sections.get(normalize(alias), [])]
        if len(groups) > 1:
            state = "ambiguous"
            doc.note("ambiguous_section", groups[0]["line"], section=label)
        elif not groups:
            state = "missing"
        else:
            body = [r["text"].strip() for r in groups[0]["body"] if r["text"].strip()]
            state = "empty" if not body else "placeholder" if all(placeholder(s) for s in body) else "present"
        sections[label] = {"state": state, "lines": [g["line"] for g in groups]}
    return {"sections": sections}


def bug_record(doc, today):
    fields = {key: doc.field(label, sections={"summary"}, preamble=True) for key, label in
              (("id", "ID"), ("title", "Title"), ("status", "Status"), ("severity", "Severity"),
               ("priority", "Priority"), ("reported", "Reported"))}
    fields["system"] = doc.field("System", sections={"summary", "classification"}, preamble=True)
    calendar_field(doc, fields["reported"])
    reported = fields["reported"].get("date")
    age = (today - date.fromisoformat(reported)).days if reported else None
    if age is not None and age < 0:
        doc.note("future_reported_date", fields["reported"]["line"])
    severity = fields["severity"]
    match = re.match(r"^S([1-4])(?:\b|[-–—])", severity["value"], re.I) if severity["state"] == "value" else None
    return {"id": identity(doc, "BUG", fields["id"]), "fields": fields,
            "severity": "S" + match[1] if match else None, "age_days": age}


def dependency_graph(records):
    counts = Counter(r["id"] for r in records if r["id"])
    duplicates = sorted(key for key, count in counts.items() if count > 1)
    nodes = {r["id"]: r for r in records if r["id"] and counts[r["id"]] == 1}
    edges, unknown, missing = [], [], set()
    adjacency = {node: set() for node in nodes}
    for node, row in nodes.items():
        dep = row["dependencies"]
        if dep["state"] != "value" or dep["ids"] is None:
            unknown.append(node)
            continue
        for target in dep["ids"]:
            edges.append([node, target])
            if target in nodes:
                adjacency[node].add(target)
            else:
                missing.add(target)
    # Iterative Kosaraju: self-loops survive, and deep chains do not recurse.
    reverse = {node: set() for node in nodes}
    for node, targets in adjacency.items():
        for target in targets:
            reverse[target].add(node)
    seen, finish = set(), []
    for node in sorted(nodes):
        stack = [(node, False)]
        while stack:
            current, expanded = stack.pop()
            if expanded:
                finish.append(current)
            elif current not in seen:
                seen.add(current)
                stack.append((current, True))
                stack.extend((target, False) for target in sorted(adjacency[current], reverse=True) if target not in seen)
    seen, cycles = set(), []
    for node in reversed(finish):
        if node in seen:
            continue
        group, stack = [], [node]
        seen.add(node)
        while stack:
            current = stack.pop()
            group.append(current)
            for target in reverse[current] - seen:
                seen.add(target)
                stack.append(target)
        if len(group) > 1 or node in adjacency[node]:
            cycles.append(sorted(group))
    on_cycle = {node for group in cycles for node in group}
    blocked, stack = set(on_cycle), list(on_cycle)
    while stack:
        current = stack.pop()
        for target in reverse[current] - blocked:
            blocked.add(target)
            stack.append(target)
    complete = bool(records) and not duplicates and not unknown and not missing and all(r["id"] for r in records)
    order = None
    if complete and not cycles:
        pending, order = set(nodes), []
        while pending:
            layer = sorted(node for node in pending if not adjacency[node] & pending)
            order.extend(layer)
            pending.difference_update(layer)
    return {"complete": complete, "nodes": sorted(nodes), "edges": sorted(edges),
            "duplicate_ids": duplicates, "unknown_dependencies": sorted(unknown),
            "missing": sorted(missing), "cycles": sorted(cycles),
            "cycle_state": "found" if cycles else "none_detected" if complete else "NOT ASSESSED",
            "blocked_by_cycle": sorted(blocked - on_cycle), "order": order}


def inspect_artifacts(root, kind, paths=None, today=None):
    result = {"schema_version": 1, "root": str(root), "kind": kind, "status": "invalid",
              "applied": False, "assessment": "NOT ASSESSED", "files_discovered": 0,
              "files_read": 0, "records": [], "errors": [], "diagnostics": [], "excluded": []}
    try:
        root = Path(root).resolve(strict=True)
        if not root.is_dir() or kind not in DEFAULTS:
            raise InputError("expected a project directory and supported artifact kind")
        result["root"] = str(root)
        current_date = date.fromisoformat(today) if today else date.today()
        files = []
        if paths:
            result["scope"] = {"mode": "explicit", "paths": [str(p) for p in paths]}
            for relative in paths:
                try:
                    path = safe_path(root, relative)
                    if not path.is_file():
                        raise InputError("explicit artifact must be a regular file")
                    if path not in files:
                        files.append(path)
                except (InputError, OSError) as error:
                    result["errors"].append({"path": str(relative), "error": str(error)})
        else:
            relative, recursive, pattern = DEFAULTS[kind]
            result["scope"] = {"mode": "discovered", "directory": relative, "recursive": recursive}
            try:
                folder = safe_path(root, relative)
            except InputError as error:
                if str(error) != "path does not exist":
                    raise
                folder = None
            queue, entries = ([folder] if folder else []), 0
            result["scope"]["present"] = folder is not None
            while queue:
                for path in sorted(queue.pop().iterdir()):
                    entries += 1
                    if entries > MAX_ENTRIES:
                        raise InputError("artifact discovery exceeds entry limit")
                    relative = path.relative_to(root).as_posix()
                    if path.name.startswith(".env") or path.name == ".git":
                        result["excluded"].append({"path": relative, "reason": "protected path"})
                    elif path.is_symlink():
                        result["errors"].append({"path": relative, "error": "symlink paths are unsupported"})
                    elif path.is_dir():
                        if recursive:
                            queue.append(path)
                    elif re.fullmatch(pattern, path.name, re.I) and path.is_file():
                        if kind == "gdds" and (path.name.casefold() in NON_SYSTEM_GDDS or path.name.casefold().startswith("gdd-cross-review-")):
                            result["excluded"].append({"path": relative, "reason": "not a system GDD"})
                        else:
                            files.append(path)
        if len(files) > MAX_FILES:
            raise InputError("artifact scope exceeds file limit")
        result["files_discovered"] = len(files)
        for path in sorted(files):
            relative = path.relative_to(root).as_posix()
            try:
                path = safe_path(root, relative)
                if not path.is_file() or path.stat().st_size > MAX_BYTES:
                    raise InputError("expected a regular artifact of at most 1 MiB")
                with path.open("rb") as source:
                    raw = source.read(MAX_BYTES + 1)
                if len(raw) > MAX_BYTES:
                    raise InputError("artifact exceeds 1 MiB")
                doc = Markdown(relative, raw.decode("utf-8-sig"))
                if not raw.strip():
                    doc.note("empty_artifact")
                row = {"path": relative, "sha256": hashlib.sha256(raw).hexdigest()}
                if kind == "stories":
                    row.update(story_record(doc))
                elif kind == "adrs":
                    row.update(adr_record(doc))
                elif kind == "gdds":
                    row.update(gdd_record(doc))
                else:
                    row.update(bug_record(doc, current_date))
                row["diagnostics"] = doc.diagnostics
                result["diagnostics"].extend(doc.diagnostics)
                result["records"].append(row)
            except (InputError, OSError, UnicodeError) as error:
                result["errors"].append({"path": relative, "error": str(error)})
        result["files_read"] = len(result["records"])
        if kind == "adrs":
            result["graph"] = dependency_graph(result["records"])
            for field in ("duplicate_ids", "missing", "unknown_dependencies"):
                if result["graph"][field]:
                    result["diagnostics"].append({"kind": "graph_" + field, "ids": result["graph"][field]})
            if result["errors"] or result["diagnostics"]:
                result["graph"].update(complete=False, order=None)
                if not result["graph"]["cycles"]:
                    result["graph"]["cycle_state"] = "NOT ASSESSED"
        if kind in ("stories", "bugs", "adrs"):
            counts = Counter(r["fields"]["status"]["value"] if r["fields"]["status"]["state"] == "value"
                             else "<" + r["fields"]["status"]["state"] + ">" for r in result["records"])
            result["summary"] = {"statuses": dict(sorted(counts.items()))}
            if kind == "bugs":
                result["summary"]["severities"] = dict(sorted(Counter(
                    r["severity"] or "<unknown>" for r in result["records"]).items()))
        result["status"] = ("partial" if result["records"] else "invalid") if result["errors"] else (
            "partial" if result["diagnostics"] else "observed" if result["records"] else "empty")
    except (InputError, OSError, ValueError) as error:
        result["errors"].append({"error": str(error)})
        result["status"] = "invalid"
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    commands = parser.add_subparsers(dest="kind", required=True)
    for kind in DEFAULTS:
        command = commands.add_parser(kind)
        command.add_argument("paths", nargs="*", help="exact repository-relative artifact files")
        if kind == "bugs":
            command.add_argument("--today", help="ISO date for reproducible age calculations")
    args = parser.parse_args()
    result = inspect_artifacts(args.root, args.kind, args.paths, getattr(args, "today", None))
    print(json.dumps(result, indent=2, sort_keys=True))
    return 2 if result["status"] in ("invalid", "partial") else 0


if __name__ == "__main__":
    raise SystemExit(main())
