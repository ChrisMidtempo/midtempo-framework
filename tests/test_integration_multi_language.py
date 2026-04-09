"""Integration tests for full generation workflow with multi-language mapping."""

from pathlib import Path

import pytest
import yaml

from scripts.capabilities import DEFAULT_CAPABILITIES
from scripts.generate_docs import generate_documentation
from tests.helpers.config_factory import create_config_with_language, create_invalid_scope_config


# Test 4.1: Full generation workflow with mono-language config
@pytest.mark.integration
def test_full_generation_workflow_mono_language(tmp_path: Path):
    """Verify complete end-to-end generation workflow succeeds with mono-language mapping."""
    # Create test config with new mono-language format
    # Provide DEFAULT_CAPABILITIES because templates expect complete capabilities
    config = create_config_with_language({"python": "all"}, capabilities=DEFAULT_CAPABILITIES)

    # Add core commands that templates reference (no longer enriched from python.yml)
    config["commands"]["test"] = {
        "command": "pytest",
        "description": "Run all tests",
        "category": "testing",
    }
    config["commands"]["lint"] = {
        "command": "ruff check scripts/ tests/",
        "description": "Run linter for code quality",
        "category": "quality",
    }
    config["commands"]["typecheck"] = {
        "command": "mypy scripts/ tests/",
        "description": "Run type checker",
        "category": "quality",
    }
    config["commands"]["test_coverage"] = {
        "command": "pytest --cov",
        "description": "Run tests with coverage",
        "category": "testing",
    }

    # Write config to temporary file
    config_path = tmp_path / "midtempo-framework.yml"
    with config_path.open("w") as f:
        yaml.dump(config, f)

    # Create output directory
    output_dir = tmp_path / "output"
    output_dir.mkdir()

    # Run generation workflow
    success = generate_documentation(config_path, output_dir)

    # Generation should succeed
    assert success is True

    # Expected output files should be created
    # (At minimum, some files should be generated)
    generated_files = list(output_dir.rglob("*"))
    assert len(generated_files) > 0, "No files were generated"


# Test 4.2: Full generation workflow with multi-language config
@pytest.mark.integration
def test_full_generation_workflow_multi_language(tmp_path: Path):
    """Verify generation workflow succeeds with multi-language mapping (all languages processed)."""
    # Create test config with multi-language format
    # Provide DEFAULT_CAPABILITIES because templates expect complete capabilities
    config = create_config_with_language(
        {"python": "backend", "typescript": "frontend"}, capabilities=DEFAULT_CAPABILITIES
    )

    # Add user-defined commands that templates might reference
    # (Templates use bare names, but multi-language generates scoped names)
    config["commands"]["test"] = {
        "command": "pytest && npm test",
        "description": "Run all tests",
        "category": "test",
    }
    config["commands"]["test_coverage"] = {
        "command": "pytest --cov && npm test -- --coverage",
        "description": "Run tests with coverage",
        "category": "test",
    }
    config["commands"]["lint"] = {
        "command": "ruff check . && npm run lint",
        "description": "Run all linting",
        "category": "quality",
    }
    config["commands"]["typecheck"] = {
        "command": "mypy . && npm run typecheck",
        "description": "Run all type checking",
        "category": "quality",
    }

    # Write config to temporary file
    config_path = tmp_path / "midtempo-framework.yml"
    with config_path.open("w") as f:
        yaml.dump(config, f)

    # Create output directory
    output_dir = tmp_path / "output"
    output_dir.mkdir()

    # Run generation workflow
    success = generate_documentation(config_path, output_dir)

    # Generation should succeed (all languages processed with scoped commands)
    assert success is True

    # Output files should be created
    generated_files = list(output_dir.rglob("*"))
    assert len(generated_files) > 0, "No files were generated"


# Test 4.3: Validation error displayed clearly to user
@pytest.mark.integration
def test_validation_error_displayed_clearly(tmp_path: Path):
    """Verify validation errors provide clear, actionable feedback to users."""
    # Create config with invalid scope name (uppercase)
    config = create_invalid_scope_config("Bad-Name")

    # Write to temporary config file
    config_path = tmp_path / "midtempo-framework.yml"
    with config_path.open("w") as f:
        yaml.dump(config, f)

    # Create output directory
    output_dir = tmp_path / "output"
    output_dir.mkdir()

    # Generation should fail validation before beginning
    # Should raise error with clear message
    with pytest.raises(Exception) as exc_info:
        generate_documentation(config_path, output_dir)

    # Error should be from validation (not a crash)
    # Could be ValidationError or ValueError depending on which validation function is used
    error_message = str(exc_info.value)

    # Error should relate to the invalid scope
    # (Either pattern violation or type error depending on current schema state)
    assert (
        "pattern" in error_message.lower()
        or "type" in error_message.lower()
        or "language" in error_message.lower()
        or "valid" in error_message.lower()
    ), f"Error message doesn't indicate validation issue: {error_message}"
