#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"
source_root="$(cd "$script_dir/.." && pwd -P)"
target_root="$(cd "${1:-$(pwd)}" && pwd -P)"
dry_run=0

if [ "${2:-}" = "--dry-run" ]; then
  dry_run=1
fi

export CCGS_SOURCE_ROOT="$source_root"
export CCGS_INSTALL_ROOT="$target_root"
export CCGS_DRY_RUN="$dry_run"
source "$source_root/.codex/lib/install.sh"
source "$source_root/.codex/lib/agents.sh"

state_preview="$(mktemp "${TMPDIR:-/tmp}/ccgs-install-state.XXXXXX")"
trap 'rm -f "$state_preview"' EXIT
install_mode="$(ccgs_detect_mode)"
export CCGS_INSTALL_MODE="$install_mode"
ccgs_capture_install_state "$state_preview"
if [ "$dry_run" = "1" ]; then
  ccgs_print_state_summary "$state_preview" "Dry-run install"
fi

ccgs_agent_collision_check "$target_root"
if [ "$source_root" != "$target_root" ]; then
  ccgs_install_assets
fi
if [ "$dry_run" = "1" ]; then
  ccgs_update_gitignore_allowlist
  printf 'Dry-run install for Codex Game Studios from %s to %s\n' "$source_root" "$target_root"
  exit 0
fi
if [ "$source_root" != "$target_root" ]; then
  ccgs_write_install_state "$state_preview"
  ccgs_update_gitignore_allowlist
  ccgs_check_deployed_gitignore
fi
ccgs_verify_manifest_paths
if [ "$source_root" = "$target_root" ]; then
  printf 'Codex Game Studios assets are present and manifest-owned at %s\n' "$target_root"
else
  printf 'Codex Game Studios assets installed from %s to %s\n' "$source_root" "$target_root"
fi
