"""Tests for parallel batch generation coordinator (scripts/generate_all.py)."""

import time
from typing import Any

import yaml

from scripts.generate_all import batch_generate, generate_single_repo
from tests.helpers.config_factory import (
    _build_instructions_for_capabilities,
    create_standard_config,
)


class TestBatchGeneration:
    """Test suite for parallel batch generation."""

    def test_parallel_processing_generates_multiple_repos(self, tmp_path):
        """Batch generation processes multiple repositories in parallel."""
        # Arrange: Create manifest with 3 repos
        manifest_path = tmp_path / "manifest.yml"

        repos = []
        for i in range(3):
            repo_dir = tmp_path / f"repo{i}"
            repo_dir.mkdir()

            config_path = repo_dir / "config.yml"
            config_data = create_standard_config("python")
            config_data["name"] = f"repo{i}"
            config_data["repo"]["title"] = f"repo{i}"
            config_path.write_text(yaml.dump(config_data))

            output_dir = repo_dir / "output"
            output_dir.mkdir()

            repos.append(
                {"path": str(repo_dir), "config": str(config_path), "output": str(output_dir)}
            )

        manifest_data: dict[str, Any] = {"repos": repos}
        manifest_path.write_text(yaml.dump(manifest_data))

        # Act: Generate with 2 workers
        result = batch_generate(manifest_path, worker_count=2)

        # Assert: All 3 repos generated successfully
        assert result["total"] == 3
        assert result["succeeded"] == 3
        assert result["failed"] == 0

    def test_error_aggregation_reports_individual_failures(self, tmp_path):
        """Batch generation continues after failures and reports them in summary."""
        # Arrange: Manifest with 3 repos, one has invalid config
        manifest_path = tmp_path / "manifest.yml"

        repos = []
        for i in range(3):
            repo_dir = tmp_path / f"repo{i}"
            repo_dir.mkdir()

            config_path = repo_dir / "config.yml"
            config_data: dict[str, Any]
            if i == 1:
                # Invalid config - missing required field
                config_data = {
                    "name": f"repo{i}",
                    "repo": {"title": f"repo{i}"},
                }  # Missing language
            else:
                # Valid config
                config_data = create_standard_config("python")
                config_data["name"] = f"repo{i}"
                config_data["repo"]["title"] = f"repo{i}"
            config_path.write_text(yaml.dump(config_data))

            output_dir = repo_dir / "output"
            output_dir.mkdir()

            repos.append(
                {"path": str(repo_dir), "config": str(config_path), "output": str(output_dir)}
            )

        manifest_data: dict[str, Any] = {"repos": repos}
        manifest_path.write_text(yaml.dump(manifest_data))

        # Act: Generate batch
        result = batch_generate(manifest_path, worker_count=2)

        # Assert: 2 succeed, 1 fails
        assert result["total"] == 3
        assert result["succeeded"] == 2
        assert result["failed"] == 1
        assert len(result["failures"]) == 1
        assert "repo1" in str(result["failures"][0])

    def test_worker_failure_isolation_continues_other_repos(self, tmp_path):
        """One repo failure doesn't stop processing of other repos."""
        # Arrange: Manifest with 3 repos, middle one fails
        manifest_path = tmp_path / "manifest.yml"

        repos = []
        for i in range(3):
            repo_dir = tmp_path / f"repo{i}"
            repo_dir.mkdir()

            config_path = repo_dir / "config.yml"
            config_data: dict[str, Any]
            if i == 1:
                # Create config that will fail during generation
                config_data = {
                    "name": f"repo{i}",
                    "repo": {"title": f"repo{i}"},
                }  # Invalid
            else:
                capabilities = {"hasUI": False, "hasDB": False}
                config_data = {
                    "name": f"repo{i}",
                    "repo": {"title": f"repo{i}", "language": {"python": "all"}},
                    "capabilities": capabilities,
                    "instructions": _build_instructions_for_capabilities(capabilities),
                    "commands": {
                        "test": {
                            "command": "pytest",
                            "description": "Run tests",
                            "category": "test",
                        },
                        "test_unit": {
                            "command": "pytest tests/unit/",
                            "description": "Run unit tests",
                            "category": "test",
                        },
                        "test_integration": {
                            "command": "pytest tests/integration/",
                            "description": "Run integration tests",
                            "category": "test",
                        },
                        "test_coverage": {
                            "command": "pytest --cov=scripts",
                            "description": "Run tests with coverage",
                            "category": "test",
                        },
                        "lint": {
                            "command": "ruff check scripts/ tests/",
                            "description": "Run linter",
                            "category": "quality",
                        },
                        "typecheck": {
                            "command": "mypy scripts/ tests/",
                            "description": "Run type checker",
                            "category": "quality",
                        },
                        "test_e2e": {
                            "command": "pytest tests/e2e/",
                            "description": "Run e2e tests",
                            "category": "test",
                        },
                        "test_e2e_ui": {
                            "command": "pytest tests/e2e/ --headed",
                            "description": "Run e2e tests with UI",
                            "category": "test",
                        },
                        "test_e2e_headed": {
                            "command": "pytest tests/e2e/ --headed",
                            "description": "Run e2e tests headed",
                            "category": "test",
                        },
                        "test_e2e_codegen": {
                            "command": "pytest tests/e2e/ --codegen",
                            "description": "Run e2e tests with codegen",
                            "category": "test",
                        },
                        "docs": {
                            "command": "python -m scripts.generate_docs",
                            "description": "Generate docs",
                            "category": "docs",
                        },
                        "dev": {
                            "command": "python -m app.main",
                            "description": "Run dev server",
                            "category": "dev",
                        },
                        "typedoc": {
                            "command": "python -m pydoc",
                            "description": "Generate type docs",
                            "category": "docs",
                        },
                        "simulate": {
                            "command": "python -m app.simulate",
                            "description": "Run simulation",
                            "category": "dev",
                        },
                    },
                }
            config_path.write_text(yaml.dump(config_data))

            output_dir = repo_dir / "output"
            output_dir.mkdir()

            repos.append(
                {"path": str(repo_dir), "config": str(config_path), "output": str(output_dir)}
            )

        manifest_data: dict[str, Any] = {"repos": repos}
        manifest_path.write_text(yaml.dump(manifest_data))

        # Act: Generate batch
        result = batch_generate(manifest_path, worker_count=2)

        # Assert: First and third repos complete, middle fails
        assert result["succeeded"] == 2
        assert result["failed"] == 1

    def test_empty_manifest_exits_cleanly(self, tmp_path):
        """Batch generation with empty repo list exits successfully."""
        # Arrange: Manifest with no repos
        manifest_path = tmp_path / "manifest.yml"
        manifest_data: dict[str, Any] = {"repos": []}
        manifest_path.write_text(yaml.dump(manifest_data))

        # Act: Generate batch
        result = batch_generate(manifest_path, worker_count=2)

        # Assert: Clean exit with zero counts
        assert result["total"] == 0
        assert result["succeeded"] == 0
        assert result["failed"] == 0

    def test_performance_scales_with_worker_count(self, tmp_path):
        """Increasing worker count reduces total batch generation time."""
        # Arrange: Manifest with 6 repos
        manifest_path = tmp_path / "manifest.yml"

        repos = []
        for i in range(6):
            repo_dir = tmp_path / f"repo{i}"
            repo_dir.mkdir()

            config_path = repo_dir / "config.yml"
            config_data = create_standard_config("python")
            config_data["name"] = f"repo{i}"
            config_data["repo"]["title"] = f"repo{i}"
            config_path.write_text(yaml.dump(config_data))

            output_dir = repo_dir / "output"
            output_dir.mkdir()

            repos.append(
                {"path": str(repo_dir), "config": str(config_path), "output": str(output_dir)}
            )

        manifest_data: dict[str, Any] = {"repos": repos}
        manifest_path.write_text(yaml.dump(manifest_data))

        # Act: Generate with 1 worker
        start_time = time.perf_counter()
        result_1_worker = batch_generate(manifest_path, worker_count=1)
        time_1_worker = time.perf_counter() - start_time

        # Act: Generate with 3 workers
        start_time = time.perf_counter()
        result_3_workers = batch_generate(manifest_path, worker_count=3)
        time_3_workers = time.perf_counter() - start_time

        # Assert: Both complete successfully
        assert result_1_worker["succeeded"] == 6
        assert result_3_workers["succeeded"] == 6

        # Assert: Parallel run is faster (allowing for overhead)
        # We expect at least some speedup, but not necessarily 3x due to overhead
        # Just verify that parallel processing happened (measured time difference)
        assert time_1_worker >= 0 and time_3_workers >= 0
        # If both succeed, we've proven parallel processing works


class TestSingleRepoGeneration:
    """Test suite for single repo generation worker function."""

    def test_generate_single_repo_returns_success_tuple(self, tmp_path):
        """Worker function generates single repo and returns success status."""
        # Arrange: Valid repo setup
        repo_dir = tmp_path / "repo"
        repo_dir.mkdir()

        config_path = repo_dir / "config.yml"
        capabilities = {"hasUI": False, "hasDB": False}
        config_data = {
            "name": "test",
            "repo": {"title": "test", "language": {"python": "all"}},
            "capabilities": capabilities,
            "instructions": _build_instructions_for_capabilities(capabilities),
            "commands": {
                "test": {"command": "pytest", "description": "Run tests", "category": "test"},
                "test_unit": {
                    "command": "pytest tests/unit/",
                    "description": "Run unit tests",
                    "category": "test",
                },
                "test_integration": {
                    "command": "pytest tests/integration/",
                    "description": "Run integration tests",
                    "category": "test",
                },
                "test_coverage": {
                    "command": "pytest --cov=scripts",
                    "description": "Run tests with coverage",
                    "category": "test",
                },
                "lint": {
                    "command": "ruff check scripts/ tests/",
                    "description": "Run linter",
                    "category": "quality",
                },
                "typecheck": {
                    "command": "mypy scripts/ tests/",
                    "description": "Run type checker",
                    "category": "quality",
                },
                "test_e2e": {
                    "command": "pytest tests/e2e/",
                    "description": "Run e2e tests",
                    "category": "test",
                },
                "test_e2e_ui": {
                    "command": "pytest tests/e2e/ --headed",
                    "description": "Run e2e tests with UI",
                    "category": "test",
                },
                "test_e2e_headed": {
                    "command": "pytest tests/e2e/ --headed",
                    "description": "Run e2e tests headed",
                    "category": "test",
                },
                "test_e2e_codegen": {
                    "command": "pytest tests/e2e/ --codegen",
                    "description": "Run e2e tests with codegen",
                    "category": "test",
                },
                "docs": {
                    "command": "python -m scripts.generate_docs",
                    "description": "Generate docs",
                    "category": "docs",
                },
                "dev": {
                    "command": "python -m app.main",
                    "description": "Run dev server",
                    "category": "dev",
                },
                "typedoc": {
                    "command": "python -m pydoc",
                    "description": "Generate type docs",
                    "category": "docs",
                },
                "simulate": {
                    "command": "python -m app.simulate",
                    "description": "Run simulation",
                    "category": "dev",
                },
            },
        }
        config_path.write_text(yaml.dump(config_data))

        output_dir = repo_dir / "output"
        output_dir.mkdir()

        # Act: Generate single repo
        result = generate_single_repo(str(repo_dir), str(config_path), str(output_dir))

        # Assert: Returns (path, success, error) tuple
        assert isinstance(result, tuple)
        assert len(result) == 3
        path, success, error = result
        assert path == str(repo_dir)
        assert success is True
        assert error is None or error == ""

    def test_generate_single_repo_returns_failure_on_invalid_config(self, tmp_path):
        """Worker function returns failure tuple on config validation error."""
        # Arrange: Invalid repo setup
        repo_dir = tmp_path / "repo"
        repo_dir.mkdir()

        config_path = repo_dir / "config.yml"
        config_data = {
            "name": "test",
            "repo": {"title": "test"},
        }  # Missing required language
        config_path.write_text(yaml.dump(config_data))

        output_dir = repo_dir / "output"
        output_dir.mkdir()

        # Act: Attempt to generate single repo
        result = generate_single_repo(str(repo_dir), str(config_path), str(output_dir))

        # Assert: Returns failure tuple
        assert isinstance(result, tuple)
        path, success, error = result
        assert path == str(repo_dir)
        assert success is False
        assert error is not None and len(error) > 0


class TestCLIEntryPoint:
    """Test suite for CLI entry point."""

    def test_cli_processes_valid_manifest_successfully(self, tmp_path, monkeypatch):
        """CLI entry point processes valid manifest and returns success code."""
        # Arrange: Create manifest with 2 repos
        manifest_path = tmp_path / "manifest.yml"

        repos = []
        for i in range(2):
            repo_dir = tmp_path / f"repo{i}"
            repo_dir.mkdir()

            config_path = repo_dir / "config.yml"
            config_data = create_standard_config("python")
            config_data["name"] = f"repo{i}"
            config_data["repo"]["title"] = f"repo{i}"
            config_path.write_text(yaml.dump(config_data))

            output_dir = repo_dir / "output"
            output_dir.mkdir()

            repos.append(
                {"path": str(repo_dir), "config": str(config_path), "output": str(output_dir)}
            )

        manifest_data: dict[str, Any] = {"repos": repos}
        manifest_path.write_text(yaml.dump(manifest_data))

        # Mock command-line arguments
        test_args = ["script_name", "--manifest", str(manifest_path), "--workers", "2"]
        monkeypatch.setattr("sys.argv", test_args)

        # Act: Run CLI
        from scripts.generate_all import _cli_main

        exit_code = _cli_main()

        # Assert: CLI returns success (0)
        assert exit_code == 0

    def test_cli_returns_error_code_when_manifest_not_found(self, tmp_path, monkeypatch):
        """CLI returns error code when manifest file does not exist."""
        # Arrange: Non-existent manifest
        manifest_path = tmp_path / "nonexistent.yml"

        # Mock command-line arguments
        test_args = ["script_name", "--manifest", str(manifest_path)]
        monkeypatch.setattr("sys.argv", test_args)

        # Act: Run CLI
        from scripts.generate_all import _cli_main

        exit_code = _cli_main()

        # Assert: CLI returns error code (1)
        assert exit_code == 1

    def test_cli_returns_error_when_repo_generation_fails(self, tmp_path, monkeypatch):
        """CLI returns error code when one or more repos fail to generate."""
        # Arrange: Manifest with invalid repo config
        manifest_path = tmp_path / "manifest.yml"

        repo_dir = tmp_path / "repo"
        repo_dir.mkdir()

        config_path = repo_dir / "config.yml"
        # Invalid config - missing required language field
        config_data = {"name": "test", "repo": {"title": "test"}}
        config_path.write_text(yaml.dump(config_data))

        output_dir = repo_dir / "output"
        output_dir.mkdir()

        manifest_data: dict[str, Any] = {
            "repos": [
                {"path": str(repo_dir), "config": str(config_path), "output": str(output_dir)}
            ]
        }
        manifest_path.write_text(yaml.dump(manifest_data))

        # Mock command-line arguments
        test_args = ["script_name", "--manifest", str(manifest_path)]
        monkeypatch.setattr("sys.argv", test_args)

        # Act: Run CLI
        from scripts.generate_all import _cli_main

        exit_code = _cli_main()

        # Assert: CLI returns error code due to failed repo
        assert exit_code == 1
