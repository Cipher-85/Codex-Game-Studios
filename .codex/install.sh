#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"
source_root="$(cd "$script_dir/.." && pwd -P)"
dry_run=0
requested_patch_mode=""
target_arg=""

while [ "$#" -gt 0 ]; do
  case "$1" in
    --dry-run)
      dry_run=1
      shift
      ;;
    --patch)
      requested_patch_mode="${2:-}"
      if [ -z "$requested_patch_mode" ]; then
        printf 'install: --patch requires incremental or full\n' >&2
        exit 2
      fi
      case "$requested_patch_mode" in
        incremental|full)
          ;;
        *)
          printf 'install: unsupported patch mode: %s\n' "$requested_patch_mode" >&2
          exit 2
          ;;
      esac
      shift 2
      ;;
    -*)
      printf 'install: unsupported option: %s\n' "$1" >&2
      exit 2
      ;;
    *)
      if [ -n "$target_arg" ]; then
        printf 'install: multiple target paths supplied\n' >&2
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
export CCGS_REQUESTED_PATCH_MODE="$requested_patch_mode"
source "$source_root/.codex/lib/install.sh"
source "$source_root/.codex/lib/agents.sh"

state_preview="$(mktemp "${TMPDIR:-/tmp}/ccgs-install-state.XXXXXX")"
trap 'rm -f "$state_preview"' EXIT
install_mode="$(ccgs_detect_mode)"
patch_mode="$(ccgs_select_patch_mode)"
export CCGS_INSTALL_MODE="$install_mode"
export CCGS_PATCH_MODE="$patch_mode"
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
