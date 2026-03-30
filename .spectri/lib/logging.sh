#!/usr/bin/env bash
# logging.sh
# Centralized logging utilities for Spectri bash scripts
#
# Provides standardized log_error, log_info, log_warn, log_success,
# and verbose functions with consistent formatting, TTY-aware color
# output, and NO_COLOR support.
#
# Usage: source "$SCRIPT_DIR/../../lib/logging.sh"
#
# Environment:
#   NO_COLOR         - Set to disable color output (https://no-color.org/)
#   SPECTRI_QUIET    - Set to "true" to suppress info/success output
#   QUIET            - Alias for SPECTRI_QUIET (backward compat)
#   VERBOSE          - Set to "true" to enable verbose output
#
# Dependencies: None (pure bash)

# Guard against double-sourcing
[[ -n "${_SPECTRI_LOGGING_LOADED:-}" ]] && return 0
_SPECTRI_LOGGING_LOADED=1

# Colors (disabled if not a terminal or NO_COLOR is set)
if [[ -t 1 ]] && [[ -z "${NO_COLOR:-}" ]]; then
    RED='\033[0;31m'
    GREEN='\033[0;32m'
    YELLOW='\033[1;33m'
    BLUE='\033[0;34m'
    NC='\033[0m'
else
    RED=''; GREEN=''; YELLOW=''; BLUE=''; NC=''
fi

log_error() {
    printf "${RED}ERROR:${NC} %s\n" "$*" >&2
}

log_warn() {
    printf "${YELLOW}WARN:${NC} %s\n" "$*" >&2
}

log_info() {
    if [[ "${SPECTRI_QUIET:-${QUIET:-}}" != "true" ]]; then
        printf "${BLUE}INFO:${NC} %s\n" "$*"
    fi
}

log_success() {
    if [[ "${SPECTRI_QUIET:-${QUIET:-}}" != "true" ]]; then
        printf "${GREEN}OK:${NC} %s\n" "$*"
    fi
}

verbose() {
    if [[ "${VERBOSE:-false}" == "true" ]]; then
        printf "${BLUE}VERBOSE:${NC} %s\n" "$*"
    fi
}
