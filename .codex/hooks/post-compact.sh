#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd "$(dirname "$0")" && pwd -P)"
source "$script_dir/../lib/hooks.sh"
log_dir="$(ccgs_log_dir)"
cat > "$log_dir/post-compact-last.json"
ccgs_hook_pass "Post-compact state recorded."
