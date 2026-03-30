---
Date Created: 2026-02-12T20:38:00+11:00
Date Updated: 2026-02-13T17:00:00+11:00
---

# Bash Shared Libraries

Reusable bash utilities sourced by scripts via `source "$SCRIPT_DIR/../../lib/<library>.sh"`.

- **common.sh** — Repository root detection, feature path resolution, branch validation
- **filename-utils.sh** — Slug generation and filename construction for kebab-case artifacts
- **logging.sh** — Standardized log_error/log_warn/log_info/log_success with TTY-aware color and NO_COLOR support
- **timestamp-utils.sh** — Portable ISO 8601, filename-safe, and date-only timestamp generation

All libraries have double-sourcing guards. See [spec 062](../../../spectri/specs/04-deployed/062-bash-shared-libraries/spec.md) for full requirements, acceptance criteria, and architecture decisions.
