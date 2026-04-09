"""Tests for schema generation script.

Tests verify that generate_schema_capabilities.py correctly transforms the
capability registry into JSON Schema properties, preserves schema structure,
and handles error conditions appropriately.
"""

import json
import tempfile
from pathlib import Path

from scripts.generate_schema_capabilities import generate_properties, generate_schema


def test_generate_valid_properties_from_registry():
    """Generation script transforms registry into correct JSON Schema properties format."""
    # Test fixture with 2 capabilities
    test_registry: dict[str, dict[str, bool | str]] = {
        "hasUI": {"default": False, "description": "UI components"},
        "hasDB": {"default": True, "description": "Database"},
    }

    # Generate properties
    properties = generate_properties(test_registry)

    # Should have 2 keys matching registry
    assert len(properties) == 2
    assert "hasUI" in properties
    assert "hasDB" in properties

    # Each property should have correct structure
    assert properties["hasUI"]["type"] == "boolean"
    assert properties["hasUI"]["description"] == "UI components"
    assert properties["hasDB"]["type"] == "boolean"
    assert properties["hasDB"]["description"] == "Database"


def test_preserve_schema_structure_outside_capabilities():
    """Generation only modifies capabilities.properties, leaving other sections unchanged."""
    # Schema fixture with multiple sections
    test_schema = {
        "properties": {
            "name": {"type": "string"},
            "repo": {"type": "object"},
            "capabilities": {"properties": {"oldProp": {"type": "boolean"}}},
            "commands": {"type": "object"},
        }
    }

    test_registry: dict[str, dict[str, bool | str]] = {
        "hasUI": {"default": False, "description": "UI"},
        "hasDB": {"default": False, "description": "DB"},
    }

    # Generate schema
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(test_schema, f)
        schema_path = f.name

    try:
        # Run generation
        generate_schema(test_registry, schema_path)

        # Load result
        with Path(schema_path).open() as f:
            result = json.load(f)

        # Top-level properties unchanged (except capabilities)
        assert result["properties"]["name"] == {"type": "string"}
        assert result["properties"]["repo"] == {"type": "object"}
        assert result["properties"]["commands"] == {"type": "object"}

        # Only capabilities.properties modified
        assert "hasUI" in result["properties"]["capabilities"]["properties"]
        assert "hasDB" in result["properties"]["capabilities"]["properties"]
        assert "oldProp" not in result["properties"]["capabilities"]["properties"]

    finally:
        Path(schema_path).unlink()


def test_schema_file_not_found():
    """Script exits with error when schema file missing."""
    test_registry: dict[str, dict[str, bool | str]] = {
        "hasUI": {"default": False, "description": "UI"}
    }
    non_existent_path = "/path/does/not/exist/config.schema.json"

    # Should raise FileNotFoundError
    try:
        generate_schema(test_registry, non_existent_path)
        raise AssertionError("Expected FileNotFoundError")
    except FileNotFoundError as e:
        assert "schema/config.schema.json not found" in str(e).lower()


def test_malformed_registry_missing_description():
    """Script detects registry entries missing required description field."""
    # Registry with incomplete entry (no description)
    malformed_registry: dict[str, dict[str, bool | str]] = {"hasUI": {"default": False}}

    # Should raise KeyError when accessing description
    try:
        generate_properties(malformed_registry)
        raise AssertionError("Expected KeyError for missing description")
    except KeyError as e:
        assert "description" in str(e)


def test_malformed_schema_json():
    """Script handles corrupted schema file gracefully."""
    test_registry: dict[str, dict[str, bool | str]] = {
        "hasUI": {"default": False, "description": "UI"}
    }

    # Create malformed JSON file
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        f.write('{"properties": {"capabilities":}')  # Invalid JSON
        schema_path = f.name

    try:
        # Should raise JSONDecodeError
        try:
            generate_schema(test_registry, schema_path)
            raise AssertionError("Expected JSONDecodeError")
        except json.JSONDecodeError as e:
            assert "invalid json" in str(e).lower() or "expecting" in str(e).lower()
    finally:
        Path(schema_path).unlink()


def test_registry_with_non_boolean_default():
    """Generated schema has type boolean even when registry default is wrong type."""
    # Registry with wrong type default
    malformed_registry: dict[str, dict[str, bool | str]] = {
        "hasUI": {"default": "yes", "description": "UI"}
    }

    # Generate properties (script doesn't validate defaults)
    properties = generate_properties(malformed_registry)

    # Should still generate type: boolean
    assert properties["hasUI"]["type"] == "boolean"
    assert properties["hasUI"]["description"] == "UI"

    # Note: Config using this default will fail schema validation later
