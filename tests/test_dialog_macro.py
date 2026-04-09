"""Test dialog enforcement macro."""

from typing import Any

from scripts.generate_docs import setup_jinja_environment
from scripts.paths import TEMPLATE_DIR


def test_dialog_macro_enforces_wait_pattern():
    """Dialog macro outputs imperative commands forcing agents to wait for validation."""
    env = setup_jinja_environment(TEMPLATE_DIR)

    template_string = """
{%- from 'macros.j2' import present_for_validation with context -%}
{{ present_for_validation(
    pre_validation="Test content to present",
    post_validation="Proceed to next step"
) }}
"""

    config: dict[str, Any] = {}
    template = env.from_string(template_string)
    result = template.render(config)

    # Macro should output imperative wait command
    assert "WAIT for human validation" in result
    assert "Test content to present" in result

    # Should include approval/rejection flow
    assert "IF human approves" in result
    assert "IF human requests changes" in result


def test_dialog_macro_with_concerns_outputs_concerns_block():
    """Dialog macro outputs a Concerns block when concerns parameter provided."""
    env = setup_jinja_environment(TEMPLATE_DIR)

    template_string = """
{%- from 'macros.j2' import present_for_validation with context -%}
{{ present_for_validation(
    pre_validation="Test content to present",
    post_validation="Proceed to next step",
    concerns="This approach increases coupling between modules."
) }}
"""

    config: dict[str, Any] = {}
    template = env.from_string(template_string)
    result = template.render(config)

    assert "Concerns" in result
    assert "This approach increases coupling between modules." in result
    # Concerns block appears before the approval prompt
    concerns_pos = result.index("Concerns")
    approval_pos = result.index("IF human approves")
    assert concerns_pos < approval_pos


def test_dialog_macro_without_concerns_matches_original_output():
    """Dialog macro output is identical to current behaviour when concerns omitted."""
    env = setup_jinja_environment(TEMPLATE_DIR)

    template_with_concerns = """
{%- from 'macros.j2' import present_for_validation with context -%}
{{ present_for_validation(
    pre_validation="Test content",
    post_validation="Next step"
) }}
"""

    template_without_concerns = """
{%- from 'macros.j2' import present_for_validation with context -%}
{{ present_for_validation(
    pre_validation="Test content",
    post_validation="Next step",
    concerns=none
) }}
"""

    config: dict[str, Any] = {}
    result_default = env.from_string(template_with_concerns).render(config)
    result_explicit_none = env.from_string(template_without_concerns).render(config)

    assert result_default == result_explicit_none
    assert "Concerns" not in result_default
