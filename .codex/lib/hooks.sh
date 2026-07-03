#!/usr/bin/env bash
set -euo pipefail

ccgs_root="${CCGS_ROOT:-$(pwd)}"

ccgs_read_stdin() {
  cat
}

ccgs_json_field() {
  local json="$1"
  local field="$2"
  python3 -c 'import json,sys
data=json.loads(sys.stdin.read() or "{}")
value=data
for part in sys.argv[1].split("."):
    value=value.get(part, "") if isinstance(value, dict) else ""
print(value if isinstance(value, str) else json.dumps(value))' "$field" <<<"$json"
}

ccgs_log_dir() {
  local dir="$ccgs_root/production/session-logs"
  mkdir -p "$dir"
  printf '%s\n' "$dir"
}

ccgs_hook_pass() {
  local message="${1:-ok}"
  :
}

ccgs_hook_warn() {
  local message="${1:-warning}"
  :
}

ccgs_hook_deny() {
  local message="${1:-denied}"
  printf '%s\n' "$message" >&2
  exit 2
}
