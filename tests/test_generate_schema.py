"""Tests for schema generation script (capabilities and instructions).

Tests verify generate_schema.py correctly transforms both capability and
instruction registries into JSON Schema sections, preserves schema structure,
and handles error conditions appropriately.
"""

import json
import tempfile
from pathlib import Path

from scripts.generate_schema import (
    generate_instruction_properties,
    generate_schema,
)


def test_generates_instruction_pattern_properties_from_registry():
    """Generation script produces patternProperties structure for instructions section."""
    # Test fixture with 2 instruction examples
    test_registry: dict[str, dict[str, str]] = {
        "db": {"page": "db.md", "description": "Database patterns"},
        "api": {"page": "api.md", "description": "API conventions"},
    }

    # Generate instruction properties
    properties = generate_instruction_properties(test_registry)

    # Should have instructions patternProperties structure
    assert "type" in properties
    assert properties["type"] == "object"

    assert "additionalProperties" in properties
    assert properties["additionalProperties"] is False

    # patternProperties with kebab-case pattern
    assert "patternProperties" in properties
    pattern_props = properties["patternProperties"]
    assert "^[a-z][a-z0-9_-]*$" in pattern_props

    # Nested structure requires page and description
    nested_schema = pattern_props["^[a-z][a-z0-9_-]*$"]
    assert nested_schema["type"] == "object"
    assert nested_schema["required"] == ["page", "description"]

    # Page field structure
    assert "page" in nested_schema["properties"]
    page_prop = nested_schema["properties"]["page"]
    assert page_prop["type"] == "string"
    assert page_prop["minLength"] == 1

    # Description field structure
    assert "description" in nested_schema["properties"]
    desc_prop = nested_schema["properties"]["description"]
    assert desc_prop["type"] == "string"
    assert desc_prop["minLength"] == 1

    # Nested additionalProperties false
    assert nested_schema["additionalProperties"] is False


def test_preserve_schema_structure_outside_instructions_section():
    """Generation only modifies instructions section, preserves all other properties."""
    # Schema fixture with multiple sections
    test_schema = {
        "properties": {
            "name": {"type": "string"},
            "repo": {"type": "object"},
            "capabilities": {"properties": {"hasUI": {"type": "boolean"}}},
            "commands": {"type": "object"},
        }
    }

    test_caps_registry: dict[str, dict[str, bool | str]] = {
        "hasUI": {"default": False, "description": "UI"},
    }

    test_instr_registry: dict[str, dict[str, str]] = {
        "db": {"page": "db.md", "description": "Database"},
    }

    # Generate schema
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(test_schema, f)
        schema_path = f.name

    try:
        # Run generation
        generate_schema(test_caps_registry, schema_path, test_instr_registry)

        # Load result
        with Path(schema_path).open() as f:
            result = json.load(f)

        # All non-instruction sections unchanged
        assert result["properties"]["name"] == {"type": "string"}
        assert result["properties"]["repo"] == {"type": "object"}
        assert result["properties"]["commands"] == {"type": "object"}

        # Capabilities section updated
        assert "hasUI" in result["properties"]["capabilities"]["properties"]

        # Instructions section added
        assert "instructions" in result["properties"]
        assert "patternProperties" in result["properties"]["instructions"]

    finally:
        Path(schema_path).unlink()


def test_handles_missing_schema_file():
    """Script raises FileNotFoundError when schema file not found."""
    test_registry: dict[str, dict[str, bool | str]] = {
        "hasUI": {"default": False, "description": "UI"}
    }
    non_existent_path = "/tmp/nonexistent-schema-12345/config.schema.json"

    # Should raise FileNotFoundError
    try:
        generate_schema(test_registry, non_existent_path)
        raise AssertionError("Expected FileNotFoundError")
    except FileNotFoundError as e:
        assert "schema/config.schema.json not found" in str(e).lower()


def test_handles_malformed_schema_json():
    """Script raises JSONDecodeError when schema file has invalid JSON syntax."""
    test_registry: dict[str, dict[str, bool | str]] = {
        "hasUI": {"default": False, "description": "UI"}
    }

    # Create malformed JSON file
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        f.write('{ "name": "test",')  # Unclosed object
        schema_path = f.name

    try:
        # Should raise JSONDecodeError
        try:
            generate_schema(test_registry, schema_path)
            raise AssertionError("Expected JSONDecodeError")
        except json.JSONDecodeError as e:
            # JSONDecodeError raised for malformed JSON
            assert "expecting" in str(e).lower() or "invalid" in str(e).lower()
    finally:
        Path(schema_path).unlink()


def test_handles_malformed_registry_missing_page_field():
    """Script raises KeyError when instruction registry entry lacks required page field."""
    # Registry with incomplete entry (no page)
    malformed_registry: dict[str, dict[str, str]] = {"db": {"description": "Database patterns"}}

    # Valid schema file
    test_schema: dict[str, dict] = {
        "properties": {
            "capabilities": {"properties": {}},
        }
    }

    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(test_schema, f)
        schema_path = f.name

    try:
        # Should raise KeyError during generation
        test_caps_registry: dict[str, dict[str, bool | str]] = {}

        try:
            generate_schema(test_caps_registry, schema_path, malformed_registry)
            raise AssertionError("Expected KeyError for missing page field")
        except KeyError as e:
            assert "page" in str(e).lower()
    finally:
        Path(schema_path).unlink()


def test_handles_malformed_registry_missing_description_field():
    """Script raises KeyError when instruction registry entry lacks required description field."""
    # Registry with incomplete entry (no description)
    malformed_registry: dict[str, dict[str, str]] = {"db": {"page": "db.md"}}

    # Valid schema file
    test_schema: dict[str, dict] = {
        "properties": {
            "capabilities": {"properties": {}},
        }
    }

    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(test_schema, f)
        schema_path = f.name

    try:
        # Should raise KeyError during generation
        test_caps_registry: dict[str, dict[str, bool | str]] = {}

        try:
            generate_schema(test_caps_registry, schema_path, malformed_registry)
            raise AssertionError("Expected KeyError for missing description field")
        except KeyError as e:
            assert "description" in str(e).lower()
    finally:
        Path(schema_path).unlink()
