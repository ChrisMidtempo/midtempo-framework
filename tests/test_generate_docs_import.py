"""Test that CLI entry point scripts can be run directly."""

import subprocess
import sys
from pathlib import Path


def test_generate_docs_imports_work_when_run_as_script():
    """
    Test that generate_docs.py successfully imports when run as a script.

    Reproduces bug where imports fail because sys.path modification happens
    after imports are processed.
    """
    # Get paths
    project_root = Path(__file__).parent.parent
    script_path = project_root / "scripts" / "generate_docs.py"

    # Run the script with minimal args to test imports
    result = subprocess.run(
        [sys.executable, str(script_path)],
        capture_output=True,
        text=True,
        cwd=str(project_root),
    )

    # Should not have import errors
    assert (
        "ModuleNotFoundError" not in result.stderr
    ), f"Import failed when running as script:\n{result.stderr}"
    assert result.returncode in [0, 1], f"Unexpected return code: {result.returncode}"


def test_cli_imports_work_when_run_as_script():
    """
    Test that scripts/cli.py successfully imports when run as a script.

    Verifies the CLI entry point has the correct sys.path setup so that
    imports work when invoked directly (as in the npm generate command).
    """
    project_root = Path(__file__).parent.parent
    script_path = project_root / "scripts" / "cli.py"

    result = subprocess.run(
        [sys.executable, str(script_path), "--help"],
        capture_output=True,
        text=True,
        cwd=str(project_root),
    )

    assert (
        "ModuleNotFoundError" not in result.stderr
    ), f"Import failed when running cli.py as script:\n{result.stderr}"
    assert result.returncode in [0, 1], f"Unexpected return code: {result.returncode}"
