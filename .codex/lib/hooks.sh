#!/usr/bin/env bash
set -euo pipefail

ccgs_find_root() {
  if [ -n "${CCGS_ROOT:-}" ]; then
    printf '%s\n' "$CCGS_ROOT"
    return
  fi

  local git_root
  git_root="$(git rev-parse --show-toplevel 2>/dev/null || true)"
  if [ -n "$git_root" ] && [ -d "$git_root/.codex" ]; then
    printf '%s\n' "$git_root"
    return
  fi

  local d
  d="$(pwd -P)"
  while [ "$d" != "/" ]; do
    if [ -d "$d/.codex" ]; then
      printf '%s\n' "$d"
      return
    fi
    d="$(dirname "$d")"
  done

  pwd -P
}

ccgs_root="$(ccgs_find_root)"

ccgs_read_stdin() {
  cat
}

ccgs_json_field() {
  local json="$1"
  local field="$2"
  local python_cmd
  python_cmd="$(ccgs_first_python || true)"
  if [ -z "$python_cmd" ]; then
    printf 'WARNING: Python not found; cannot parse hook JSON field %s. Hook will fail open.\n' "$field" >&2
    printf '\n'
    return 0
  fi

  "$python_cmd" -c 'import json,sys
try:
    data=json.loads(sys.stdin.read() or "{}")
except json.JSONDecodeError:
    data={}
value=data
for part in sys.argv[1].split("."):
    value=value.get(part, "") if isinstance(value, dict) else ""
if value is None:
    value=""
print(value if isinstance(value, str) else json.dumps(value))' "$field" <<<"$json" || {
    printf 'WARNING: Python failed while parsing hook JSON field %s. Hook will fail open.\n' "$field" >&2
    printf '\n'
    return 0
  }
}

ccgs_log_dir() {
  local dir="$ccgs_root/production/session-logs"
  mkdir -p "$dir"
  printf '%s\n' "$dir"
}

ccgs_write_session_baseline() {
  local branch="$1"
  local start_head="$2"
  local started_at="$3"
  local output="$4"
  local python_cmd
  python_cmd="$(ccgs_first_python || true)"
  if [ -z "$python_cmd" ]; then
    printf 'WARNING: Python not found; session review baseline was not recorded.\n' >&2
    return 0
  fi
  "$python_cmd" - "$branch" "$start_head" "$started_at" "$output" <<'PY'
import json
import sys
from pathlib import Path

branch, start_head, started_at, output = sys.argv[1:]
payload = {
    "schema_version": 1,
    "branch": branch or None,
    "start_head": start_head or None,
    "started_at": started_at,
}
Path(output).write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
PY
}

ccgs_active_state_kind() {
  local state_file="$1"
  if [ ! -f "$state_file" ]; then
    printf 'missing\n'
  elif grep -Eq '^## (Current Focus|Phase Guard|Source Freshness|Session Worklist|Owed Before Starting)' "$state_file" 2>/dev/null; then
    printf 'substantive\n'
  else
    printf 'pointer\n'
  fi
}

ccgs_preview_bounded() {
  local file="$1"
  local max_lines="$2"
  local total_lines
  total_lines="$(wc -l < "$file" 2>/dev/null | tr -d ' ' || echo 0)"
  if [ "${total_lines:-0}" -le "$max_lines" ] 2>/dev/null; then
    cat "$file"
    return
  fi

  local first_lines=$((max_lines / 2))
  local last_lines=$((max_lines - first_lines))
  head -n "$first_lines" "$file"
  echo "... (bounded preview - $total_lines total lines)"
  tail -n "$last_lines" "$file"
}

ccgs_relpath() {
  local path="$1"
  path="${path//\\//}"
  path="${path#./}"
  path="${path#$ccgs_root/}"
  printf '%s\n' "$path"
}

ccgs_payload_paths() {
  local payload="$1"
  local file_path
  file_path="$(ccgs_json_field "$payload" "tool_input.file_path")"
  if [ -n "$file_path" ]; then
    ccgs_relpath "$file_path"
    return
  fi

  local patch
  patch="$(ccgs_json_field "$payload" "tool_input.command")"
  if [ -z "$patch" ]; then
    patch="$(ccgs_json_field "$payload" "tool_input.patch")"
  fi
  if [ -z "$patch" ]; then
    return
  fi

  printf '%s\n' "$patch" | sed -n \
    -e 's/^\*\*\* Add File: //p' \
    -e 's/^\*\*\* Update File: //p' \
    -e 's/^\*\*\* Delete File: //p' \
    -e 's/^\*\*\* Move to: //p' | while IFS= read -r path; do
      ccgs_relpath "$path"
    done | awk 'NF && !seen[$0]++'
}

ccgs_is_git_subcommand() {
  local command="$1"
  local subcommand="$2"
  local regex="^[[:space:]]*git([[:space:]]+-C[[:space:]]+[^[:space:]]+)?[[:space:]]+${subcommand}([[:space:]]|$)"
  [[ "$command" =~ $regex ]]
}

ccgs_first_python() {
  local cmd
  for cmd in python3 python py; do
    if command -v "$cmd" >/dev/null 2>&1; then
      printf '%s\n' "$cmd"
      return 0
    fi
  done
  return 1
}

ccgs_hook_pass() {
  local message="${1:-ok}"
  printf '%s\n' "$message"
  exit 0
}

ccgs_hook_warn() {
  local message="${1:-warning}"
  printf '%s\n' "$message" >&2
  exit 0
}

ccgs_hook_deny() {
  local message="${1:-denied}"
  printf '%s\n' "$message" >&2
  exit 2
}
