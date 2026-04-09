"""Build-time script to generate ui/json/languages.json from commands/*.yml.j2 templates."""

import json
import logging

import yaml
from jinja2 import Environment, FileSystemLoader

from scripts.paths import PROJECT_ROOT

logger = logging.getLogger(__name__)


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
    output: dict[str, list[dict[str, str]]] = {}

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

        output[language] = entries

    ui_dir = PROJECT_ROOT / "ui" / "json"
    ui_dir.mkdir(parents=True, exist_ok=True)
    (ui_dir / "languages.json").write_text(json.dumps(output, indent=2))


if __name__ == "__main__":
    build_ui_manifest()
