#!/usr/bin/env python3
"""Validate docstring presence on all public functions and classes.

Checks that all public exports in scripts/ have docstrings. Exits with code 1
if any are missing.
"""

import ast
import sys
from pathlib import Path


def find_undocumented(scripts_dir: Path) -> list[str]:
    """
    Find all public functions and classes without docstrings.

    Args:
        scripts_dir: Path to scripts directory to scan

    Returns:
        List of strings in format "file.py:line:name" for undocumented items
    """
    undocumented = []

    for py_file in scripts_dir.glob("*.py"):
        if py_file.name == "__init__.py":
            continue

        with py_file.open() as f:
            try:
                tree = ast.parse(f.read(), filename=str(py_file))
            except SyntaxError:
                continue

        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                docstring = ast.get_docstring(node)

                if docstring is None:
                    # Skip private functions/classes (starting with _)
                    # unless they're dunder methods (__init__, __str__, etc.)
                    if node.name.startswith("_") and not (
                        node.name.startswith("__") and node.name.endswith("__")
                    ):
                        continue

                    undocumented.append(f"{py_file.name}:{node.lineno}:{node.name}")

    return sorted(undocumented)


def main() -> int:
    """
    Validate documentation coverage in scripts directory.

    Returns:
        Exit code: 0 if all public items documented, 1 if any missing
    """
    project_root = Path(__file__).parent.parent
    scripts_dir = project_root / "scripts"

    if not scripts_dir.exists():
        print(f"Error: scripts directory not found at {scripts_dir}", file=sys.stderr)
        return 1

    undocumented = find_undocumented(scripts_dir)

    if undocumented:
        print(f"❌ Found {len(undocumented)} undocumented public functions/classes:\n")
        for item in undocumented:
            print(f"  {item}")
        print("\nAll public functions and classes must have docstrings.")
        return 1

    print("✅ All public functions and classes have docstrings!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
