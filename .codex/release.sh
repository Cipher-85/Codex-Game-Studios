#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"
root="$(cd "$script_dir/.." && pwd -P)"
version_file="$root/.codex/VERSION"
changelog_file="$root/CHANGELOG.md"

usage() {
  cat >&2 <<'EOF'
usage:
  ./.codex/release.sh current
  ./.codex/release.sh bump patch|minor|major|X.Y.Z [--dry-run] [--date YYYY-MM-DD]
  ./.codex/release.sh check
EOF
}

current_version() {
  tr -d '[:space:]' < "$version_file"
}

validate_version() {
  python3 - "$1" <<'PY'
import re, sys
value = sys.argv[1]
if not re.fullmatch(r"(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)", value):
    raise SystemExit(f"invalid version: {value}")
PY
}

bump_version() {
  local kind="$1"
  local current
  current="$(current_version)"
  validate_version "$current"
  python3 - "$current" "$kind" <<'PY'
import re, sys
current, kind = sys.argv[1], sys.argv[2]
major, minor, patch = (int(part) for part in current.split("."))
if kind == "patch":
    patch += 1
elif kind == "minor":
    minor += 1
    patch = 0
elif kind == "major":
    major += 1
    minor = 0
    patch = 0
elif re.fullmatch(r"(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)", kind):
    print(kind)
    raise SystemExit(0)
else:
    raise SystemExit(f"unsupported bump: {kind}")
print(f"{major}.{minor}.{patch}")
PY
}

write_changelog_section() {
  local version="$1"
  local release_date="$2"
  python3 - "$changelog_file" "$version" "$release_date" <<'PY'
import re, sys
from pathlib import Path

path = Path(sys.argv[1])
version = sys.argv[2]
release_date = sys.argv[3]
heading = f"## v{version} - {release_date}"
placeholder = "- Document release notes before tagging this version."
section = f"{heading}\n\n{placeholder}\n\n"

text = path.read_text(encoding="utf-8") if path.exists() else "# Changelog\n"
pattern = re.compile(rf"^## v{re.escape(version)}(?:\s+-\s+\d{{4}}-\d{{2}}-\d{{2}})?\s*$", re.MULTILINE)
match = pattern.search(text)
if match:
    line_end = text.find("\n", match.start())
    if line_end == -1:
        line_end = len(text)
    text = text[:match.start()] + heading + text[line_end:]
elif text.startswith("# Changelog\n"):
    insert_at = text.find("\n") + 1
    text = text[:insert_at] + "\n" + section + text[insert_at:].lstrip("\n")
else:
    text = "# Changelog\n\n" + section + text.lstrip("\n")
path.write_text(text.rstrip() + "\n", encoding="utf-8")
PY
}

cmd="${1:-}"
if [ -n "$cmd" ]; then
  shift
fi

case "$cmd" in
  current)
    current_version
    ;;
  check)
    python3 "$root/.codex/lib/validate_release.py" --root "$root"
    ;;
  bump)
    bump_kind="${1:-}"
    if [ -z "$bump_kind" ]; then
      usage
      exit 2
    fi
    shift
    dry_run=0
    release_date="$(date -u +%F)"
    while [ "$#" -gt 0 ]; do
      case "$1" in
        --dry-run)
          dry_run=1
          shift
          ;;
        --date)
          release_date="${2:-}"
          if [ -z "$release_date" ]; then
            printf 'release: --date requires YYYY-MM-DD\n' >&2
            exit 2
          fi
          shift 2
          ;;
        *)
          printf 'release: unsupported argument: %s\n' "$1" >&2
          usage
          exit 2
          ;;
      esac
    done
    if ! [[ "$release_date" =~ ^[0-9]{4}-[0-9]{2}-[0-9]{2}$ ]]; then
      printf 'release: invalid date: %s\n' "$release_date" >&2
      exit 2
    fi
    next_version="$(bump_version "$bump_kind")"
    if [ "$dry_run" = "1" ]; then
      printf 'would update .codex/VERSION: %s -> %s\n' "$(current_version)" "$next_version"
      printf 'would create/update CHANGELOG.md section: v%s - %s\n' "$next_version" "$release_date"
      exit 0
    fi
    printf '%s\n' "$next_version" > "$version_file"
    write_changelog_section "$next_version" "$release_date"
    printf 'updated release version to %s\n' "$next_version"
    ;;
  *)
    usage
    exit 2
    ;;
esac
