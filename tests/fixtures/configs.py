"""Test fixture factories for config dictionaries."""

from typing import Any


def _create_minimal_config_base(capabilities: dict[str, bool] | None = None) -> dict[str, Any]:
    """
    Create minimal config with required top-level fields.

    Args:
        capabilities: Optional capabilities dict. Tests specify only capabilities
            they explicitly test. Defaults to empty dict for maximum decoupling
            from schema structure.

    Returns:
        Minimal config dict with specified capabilities (or empty dict)
    """
    return {
        "name": "test-project",
        "repo": {
            "title": "Test Project",
            "language": {"python": "python"},
        },
        "capabilities": capabilities if capabilities is not None else {},
        "commands": {},
    }


def create_valid_command(
    name: str,
    command: str,
    description: str,
    category: str,
    capabilities: dict[str, bool] | None = None,
) -> dict[str, Any]:
    """
    Create a valid command in object format.

    Args:
        name: Command name key
        command: Command string to execute
        description: Human-readable description
        category: Command category for grouping
        capabilities: Optional capabilities dict for test

    Returns:
        Dictionary with single command in object format
    """
    config = _create_minimal_config_base(capabilities=capabilities)
    config["commands"] = {
        name: {
            "command": command,
            "description": description,
            "category": category,
        }
    }
    return config


def create_string_format_command(
    name: str, command: str, capabilities: dict[str, bool] | None = None
) -> dict[str, Any]:
    """
    Create a command in deprecated string format.

    Args:
        name: Command name key
        command: Command string value
        capabilities: Optional capabilities dict for test

    Returns:
        Dictionary with single command in string format
    """
    config = _create_minimal_config_base(capabilities=capabilities)
    config["commands"] = {name: command}
    return config


def create_incomplete_command(
    name: str, capabilities: dict[str, bool] | None = None, **fields: str
) -> dict[str, Any]:
    """
    Create a command object with only specified fields (missing required fields).

    Args:
        name: Command name key
        capabilities: Optional capabilities dict for test
        **fields: Field names and values to include in command object

    Returns:
        Dictionary with incomplete command object
    """
    config = _create_minimal_config_base(capabilities=capabilities)
    config["commands"] = {name: dict(fields)}
    return config


def create_full_test_config(capabilities: dict[str, bool] | None = None) -> dict[str, Any]:
    """
    Create a complete config with multiple commands across categories.

    Args:
        capabilities: Optional capabilities dict for test

    Returns:
        Dictionary with test, quality, and utilities category commands
    """
    config = _create_minimal_config_base(capabilities=capabilities)
    config["commands"] = {
        "test": {
            "command": "npm run test:python",
            "description": "Run unit tests",
            "category": "test",
        },
        "test_coverage": {
            "command": "npm run test:python:coverage",
            "description": "Run tests with coverage",
            "category": "test",
        },
        "lint": {
            "command": "npm run lint:python",
            "description": "Run linter",
            "category": "quality",
        },
        "typecheck": {
            "command": "npm run typecheck:python",
            "description": "Run type checker",
            "category": "quality",
        },
        "generate": {
            "command": "npm run generate",
            "description": "Generate docs",
            "category": "utilities",
        },
    }
    return config
