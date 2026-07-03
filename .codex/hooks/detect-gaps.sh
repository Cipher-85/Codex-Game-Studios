#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd "$(dirname "$0")" && pwd -P)"
source "$script_dir/../lib/hooks.sh"

echo "=== Checking for Documentation Gaps ==="

fresh_project=true

tech_prefs="$ccgs_root/.codex/docs/technical-preferences.md"
if [ -f "$tech_prefs" ]; then
  engine_line="$(grep -E '^- \*\*Engine\*\*:' "$tech_prefs" 2>/dev/null || true)"
  if [ -n "$engine_line" ] && ! printf '%s\n' "$engine_line" | grep -q "TO BE CONFIGURED" 2>/dev/null; then
    fresh_project=false
  fi
fi

if [ -f "$ccgs_root/design/gdd/game-concept.md" ]; then
  fresh_project=false
fi

if [ -d "$ccgs_root/src" ]; then
  src_check="$(find "$ccgs_root/src" -type f \( -name '*.gd' -o -name '*.cs' -o -name '*.cpp' -o -name '*.c' -o -name '*.h' -o -name '*.hpp' -o -name '*.rs' -o -name '*.py' -o -name '*.js' -o -name '*.ts' \) 2>/dev/null | head -1 || true)"
  if [ -n "$src_check" ]; then
    fresh_project=false
  fi
fi

if [ "$fresh_project" = true ]; then
  echo ""
  echo "NEW PROJECT: No engine configured, no game concept, no source code."
  echo "   This looks like a fresh start. Run: \$start"
  echo ""
  echo "To get a comprehensive project analysis, run: \$project-stage-detect"
  echo "==================================="
  exit 0
fi

if [ -d "$ccgs_root/src" ]; then
  src_files="$(find "$ccgs_root/src" -type f \( -name '*.gd' -o -name '*.cs' -o -name '*.cpp' -o -name '*.c' -o -name '*.h' -o -name '*.hpp' -o -name '*.rs' -o -name '*.py' -o -name '*.js' -o -name '*.ts' \) 2>/dev/null | wc -l | tr -d ' ')"
else
  src_files=0
fi

if [ -d "$ccgs_root/design/gdd" ]; then
  design_files="$(find "$ccgs_root/design/gdd" -type f -name '*.md' 2>/dev/null | wc -l | tr -d ' ')"
else
  design_files=0
fi

if [ "$src_files" -gt 50 ] && [ "$design_files" -lt 5 ]; then
  echo "WARNING: Substantial codebase ($src_files source files) but sparse design docs ($design_files files)"
  echo "    Suggested action: \$reverse-document design src/[system]"
  echo "    Or run: \$project-stage-detect to get full analysis"
fi

if [ -d "$ccgs_root/prototypes" ]; then
  undocumented_protos=()
  while IFS= read -r proto_dir; do
    [ -n "$proto_dir" ] || continue
    if [ ! -f "$proto_dir/README.md" ] && [ ! -f "$proto_dir/CONCEPT.md" ]; then
      undocumented_protos+=("$(basename "$proto_dir")")
    fi
  done < <(find "$ccgs_root/prototypes" -mindepth 1 -maxdepth 1 -type d 2>/dev/null)

  if [ "${#undocumented_protos[@]}" -gt 0 ]; then
    echo "WARNING: ${#undocumented_protos[@]} undocumented prototype(s) found:"
    for proto in "${undocumented_protos[@]}"; do
      echo "    - prototypes/$proto/ (no README or CONCEPT doc)"
    done
    echo "    Suggested action: \$reverse-document concept prototypes/[name]"
  fi
fi

if [ -d "$ccgs_root/src/core" ] || [ -d "$ccgs_root/src/engine" ]; then
  if [ ! -d "$ccgs_root/docs/architecture" ]; then
    echo "WARNING: Core engine/systems exist but no docs/architecture/ directory"
    echo "    Suggested action: Create docs/architecture/ and run \$architecture-decision"
  else
    adr_count="$(find "$ccgs_root/docs/architecture" -type f -name '*.md' 2>/dev/null | wc -l | tr -d ' ')"
    if [ "$adr_count" -lt 3 ]; then
      echo "WARNING: Core systems exist but only $adr_count ADR(s) documented"
      echo "    Suggested action: \$reverse-document architecture src/core/[system]"
    fi
  fi
fi

if [ -d "$ccgs_root/src/gameplay" ]; then
  while IFS= read -r system_dir; do
    [ -n "$system_dir" ] || continue
    system_name="$(basename "$system_dir")"
    file_count="$(find "$system_dir" -type f 2>/dev/null | wc -l | tr -d ' ')"
    if [ "$file_count" -ge 5 ]; then
      design_doc_1="$ccgs_root/design/gdd/${system_name}-system.md"
      design_doc_2="$ccgs_root/design/gdd/${system_name}.md"
      if [ ! -f "$design_doc_1" ] && [ ! -f "$design_doc_2" ]; then
        echo "WARNING: Gameplay system 'src/gameplay/$system_name/' ($file_count files) has no design doc"
        echo "    Expected: design/gdd/${system_name}-system.md or design/gdd/${system_name}.md"
        echo "    Suggested action: \$reverse-document design src/gameplay/$system_name"
      fi
    fi
  done < <(find "$ccgs_root/src/gameplay" -mindepth 1 -maxdepth 1 -type d 2>/dev/null)
fi

if [ "$src_files" -gt 100 ]; then
  if [ ! -d "$ccgs_root/production/sprints" ] && [ ! -d "$ccgs_root/production/milestones" ]; then
    echo "WARNING: Large codebase ($src_files files) but no production planning found"
    echo "    Suggested action: \$sprint-plan or create production/ directory"
  fi
fi

echo ""
echo "To get a comprehensive project analysis, run: \$project-stage-detect"
echo "==================================="
exit 0
