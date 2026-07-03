#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd "$(dirname "$0")" && pwd -P)"
source "$script_dir/../lib/hooks.sh"
payload="$(ccgs_read_stdin)"
command="$(ccgs_json_field "$payload" "tool_input.command")"

if [[ "$command" == *"git commit"* ]] && [ ! -f "$ccgs_root/production/test-evidence/latest.md" ]; then
  ccgs_hook_deny "Create production/test-evidence/latest.md before committing Game Studios work."
fi

ccgs_hook_pass "Commit command allowed."
