#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd "$(dirname "$0")" && pwd -P)"
source "$script_dir/../lib/hooks.sh"
payload="$(ccgs_read_stdin)"
tool_name="$(ccgs_json_field "$payload" "tool_name")"
log_dir="$(ccgs_log_dir)"
printf '%s\n' "$payload" > "$log_dir/asset-validation-last.json"
ccgs_hook_warn "Asset validation advisory recorded for $tool_name."
