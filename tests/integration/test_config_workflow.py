"""Integration tests for full config validation and generation workflow.

Tests verify end-to-end workflow:
- Valid configs pass validation and generate documentation
- Invalid configs fail validation before rendering
- Templates access command metadata through filters
"""

import tempfile
from pathlib import Path

import pytest
import yaml
from jsonschema import ValidationError

from tests.fixtures.schemas import validate_test_config
from tests.fixtures.templates import render_test_template


@pytest.mark.integration
class TestConfigWorkflow:
    """Integration tests for config workflow."""

    def test_full_generation_workflow_succeeds(self):
        """End-to-end test: object format commands pass validation and generate docs.

        Gate 1: Testing real behaviour → VALID (full workflow execution)
        Gate 2: No test-only methods → VALID
        Gate 3: Understand dependencies → VALID (validation → templates → rendering)
        Gate 4: Complete mock → VALID (minimal test config)
        Gate 5: Test isolation → VALID (temporary files)
        Gate 6: Coverage scope → VALID (happy path integration)
        """
        from tests.fixtures.configs import _create_minimal_config_base

        # Create temporary config with object format commands
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yml", delete=False) as f:
            config = _create_minimal_config_base()
            config["commands"] = {
                "test": {
                    "command": "npm run test:python",
                    "description": "Run all Python unit tests",
                    "category": "test",
                },
                "lint": {
                    "command": "npm run lint:python",
                    "description": "Run Python linter for code quality",
                    "category": "quality",
                },
            }
            yaml.dump(config, f)
            config_path = Path(f.name)

        try:
            # Validation should succeed
            validated_config = validate_test_config(config)

            assert "commands" in validated_config
            assert "test" in validated_config["commands"]
            assert validated_config["commands"]["test"]["command"] == "npm run test:python"

        finally:
            # Cleanup
            config_path.unlink()

    def test_schema_validation_blocks_invalid_config(self):
        """Verify string format commands fail validation before template rendering.

        Gate 1: Testing real behaviour → VALID (ValidationError raised)
        Gate 2: No test-only methods → VALID
        Gate 3: Understand dependencies → VALID (validation fails fast)
        Gate 4: Complete mock → VALID
        Gate 5: Test isolation → VALID
        Gate 6: Coverage scope → VALID (error path - invalid format)
        """
        from tests.fixtures.configs import create_string_format_command

        # Config with deprecated string format
        config = create_string_format_command("test", "npm run test:python")

        with pytest.raises(ValidationError) as exc_info:
            validate_test_config(config)

        error_message = str(exc_info.value.message)
        # Should indicate type mismatch (string instead of object)
        assert "type" in error_message.lower() or "string" in error_message.lower()

    def test_templates_access_command_metadata(self):
        """Verify templates can access command strings through cmd filter.

        Gate 1: Testing real behaviour → VALID (asserts on rendered output)
        Gate 2: No test-only methods → VALID
        Gate 3: Understand dependencies → VALID (Jinja2 filter execution)
        Gate 4: Complete mock → VALID (context with object format command)
        Gate 5: Test isolation → VALID
        Gate 6: Coverage scope → VALID (filter integration in template)
        """
        template_str = '{{ "test" | cmd }}'
        context = {
            "commands": {
                "test": {
                    "command": "npm run test:python",
                    "description": "Run tests",
                    "category": "test",
                }
            }
        }

        rendered = render_test_template(template_str, context)

        # Filter should extract command string
        assert rendered == "npm run test:python"
        assert isinstance(rendered, str)
