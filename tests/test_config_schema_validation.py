"""Schema validation tests for multi-language mapping format.

IMPORTANT: All validation in this file uses the centralized validate_test_config()
wrapper from tests.fixtures.schemas. This ensures schema validation logic remains
in a single location. When schema location or validation behavior changes, all tests
automatically inherit the updates without modification.
"""

import pytest
from jsonschema import ValidationError

from tests.fixtures.schemas import load_test_schema, validate_test_config
from tests.helpers.config_factory import (
    create_config_with_language,
    create_invalid_scope_config,
    create_valid_config,
)


# Test 1.1: Valid mono-language mapping
def test_valid_mono_language_mapping():
    """Verify config with single language mapping {python: all} passes validation."""
    config = create_config_with_language({"python": "all"})

    # Should not raise ValidationError
    validate_test_config(config)


# Test 1.2: Valid multi-language mapping (2 languages)
def test_valid_multi_language_mapping_two_languages():
    """Verify config with two languages mapping to distinct scopes passes validation."""
    config = create_config_with_language({"python": "backend", "typescript": "frontend"})

    # Should not raise ValidationError
    validate_test_config(config)


# Test 1.3: Valid multi-language mapping (3 languages)
def test_valid_multi_language_mapping_three_languages():
    """Verify schema supports three or more languages with distinct scope identifiers."""
    config = create_config_with_language(
        {"python": "backend", "typescript": "frontend", "rust": "services"}
    )

    # Should not raise ValidationError
    validate_test_config(config)


# Test 1.4: Rejects uppercase in scope name
def test_rejects_uppercase_in_scope():
    """Verify schema rejects scope identifiers containing uppercase characters."""
    config = create_invalid_scope_config("Backend")

    with pytest.raises(ValidationError) as exc_info:
        validate_test_config(config)

    # Error should mention pattern mismatch
    error = exc_info.value
    assert "pattern" in str(error).lower() or "does not match" in str(error).lower()


# Test 1.5: Rejects special characters in scope
def test_rejects_special_characters_in_scope():
    """Verify schema rejects scope identifiers containing special characters."""
    config = create_invalid_scope_config("back@end")

    with pytest.raises(ValidationError) as exc_info:
        validate_test_config(config)

    # Error should indicate pattern validation failure
    error = exc_info.value
    assert "pattern" in str(error).lower() or "does not match" in str(error).lower()


# Test 1.6: Rejects scope too short (1 char)
def test_rejects_scope_too_short():
    """Verify schema enforces minimum length constraint of 2 characters."""
    config = create_invalid_scope_config("a")

    with pytest.raises(ValidationError) as exc_info:
        validate_test_config(config)

    # Error should mention minLength constraint
    error = exc_info.value
    assert "minLength" in str(error) or "too short" in str(error).lower()


# Test 1.7: Rejects scope too long (21+ chars)
def test_rejects_scope_too_long():
    """Verify schema enforces maximum length constraint of 20 characters."""
    # 31 characters - well over the 20 char limit
    config = create_invalid_scope_config("this-is-a-very-long-scope-name")

    with pytest.raises(ValidationError) as exc_info:
        validate_test_config(config)

    # Error should mention maxLength constraint
    error = exc_info.value
    assert "maxLength" in str(error) or "too long" in str(error).lower()


# Test 1.8: Rejects empty language mapping
def test_rejects_empty_language_mapping():
    """Verify schema requires at least one language mapping (rejects empty object)."""
    config = create_config_with_language({})

    with pytest.raises(ValidationError) as exc_info:
        validate_test_config(config)

    # Error should mention minProperties constraint
    error = exc_info.value
    assert "minProperties" in str(error) or "empty" in str(error).lower()


# Test 1.9: Rejects missing language field
def test_rejects_missing_language_field():
    """Verify schema requires repo.language field to be present."""
    config = create_valid_config()
    # Remove language field
    del config["repo"]["language"]

    with pytest.raises(ValidationError) as exc_info:
        validate_test_config(config)

    # Error should indicate language is required
    error = exc_info.value
    assert "required" in str(error).lower() and "language" in str(error).lower()


# Test 1.10: Valid 2-character scope (boundary)
def test_valid_two_character_scope():
    """Verify schema accepts minimum valid scope length of exactly 2 characters."""
    config = create_config_with_language({"python": "db"})

    # Should not raise ValidationError
    validate_test_config(config)


# Test 1.11: Valid 20-character scope (boundary)
def test_valid_twenty_character_scope():
    """Verify schema accepts maximum valid scope length of exactly 20 characters."""
    # Exactly 20 characters
    config = create_config_with_language({"python": "this-scope-is-20chr"})

    # Should not raise ValidationError
    validate_test_config(config)


# Test 1.12: Valid scope with hyphens and underscores
def test_valid_scope_with_hyphens_and_underscores():
    """Verify schema accepts scope identifiers with valid special characters."""
    config = create_config_with_language({"python": "admin-api_v2"})

    # Should not raise ValidationError
    validate_test_config(config)


# Test 1.13: Rejects old string format
def test_rejects_old_string_format():
    """Verify schema rejects legacy string format and requires new object format."""
    config = create_valid_config()
    # Use old string format instead of object
    config["repo"]["language"] = "python"

    with pytest.raises(ValidationError) as exc_info:
        validate_test_config(config)

    # Error should indicate type mismatch
    error = exc_info.value
    assert "type" in str(error).lower() or (
        "object" in str(error).lower() and "string" in str(error).lower()
    )


# Test 1.14: Valid scoped command names
def test_valid_scoped_command_names():
    """Verify schema accepts scoped command names following {scope}_{command} pattern."""
    config = create_valid_config()
    # Add scoped commands for multi-language setup
    config["commands"]["backend_test"] = {
        "command": "pytest",
        "description": "Run backend tests",
        "category": "test",
    }
    config["commands"]["frontend_lint"] = {
        "command": "npm run lint",
        "description": "Run frontend linter",
        "category": "quality",
    }
    config["commands"]["db_typecheck"] = {
        "command": "mypy db/",
        "description": "Run database type checker",
        "category": "quality",
    }

    # Should not raise ValidationError
    validate_test_config(config)


# Test 1.15: Valid scoped command with hyphens in scope
def test_valid_scoped_command_with_hyphens():
    """Verify schema accepts scoped commands with hyphens in scope identifier."""
    config = create_valid_config()
    config["commands"]["admin-api_test"] = {
        "command": "pytest admin/",
        "description": "Run admin API tests",
        "category": "test",
    }

    # Should not raise ValidationError
    validate_test_config(config)


# ═══════════════════════════════════════════════════════════════════════════
# TEST PROCESS VOCABULARY — NAMED SCHEMA PROPERTIES
# ═══════════════════════════════════════════════════════════════════════════


def test_schema_defines_test_summary_as_named_property():
    """Verify schema defines test_summary as explicit named property in commands.properties."""
    schema = load_test_schema()
    command_properties = schema["properties"]["commands"]["properties"]

    assert "test_summary" in command_properties


def test_schema_defines_test_unit_as_named_property():
    """Verify schema defines test_unit as explicit named property in commands.properties."""
    schema = load_test_schema()
    command_properties = schema["properties"]["commands"]["properties"]

    assert "test_unit" in command_properties


def test_schema_defines_test_integration_as_named_property():
    """Verify schema defines test_integration as explicit named property in commands.properties."""
    schema = load_test_schema()
    command_properties = schema["properties"]["commands"]["properties"]

    assert "test_integration" in command_properties


def test_schema_defines_test_e2e_as_named_property():
    """Verify schema defines test_e2e as explicit named property in commands.properties."""
    schema = load_test_schema()
    command_properties = schema["properties"]["commands"]["properties"]

    assert "test_e2e" in command_properties


def test_schema_test_process_properties_reference_command_object():
    """Verify all test process named properties reference the commandObject definition."""
    schema = load_test_schema()
    command_properties = schema["properties"]["commands"]["properties"]
    test_keys = ["test_summary", "test_unit", "test_integration", "test_e2e"]

    for key in test_keys:
        prop = command_properties[key]
        assert "$ref" in prop, f"{key} missing $ref to commandObject"
        assert prop["$ref"] == "#/definitions/commandObject"


def test_existing_config_without_new_properties_still_validates():
    """Verify existing configs without test_summary/test_unit/test_integration pass validation."""
    config = create_valid_config()

    # Config has test and test_coverage but not the new keys — should still validate
    assert "test_summary" not in config["commands"]
    validate_test_config(config)


# ═══════════════════════════════════════════════════════════════════════════
# BUG FIX TESTS — Schema validation gaps (06/04/2026)
# Bug 1: Oversized payload passes schema validation (CG-IV2)
# Bug 2: Arbitrary language key names accepted by schema (CG-IV1)
# ═══════════════════════════════════════════════════════════════════════════


def test_rejects_repo_title_exceeding_max_length():
    """Schema must reject repo.title strings longer than maxLength."""
    config = create_valid_config()
    config["repo"]["title"] = "A" * 10000

    with pytest.raises(ValidationError) as exc_info:
        validate_test_config(config)

    error = exc_info.value
    assert "maxLength" in str(error) or "too long" in str(error).lower()


def test_rejects_command_command_field_exceeding_max_length():
    """Schema must reject command.command strings longer than maxLength."""
    config = create_valid_config()
    config["commands"]["test"]["command"] = "A" * 10000

    with pytest.raises(ValidationError) as exc_info:
        validate_test_config(config)

    error = exc_info.value
    assert "maxLength" in str(error) or "too long" in str(error).lower()


def test_rejects_command_description_exceeding_max_length():
    """Schema must reject command.description strings longer than maxLength."""
    config = create_valid_config()
    config["commands"]["test"]["description"] = "A" * 10000

    with pytest.raises(ValidationError) as exc_info:
        validate_test_config(config)

    error = exc_info.value
    assert "maxLength" in str(error) or "too long" in str(error).lower()


def test_rejects_command_category_exceeding_max_length():
    """Schema must reject command.category strings longer than maxLength."""
    config = create_valid_config()
    config["commands"]["test"]["category"] = "A" * 10000

    with pytest.raises(ValidationError) as exc_info:
        validate_test_config(config)

    error = exc_info.value
    assert "maxLength" in str(error) or "too long" in str(error).lower()


def test_rejects_proto_pollution_language_key():
    """Schema must reject __proto__ as a language key name."""
    config = create_config_with_language({"__proto__": "all"})

    with pytest.raises(ValidationError) as exc_info:
        validate_test_config(config)

    error = exc_info.value
    assert (
        "pattern" in str(error).lower()
        or "does not match" in str(error).lower()
        or "additional" in str(error).lower()
    )


def test_rejects_language_key_starting_with_underscore():
    """Schema must reject language key names starting with underscore."""
    config = create_config_with_language({"_private": "all"})

    with pytest.raises(ValidationError) as exc_info:
        validate_test_config(config)

    error = exc_info.value
    assert (
        "pattern" in str(error).lower()
        or "does not match" in str(error).lower()
        or "additional" in str(error).lower()
    )


def test_valid_language_key_still_accepted_after_pattern_tightening():
    """Valid lowercase language keys must still pass after pattern is tightened."""
    config = create_config_with_language({"python": "all"})

    # Should not raise
    validate_test_config(config)
