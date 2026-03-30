"""Subprocess wrapper for external tool calls (git, gh, etc.).

Provides a mockable interface for tests and consistent error handling
across all Python modules that need to call external commands.
"""

from __future__ import annotations

import os
import subprocess
from dataclasses import dataclass
from pathlib import Path


@dataclass
class CommandResult:
    """Result of a shell command execution."""

    returncode: int
    stdout: str
    stderr: str

    @property
    def success(self) -> bool:
        return self.returncode == 0


def run(
    args: list[str],
    *,
    cwd: Path | str | None = None,
    env: dict[str, str] | None = None,
    capture: bool = True,
    check: bool = False,
    timeout: int | None = 30,
) -> CommandResult:
    """Run a shell command and return the result.

    Args:
        args: Command and arguments (e.g., ["git", "status"]).
        cwd: Working directory. Defaults to current directory.
        env: Additional environment variables (merged with os.environ).
        capture: Whether to capture stdout/stderr. Defaults to True.
        check: If True, raise on non-zero exit code.
        timeout: Timeout in seconds. None for no timeout.

    Returns:
        CommandResult with returncode, stdout, stderr.

    Raises:
        subprocess.CalledProcessError: If check=True and command fails.
        subprocess.TimeoutExpired: If command exceeds timeout.
    """
    run_env = os.environ.copy()
    if env:
        run_env.update(env)

    result = subprocess.run(
        args,
        cwd=cwd,
        env=run_env,
        capture_output=capture,
        text=True,
        timeout=timeout,
    )

    if check and result.returncode != 0:
        raise subprocess.CalledProcessError(
            result.returncode,
            args,
            output=result.stdout if capture else None,
            stderr=result.stderr if capture else None,
        )

    return CommandResult(
        returncode=result.returncode,
        stdout=result.stdout if capture else "",
        stderr=result.stderr if capture else "",
    )


def git(*args: str, cwd: Path | str | None = None, check: bool = True) -> CommandResult:
    """Run a git command.

    Args:
        *args: Git subcommand and arguments (e.g., "status", "--short").
        cwd: Working directory (should be inside a git repo).
        check: If True (default), raise on non-zero exit code.
    """
    return run(["git", *args], cwd=cwd, check=check)


def gh(*args: str, cwd: Path | str | None = None, check: bool = True) -> CommandResult:
    """Run a GitHub CLI command.

    Args:
        *args: gh subcommand and arguments.
        cwd: Working directory.
        check: If True (default), raise on non-zero exit code.
    """
    return run(["gh", *args], cwd=cwd, check=check)
