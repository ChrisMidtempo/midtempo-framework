"""Build-time script to generate ui/json/languages.json from commands/*.yml.j2 templates."""

import json
import logging
import re

import yaml
from jinja2 import Environment, FileSystemLoader

from scripts.paths import PROJECT_ROOT

logger = logging.getLogger(__name__)

_MUTATION_KEY_PATTERN = re.compile(r"^  # (mutate(?:_diff)?):\s*$")
_MUTATION_SUB_KEY_PREFIX = "  #   "


def extract_mutation_commands(rendered: str) -> dict[str, dict]:
    """
    Extract commented-out mutation command stubs from a rendered command template.

    Scans for blocks of the form:
      # mutate:
      #   command: "..."
      #   description: "..."
      #   category: "test"

    Returns a dict keyed by command name (e.g. "mutate", "mutate_diff").
    Each value has the same shape as a regular commands entry: name, command, description, category.
    """
    lines = rendered.splitlines()
    result: dict[str, dict] = {}
    i = 0
    while i < len(lines):
        m = _MUTATION_KEY_PATTERN.match(lines[i])
        if m:
            cmd_key = m.group(1)
            block_parts = [lines[i][4:]]  # strip "  # " prefix → "mutate:"
            j = i + 1
            while j < len(lines) and lines[j].startswith(_MUTATION_SUB_KEY_PREFIX):
                block_parts.append(lines[j][4:])  # strip "  # " → "  key: value"
                j += 1
            try:
                parsed = yaml.safe_load("\n".join(block_parts))
                if isinstance(parsed, dict) and cmd_key in parsed:
                    cmd_data = parsed[cmd_key]
                    if isinstance(cmd_data, dict):
                        result[cmd_key] = {
                            "name": cmd_key,
                            "command": cmd_data.get("command", ""),
                            "description": cmd_data.get("description", ""),
                            "category": cmd_data.get("category", ""),
                        }
            except yaml.YAMLError:
                pass
            i = j
        else:
            i += 1
    return result


def build_ui_manifest() -> None:
    """
    Generate ui/json/languages.json from commands/*.yml.j2 templates.

    Discovers language templates, renders each with base_config="", extracts
    the commands section, and writes a JSON manifest consumed by the UI.

    Raises:
        FileNotFoundError: If PROJECT_ROOT / "commands" directory does not exist
    """
    commands_dir = PROJECT_ROOT / "commands"
    if not commands_dir.exists():
        raise FileNotFoundError(f"commands/ directory not found at {commands_dir}")

    env = Environment(loader=FileSystemLoader(commands_dir))
    output: dict[str, dict] = {}

    for template_path in sorted(commands_dir.glob("*.yml.j2")):
        language = template_path.stem.replace(".yml", "")
        template = env.get_template(template_path.name)
        rendered = template.render(base_config="")

        try:
            parsed = yaml.safe_load(rendered)
        except yaml.YAMLError:
            logger.warning("Skipping %s: failed to parse rendered YAML", language)
            continue

        if not parsed or "commands" not in parsed:
            continue

        entries = []
        for cmd_name, cmd_data in parsed["commands"].items():
            if not isinstance(cmd_data, dict):
                continue
            entries.append(
                {
                    "name": cmd_name,
                    "command": cmd_data.get("command", ""),
                    "description": cmd_data.get("description", ""),
                    "category": cmd_data.get("category", ""),
                }
            )

        output[language] = {
            "commands": entries,
            "mutationCommands": extract_mutation_commands(rendered),
        }

    ui_dir = PROJECT_ROOT / "ui" / "json"
    ui_dir.mkdir(parents=True, exist_ok=True)
    (ui_dir / "languages.json").write_text(json.dumps(output, indent=2))


if __name__ == "__main__":
    build_ui_manifest()
