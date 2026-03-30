"""Centralized logging utilities for Spectri Python scripts.

Python equivalent of logging.sh. Provides standardized log functions
with TTY-aware color output, NO_COLOR support, SPECTRI_QUIET, and VERBOSE.
"""

from __future__ import annotations

import os
import sys


def _use_color(stream=None) -> bool:
    """Check if color output should be used."""
    if os.environ.get("NO_COLOR"):
        return False
    if stream is None:
        stream = sys.stdout
    return hasattr(stream, "isatty") and stream.isatty()


# ANSI color codes
_RED = "\033[0;31m"
_GREEN = "\033[0;32m"
_YELLOW = "\033[1;33m"
_BLUE = "\033[0;34m"
_NC = "\033[0m"


def _is_quiet() -> bool:
    """Check if quiet mode is active."""
    return os.environ.get("SPECTRI_QUIET", os.environ.get("QUIET", "")) == "true"


def _colorize(color: str, text: str, stream) -> str:
    """Apply color to text if color output is enabled."""
    if _use_color(stream):
        return f"{color}{text}{_NC}"
    return text


def log_error(*args: object) -> None:
    """Print error message to stderr. Never suppressed by quiet mode."""
    msg = " ".join(str(a) for a in args)
    prefix = _colorize(_RED, "ERROR:", sys.stderr)
    print(f"{prefix} {msg}", file=sys.stderr)


def log_warn(*args: object) -> None:
    """Print warning message to stderr. Never suppressed by quiet mode."""
    msg = " ".join(str(a) for a in args)
    prefix = _colorize(_YELLOW, "WARN:", sys.stderr)
    print(f"{prefix} {msg}", file=sys.stderr)


def log_info(*args: object) -> None:
    """Print info message to stdout. Suppressed when SPECTRI_QUIET=true."""
    if _is_quiet():
        return
    msg = " ".join(str(a) for a in args)
    prefix = _colorize(_BLUE, "INFO:", sys.stdout)
    print(f"{prefix} {msg}")


def log_success(*args: object) -> None:
    """Print success message to stdout. Suppressed when SPECTRI_QUIET=true."""
    if _is_quiet():
        return
    msg = " ".join(str(a) for a in args)
    prefix = _colorize(_GREEN, "OK:", sys.stdout)
    print(f"{prefix} {msg}")


def verbose(*args: object) -> None:
    """Print verbose/debug message. Only shown when VERBOSE=true."""
    if os.environ.get("VERBOSE", "false") != "true":
        return
    msg = " ".join(str(a) for a in args)
    prefix = _colorize(_BLUE, "VERBOSE:", sys.stdout)
    print(f"{prefix} {msg}")
