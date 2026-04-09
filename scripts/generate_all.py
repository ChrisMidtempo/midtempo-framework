"""Parallel batch generation coordinator for multiple repositories."""

from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path
from typing import Any

import yaml


def generate_single_repo(
    repo_path: str, config_path: str, output_dir: str
) -> tuple[str, bool, str | None]:
    """
    Generate documentation for a single repository.

    Worker function executed by ProcessPoolExecutor for parallel generation.

    Args:
        repo_path: Path to repository directory
        config_path: Path to config YAML file
        output_dir: Directory to write generated documentation

    Returns:
        Tuple of (repo_path, success, error_message)
    """
    try:
        from scripts.generate_docs import generate_documentation_with_timing

        # Convert strings to Path objects
        config_path_obj = Path(config_path)
        output_dir_obj = Path(output_dir)

        # Generate documentation (this will validate config and generate files)
        generate_documentation_with_timing(config_path_obj, output_dir_obj)

        # Success
        return (repo_path, True, None)

    except Exception as e:
        # Failure - return error message
        return (repo_path, False, str(e))


def batch_generate(manifest_path: Path, worker_count: int = 4) -> dict[str, Any]:
    """
    Generate documentation for multiple repositories in parallel.

    Reads manifest file listing repos, spawns worker pool, processes repos in parallel.

    Args:
        manifest_path: Path to YAML manifest file with repos list
        worker_count: Number of parallel workers (default 4)

    Returns:
        Dictionary with total, succeeded, failed counts and failure details
    """
    # Load manifest
    with manifest_path.open() as f:
        manifest_data = yaml.safe_load(f)

    repos = manifest_data.get("repos", [])

    # Handle empty manifest
    if not repos:
        return {"total": 0, "succeeded": 0, "failed": 0, "failures": []}

    # Process repos in parallel
    successes = []
    failures = []

    with ProcessPoolExecutor(max_workers=worker_count) as executor:
        # Submit all jobs
        futures = {}
        for repo in repos:
            repo_path = repo["path"]
            config_path = repo["config"]
            output_dir = repo["output"]

            future = executor.submit(generate_single_repo, repo_path, config_path, output_dir)
            futures[future] = repo

        # Collect results as they complete
        for future in as_completed(futures):
            repo = futures[future]
            try:
                repo_path, success, error = future.result()

                if success:
                    successes.append(repo_path)
                else:
                    failures.append({"path": repo_path, "error": error})

            except Exception as e:
                # Handle unexpected exceptions from worker
                failures.append({"path": repo["path"], "error": str(e)})

    return {
        "total": len(repos),
        "succeeded": len(successes),
        "failed": len(failures),
        "failures": failures,
    }


def _cli_main() -> int:
    """
    CLI entry point for batch generation.

    Returns:
        0 on success (all repos succeeded), 1 on failure (any repo failed)
    """
    import argparse
    import sys

    # Add parent directory to path for direct script execution
    if __name__ == "__main__":
        script_dir = Path(__file__).parent
        project_root = script_dir.parent
        if str(project_root) not in sys.path:
            sys.path.insert(0, str(project_root))

    parser = argparse.ArgumentParser(
        description="Generate documentation for multiple repositories in parallel"
    )

    parser.add_argument(
        "--manifest",
        "-m",
        type=Path,
        required=True,
        help="Path to YAML manifest file listing repositories",
    )

    parser.add_argument(
        "--workers",
        "-w",
        type=int,
        default=4,
        help="Number of parallel workers (default: 4)",
    )

    args = parser.parse_args()

    # Validate manifest file exists
    if not args.manifest.exists():
        print(f"Error: Manifest file not found: {args.manifest}", file=sys.stderr)
        return 1

    try:
        result = batch_generate(args.manifest, args.workers)

        print(
            f"✓ Processed {result['total']} repositories: {result['succeeded']} succeeded, {result['failed']} failed"
        )

        if result["failures"]:
            print("\nFailures:")
            for failure in result["failures"]:
                print(f"  - {failure['path']}: {failure['error']}")
            return 1

        return 0

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    import sys

    sys.exit(_cli_main())
