#!/usr/bin/env bash
set -euo pipefail

base_dir="$(cd "$(dirname "$0")" && pwd -P)"
cmd="${1:-}"
shift || true

run() {
  local name="$1"
  shift
  python3 "$base_dir/lib/$name" "$@"
}

case "$cmd" in
  all)
    run validate_manifest.py "$@"
    run validate_runtime.py "$@"
    run validate_hooks.py "$@"
    run validate_rules.py "$@"
    run validate_install.py "$@"
    run validate_smoke.py headless "$@"
    ;;
  manifest)
    run validate_manifest.py "$@"
    ;;
  runtime)
    run validate_runtime.py "$@"
    ;;
  skills)
    run validate_runtime.py --kind skills "$@"
    ;;
  agents)
    run validate_runtime.py --kind agents "$@"
    ;;
  config)
    run validate_rules.py "$@"
    ;;
  hooks)
    run validate_hooks.py "$@"
    ;;
  coexistence)
    run validate_install.py "$@"
    ;;
  smoke-headless)
    run validate_smoke.py headless "$@"
    ;;
  smoke-interactive)
    run validate_smoke.py interactive "$@"
    ;;
  docs)
    run validate_runtime.py --kind docs "$@"
    ;;
  *)
    printf 'audit: unsupported command: %s\n' "${cmd:-<none>}" >&2
    exit 2
    ;;
esac
