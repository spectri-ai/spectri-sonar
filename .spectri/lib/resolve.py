"""Shared resolve lifecycle functions for all artifact types.

Python equivalent of resolve-common.sh. Provides:
- resolve_update_frontmatter: Update a YAML frontmatter field
- resolve_move_to_resolved: Move file to resolved/ subfolder (git-aware)
- resolve_print_summary: Print standard resolution summary
"""

from __future__ import annotations

import re
import subprocess
from pathlib import Path


def resolve_update_frontmatter(file: Path, field: str, value: str) -> None:
    """Update a YAML frontmatter field in a file.

    If the field exists, updates its value. If not, inserts before the closing ---.
    """
    content = file.read_text()
    lines = content.split("\n")

    # Check if field already exists
    field_pattern = re.compile(rf"^{re.escape(field)}: .*$")
    found = False
    for i, line in enumerate(lines):
        if field_pattern.match(line):
            lines[i] = f"{field}: {value}"
            found = True
            break

    if not found:
        # Insert before the closing --- (second occurrence)
        closing_count = 0
        for i, line in enumerate(lines):
            if line.strip() == "---":
                closing_count += 1
                if closing_count == 2:
                    lines.insert(i, f"{field}: {value}")
                    break

    file.write_text("\n".join(lines))


def resolve_move_to_resolved(file: Path, resolved_dir: Path) -> bool:
    """Move file to resolved/ subfolder, preserving git history.

    Returns True on success, False on failure.
    """
    resolved_dir.mkdir(parents=True, exist_ok=True)
    dest = resolved_dir / file.name

    # Prefer git mv for history preservation
    try:
        subprocess.run(
            ["git", "mv", str(file), str(dest)],
            capture_output=True, check=True,
        )
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass

    # Fall back to regular mv + git staging
    try:
        file.rename(dest)
        subprocess.run(["git", "add", str(dest)], capture_output=True)
        subprocess.run(["git", "rm", "--cached", str(file)], capture_output=True)
        return True
    except OSError:
        return False


def resolve_print_summary(
    artifact_type: str,
    basename: str,
    status: str,
    date: str,
    dest_dir: str,
    notes: str = "",
) -> str:
    """Format standard resolution summary.

    Returns the summary as a string (also prints it).
    """
    lines = [
        f"{artifact_type} resolved: {basename}",
        f"  Status: {status}",
        f"  Date: {date}",
    ]
    if notes:
        lines.append(f"  Notes: {notes}")
    lines.append(f"  Moved to: {dest_dir}/{basename}")

    summary = "\n".join(lines)
    print(summary)
    return summary
