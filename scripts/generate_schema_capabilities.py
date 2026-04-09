"""Schema generation script for capability properties.

Reads CAPABILITIES registry and generates JSON Schema properties section,
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


def generate_schema(registry: dict[str, dict[str, bool | str]], schema_path: str) -> None:
    """Generate and update schema file with capability properties.

    Args:
        registry: CAPABILITIES dict from capabilities module
        schema_path: Path to schema JSON file

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

    # Write updated schema back to disk
    with schema_file.open("w") as f:
        json.dump(schema, f, indent=2)
        f.write("\n")  # Add trailing newline


def main() -> None:
    """Main entry point for schema generation."""
    from scripts.capabilities import CAPABILITIES

    # Get schema path relative to project root
    project_root = Path(__file__).parent.parent
    schema_path = project_root / "schema" / "config.schema.json"

    generate_schema(CAPABILITIES, str(schema_path))


if __name__ == "__main__":
    main()
