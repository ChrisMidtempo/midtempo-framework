"""Framework initialization API for creating midtempo-framework project configurations."""

from pathlib import Path
from typing import Any

import yaml
from jinja2 import Environment, FileSystemLoader

from scripts.capabilities import DEFAULT_CAPABILITIES
from scripts.paths import PROJECT_ROOT


def initialize_framework(folder_name: str, language: str) -> bool:
    """
    Initialize framework project configuration.

    Public API entry point. Creates folder if needed, generates
    midtempo-framework.yml with minimal valid configuration using Jinja2 templates.

    Args:
        folder_name: Target folder for project (created if doesn't exist)
        language: Programming language (must exist in commands/*.yml.j2)

    Returns:
        True on success

    Raises:
        ValueError: Language not supported (lists available languages) or reserved name used
        OSError: Folder creation or file write failed (permissions, I/O)
    """
    rendered = render_config_string(folder_name, language)

    folder_path = PROJECT_ROOT / "agents" / folder_name if folder_name else Path.cwd()
    folder_path.mkdir(parents=True, exist_ok=True)
    (folder_path / "midtempo-framework.yml").write_text(rendered)

    return True


def render_config_string(name: str, language: str) -> str:
    """
    Render configuration as a YAML string without writing to disk.

    Args:
        name: Project name (must not be reserved)
        language: Programming language (must exist in commands/*.yml.j2)

    Returns:
        Rendered YAML string

    Raises:
        ValueError: Reserved name used, language not supported, or rendered YAML is invalid
    """
    if name == "midtempo-framework":
        raise ValueError("The name 'midtempo-framework' is reserved")

    available_languages = _discover_languages()
    if language not in available_languages:
        raise ValueError(
            f"Language '{language}' not supported. Available: {', '.join(available_languages)}"
        )

    base_config = _build_base_config(name, language)

    commands_dir = PROJECT_ROOT / "commands"
    env = Environment(loader=FileSystemLoader(commands_dir))
    template = env.get_template(f"{language}.yml.j2")
    rendered = template.render(base_config=yaml.dump(base_config, sort_keys=False))

    try:
        yaml.safe_load(rendered)
    except yaml.YAMLError as e:
        raise ValueError(f"Template rendered invalid YAML: {e}") from e

    return rendered


def _discover_languages() -> list[str]:
    """
    Scan commands/*.yml.j2 for available languages.

    Returns:
        Sorted list of language names based on .yml.j2 template files in commands/ directory
    """
    commands_dir = PROJECT_ROOT / "commands"
    template_files = commands_dir.glob("*.yml.j2")
    # Extract language name from "language.yml.j2" -> "language"
    languages = [f.name.replace(".yml.j2", "") for f in template_files]
    return sorted(languages)


def _build_base_config(folder_name: str, language: str) -> dict[str, Any]:
    """
    Build base configuration dictionary with required fields.

    Args:
        folder_name: Project folder name
        language: Programming language

    Returns:
        Configuration dictionary with name, repo, capabilities fields

    Raises:
        ValueError: If folder_name is empty
    """
    if not folder_name:
        raise ValueError("Folder name is required")

    return {
        "name": folder_name,
        "repo": {
            "title": folder_name,
            "language": {language: "all"},
            "setup": True,
            "logfile": None,
            "agentFile": "AGENTS",
        },
        "capabilities": {**DEFAULT_CAPABILITIES},
    }
