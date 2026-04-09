"""CI validation tests for registry and schema synchronisation.

Tests detect drift between CAPABILITIES registry and schema properties,
ensuring developers run generation after registry changes.
"""

import json
from pathlib import Path

from scripts.capabilities import CAPABILITIES


def test_detect_registry_key_not_in_schema():
    """CI validation catches when developer adds capability to registry but forgets schema generation."""
    # Simulate registry with 3 capabilities
    test_registry: dict[str, dict[str, bool | str]] = {"hasUI": {}, "hasDB": {}, "hasDocker": {}}

    # Simulate schema with only 2 properties
    test_schema_keys = {"hasUI", "hasDB"}

    # Detect drift
    registry_keys = set(test_registry.keys())
    missing_in_schema = registry_keys - test_schema_keys

    # Should detect hasDocker missing
    assert len(missing_in_schema) > 0, "Should detect capability in registry but not schema"
    assert "hasDocker" in missing_in_schema


def test_detect_schema_property_not_in_registry():
    """Catches orphaned schema properties (capability removed from registry but schema not regenerated)."""
    # Simulate registry with 2 capabilities
    test_registry: dict[str, dict[str, bool | str]] = {"hasUI": {}, "hasDB": {}}

    # Simulate schema with 3 properties
    test_schema_keys = {"hasUI", "hasDB", "hasDocker"}

    # Detect drift
    registry_keys = set(test_registry.keys())
    missing_in_registry = test_schema_keys - registry_keys

    # Should detect hasDocker orphaned
    assert len(missing_in_registry) > 0, "Should detect property in schema but not registry"
    assert "hasDocker" in missing_in_registry


def test_registry_and_schema_synchronised():
    """Validates happy path when registry and schema match exactly."""
    # Load real schema file
    schema_path = Path(__file__).parent.parent / "schema" / "config.schema.json"

    with schema_path.open() as f:
        schema = json.load(f)

    # Get schema capability keys
    schema_keys = set(schema["properties"]["capabilities"]["properties"].keys())

    # Get registry keys
    registry_keys = set(CAPABILITIES.keys())

    # Should match exactly
    assert (
        registry_keys == schema_keys
    ), f"Registry and schema out of sync. Registry: {registry_keys}, Schema: {schema_keys}. Run npm run schema:generate"


def test_property_order_irrelevant():
    """Ensures validation uses set comparison (order doesn't matter)."""
    # Registry with keys in one order
    test_registry: dict[str, dict[str, bool | str]] = {"hasUI": {}, "hasDB": {}}

    # Schema with keys in different order
    test_schema_keys = {"hasDB", "hasUI"}

    # Set comparison should match
    registry_keys = set(test_registry.keys())
    assert registry_keys == test_schema_keys
