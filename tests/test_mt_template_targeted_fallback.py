"""Tests for mt.md.j2 graceful fallback when `mutate_targeted` is absent.

Reproduces and guards the generation bug where enabling `hasMutationTesting`
on a config without a `mutate_targeted` command crashed rendering with
`KeyError: "Command 'mutate_targeted' not found in config"`.

`mutate_targeted` is supplied by rec-1 for the Stryker (TS/JS) family only.
When absent, `mt.md.j2` must resolve path-filter scope to the full `mutate`
command rather than raising.
"""

from jinja2 import Environment, FileSystemLoader, StrictUndefined

from scripts.filters import _cmd_filter
from scripts.paths import TEMPLATE_DIR

TEMPLATE_NAME = "agents/mt.md.j2"


def _make_env() -> Environment:
    """Create a Jinja2 environment with the cmd filter registered."""
    env = Environment(
        loader=FileSystemLoader(str(TEMPLATE_DIR)),
        undefined=StrictUndefined,
    )
    env.filters["cmd"] = _cmd_filter
    return env


def _command(value: str, description: str) -> dict:
    """Build a single command config entry."""
    return {"command": value, "description": description, "category": "test"}


def test_renders_without_targeted_command_falls_back_to_full_mutate():
    """mt.md.j2 renders without `mutate_targeted`, falling back to the full mutate command."""
    env = _make_env()
    template = env.get_template(TEMPLATE_NAME)
    context = {
        "commands": {
            "mutate": _command("FULL-MUTATE-CMD", "Run mutation tests"),
            "mutate_diff": _command("DIFF-MUTATE-CMD", "Run mutation tests on changed files"),
        }
    }

    rendered = template.render(context)

    # Path-filter scope sites must resolve to the full mutate command + path arg
    assert 'FULL-MUTATE-CMD -- "<paths>"' in rendered, (
        "Path-filter scope did not fall back to the full mutate command when "
        "mutate_targeted is absent"
    )
    # No unresolved targeted reference should remain in the output
    assert "mutate_targeted" not in rendered, (
        "Rendered output still references 'mutate_targeted' which the consumer "
        "config does not define"
    )


def test_renders_targeted_command_when_present():
    """mt.md.j2 renders the consumer's `mutate_targeted` command when it is defined."""
    env = _make_env()
    template = env.get_template(TEMPLATE_NAME)
    context = {
        "commands": {
            "mutate": _command("FULL-MUTATE-CMD", "Run mutation tests"),
            "mutate_diff": _command("DIFF-MUTATE-CMD", "Run mutation tests on changed files"),
            "mutate_targeted": _command("TARGETED-CMD", "Run mutation tests on supplied paths"),
        }
    }

    rendered = template.render(context)

    assert 'TARGETED-CMD -- "<paths>"' in rendered, (
        "Path-filter scope did not resolve to the consumer's mutate_targeted command"
    )
