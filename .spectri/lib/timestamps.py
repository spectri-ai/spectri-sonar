"""Timestamp generation utilities for Spectri.

Python equivalent of timestamp-utils.sh. Provides consistent timestamp
formatting across all Spectri artifacts.
"""

from __future__ import annotations

from datetime import datetime, timezone


def get_iso_timestamp() -> str:
    """Generate ISO 8601 timestamp with timezone.

    Format: YYYY-MM-DDTHH:MM:SS+HH:MM (e.g., "2026-01-09T12:30:00+00:00")
    """
    now = datetime.now(timezone.utc)
    return now.strftime("%Y-%m-%dT%H:%M:%S") + _format_utc_offset(now)


def get_filename_timestamp() -> str:
    """Generate filename-safe timestamp.

    Format: YYYY-MM-DD-HHMM (e.g., "2026-01-09-1230")
    """
    now = datetime.now(timezone.utc)
    return now.strftime("%Y-%m-%d-%H%M")


def get_date_timestamp() -> str:
    """Generate date-only timestamp.

    Format: YYYY-MM-DD (e.g., "2026-01-09")
    """
    now = datetime.now(timezone.utc)
    return now.strftime("%Y-%m-%d")


def _format_utc_offset(dt: datetime) -> str:
    """Format UTC offset as +HH:MM or -HH:MM."""
    offset = dt.utcoffset()
    if offset is None:
        return "+00:00"
    total_seconds = int(offset.total_seconds())
    sign = "+" if total_seconds >= 0 else "-"
    total_seconds = abs(total_seconds)
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    return f"{sign}{hours:02d}:{minutes:02d}"
