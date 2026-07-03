#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd "$(dirname "$0")" && pwd -P)"
source "$script_dir/../lib/hooks.sh"

payload="$(ccgs_read_stdin)"
log_dir="$(ccgs_log_dir)"
printf '%s\n' "$payload" > "$log_dir/session-stop.json"

timestamp="$(date +%Y%m%d_%H%M%S)"
recent_commits="$(git -C "$ccgs_root" log --oneline --since='8 hours ago' 2>/dev/null || true)"
modified_files="$(git -C "$ccgs_root" diff --name-only 2>/dev/null || true)"
state_file="$ccgs_root/production/session-state/active.md"

if [ -f "$state_file" ]; then
  {
    echo "## Archived Session State: $timestamp"
    cat "$state_file"
    echo "---"
    echo ""
  } >> "$log_dir/session-log.md" 2>/dev/null
fi

if [ -n "$recent_commits" ] || [ -n "$modified_files" ]; then
  {
    echo "## Session End: $timestamp"
    if [ -n "$recent_commits" ]; then
      echo "### Commits"
      echo "$recent_commits"
    fi
    if [ -n "$modified_files" ]; then
      echo "### Uncommitted Changes"
      echo "$modified_files"
    fi
    echo "---"
    echo ""
  } >> "$log_dir/session-log.md" 2>/dev/null
fi

exit 0
