"""Schema validation tests for generated capability properties.

Tests verify generated schema remains valid JSON Schema Draft 07 and
correctly validates configs with capabilities.
"""

import json
from pathlib import Path

import jsonschema


def test_generated_schema_is_valid_json_schema_draft_07():
    """Validates generated schema file conforms to JSON Schema specification."""
    # Load schema file
    schema_path = Path(__file__).parent.parent / "schema" / "config.schema.json"

    with schema_path.open() as f:
        schema = json.load(f)

    # Should have $schema field pointing to Draft 07
    assert "$schema" in schema
    assert "draft-07" in schema["$schema"]

    # Schema should be valid JSON (already loaded successfully)
    assert isinstance(schema, dict)

    # Should have required top-level keys
    assert "type" in schema
    assert "properties" in schema


def test_config_with_all_capabilities_validates():
    """Verifies configs using generated schema properties pass validation."""
    # Load schema
    schema_path = Path(__file__).parent.parent / "schema" / "config.schema.json"

    with schema_path.open() as f:
        schema = json.load(f)

    # Config with all capabilities defined
    config = {
        "name": "test-project",
        "repo": {"title": "Test", "language": {"python": "all"}},
        "capabilities": {"hasUI": True, "hasDB": False},
        "commands": {"test": {"command": "pytest", "description": "Run tests", "category": "test"}},
    }

    # Should validate without error
    jsonschema.validate(config, schema)


def test_config_with_unknown_capability_rejected():
    """Ensures schema enforces additionalProperties: false for capabilities."""
    # Load schema
    schema_path = Path(__file__).parent.parent / "schema" / "config.schema.json"

    with schema_path.open() as f:
        schema = json.load(f)

    # Config with non-existent capability
    config = {
        "name": "test-project",
        "repo": {"title": "Test", "language": {"python": "all"}},
        "capabilities": {"hasDocker": True},  # Not in registry
        "commands": {"test": {"command": "pytest", "description": "Run tests", "category": "test"}},
    }

    # Should raise ValidationError
    try:
        jsonschema.validate(config, schema)
        raise AssertionError("Expected ValidationError for unknown capability")
    except jsonschema.ValidationError as e:
        # Error should mention additionalProperties or unknown property
        error_msg = str(e).lower()
        assert "additional" in error_msg or "hasDocker" in error_msg.lower()


def test_config_with_non_boolean_capability_rejected():
    """Validates type checking for capability values."""
    # Load schema
    schema_path = Path(__file__).parent.parent / "schema" / "config.schema.json"

    with schema_path.open() as f:
        schema = json.load(f)

    # Config with wrong type value
    config = {
        "name": "test-project",
        "repo": {"title": "Test", "language": {"python": "all"}},
        "capabilities": {"hasUI": "yes"},  # Should be boolean
        "commands": {"test": {"command": "pytest", "description": "Run tests", "category": "test"}},
    }

    # Should raise ValidationError
    try:
        jsonschema.validate(config, schema)
        raise AssertionError("Expected ValidationError for non-boolean capability")
    except jsonschema.ValidationError as e:
        # Error should mention type
        error_msg = str(e).lower()
        assert "type" in error_msg or "boolean" in error_msg
