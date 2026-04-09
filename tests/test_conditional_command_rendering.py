"""
Test for conditional command rendering in Jinja2 templates.

Reproduces bug where {% if commands.test_coverage is defined %} doesn't prevent
{{ "test_coverage" | cmd }} from raising KeyError when command is missing.

Gate 1: Asserts on real behaviour (template rendering output) → VALID
Gate 2: No test-only methods needed → VALID
Gate 3: Dependencies understood (Jinja2 template engine) → VALID
Gate 4: No mocks needed (real Jinja2 environment) → VALID
Gate 5: Test fails for correct reason (KeyError when command missing) → VALID
Gate 6: Happy path + error path covered → VALID
"""

from jinja2 import DictLoader, Environment, StrictUndefined

from scripts.filters import _cmd_filter


def test_conditional_command_with_missing_command_should_not_error():
    """
    Reproduce bug: {% if commands.test_coverage is defined %} followed by
    {{ "test_coverage" | cmd }} raises KeyError when test_coverage missing.

    Expected: Template should render without error, omitting the conditional block.
    Actual: KeyError raised from _cmd_filter even though condition checks 'is defined'.

    Root cause hypothesis: Jinja2's 'is defined' test with dict access might not work
    as expected, or filter is being evaluated before condition check.
    """
    # Given: Template with conditional command reference (mirrors bugs.md.j2:75-91)
    template_str = """
{%- if commands.test_coverage is defined %}
### Coverage Section
{{ "test_coverage" | cmd }}
{%- endif %}
""".strip()

    # Given: Context WITHOUT test_coverage command
    context = {
        "commands": {
            "test": {"command": "pytest"},
            "lint": {"command": "ruff check ."},
            "typecheck": {"command": "mypy ."},
            # test_coverage intentionally missing
        },
        "repo": {"language": {"python": "all"}},
    }

    # Given: Jinja2 environment with cmd filter AND StrictUndefined (like generate_docs.py)
    env = Environment(loader=DictLoader({"test": template_str}), undefined=StrictUndefined)
    env.filters["cmd"] = _cmd_filter

    # When: Render template
    template = env.get_template("test")
    result = template.render(context)

    # Then: Should render without error (conditional block omitted)
    # FIX: After enrichment loads variants section, test_coverage won't be missing.
    # But for this test, we explicitly omit it to verify 'is defined' works correctly.
    assert result == ""


def test_conditional_command_with_present_command_renders_correctly():
    """
    Verify conditional works correctly when command IS present.

    This is the happy path - ensures our fix doesn't break working functionality.
    """
    # Given: Template with conditional command reference
    template_str = """
{%- if commands.test_coverage is defined %}
### Coverage Section
{{ "test_coverage" | cmd }}
{%- endif %}
""".strip()

    # Given: Context WITH test_coverage command
    context = {
        "commands": {
            "test": {"command": "pytest"},
            "test_coverage": {"command": "pytest --cov"},
        },
        "repo": {"language": {"python": "all"}},
    }

    # Given: Jinja2 environment with cmd filter AND StrictUndefined
    env = Environment(loader=DictLoader({"test": template_str}), undefined=StrictUndefined)
    env.filters["cmd"] = _cmd_filter

    # When: Render template
    template = env.get_template("test")
    result = template.render(context)

    # Then: Should render the conditional block with command
    assert "### Coverage Section" in result
    assert "pytest --cov" in result
