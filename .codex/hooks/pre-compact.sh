#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd "$(dirname "$0")" && pwd -P)"
source "$script_dir/../lib/hooks.sh"

log_dir="$(ccgs_log_dir)"
cat > "$log_dir/pre-compact-last.json"

echo "=== SESSION STATE BEFORE COMPACTION ==="
echo "Timestamp: $(date)"

state_file="$ccgs_root/production/session-state/active.md"
handoff_file="$ccgs_root/production/session-handoff.md"
state_kind="$(ccgs_active_state_kind "$state_file")"

if [ "$state_kind" = "substantive" ]; then
  echo ""
  echo "## Active Session State (from production/session-state/active.md)"
  ccgs_preview_bounded "$state_file" 100
  if [ -f "$handoff_file" ]; then
    echo ""
    echo "## Canonical Handoff Fallback"
    ccgs_preview_bounded "$handoff_file" 60
  fi
else
  echo ""
  if [ -f "$handoff_file" ]; then
    echo "## Canonical Handoff Recovery (elevated)"
    ccgs_preview_bounded "$handoff_file" 60
  else
    echo "## No canonical handoff found"
  fi
  if [ "$state_kind" = "pointer" ]; then
    echo ""
    echo "## Pointer-Only Active State"
    ccgs_preview_bounded "$state_file" 20
  else
    echo "No active session state file found."
  fi
fi

echo ""
echo "## Files Modified (git working tree)"

changed="$(git -C "$ccgs_root" diff --name-only 2>/dev/null || true)"
staged="$(git -C "$ccgs_root" diff --staged --name-only 2>/dev/null || true)"
untracked="$(git -C "$ccgs_root" ls-files --others --exclude-standard 2>/dev/null || true)"

if [ -n "$changed" ]; then
  echo "Unstaged changes:"
  printf '%s\n' "$changed" | while IFS= read -r f; do echo "  - $f"; done
fi
if [ -n "$staged" ]; then
  echo "Staged changes:"
  printf '%s\n' "$staged" | while IFS= read -r f; do echo "  - $f"; done
fi
if [ -n "$untracked" ]; then
  echo "New untracked files:"
  printf '%s\n' "$untracked" | while IFS= read -r f; do echo "  - $f"; done
fi
if [ -z "$changed" ] && [ -z "$staged" ] && [ -z "$untracked" ]; then
  echo "  (no uncommitted changes)"
fi

echo ""
echo "## Design Docs - Work In Progress"

wip_found=false
if [ -d "$ccgs_root/design/gdd" ]; then
  while IFS= read -r f; do
    [ -n "$f" ] || continue
    incomplete="$(grep -n -E 'TODO|WIP|PLACEHOLDER|\[TO BE|\[TBD\]' "$f" 2>/dev/null || true)"
    if [ -n "$incomplete" ]; then
      wip_found=true
      rel="$(ccgs_relpath "$f")"
      echo "  $rel:"
      printf '%s\n' "$incomplete" | while IFS= read -r line; do echo "    $line"; done
    fi
  done < <(find "$ccgs_root/design/gdd" -maxdepth 1 -type f -name '*.md' 2>/dev/null)
fi

if [ "$wip_found" = false ]; then
  echo "  (no WIP markers found in design docs)"
fi

echo "Context compaction occurred at $(date)." >> "$log_dir/compaction-log.txt" 2>/dev/null || true

echo ""
echo "## Recovery Instructions"
echo "After compaction, read substantive production/session-state/active.md first."
echo "Use production/session-handoff.md as the canonical fallback; elevate it when active.md is missing or pointer-only."
echo "Then read any files listed above that are being actively worked on."
echo "=== END SESSION STATE ==="
exit 0
