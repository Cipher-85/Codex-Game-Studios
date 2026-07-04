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
  ./.codex/release.sh publish [--dry-run]
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

release_tag() {
  printf 'codex-v%s\n' "$(current_version)"
}

release_title() {
  printf 'Codex Game Studios v%s\n' "$(current_version)"
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

extract_release_notes() {
  local version="$1"
  python3 - "$changelog_file" "$version" <<'PY'
import re
import sys
from pathlib import Path

path = Path(sys.argv[1])
version = sys.argv[2]
try:
    text = path.read_text(encoding="utf-8")
except FileNotFoundError as exc:
    raise SystemExit(f"release: missing CHANGELOG.md: {exc}")

heading_pattern = re.compile(
    rf"^## v{re.escape(version)}(?:\s+-\s+\d{{4}}-\d{{2}}-\d{{2}})?\s*$",
    re.MULTILINE,
)
match = heading_pattern.search(text)
if not match:
    raise SystemExit(f"release: CHANGELOG.md is missing section ## v{version}")

body_start = text.find("\n", match.end())
if body_start == -1:
    body = ""
else:
    next_heading = re.search(r"^##\s+", text[body_start + 1 :], re.MULTILINE)
    if next_heading:
        body = text[body_start + 1 : body_start + 1 + next_heading.start()]
    else:
        body = text[body_start + 1 :]

notes = body.strip()
placeholder_markers = (
    "Document release notes before tagging this version.",
    "TBD",
    "TODO",
    "[PLACEHOLDER]",
    "[TODO]",
)
if not notes:
    raise SystemExit(f"release: CHANGELOG.md section v{version} has no release notes")
if any(marker in notes for marker in placeholder_markers):
    raise SystemExit(f"release: CHANGELOG.md section v{version} still contains placeholder text")

print(notes)
PY
}

require_clean_worktree() {
  if [ -n "$(git -C "$root" status --porcelain)" ]; then
    printf 'release: worktree must be clean before publishing\n' >&2
    exit 1
  fi
}

require_gh_ready() {
  if ! command -v gh >/dev/null 2>&1; then
    printf 'release: gh CLI is required for publishing\n' >&2
    exit 1
  fi
  if ! gh auth status >/dev/null 2>&1; then
    printf 'release: gh CLI is not authenticated\n' >&2
    exit 1
  fi
}

origin_main_commit() {
  git -C "$root" ls-remote --exit-code origin refs/heads/main | awk '{print $1}'
}

require_head_matches_origin_main() {
  local head
  local origin_main
  head="$(git -C "$root" rev-parse HEAD)"
  if ! origin_main="$(origin_main_commit)"; then
    printf 'release: could not read origin/main\n' >&2
    exit 1
  fi
  if [ "$head" != "$origin_main" ]; then
    printf 'release: HEAD (%s) does not match origin/main (%s)\n' "$head" "$origin_main" >&2
    exit 1
  fi
}

origin_tag_commit() {
  local tag="$1"
  local peeled
  local exact
  peeled="$(git -C "$root" ls-remote --tags origin "refs/tags/$tag^{}" | awk '{print $1}')"
  if [ -n "$peeled" ]; then
    printf '%s\n' "$peeled"
    return 0
  fi
  exact="$(git -C "$root" ls-remote --tags origin "refs/tags/$tag" | awk '{print $1}')"
  if [ -n "$exact" ]; then
    printf '%s\n' "$exact"
  fi
}

require_origin_tag_missing_or_head() {
  local tag="$1"
  local head="$2"
  local remote_tag
  remote_tag="$(origin_tag_commit "$tag")"
  if [ -n "$remote_tag" ] && [ "$remote_tag" != "$head" ]; then
    printf 'release: origin tag %s points at %s, not HEAD %s\n' "$tag" "$remote_tag" "$head" >&2
    exit 1
  fi
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
  publish)
    dry_run=0
    while [ "$#" -gt 0 ]; do
      case "$1" in
        --dry-run)
          dry_run=1
          shift
          ;;
        *)
          printf 'release: unsupported argument: %s\n' "$1" >&2
          usage
          exit 2
          ;;
      esac
    done

    validate_version "$(current_version)"
    version="$(current_version)"
    tag="$(release_tag)"
    title="$(release_title)"
    head="$(git -C "$root" rev-parse HEAD)"
    notes="$(extract_release_notes "$version")"

    if [ "$dry_run" = "1" ]; then
      printf 'intended release tag: %s\n' "$tag"
      printf 'intended release title: %s\n' "$title"
      printf 'intended release target: %s\n' "$head"
      printf 'intended release branch: origin/main\n'
    fi

    require_clean_worktree
    require_gh_ready
    require_head_matches_origin_main
    "$script_dir/release.sh" check
    require_origin_tag_missing_or_head "$tag" "$head"

    if [ "$dry_run" != "1" ]; then
      printf 'release tag: %s\n' "$tag"
      printf 'release title: %s\n' "$title"
      printf 'release target: %s\n' "$head"
      printf 'release branch: origin/main\n'
    fi

    if [ "$dry_run" = "1" ]; then
      printf 'dry run: checks passed; would create GitHub release and tag if missing\n'
      exit 0
    fi

    gh release create "$tag" \
      --title "$title" \
      --notes "$notes" \
      --target "$head" \
      --latest \
      --fail-on-no-commits
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
