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

state_file="$(ccgs_install_state_file)"
state_preview=""
if [ -f "$state_file" ]; then
  uninstall_mode="$(ccgs_install_mode)"
  state_preview="$state_file"
else
  state_preview="$(mktemp "${TMPDIR:-/tmp}/ccgs-uninstall-state.XXXXXX")"
  trap 'rm -f "$state_preview"' EXIT
  uninstall_mode="$(ccgs_detect_mode)"
  export CCGS_INSTALL_MODE="$uninstall_mode"
  ccgs_capture_install_state "$state_preview"
fi
export CCGS_INSTALL_MODE="$uninstall_mode"
if [ "$dry_run" = "1" ]; then
  ccgs_print_state_summary "$state_preview" "Dry-run uninstall"
fi

ccgs_uninstall_assets
ccgs_remove_gitignore_allowlist
if [ "$dry_run" = "1" ]; then
  printf 'Dry-run uninstall for Codex Game Studios at %s\n' "$target_root"
else
  printf 'Codex Game Studios assets removed from %s\n' "$target_root"
fi
