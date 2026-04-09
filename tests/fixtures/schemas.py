"""Test fixture utilities for schema loading and validation."""

import json
from pathlib import Path
from typing import Any

from jsonschema import validate

# Path to schema file (relative to project root)
SCHEMA_PATH = Path(__file__).parent.parent.parent / "schema" / "config.schema.json"


def load_test_schema() -> dict[str, Any]:
    """
    Load JSON schema from config.schema.json file.

    Returns:
        Schema dictionary

    Raises:
        FileNotFoundError: If schema file doesn't exist
    """
    if not SCHEMA_PATH.exists():
        raise FileNotFoundError(f"Schema file not found: {SCHEMA_PATH}")

    with SCHEMA_PATH.open() as f:
        schema: dict[str, Any] = json.load(f)
        return schema


def validate_test_config(config_dict: dict[str, Any]) -> dict[str, Any]:
    """
    Validate config dictionary against JSON schema.

    Wrapper around jsonschema.validate() for test consistency.

    Args:
        config_dict: Configuration dictionary to validate

    Returns:
        Same config dictionary if validation succeeds

    Raises:
        ValidationError: If config doesn't match schema
    """
    schema = load_test_schema()
    validate(instance=config_dict, schema=schema)
    return config_dict
