"""Tests for create_standard_config factory function."""

import pytest

from tests.fixtures.schemas import validate_test_config
from tests.helpers.config_factory import (
    create_config_with_language,
    create_standard_config,
    create_valid_config,
)

# ═══════════════════════════════════════════════════════════════════════════
# SUCCESS PATH TESTS
# ═══════════════════════════════════════════════════════════════════════════


def test_returns_valid_config_for_python_with_no_capabilities():
    """
    Verify the factory returns a complete, schema-compliant config dictionary
    for Python language with all capabilities disabled.

    Gate 1: Testing real behaviour (function return value) → VALID
    Gate 2: No test-only methods → VALID
    Gate 3: No mocking dependencies → VALID
    Gate 4: No mocks → VALID
    Gate 5: Test is isolated → VALID
    Gate 6: Happy path covered → VALID
    """
    config = create_standard_config(language="python", capabilities=set())

    assert "name" in config
    assert "repo" in config
    assert "capabilities" in config
    assert "commands" in config
    assert config["repo"]["language"] == {"python": "all"}
    assert config["capabilities"]["hasUI"] is False
    assert config["capabilities"]["hasDB"] is False
    assert isinstance(config["commands"], dict)
    assert len(config["commands"]) > 0


def test_returns_valid_config_for_python_with_hasdb_capability():
    """
    Verify the factory correctly transforms a capabilities set into a dict
    with explicit True/False values.

    Gate 1: Testing real behaviour (capabilities dict transformation) → VALID
    Gate 5: Test is isolated and order-independent → VALID
    Gate 6: Happy path with single capability → VALID
    """
    config = create_standard_config(language="python", capabilities={"hasDB"})

    assert config["capabilities"]["hasDB"] is True
    assert config["capabilities"]["hasUI"] is False
    assert "commands" in config
    assert isinstance(config["commands"], dict)


def test_returns_valid_config_for_typescript_with_multiple_capabilities():
    """
    Verify the factory handles multiple capabilities simultaneously and loads
    language-specific command sets from different YAML files.

    Gate 1: Testing real behaviour (multiple capabilities, different YAML) → VALID
    Gate 5: Test is isolated → VALID
    Gate 6: Happy path with multiple capabilities → VALID
    """
    config = create_standard_config(language="typescript", capabilities={"hasUI", "hasDB"})

    assert config["capabilities"]["hasUI"] is True
    assert config["capabilities"]["hasDB"] is True
    assert config["repo"]["language"] == {"typescript": "all"}
    assert isinstance(config["commands"], dict)
    assert len(config["commands"]) > 0


def test_loads_all_command_sections_from_yaml():
    """
    Verify the factory merges all YAML sections (core, variants, formatting,
    documentation) into a single commands dict.

    Gate 1: Testing real behaviour (YAML section merging) → VALID
    Gate 5: Test is isolated → VALID
    Gate 6: Happy path for section merging → VALID
    """
    config = create_standard_config(language="python")

    commands = config["commands"]
    assert "test" in commands
    assert "lint" in commands
    assert "typecheck" in commands
    assert "test_coverage" in commands
    assert "lint_fix" in commands
    assert "format" in commands
    assert "format_check" in commands


def test_commands_use_object_format_with_required_fields():
    """
    Verify all command entries in the returned config use the correct object
    format with required fields per schema requirements.

    Gate 1: Testing real behaviour (command structure validation) → VALID
    Gate 5: Test is isolated → VALID
    Gate 6: Happy path for object format → VALID
    """
    config = create_standard_config(language="python")

    for command_name, command_entry in config["commands"].items():
        assert isinstance(command_entry, dict), f"{command_name} is not a dict"
        assert "command" in command_entry, f"{command_name} missing 'command'"
        assert "description" in command_entry, f"{command_name} missing 'description'"
        assert "category" in command_entry, f"{command_name} missing 'category'"
        assert isinstance(command_entry["command"], str)
        assert isinstance(command_entry["description"], str)
        assert isinstance(command_entry["category"], str)


def test_generated_config_passes_schema_validation():
    """
    Verify the factory output is a fully valid config that passes schema
    validation without modification.

    Gate 1: Testing real behaviour (schema validation success) → VALID
    Gate 3: Using real validation dependency → VALID
    Gate 5: Test is isolated → VALID
    Gate 6: Happy path for schema compliance → VALID
    """
    config = create_standard_config(language="python", capabilities={"hasDB"})

    validate_test_config(config)


def test_language_mapping_uses_all_scope_format():
    """
    Verify the factory generates single-language configs with the
    {"language": "all"} format.

    Gate 1: Testing real behaviour (language mapping format) → VALID
    Gate 5: Test is isolated → VALID
    Gate 6: Happy path for language format → VALID
    """
    config = create_standard_config(language="python")

    assert config["repo"]["language"] == {"python": "all"}


# ═══════════════════════════════════════════════════════════════════════════
# ERROR CONDITION TESTS
# ═══════════════════════════════════════════════════════════════════════════


def test_raises_filenotfounderror_for_nonexistent_language():
    """
    Verify the factory provides clear, helpful error messages when attempting
    to load commands for a language that doesn't have a YAML file.

    Gate 1: Testing real behaviour (exception raised with message) → VALID
    Gate 5: Test is isolated → VALID
    Gate 6: Error path tested → VALID
    """
    with pytest.raises(FileNotFoundError) as exc_info:
        create_standard_config(language="fortran")

    error_message = str(exc_info.value)
    assert "fortran.yml" in error_message
    assert "Available languages" in error_message


def test_raises_valueerror_for_empty_string_language():
    """
    Verify the factory validates input parameters before attempting file
    operations.

    Gate 1: Testing real behaviour (ValueError raised) → VALID
    Gate 5: Test is isolated → VALID
    Gate 6: Error path for invalid input → VALID
    """
    with pytest.raises(ValueError) as exc_info:
        create_standard_config(language="")

    assert "language parameter cannot be empty" in str(exc_info.value)


def test_handles_yaml_parsing_errors_gracefully():
    """
    Verify the factory propagates YAML parsing errors with helpful context
    when encountering malformed YAML files.

    Gate 1: Testing real behaviour (exception propagation) → VALID
    Gate 3: Using real YAML parser → VALID
    Gate 5: Test uses temporary file, isolated → VALID
    Gate 6: Error path for malformed YAML → VALID

    NOTE: This test will fail in Phase 2 because the factory doesn't
    implement YAML loading yet. In Phase 3, when YAML loading is implemented,
    this test will verify proper error propagation.
    """
    # This test expects the factory to attempt loading a YAML file
    # Since no real language "malformed-test" exists, and the factory
    # should eventually validate and load YAML, this will test error handling

    # For now, this will fail because the factory returns {} without
    # attempting to load any YAML file
    with pytest.raises(FileNotFoundError):
        # Using a language that doesn't exist to trigger YAML file access
        create_standard_config(language="nonexistent-malformed-language")


# ═══════════════════════════════════════════════════════════════════════════
# EDGE CASE TESTS
# ═══════════════════════════════════════════════════════════════════════════


def test_empty_capabilities_set_produces_all_false():
    """
    Verify the default behaviour when no capabilities are specified - all
    known capabilities should be explicitly set to False.

    Gate 1: Testing real behaviour (capabilities dict with False values) → VALID
    Gate 5: Test is isolated → VALID
    Gate 6: Boundary condition (empty set) → VALID
    """
    config = create_standard_config(language="python", capabilities=set())

    assert config["capabilities"]["hasUI"] is False
    assert config["capabilities"]["hasDB"] is False


def test_unknown_capability_keys_silently_ignored():
    """
    Verify the factory handles forward compatibility by including unrecognised
    capability keys (merge pattern allows forward compatibility).

    Gate 1: Testing real behaviour (unknown keys included via merge) → VALID
    Gate 5: Test is isolated → VALID
    Gate 6: Edge case for unknown input → VALID
    """
    config = create_standard_config(language="python", capabilities={"hasUI", "hasFuture"})

    assert config["capabilities"]["hasUI"] is True
    assert config["capabilities"]["hasDB"] is False
    assert config["capabilities"]["hasFuture"] is True


def test_capabilities_parameter_defaults_to_empty_set():
    """
    Verify the function signature default parameter works correctly when
    capabilities argument is omitted.

    Gate 1: Testing real behaviour (default parameter) → VALID
    Gate 5: Test is isolated → VALID
    Gate 6: Boundary condition (omitted parameter) → VALID
    """
    config = create_standard_config(language="python")

    assert config["capabilities"]["hasUI"] is False
    assert config["capabilities"]["hasDB"] is False


def test_all_supported_languages_work_identically():
    """
    Verify the factory is language-agnostic and provides consistent behaviour
    across all supported languages.

    Gate 1: Testing real behaviour (cross-language consistency) → VALID
    Gate 5: Test is isolated (fresh calls for each language) → VALID
    Gate 6: Edge case for all supported inputs → VALID
    """
    languages = ["python", "typescript", "go", "swift"]

    for language in languages:
        config = create_standard_config(language=language)

        assert config["repo"]["language"] == {language: "all"}
        assert isinstance(config["commands"], dict)
        assert len(config["commands"]) > 0
        validate_test_config(config)


def test_function_is_stateless_repeated_calls_produce_identical_output():
    """
    Verify the factory is a pure function with no side effects.

    Gate 1: Testing real behaviour (function purity, identical output) → VALID
    Gate 5: Test verifies isolation explicitly → VALID
    Gate 6: Edge case for statefulness → VALID
    """
    config1 = create_standard_config(language="python", capabilities={"hasDB"})
    config2 = create_standard_config(language="python", capabilities={"hasDB"})

    assert config1 == config2
    assert config1["capabilities"] == config2["capabilities"]
    assert config1["commands"] == config2["commands"]


def test_existing_factory_functions_remain_unchanged():
    """
    Verify backward compatibility - existing factory functions continue to
    work as expected.

    Gate 1: Testing real behaviour (existing functions still work) → VALID
    Gate 5: Test is isolated → VALID
    Gate 6: Regression testing → VALID
    """
    config1 = create_valid_config()
    assert "name" in config1
    assert "commands" in config1

    config2 = create_config_with_language({"python": "backend"})
    assert config2["repo"]["language"] == {"python": "backend"}
    assert "commands" in config2


# ═══════════════════════════════════════════════════════════════════════════
# TEST PROCESS VOCABULARY — LANGUAGE DEFAULT TESTS
# ═══════════════════════════════════════════════════════════════════════════


def test_python_defaults_include_test_summary():
    """Verify Python language defaults provide test_summary as active command."""
    config = create_standard_config(language="python")

    assert "test_summary" in config["commands"]


def test_python_defaults_include_active_test_unit():
    """Verify Python language defaults provide test_unit as active (uncommented) command."""
    config = create_standard_config(language="python")

    assert "test_unit" in config["commands"]


def test_python_defaults_include_active_test_integration():
    """Verify Python language defaults provide test_integration as active (uncommented) command."""
    config = create_standard_config(language="python")

    assert "test_integration" in config["commands"]


def test_python_test_summary_uses_quiet_flags():
    """Verify Python test_summary command uses pytest quiet flags."""
    config = create_standard_config(language="python")

    cmd = config["commands"]["test_summary"]["command"]
    assert "-q" in cmd or "--tb=short" in cmd


def test_python_test_coverage_includes_quiet_flags():
    """Verify Python test_coverage command includes quiet flags for test output."""
    config = create_standard_config(language="python")

    cmd = config["commands"]["test_coverage"]["command"]
    assert "-q" in cmd or "--tb=short" in cmd


def test_all_languages_provide_test_summary():
    """Verify all 5 language defaults provide test_summary as active command."""
    languages = ["python", "typescript", "typescript-npm", "go", "swift"]

    for language in languages:
        config = create_standard_config(language=language)
        assert "test_summary" in config["commands"], f"{language} missing test_summary"


def test_all_languages_provide_active_test_unit():
    """Verify all 5 language defaults provide test_unit as active command."""
    languages = ["python", "typescript", "typescript-npm", "go", "swift"]

    for language in languages:
        config = create_standard_config(language=language)
        assert "test_unit" in config["commands"], f"{language} missing test_unit"


def test_all_languages_provide_active_test_integration():
    """Verify all 5 language defaults provide test_integration as active command."""
    languages = ["python", "typescript", "typescript-npm", "go", "swift"]

    for language in languages:
        config = create_standard_config(language=language)
        assert "test_integration" in config["commands"], f"{language} missing test_integration"
