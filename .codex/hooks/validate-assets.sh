#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd "$(dirname "$0")" && pwd -P)"
source "$script_dir/../lib/hooks.sh"

payload="$(ccgs_read_stdin)"
log_dir="$(ccgs_log_dir)"
printf '%s\n' "$payload" > "$log_dir/asset-validation-last.json"

paths="$(ccgs_payload_paths "$payload" || true)"
if [ -z "$paths" ]; then
  exit 0
fi

warnings=""
errors=""

while IFS= read -r file_path; do
  [ -n "$file_path" ] || continue
  file_path="$(ccgs_relpath "$file_path")"

  if ! printf '%s\n' "$file_path" | grep -qE '(^|/)assets/'; then
    continue
  fi

  filename="$(basename "$file_path")"
  if printf '%s\n' "$filename" | grep -qE '[A-Z[:space:]-]'; then
    warnings="${warnings}"$'\n'"  NAMING: $file_path must be lowercase with underscores (got: $filename)"
  fi

  if printf '%s\n' "$file_path" | grep -qE '(^|/)assets/data/.*\.json$'; then
    if [ -f "$ccgs_root/$file_path" ]; then
      python_cmd="$(ccgs_first_python || true)"
      if [ -n "$python_cmd" ]; then
        if ! "$python_cmd" -m json.tool "$ccgs_root/$file_path" >/dev/null 2>&1; then
          errors="${errors}"$'\n'"  FORMAT: $file_path is not valid JSON - fix syntax errors before continuing"
        fi
      fi
    fi
  fi
done <<<"$paths"

if [ -n "$warnings" ]; then
  {
    echo "=== Asset Validation: Warnings ==="
    printf '%s\n' "$warnings"
    echo "=================================="
    echo "(Warnings are advisory. Fix before final commit.)"
  } >&2
fi

if [ -n "$errors" ]; then
  {
    echo "=== Asset Validation: ERRORS (Blocking) ==="
    printf '%s\n' "$errors"
    echo "==========================================="
    echo "Fix these errors before proceeding."
  } >&2
  exit 2
fi

exit 0
