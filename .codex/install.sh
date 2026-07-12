#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"
source_root="$(cd "$script_dir/.." && pwd -P)"
dry_run=0
replace_modified=0
requested_patch_mode=""
target_arg=""

while [ "$#" -gt 0 ]; do
  case "$1" in
    --dry-run)
      dry_run=1
      shift
      ;;
    --replace-modified)
      replace_modified=1
      shift
      ;;
    -h|--help)
      cat <<'EOF'
Usage: ./.codex/install.sh [--dry-run] [--replace-modified] [--patch incremental|full] [target]

By default, installation aborts before mutation when a package-owned target was
locally modified. --replace-modified permits backup-first replacement only for
paths proven package-owned by valid install state; it never adopts unowned
conflicts.
EOF
      exit 0
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
export CCGS_REPLACE_MODIFIED="$replace_modified"
export CCGS_REQUESTED_PATCH_MODE="$requested_patch_mode"
source "$source_root/.codex/lib/install.sh"
source "$source_root/.codex/lib/agents.sh"

existing_state="$target_root/$ccgs_install_state_rel"
if [ -e "$existing_state" ]; then
  if ccgs_target_path_has_symlink "$ccgs_install_state_rel" || ! ccgs_install_state_valid; then
    printf 'install: refusing invalid, unsafe, or stale install state at %s\n' "$ccgs_install_state_rel" >&2
    exit 1
  fi
  export CCGS_INSTALL_STATE_VALIDATED=1
else
  export CCGS_INSTALL_STATE_VALIDATED=0
fi

state_preview="$(mktemp "${TMPDIR:-/tmp}/ccgs-install-state.XXXXXX")"
transaction_started=0
install_succeeded=0
cleanup_install() {
  local status="$?"
  if [ "$transaction_started" = "1" ] && [ "$install_succeeded" != "1" ]; then
    ccgs_transaction_restore || true
  fi
  rm -f "$state_preview"
  return "$status"
}
trap cleanup_install EXIT
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
  ccgs_install_preflight
  if [ "$dry_run" != "1" ]; then
    ccgs_transaction_prepare_install
    transaction_started=1
  fi
  ccgs_install_assets
fi
if [ "$dry_run" = "1" ]; then
  ccgs_update_gitignore_allowlist
  printf 'Dry-run install for Codex Game Studios from %s to %s\n' "$source_root" "$target_root"
  exit 0
fi
if [ "$source_root" != "$target_root" ]; then
  ccgs_update_gitignore_allowlist
fi
ccgs_verify_manifest_paths
if [ "${CCGS_TEST_FAILPOINT:-}" = "after-verify" ]; then
  printf 'installer test failpoint: after-verify\n' >&2
  exit 97
fi
if [ "$source_root" != "$target_root" ]; then
  ccgs_check_deployed_gitignore
  ccgs_write_install_state "$state_preview"
  ccgs_transaction_commit
  transaction_started=0
fi
install_succeeded=1
if [ "$source_root" = "$target_root" ]; then
  printf 'Codex Game Studios assets are present and manifest-owned at %s\n' "$target_root"
else
  printf 'Codex Game Studios assets installed from %s to %s\n' "$source_root" "$target_root"
  printf 'Static package verification passed. Codex trust and runtime activation require a trusted project and a new session; they were not verified by this installer.\n'
fi
