#!/usr/bin/env bash
# validation.sh — Shared validation functions for Spectri scripts
#
# Provides: validate_priority, validate_slug, VALID_PRIORITIES
#
# Usage: source "$SCRIPT_DIR/../../lib/validation.sh"

# Double-sourcing guard
if [[ -n "${_SPECTRI_VALIDATION_SH_LOADED:-}" ]]; then
    return 0
fi
_SPECTRI_VALIDATION_SH_LOADED=1

VALID_PRIORITIES="critical high medium low"

validate_priority() {
    local priority="$1"
    for valid in $VALID_PRIORITIES; do
        if [[ "$priority" == "$valid" ]]; then
            return 0
        fi
    done
    return 1
}

validate_slug() {
    local slug="$1"
    # Check if slug matches kebab-case pattern (lowercase letters, numbers, hyphens)
    if [[ ! "$slug" =~ ^[a-z0-9]+(-[a-z0-9]+)*$ ]]; then
        return 1
    fi
    return 0
}
