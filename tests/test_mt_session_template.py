"""Tests for mt-session.md.j2 template cmd filter integration.

Covers:
- T4.1: Template renders `mutate` to consumer-configured command name
- T4.2: Template renders `mutate_diff` to consumer-configured command name
- T4.3: Rendering raises `KeyError` when `mutate` key absent from consumer config
"""

import pytest
from jinja2 import Environment, FileSystemLoader, StrictUndefined

from scripts.filters import _cmd_filter
from scripts.paths import TEMPLATE_DIR

TEMPLATE_NAME = "templates/mt-session.md.j2"


def _make_env() -> Environment:
    """Create a Jinja2 environment with cmd filter registered."""
    env = Environment(
        loader=FileSystemLoader(str(TEMPLATE_DIR)),
        undefined=StrictUndefined,
    )
    env.filters["cmd"] = _cmd_filter
    return env


def _make_consumer_config(mutate_command: str, mutate_diff_command: str) -> dict:
    """Build a consumer context dict with mutate and mutate_diff commands."""
    return {
        "commands": {
            "mutate": {
                "command": mutate_command,
                "description": "Run mutation tests",
                "category": "test",
            },
            "mutate_diff": {
                "command": mutate_diff_command,
                "description": "Run mutation tests on changed files since last commit",
                "category": "test",
            },
        }
    }


def test_template_renders_mutate_to_consumer_command():
    """Rendering mt-session.md.j2 resolves `mutate` to the consumer-configured command. (T4.1, B10)"""
    env = _make_env()
    template = env.get_template(TEMPLATE_NAME)
    consumer_command = "consumer-run-mutate-configured"
    context = _make_consumer_config(
        mutate_command=consumer_command,
        mutate_diff_command="consumer-run-mutate-diff-configured",
    )

    rendered = template.render(context)

    assert consumer_command in rendered, (
        f"Rendered mt-session.md.j2 does not contain consumer's mutate command "
        f"'{consumer_command}' — {{ 'mutate' | cmd }} filter not resolving consumer config"
    )
    assert "{{ 'mutate' | cmd }}" not in rendered, (
        "Rendered output still contains raw Jinja2 expression '{{ \\'mutate\\' | cmd }}' — "
        "template not rendering cmd filter correctly"
    )


def test_template_renders_mutate_diff_to_consumer_command():
    """Rendering mt-session.md.j2 resolves `mutate_diff` to the consumer-configured command. (T4.2, B10)"""
    env = _make_env()
    template = env.get_template(TEMPLATE_NAME)
    consumer_diff_command = "consumer-run-mutate-diff-configured"
    context = _make_consumer_config(
        mutate_command="consumer-run-mutate-configured",
        mutate_diff_command=consumer_diff_command,
    )

    rendered = template.render(context)

    assert consumer_diff_command in rendered, (
        f"Rendered mt-session.md.j2 does not contain consumer's mutate_diff command "
        f"'{consumer_diff_command}' — {{ 'mutate_diff' | cmd }} filter not resolving consumer config"
    )
    assert "{{ 'mutate_diff' | cmd }}" not in rendered, (
        "Rendered output still contains raw Jinja2 expression '{{ \\'mutate_diff\\' | cmd }}' — "
        "template not rendering cmd filter correctly"
    )


def test_rendering_raises_key_error_when_mutate_absent():
    """Rendering mt-session.md.j2 raises `KeyError` when `mutate` absent from consumer config. (T4.3, B11)

    `_cmd_filter` raises KeyError when a command key is absent from config — intentional
    fail-fast behaviour so consumers discover missing commands at generation time.
    """
    env = _make_env()
    template = env.get_template(TEMPLATE_NAME)
    context = {
        "commands": {
            "lint": {
                "command": "ruff check .",
                "description": "Run linter",
                "category": "lint",
            }
        }
    }

    with pytest.raises(KeyError) as exc_info:
        template.render(context)

    assert "mutate" in str(
        exc_info.value
    ), f"KeyError message does not contain 'mutate': {exc_info.value!r}"
