#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd "$(dirname "$0")" && pwd -P)"
source "$script_dir/../lib/hooks.sh"

payload="$(ccgs_read_stdin)"
log_dir="$(ccgs_log_dir)"
printf '%s\n' "$payload" > "$log_dir/skill-change-last.json"

paths="$(ccgs_payload_paths "$payload" || true)"
if [ -z "$paths" ]; then
  exit 0
fi

while IFS= read -r file_path; do
  [ -n "$file_path" ] || continue
  file_path="$(ccgs_relpath "$file_path")"

  if ! printf '%s\n' "$file_path" | grep -qE '(^|/)\.agents/skills/'; then
    continue
  fi

  skill_name="$(printf '%s\n' "$file_path" | sed -n 's#^\.agents/skills/\([^/]*\).*#\1#p')"
  if [ -z "$skill_name" ]; then
    continue
  fi

  {
    echo "=== Skill Modified: $skill_name ==="
    echo "Run \$skill-test static $skill_name to validate structural compliance."
    echo "===================================="
  } >&2
done <<<"$paths"

exit 0
