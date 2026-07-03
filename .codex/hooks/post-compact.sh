#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd "$(dirname "$0")" && pwd -P)"
source "$script_dir/../lib/hooks.sh"

log_dir="$(ccgs_log_dir)"
cat > "$log_dir/post-compact-last.json"

active="$ccgs_root/production/session-state/active.md"

echo "=== Context Restored After Compaction ==="

if [ -f "$active" ]; then
  size="$(wc -l < "$active" 2>/dev/null | tr -d ' ' || echo '?')"
  echo "Session state file exists: production/session-state/active.md ($size lines)"
  echo "IMPORTANT: Read this file now to restore your working context."
  echo "It contains: current task, decisions made, files in progress, open questions."
else
  echo "No session state file found at production/session-state/active.md"
  echo "If you were mid-task, check production/session-logs/ for the last session audit."
fi

echo "========================================="
exit 0
