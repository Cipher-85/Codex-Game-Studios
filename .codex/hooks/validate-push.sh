#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd "$(dirname "$0")" && pwd -P)"
source "$script_dir/../lib/hooks.sh"

payload="$(ccgs_read_stdin)"
command="$(ccgs_json_field "$payload" "tool_input.command")"

if ! ccgs_is_git_subcommand "$command" "push"; then
  exit 0
fi

current_branch="$(git -C "$ccgs_root" rev-parse --abbrev-ref HEAD 2>/dev/null || true)"
matched_branch=""

for branch in develop main master; do
  if [ "$current_branch" = "$branch" ]; then
    matched_branch="$branch"
    break
  fi
  if printf '%s\n' "$command" | grep -qE "[[:space:]]${branch}([[:space:]]|$)"; then
    matched_branch="$branch"
    break
  fi
done

if [ -n "$matched_branch" ]; then
  {
    echo "Push to protected branch '$matched_branch' detected."
    echo "Reminder: Ensure build passes, unit tests pass, and no S1/S2 bugs exist."
  } >&2
fi

exit 0
