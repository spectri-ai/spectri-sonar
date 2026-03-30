#!/usr/bin/env bash
# timestamp-utils.sh
# Portable timestamp generation utilities for Spec Flow
#
# Provides standard timestamp functions for consistent formatting across
# all Spec Flow documentation (implementation summaries, session summaries,
# handoff prompts, research docs, etc.)
#
# Dependencies: Standard Unix date command (macOS/Linux) or PowerShell Get-Date (Windows)
# Platform Support: macOS (BSD date), Linux (GNU date), Windows (via Git Bash/WSL)

# Guard against double-sourcing
[[ -n "${_SPECTRI_TIMESTAMP_UTILS_LOADED:-}" ]] && return 0
_SPECTRI_TIMESTAMP_UTILS_LOADED=1

# Generate ISO 8601 timestamp with timezone
# Format: YYYY-MM-DDTHH:MM:SS+/-HH:MM (e.g., "2026-01-09T12:30:00+11:00")
# Use case: Date Created and Date Updated fields in frontmatter
get_iso_timestamp() {
    date +"%Y-%m-%dT%H:%M:%S%z" | sed 's/\([0-9]\{2\}\)$/:\1/'
}

# Generate filename timestamp
# Format: YYYY-MM-DD-HHMM (e.g., "2026-01-09-1230")
# Use case: Implementation summaries, session summaries, handoff prompts
get_filename_timestamp() {
    date +"%Y-%m-%d-%H%M"
}

# Generate date-only timestamp
# Format: YYYY-MM-DD (e.g., "2026-01-09")
# Use case: Research documents, verification reports
get_date_timestamp() {
    date +"%Y-%m-%d"
}
