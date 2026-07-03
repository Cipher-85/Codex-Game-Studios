#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd "$(dirname "$0")" && pwd -P)"
source "$script_dir/../lib/hooks.sh"

payload="$(ccgs_read_stdin)"
command="$(ccgs_json_field "$payload" "tool_input.command")"

if ! ccgs_is_git_subcommand "$command" "commit"; then
  exit 0
fi

staged="$(git -C "$ccgs_root" diff --cached --name-only 2>/dev/null || true)"
if [ -z "$staged" ]; then
  exit 0
fi

warnings=""

design_files="$(printf '%s\n' "$staged" | grep -E '^design/gdd/' || true)"
if [ -n "$design_files" ]; then
  while IFS= read -r file; do
    [ -n "$file" ] || continue
    if [[ "$file" == *.md ]] && [ -f "$ccgs_root/$file" ]; then
      for section in "Overview" "Player Fantasy" "Detailed" "Formulas" "Edge Cases" "Dependencies" "Tuning Knobs" "Acceptance Criteria"; do
        if ! grep -qi "$section" "$ccgs_root/$file"; then
          warnings="${warnings}"$'\n'"DESIGN: $file missing required section: $section"
        fi
      done
    fi
  done <<<"$design_files"
fi

data_files="$(printf '%s\n' "$staged" | grep -E '^assets/data/.*\.json$' || true)"
if [ -n "$data_files" ]; then
  python_cmd="$(ccgs_first_python || true)"
  while IFS= read -r file; do
    [ -n "$file" ] || continue
    if [ -f "$ccgs_root/$file" ]; then
      if [ -n "$python_cmd" ]; then
        if ! "$python_cmd" -m json.tool "$ccgs_root/$file" >/dev/null 2>&1; then
          ccgs_hook_deny "BLOCKED: $file is not valid JSON"
        fi
      else
        printf 'WARNING: Cannot validate JSON because Python is not available: %s\n' "$file" >&2
      fi
    fi
  done <<<"$data_files"
fi

code_files="$(printf '%s\n' "$staged" | grep -E '^src/gameplay/' || true)"
if [ -n "$code_files" ]; then
  while IFS= read -r file; do
    [ -n "$file" ] || continue
    if [ -f "$ccgs_root/$file" ]; then
      if grep -nE '(damage|health|speed|rate|chance|cost|duration)[[:space:]]*[:=][[:space:]]*[0-9]+' "$ccgs_root/$file" >/dev/null 2>&1; then
        warnings="${warnings}"$'\n'"CODE: $file may contain hardcoded gameplay values. Use data files."
      fi
    fi
  done <<<"$code_files"
fi

src_files="$(printf '%s\n' "$staged" | grep -E '^src/' || true)"
if [ -n "$src_files" ]; then
  while IFS= read -r file; do
    [ -n "$file" ] || continue
    if [ -f "$ccgs_root/$file" ]; then
      if grep -nE '(TODO|FIXME|HACK)[^(]' "$ccgs_root/$file" >/dev/null 2>&1; then
        warnings="${warnings}"$'\n'"STYLE: $file has TODO/FIXME without owner tag. Use TODO(name) format."
      fi
    fi
  done <<<"$src_files"
fi

if [ -n "$warnings" ]; then
  {
    echo "=== Commit Validation Warnings ==="
    printf '%s\n' "$warnings"
    echo "=================================="
  } >&2
fi

exit 0
