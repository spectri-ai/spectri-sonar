#!/usr/bin/env bash
# filename-utils.sh
# Filename generation utilities for Spectri
#
# Provides standardized slug and filename generation functions used across
# scripts that create ADRs, RFCs, threads, specs, and other named artifacts.
#
# Dependencies: sed, tr (standard Unix utilities)

# Guard against double-sourcing
[[ -n "${_SPECTRI_FILENAME_UTILS_LOADED:-}" ]] && return 0
_SPECTRI_FILENAME_UTILS_LOADED=1

# Convert a string to a lowercase kebab-case slug
# Input:  Any string (e.g., "My Feature Title")
# Output: Lowercase kebab-case (e.g., "my-feature-title")
# Steps:  lowercase → non-alphanumeric to hyphens → collapse multiples → trim edges
slugify() {
    local input="$1"
    echo "$input" \
        | tr '[:upper:]' '[:lower:]' \
        | sed 's/[^a-z0-9]/-/g' \
        | sed 's/-\{2,\}/-/g' \
        | sed 's/^-//; s/-$//'
}
