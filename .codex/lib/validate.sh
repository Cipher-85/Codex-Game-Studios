#!/usr/bin/env bash
set -euo pipefail

ccgs_run_audit() {
  local root="${1:-$(pwd)}"
  "$root/.codex/audit.sh" all --root "$root"
}
