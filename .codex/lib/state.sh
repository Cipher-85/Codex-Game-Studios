#!/usr/bin/env bash
set -euo pipefail

ccgs_state_read() {
  local root="${1:-$(pwd)}"
  local file="$2"
  if [ -f "$root/$file" ]; then
    sed -n '1,20p' "$root/$file"
  else
    printf 'unset\n'
  fi
}
