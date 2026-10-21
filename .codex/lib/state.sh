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

# Observational status stays available on configuration/tooling errors, but never
# substitutes a mode that might hide a required director gate.
ccgs_review_mode() {
  local root="$1"
  local helper="$root/.codex/lib/project_config.py"
  local python_cmd
  python_cmd="$(ccgs_first_python || true)"
  if [ -z "$python_cmd" ] || [ ! -f "$helper" ]; then
    printf 'Review mode NOT ASSESSED: Python and the installed project_config.py are required.\n' >&2
    printf 'NOT ASSESSED\n'
    return 0
  fi
  local output
  if output="$("$python_cmd" "$helper" --root "$root" review-mode --format text)"; then
    case "$output" in
      'full ('*')'|'lean ('*')'|'solo ('*')')
        printf '%s\n' "$output"
        return 0
        ;;
    esac
  elif [ "$output" = "INVALID" ]; then
    printf 'Review mode INVALID: repair configuration before review routing.\n' >&2
    printf 'INVALID\n'
    return 0
  fi
  printf 'Review mode NOT ASSESSED: configuration helper failed or returned an unsupported result.\n' >&2
  printf 'NOT ASSESSED\n'
}

ccgs_stage() {
  local root="$1"
  local helper="$root/.codex/lib/project_config.py"
  local python_cmd output
  python_cmd="$(ccgs_first_python || true)"
  if [ -z "$python_cmd" ] || [ ! -f "$helper" ]; then
    printf 'Stage NOT ASSESSED: Python and project_config.py are required.\n' >&2
    printf 'NOT ASSESSED\n'
    return 0
  fi
  if output="$("$python_cmd" "$helper" --root "$root" stage --format text)"; then
    case "$output" in
      'Concept ('*')'|'Systems Design ('*')'|'Technical Setup ('*')'|'Pre-Production ('*')'|'Production ('*')'|'Polish ('*')'|'Release ('*')'|'Live ('*')'|'unset (unset)')
        printf '%s\n' "$output"
        return 0
        ;;
    esac
  elif [ "$output" = "INVALID" ]; then
    printf 'Stage INVALID: repair configuration before stage routing.\n' >&2
    printf 'INVALID\n'
    return 0
  fi
  printf 'Stage NOT ASSESSED: helper failed or returned an unsupported result.\n' >&2
  printf 'NOT ASSESSED\n'
}
