#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd "$(dirname "$0")" && pwd -P)"
source "$script_dir/../lib/hooks.sh"
source "$script_dir/../lib/state.sh"

stage="$(ccgs_stage "$ccgs_root")"
review="$(ccgs_review_mode "$ccgs_root")"
active="$(ccgs_state_read "$ccgs_root" production/session-state/active.md | head -n 1)"
ccgs_hook_pass "Stage: $stage | Review mode: $review | Active session: $active"
