"""Factory functions for creating test config dictionaries."""

from pathlib import Path
from typing import Any

import yaml
from jinja2 import Environment, FileSystemLoader

from scripts.capabilities import DEFAULT_CAPABILITIES


def create_valid_config(
    capabilities: dict[str, bool] | None = None,
    security: dict | None = None,
) -> dict[str, Any]:
    """
    Create minimal valid config dict with all required fields.

    Args:
        capabilities: Optional capabilities dict. Tests specify only capabilities
            they explicitly test. Defaults to empty dict for maximum decoupling
            from schema structure.
        security: Optional security section dict. When provided, included in
            returned config. When omitted, no security key appears.

    Returns:
        Minimal valid config dictionary
    """
    caps = capabilities if capabilities is not None else {}
    config = {
        "name": "test-project",
        "repo": {
            "title": "Test Project",
            "language": {"python": "all"},
        },
        "capabilities": caps,
        "commands": {
            "test": {
                "command": "pytest",
                "description": "Run tests",
                "category": "test",
            },
            "lint": {
                "command": "ruff check .",
                "description": "Run linter",
                "category": "quality",
            },
            "typecheck": {
                "command": "mypy .",
                "description": "Run type checker",
                "category": "quality",
            },
            "test_coverage": {
                "command": "pytest --cov",
                "description": "Run tests with coverage",
                "category": "test",
            },
        },
        "instructions": _build_instructions_for_capabilities(caps),
    }
    if security is not None:
        config["security"] = security
    return config


def create_config_with_language(
    mapping: dict[str, str], capabilities: dict[str, bool] | None = None
) -> dict[str, Any]:
    """
    Create config with specified language mapping and NO pre-defined commands.

    Args:
        mapping: Language to scope mapping dict (e.g., {"python": "backend"})
        capabilities: Optional capabilities dict. Tests specify only capabilities
            they explicitly test. Defaults to empty dict for maximum decoupling
            from schema structure.

    Returns:
        Config dict with specified language mapping and empty commands dict
    """
    caps = capabilities if capabilities is not None else {}
    return {
        "name": "test-project",
        "repo": {
            "title": "Test Project",
            "language": mapping,
        },
        "capabilities": caps,
        "commands": {},
        "instructions": _build_instructions_for_capabilities(caps),
    }


def create_invalid_scope_config(scope_value: str) -> dict[str, Any]:
    """
    Create config with invalid scope value for testing validation failures.

    Args:
        scope_value: Invalid scope value to test (e.g., "Backend", "back@end")

    Returns:
        Config dict with invalid scope value
    """
    config = create_valid_config()
    config["repo"]["language"] = {"python": scope_value}
    return config


def create_config_with_language_and_commands(
    language_mapping: dict[str, str],
    commands_dict: dict[str, Any],
    capabilities: dict[str, bool] | None = None,
) -> dict[str, Any]:
    """
    Create config with specified language mapping and user-defined commands.

    Args:
        language_mapping: Language to scope mapping dict (e.g., {"python": "backend"})
        commands_dict: User-defined commands dict (e.g., {"backend_test": {...}})
        capabilities: Optional capabilities dict. Tests specify only capabilities
            they explicitly test. Defaults to empty dict for maximum decoupling
            from schema structure.

    Returns:
        Config dict with specified language mapping and commands
    """
    caps = capabilities if capabilities is not None else {}
    return {
        "name": "test-project",
        "repo": {
            "title": "Test Project",
            "language": language_mapping,
        },
        "capabilities": caps,
        "commands": commands_dict,
        "instructions": _build_instructions_for_capabilities(caps),
    }


def create_standard_config(language: str, capabilities: set[str] | None = None) -> dict[str, Any]:
    """
    Create standard config with commands loaded from language template files.

    Args:
        language: Language name (e.g., "python", "typescript")
        capabilities: Set of capability names to enable (e.g., {"hasDB"})

    Returns:
        Complete config dict with commands populated from rendered template

    Raises:
        ValueError: If language parameter is empty
        FileNotFoundError: If template file for language doesn't exist
        yaml.YAMLError: If rendered YAML has parsing errors
    """
    # Validate input
    if not language:
        raise ValueError("language parameter cannot be empty")

    # Default capabilities to empty set
    if capabilities is None:
        capabilities = set()

    # Build path to template file
    commands_dir = Path(__file__).parent.parent.parent / "commands"
    template_path = commands_dir / f"{language}.yml.j2"

    # Check if template exists and provide helpful error message
    if not template_path.exists():
        available_languages = sorted(
            [f.stem.replace(".yml", "") for f in commands_dir.glob("*.yml.j2") if f.is_file()]
        )
        raise FileNotFoundError(
            f"commands/{language}.yml.j2 not found. "
            f"Available languages: {', '.join(available_languages)}"
        )

    # Transform capabilities set to dict by merging over defaults
    enabled_capabilities = dict.fromkeys(capabilities, True)
    capabilities_dict = {**DEFAULT_CAPABILITIES, **enabled_capabilities}

    # Build instructions based on capabilities (required by templates)
    instructions = _build_instructions_for_capabilities(capabilities_dict)

    # Build base config
    base_config = {
        "name": "test-project",
        "repo": {
            "title": "Test Project",
            "language": {language: "all"},
        },
        "capabilities": capabilities_dict,
    }

    # Render template with base config
    env = Environment(loader=FileSystemLoader(commands_dir))
    template = env.get_template(f"{language}.yml.j2")
    base_config_yaml = yaml.dump(base_config, sort_keys=False)
    rendered = template.render(base_config=base_config_yaml)

    # Parse rendered YAML
    try:
        yaml_data: dict[str, Any] = yaml.safe_load(rendered)
    except yaml.YAMLError as e:
        raise yaml.YAMLError(f"Error parsing rendered template {template_path}: {e}") from e

    # Add instructions to the config
    yaml_data["instructions"] = instructions

    # Return the complete config (which includes commands from template)
    return yaml_data


def _build_instructions_for_capabilities(capabilities: dict[str, bool]) -> dict[str, Any]:
    """
    Build instructions dict based on enabled capabilities.

    Templates require certain instructions to be defined in the config.
    Core instructions are always included, capability-specific instructions
    are added when the corresponding capability is enabled.

    Args:
        capabilities: Dict of capability names to boolean values

    Returns:
        Instructions dict matching the format expected by the instructions filter
    """
    # Core instructions - always required by templates
    instructions: dict[str, Any] = {
        "purpose": {
            "page": "purpose.md",
            "description": "Provides an overview of the goal and capabilities of the service",
        },
        "architecture": {
            "page": "architecture.md",
            "description": "Services architectural structure and design principles",
        },
        "error-handling": {
            "page": "error-handling.md",
            "description": "Error handling patterns and conventions for the repository",
        },
    }

    # Database instructions - required when hasDB capability is enabled
    if capabilities.get("hasDB"):
        instructions["db"] = {
            "page": "db.md",
            "description": "Database access patterns, connection rules, and credential handling",
        }

    # UI instructions - required when hasUI capability is enabled
    if capabilities.get("hasUI"):
        instructions["frontend-design"] = {
            "page": "frontend-design.md",
            "description": "Component architecture, composition patterns, and UI organisation",
        }
        instructions["style-guide"] = {
            "page": "style-guide.md",
            "description": "CSS style rules and conventions",
        }
        instructions["new-page"] = {
            "page": "new-page.md",
            "description": "How to wire a new page into the UI",
        }

    return instructions
