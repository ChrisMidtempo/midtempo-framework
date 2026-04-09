"""Add language to existing midtempo-framework.yml configuration.

This script transforms single-language configs to multi-language with scope prefixing,
or adds languages to existing multi-language configs while preserving comments and formatting.
"""

import json
import re
from pathlib import Path
from typing import Any

import yaml
from jinja2 import Environment, FileSystemLoader
from jsonschema import ValidationError, validate
from ruamel.yaml import YAML
from ruamel.yaml.comments import CommentedMap

from scripts.capabilities import DEFAULT_CAPABILITIES
from scripts.paths import CONFIG_SCHEMA_PATH

# Path constants
COMMANDS_DIR = Path(__file__).parent.parent / "commands"
AGENTS_DIR = Path(__file__).parent.parent / "agents"

# Validation constants
SCOPE_PATTERN = re.compile(r"^[a-z][a-z0-9_-]*$")
SCOPE_MIN_LENGTH = 2
SCOPE_MAX_LENGTH = 20
RESERVED_REPO_NAME = "midtempo-framework"
CORE_COMMANDS = ["test", "lint", "typecheck"]


def _discover_languages() -> list[str]:
    """
    Discover available languages by scanning commands/*.yml.j2 template files.

    Returns:
        List of available language names (e.g., ['python', 'typescript'])
    """
    if not COMMANDS_DIR.exists():
        return []

    languages = []
    for template_file in COMMANDS_DIR.glob("*.yml.j2"):
        # Extract language name from "language.yml.j2" -> "language"
        language_name = template_file.stem.replace(".yml", "")
        languages.append(language_name)

    return sorted(languages)


def _load_language_config(language: str) -> dict[str, Any]:
    """
    Load core commands from commands/{language}.yml.j2 template file.

    Args:
        language: Language name (e.g., 'python', 'typescript')

    Returns:
        Dictionary containing language config with 'core' commands extracted from template

    Raises:
        FileNotFoundError: If language template file doesn't exist
        ValueError: If core commands missing (test, lint, typecheck)
    """
    template_path = COMMANDS_DIR / f"{language}.yml.j2"

    if not template_path.exists():
        raise FileNotFoundError(f"Language config not found: {template_path}")

    # Render template with minimal base config
    base_config = {
        "name": "temp-project",
        "repo": {
            "title": "Temp Project",
            "language": {language: "all"},
        },
        "capabilities": {**DEFAULT_CAPABILITIES},
    }

    env = Environment(loader=FileSystemLoader(COMMANDS_DIR))
    template = env.get_template(f"{language}.yml.j2")
    base_config_yaml = yaml.dump(base_config, sort_keys=False)
    rendered = template.render(base_config=base_config_yaml)

    # Parse rendered YAML
    config = yaml.safe_load(rendered)

    # Extract core commands from the commands section
    if "commands" not in config:
        raise ValueError(f"Language config '{language}' missing 'commands' section")

    # Extract only core commands (test, lint, typecheck)
    core_commands = {}
    for cmd_name in CORE_COMMANDS:
        if cmd_name not in config["commands"]:
            raise ValueError(f"Language config '{language}' missing core command: {cmd_name}")
        core_commands[cmd_name] = config["commands"][cmd_name]

    # Return in the expected structure with 'core' section
    return {"core": core_commands}


def _validate_scope_pattern(scope: str) -> None:
    """
    Validate scope matches schema pattern ^[a-z][a-z0-9_-]*$ with length 2-20.

    Args:
        scope: Scope identifier to validate

    Raises:
        ValueError: If scope doesn't match pattern or length requirements
    """
    if not SCOPE_PATTERN.match(scope):
        raise ValueError(f"Scope must match ^[a-z][a-z0-9_-]*$ (2-20 chars). Got: {scope}")

    if len(scope) < SCOPE_MIN_LENGTH or len(scope) > SCOPE_MAX_LENGTH:
        raise ValueError(
            f"Scope must match ^[a-z][a-z0-9_-]*$ (2-20 chars). Got: {len(scope)} characters"
        )


def _detect_mode(config: dict[str, Any]) -> str:
    """
    Detect if config is single-language or multi-language mode.

    Single-language: any repo.language[*] == "all"
    Multi-language: all repo.language[*] != "all"

    Args:
        config: Config dictionary

    Returns:
        "single" or "multi"
    """
    languages = config.get("repo", {}).get("language", {})

    for scope in languages.values():
        if scope == "all":
            return "single"

    return "multi"


def _validate_no_collision(
    config: dict[str, Any], new_scope: str, core_commands: list[str]
) -> list[str]:
    """
    Check if new scoped commands would collide with existing commands.

    Args:
        config: Config dictionary with commands section
        new_scope: Scope for new language (e.g., 'frontend')
        core_commands: List of core command names (e.g., ['test', 'lint', 'typecheck'])

    Returns:
        List of conflicting command keys (empty if no conflicts)
    """
    existing_commands = config.get("commands", {})
    conflicts = []

    for cmd in core_commands:
        scoped_command = f"{new_scope}_{cmd}"
        if scoped_command in existing_commands:
            conflicts.append(scoped_command)

    return conflicts


def _transform_single_to_multi(
    config: dict[str, Any], existing_language: str, existing_scope: str
) -> None:
    """
    Transform single-language config to multi-language by renaming scope and prefixing commands.

    Modifies config in-place:
    - Changes repo.language[existing_language] from "all" to existing_scope
    - Renames all command keys: {cmd} → {existing_scope}_{cmd}

    Args:
        config: Config dictionary to transform (modified in-place)
        existing_language: Current language key (e.g., 'python')
        existing_scope: New scope for existing language (e.g., 'backend')
    """
    # Update language scope
    config["repo"]["language"][existing_language] = existing_scope

    # Rename all command keys with scope prefix
    commands = config.get("commands", {})
    command_keys = list(commands.keys())

    for old_key in command_keys:
        new_key = f"{existing_scope}_{old_key}"
        # Preserve comments and structure by copying the value
        commands[new_key] = commands[old_key]
        del commands[old_key]


def _add_language_to_config(config: dict[str, Any], language: str, new_scope: str) -> None:
    """
    Add new language to config with scoped commands.

    Modifies config in-place:
    - Adds {language: new_scope} to repo.language
    - Inserts {new_scope}_test, {new_scope}_lint, {new_scope}_typecheck commands

    Args:
        config: Config dictionary to modify (modified in-place)
        language: Language to add (e.g., 'typescript')
        new_scope: Scope for new language (e.g., 'frontend')
    """
    # Load language config
    lang_config = _load_language_config(language)

    # Add language to repo.language
    config["repo"]["language"][language] = new_scope

    # Add scoped commands from language core commands
    commands = config.get("commands", CommentedMap())
    if "commands" not in config:
        config["commands"] = commands

    for cmd_name, cmd_config in lang_config["core"].items():
        scoped_name = f"{new_scope}_{cmd_name}"
        # Create new command entry preserving structure
        commands[scoped_name] = CommentedMap(
            {
                "command": cmd_config["command"],
                "description": cmd_config["description"],
                "category": cmd_config["category"],
            }
        )


def _load_yaml_with_comments(file_path: Path) -> tuple[YAML, dict[str, Any]]:
    """
    Load YAML file preserving comments and formatting using ruamel.yaml.

    Args:
        file_path: Path to YAML file

    Returns:
        Tuple of (YAML handler instance, config dict)

    Raises:
        FileNotFoundError: If file doesn't exist
    """
    if not file_path.exists():
        raise FileNotFoundError(f"Config not found at {file_path}")

    yaml_handler = YAML()
    yaml_handler.preserve_quotes = True
    yaml_handler.default_flow_style = False
    yaml_handler.width = 4096  # Prevent line wrapping

    with file_path.open() as f:
        config = yaml_handler.load(f)

    return yaml_handler, config


def _write_yaml_with_comments(yaml_handler: YAML, config: dict[str, Any], file_path: Path) -> None:
    """
    Write YAML file preserving comments and formatting using ruamel.yaml.

    Args:
        yaml_handler: YAML instance used to load the config
        config: Config dictionary to write
        file_path: Path to write YAML file

    Raises:
        IOError: If write fails
    """
    with file_path.open("w") as f:
        yaml_handler.dump(config, f)


def add_language(
    repo: str,
    language: str,
    new_scope: str,
    existing_scope: str | None = None,
    config_path: Path | None = None,
) -> bool:
    """
    Add language to existing midtempo-framework.yml configuration.

    Transforms single-language configs to multi-language with scope renaming,
    or extends multi-language configs with new language.

    Args:
        repo: Repository folder name in agents/
        language: Language to add (must exist in commands/*.yml)
        new_scope: Scope identifier for new language (e.g., 'frontend')
        existing_scope: Scope for existing language (required for single-language configs)
        config_path: Optional path to config file (defaults to agents/{repo}/midtempo-framework.yml)

    Returns:
        True if successful

    Raises:
        ValueError: If validation fails (invalid language, scope, duplicate, collision, etc.)
        FileNotFoundError: If config file doesn't exist
    """
    # Validate reserved repo name
    if repo == RESERVED_REPO_NAME:
        raise ValueError(f"Cannot modify reserved '{RESERVED_REPO_NAME}' config")

    # Validate language is supported
    available_languages = _discover_languages()
    if language not in available_languages:
        raise ValueError(
            f"Language '{language}' not supported. " f"Available: {', '.join(available_languages)}"
        )

    # Validate scope pattern
    _validate_scope_pattern(new_scope)
    if existing_scope:
        _validate_scope_pattern(existing_scope)

    # Determine config path
    if config_path is None:
        config_path = AGENTS_DIR / repo / "midtempo-framework.yml"

    # Load config with comment preservation
    yaml_handler, config = _load_yaml_with_comments(config_path)

    # Check for duplicate language
    existing_languages = config.get("repo", {}).get("language", {})
    if language in existing_languages:
        raise ValueError(f"Language '{language}' already exists in config")

    # Detect mode
    mode = _detect_mode(config)

    # Validate existing_scope requirement for single-language configs
    if mode == "single" and existing_scope is None:
        raise ValueError(
            "Config is single-language but --existing-scope not provided. "
            "Use --existing-scope to specify scope for existing language."
        )

    # Check for command collisions
    conflicts = _validate_no_collision(config, new_scope, CORE_COMMANDS)
    if conflicts:
        raise ValueError(f"Scoped commands conflict with existing: {', '.join(conflicts)}")

    # Transform single→multi if needed
    if mode == "single":
        # existing_scope is guaranteed to be not None by the validation above
        assert (
            existing_scope is not None
        ), "existing_scope must be provided for single-language configs"
        existing_language = list(existing_languages.keys())[0]
        _transform_single_to_multi(config, existing_language, existing_scope)

    # Add new language
    _add_language_to_config(config, language, new_scope)

    # Validate transformed config against schema
    # Convert to plain dict for validation
    from io import StringIO

    stream = StringIO()
    yaml_handler.dump(config, stream)
    config_dict = yaml.safe_load(stream.getvalue())

    # Load schema and validate
    with CONFIG_SCHEMA_PATH.open() as f:
        schema = json.load(f)

    try:
        validate(instance=config_dict, schema=schema)
    except ValidationError as e:
        raise ValueError(f"Config validation failed: {e.message}") from e

    # Write config atomically with comment preservation
    _write_yaml_with_comments(yaml_handler, config, config_path)

    return True
