"""Documentation generation script using Jinja2 templates."""

import sys
import time
import tomllib
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

# Add parent directory to path for direct script execution
if __name__ == "__main__":
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))

from jinja2 import Environment, FileSystemLoader, StrictUndefined, UndefinedError

from scripts.filters import (
    SmartContext,
    _category_filter,
    _category_impl,
    _cmd_filter,
    _cmd_impl,
    _instructions_filter,
    _instructions_impl,
    _InstructionsNamespace,
)
from scripts.language_config import (
    _generate_config_file,
)


def render_template_with_context(
    env: Environment, template_name: str, context: dict[str, Any], template_dir: Path
) -> str:
    """
    Render template with enhanced error messages showing file:line context.

    Args:
        env: Jinja2 environment
        template_name: Name of template file to render
        context: Context dictionary for template rendering
        template_dir: Directory containing templates (for error context)

    Returns:
        Rendered template string

    Raises:
        UndefinedError: With file:line context and config suggestion
    """
    try:
        template = env.get_template(template_name)
        return template.render(context)
    except UndefinedError as e:
        # Extract variable name from error message
        error_msg = str(e)

        # Try to find line number in template where error occurred
        template_path = template_dir / template_name
        if template_path.exists():
            # Enhanced error message with file context
            raise UndefinedError(
                f"{template_name}: {error_msg}\n"
                f"   → Check midtempo-framework.yml has the variable defined"
            ) from e
        else:
            # Fallback if template path not found
            raise UndefinedError(f"{template_name}: {error_msg}") from e


def _enrich_config(config: dict[str, Any]) -> None:
    """
    Enrich configuration dictionary with capability and context defaults.

    Modifies config in place: fills missing capability flags from
    DEFAULT_CAPABILITIES, sets agentFile default, wraps instructions in
    namespace, and adds dateStamp.

    Args:
        config: Configuration dictionary to enrich in place
    """
    from scripts.capabilities import DEFAULT_CAPABILITIES

    if "capabilities" not in config:
        config["capabilities"] = {}
    config["capabilities"] = {**DEFAULT_CAPABILITIES, **config["capabilities"]}

    if "repo" not in config:
        config["repo"] = {}
    config["repo"].setdefault("agentFile", "AGENTS")

    if "instructions" not in config:
        config["instructions"] = _InstructionsNamespace({})
    else:
        config["instructions"] = _InstructionsNamespace(config["instructions"])

    config["dateStamp"] = datetime.now(UTC).strftime("%d/%m/%Y")


def generate_documentation_with_timing(
    config_path: Path, output_dir: Path, template_dir: Path | None = None
) -> dict[str, Any]:
    """
    Generate documentation and return timing information.

    Args:
        config_path: Path to config YAML file
        output_dir: Directory to write generated documentation
        template_dir: Optional template directory (uses default if not provided)

    Returns:
        Dictionary with file_count and elapsed time in seconds
    """
    import yaml

    # Use provided template_dir or default
    use_default_template_dir = template_dir is None
    if template_dir is None:
        from scripts.paths import TEMPLATE_DIR

        template_dir = TEMPLATE_DIR

    # Start timing
    start_time = time.perf_counter()

    # Load config (validate only when using default template dir for production)
    if use_default_template_dir:
        from scripts.validate_config import validate_config

        config = validate_config(config_path)
    else:
        # For testing with custom template dir, just load YAML without strict validation
        with config_path.open() as f:
            config = yaml.safe_load(f)

    _enrich_config(config)

    # Use orchestration helper for namespaced generation (production mode)
    if "name" in config:
        from scripts.paths import PROJECT_ROOT

        file_count = _orchestrate_generation(
            config, config_path, template_dir, output_dir, PROJECT_ROOT
        )
    else:
        # Legacy behavior for tests without name field (backward compatibility)
        env = setup_jinja_environment(template_dir)
        file_count = _render_templates_to_directory(env, template_dir, config, output_dir)

    # Calculate elapsed time
    elapsed = time.perf_counter() - start_time

    return {"file_count": file_count, "elapsed": elapsed}


def setup_jinja_environment(template_dir: Path) -> Environment:
    """
    Setup Jinja2 environment with configuration.

    Args:
        template_dir: Directory containing Jinja2 templates

    Returns:
        Configured Jinja2 Environment
    """
    env = Environment(
        loader=FileSystemLoader(str(template_dir)),
        undefined=StrictUndefined,
        trim_blocks=True,
        lstrip_blocks=True,
    )
    env.filters["cmd"] = _cmd_filter
    env.filters["category"] = _category_filter
    env.filters["instructions"] = _instructions_filter

    # Load global macros and make them available in all templates
    macros_path = template_dir / "macros.j2"
    if macros_path.exists():
        # Load macros template and get module
        macros_template = env.get_template("macros.j2")
        macros_module = macros_template.make_module()

        # Add all macros from module to global namespace
        for name in dir(macros_module):
            if not name.startswith("_"):  # Skip private attributes
                env.globals[name] = getattr(macros_module, name)

    return env


def render_template(env: Environment, template_name: str, context: dict[str, Any]) -> str:
    """
    Render a template with given context.

    Args:
        env: Jinja2 environment
        template_name: Name of template file to render
        context: Context dictionary for template rendering

    Returns:
        Rendered template string

    Raises:
        UndefinedError: If template references undefined variable
        TemplateNotFound: If template file doesn't exist
    """
    template = env.get_template(template_name)
    return template.render(context)


def _remap_template_path(relative_path: Path) -> Path:
    """
    Remap template directory paths to output directory paths.

    Mapping rules:
    - agents/* → * (strip agents/ prefix, put files at root)
    - instructions/* → instructions/* (unchanged)
    - rules/* → rules/* (unchanged)
    - templates/* → templates/* (unchanged)
    - base/* → (should be skipped before calling this)

    Args:
        relative_path: Path to template file relative to template directory

    Returns:
        Remapped output path
    """
    parts = relative_path.parts

    if not parts:
        return relative_path

    first_dir = parts[0]

    if first_dir == "agents":
        # Remove "agents/" prefix - files go to root of output directory
        return Path(*parts[1:]) if len(parts) > 1 else relative_path
    else:
        # instructions/*, rules/*, templates/* all remain unchanged
        return relative_path


def _extract_framework_version(project_root: Path) -> str:
    """
    Extract version from pyproject.toml.

    Args:
        project_root: Path to project root directory containing pyproject.toml

    Returns:
        Framework version string

    Raises:
        FileNotFoundError: If pyproject.toml doesn't exist
        KeyError: If version field missing from pyproject.toml
    """
    pyproject_path = project_root / "pyproject.toml"

    with pyproject_path.open("rb") as f:
        data = tomllib.load(f)

    project_data = data["project"]
    version: str = project_data["version"]
    return version


def _cleanup_md_files(output_dir: Path) -> None:
    """
    Remove all .md files from output directory before generation.

    Preserves client-maintained instruction files in instructions/ subfolder.

    Args:
        output_dir: Directory to clean up
    """
    for md_file in output_dir.glob("**/*.md"):
        # Skip files in instructions/ subfolder (client-maintained)
        if "instructions" in md_file.parts:
            continue
        md_file.unlink()


def _orchestrate_generation(
    config: dict[str, Any],
    config_path: Path,
    template_dir: Path,
    output_dir: Path,
    project_root: Path,
) -> int:
    """
    Orchestrate template rendering and config generation.

    Coordinates the generation workflow: namespace setup, template rendering,
    and config file generation. This function intentionally handles multiple
    steps as it serves as the central orchestration point.

    Args:
        config: Configuration dictionary with name field
        config_path: Path to input config file (will be updated with metadata)
        template_dir: Directory containing Jinja2 templates
        output_dir: Base output directory
        project_root: Project root for version extraction

    Returns:
        Number of files rendered
    """
    # Auto-prefix with agents/[name]/ for non-framework projects
    # midtempo-framework uses /midtempo-framework/, others use /agents/[name]/
    project_name = config.get("name", "")
    if project_name == "midtempo-framework":
        namespaced_output_dir = output_dir / "midtempo-framework"
    else:
        namespaced_output_dir = output_dir / "agents" / project_name

    # Remove all existing .md files before generation
    _cleanup_md_files(namespaced_output_dir)

    # Setup Jinja2 environment
    env = setup_jinja_environment(template_dir)

    # Render all templates to output directory with user config (no enrichment)
    # Language defaults from commands/*.yml only used during init, not generation
    file_count = _render_templates_to_directory(env, template_dir, config, namespaced_output_dir)

    # Extract framework version and update config file with metadata
    framework_version = _extract_framework_version(project_root)
    _generate_config_file(config_path, framework_version)

    return file_count


def _should_skip_template(relative_path: Path, config: dict[str, Any]) -> bool:
    """
    Check if template should be skipped based on project capabilities.

    Always-skip rules:
    - base/* templates → Never generate (only for inheritance)
    - macros.j2 → Never generate (utility file with reusable macros)

    Capability-conditional rules are data-driven from TEMPLATE_SKIP_RULES in
    scripts.capabilities. Single-key entries skip when the named capability is
    falsy; multi-key entries skip when all listed capabilities are falsy.

    Args:
        relative_path: Path to template file relative to template directory
        config: Context dictionary containing capabilities

    Returns:
        True if template should be skipped, False otherwise
    """
    from scripts.capabilities import TEMPLATE_SKIP_RULES

    path_str = str(relative_path)

    # Skip base templates (only for inheritance, not direct generation)
    if path_str.startswith("base/"):
        return True

    # Skip macros.j2 (utility file with reusable macros, not for output)
    if path_str == "macros.j2":
        return True

    capabilities = config.get("capabilities", {})

    for pattern, keys in TEMPLATE_SKIP_RULES.items():
        if pattern in path_str:
            if isinstance(keys, list):
                if not any(capabilities.get(k, False) for k in keys):
                    return True
            elif not capabilities.get(keys, False):
                return True

    return False


def _render_templates_to_directory(
    env: Environment, template_dir: Path, config: dict[str, Any], output_dir: Path
) -> int:
    """
    Render all templates in directory to output directory.

    Private helper function to eliminate duplication between generation functions.

    Args:
        env: Jinja2 environment
        template_dir: Directory containing templates
        config: Context dictionary for template rendering
        output_dir: Directory to write generated documentation

    Returns:
        Number of files rendered
    """
    # Inject SmartContext as 'this' for macro access to filters
    filter_implementations = {
        "cmd": _cmd_impl,
        "category": _category_impl,
        "instructions": _instructions_impl,
    }
    config["this"] = SmartContext(config, filter_implementations)

    # Find all template files
    template_files = list(template_dir.rglob("*.j2"))

    files_rendered = 0

    # Render each template and write to output directory
    for template_file in template_files:
        # Get relative path from template directory
        relative_path = template_file.relative_to(template_dir)

        # Check if template should be skipped based on capabilities
        if _should_skip_template(relative_path, config):
            continue

        # Remap template path to output path
        remapped_path = _remap_template_path(relative_path)

        # Convert .j2 extension to .md for output
        output_path = output_dir / str(remapped_path).replace(".j2", "")

        # Rename AGENTS.md to CLAUDE.md when repo.agentFile is CLAUDE
        agent_file = config.get("repo", {}).get("agentFile", "AGENTS")
        if agent_file != "AGENTS" and output_path.name == "AGENTS.md":
            output_path = output_path.with_name(f"{agent_file}.md")

        # Create parent directories if needed
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Render template
        template_name = str(relative_path)
        rendered_content = render_template(env, template_name, config)

        # Write rendered content to output file
        output_path.write_text(rendered_content)

        files_rendered += 1

    return files_rendered


def generate_documentation(config_path: Path, output_dir: Path) -> bool:
    """
    Generate documentation from config and templates.

    Args:
        config_path: Path to config YAML file
        output_dir: Directory to write generated documentation

    Returns:
        True if generation succeeded, False otherwise
    """
    from scripts.paths import PROJECT_ROOT, TEMPLATE_DIR
    from scripts.validate_config import validate_config

    # Load and validate config
    config = validate_config(config_path)

    _enrich_config(config)

    # Orchestrate generation workflow
    _orchestrate_generation(config, config_path, TEMPLATE_DIR, output_dir, PROJECT_ROOT)

    return True
