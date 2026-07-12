#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"
source_root="$(cd "$script_dir/.." && pwd -P)"
dry_run=0
target_arg=""

while [ "$#" -gt 0 ]; do
  case "$1" in
    --dry-run)
      dry_run=1
      shift
      ;;
    -h|--help)
      cat <<'EOF'
Usage: ./.codex/uninstall.sh [--dry-run] [target]

--dry-run may appear before or after the optional target.
EOF
      exit 0
      ;;
    -*)
      printf 'uninstall: unsupported option: %s\n' "$1" >&2
      exit 2
      ;;
    *)
      if [ -n "$target_arg" ]; then
        printf 'uninstall: multiple target paths supplied\n' >&2
        exit 2
      fi
      target_arg="$1"
      shift
      ;;
  esac
done

target_root="$(cd "${target_arg:-$(pwd)}" && pwd -P)"

export CCGS_SOURCE_ROOT="$source_root"
export CCGS_INSTALL_ROOT="$target_root"
export CCGS_DRY_RUN="$dry_run"
source "$source_root/.codex/lib/install.sh"

state_file="$(ccgs_install_state_file)"
if ccgs_target_path_has_symlink ".gitignore"; then
  printf 'uninstall: refusing symlinked .gitignore; no project files were changed\n' >&2
  exit 1
fi
if [ ! -e "$state_file" ]; then
  printf 'uninstall: missing %s; refusing to infer package ownership from file contents\n' "$ccgs_install_state_rel" >&2
  exit 1
fi
if ccgs_target_path_has_symlink "$ccgs_install_state_rel" || ! ccgs_install_state_valid; then
  printf 'uninstall: invalid, unsafe, or stale %s; no project files were changed\n' "$ccgs_install_state_rel" >&2
  exit 1
fi
export CCGS_INSTALL_STATE_VALIDATED=1
state_preview="$state_file"
uninstall_mode="$(ccgs_install_mode)"
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
