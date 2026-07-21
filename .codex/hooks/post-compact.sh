#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd "$(dirname "$0")" && pwd -P)"
source "$script_dir/../lib/hooks.sh"

log_dir="$(ccgs_log_dir)"
cat > "$log_dir/post-compact-last.json"

active="$ccgs_root/production/session-state/active.md"
handoff="$ccgs_root/production/session-handoff.md"
state_kind="$(ccgs_active_state_kind "$active")"

echo "=== Context Restored After Compaction ==="

if [ "$state_kind" = "substantive" ]; then
  echo "## Substantive Active Session State"
  ccgs_preview_bounded "$active" 80
  if [ -f "$handoff" ]; then
    echo ""
    echo "## Canonical Handoff Fallback"
    ccgs_preview_bounded "$handoff" 60
  fi
else
  if [ -f "$handoff" ]; then
    echo "## Canonical Handoff Recovery (elevated)"
    ccgs_preview_bounded "$handoff" 60
  else
    echo "No canonical handoff found at production/session-handoff.md"
  fi
  if [ "$state_kind" = "pointer" ]; then
    echo ""
    echo "## Pointer-Only Active State"
    ccgs_preview_bounded "$active" 20
  else
    echo "No session state file found at production/session-state/active.md"
  fi
fi

echo "========================================="
exit 0
