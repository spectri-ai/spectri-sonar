"""Repository detection and feature path resolution.

Python equivalent of common.sh. Leverages paths.py where it overlaps.
"""

from __future__ import annotations

import os
import platform
import re
import subprocess
from pathlib import Path


def get_repo_root() -> Path:
    """Get repository root, with fallback for non-git repos.

    Respects PROJECT_ROOT env var for test isolation.
    """
    project_root = os.environ.get("PROJECT_ROOT")
    if project_root:
        return Path(project_root)

    try:
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True, text=True, check=True,
        )
        return Path(result.stdout.strip())
    except (subprocess.CalledProcessError, FileNotFoundError):
        # Fall back to module location (matches common.sh fallback)
        return Path(__file__).resolve().parent.parent.parent.parent


def get_current_branch() -> str:
    """Get current git branch, with fallback for non-git repos.

    Respects SPECIFY_FEATURE env var override.
    """
    specify_feature = os.environ.get("SPECIFY_FEATURE")
    if specify_feature:
        return specify_feature

    try:
        result = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            capture_output=True, text=True, check=True,
        )
        return result.stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass

    # For non-git repos, find latest feature directory
    repo_root = get_repo_root()
    specs_dir = repo_root / "spectri" / "specs"

    if specs_dir.is_dir():
        highest = 0
        latest_feature = ""
        for d in specs_dir.iterdir():
            if d.is_dir():
                match = re.match(r"^(\d{3})-", d.name)
                if match:
                    number = int(match.group(1))
                    if number > highest:
                        highest = number
                        latest_feature = d.name

        if latest_feature:
            return latest_feature

    return "main"


def has_git() -> bool:
    """Check if we're inside a git repository."""
    try:
        subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True, check=True,
        )
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def check_feature_branch(
    branch: str, has_git_repo: bool, skip_branch_check: bool = False
) -> tuple[bool, str]:
    """Validate feature branch naming.

    Returns (ok, error_message). ok=True means branch is valid or check was skipped.
    """
    if skip_branch_check:
        return True, ""

    if not has_git_repo:
        return True, "Warning: Git repository not detected; skipped branch validation"

    if not re.match(r"^\d{3}-", branch):
        return False, (
            f"ERROR: Not on a feature branch. Current branch: {branch}\n"
            "Feature branches should be named like: 001-feature-name\n"
            "Tip: Use --spec <spec-folder> to work on a spec without a feature branch"
        )

    return True, ""


def find_spec_in_stages(repo_root: Path, spec_name: str) -> Path:
    """Search for a spec folder across all stage subdirectories.

    Returns the full path if found, or falls back to specs root.
    """
    specs_dir = repo_root / "spectri" / "specs"

    # Search stage subdirectories (00-* through 05-*)
    for stage_dir in sorted(specs_dir.glob("0[0-5]-*")):
        candidate = stage_dir / spec_name
        if candidate.is_dir():
            return candidate

    return specs_dir / spec_name


def find_feature_dir_by_prefix(repo_root: Path, branch_name: str) -> Path:
    """Find feature directory by numeric prefix.

    Allows multiple branches to work on the same spec.
    """
    specs_dir = repo_root / "spectri" / "specs"

    match = re.match(r"^(\d{3})-", branch_name)
    if not match:
        return find_spec_in_stages(repo_root, branch_name)

    prefix = match.group(1)
    matches: list[Path] = []

    if specs_dir.is_dir():
        for stage_dir in sorted(specs_dir.glob("0[0-5]-*")):
            for d in stage_dir.iterdir():
                if d.is_dir() and d.name.startswith(f"{prefix}-"):
                    matches.append(d)

    if len(matches) == 0:
        return specs_dir / branch_name
    elif len(matches) == 1:
        return matches[0]
    else:
        import sys
        names = [m.name for m in matches]
        print(
            f"ERROR: Multiple spec directories found with prefix '{prefix}': {' '.join(names)}",
            file=sys.stderr,
        )
        print("Please ensure only one spec directory exists per numeric prefix.", file=sys.stderr)
        return specs_dir / branch_name


def get_feature_paths(spec_override: str = "") -> dict[str, str]:
    """Get all feature-related paths.

    Returns a dict with keys: REPO_ROOT, CURRENT_BRANCH, HAS_GIT,
    FEATURE_DIR, FEATURE_SPEC, IMPL_PLAN, TASKS, RESEARCH,
    DATA_MODEL, QUICKSTART, CONTRACTS_DIR, SKIP_BRANCH_CHECK.
    """
    repo_root = get_repo_root()
    current_branch = get_current_branch()
    has_git_repo = has_git()
    skip_branch_check = False

    if spec_override:
        spec_path = Path(spec_override)
        if spec_path.is_absolute():
            feature_dir = spec_path
        elif spec_override.startswith("spectri/specs/"):
            feature_dir = repo_root / spec_override
        else:
            feature_dir = find_spec_in_stages(repo_root, spec_override)
        skip_branch_check = True
    else:
        feature_dir = find_feature_dir_by_prefix(repo_root, current_branch)

    fd = str(feature_dir)
    return {
        "REPO_ROOT": str(repo_root),
        "CURRENT_BRANCH": current_branch,
        "HAS_GIT": str(has_git_repo).lower(),
        "FEATURE_DIR": fd,
        "FEATURE_SPEC": f"{fd}/spec.md",
        "IMPL_PLAN": f"{fd}/plan.md",
        "TASKS": f"{fd}/tasks.md",
        "RESEARCH": f"{fd}/research.md",
        "DATA_MODEL": f"{fd}/data-model.md",
        "QUICKSTART": f"{fd}/quickstart.md",
        "CONTRACTS_DIR": f"{fd}/contracts",
        "SKIP_BRANCH_CHECK": str(skip_branch_check).lower(),
    }


def sed_inplace(pattern: str, filepath: Path) -> None:
    """Portable sed in-place editing.

    Applies a sed substitution pattern to a file in-place.
    """
    if platform.system() == "Darwin":
        subprocess.run(["sed", "-i", "", pattern, str(filepath)], check=True)
    else:
        subprocess.run(["sed", "-i", pattern, str(filepath)], check=True)
