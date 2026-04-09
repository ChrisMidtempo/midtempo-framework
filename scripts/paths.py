"""Shared path constants for scripts."""

from pathlib import Path

# Base directory for the project
PROJECT_ROOT = Path(__file__).parent.parent

# Common paths used across scripts
TEMPLATE_DIR = PROJECT_ROOT / "jinja-templates"
SCHEMA_DIR = PROJECT_ROOT / "schema"
CONFIG_SCHEMA_PATH = SCHEMA_DIR / "config.schema.json"
COMMANDS_DIR = PROJECT_ROOT / "commands"
