"""Change preview and diff tool for template generation."""

import difflib
import shutil
import tempfile
from pathlib import Path
from typing import Any


def generate_unified_diff(file_a: Path, file_b: Path) -> str:
    """
    Generate unified diff between two files.

    Args:
        file_a: Path to first file (existing)
        file_b: Path to second file (generated)

    Returns:
        Unified diff string showing changes
    """
    lines_a = file_a.read_text().splitlines(keepends=True)
    lines_b = file_b.read_text().splitlines(keepends=True)

    diff = difflib.unified_diff(
        lines_a, lines_b, fromfile=str(file_a), tofile=str(file_b), lineterm=""
    )

    return "\n".join(diff)


def compare_directories(existing_dir: Path, generated_dir: Path) -> dict[str, list[Path]]:
    """
    Compare two directories and categorize changes.

    Args:
        existing_dir: Directory with existing output
        generated_dir: Directory with newly generated output

    Returns:
        Dictionary with 'added', 'modified', 'deleted' lists of file paths
    """
    # Get all files in both directories
    existing_files = {
        f.relative_to(existing_dir): f for f in existing_dir.rglob("*") if f.is_file()
    }
    generated_files = {
        f.relative_to(generated_dir): f for f in generated_dir.rglob("*") if f.is_file()
    }

    added = []
    modified = []
    deleted = []

    # Find added and modified files
    for rel_path, gen_file in generated_files.items():
        if rel_path not in existing_files:
            # New file
            added.append(gen_file)
        else:
            # Check if modified
            existing_file = existing_files[rel_path]
            if existing_file.read_text() != gen_file.read_text():
                modified.append(gen_file)

    # Find deleted files
    for rel_path, existing_file in existing_files.items():
        if rel_path not in generated_files:
            deleted.append(existing_file)

    return {"added": added, "modified": modified, "deleted": deleted}


def detect_changes(existing_dir: Path, generated_dir: Path) -> bool:
    """
    Detect if any changes exist between directories.

    Args:
        existing_dir: Directory with existing output
        generated_dir: Directory with newly generated output

    Returns:
        True if changes detected, False if identical
    """
    changes = compare_directories(existing_dir, generated_dir)
    return len(changes["added"]) > 0 or len(changes["modified"]) > 0 or len(changes["deleted"]) > 0


def preview_changes(config_path: Path, target_dir: Path, dry_run: bool = False) -> dict[str, Any]:
    """
    Preview changes before applying them.

    Generates to temporary directory, shows diff, optionally applies changes.

    Args:
        config_path: Path to config YAML file
        target_dir: Target directory for applying changes
        dry_run: If True, show diff but don't apply changes

    Returns:
        Dictionary with change summary and dry_run status
    """
    from scripts.generate_docs import generate_documentation_with_timing

    # Generate to temporary directory
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_output = Path(temp_dir) / "output"
        temp_output.mkdir()

        # Generate documentation
        generate_documentation_with_timing(config_path, temp_output)

        # Compare with existing target
        if not target_dir.exists():
            # No existing output, everything is new
            changes = {
                "added": list(temp_output.rglob("*")),
                "modified": [],
                "deleted": [],
            }
            has_changes = True
        else:
            changes = compare_directories(target_dir, temp_output)
            has_changes = detect_changes(target_dir, temp_output)

        # Apply changes if not dry run and changes exist
        applied = False
        if has_changes and not dry_run:
            # Copy temp output to target
            if target_dir.exists():
                shutil.rmtree(target_dir)
            shutil.copytree(temp_output, target_dir)
            applied = True

        return {
            "changes_detected": has_changes,
            "added": len(changes["added"]),
            "modified": len(changes["modified"]),
            "deleted": len(changes["deleted"]),
            "applied": applied,
            "dry_run": dry_run,
        }
