#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd "$(dirname "$0")" && pwd -P)"
source "$script_dir/../lib/hooks.sh"

payload="$(ccgs_read_stdin)"
log_dir="$(ccgs_log_dir)"
printf '%s\n' "$payload" > "$log_dir/session-start.json"

echo "=== Codex Game Studios - Session Context ==="

branch="$(git -C "$ccgs_root" rev-parse --abbrev-ref HEAD 2>/dev/null || true)"
if [ -n "$branch" ]; then
  echo "Branch: $branch"
  echo ""
  echo "Recent commits:"
  (git -C "$ccgs_root" log --oneline -5 2>/dev/null || true) | while IFS= read -r line; do
    echo "  $line"
  done
fi

latest_sprint="$(ls -t "$ccgs_root"/production/sprints/sprint-*.md 2>/dev/null | head -1 || true)"
if [ -n "$latest_sprint" ]; then
  echo ""
  echo "Active sprint: $(basename "$latest_sprint" .md)"
fi

latest_milestone="$(ls -t "$ccgs_root"/production/milestones/*.md 2>/dev/null | head -1 || true)"
if [ -n "$latest_milestone" ]; then
  echo "Active milestone: $(basename "$latest_milestone" .md)"
fi

bug_count=0
for dir in tests/playtest production; do
  if [ -d "$ccgs_root/$dir" ]; then
    count="$(find "$ccgs_root/$dir" -name 'BUG-*.md' 2>/dev/null | wc -l | tr -d ' ')"
    bug_count=$((bug_count + count))
  fi
done
if [ "$bug_count" -gt 0 ]; then
  echo "Open bugs: $bug_count"
fi

if [ -d "$ccgs_root/src" ]; then
  todo_count="$({ grep -R "TODO" "$ccgs_root/src" 2>/dev/null || true; } | wc -l | tr -d ' ')"
  fixme_count="$({ grep -R "FIXME" "$ccgs_root/src" 2>/dev/null || true; } | wc -l | tr -d ' ')"
  if [ "$todo_count" -gt 0 ] || [ "$fixme_count" -gt 0 ]; then
    echo ""
    echo "Code health: ${todo_count} TODOs, ${fixme_count} FIXMEs in src/"
  fi
fi

state_file="$ccgs_root/production/session-state/active.md"
if [ -f "$state_file" ]; then
  echo ""
  echo "=== ACTIVE SESSION STATE DETECTED ==="
  echo "A previous session left state at: production/session-state/active.md"
  echo "Read this file to recover context and continue where you left off."
  echo ""
  echo "Quick summary (last 20 lines):"
  tail -20 "$state_file" 2>/dev/null || true
  total_lines="$(wc -l < "$state_file" 2>/dev/null | tr -d ' ' || echo 0)"
  if [ "${total_lines:-0}" -gt 20 ] 2>/dev/null; then
    echo "  ... ($total_lines total lines - read the full file to continue)"
  fi
  echo "=== END SESSION STATE PREVIEW ==="
fi

echo "==================================="
exit 0
