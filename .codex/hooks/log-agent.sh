#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd "$(dirname "$0")" && pwd -P)"
source "$script_dir/../lib/hooks.sh"

payload="$(ccgs_read_stdin)"
agent_name="$(ccgs_json_field "$payload" "agent_type")"
if [ -z "$agent_name" ]; then
  agent_name="unknown"
fi

timestamp="$(date +%Y%m%d_%H%M%S)"
log_dir="$(ccgs_log_dir)"

echo "$timestamp | Agent invoked: $agent_name" >> "$log_dir/agent-audit.log" 2>/dev/null
printf '%s\n' "$payload" >> "$log_dir/agents-start.jsonl"

exit 0
