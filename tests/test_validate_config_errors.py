"""Enhanced error message tests for validation failures."""

from pathlib import Path

import pytest
import yaml

from scripts.validate_config import validate_config_with_enhanced_errors
from tests.helpers.config_factory import create_invalid_scope_config, create_valid_config


# Test 2.1: Enhanced error message for pattern violation
def test_enhanced_error_pattern_violation(tmp_path: Path):
    """Verify enhanced validation provides clear messages for pattern violations."""
    # Create config with scope value violating pattern (uppercase and numbers)
    config = create_invalid_scope_config("Backend123")

    # Write to temporary config file
    config_path = tmp_path / "midtempo-framework.yml"
    with config_path.open("w") as f:
        yaml.dump(config, f)

    # Should raise ValueError with enhanced error message
    with pytest.raises(ValueError) as exc_info:
        validate_config_with_enhanced_errors(config_path)

    error_message = str(exc_info.value)

    # Error message should be user-friendly and include:
    # - Field path indication
    # - Pattern requirement explanation
    # - Clear guidance
    assert "repo.language" in error_message or "language" in error_message.lower()
    # Should mention pattern or provide guidance about valid scope names
    assert (
        "pattern" in error_message.lower()
        or "lowercase" in error_message.lower()
        or "^[a-z]" in error_message
        or "valid" in error_message.lower()
    )


# Test 2.2: Enhanced error message for missing required field
def test_enhanced_error_missing_required_field(tmp_path: Path):
    """Verify enhanced error handling provides clear messages for missing required fields."""
    # Create config without language field
    config = create_valid_config()
    del config["repo"]["language"]

    # Write to temporary config file
    config_path = tmp_path / "midtempo-framework.yml"
    with config_path.open("w") as f:
        yaml.dump(config, f)

    # Should raise ValueError with enhanced error message
    with pytest.raises(ValueError) as exc_info:
        validate_config_with_enhanced_errors(config_path)

    error_message = str(exc_info.value)

    # Error message should include:
    # - Full field path
    # - Indication that field is required
    assert "repo.language" in error_message or (
        "repo" in error_message and "language" in error_message
    )
    assert "required" in error_message.lower() or "missing" in error_message.lower()
