"""Tests for schema validation with optional capabilities.

Tests verify that config.schema.json accepts configs with empty, partial,
or complete capabilities objects, and rejects invalid capability types or
unknown properties.
"""

import json
from pathlib import Path

import pytest
from jsonschema import ValidationError, validate

# Load schema once for all tests
SCHEMA_PATH = Path(__file__).parent.parent / "schema" / "config.schema.json"
with SCHEMA_PATH.open() as f:
    SCHEMA = json.load(f)


def test_validate_config_with_empty_capabilities():
    """Schema validator accepts config containing empty capabilities object."""
    config = {
        "name": "test-project",
        "repo": {"title": "Test Project", "language": {"python": "py"}},
        "capabilities": {},
        "commands": {},
    }

    # Should not raise ValidationError
    validate(instance=config, schema=SCHEMA)


def test_validate_config_with_partial_capabilities():
    """Schema validator accepts config with subset of capability properties."""
    config = {
        "name": "test-project",
        "repo": {"title": "Test Project", "language": {"python": "py"}},
        "capabilities": {"hasUI": True},
        "commands": {},
    }

    # Should not raise ValidationError
    validate(instance=config, schema=SCHEMA)


def test_validate_config_with_complete_capabilities():
    """Schema validator accepts config with all capability properties present."""
    config = {
        "name": "test-project",
        "repo": {"title": "Test Project", "language": {"python": "py"}},
        "capabilities": {"hasUI": False, "hasDB": False},
        "commands": {},
    }

    # Should not raise ValidationError (backward compatibility)
    validate(instance=config, schema=SCHEMA)


def test_reject_invalid_capability_type():
    """Schema validator rejects config where capability has non-boolean type."""
    config = {
        "name": "test-project",
        "repo": {"title": "Test Project", "language": {"python": "py"}},
        "capabilities": {"hasUI": "yes"},  # String instead of boolean
        "commands": {},
    }

    # Should raise ValidationError for type mismatch
    with pytest.raises(ValidationError) as exc_info:
        validate(instance=config, schema=SCHEMA)

    # Verify error message indicates type problem
    error = exc_info.value
    assert "type" in error.message.lower() or "boolean" in error.message.lower()


def test_reject_unknown_capability_property():
    """Schema validator rejects config with unknown capability property."""
    config = {
        "name": "test-project",
        "repo": {"title": "Test Project", "language": {"python": "py"}},
        "capabilities": {"hasUI": False, "unknownCapability": True},
        "commands": {},
    }

    # Should raise ValidationError for additional property
    with pytest.raises(ValidationError) as exc_info:
        validate(instance=config, schema=SCHEMA)

    # Verify error identifies the unknown property
    error = exc_info.value
    assert "additional" in error.message.lower() or "unknownCapability" in str(error)
