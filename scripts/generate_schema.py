"""Schema generation script for capability and instruction properties.

Reads CAPABILITIES and INSTRUCTIONS registries and generates JSON Schema sections,
updating the schema file while preserving all other structure.
"""

import json
from pathlib import Path


def generate_properties(
    capabilities_dict: dict[str, dict[str, bool | str]],
) -> dict[str, dict[str, str]]:
    """Transform capability registry into JSON Schema properties.

    Args:
        capabilities_dict: Dict mapping capability names to metadata dicts
                          with 'default' and 'description' keys

    Returns:
        Dict of JSON Schema properties
    """
    properties = {}
    for name, metadata in capabilities_dict.items():
        properties[name] = {"type": "boolean", "description": str(metadata["description"])}
    return properties


def generate_instruction_properties(instructions_dict: dict[str, dict[str, str]]) -> dict:
    """Generate patternProperties structure for instructions.

    Args:
        instructions_dict: Dict mapping instruction names to metadata dicts
                          with 'page' and 'description' keys

    Returns:
        Dict with patternProperties structure for JSON Schema

    Raises:
        KeyError: If any registry entry lacks required 'page' or 'description' field
    """
    # Validate registry entries before generating schema
    for name, metadata in instructions_dict.items():
        if "page" not in metadata:
            raise KeyError(f"Instruction '{name}' missing required 'page' field")
        if "description" not in metadata:
            raise KeyError(f"Instruction '{name}' missing required 'description' field")

    return {
        "type": "object",
        "additionalProperties": False,
        "patternProperties": {
            "^[a-z][a-z0-9_-]*$": {
                "type": "object",
                "required": ["page", "description"],
                "properties": {
                    "page": {
                        "type": "string",
                        "minLength": 1,
                        "description": "Path to instruction file relative to instructions/ directory",
                    },
                    "description": {
                        "type": "string",
                        "minLength": 1,
                        "description": "Human-readable description of what this instruction covers",
                    },
                },
                "additionalProperties": False,
            }
        },
    }


def generate_security_properties() -> dict:
    """Generate patternProperties structure for security section.

    Returns:
        Dict with patternProperties structure for JSON Schema
    """
    return {
        "type": "object",
        "additionalProperties": False,
        "patternProperties": {
            "^[a-z][a-z0-9_-]*$": {
                "type": "object",
                "required": ["page", "description"],
                "properties": {
                    "page": {
                        "type": "string",
                        "minLength": 1,
                        "description": "Path to security rule sub-document",
                    },
                    "description": {
                        "type": "string",
                        "minLength": 1,
                        "description": "Human-readable description of the security domain",
                    },
                },
                "additionalProperties": False,
            }
        },
    }


def generate_schema(
    registry: dict[str, dict[str, bool | str]],
    schema_path: str,
    instructions_registry: dict[str, dict[str, str]] | None = None,
) -> None:
    """Generate and update schema file with capability and instruction properties.

    Args:
        registry: CAPABILITIES dict from capabilities module
        schema_path: Path to schema JSON file
        instructions_registry: Optional INSTRUCTIONS dict from instructions module

    Raises:
        FileNotFoundError: If schema file doesn't exist
        json.JSONDecodeError: If schema file has invalid JSON
    """
    schema_file = Path(schema_path)

    if not schema_file.exists():
        raise FileNotFoundError("schema/config.schema.json not found")

    # Load existing schema
    with schema_file.open() as f:
        schema = json.load(f)

    # Generate properties from registry
    properties = generate_properties(registry)

    # Update capabilities.properties section
    schema["properties"]["capabilities"]["properties"] = properties

    # Update instructions section if registry provided
    if instructions_registry is not None:
        instruction_properties = generate_instruction_properties(instructions_registry)
        schema["properties"]["instructions"] = instruction_properties

    # Update security section
    security_properties = generate_security_properties()
    schema["properties"]["security"] = security_properties

    # Write updated schema back to disk
    with schema_file.open("w") as f:
        json.dump(schema, f, indent=2)
        f.write("\n")  # Add trailing newline


def main() -> None:
    """Main entry point for schema generation."""
    from scripts.capabilities import CAPABILITIES
    from scripts.instructions import INSTRUCTIONS

    # Get schema path relative to project root
    project_root = Path(__file__).parent.parent
    schema_path = project_root / "schema" / "config.schema.json"

    generate_schema(CAPABILITIES, str(schema_path), INSTRUCTIONS)


if __name__ == "__main__":
    main()
