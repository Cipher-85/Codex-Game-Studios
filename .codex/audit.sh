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
    run validate_runtime.py --kind skills "$@"
    run validate_runtime.py --kind agents "$@"
    run validate_hooks.py "$@"
    run validate_rules.py "$@"
    run validate_evidence.py "$@"
    run validate_artifact_facts.py "$@"
    run validate_project_config.py "$@"
    run validate_config_migration.py "$@"
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
  evidence)
    run validate_evidence.py "$@"
    ;;
  artifact-facts)
    run validate_artifact_facts.py "$@"
    ;;
  project-config)
    run validate_project_config.py "$@"
    ;;
  config-migration)
    run validate_config_migration.py "$@"
    ;;
  coexistence)
    run validate_install.py "$@"
    ;;
  release)
    run validate_release.py "$@"
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
