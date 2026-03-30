#!/usr/bin/env bash
# resolve-common.sh - Shared resolve lifecycle functions for all artifact types
#
# Provides consistent resolve workflow:
#   1. Update frontmatter status field
#   2. Populate resolution metadata (date, notes)
#   3. Move file to resolved/ subfolder (preserving git history, staging included)
#
# Usage: source resolve-common.sh
#
# Dependencies: logging.sh, timestamp-utils.sh, common.sh (for sed_inplace)

# Guard against double-sourcing
[[ -n "${_SPECTRI_RESOLVE_COMMON_LOADED:-}" ]] && return 0
_SPECTRI_RESOLVE_COMMON_LOADED=1

# Source dependencies
RESOLVE_LIB_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$RESOLVE_LIB_DIR/logging.sh"
source "$RESOLVE_LIB_DIR/timestamp-utils.sh"
source "$RESOLVE_LIB_DIR/common.sh"

# ============================================================================
# resolve_update_frontmatter - Update a YAML frontmatter field in a file
#
# Usage: resolve_update_frontmatter <file> <field> <value>
# ============================================================================
resolve_update_frontmatter() {
  local file="$1"
  local field="$2"
  local value="$3"

  if grep -q "^${field}:" "$file" 2>/dev/null; then
    sed_inplace "s/^${field}: .*/${field}: ${value}/" "$file"
  else
    # Field doesn't exist - insert before the closing ---
    sed_inplace "0,/^---$/!{/^---$/i\\
${field}: ${value}
}" "$file"
  fi
}

# ============================================================================
# resolve_move_to_resolved - Move file to resolved/ subfolder
#
# Usage: resolve_move_to_resolved <file> <resolved_dir>
# Returns: 0 on success, 1 on failure
# ============================================================================
resolve_move_to_resolved() {
  local file="$1"
  local resolved_dir="$2"
  local basename
  basename=$(basename "$file")

  mkdir -p "$resolved_dir"

  # Prefer git mv for history preservation, fall back to mv
  if git mv "$file" "$resolved_dir/$basename" 2>/dev/null; then
    return 0
  else
    mv "$file" "$resolved_dir/$basename" || return 1
    git add "$resolved_dir/$basename" 2>/dev/null || true
    git rm --cached "$file" 2>/dev/null || true
    return 0
  fi
}

# ============================================================================
# resolve_print_summary - Print standard resolution summary
#
# Usage: resolve_print_summary <artifact_type> <basename> <status> <date> <dest_dir> [<notes>]
# ============================================================================
resolve_print_summary() {
  local artifact_type="$1"
  local basename="$2"
  local status="$3"
  local date="$4"
  local dest_dir="$5"
  local notes="${6:-}"

  echo "${artifact_type} resolved: $basename"
  echo "  Status: $status"
  echo "  Date: $date"
  if [[ -n "$notes" ]]; then
    echo "  Notes: $notes"
  fi
  echo "  Moved to: $dest_dir/$basename"
}
