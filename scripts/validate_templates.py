"""Template syntax validator for Jinja2 templates."""

import argparse
import contextlib
import re
import sys
from pathlib import Path
from typing import Any

import yaml
from jinja2 import Environment, FileSystemLoader, meta
from jinja2.exceptions import TemplateError, UndefinedError


def _check_variable_exists(var: str, available_vars: set[str]) -> bool:
    """
    Check if a variable exists in the available variables set.

    Args:
        var: Variable name to check
        available_vars: Set of available variable paths

    Returns:
        True if variable exists as top-level key or nested path
    """
    return var in available_vars or any(av.startswith(f"{var}.") for av in available_vars)


def _find_variable_line_number(var: str, template_source: str, template_name: str) -> str:
    """
    Find the line number where a variable appears in template source.

    Args:
        var: Variable name to find
        template_source: Template source code
        template_name: Template file name for reporting

    Returns:
        Formatted string with location (filename:line or just filename)
    """
    for line_num, line in enumerate(template_source.split("\n"), 1):
        if f"{{{{ {var}" in line or f"{{{{{var}" in line:
            return f"{template_name}:{line_num}: {var}"
    # If no specific line found, just report the variable
    return f"{template_name}: {var}"


def find_unused_variables(template_dir: Path, config: dict[str, Any]) -> list[str]:
    """
    Find variables used in templates that are not defined in config.

    Args:
        template_dir: Directory containing templates
        config: Config dictionary with available variables

    Returns:
        List of unused variable references with file:line context
    """
    env = Environment(loader=FileSystemLoader(str(template_dir)))
    _register_stub_filters(env)
    unused_vars = []

    # Get all template files
    template_files = list(template_dir.rglob("*.j2"))

    # Build set of available variables from config (top-level keys are what Jinja2 sees)
    def get_available_variables(d: dict[str, Any]) -> set[str]:
        """Get all top-level and nested keys accessible in templates."""
        keys: set[str] = set()

        def add_keys(obj: Any, prefix: str = "") -> None:
            """
            Recursively add dictionary keys to keys set with dotted paths.

            Args:
                obj: Object to extract keys from (processes dicts only)
                prefix: Current dotted path prefix for nested keys
            """
            if isinstance(obj, dict):
                for key, value in obj.items():
                    full_key = f"{prefix}.{key}" if prefix else key
                    keys.add(full_key)
                    # If value is a dict, recurse to add nested keys
                    if isinstance(value, dict):
                        add_keys(value, full_key)

        add_keys(d)
        return keys

    available_vars = get_available_variables(config)

    for template_file in template_files:
        template_name = str(template_file.relative_to(template_dir))
        template_source = template_file.read_text()

        # Parse template to find undeclared variables
        try:
            parsed_content = env.parse(template_source)
            undeclared = meta.find_undeclared_variables(parsed_content)

            # Check which undeclared variables are not in config
            for var in undeclared:
                if not _check_variable_exists(var, available_vars):
                    location = _find_variable_line_number(var, template_source, template_name)
                    unused_vars.append(location)

        except Exception:
            # Skip templates that can't be parsed
            continue

    return unused_vars


def find_orphaned_partials(template_dir: Path) -> list[Path]:
    """
    Find partial templates not included by any template.

    Args:
        template_dir: Directory containing templates

    Returns:
        List of orphaned partial file paths
    """
    # Find all partial files (in partials/ subdirectory)
    partials_dir = template_dir / "partials"
    if not partials_dir.exists():
        return []

    partial_files = set(partials_dir.rglob("*.j2"))
    if not partial_files:
        return []

    # Find all non-partial template files
    all_template_files = list(template_dir.rglob("*.j2"))
    non_partial_files = [
        f
        for f in all_template_files
        if not str(f.relative_to(template_dir)).startswith("partials/")
    ]

    # Track which partials are included
    included_partials = set()

    # Scan all templates for {% include %} statements
    include_pattern = re.compile(r'{%\s*include\s+["\']([^"\']+)["\']\s*%}')

    for template_file in non_partial_files:
        try:
            content = template_file.read_text()
            matches = include_pattern.findall(content)
            for match in matches:
                # Resolve the included file path
                # Could be relative to template_dir or partials/
                potential_paths = [
                    template_dir / match,
                    partials_dir / match,
                    template_dir / match if not match.endswith(".j2") else template_dir / match,
                ]
                for path in potential_paths:
                    if path.exists() and path in partial_files:
                        included_partials.add(path)
        except Exception:
            # Skip files that can't be read
            continue

    # Return partials that are not included
    orphaned = [p for p in partial_files if p not in included_partials]
    return orphaned


def _collect_validation_errors(
    template_dir: Path, config: dict[str, Any], check_content: bool
) -> list[str]:
    """
    Collect validation errors from template analysis.

    Args:
        template_dir: Directory containing templates
        config: Config dictionary for validation
        check_content: If True, validate variable usage

    Returns:
        List of error messages
    """
    errors = []

    # Check for unused variables (only if check_content is True)
    if check_content:
        unused_vars = find_unused_variables(template_dir, config)
        if unused_vars:
            for var in unused_vars:
                errors.append(f"Undefined variable: {var}")

    # Check basic syntax validation (circular inheritance, etc.)
    try:
        validate_all_templates(template_dir)
    except RecursionError as e:
        errors.append(str(e))
    except TemplateError as e:
        # Only add non-undefined errors (circular inheritance, syntax errors, etc.)
        if "undefined" not in str(e).lower():
            errors.append(str(e))

    return errors


def _collect_validation_warnings(template_dir: Path) -> list[str]:
    """
    Collect validation warnings from template analysis.

    Args:
        template_dir: Directory containing templates

    Returns:
        List of warning messages
    """
    warnings = []

    # Check for orphaned partials (warnings)
    orphaned = find_orphaned_partials(template_dir)
    if orphaned:
        for partial in orphaned:
            rel_path = partial.relative_to(template_dir)
            warnings.append(f"Orphaned partial: {rel_path}")

    return warnings


def validate_templates_with_config(
    template_dir: Path, config: dict[str, Any], strict: bool = False, check_content: bool = True
) -> bool:
    """
    Validate templates against config, optionally treating warnings as errors.

    Args:
        template_dir: Directory containing templates
        config: Config dictionary for validation
        strict: If True, warnings are treated as errors
        check_content: If True, validate variable usage (default: True for backward compatibility)

    Returns:
        True if validation passes

    Raises:
        ValueError: If validation fails or strict mode encounters warnings
    """
    # Collect errors and warnings using helper functions
    errors = _collect_validation_errors(template_dir, config, check_content)
    warnings = _collect_validation_warnings(template_dir)

    # Report errors
    if errors:
        raise ValueError("\n".join(errors))

    # In strict mode, treat warnings as errors
    if strict and warnings:
        raise ValueError(f"Strict mode: {len(warnings)} warnings found:\n" + "\n".join(warnings))

    return True


def validate_template_syntax(template_path: Path) -> bool:
    """
    Validate Jinja2 template syntax.

    Args:
        template_path: Path to template file

    Returns:
        True if valid, raises exception if invalid

    Raises:
        TemplateSyntaxError: If template has syntax errors
    """
    # Create environment with the template's parent directory as loader
    env = Environment(loader=FileSystemLoader(str(template_path.parent)))
    _register_stub_filters(env)

    # Parse template to check for syntax errors (raises TemplateSyntaxError if invalid)
    env.parse(template_path.read_text())

    return True


def _register_stub_filters(env: Environment) -> None:
    """
    Register stub custom filters so templates parse without errors.

    The generation pipeline (generate_docs.py) registers real filters (cmd, category,
    instructions). During validation we only need the names to exist so Jinja2's
    parser accepts the templates.

    Args:
        env: Jinja2 Environment to register stub filters on
    """
    _stub = lambda value: ""  # noqa: E731
    for name in ("cmd", "category", "instructions"):
        env.filters[name] = _stub


def validate_all_templates(template_dir: Path) -> bool:
    """
    Validate all templates in directory (syntax only).

    This validates template structure (syntax, inheritance) without rendering content.
    Use validate_templates_with_config() to also validate variable usage.

    Args:
        template_dir: Directory containing templates

    Returns:
        True if all templates valid

    Raises:
        TemplateSyntaxError: If any template has syntax errors
        TemplateError: If circular inheritance detected
    """
    # Create environment with the template directory as loader
    env = Environment(loader=FileSystemLoader(str(template_dir)))
    _register_stub_filters(env)

    # Find all .j2 template files
    template_files = list(template_dir.rglob("*.j2"))

    # Validate each template
    for template_file in template_files:
        # Get relative path for template name
        template_name = str(template_file.relative_to(template_dir))

        try:
            # Parse template to check syntax (doesn't require variables)
            template_source = template_file.read_text()
            env.parse(template_source)

            # Render with empty context to detect circular inheritance
            # (this is the only reliable way to detect it in Jinja2)
            # We ignore UndefinedError since that's handled separately by find_unused_variables
            template = env.get_template(template_name)
            with contextlib.suppress(UndefinedError):
                # Expected when template uses variables - this is okay for syntax validation
                template.render({})
        except RecursionError:
            # Circular inheritance causes recursion error
            raise TemplateError(
                f"Circular template inheritance detected in {template_name}"
            ) from None

    return True


def main() -> int:
    """CLI entry point for template validation."""
    parser = argparse.ArgumentParser(
        description="Validate Jinja2 templates syntax and variable usage"
    )
    parser.add_argument(
        "--template-dir",
        type=Path,
        default=Path("jinja-templates"),
        help="Directory containing templates (default: jinja-templates)",
    )
    parser.add_argument(
        "--config",
        type=Path,
        help="Path to YAML config file for validation (optional)",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Treat warnings as errors",
    )
    parser.add_argument(
        "--syntax-only",
        action="store_true",
        help="Only validate syntax, skip variable and content checks",
    )

    args = parser.parse_args()

    try:
        template_dir = args.template_dir
        if not template_dir.exists():
            print(f"Error: Template directory not found: {template_dir}", file=sys.stderr)
            return 1

        # If config is provided, do full validation
        if args.config:
            config_path = args.config
            if not config_path.exists():
                print(f"Error: Config file not found: {config_path}", file=sys.stderr)
                return 1

            with config_path.open() as f:
                config = yaml.safe_load(f)

            check_content = not args.syntax_only
            validate_templates_with_config(
                template_dir, config, strict=args.strict, check_content=check_content
            )
            print(f"✓ All templates validated successfully (config: {config_path})")
        else:
            # Syntax-only validation
            validate_all_templates(template_dir)
            print("✓ All templates validated successfully (syntax only)")

        return 0

    except ValueError as e:
        print(f"Validation failed:\n{e}", file=sys.stderr)
        return 1
    except TemplateError as e:
        print(f"Template error:\n{e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
