#!/usr/bin/env bash
# Advisory checks only: approval and existing blocking rules remain authoritative.
set -euo pipefail
script_dir="$(cd "$(dirname "$0")" && pwd -P)"
source "$script_dir/../lib/hooks.sh"
python_cmd="$(ccgs_first_python || true)"
if [ -z "$python_cmd" ]; then
  printf '%s\n' '{"systemMessage":"CCGS artifact warning: NOT ASSESSED: Python unavailable","hookSpecificOutput":{"hookEventName":"PreToolUse","additionalContext":"CCGS artifact warning: NOT ASSESSED: Python unavailable"}}'
  exit 0
fi
if output="$("$python_cmd" -B "$script_dir/../lib/artifact_guards.py" --root "$ccgs_root")"; then
  [ -z "$output" ] || printf '%s\n' "$output"
else
  printf '%s\n' '{"systemMessage":"CCGS artifact warning: NOT ASSESSED: validator failed","hookSpecificOutput":{"hookEventName":"PreToolUse","additionalContext":"CCGS artifact warning: NOT ASSESSED: validator failed"}}'
fi
exit 0
