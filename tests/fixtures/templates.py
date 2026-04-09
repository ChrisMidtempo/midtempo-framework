"""Test fixture utilities for Jinja2 template testing."""

from typing import Any

from jinja2 import Environment, StrictUndefined


def create_jinja_env_with_filters() -> Environment:
    """
    Create Jinja2 environment with custom filters registered.

    Imports and registers the cmd and category filters from generate_docs.py.

    Returns:
        Configured Jinja2 Environment with filters
    """
    from scripts.filters import _category_filter, _cmd_filter

    env = Environment(undefined=StrictUndefined)
    env.filters["cmd"] = _cmd_filter
    env.filters["category"] = _category_filter
    return env


def render_test_template(template_str: str, context: dict[str, Any]) -> str:
    """
    Render a template string with context.

    Args:
        template_str: Jinja2 template string to render
        context: Context dictionary for template rendering

    Returns:
        Rendered template string

    Raises:
        UndefinedError: If template references undefined variable
    """
    env = create_jinja_env_with_filters()
    template = env.from_string(template_str)
    return template.render(context)
