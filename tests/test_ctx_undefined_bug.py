"""Test for ctx undefined bug in macros/templates.

This test reproduces the bug where templates reference 'ctx' directly
instead of using 'this' which is the SmartContext instance passed to templates.
"""

import pytest
from jinja2 import UndefinedError

from scripts.generate_docs import render_template, setup_jinja_environment


class TestCtxUndefinedBug:
    """Test suite for ctx undefined error in template rendering."""

    def test_template_using_ctx_directly_raises_undefined_error(self, tmp_path):
        """
        Template referencing ctx directly (not via parameter) raises UndefinedError.

        This reproduces the bug where templates use {{ ctx.cmd('lint') }} instead of
        {{ this.cmd('lint') }}, where 'this' is the SmartContext instance.

        Gate 1: Asserting on real behaviour (exception raised) → VALID
        Gate 2: No test-only methods needed → VALID
        Gate 3: No mocks needed (pure template rendering) → VALID
        Gate 4: N/A (no mocks) → VALID
        Gate 5: Test fails for correct reason (ctx undefined) → VALID
        """
        # Arrange: Create template that references ctx directly (bug)
        template_dir = tmp_path / "templates"
        template_dir.mkdir()
        template_path = template_dir / "test.md.j2"
        template_path.write_text(
            """# Test Template
Command: {{ ctx.cmd('lint') }}
"""
        )

        config = {
            "commands": {
                "lint": {
                    "command": "npm run lint",
                    "description": "Run linter",
                    "category": "quality",
                }
            },
            "repo": {"language": {"typescript": "all"}},
        }
        env = setup_jinja_environment(template_dir)

        # Act & Assert: Rendering raises UndefinedError for 'ctx'
        with pytest.raises(UndefinedError) as exc_info:
            render_template(env, "test.md.j2", config)

        error_message = str(exc_info.value)
        assert "'ctx' is undefined" in error_message

    def test_template_using_this_renders_successfully(self, tmp_path):
        """
        Template referencing 'this' (SmartContext) renders successfully.

        This demonstrates the correct approach - using 'this' instead of 'ctx'.

        Gate 1: Asserting on real behaviour (successful render) → VALID
        Gate 2: No test-only methods → VALID
        Gate 3: No mocks → VALID
        Gate 4: N/A → VALID
        Gate 5: Happy path validation → VALID
        """
        # Import SmartContext and filter implementations
        from typing import Any

        from scripts.filters import SmartContext, _cmd_impl

        # Arrange: Create template that correctly uses 'this'
        template_dir = tmp_path / "templates"
        template_dir.mkdir()
        template_path = template_dir / "test.md.j2"
        template_path.write_text(
            """# Test Template
Command: {{ this.cmd('lint') }}
"""
        )

        config: dict[str, Any] = {
            "commands": {
                "lint": {
                    "command": "npm run lint",
                    "description": "Run linter",
                    "category": "quality",
                }
            },
            "repo": {"language": {"typescript": "all"}},
        }

        # Inject SmartContext as 'this' (mimics what generate_docs.py does)
        filter_implementations = {"cmd": _cmd_impl}
        config["this"] = SmartContext(config, filter_implementations)

        env = setup_jinja_environment(template_dir)

        # Act: Render template
        result = render_template(env, "test.md.j2", config)

        # Assert: Template renders successfully with command
        assert "Command: npm run lint" in result
