#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd "$(dirname "$0")" && pwd -P)"
source "$script_dir/../lib/hooks.sh"
payload="$(ccgs_read_stdin)"
command="$(ccgs_json_field "$payload" "tool_input.command")"
branch="$(git -C "$ccgs_root" branch --show-current 2>/dev/null || true)"

if [[ "$command" == *"git push"* && "$branch" =~ ^(main|master)$ ]]; then
  ccgs_hook_deny "Refusing direct push from protected branch $branch."
fi

ccgs_hook_pass "Push command allowed."
