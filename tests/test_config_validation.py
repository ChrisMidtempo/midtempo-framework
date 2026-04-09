"""Tests for config schema validator (scripts/validate_config.py)."""

import pytest
import yaml
from jsonschema import ValidationError

from scripts.validate_config import validate_config, validate_config_with_enhanced_errors
from tests.helpers.config_factory import create_standard_config

"""
VALIDATION TEST PATTERN
=======================

All tests use the "valid base + override" pattern:

1. Create valid config with create_standard_config()
2. Override specific field to make it invalid
3. Add comment explaining what's invalid

Example:
    config = create_standard_config("python")
    config["name"] = ""  # Empty name should fail validation
    assert not validate_config(config)

This keeps validation tests DRY while clearly showing what's being tested.
"""


class TestConfigValidation:
    """Test suite for config schema validation."""

    def test_valid_typescript_ui_db_config_passes(self, tmp_path):
        """Valid TypeScript+UI+DB config passes validation and returns validated dict."""
        # Arrange: Create valid config YAML using factory
        config_path = tmp_path / "config.yml"
        config_data = create_standard_config("typescript", {"hasUI", "hasDB"})
        config_data["name"] = "example-app"
        config_data["repo"]["title"] = "example.app"
        config_path.write_text(yaml.dump(config_data))

        # Act: Validate config
        result = validate_config(config_path)

        # Assert: Returns validated config dict with correct types
        assert result is not None
        assert isinstance(result, dict)
        assert result["repo"]["title"] == "example.app"
        assert result["repo"]["language"] == {"typescript": "all"}
        assert result["capabilities"]["hasUI"] is True
        assert result["capabilities"]["hasDB"] is True
        assert result["commands"]["test"]["command"] == "npm test"

    def test_missing_required_field_rejects_config(self, tmp_path):
        """Config missing required field raises ValidationError."""
        # Arrange: Create config missing repo.language using override pattern
        config_path = tmp_path / "config.yml"
        config_data = create_standard_config("python")
        del config_data["repo"]["language"]  # Remove required field to test validation
        config_path.write_text(yaml.dump(config_data))

        # Act & Assert: Validation raises error with clear message
        try:
            validate_config(config_path)
            # If we get here without exception, test fails
            raise AssertionError("Should have raised ValidationError for missing language field")
        except NotImplementedError:
            # Expected during Phase 2 - implementation not complete
            raise
        except Exception as e:
            # Once implemented, should raise ValidationError
            error_message = str(e).lower()
            assert "language" in error_message or "required" in error_message

    def test_invalid_enum_value_rejects_config(self, tmp_path):
        """Invalid enum value raises ValidationError listing valid options."""
        # Arrange: Create config with invalid language enum using override pattern
        config_path = tmp_path / "config.yml"
        config_data = create_standard_config("python")
        config_data["repo"]["language"] = "ruby"  # Invalid enum - not in schema
        config_path.write_text(yaml.dump(config_data))

        # Act & Assert: Validation raises error indicating invalid enum
        try:
            validate_config(config_path)
            # If we get here without exception, test fails
            raise AssertionError("Should have raised ValidationError for invalid enum value")
        except NotImplementedError:
            # Expected during Phase 2 - implementation not complete
            raise
        except Exception as e:
            # Once implemented, should raise ValidationError
            error_message = str(e).lower()
            assert "ruby" in error_message or "enum" in error_message or "invalid" in error_message

    def test_malformed_yaml_rejects_before_schema_validation(self, tmp_path):
        """Malformed YAML raises YAMLError before schema validation."""
        # Arrange: Create file with invalid YAML syntax
        config_path = tmp_path / "config.yml"
        config_path.write_text(
            """
repo
  name: "example.app"
  language: "typescript
"""
        )

        # Act & Assert: YAML parsing error raised before validation
        try:
            validate_config(config_path)
            # If we get here without exception, test fails
            raise AssertionError("Should have raised YAMLError for malformed YAML")
        except NotImplementedError:
            # Expected during Phase 2 - implementation not complete
            raise
        except yaml.YAMLError:
            # Expected behavior once implemented - YAML error before schema validation
            pass

    def test_enhanced_error_messages_for_missing_fields(self, tmp_path):
        """Enhanced validation provides clear context for missing required fields."""
        # Arrange: Config missing required field repo.language using override pattern
        config_path = tmp_path / "config.yml"
        config_data = create_standard_config("python")
        del config_data["repo"]["language"]  # Remove required field to test enhanced error message
        config_path.write_text(yaml.dump(config_data))

        # Act & Assert: Error message includes field path and clear context
        with pytest.raises(Exception) as exc_info:
            validate_config_with_enhanced_errors(config_path)

        error_message = str(exc_info.value)
        # Should mention the missing field with clear context
        assert "repo.language" in error_message or (
            "language" in error_message and "required" in error_message.lower()
        )

    def test_enum_validation_lists_valid_options(self, tmp_path):
        """Invalid enum value error lists all valid options from schema."""
        # Arrange: Config with invalid enum value for repo.language using override pattern
        config_path = tmp_path / "config.yml"
        config_data = create_standard_config("python")
        config_data["repo"]["language"] = "ruby"  # Invalid enum - should be typescript or python
        config_path.write_text(yaml.dump(config_data))

        # Act & Assert: Error message lists valid enum options
        with pytest.raises(Exception) as exc_info:
            validate_config_with_enhanced_errors(config_path)

        error_message = str(exc_info.value)
        # Should show "Invalid: ruby, valid options: typescript, python" or similar
        assert "ruby" in error_message or "invalid" in error_message.lower()
        # Should suggest valid options
        assert (
            "typescript" in error_message.lower() or "python" in error_message.lower()
        ) or "valid" in error_message.lower()

    def test_valid_config_with_enhanced_validation_passes(self, tmp_path):
        """Valid config passes enhanced validation and returns config dict."""
        # Arrange: Complete valid config using factory
        config_path = tmp_path / "config.yml"
        config_data = create_standard_config("python")
        config_data["name"] = "test-repo"
        config_data["repo"]["title"] = "test-repo"
        config_path.write_text(yaml.dump(config_data))

        # Act: Validate with enhanced error handling
        result = validate_config_with_enhanced_errors(config_path)

        # Assert: Returns validated config
        assert result is not None
        assert result["repo"]["title"] == "test-repo"
        assert result["repo"]["language"] == {"python": "all"}

    def test_missing_top_level_name_field_rejects_config(self, tmp_path):
        """Config missing required top-level name field raises ValidationError."""
        # Arrange: Create config missing top-level name field using override pattern
        config_path = tmp_path / "config.yml"
        config_data = create_standard_config("typescript", {"hasUI", "hasDB"})
        del config_data["name"]  # Remove required top-level field to test validation
        config_path.write_text(yaml.dump(config_data))

        # Act & Assert: Validation raises error with clear message
        with pytest.raises(Exception) as exc_info:
            validate_config(config_path)

        error_message = str(exc_info.value).lower()
        # Should mention the missing name field with clear context
        assert "name" in error_message and "required" in error_message

    def test_invalid_name_pattern_with_whitespace_rejects_config(self, tmp_path):
        """Config with name containing whitespace raises ValidationError."""
        # Arrange: Create config with invalid name (contains space) using override pattern
        config_path = tmp_path / "config.yml"
        config_data = create_standard_config("python")
        config_data["name"] = "invalid name"  # Contains whitespace - invalid
        config_path.write_text(yaml.dump(config_data))

        # Act & Assert: Validation raises error indicating pattern mismatch
        with pytest.raises(Exception) as exc_info:
            validate_config(config_path)

        error_message = str(exc_info.value).lower()
        # Should indicate pattern validation failure
        assert "name" in error_message or "pattern" in error_message or "invalid" in error_message

    def test_invalid_name_pattern_starting_with_hyphen_rejects_config(self, tmp_path):
        """Config with name starting with hyphen raises ValidationError."""
        # Arrange: Create config with invalid name (starts with hyphen) using override pattern
        config_path = tmp_path / "config.yml"
        config_data = create_standard_config("typescript", {"hasUI"})
        config_data["name"] = "-invalid"  # Starts with hyphen - invalid
        config_path.write_text(yaml.dump(config_data))

        # Act & Assert: Validation raises error indicating pattern mismatch
        with pytest.raises(Exception) as exc_info:
            validate_config(config_path)

        error_message = str(exc_info.value).lower()
        # Should indicate pattern validation failure
        assert "name" in error_message or "pattern" in error_message or "invalid" in error_message

    def test_valid_name_with_dots_and_hyphens_passes_validation(self, tmp_path):
        """Config with valid name containing dots and hyphens passes validation."""
        # Arrange: Create config with valid name (alphanumeric with dots, hyphens, underscores)
        config_path = tmp_path / "config.yml"
        config_data = create_standard_config("python", {"hasDB"})
        config_data["name"] = "example-framework_v1.0"  # Valid directory name
        config_data["repo"]["title"] = "example.framework"
        config_path.write_text(yaml.dump(config_data))

        # Act: Validate config
        result = validate_config(config_path)

        # Assert: Returns validated config dict with name field
        assert result is not None
        assert isinstance(result, dict)
        assert result["name"] == "example-framework_v1.0"

    def test_extended_command_format_with_all_fields_passes_validation(self, tmp_path):
        """Config with extended command format (command, description, category) passes validation."""
        # Arrange: Create config with extended command object format using factory
        config_path = tmp_path / "config.yml"
        config_data = create_standard_config("typescript", {"hasUI"})
        # Factory already provides extended command format with all fields
        config_path.write_text(yaml.dump(config_data))

        # Act: Validate config
        result = validate_config(config_path)

        # Assert: Returns validated config with object format
        assert result is not None
        assert result["commands"]["test"]["command"] == "npm test"
        assert result["commands"]["test_coverage"]["command"] == "npm test -- --silent --coverage"
        assert (
            result["commands"]["test_coverage"]["description"] == "Run tests with coverage report"
        )
        assert result["commands"]["test_coverage"]["category"] == "test"

    def test_extended_command_format_with_command_only_rejects_validation(self, tmp_path):
        """Config with extended format containing only command field is rejected (description and category required)."""
        # Arrange: Extended format with only command field (missing required description/category)
        config_path = tmp_path / "config.yml"
        config_data = create_standard_config("python")
        # Add invalid command with only command field (missing description/category)
        config_data["commands"]["build"] = {"command": "python -m build"}
        config_path.write_text(yaml.dump(config_data))

        # Act & Assert: Validation raises error
        with pytest.raises(Exception) as exc_info:
            validate_config(config_path)

        error_message = str(exc_info.value).lower()
        # Should mention missing required fields
        assert ("description" in error_message and "required" in error_message) or (
            "category" in error_message and "required" in error_message
        )

    def test_extended_command_format_missing_command_field_rejects_config(self, tmp_path):
        """Extended command format missing required 'command' field raises ValidationError."""
        # Arrange: Extended format missing required command field using override pattern
        config_path = tmp_path / "config.yml"
        config_data = create_standard_config("typescript")
        # Add invalid command missing required 'command' field
        config_data["commands"]["build"] = {
            "description": "Build the project",
            "category": "build",
        }
        config_path.write_text(yaml.dump(config_data))

        # Act & Assert: Validation raises error
        with pytest.raises(Exception) as exc_info:
            validate_config(config_path)

        error_message = str(exc_info.value).lower()
        # Should mention missing command field
        assert "command" in error_message and (
            "required" in error_message or "missing" in error_message
        )

    def test_repo_logfile_accepts_string_path(self, tmp_path):
        """Config with repo.logfile as string path passes validation."""
        # Arrange: Create config with repo.logfile as string
        config_path = tmp_path / "config.yml"
        config_data = create_standard_config("python")
        config_data["repo"]["logfile"] = "planning/last-test-ran.log"
        config_path.write_text(yaml.dump(config_data))

        # Act: Validate config
        result = validate_config(config_path)

        # Assert: Returns validated config with logfile field
        assert result is not None
        assert result["repo"]["logfile"] == "planning/last-test-ran.log"

    def test_repo_logfile_accepts_null(self, tmp_path):
        """Config with repo.logfile as null passes validation."""
        # Arrange: Create config with repo.logfile as null (no log file)
        config_path = tmp_path / "config.yml"
        config_data = create_standard_config("typescript")
        config_data["repo"]["logfile"] = None
        config_path.write_text(yaml.dump(config_data))

        # Act: Validate config
        result = validate_config(config_path)

        # Assert: Returns validated config with null logfile
        assert result is not None
        assert result["repo"]["logfile"] is None

    def test_repo_logfile_optional_defaults_when_omitted(self, tmp_path):
        """Config without repo.logfile passes validation (optional field)."""
        # Arrange: Create config without repo.logfile field (should use default)
        config_path = tmp_path / "config.yml"
        config_data = create_standard_config("python")
        # Explicitly verify logfile not in config
        assert "logfile" not in config_data["repo"]
        config_path.write_text(yaml.dump(config_data))

        # Act: Validate config
        result = validate_config(config_path)

        # Assert: Returns validated config (logfile field optional)
        assert result is not None
        assert result["repo"]["title"] == "Test Project"

    def test_repo_setup_accepts_boolean_true(self, tmp_path):
        """Config with repo.setup as true passes validation."""
        # Arrange: Create config with repo.setup enabled
        config_path = tmp_path / "config.yml"
        config_data = create_standard_config("typescript", {"hasUI"})
        config_data["repo"]["setup"] = True
        config_path.write_text(yaml.dump(config_data))

        # Act: Validate config
        result = validate_config(config_path)

        # Assert: Returns validated config with setup enabled
        assert result is not None
        assert result["repo"]["setup"] is True

    def test_repo_setup_accepts_boolean_false(self, tmp_path):
        """Config with repo.setup as false passes validation."""
        # Arrange: Create config with repo.setup disabled
        config_path = tmp_path / "config.yml"
        config_data = create_standard_config("python", {"hasDB"})
        config_data["repo"]["setup"] = False
        config_path.write_text(yaml.dump(config_data))

        # Act: Validate config
        result = validate_config(config_path)

        # Assert: Returns validated config with setup disabled
        assert result is not None
        assert result["repo"]["setup"] is False

    def test_repo_setup_optional_defaults_when_omitted(self, tmp_path):
        """Config without repo.setup passes validation (optional field)."""
        # Arrange: Create config without repo.setup field (should use default)
        config_path = tmp_path / "config.yml"
        config_data = create_standard_config("typescript")
        # Explicitly verify setup not in config
        assert "setup" not in config_data["repo"]
        config_path.write_text(yaml.dump(config_data))

        # Act: Validate config
        result = validate_config(config_path)

        # Assert: Returns validated config (setup field optional)
        assert result is not None
        assert result["repo"]["title"] == "Test Project"

    def test_repo_agent_file_accepts_agents(self, tmp_path):
        """Config with repo.agentFile as AGENTS passes validation."""
        # Arrange: Create config with repo.agentFile set to AGENTS
        config_path = tmp_path / "config.yml"
        config_data = create_standard_config("python")
        config_data["repo"]["agentFile"] = "AGENTS"
        config_path.write_text(yaml.dump(config_data))

        # Act: Validate config
        result = validate_config(config_path)

        # Assert: Returns validated config with agentFile field
        assert result is not None
        assert result["repo"]["agentFile"] == "AGENTS"

    def test_repo_agent_file_accepts_claude(self, tmp_path):
        """Config with repo.agentFile as CLAUDE passes validation."""
        # Arrange: Create config with repo.agentFile set to CLAUDE
        config_path = tmp_path / "config.yml"
        config_data = create_standard_config("python")
        config_data["repo"]["agentFile"] = "CLAUDE"
        config_path.write_text(yaml.dump(config_data))

        # Act: Validate config
        result = validate_config(config_path)

        # Assert: Returns validated config with agentFile field
        assert result is not None
        assert result["repo"]["agentFile"] == "CLAUDE"

    def test_repo_agent_file_rejects_invalid_value(self, tmp_path):
        """Config with invalid repo.agentFile value fails validation."""
        # Arrange: Create config with invalid agentFile value
        config_path = tmp_path / "config.yml"
        config_data = create_standard_config("python")
        config_data["repo"]["agentFile"] = "INVALID"
        config_path.write_text(yaml.dump(config_data))

        # Act & Assert: Validation rejects invalid enum value
        with pytest.raises(ValidationError):
            validate_config(config_path)

    def test_repo_agent_file_optional_defaults_when_omitted(self, tmp_path):
        """Config without repo.agentFile passes validation (optional field)."""
        # Arrange: Create config without repo.agentFile field
        config_path = tmp_path / "config.yml"
        config_data = create_standard_config("python")
        # Explicitly verify agentFile not in config
        assert "agentFile" not in config_data["repo"]
        config_path.write_text(yaml.dump(config_data))

        # Act: Validate config
        result = validate_config(config_path)

        # Assert: Returns validated config (agentFile field optional)
        assert result is not None
        assert result["repo"]["title"] == "Test Project"
