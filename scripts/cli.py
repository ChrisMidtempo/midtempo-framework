"""CLI entry point for documentation generation."""

import sys
from pathlib import Path

# Add parent directory to path for direct script execution
if __name__ == "__main__":
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))

from scripts.generate_docs import generate_documentation_with_timing


def _cli_main() -> int:
    """
    CLI entry point for documentation generation.

    Returns:
        0 on success, 1 on failure
    """
    import argparse

    parser = argparse.ArgumentParser(
        description="Generate midtempo framework documentation from templates"
    )

    parser.add_argument(
        "--config",
        "-c",
        type=Path,
        required=True,
        help="Path to config YAML file",
    )

    parser.add_argument(
        "--output",
        "-o",
        type=Path,
        required=True,
        help="Output directory for generated files",
    )

    args = parser.parse_args()

    # Validate config file exists
    if not args.config.exists():
        print(f"Error: Config file not found: {args.config}", file=sys.stderr)
        return 1

    try:
        result = generate_documentation_with_timing(args.config, args.output)
        print(f"✓ Generated {result['file_count']} files in {result['elapsed']:.2f}s")
        return 0

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(_cli_main())
