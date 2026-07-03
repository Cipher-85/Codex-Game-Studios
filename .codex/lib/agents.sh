#!/usr/bin/env bash
set -euo pipefail

ccgs_agent_collision_check() {
  local root="${1:-$(pwd)}"
  local duplicate=0
  if [ -d "$root/.codex/agents" ]; then
    while IFS= read -r agent; do
      [ -n "$agent" ] || continue
      case "$agent" in
        default|worker|explorer)
          printf 'agent name collides with Codex built-in: %s\n' "$agent" >&2
          duplicate=1
          ;;
      esac
    done < <(find "$root/.codex/agents" -maxdepth 1 -type f -name '*.toml' -exec basename {} .toml \; | sort)
  fi
  return "$duplicate"
}
