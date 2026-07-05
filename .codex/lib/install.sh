#!/usr/bin/env bash
set -euo pipefail

ccgs_install_root="${CCGS_INSTALL_ROOT:-$(pwd)}"
ccgs_source_root="${CCGS_SOURCE_ROOT:-$ccgs_install_root}"
ccgs_dry_run="${CCGS_DRY_RUN:-0}"
ccgs_marker_start="<!-- BEGIN CCGS CODEX PORT -->"
ccgs_marker_end="<!-- END CCGS CODEX PORT -->"
ccgs_migrated_start="<!-- BEGIN CCGS MIGRATED LEGACY INSTRUCTIONS -->"
ccgs_migrated_end="<!-- END CCGS MIGRATED LEGACY INSTRUCTIONS -->"
ccgs_gitignore_start="# BEGIN CCGS CODEX PORT GITIGNORE"
ccgs_gitignore_end="# END CCGS CODEX PORT GITIGNORE"
ccgs_install_state_rel=".codex/manifest/install-state.json"
ccgs_install_state_schema_version=2

ccgs_refuse_claude_path() {
  local path="$1"
  case "$path" in
    .codex/tests/*)
      return 0
      ;;
  esac
  case "$path" in
    .claude/*|CLAUDE.md|*/.claude/*|*/CLAUDE.md)
      printf 'refusing to modify Claude-owned path: %s\n' "$path" >&2
      exit 1
      ;;
  esac
}

ccgs_backup_file() {
  local path="$1"
  local target_file="$ccgs_install_root/$path"
  [ -f "$target_file" ] || return 0
  local stamp
  stamp="$(date -u +%Y%m%dT%H%M%SZ)"
  local backup_dir="$ccgs_install_root/.codex/backups/$stamp"
  mkdir -p "$backup_dir/$(dirname "$path")"
  cp "$target_file" "$backup_dir/$path"
}

ccgs_backup_if_modified_before_remove() {
  local path="$1"
  local source_file="$ccgs_source_root/$path"
  local target_file="$ccgs_install_root/$path"
  [ -f "$target_file" ] || return 0
  if [ ! -f "$source_file" ] || ! cmp -s "$source_file" "$target_file"; then
    ccgs_backup_file "$path"
  fi
}

ccgs_claude_guardrail_signals() {
  [ -f "$ccgs_install_root/CLAUDE.md" ] && printf 'CLAUDE.md\n'
  [ -f "$ccgs_install_root/claude.md" ] && printf 'claude.md\n'
  [ -d "$ccgs_install_root/.claude" ] && printf '.claude/\n'
  return 0
}

ccgs_shared_signature_candidates() {
  cat <<'EOF'
CCGS Skill Testing Framework
docs/WORKFLOW-GUIDE.md
docs/COLLABORATIVE-DESIGN-PRINCIPLE.md
docs/engine-reference
design/registry/entities.yaml
production/session-state
.claude/skills
.claude/agents
EOF
}

ccgs_shared_signature_paths() {
  while IFS= read -r path; do
    [ -e "$ccgs_install_root/$path" ] && printf '%s\n' "$path"
  done < <(ccgs_shared_signature_candidates)
  return 0
}

ccgs_detect_mode() {
  local guardrails signatures
  guardrails="$(ccgs_claude_guardrail_signals || true)"
  signatures="$(ccgs_shared_signature_paths || true)"
  if [ -z "$guardrails" ]; then
    printf 'codex_only\n'
  elif [ -n "$signatures" ]; then
    printf 'claude_ccgs_coexist\n'
  else
    printf 'claude_present_no_ccgs\n'
  fi
}

ccgs_package_version() {
  tr -d '[:space:]' < "$ccgs_source_root/.codex/VERSION"
}

ccgs_package_commit() {
  if git -C "$ccgs_source_root" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    git -C "$ccgs_source_root" rev-parse --short=12 HEAD 2>/dev/null || printf 'unknown\n'
  else
    printf 'unknown\n'
  fi
}

ccgs_install_state_schema() {
  local state_file="$ccgs_install_root/$ccgs_install_state_rel"
  [ -f "$state_file" ] || return 1
  python3 - "$state_file" <<'PY'
import json, sys
from pathlib import Path
try:
    print(json.loads(Path(sys.argv[1]).read_text(encoding="utf-8")).get("schema_version", ""))
except Exception:
    raise SystemExit(1)
PY
}

ccgs_select_patch_mode() {
  if [ -n "${CCGS_REQUESTED_PATCH_MODE:-}" ]; then
    case "$CCGS_REQUESTED_PATCH_MODE" in
      incremental|full)
        printf '%s\n' "$CCGS_REQUESTED_PATCH_MODE"
        return 0
        ;;
      *)
        printf 'unsupported patch mode: %s\n' "$CCGS_REQUESTED_PATCH_MODE" >&2
        return 2
        ;;
    esac
  fi

  local state_file schema
  state_file="$ccgs_install_root/$ccgs_install_state_rel"
  if [ ! -f "$state_file" ]; then
    printf 'full\n'
    return 0
  fi
  schema="$(ccgs_install_state_schema || true)"
  if [ "$schema" = "$ccgs_install_state_schema_version" ]; then
    printf 'incremental\n'
  else
    printf 'full\n'
  fi
}

ccgs_install_mode() {
  if [ -n "${CCGS_INSTALL_MODE:-}" ]; then
    printf '%s\n' "$CCGS_INSTALL_MODE"
  elif [ -f "$ccgs_install_root/$ccgs_install_state_rel" ]; then
    local mode
    mode="$(python3 - "$ccgs_install_root/$ccgs_install_state_rel" <<'PY'
import json, sys
from pathlib import Path
try:
    print(json.loads(Path(sys.argv[1]).read_text(encoding="utf-8")).get("detected_mode", ""))
except Exception:
    print("")
PY
)"
    if [ -n "$mode" ]; then
      printf '%s\n' "$mode"
    else
      ccgs_detect_mode
    fi
  else
    ccgs_detect_mode
  fi
}

ccgs_shared_manifest_path() {
  local path="$1"
  case "$path" in
    ATTRIBUTION.md|README.md|CCGS\ Skill\ Testing\ Framework/*|design/registry/*|docs/WORKFLOW-GUIDE.md|docs/COLLABORATIVE-DESIGN-PRINCIPLE.md|docs/architecture/*|docs/engine-reference/*|docs/examples/*|docs/registry/*|production/session-state/*|src/.gitkeep)
      return 0
      ;;
    *)
      return 1
      ;;
  esac
}

ccgs_state_created_shared_paths() {
  local state_file="$ccgs_install_root/$ccgs_install_state_rel"
  [ -f "$state_file" ] || return 0
  python3 - "$state_file" <<'PY'
import json, sys
from pathlib import Path
try:
    data = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
except Exception:
    raise SystemExit(0)
for path in data.get("shared_paths_created_by_codex", []):
    print(path)
PY
}

ccgs_path_in_state_created_shared() {
  local needle="$1"
  while IFS= read -r path; do
    [ "$path" = "$needle" ] && return 0
  done < <(ccgs_state_created_shared_paths)
  return 1
}

ccgs_capture_install_state() {
  local output_file="$1"
  local mode="${CCGS_INSTALL_MODE:-$(ccgs_detect_mode)}"
  local patch_mode="${CCGS_PATCH_MODE:-$(ccgs_select_patch_mode)}"
  local package_version package_commit temp_dir
  package_version="$(ccgs_package_version)"
  package_commit="$(ccgs_package_commit)"
  temp_dir="$(mktemp -d "${TMPDIR:-/tmp}/ccgs-install-state.XXXXXX")"
  ccgs_claude_guardrail_signals > "$temp_dir/guardrails"
  ccgs_shared_signature_paths > "$temp_dir/signatures"
  ccgs_deploy_paths | sort -u > "$temp_dir/deploy-paths"
  : > "$temp_dir/created"
  : > "$temp_dir/preserved"

  while IFS= read -r path; do
    ccgs_shared_manifest_path "$path" || continue
    if [ "$mode" = "claude_ccgs_coexist" ] && [ -e "$ccgs_install_root/$path" ]; then
      printf '%s\n' "$path" >> "$temp_dir/preserved"
    elif [ ! -e "$ccgs_install_root/$path" ]; then
      printf '%s\n' "$path" >> "$temp_dir/created"
    fi
  done < "$temp_dir/deploy-paths"

  python3 - "$output_file" "$mode" "$patch_mode" "$package_version" "$package_commit" "$ccgs_source_root" "$temp_dir/guardrails" "$temp_dir/signatures" "$temp_dir/created" "$temp_dir/preserved" "$temp_dir/deploy-paths" "$ccgs_marker_start" "$ccgs_marker_end" <<'PY'
import hashlib
import json, sys
from datetime import datetime, timezone
from pathlib import Path

output = Path(sys.argv[1])
mode = sys.argv[2]
patch_mode = sys.argv[3]
package_version = sys.argv[4]
package_commit = sys.argv[5]
source_root = Path(sys.argv[6])
guardrails = Path(sys.argv[7])
signatures = Path(sys.argv[8])
created = Path(sys.argv[9])
preserved = Path(sys.argv[10])
deploy_paths = Path(sys.argv[11])
marker_start = sys.argv[12]
marker_end = sys.argv[13]

def lines(path: Path) -> list[str]:
    return [line for line in path.read_text(encoding="utf-8").splitlines() if line]

def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def marker_block(text: str, rel: str) -> str:
    start_index = text.find(marker_start)
    end_index = text.find(marker_end)
    if start_index == -1 or end_index == -1 or end_index < start_index:
        raise SystemExit(f"{rel}: missing CCGS marker block")
    end_index += len(marker_end)
    return text[start_index:end_index]

installed_file_hashes = {}
marker_block_hashes = {}
for rel in lines(deploy_paths):
    source_file = source_root / rel
    if not source_file.is_file():
        continue
    data = source_file.read_bytes()
    installed_file_hashes[rel] = sha256_bytes(data)
    if not rel.startswith(".codex/tests/") and (rel == "AGENTS.md" or rel.endswith("/AGENTS.md")):
        marker = marker_block(data.decode("utf-8"), rel)
        marker_block_hashes[rel] = sha256_bytes(marker.encode("utf-8"))

now = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
data = {
    "schema_version": 2,
    "generated_at": now,
    "installed_at": now,
    "detected_mode": mode,
    "patch_mode": patch_mode,
    "ccgs_version": package_version,
    "package_commit": package_commit,
    "claude_guardrail_signals": lines(guardrails),
    "shared_ccgs_asset_signatures_found": lines(signatures),
    "shared_paths_created_by_codex": lines(created),
    "shared_paths_preserved_preexisting": lines(preserved),
    "installed_file_hashes": installed_file_hashes,
    "marker_block_hashes": marker_block_hashes,
}
output.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")
PY
  rm -rf "$temp_dir"
}

ccgs_install_state_file() {
  printf '%s/%s\n' "$ccgs_install_root" "$ccgs_install_state_rel"
}

ccgs_write_install_state() {
  local captured_state="$1"
  local state_file
  state_file="$(ccgs_install_state_file)"
  mkdir -p "$(dirname "$state_file")"
  cp "$captured_state" "$state_file"
}

ccgs_print_state_summary() {
  local state_file="$1"
  local action="$2"
  python3 - "$state_file" "$action" <<'PY'
import json, sys
from pathlib import Path

data = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
action = sys.argv[2]
print(f"{action} mode: {data.get('detected_mode', '<unknown>')}")
print(f"Patch mode: {data.get('patch_mode', '<unknown>')}")
print(f"CCGS version: {data.get('ccgs_version', '<unknown>')}")
print("Claude guardrail signals: " + (", ".join(data.get("claude_guardrail_signals", [])) or "<none>"))
print("Shared CCGS signatures found: " + (", ".join(data.get("shared_ccgs_asset_signatures_found", [])) or "<none>"))
print("Shared paths preserved: " + (", ".join(data.get("shared_paths_preserved_preexisting", [])) or "<none>"))
print("Shared paths created by Codex: " + (", ".join(data.get("shared_paths_created_by_codex", [])) or "<none>"))
PY
}

ccgs_manifest_paths() {
  python3 - "$ccgs_source_root/.codex/manifest/installed-files.json" <<'PY'
import json, sys
from pathlib import Path
path = Path(sys.argv[1])
data = json.loads(path.read_text(encoding="utf-8"))
for row in data:
    print(row["path"])
PY
}

ccgs_deploy_paths() {
  ccgs_manifest_paths
  if [ -d "$ccgs_source_root/.codex/tests" ]; then
    (cd "$ccgs_source_root" && find .codex/tests -type f -print)
  fi
}

ccgs_gitignore_allowlist_paths() {
  ccgs_deploy_paths
  printf '%s\n' "$ccgs_install_state_rel"
}

ccgs_gitignore_allowlist_patterns() {
  local paths_file
  paths_file="$(mktemp "${TMPDIR:-/tmp}/ccgs-gitignore-paths.XXXXXX")"
  ccgs_gitignore_allowlist_paths | sort -u > "$paths_file"
  python3 - "$paths_file" <<'PY'
import sys
from collections import defaultdict
from pathlib import Path

def escape(path: str) -> str:
    return path.replace("\\", "\\\\").replace(" ", "\\ ")

shared_content_roots = {
    ".github",
    "assets",
    "design",
    "docs",
    "production",
    "prototypes",
    "src",
    "tests",
    "tools",
}

def is_shared_content_path(path: str) -> bool:
    return path.split("/", 1)[0] in shared_content_roots

children: dict[str, set[str]] = defaultdict(set)
files_by_dir: dict[str, set[str]] = defaultdict(set)

for raw in Path(sys.argv[1]).read_text(encoding="utf-8").splitlines():
    path = raw.strip()
    if not path:
        continue
    parts = path.split("/")
    parent = ""
    for index, part in enumerate(parts[:-1]):
        current = "/".join(parts[: index + 1])
        children[parent].add(current)
        parent = current
    files_by_dir[parent].add(path)

def emit_dir(path: str) -> None:
    print("!" + escape(path) + "/")
    if not is_shared_content_path(path):
        print(escape(path) + "/*")
    for child in sorted(children.get(path, ())):
        emit_dir(child)
    for file_path in sorted(files_by_dir.get(path, ())):
        print("!" + escape(file_path))

for child in sorted(children.get("", ())):
    emit_dir(child)
for file_path in sorted(files_by_dir.get("", ())):
    print("!" + escape(file_path))
PY
  rm -f "$paths_file"
}

ccgs_gitignore_allowlist_block() {
  printf '%s\n' "$ccgs_gitignore_start"
  printf '# Added by Codex Game Studios so installed repo-local runtime files remain trackable.\n'
  ccgs_gitignore_allowlist_patterns
  printf '%s\n' "$ccgs_gitignore_end"
}

ccgs_update_gitignore_allowlist() {
  local target_file="$ccgs_install_root/.gitignore"
  [ -f "$target_file" ] || return 0

  local block_file
  block_file="$(mktemp "${TMPDIR:-/tmp}/ccgs-gitignore.XXXXXX")"
  ccgs_gitignore_allowlist_block > "$block_file"

  if [ "$ccgs_dry_run" = "1" ]; then
    printf 'would update .gitignore CCGS allowlist\n'
    rm -f "$block_file"
    return 0
  fi

  ccgs_backup_file ".gitignore"
  python3 - "$target_file" "$block_file" "$ccgs_gitignore_start" "$ccgs_gitignore_end" <<'PY'
import sys
from pathlib import Path

target = Path(sys.argv[1])
block = Path(sys.argv[2]).read_text(encoding="utf-8").rstrip() + "\n"
start = sys.argv[3]
end = sys.argv[4]
text = target.read_text(encoding="utf-8") if target.exists() else ""
start_index = text.find(start)
end_index = text.find(end)
if start_index != -1 and end_index != -1 and end_index >= start_index:
    end_index += len(end)
    updated = text[:start_index] + block.rstrip() + text[end_index:]
else:
    separator = "" if not text or text.endswith("\n\n") else "\n\n"
    updated = text + separator + block
target.write_text(updated.rstrip() + "\n", encoding="utf-8")
PY
  rm -f "$block_file"
}

ccgs_check_deployed_gitignore() {
  local target_file="$ccgs_install_root/.gitignore"
  [ -f "$target_file" ] || return 0
  git -C "$ccgs_install_root" rev-parse --is-inside-work-tree >/dev/null 2>&1 || return 0

  local paths_file ignored_file
  paths_file="$(mktemp "${TMPDIR:-/tmp}/ccgs-gitignore-paths.XXXXXX")"
  ignored_file="$(mktemp "${TMPDIR:-/tmp}/ccgs-gitignore-ignored.XXXXXX")"
  while IFS= read -r path; do
    [ -e "$ccgs_install_root/$path" ] && printf '%s\n' "$path"
  done < <(ccgs_gitignore_allowlist_paths | sort -u) > "$paths_file"

  if git -C "$ccgs_install_root" check-ignore --no-index --stdin < "$paths_file" > "$ignored_file"; then
    printf 'deployed CCGS paths are still gitignored after .gitignore update:\n' >&2
    sed 's/^/  /' "$ignored_file" >&2
    rm -f "$paths_file" "$ignored_file"
    return 1
  fi

  rm -f "$paths_file" "$ignored_file"
  return 0
}

ccgs_remove_gitignore_allowlist() {
  local target_file="$ccgs_install_root/.gitignore"
  [ -f "$target_file" ] || return 0

  if [ "$ccgs_dry_run" = "1" ]; then
    if grep -qF "$ccgs_gitignore_start" "$target_file"; then
      printf 'would remove .gitignore CCGS allowlist\n'
    fi
    return 0
  fi

  set +e
  ccgs_remove_named_block "$target_file" "$ccgs_gitignore_start" "$ccgs_gitignore_end"
  local status=$?
  set -e
  [ "$status" -eq 3 ] && return 0
  return "$status"
}

ccgs_obsolete_paths() {
  cat <<'EOF'
assets/data/AGENTS.md
assets/shaders/AGENTS.md
design/AGENTS.md
design/gdd/AGENTS.md
design/narrative/AGENTS.md
docs/AGENTS.md
prototypes/AGENTS.md
src/AGENTS.md
src/ai/AGENTS.md
src/core/AGENTS.md
src/gameplay/AGENTS.md
src/networking/AGENTS.md
src/ui/AGENTS.md
tests/AGENTS.md
tools/AGENTS.md
production/session-logs/agents-start.jsonl
production/session-logs/agents-stop.jsonl
production/session-logs/asset-validation-last.json
production/session-logs/post-compact-last.json
production/session-logs/pre-compact-last.json
production/session-logs/session-start.json
production/session-logs/session-stop.json
production/session-logs/skill-change-last.json
EOF
}

ccgs_verify_manifest_paths() {
  local missing=0
  while IFS= read -r path; do
    ccgs_refuse_claude_path "$path"
    if [ ! -e "$ccgs_install_root/$path" ]; then
      printf 'missing installed path: %s\n' "$path" >&2
      missing=1
    fi
  done < <(ccgs_deploy_paths | sort -u)
  return "$missing"
}

ccgs_extract_marker_block() {
  local source_file="$1"
  python3 - "$source_file" "$ccgs_marker_start" "$ccgs_marker_end" <<'PY'
import sys
from pathlib import Path

path = Path(sys.argv[1])
start = sys.argv[2]
end = sys.argv[3]
text = path.read_text(encoding="utf-8")
start_index = text.find(start)
end_index = text.find(end)
if start_index == -1 or end_index == -1 or end_index < start_index:
    raise SystemExit(f"{path}: missing CCGS marker block")
end_index += len(end)
print(text[start_index:end_index])
PY
}

ccgs_write_marker_block() {
  local target_file="$1"
  local block="$2"
  python3 - "$target_file" "$ccgs_marker_start" "$ccgs_marker_end" "$block" <<'PY'
import sys
from pathlib import Path

path = Path(sys.argv[1])
start = sys.argv[2]
end = sys.argv[3]
block = sys.argv[4].rstrip() + "\n"
text = path.read_text(encoding="utf-8") if path.exists() else ""
start_index = text.find(start)
end_index = text.find(end)
if start_index != -1 and end_index != -1 and end_index >= start_index:
    end_index += len(end)
    updated = text[:start_index] + block.rstrip() + text[end_index:]
else:
    separator = "" if not text or text.endswith("\n\n") else "\n\n"
    updated = text + separator + block
path.parent.mkdir(parents=True, exist_ok=True)
path.write_text(updated.rstrip() + "\n", encoding="utf-8")
PY
}

ccgs_claude_guardrail_file() {
  if [ -f "$ccgs_install_root/CLAUDE.md" ]; then
    printf '%s\n' "$ccgs_install_root/CLAUDE.md"
  elif [ -f "$ccgs_install_root/claude.md" ]; then
    printf '%s\n' "$ccgs_install_root/claude.md"
  fi
}

ccgs_append_migrated_legacy_block() {
  local target_file="$1"
  local legacy_file
  legacy_file="$(ccgs_claude_guardrail_file || true)"
  [ -n "$legacy_file" ] || return 0
  [ -f "$target_file" ] || return 0

  python3 - "$target_file" "$legacy_file" "$ccgs_migrated_start" "$ccgs_migrated_end" <<'PY'
import sys
from pathlib import Path

target = Path(sys.argv[1])
legacy = Path(sys.argv[2])
start = sys.argv[3]
end = sys.argv[4]
text = target.read_text(encoding="utf-8")
if start in text and end in text:
    raise SystemExit(0)

legacy_text = legacy.read_text(encoding="utf-8")
legacy_text = legacy_text.replace(".claude/", "[legacy Claude runtime]/")
legacy_text = legacy_text.replace("CLAUDE.md", "legacy Claude instruction file")
legacy_text = legacy_text.rstrip()

block = f"""{start}
## Migrated Existing Project Instructions

The following project instructions were copied from the preexisting legacy
guardrail file during Codex Game Studios install. Treat them as project guidance
only; do not treat legacy runtime paths or unsupported commands as active Codex
mechanisms.

{legacy_text}
{end}
"""

separator = "\n\n" if text.strip() else ""
target.write_text(text.rstrip() + separator + block, encoding="utf-8")
PY
}

ccgs_write_migrated_legacy_block() {
  local target_file="$1"
  local legacy_file
  legacy_file="$(ccgs_claude_guardrail_file || true)"
  [ -n "$legacy_file" ] || return 0

  mkdir -p "$(dirname "$target_file")"
  : > "$target_file"
  ccgs_append_migrated_legacy_block "$target_file"
}

ccgs_remove_marker_block() {
  local target_file="$1"
  [ -f "$target_file" ] || return 0
  set +e
  python3 - "$target_file" "$ccgs_marker_start" "$ccgs_marker_end" <<'PY'
import sys
from pathlib import Path

path = Path(sys.argv[1])
start = sys.argv[2]
end = sys.argv[3]
text = path.read_text(encoding="utf-8")
start_index = text.find(start)
end_index = text.find(end)
if start_index == -1 or end_index == -1 or end_index < start_index:
    raise SystemExit(3)
end_index += len(end)
updated = (text[:start_index].rstrip() + "\n\n" + text[end_index:].lstrip()).strip()
if updated:
    path.write_text(updated + "\n", encoding="utf-8")
else:
    path.unlink()
PY
  local status=$?
  set -e
  [ "$status" -eq 3 ] && return 3
  return "$status"
}

ccgs_remove_named_block() {
  local target_file="$1"
  local start="$2"
  local end="$3"
  [ -f "$target_file" ] || return 0
  set +e
  python3 - "$target_file" "$start" "$end" <<'PY'
import sys
from pathlib import Path

path = Path(sys.argv[1])
start = sys.argv[2]
end = sys.argv[3]
text = path.read_text(encoding="utf-8")
start_index = text.find(start)
end_index = text.find(end)
if start_index == -1 or end_index == -1 or end_index < start_index:
    raise SystemExit(3)
end_index += len(end)
updated = (text[:start_index].rstrip() + "\n\n" + text[end_index:].lstrip()).strip()
if updated:
    path.write_text(updated + "\n", encoding="utf-8")
else:
    path.unlink()
PY
  local status=$?
  set -e
  [ "$status" -eq 3 ] && return 3
  return "$status"
}

ccgs_remove_agents_stub_if_empty() {
  local target_file="$1"
  [ -f "$target_file" ] || return 0
  local compact
  compact="$(tr -d '\n\r\t ' < "$target_file")"
  if [ -z "$compact" ] || [ "$compact" = "#CodexGameStudiosInstructions" ]; then
    rm -f "$target_file"
  fi
}

ccgs_incremental_source_unchanged() {
  local path="$1"
  [ "${CCGS_PATCH_MODE:-}" = "incremental" ] || return 1
  [ -e "$ccgs_install_root/$path" ] || return 1
  local state_file
  state_file="$(ccgs_install_state_file)"
  [ -f "$state_file" ] || return 1
  python3 - "$state_file" "$ccgs_source_root" "$path" "$ccgs_marker_start" "$ccgs_marker_end" <<'PY'
import hashlib
import json
import sys
from pathlib import Path

state = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
source_root = Path(sys.argv[2])
rel = sys.argv[3]
marker_start = sys.argv[4]
marker_end = sys.argv[5]

if state.get("schema_version") != 2:
    raise SystemExit(1)

source_file = source_root / rel
if not source_file.is_file():
    raise SystemExit(1)

data = source_file.read_bytes()
actual_file_hash = hashlib.sha256(data).hexdigest()
if state.get("installed_file_hashes", {}).get(rel) != actual_file_hash:
    raise SystemExit(1)

if not rel.startswith(".codex/tests/") and (rel == "AGENTS.md" or rel.endswith("/AGENTS.md")):
    text = data.decode("utf-8")
    start_index = text.find(marker_start)
    end_index = text.find(marker_end)
    if start_index == -1 or end_index == -1 or end_index < start_index:
        raise SystemExit(1)
    end_index += len(marker_end)
    marker = text[start_index:end_index].encode("utf-8")
    actual_marker_hash = hashlib.sha256(marker).hexdigest()
    if state.get("marker_block_hashes", {}).get(rel) != actual_marker_hash:
        raise SystemExit(1)

raise SystemExit(0)
PY
}

ccgs_install_file() {
  local path="$1"
  ccgs_refuse_claude_path "$path"
  local source_file="$ccgs_source_root/$path"
  local target_file="$ccgs_install_root/$path"
  local mode
  mode="$(ccgs_install_mode)"
  if [ ! -f "$source_file" ]; then
    printf 'missing source path: %s\n' "$path" >&2
    return 1
  fi

  if ccgs_incremental_source_unchanged "$path"; then
    [ "$ccgs_dry_run" = "1" ] && printf 'would skip unchanged %s\n' "$path"
    return 0
  fi

  if [ "$mode" = "claude_ccgs_coexist" ] && ccgs_shared_manifest_path "$path" && [ -e "$target_file" ]; then
    if [ "$ccgs_dry_run" = "1" ]; then
      printf 'would preserve preexisting shared %s\n' "$path"
    fi
    return 0
  fi

  case "$path" in
    .codex/tests/*)
      if [ "$ccgs_dry_run" = "1" ]; then
        printf 'would install %s\n' "$path"
        return 0
      fi
      if [ -f "$target_file" ] && ! cmp -s "$source_file" "$target_file"; then
        ccgs_backup_file "$path"
      fi
      mkdir -p "$(dirname "$target_file")"
      cp -p "$source_file" "$target_file"
      ;;
    AGENTS.md|*/AGENTS.md)
      if [ "$ccgs_dry_run" = "1" ]; then
        printf 'would install marker-managed %s\n' "$path"
        return 0
      fi
      if [ -f "$target_file" ] && ! cmp -s "$source_file" "$target_file"; then
        ccgs_backup_file "$path"
      fi
      if [ -f "$target_file" ]; then
        local block
        block="$(ccgs_extract_marker_block "$source_file")" || return 1
        ccgs_write_marker_block "$target_file" "$block"
      else
        if [ "$path" = "AGENTS.md" ] && [ "$mode" = "claude_present_no_ccgs" ] && [ -n "$(ccgs_claude_guardrail_file || true)" ]; then
          local block
          block="$(ccgs_extract_marker_block "$source_file")" || return 1
          ccgs_write_migrated_legacy_block "$target_file"
          ccgs_write_marker_block "$target_file" "$block"
        else
          mkdir -p "$(dirname "$target_file")"
          cp -p "$source_file" "$target_file"
        fi
      fi
      ;;
    *)
      if [ "$ccgs_dry_run" = "1" ]; then
        printf 'would install %s\n' "$path"
        return 0
      fi
      if [ -f "$target_file" ] && ! cmp -s "$source_file" "$target_file"; then
        ccgs_backup_file "$path"
      fi
      mkdir -p "$(dirname "$target_file")"
      cp -p "$source_file" "$target_file"
      ;;
  esac
}

ccgs_install_assets() {
  local failed=0
  while IFS= read -r path; do
    ccgs_install_file "$path" || failed=1
  done < <(ccgs_deploy_paths | sort -u)
  ccgs_remove_obsolete_assets || failed=1
  ccgs_prune_empty_dirs
  return "$failed"
}

ccgs_uninstall_file() {
  local path="$1"
  ccgs_refuse_claude_path "$path"
  local target_file="$ccgs_install_root/$path"
  [ -e "$target_file" ] || return 0
  local mode state_file
  mode="$(ccgs_install_mode)"
  state_file="$(ccgs_install_state_file)"

  if [ "$mode" = "claude_ccgs_coexist" ] && ccgs_shared_manifest_path "$path"; then
    if [ -f "$state_file" ]; then
      if ! ccgs_path_in_state_created_shared "$path"; then
        [ "$ccgs_dry_run" = "1" ] && printf 'would preserve preexisting shared %s\n' "$path"
        return 0
      fi
    else
      [ "$ccgs_dry_run" = "1" ] && printf 'would preserve shared %s because install state is missing\n' "$path"
      return 0
    fi
  fi

  if [ "$ccgs_dry_run" = "1" ]; then
    printf 'would remove %s\n' "$path"
    return 0
  fi

  case "$path" in
    .codex/tests/*)
      ccgs_backup_if_modified_before_remove "$path"
      rm -f "$target_file"
      ;;
    AGENTS.md|*/AGENTS.md)
      local source_file="$ccgs_source_root/$path"
      if [ "$ccgs_source_root" != "$ccgs_install_root" ] && [ -f "$source_file" ] && cmp -s "$source_file" "$target_file"; then
        rm -f "$target_file"
      else
        local changed=0
        ccgs_remove_marker_block "$target_file"
        local status=$?
        if [ "$status" -eq 0 ]; then
          changed=1
        elif [ "$status" -ne 3 ]; then
          return "$status"
        fi
        if [ "$path" = "AGENTS.md" ]; then
          ccgs_remove_named_block "$target_file" "$ccgs_migrated_start" "$ccgs_migrated_end"
          status=$?
          if [ "$status" -eq 0 ]; then
            changed=1
          elif [ "$status" -ne 3 ]; then
            return "$status"
          fi
        fi
        if [ "$changed" -eq 0 ]; then
          printf 'leaving unowned instruction file unchanged: %s\n' "$path"
        fi
        if [ "$path" = "AGENTS.md" ]; then
          ccgs_remove_agents_stub_if_empty "$target_file"
        fi
      fi
      ;;
    *)
      ccgs_backup_if_modified_before_remove "$path"
      rm -f "$target_file"
      ;;
  esac
}

ccgs_prune_empty_dirs() {
  [ "$ccgs_dry_run" = "1" ] && return 0
  local mode
  mode="$(ccgs_install_mode)"
  if [ -d "$ccgs_install_root/.codex" ]; then
    find "$ccgs_install_root/.codex" -type d -name __pycache__ -prune -exec rm -rf {} + 2>/dev/null || true
  fi
  local dirs=(".codex" ".agents" "CCGS Skill Testing Framework" "assets" "design" "production" "prototypes" "src" "tests" "tools")
  if [ "$mode" = "claude_ccgs_coexist" ]; then
    dirs=(".codex" ".agents")
  fi
  for dir in "${dirs[@]}"; do
    if [ -d "$ccgs_install_root/$dir" ]; then
      local changed=1
      while [ "$changed" = "1" ]; do
        changed=0
        while IFS= read -r empty_dir; do
          rmdir "$empty_dir" 2>/dev/null && changed=1 || true
        done < <(find "$ccgs_install_root/$dir" -depth -type d -empty 2>/dev/null)
      done
    fi
  done
}

ccgs_remove_obsolete_assets() {
  local failed=0
  while IFS= read -r path; do
    ccgs_refuse_claude_path "$path"
    local target_file="$ccgs_install_root/$path"
    [ -e "$target_file" ] || continue

    if [ "$ccgs_dry_run" = "1" ]; then
      printf 'would remove obsolete %s\n' "$path"
      continue
    fi

    case "$path" in
      */AGENTS.md|AGENTS.md)
        ccgs_remove_marker_block "$target_file"
        local status=$?
        if [ "$status" -eq 3 ] && [ "$(tr -d '\n\r\t ' < "$target_file")" = "#CodexGameStudiosInstructions" ]; then
          rm -f "$target_file"
        elif [ "$status" -ne 0 ] && [ "$status" -ne 3 ]; then
          failed=1
        fi
        ;;
      *)
        if [ ! -s "$target_file" ] || grep -q '"hook_event_name"' "$target_file" 2>/dev/null; then
          rm -f "$target_file"
        fi
        ;;
    esac
  done < <(ccgs_obsolete_paths)
  return "$failed"
}

ccgs_uninstall_assets() {
  local failed=0
  while IFS= read -r path; do
    ccgs_uninstall_file "$path" || failed=1
  done < <(ccgs_deploy_paths | sort -r -u)
  local state_file
  state_file="$(ccgs_install_state_file)"
  if [ -e "$state_file" ]; then
    if [ "$ccgs_dry_run" = "1" ]; then
      printf 'would remove %s\n' "$ccgs_install_state_rel"
    else
      rm -f "$state_file"
    fi
  fi
  ccgs_remove_obsolete_assets || failed=1
  ccgs_prune_empty_dirs
  return "$failed"
}
