"""Shared validation functions for Spectri.

Python equivalent of validation.sh. Provides priority and slug validation.
"""

from __future__ import annotations

import re

VALID_PRIORITIES = ("critical", "high", "medium", "low")


def validate_priority(priority: str) -> bool:
    """Check if priority is one of: critical, high, medium, low."""
    return priority in VALID_PRIORITIES


def validate_slug(slug: str) -> bool:
    """Check if slug matches kebab-case pattern (lowercase letters, numbers, hyphens)."""
    return bool(re.match(r"^[a-z0-9]+(-[a-z0-9]+)*$", slug))
