#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd "$(dirname "$0")" && pwd -P)"
source "$script_dir/../lib/hooks.sh"

missing=()
for path in production design docs/architecture src tests; do
  if [ ! -e "$ccgs_root/$path" ]; then
    missing+=("$path")
  fi
done

if [ "${#missing[@]}" -gt 0 ]; then
  ccgs_hook_warn "Game Studios gap check: missing ${missing[*]}"
else
  ccgs_hook_pass "Game Studios gap check passed."
fi
