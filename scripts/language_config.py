"""Language configuration and enrichment utilities.

Handles loading language defaults, scope validation, and config merging.
"""

import copy
import re
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import yaml
from jinja2 import Environment, FileSystemLoader

from scripts.capabilities import DEFAULT_CAPABILITIES


def _validate_language_scopes(language_mapping: dict[str, str]) -> None:
    """
    Validate language scope configuration rules.

    Args:
        language_mapping: Dict mapping language names to scope values

    Raises:
        ValueError: If validation rules are violated
    """
    scopes = list(language_mapping.values())

    # Rule 1: Multiple languages cannot all use "all" scope
    if len(language_mapping) > 1 and "all" in scopes:
        raise ValueError(
            f"Scope 'all' cannot be used with multiple languages. "
            f"Found languages: {', '.join(language_mapping.keys())} "
            f"with 'all' scope. Use specific scope names like 'backend', 'frontend'."
        )

    # Rule 2: No duplicate scope values
    if len(scopes) != len(set(scopes)):
        # Find duplicates
        seen: dict[str, str] = {}
        duplicates: dict[str, list[str]] = {}
        for lang, scope in language_mapping.items():
            if scope in seen:
                duplicates.setdefault(scope, [seen[scope]]).append(lang)
            seen[scope] = lang

        dup_scope = next(iter(duplicates))
        dup_langs = duplicates[dup_scope]
        raise ValueError(
            f"Duplicate scope values detected: scope '{dup_scope}' "
            f"used by languages: {', '.join(dup_langs)}. "
            f"Each language must have unique scope identifier."
        )


def _apply_scope_to_description(description: str, scope: str) -> str:
    """
    Apply scope context to command description string.

    Args:
        description: Original description from defaults
        scope: Scope value to apply

    Returns:
        Description with scope context applied
    """
    if scope == "all":
        return description  # No change for mono-language

    # Replace " all " with " {scope} "
    scoped_desc = description.replace(" all ", f" {scope} ")

    # If no replacement made, insert scope after "Run "
    if scoped_desc == description and scoped_desc.startswith("Run "):
        scoped_desc = scoped_desc.replace("Run ", f"Run {scope} ", 1)

    return scoped_desc


def _load_language_defaults(language: str, commands_dir: Path) -> dict[str, Any]:
    """
    Load and validate language defaults from template file or legacy YAML file.

    Args:
        language: Language name
        commands_dir: Directory containing language template files

    Returns:
        Parsed language defaults dictionary with 'core' section

    Raises:
        FileNotFoundError: If language file doesn't exist
        KeyError: If language file missing required core commands
    """
    template_file = commands_dir / f"{language}.yml.j2"
    legacy_file = commands_dir / f"{language}.yml"

    # Try template file first (new format)
    if template_file.exists():
        # Render template with minimal base config
        base_config = {
            "name": "temp-project",
            "repo": {
                "title": "Temp Project",
                "language": {language: "all"},
            },
            "capabilities": {**DEFAULT_CAPABILITIES},
        }

        env = Environment(loader=FileSystemLoader(commands_dir))
        template = env.get_template(f"{language}.yml.j2")
        base_config_yaml = yaml.dump(base_config, sort_keys=False)
        rendered = template.render(base_config=base_config_yaml)

        # Parse rendered YAML
        config = yaml.safe_load(rendered)

        if "commands" not in config:
            raise KeyError(f"Language template {language}.yml.j2 missing 'commands' section")

        # Extract core commands (test, lint, typecheck)
        core_commands = {}
        for cmd_name in ["test", "lint", "typecheck"]:
            if cmd_name in config["commands"]:
                core_commands[cmd_name] = config["commands"][cmd_name]

        # Group remaining commands as variants
        variants = {}
        for cmd_name, cmd_config in config["commands"].items():
            if cmd_name not in core_commands:
                variants[cmd_name] = cmd_config

        # Return in expected structure with sections
        result = {"core": core_commands}
        if variants:
            result["variants"] = variants

        return result

    # Fall back to legacy .yml file (for test fixtures)
    elif legacy_file.exists():
        with legacy_file.open() as f:
            language_defaults: dict[str, Any] = yaml.safe_load(f)

        if "core" not in language_defaults:
            raise KeyError(f"Language file {language}.yml missing required 'core' section")

        return language_defaults

    # Neither file exists
    else:
        available_languages = sorted(
            [f.stem.replace(".yml", "") for f in commands_dir.glob("*.yml.j2") if f.is_file()]
        )
        raise FileNotFoundError(
            f"Language defaults file not found: {language}.yml. "
            f"Supported languages: {', '.join(available_languages)}"
        )


def _collect_sections_to_merge(language_defaults: dict[str, Any]) -> list[str]:
    """
    Collect section names to merge from language defaults.

    Args:
        language_defaults: Parsed language defaults dictionary

    Returns:
        List of section names to merge (core is always first)
    """
    sections = ["core"]
    for optional_section in ["variants", "formatting", "documentation"]:
        if optional_section in language_defaults:
            sections.append(optional_section)
    return sections


def _merge_section_commands(
    enriched: dict[str, Any], section_commands: dict[str, Any] | None, scope: str
) -> None:
    """
    Merge commands from a section into enriched config.

    Args:
        enriched: Config dictionary to merge into (mutated in-place)
        section_commands: Commands from a YAML section (may be None)
        scope: Scope string for command naming
    """
    if section_commands is None:
        return

    for cmd_name, cmd_def in section_commands.items():
        scoped_name = cmd_name if scope == "all" else f"{scope}_{cmd_name}"

        if scoped_name not in enriched["commands"]:
            scoped_desc = _apply_scope_to_description(cmd_def["description"], scope)
            enriched["commands"][scoped_name] = {
                "command": cmd_def["command"],
                "description": scoped_desc,
                "category": cmd_def["category"],
            }


def _enrich_config_with_language_defaults(config: dict, commands_dir: Path) -> dict:
    """
    Enrich config with language-specific command defaults.

    Iterates all languages in repo.language mapping, loads their defaults files,
    and merges commands from all sections (core, variants, formatting, documentation)
    with scope-aware naming. For mono-language configs with 'all' scope, generates
    bare command names. For multi-language configs, generates scoped command names
    ({scope}_{command} pattern).

    Args:
        config: Configuration dictionary with repo.language field
        commands_dir: Directory containing language YML files

    Returns:
        Enriched config dictionary with language defaults merged

    Raises:
        ValueError: If multiple languages use 'all' scope or duplicate scopes detected
        FileNotFoundError: If language YML file doesn't exist
        KeyError: If language YML missing required 'core' section
    """
    enriched = copy.deepcopy(config)
    language_mapping = enriched["repo"]["language"]

    _validate_language_scopes(language_mapping)

    if "commands" not in enriched:
        enriched["commands"] = {}

    for language, scope in language_mapping.items():
        language_defaults = _load_language_defaults(language, commands_dir)
        sections_to_merge = _collect_sections_to_merge(language_defaults)

        for section_name in sections_to_merge:
            section_commands = language_defaults[section_name]
            _merge_section_commands(enriched, section_commands, scope)

    return enriched


def _generate_config_file(
    config_path: Path,
    framework_version: str,
) -> None:
    """
    Update config file in place with metadata using text manipulation to preserve comments.

    Args:
        config_path: Path to input config file to update
        framework_version: Framework version to include in metadata
    """
    # Read existing config as text
    content = config_path.read_text()

    # Generate new metadata values
    generated_at = datetime.now(UTC).isoformat()

    # Check if metadata section exists
    metadata_pattern = r"^metadata:\s*$"
    has_metadata = bool(re.search(metadata_pattern, content, re.MULTILINE))

    if has_metadata:
        # Update existing metadata fields
        # Update generated_at if present, otherwise add it
        generated_at_pattern = r"^(\s+)generated_at:.*$"
        if re.search(generated_at_pattern, content, re.MULTILINE):
            content = re.sub(
                generated_at_pattern,
                rf"\1generated_at: '{generated_at}'",
                content,
                flags=re.MULTILINE,
            )
        else:
            # Add generated_at after metadata: line
            content = re.sub(
                metadata_pattern,
                rf"metadata:\n  generated_at: '{generated_at}'",
                content,
                flags=re.MULTILINE,
            )

        # Update framework_version if present, otherwise add it
        framework_version_pattern = r"^(\s+)framework_version:.*$"
        if re.search(framework_version_pattern, content, re.MULTILINE):
            content = re.sub(
                framework_version_pattern,
                rf"\1framework_version: {framework_version}",
                content,
                flags=re.MULTILINE,
            )
        else:
            # Add framework_version after generated_at
            generated_at_line_pattern = r"^(\s+generated_at:.*)$"
            content = re.sub(
                generated_at_line_pattern,
                rf"\1\n  framework_version: {framework_version}",
                content,
                flags=re.MULTILINE,
            )
    else:
        # Append new metadata section at the end
        metadata_section = f"\nmetadata:\n  generated_at: '{generated_at}'\n  framework_version: {framework_version}\n"
        content = content.rstrip() + metadata_section

    # Write back to same file
    config_path.write_text(content)
