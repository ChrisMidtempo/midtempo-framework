"""Config schema validator for midtempo-framework.yml files."""

import json
from pathlib import Path
from typing import Any, cast

import yaml
from jsonschema import ValidationError, validate

from scripts.paths import CONFIG_SCHEMA_PATH


def validate_config_with_enhanced_errors(config_path: Path | dict[str, Any]) -> dict[str, Any]:
    """
    Validate config with enhanced error messages for enums and missing fields.

    Args:
        config_path: Path to midtempo-framework.yml config file or config dict

    Returns:
        Validated config dictionary

    Raises:
        ValueError: With enhanced error messages for validation failures
    """
    # Load YAML config
    if isinstance(config_path, dict):
        config_data = config_path
    else:
        with config_path.open() as f:
            config_data = yaml.safe_load(f)

    # Load JSON Schema
    with CONFIG_SCHEMA_PATH.open() as f:
        schema = json.load(f)

    # Validate config against schema with enhanced error messages
    try:
        validate(instance=config_data, schema=schema)
    except ValidationError as e:
        # Build enhanced error message
        error_parts = []

        # Check for missing required field
        if str(e.validator) == "required":
            missing_field = e.message.split("'")[1] if "'" in e.message else "unknown"
            # Build field path
            field_path = ".".join(str(p) for p in e.absolute_path) if e.absolute_path else "root"
            if field_path != "root":
                full_field_path = f"{field_path}.{missing_field}"
            else:
                full_field_path = missing_field
            error_parts.append(f"Missing required field: {full_field_path}")

        # Check for enum validation error
        elif str(e.validator) == "enum":
            invalid_value = e.instance
            # Get enum values from schema (with type safety)
            enum_values = e.schema.get("enum", []) if isinstance(e.schema, dict) else []
            field_path = ".".join(str(p) for p in e.absolute_path) if e.absolute_path else "value"
            error_parts.append(
                f"Invalid value for {field_path}: {invalid_value}\n"
                f"Valid options: {', '.join(str(opt) for opt in enum_values)}"
            )

        # Check for pattern validation error
        elif str(e.validator) == "pattern":
            invalid_value = e.instance
            pattern = e.schema.get("pattern", "") if isinstance(e.schema, dict) else ""
            field_path = ".".join(str(p) for p in e.absolute_path) if e.absolute_path else "value"
            error_parts.append(
                f"Invalid value for {field_path}: {invalid_value}\n"
                f"Scope names must match pattern: {pattern}\n"
                f"Requirements: lowercase start, alphanumeric + hyphens/underscores, 2-20 chars\n"
                f"Examples: all, backend, frontend, admin-api, user_service"
            )

        # Check for additional properties error
        elif str(e.validator) == "additionalProperties":
            error_parts.append(f"Unexpected field: {e.message}")

        else:
            # Generic validation error
            error_parts.append(f"Validation error: {e.message}")

        raise ValueError("\n".join(error_parts)) from e

    return config_data


def validate_config(config_path: Path) -> dict[str, Any]:
    """
    Validate config YAML against JSON Schema.

    Args:
        config_path: Path to midtempo-framework.yml config file

    Returns:
        Validated config dictionary

    Raises:
        yaml.YAMLError: If YAML syntax is invalid
        ValidationError: If config doesn't match schema
    """
    # Load YAML config (raises yaml.YAMLError if malformed)
    with config_path.open() as f:
        config_data = yaml.safe_load(f)

    # Load JSON Schema
    with CONFIG_SCHEMA_PATH.open() as f:
        schema = json.load(f)

    # Validate config against schema (raises ValidationError if invalid)
    validate(instance=config_data, schema=schema)

    # After validation, we know config_data matches our schema
    return cast(dict[str, Any], config_data)
