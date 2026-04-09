"""Test schema validation for deprecating string format commands.

Tests verify that JSON schema correctly:
- Rejects deprecated string format commands
- Requires all three fields (command, description, category) in object format
- Enforces minLength: 1 for all fields
- Rejects additional properties
- Accepts valid object format commands
"""

import pytest
from jsonschema import ValidationError

from tests.fixtures.configs import (
    create_incomplete_command,
    create_string_format_command,
    create_valid_command,
)
from tests.fixtures.schemas import validate_test_config


class TestSchemaValidation:
    """Schema validation tests for command format deprecation."""

    def test_rejects_string_format_commands(self):
        """Schema validation must reject configs using deprecated string format.

        Gate 1: Testing real behaviour → VALID (asserts on ValidationError, not mock)
        Gate 2: No test-only methods → VALID (no production code changes)
        Gate 3: Understand dependencies → VALID (jsonschema validates configs)
        Gate 4: Complete mock → VALID (using real schema, no mocks)
        Gate 5: Test isolation → VALID (fresh config dict each test)
        Gate 6: Coverage scope → VALID (error path for string format rejection)
        """
        config = create_string_format_command("test", "npm run test:python")

        with pytest.raises(ValidationError) as exc_info:
            validate_test_config(config)

        error_message = str(exc_info.value.message)
        assert (
            "'test' should be object, not string" in error_message
            or "type" in error_message.lower()
        )

    def test_rejects_missing_command_field(self):
        """Object format commands must include required 'command' field.

        Gate 1: Testing real behaviour → VALID (asserts on ValidationError)
        Gate 2: No test-only methods → VALID
        Gate 3: Understand dependencies → VALID (jsonschema required field validation)
        Gate 4: Complete mock → VALID (real schema)
        Gate 5: Test isolation → VALID (fresh config)
        Gate 6: Coverage scope → VALID (error path for missing field)
        """
        config = create_incomplete_command("test", description="Run tests", category="test")

        with pytest.raises(ValidationError) as exc_info:
            validate_test_config(config)

        error_message = str(exc_info.value.message)
        assert "'command' is a required property" in error_message

    def test_rejects_missing_description_field(self):
        """Object format commands must include required 'description' field.

        Gate 1: Testing real behaviour → VALID
        Gate 2: No test-only methods → VALID
        Gate 3: Understand dependencies → VALID
        Gate 4: Complete mock → VALID
        Gate 5: Test isolation → VALID
        Gate 6: Coverage scope → VALID (error path)
        """
        config = create_incomplete_command("test", command="npm run test:python", category="test")

        with pytest.raises(ValidationError) as exc_info:
            validate_test_config(config)

        error_message = str(exc_info.value.message)
        assert "'description' is a required property" in error_message

    def test_rejects_missing_category_field(self):
        """Object format commands must include required 'category' field.

        Gate 1: Testing real behaviour → VALID
        Gate 2: No test-only methods → VALID
        Gate 3: Understand dependencies → VALID
        Gate 4: Complete mock → VALID
        Gate 5: Test isolation → VALID
        Gate 6: Coverage scope → VALID (error path)
        """
        config = create_incomplete_command(
            "test", command="npm run test:python", description="Run tests"
        )

        with pytest.raises(ValidationError) as exc_info:
            validate_test_config(config)

        error_message = str(exc_info.value.message)
        assert "'category' is a required property" in error_message

    def test_rejects_empty_command_string(self):
        """The 'command' field must contain at least one character.

        Gate 1: Testing real behaviour → VALID
        Gate 2: No test-only methods → VALID
        Gate 3: Understand dependencies → VALID (jsonschema minLength validation)
        Gate 4: Complete mock → VALID
        Gate 5: Test isolation → VALID
        Gate 6: Coverage scope → VALID (boundary condition - empty string)
        """
        config = create_valid_command("test", "", "Run tests", "test")

        with pytest.raises(ValidationError) as exc_info:
            validate_test_config(config)

        error_message = str(exc_info.value.message)
        assert "non-empty" in error_message or "too short" in error_message.lower()

    def test_rejects_empty_description_string(self):
        """The 'description' field must contain at least one character.

        Gate 1: Testing real behaviour → VALID
        Gate 2: No test-only methods → VALID
        Gate 3: Understand dependencies → VALID
        Gate 4: Complete mock → VALID
        Gate 5: Test isolation → VALID
        Gate 6: Coverage scope → VALID (boundary condition)
        """
        config = create_valid_command("test", "npm run test:python", "", "test")

        with pytest.raises(ValidationError) as exc_info:
            validate_test_config(config)

        error_message = str(exc_info.value.message)
        assert "non-empty" in error_message or "too short" in error_message.lower()

    def test_rejects_empty_category_string(self):
        """The 'category' field must contain at least one character.

        Gate 1: Testing real behaviour → VALID
        Gate 2: No test-only methods → VALID
        Gate 3: Understand dependencies → VALID
        Gate 4: Complete mock → VALID
        Gate 5: Test isolation → VALID
        Gate 6: Coverage scope → VALID (boundary condition)
        """
        config = create_valid_command("test", "npm run test:python", "Run tests", "")

        with pytest.raises(ValidationError) as exc_info:
            validate_test_config(config)

        error_message = str(exc_info.value.message)
        assert "non-empty" in error_message or "too short" in error_message.lower()

    def test_rejects_additional_properties(self):
        """Command objects must contain only the three defined fields.

        Gate 1: Testing real behaviour → VALID
        Gate 2: No test-only methods → VALID
        Gate 3: Understand dependencies → VALID (jsonschema additionalProperties)
        Gate 4: Complete mock → VALID
        Gate 5: Test isolation → VALID
        Gate 6: Coverage scope → VALID (error path for extra fields)
        """
        from tests.fixtures.configs import _create_minimal_config_base

        config = _create_minimal_config_base()
        config["commands"] = {
            "test": {
                "command": "npm run test:python",
                "description": "Run tests",
                "category": "test",
                "extra": "unexpected value",
            }
        }

        with pytest.raises(ValidationError) as exc_info:
            validate_test_config(config)

        error_message = str(exc_info.value.message)
        assert "additional" in error_message.lower() or "extra" in error_message

    def test_accepts_valid_object_format(self):
        """Well-formed command objects with all three required fields must pass.

        Gate 1: Testing real behaviour → VALID (asserts on successful validation)
        Gate 2: No test-only methods → VALID
        Gate 3: Understand dependencies → VALID (jsonschema returns validated dict)
        Gate 4: Complete mock → VALID
        Gate 5: Test isolation → VALID
        Gate 6: Coverage scope → VALID (happy path)
        """
        config = create_valid_command(
            "test", "npm run test:python", "Run all Python unit tests", "test"
        )

        # Should not raise exception
        result = validate_test_config(config)

        # Should return the config unchanged
        assert result == config
        assert "commands" in result
        assert "test" in result["commands"]

    def test_accepts_special_characters_in_description(self):
        """Description fields must support quotes, apostrophes, and symbols.

        Gate 1: Testing real behaviour → VALID
        Gate 2: No test-only methods → VALID
        Gate 3: Understand dependencies → VALID (string validation)
        Gate 4: Complete mock → VALID
        Gate 5: Test isolation → VALID
        Gate 6: Coverage scope → VALID (boundary - special characters)
        """
        config = create_valid_command(
            "test",
            "npm run test:python",
            'Run tests with "quotes", apostrophe\'s, and symbols: @#$%',
            "test",
        )

        result = validate_test_config(config)

        # Special characters should be preserved
        assert result["commands"]["test"]["description"] == (
            'Run tests with "quotes", apostrophe\'s, and symbols: @#$%'
        )

    def test_accepts_long_descriptions(self):
        """Description fields must support detailed documentation without length limits.

        Gate 1: Testing real behaviour → VALID
        Gate 2: No test-only methods → VALID
        Gate 3: Understand dependencies → VALID (no maxLength in schema)
        Gate 4: Complete mock → VALID
        Gate 5: Test isolation → VALID
        Gate 6: Coverage scope → VALID (boundary - long strings)
        """
        long_description = "A" * 300
        config = create_valid_command("test", "npm run test:python", long_description, "test")

        result = validate_test_config(config)

        # Full description should be preserved
        assert result["commands"]["test"]["description"] == long_description
        assert len(result["commands"]["test"]["description"]) == 300
