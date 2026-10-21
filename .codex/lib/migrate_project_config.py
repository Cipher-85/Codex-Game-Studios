#!/usr/bin/env python3
"""Preview or explicitly stage project-owned config; never execute its consumers."""
from __future__ import annotations

import argparse
from contextlib import contextmanager
import difflib
import fcntl
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import tempfile

import project_config as config


BACKUPS = ".codex/backups/config-migration"
INPUTS = ("project.yaml", "project.local.yaml", ".gitignore",
          "production/review-mode.txt", "production/stage.txt",
          ".codex/docs/technical-preferences.md")
TARGETS = ("project.yaml", ".gitignore")
START = "# BEGIN CCGS CODEX PORT GITIGNORE"
END = "# END CCGS CODEX PORT GITIGNORE"
LIMIT = 131072
DERIVED = {"plan_id", "transaction", "transaction_files", "temporary_files"}


class MigrationError(ValueError):
    pass


def digest(data):
    return hashlib.sha256(data).hexdigest()


def fingerprint(value):
    return digest(json.dumps(value, sort_keys=True, separators=(",", ":")).encode())


def safe_path(root, relative):
    """Only fixed package-relative paths or validated transaction paths reach here."""
    path = root
    for part in Path(relative).parts:
        if part in ("..", "/"):
            raise MigrationError("unsafe relative path")
        path /= part
        if path.is_symlink():
            raise MigrationError(f"{relative}: symlink paths are unsupported")
        if path != root / relative and path.exists() and not path.is_dir():
            raise MigrationError(f"{relative}: parent is not a directory")
    return path


def state(data, mode):
    return {"exists": True, "sha256": digest(data), "mode": mode}


def snapshot(root, relative, limit=LIMIT):
    path = safe_path(root, relative)
    if not path.exists():
        return {"exists": False}, None
    info = path.stat()
    if not stat.S_ISREG(info.st_mode) or info.st_size > limit:
        raise MigrationError(f"{relative}: expected a regular file of at most {limit} bytes")
    mode = stat.S_IMODE(info.st_mode)
    if mode & 0o7000:
        raise MigrationError(f"{relative}: special permission bits are unsupported")
    data = path.read_bytes()
    if len(data) > limit:
        raise MigrationError(f"{relative}: file grew beyond the size limit")
    return state(data, mode), data


def tools_hash():
    return {name: digest(Path(__file__).with_name(name).read_bytes())
            for name in ("migrate_project_config.py", "project_config.py")}


def history(root):
    parent = safe_path(root, BACKUPS)
    if not parent.exists():
        return []
    if not parent.is_dir():
        raise MigrationError(f"{BACKUPS}: expected directory")
    result = []
    for path in parent.iterdir():
        if path.is_symlink():
            raise MigrationError(f"{path.relative_to(root)}: symlink paths are unsupported")
        if path.name == "transaction.lock" and path.is_file():
            continue
        if not re.fullmatch(r"[0-9a-f]{64}", path.name) or not path.is_dir():
            raise MigrationError(f"{path.relative_to(root)}: unexpected migration history entry")
        result.append(path.name)
        if len(result) > 1000:
            raise MigrationError("migration history exceeds 1000 transactions; review/archive manually")
        _, data = snapshot(root, str(path.relative_to(root)) + "/receipt.json", limit=1048576)
        try:
            receipt = json.loads(data) if data is not None else None
        except (ValueError, RecursionError) as error:
            raise MigrationError(f"{path.relative_to(root)}: invalid journal; inspect retained backups") from error
        if not isinstance(receipt, dict) or receipt.get("status") not in (
            "staged", "rolled_back", "failed_rolled_back"
        ):
            raise MigrationError(f"{path.relative_to(root)}: unfinished or missing journal; recover before new staging")
    return sorted(result)


def ignore_content(data):
    text = data.decode("utf-8-sig") if data is not None else ""
    lines = text.splitlines()
    inside = False
    outside = []
    starts = ends = 0
    for line in lines:
        if line == START:
            starts += 1
            if inside or starts > 1:
                raise MigrationError(".gitignore: duplicate or nested managed block")
            inside = True
        elif line == END:
            ends += 1
            if not inside:
                raise MigrationError(".gitignore: unmatched managed block end")
            inside = False
        elif not inside and line.strip() and not line.startswith("#"):
            outside.append(line)
        elif inside and line.strip() and not line.startswith("#"):
            # A later managed rule could negate an earlier project-owned rule.
            outside.append(None)
    if inside or starts != ends:
        raise MigrationError(".gitignore: unfinished managed block")
    if outside and outside[-1] == "/project.local.yaml":
        return data
    newline = b"\r\n" if data and b"\r\n" in data else b"\n"
    content = data or b""
    if content and not content.endswith(b"\n"):
        content += newline
    return content + newline.join((b"# CCGS project-owned local settings", b"/project.local.yaml", b""))


def yaml_content(mapped):
    tree = {"schema_version": 1}
    for key, entry in sorted(mapped.items()):
        section, leaf = key.split(".")
        tree.setdefault(section, {})[leaf] = entry["value"]
    lines = ["# Project-owned CCGS config; inspect operational_keys before using its consumers."]
    for key, value in tree.items():
        if isinstance(value, dict):
            lines.append(key + ":")
            lines.extend("  " + leaf + ": " + json.dumps(item, ensure_ascii=False)
                         for leaf, item in value.items())
        else:
            lines.append(key + ": " + str(value))
    return ("\n".join(lines) + "\n").encode()


def plan(root):
    root = Path(root).resolve()
    result = {"root": str(root), "status": "blocked", "activation": "preview-only",
              "applied": False, "operational_keys": list(config.OPERATIONAL_KEYS),
              "inputs": {}, "tools": tools_hash(), "history": [],
              "mapped": {}, "unmapped": [], "conflicts": [], "changes": [], "errors": [],
              "notes": ["Staged operational keys affect their subsequent consumers; other settings remain candidates. This transaction runs no workflow.",
                        "No rigor tier or separate engine version is inferred. Local YAML is never written."]}
    try:
        if not root.is_dir():
            raise MigrationError("project root is not a directory")
        result["history"] = history(root)
        contents = {}
        for relative in INPUTS:
            result["inputs"][relative], contents[relative] = snapshot(root, relative)
        resolved = config.resolve(root)
        if resolved["status"] != "ready":
            raise MigrationError("; ".join(resolved["errors"]))
        base, exists = config.load_config(root, "project.yaml")
        mapped, prose = config.legacy_values(root)
        prefs = config.read_file(root, ".codex/docs/technical-preferences.md") or ""
        for label in ("Engine", "Language"):
            if len(re.findall(r"^- \*\*" + label + r"\*\*:", prefs, re.M)) > 1:
                raise MigrationError(f"technical-preferences.md: ambiguous repeated {label} lines")
        result["mapped"] = mapped
        if prose:
            result["unmapped"].append({"path": ".codex/docs/technical-preferences.md",
                                      "reason": "Only supported literal technical fields map. Custom prose, required tests and specialist routing stay authoritative and are never removed."})
        for key, entry in mapped.items():
            if base.get(key) is not None and base[key] != entry["value"]:
                result["conflicts"].append({"key": key, "project": base[key], "legacy": entry})
        if result["conflicts"]:
            raise MigrationError("project.yaml conflicts with legacy fields; resolve explicitly before staging")
        proposed = {}
        if not exists:
            proposed["project.yaml"] = yaml_content(mapped)
        else:
            result["notes"].append("Existing project.yaml is preserved byte for byte; missing fields retain legacy fallback.")
        ignored = ignore_content(contents[".gitignore"])
        if ignored != contents[".gitignore"]:
            proposed[".gitignore"] = ignored
        for relative, content in proposed.items():
            if len(content) > LIMIT:
                raise MigrationError(f"{relative}: proposed content exceeds 128 KiB")
            before = result["inputs"][relative]
            mode = before.get("mode", 0o644)
            result["changes"].append({
                "path": relative, "action": "replace" if before["exists"] else "create",
                "before": before, "after": state(content, mode), "content": content.decode("utf-8"),
                "diff": "".join(difflib.unified_diff(
                    (contents[relative] or b"").decode("utf-8").splitlines(keepends=True),
                    content.decode("utf-8").splitlines(keepends=True),
                    fromfile=relative + " (before)", tofile=relative + " (staged)")),
            })
        result["status"] = "ready" if result["changes"] else "noop"
    except (MigrationError, config.ConfigError, OSError, UnicodeError) as error:
        result.update(status="blocked", changes=[], errors=[str(error)])
    result["plan_id"] = fingerprint(result)
    result["transaction"] = BACKUPS + "/" + result["plan_id"]
    result["transaction_files"] = ([result["transaction"] + "/receipt.json", BACKUPS + "/transaction.lock"] +
                                   [result["transaction"] + f"/before-{i}" for i, c in enumerate(result["changes"]) if c["before"]["exists"]]) if result["changes"] else []
    result["temporary_files"] = ["<changed-file-parent>/.ccgs-config-*.tmp (removed after replacement)"] if result["changes"] else []
    return result


def atomic_write(path, data, mode):
    """Same-directory replacement, with flushed contents and original file mode."""
    fd, temporary = tempfile.mkstemp(prefix=".ccgs-config-", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(data)
            os.fchmod(stream.fileno(), mode)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


@contextmanager
def transaction_lock(root):
    parent = safe_path(root, BACKUPS)
    parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    path = safe_path(root, BACKUPS + "/transaction.lock")
    descriptor = os.open(path, os.O_CREAT | os.O_RDWR | os.O_NOFOLLOW | os.O_NONBLOCK, 0o600)
    try:
        if not stat.S_ISREG(os.fstat(descriptor).st_mode):
            raise MigrationError("transaction lock is not a regular file")
        try:
            fcntl.flock(descriptor, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as error:
            raise MigrationError("another configuration transaction holds the lock") from error
        yield
    finally:
        os.close(descriptor)


def write_receipt(root, transaction, receipt):
    path = safe_path(root, transaction + "/receipt.json")
    atomic_write(path, (json.dumps(receipt, indent=2, sort_keys=True) + "\n").encode(), 0o600)


def restore(root, proposal, transaction):
    """Restore only known before/after states, checking all targets before any edit."""
    for change in proposal["changes"]:
        current, _ = snapshot(root, change["path"])
        if current not in (change["before"], change["after"]):
            raise MigrationError(change["path"] + ": later edits prevent recovery")
    for i in reversed(range(len(proposal["changes"]))):
        change = proposal["changes"][i]
        current, _ = snapshot(root, change["path"])
        if current == change["before"]:
            continue
        if current != change["after"]:
            raise MigrationError(change["path"] + ": changed during recovery")
        path = safe_path(root, change["path"])
        if change["before"]["exists"]:
            _, data = snapshot(root, transaction + f"/before-{i}")
            if data is None or digest(data) != change["before"]["sha256"]:
                raise MigrationError("missing or changed backup for " + change["path"])
            atomic_write(path, data, change["before"]["mode"])
        else:
            path.unlink()
        if snapshot(root, change["path"])[0] != change["before"]:
            raise MigrationError(change["path"] + ": restore verification failed")


def outcome(status, **kwargs):
    return {"status": status, "activation": "preview-only", "applied": False,
            "operational_keys": list(config.OPERATIONAL_KEYS), **kwargs}


def apply(root, expected):
    root = Path(root).resolve()
    proposal = plan(root)
    if proposal["plan_id"] != expected:
        return outcome("blocked", errors=["Stale or wrong-root plan; preview and approve the current plan again."])
    if proposal["status"] in ("blocked", "noop"):
        return outcome(proposal["status"], errors=proposal["errors"])
    transaction = proposal["transaction"]
    try:
        with transaction_lock(root):
            if plan(root) != proposal:
                raise MigrationError("inputs changed while acquiring the lock; preview again")
            directory = safe_path(root, transaction)
            directory.mkdir(mode=0o700)
            receipt = {"schema_version": 1, "status": "preparing", "plan": proposal, "errors": []}
            try:
                for i, change in enumerate(proposal["changes"]):
                    current, data = snapshot(root, change["path"])
                    if current != change["before"]:
                        raise MigrationError(change["path"] + ": changed before backup")
                    if data is not None:
                        atomic_write(directory / f"before-{i}", data, 0o600)
                receipt["status"] = "applying"
                write_receipt(root, transaction, receipt)
                # Recheck every source after backup and before the first target write.
                for relative, original in proposal["inputs"].items():
                    if snapshot(root, relative)[0] != original:
                        raise MigrationError(relative + ": changed after approval")
                for change in proposal["changes"]:
                    if snapshot(root, change["path"])[0] != change["before"]:
                        raise MigrationError(change["path"] + ": changed during staging")
                    atomic_write(safe_path(root, change["path"]), change["content"].encode(), change["after"]["mode"])
                    if snapshot(root, change["path"])[0] != change["after"]:
                        raise MigrationError(change["path"] + ": write verification failed")
                receipt["status"] = "staged"
                write_receipt(root, transaction, receipt)
                return outcome("staged", staged=True, transaction=transaction, errors=[])
            except (MigrationError, OSError, UnicodeError) as error:
                receipt["errors"].append(str(error))
                try:
                    restore(root, proposal, transaction)
                    receipt["status"] = "failed_rolled_back"
                except (MigrationError, OSError, UnicodeError) as recovery:
                    receipt["status"] = "recovery_required"
                    receipt["errors"].append(str(recovery))
                try:
                    write_receipt(root, transaction, receipt)
                except (MigrationError, OSError, UnicodeError) as journal:
                    receipt["status"] = "recovery_required"
                    receipt["errors"].append("Cannot persist recovery receipt: " + str(journal))
                return outcome(receipt["status"], transaction=transaction, errors=receipt["errors"])
    except (MigrationError, OSError) as error:
        return outcome("blocked", errors=[str(error)])


def read_receipt(root, transaction):
    if not re.fullmatch(re.escape(BACKUPS) + r"/[0-9a-f]{64}", transaction):
        raise MigrationError("expected the exact config-migration transaction path from the receipt")
    receipt_state, data = snapshot(root, transaction + "/receipt.json", limit=1048576)
    if data is None:
        raise MigrationError("transaction receipt is missing; inspect retained backups manually")
    receipt = json.loads(data)
    if not isinstance(receipt, dict) or receipt.get("schema_version") != 1 or receipt.get("status") not in (
        "applying", "staged", "rolling_back", "recovery_required", "failed_rolled_back", "rolled_back"
    ):
        raise MigrationError("unsupported transaction receipt")
    proposal = receipt["plan"]
    if not isinstance(proposal, dict):
        raise MigrationError("invalid plan in transaction receipt")
    core = {k: v for k, v in proposal.items() if k not in DERIVED}
    if (proposal["root"] != str(root) or fingerprint(core) != proposal["plan_id"] or
            transaction != BACKUPS + "/" + proposal["plan_id"] or proposal["transaction"] != transaction):
        raise MigrationError("receipt fingerprint or project root mismatch")
    paths = [c["path"] for c in proposal["changes"]]
    if not paths or paths != [p for p in TARGETS if p in paths]:
        raise MigrationError("receipt contains unexpected or repeated targets")
    backups = {}
    for i, change in enumerate(proposal["changes"]):
        if (change["before"] != proposal["inputs"][change["path"]] or
                change["after"] != state(change["content"].encode(), change["after"]["mode"]) or
                (change["path"] == "project.yaml" and change["before"]["exists"])):
            raise MigrationError("receipt contains invalid target states")
        current, _ = snapshot(root, change["path"])
        if current not in (change["before"], change["after"]):
            raise MigrationError(change["path"] + ": later edits prevent rollback")
        if receipt["status"] == "staged" and current != change["after"]:
            raise MigrationError(change["path"] + ": staged file was changed or deleted")
        if receipt["status"] in ("rolled_back", "failed_rolled_back") and current != change["before"]:
            raise MigrationError(change["path"] + ": restored file was changed")
        if change["before"]["exists"]:
            name = transaction + f"/before-{i}"
            backup_state, backup = snapshot(root, name)
            backups[name] = backup_state
            if receipt["status"] not in ("rolled_back", "failed_rolled_back") and (
                backup is None or digest(backup) != change["before"]["sha256"]
            ):
                raise MigrationError("missing or changed backup for " + change["path"])
    return receipt, receipt_state, backups


def rollback_plan(root, transaction):
    root = Path(root).resolve()
    result = outcome("blocked", root=str(root), transaction=transaction, changes=[], errors=[])
    try:
        receipt, receipt_state, backups = read_receipt(root, transaction)
        result.update(receipt=receipt_state, backups=backups, tools=tools_hash())
        for i, change in enumerate(receipt["plan"]["changes"]):
            current, content = snapshot(root, change["path"])
            if current != change["before"]:
                restored = snapshot(root, transaction + f"/before-{i}")[1] if change["before"]["exists"] else None
                result["changes"].append({
                    "path": change["path"], "before": current, "after": change["before"],
                    "action": "replace" if restored is not None else "delete",
                    "content": restored.decode("utf-8") if restored is not None else None,
                    "diff": "".join(difflib.unified_diff(
                        (content or b"").decode("utf-8").splitlines(keepends=True),
                        (restored or b"").decode("utf-8").splitlines(keepends=True),
                        fromfile=change["path"] + " (current)", tofile=change["path"] + " (restored)")),
                })
        needs_journal = receipt["status"] not in ("rolled_back", "failed_rolled_back")
        result["status"] = "ready" if result["changes"] or needs_journal else "noop"
        if result["status"] == "ready":
            result["receipt_write"] = transaction + "/receipt.json"
            result["receipt_status"] = {"before": receipt["status"], "after": "rolled_back"}
            result["temporary_files"] = ["<restored-file-parent>/.ccgs-config-*.tmp (removed after replacement)"]
    except (MigrationError, OSError, UnicodeError, ValueError, KeyError, TypeError, AttributeError, RecursionError) as error:
        result.update(status="blocked", changes=[], errors=[str(error)])
    result["plan_id"] = fingerprint(result)
    return result


def rollback(root, transaction, expected):
    root = Path(root).resolve()
    proposal = rollback_plan(root, transaction)
    if proposal["plan_id"] != expected:
        return outcome("blocked", errors=["Stale rollback plan; preview and approve again."])
    if proposal["status"] != "ready":
        return proposal
    try:
        with transaction_lock(root):
            if rollback_plan(root, transaction) != proposal:
                raise MigrationError("rollback inputs changed while acquiring the lock")
            receipt, _, _ = read_receipt(root, transaction)
            try:
                receipt["status"] = "rolling_back"
                write_receipt(root, transaction, receipt)
                restore(root, receipt["plan"], transaction)
                receipt["status"] = "rolled_back"
                write_receipt(root, transaction, receipt)
                return outcome("rolled_back", transaction=transaction, errors=[])
            except (MigrationError, OSError, UnicodeError) as error:
                receipt.update(status="recovery_required", errors=[str(error)])
                try:
                    write_receipt(root, transaction, receipt)
                except (MigrationError, OSError, UnicodeError) as journal:
                    receipt["errors"].append("Cannot persist recovery receipt: " + str(journal))
                return outcome("recovery_required", transaction=transaction, errors=receipt["errors"])
    except (MigrationError, OSError) as error:
        return outcome("blocked", errors=[str(error)])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("plan")
    stage = commands.add_parser("apply")
    stage.add_argument("--expect-plan", required=True)
    for name in ("rollback-plan", "rollback"):
        command = commands.add_parser(name)
        command.add_argument("transaction")
        if name == "rollback":
            command.add_argument("--expect-plan", required=True)
    args = parser.parse_args()
    if args.command == "plan":
        result = plan(args.root)
    elif args.command == "apply":
        result = apply(args.root, args.expect_plan)
    elif args.command == "rollback-plan":
        result = rollback_plan(args.root, args.transaction)
    else:
        result = rollback(args.root, args.transaction, args.expect_plan)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 2 if result["status"] in ("blocked", "failed_rolled_back", "recovery_required") else 0


if __name__ == "__main__":
    raise SystemExit(main())
