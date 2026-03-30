#!/usr/bin/env bash
# Common functions and variables for all scripts

# Guard against double-sourcing
[[ -n "${_SPECTRI_COMMON_LOADED:-}" ]] && return 0
_SPECTRI_COMMON_LOADED=1

# Get repository root, with fallback for non-git repositories
# Respects PROJECT_ROOT env var for test isolation
get_repo_root() {
    if [[ -n "${PROJECT_ROOT:-}" ]]; then
        echo "$PROJECT_ROOT"
    elif git rev-parse --show-toplevel >/dev/null 2>&1; then
        git rev-parse --show-toplevel
    else
        # Fall back to script location for non-git repos
        local script_dir="$(CDPATH="" cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
        (cd "$script_dir/../../.." && pwd)
    fi
}

# Get current branch, with fallback for non-git repositories
get_current_branch() {
    # First check if SPECIFY_FEATURE environment variable is set
    if [[ -n "${SPECIFY_FEATURE:-}" ]]; then
        echo "$SPECIFY_FEATURE"
        return
    fi

    # Then check git if available
    if git rev-parse --abbrev-ref HEAD >/dev/null 2>&1; then
        git rev-parse --abbrev-ref HEAD
        return
    fi

    # For non-git repos, try to find the latest feature directory
    local repo_root=$(get_repo_root)
    local specs_dir="$repo_root/spectri/specs"

    if [[ -d "$specs_dir" ]]; then
        local latest_feature=""
        local highest=0

        for dir in "$specs_dir"/*; do
            if [[ -d "$dir" ]]; then
                local dirname=$(basename "$dir")
                if [[ "$dirname" =~ ^([0-9]{3})- ]]; then
                    local number=${BASH_REMATCH[1]}
                    number=$((10#$number))
                    if [[ "$number" -gt "$highest" ]]; then
                        highest=$number
                        latest_feature=$dirname
                    fi
                fi
            fi
        done

        if [[ -n "$latest_feature" ]]; then
            echo "$latest_feature"
            return
        fi
    fi

    echo "main"  # Final fallback
}

# Check if we have git available
has_git() {
    git rev-parse --show-toplevel >/dev/null 2>&1
}

check_feature_branch() {
    local branch="$1"
    local has_git_repo="$2"
    local skip_branch_check="${3:-false}"

    # Skip branch check if explicitly requested (branchless mode)
    if [[ "$skip_branch_check" == "true" ]]; then
        return 0
    fi

    # For non-git repos, we can't enforce branch naming but still provide output
    if [[ "$has_git_repo" != "true" ]]; then
        echo "[specify] Warning: Git repository not detected; skipped branch validation" >&2
        return 0
    fi

    if [[ ! "$branch" =~ ^[0-9]{3}- ]]; then
        echo "ERROR: Not on a feature branch. Current branch: $branch" >&2
        echo "Feature branches should be named like: 001-feature-name" >&2
        echo "Tip: Use --spec <spec-folder> to work on a spec without a feature branch" >&2
        return 1
    fi

    return 0
}

get_feature_dir() { find_spec_in_stages "$1" "$2"; }

# Search for a spec folder across all stage subdirectories
# Returns the full path to the spec folder if found, or falls back to specs root
find_spec_in_stages() {
    local repo_root="$1"
    local spec_name="$2"
    local specs_dir="$repo_root/spectri/specs"

    # Search stage subdirectories (01-drafting through 05-archived)
    for dir in "$specs_dir"/0[0-5]-*/"$spec_name"; do
        if [[ -d "$dir" ]]; then
            echo "$dir"
            return
        fi
    done

    # Not found in any stage — return root path as fallback
    echo "$specs_dir/$spec_name"
}

# Find feature directory by numeric prefix instead of exact branch match
# This allows multiple branches to work on the same spec (e.g., 004-fix-bug, 004-add-feature)
find_feature_dir_by_prefix() {
    local repo_root="$1"
    local branch_name="$2"
    local specs_dir="$repo_root/spectri/specs"

    # Extract numeric prefix from branch (e.g., "004" from "004-whatever")
    if [[ ! "$branch_name" =~ ^([0-9]{3})- ]]; then
        # If branch doesn't have numeric prefix, try exact match across stages
        find_spec_in_stages "$repo_root" "$branch_name"
        return
    fi

    local prefix="${BASH_REMATCH[1]}"

    # Search for directories across stage subdirectories that start with this prefix
    local matches=()
    local match_paths=()
    if [[ -d "$specs_dir" ]]; then
        for dir in "$specs_dir"/0[0-5]-*/"$prefix"-*; do
            if [[ -d "$dir" ]]; then
                matches+=("$(basename "$dir")")
                match_paths+=("$dir")
            fi
        done
    fi

    # Handle results
    if [[ ${#matches[@]} -eq 0 ]]; then
        # No match found - return the branch name path (will fail later with clear error)
        echo "$specs_dir/$branch_name"
    elif [[ ${#matches[@]} -eq 1 ]]; then
        # Exactly one match - return full path including stage
        echo "${match_paths[0]}"
    else
        # Multiple matches - this shouldn't happen with proper naming convention
        echo "ERROR: Multiple spec directories found with prefix '$prefix': ${matches[*]}" >&2
        echo "Please ensure only one spec directory exists per numeric prefix." >&2
        echo "$specs_dir/$branch_name"  # Return something to avoid breaking the script
    fi
}

get_feature_paths() {
    local spec_override="${1:-}"
    local repo_root=$(get_repo_root)
    local current_branch=$(get_current_branch)
    local has_git_repo="false"
    local feature_dir=""
    local skip_branch_check="false"

    if has_git; then
        has_git_repo="true"
    fi

    # If spec folder override provided, use it directly
    if [[ -n "$spec_override" ]]; then
        # Handle both full paths and relative spec names
        if [[ "$spec_override" == /* ]]; then
            feature_dir="$spec_override"
        elif [[ "$spec_override" == spectri/specs/* ]]; then
            feature_dir="$repo_root/$spec_override"
        else
            # Search stage subdirectories for the spec folder
            feature_dir=$(find_spec_in_stages "$repo_root" "$spec_override")
        fi
        skip_branch_check="true"
    else
        # Use prefix-based lookup to support multiple branches per spec
        feature_dir=$(find_feature_dir_by_prefix "$repo_root" "$current_branch")
    fi

    cat <<EOF
REPO_ROOT='$repo_root'
CURRENT_BRANCH='$current_branch'
HAS_GIT='$has_git_repo'
FEATURE_DIR='$feature_dir'
FEATURE_SPEC='$feature_dir/spec.md'
IMPL_PLAN='$feature_dir/plan.md'
TASKS='$feature_dir/tasks.md'
RESEARCH='$feature_dir/research.md'
DATA_MODEL='$feature_dir/data-model.md'
QUICKSTART='$feature_dir/quickstart.md'
CONTRACTS_DIR='$feature_dir/contracts'
SKIP_BRANCH_CHECK='$skip_branch_check'
EOF
}

check_file() { [[ -f "$1" ]] && echo "  ✓ $2" || echo "  ✗ $2"; }
check_dir() { [[ -d "$1" && -n $(ls -A "$1" 2>/dev/null) ]] && echo "  ✓ $2" || echo "  ✗ $2"; }

# Portable sed in-place editing (macOS BSD sed vs GNU sed)
# Usage: sed_inplace "s/old/new/" "$FILE"
sed_inplace() {
    if [[ "$OSTYPE" == "darwin"* ]]; then
        sed -i '' "$@"
    else
        sed -i "$@"
    fi
}

