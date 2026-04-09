"""Config enrichment tests for language defaults merging."""

from pathlib import Path

import pytest

from scripts.language_config import _enrich_config_with_language_defaults
from scripts.paths import COMMANDS_DIR
from tests.helpers.config_factory import (
    create_config_with_language,
    create_config_with_language_and_commands,
)


# Test 3.1: Extracts first language from mono-language mapping
def test_extracts_first_language_from_mono_language_mapping():
    """Verify enrichment extracts single language from {python: all} and loads defaults."""
    config = create_config_with_language({"python": "all"})

    # Call enrichment with real commands directory
    enriched = _enrich_config_with_language_defaults(config, COMMANDS_DIR)

    # Should extract "python" and load commands/python.yml
    # Commands should be merged from yml file
    assert "commands" in enriched
    assert "test" in enriched["commands"]
    assert "lint" in enriched["commands"]
    assert "typecheck" in enriched["commands"]

    # Values should match python.yml core commands (object format)
    assert enriched["commands"]["test"]["command"] == "pytest"
    assert "ruff" in enriched["commands"]["lint"]["command"]
    assert "mypy" in enriched["commands"]["typecheck"]["command"]


# Test 3.2: Processes ALL languages from multi-language mapping (updated for Rec 3)
def test_extracts_first_language_from_multi_language_mapping():
    """Verify enrichment processes ALL languages, not just first (Rec 3 behavior)."""
    # Use real commands directory with actual defaults files
    config = create_config_with_language({"python": "backend", "typescript": "frontend"})

    # Call enrichment
    enriched = _enrich_config_with_language_defaults(config, COMMANDS_DIR)

    # Should process BOTH languages and generate scoped commands for each
    assert "commands" in enriched

    # Should have scoped commands for backend (python)
    assert "backend_test" in enriched["commands"]
    assert enriched["commands"]["backend_test"]["command"] == "pytest"

    # Should have scoped commands for frontend (typescript)
    assert "frontend_test" in enriched["commands"]
    assert "npm test" in enriched["commands"]["frontend_test"]["command"]

    # Should NOT have bare command names
    assert "test" not in enriched["commands"]


# Test 3.3: Raises error if language yml file missing
def test_raises_error_if_language_yml_missing(tmp_path: Path):
    """Verify enrichment provides clear error when language yml file doesn't exist."""
    config = create_config_with_language({"ruby": "all"})

    # Use empty temporary directory (no ruby.yml exists)
    empty_commands_dir = tmp_path / "commands"
    empty_commands_dir.mkdir()

    # Should raise FileNotFoundError
    with pytest.raises(FileNotFoundError) as exc_info:
        _enrich_config_with_language_defaults(config, empty_commands_dir)

    error_message = str(exc_info.value)

    # Error should indicate which file is missing
    assert "ruby.yml" in error_message or "ruby" in error_message.lower()


# Test 3.4: Merges core defaults into commands section
def test_merges_core_defaults_into_commands():
    """Verify enrichment correctly merges language defaults into config's commands section."""
    config = create_config_with_language({"python": "all"})
    # Start with empty commands
    config["commands"] = {}

    # Call enrichment
    enriched = _enrich_config_with_language_defaults(config, COMMANDS_DIR)

    # Commands should be populated from python.yml core section (object format)
    assert enriched["commands"]["test"]["command"] == "pytest"
    assert "ruff check" in enriched["commands"]["lint"]["command"]
    assert "mypy" in enriched["commands"]["typecheck"]["command"]

    # Original config should not be mutated (deep copy)
    assert config["commands"] == {}


# Test 3.5: Preserves user-specified commands (no override)
def test_preserves_user_specified_commands():
    """Verify enrichment does not override commands explicitly defined by user."""
    config = create_config_with_language({"python": "all"})
    # User has custom test command
    config["commands"] = {
        "test": {
            "command": "pytest tests/ --custom-flag",
            "description": "Run tests with custom flag",
            "category": "test",
        }
    }

    # Call enrichment
    enriched = _enrich_config_with_language_defaults(config, COMMANDS_DIR)

    # User's test command should be preserved, NOT overwritten by default
    assert enriched["commands"]["test"]["command"] == "pytest tests/ --custom-flag"

    # Other defaults should still be merged (object format)
    assert "lint" in enriched["commands"]
    assert "ruff check" in enriched["commands"]["lint"]["command"]

    # User command takes precedence (not the default)
    assert enriched["commands"]["test"]["command"] != "pytest"  # Not the default


# Test 3.6: Generate docs does NOT enrich with language defaults
def test_generate_docs_does_not_enrich_from_language_defaults(tmp_path: Path):
    """
    Verify generate_documentation_with_timing does NOT add commands from python.yml.

    Gate 1: Asserting on real behaviour (rendered output) → VALID
    Gate 2: No test-only methods → VALID
    Gate 3: No mocks → VALID
    Gate 4: N/A → VALID
    Gate 5: Isolated test with tmp_path → VALID
    Gate 6: Happy path for generation without enrichment → VALID

    Context: User purposely removed test_coverage from their config.
    Generation should NOT bring it back from commands/python.yml.
    """
    import yaml

    from scripts.generate_docs import generate_documentation_with_timing

    # Given: Config with ONLY user-defined commands (no enrichment)
    config_data = {
        "name": "test-no-enrich",
        "repo": {
            "title": "Test Project",
            "language": {"python": "all"},
            "type": "api",
        },
        "capabilities": {
            "hasUI": False,
            "hasDB": False,
        },
        "commands": {
            "test": {"command": "pytest", "description": "Run tests", "category": "testing"},
            "lint": {"command": "ruff check", "description": "Lint code", "category": "quality"},
            "typecheck": {"command": "mypy", "description": "Type check", "category": "quality"},
        },
    }

    # Create config file
    config_path = tmp_path / "midtempo-framework.yml"
    config_path.write_text(yaml.dump(config_data))

    # Create minimal template that renders command count
    # If enrichment happens, this will show more than 3 commands
    template_dir = tmp_path / "templates"
    template_dir.mkdir()
    agents_dir = template_dir / "agents"
    agents_dir.mkdir()
    (agents_dir / "test.md.j2").write_text(
        "# Test\nCommand count: {{ commands | length }}\n"
        "Commands: {% for cmd in commands.keys() %}{{ cmd }}, {% endfor %}"
    )

    # Create output dir
    output_dir = tmp_path / "output"

    # When: Generate documentation
    generate_documentation_with_timing(config_path, output_dir, template_dir)

    # Then: Check generated output to see if enrichment occurred
    namespaced_dir = output_dir / "agents" / "test-no-enrich"
    generated_file = namespaced_dir / "test.md"
    assert generated_file.exists()

    content = generated_file.read_text()

    # Assert: Generated output should show ONLY 3 commands (not enriched)
    # Currently will FAIL because enrichment adds commands from python.yml
    assert (
        "Command count: 3" in content
    ), f"Expected 3 commands, but generated content shows: {content}"

    # Should have the 3 user commands
    assert "test" in content
    assert "lint" in content
    assert "typecheck" in content

    # Should NOT have enriched commands from python.yml
    assert "test_coverage" not in content
    assert "lint_fix" not in content
    assert "format" not in content
    assert "test_unit" not in content


# ================================
# NEW TESTS FOR SCOPED DEFAULTS (Rec 3)
# ================================

# Fixture directory for test YAML files
FIXTURES_DIR = Path(__file__).parent / "fixtures" / "commands"


# Test 1.1: Mono-language config with `all` scope generates bare command names
def test_mono_language_all_scope_generates_bare_names():
    """When single language with 'all' scope, commands have bare names (no prefix)."""
    config = create_config_with_language({"python": "all"})

    enriched = _enrich_config_with_language_defaults(config, FIXTURES_DIR)

    # Should generate bare names: test, lint, typecheck (no all_ prefix)
    assert "test" in enriched["commands"]
    assert "lint" in enriched["commands"]
    assert "typecheck" in enriched["commands"]

    # Should NOT have scoped names
    assert "all_test" not in enriched["commands"]

    # Metadata preserved
    assert enriched["commands"]["test"]["command"] == "pytest"
    assert enriched["commands"]["test"]["description"] == "Run all tests"
    assert enriched["commands"]["test"]["category"] == "test"


# Test 1.2: Multi-language config (2 languages) generates scoped commands for each language
def test_multi_language_generates_scoped_commands():
    """When two languages declared, generates scoped commands for both."""
    config = create_config_with_language({"python": "backend", "typescript": "frontend"})

    enriched = _enrich_config_with_language_defaults(config, FIXTURES_DIR)

    # Should generate 6 scoped commands (3 per language)
    assert "backend_test" in enriched["commands"]
    assert "backend_lint" in enriched["commands"]
    assert "backend_typecheck" in enriched["commands"]
    assert "frontend_test" in enriched["commands"]
    assert "frontend_lint" in enriched["commands"]
    assert "frontend_typecheck" in enriched["commands"]

    # Should NOT have bare names
    assert "test" not in enriched["commands"]

    # Python commands use pytest
    assert enriched["commands"]["backend_test"]["command"] == "pytest"

    # TypeScript commands use npm
    assert enriched["commands"]["frontend_test"]["command"] == "npm test"


# Test 1.3: Multi-language config (3 languages) generates scoped commands for all languages
def test_multi_language_three_languages_generates_all_scoped_commands():
    """When three languages declared, generates scoped commands for all three."""
    # For testing purposes, we'll use python twice with different scopes
    # (In real usage, you'd have 3 different languages)
    config = create_config_with_language(
        {"python": "api", "typescript": "frontend"}  # Will extend in future
    )

    enriched = _enrich_config_with_language_defaults(config, FIXTURES_DIR)

    # Should generate commands for both scopes
    assert "api_test" in enriched["commands"]
    assert "api_lint" in enriched["commands"]
    assert "api_typecheck" in enriched["commands"]
    assert "frontend_test" in enriched["commands"]
    assert "frontend_lint" in enriched["commands"]
    assert "frontend_typecheck" in enriched["commands"]

    # All commands should have complete metadata
    assert enriched["commands"]["api_test"]["category"] == "test"
    assert enriched["commands"]["frontend_test"]["category"] == "test"


# Test 2.1: Mono-language descriptions preserve original text
def test_mono_language_descriptions_preserve_original():
    """When single language with 'all' scope, descriptions unchanged from defaults."""
    config = create_config_with_language({"python": "all"})

    enriched = _enrich_config_with_language_defaults(config, FIXTURES_DIR)

    # Descriptions should be unchanged from defaults file
    assert enriched["commands"]["test"]["description"] == "Run all tests"
    assert enriched["commands"]["lint"]["description"] == "Run linter for code quality"
    assert enriched["commands"]["typecheck"]["description"] == "Run type checker"


# Test 2.2: Multi-language descriptions include scope context
def test_multi_language_descriptions_include_scope():
    """When multi-language, descriptions include scope context."""
    config = create_config_with_language({"python": "backend", "typescript": "frontend"})

    enriched = _enrich_config_with_language_defaults(config, FIXTURES_DIR)

    # Descriptions should have scope context
    # "Run all tests" -> "Run backend tests" / "Run frontend tests"
    assert enriched["commands"]["backend_test"]["description"] == "Run backend tests"
    assert enriched["commands"]["frontend_test"]["description"] == "Run frontend tests"

    # For descriptions without "all", scope inserted after "Run "
    assert (
        enriched["commands"]["backend_lint"]["description"] == "Run backend linter for code quality"
    )
    assert enriched["commands"]["frontend_typecheck"]["description"] == "Run frontend type checker"


# Test 3.1: Multiple languages with `all` scope raises ValueError
def test_multi_language_all_scope_raises_error():
    """When multiple languages use 'all' scope, validation fails."""
    config = create_config_with_language({"python": "all", "typescript": "all"})

    with pytest.raises(ValueError) as exc_info:
        _enrich_config_with_language_defaults(config, FIXTURES_DIR)

    error_message = str(exc_info.value)
    assert "Scope 'all' cannot be used with multiple languages" in error_message
    assert "python" in error_message.lower()
    assert "typescript" in error_message.lower()


# Test 3.2: Duplicate scope values raises ValueError
def test_duplicate_scope_values_raises_error():
    """When multiple languages use same scope, validation fails."""
    config = create_config_with_language({"python": "backend", "typescript": "backend"})

    with pytest.raises(ValueError) as exc_info:
        _enrich_config_with_language_defaults(config, FIXTURES_DIR)

    error_message = str(exc_info.value)
    assert "Duplicate scope values detected" in error_message
    assert "backend" in error_message


# Test 3.3: Valid multi-language config with unique scopes passes validation
def test_valid_multi_language_passes_validation():
    """When multi-language with unique scopes, validation passes."""
    config = create_config_with_language({"python": "backend", "typescript": "frontend"})

    # Should not raise
    enriched = _enrich_config_with_language_defaults(config, FIXTURES_DIR)

    # Should have 6 commands
    assert len([k for k in enriched["commands"] if "_" in k]) == 6


# Test 4.1: User-defined scoped command completely replaces default
def test_user_scoped_command_replaces_default():
    """User-defined scoped command completely replaces default for that command."""
    config = create_config_with_language_and_commands(
        {"python": "backend"},
        {
            "backend_test": {
                "command": "custom pytest",
                "description": "Custom backend tests",
                "category": "test",
            }
        },
    )

    enriched = _enrich_config_with_language_defaults(config, FIXTURES_DIR)

    # User command should win
    assert enriched["commands"]["backend_test"]["command"] == "custom pytest"
    assert enriched["commands"]["backend_test"]["description"] == "Custom backend tests"

    # Other defaults should be merged
    assert "backend_lint" in enriched["commands"]
    assert enriched["commands"]["backend_lint"]["command"] == "ruff check ."


# Test 4.2: User-defined commands for one scope don't affect other scope defaults
def test_user_override_one_scope_doesnt_affect_others():
    """User override for one scope doesn't affect other scope defaults."""
    config = create_config_with_language_and_commands(
        {"python": "backend", "typescript": "frontend"},
        {
            "backend_test": {
                "command": "custom",
                "description": "Custom",
                "category": "test",
            }
        },
    )

    enriched = _enrich_config_with_language_defaults(config, FIXTURES_DIR)

    # backend_test uses user values
    assert enriched["commands"]["backend_test"]["command"] == "custom"

    # Other backend commands use defaults
    assert enriched["commands"]["backend_lint"]["command"] == "ruff check ."

    # All frontend commands use defaults
    assert enriched["commands"]["frontend_test"]["command"] == "npm test"
    assert enriched["commands"]["frontend_lint"]["command"] == "eslint src/ tests/"


# Test 5.1: Missing language defaults file raises FileNotFoundError
def test_missing_language_file_raises_error(tmp_path: Path):
    """When language defaults file missing, raises clear error."""
    config = create_config_with_language({"ruby": "all"})

    # Use empty directory
    empty_dir = tmp_path / "commands"
    empty_dir.mkdir()

    with pytest.raises(FileNotFoundError) as exc_info:
        _enrich_config_with_language_defaults(config, empty_dir)

    error_message = str(exc_info.value)
    assert "ruby.yml" in error_message or "ruby" in error_message.lower()


# Test 5.2: Language file missing `core` section raises KeyError
def test_language_file_missing_core_raises_error():
    """When language file missing core section, raises clear error."""
    # Create config pointing to malformed.yml fixture
    config = create_config_with_language({"malformed": "all"})

    # malformed.yml exists but has no core section
    with pytest.raises(KeyError) as exc_info:
        _enrich_config_with_language_defaults(config, FIXTURES_DIR)

    error_message = str(exc_info.value)
    assert "core" in error_message.lower() or "malformed" in error_message.lower()


# Test 6.1: Single language with `all` scope (special case applies correctly)
def test_single_language_all_scope_special_case():
    """Special case for scope='all' works for n=1 languages."""
    config = create_config_with_language({"python": "all"})

    enriched = _enrich_config_with_language_defaults(config, FIXTURES_DIR)

    # Should have bare names, not all_ prefix
    assert "test" in enriched["commands"]
    assert "all_test" not in enriched["commands"]


# Test 6.2: Scope with hyphens generates valid command names
def test_scope_with_hyphens_generates_valid_names():
    """Scope with hyphens generates valid command names."""
    config = create_config_with_language({"python": "admin-api"})

    enriched = _enrich_config_with_language_defaults(config, FIXTURES_DIR)

    # Should generate hyphenated scoped names
    assert "admin-api_test" in enriched["commands"]
    assert "admin-api_lint" in enriched["commands"]
    assert "admin-api_typecheck" in enriched["commands"]

    # Commands should be accessible
    assert enriched["commands"]["admin-api_test"]["command"] == "pytest"


# Test 6.3: Long scope name (20 chars) generates long command names
def test_long_scope_name_generates_long_command_names():
    """Scope at maximum length (20 chars) generates valid long command names."""
    config = create_config_with_language({"python": "verylongscopename12"})  # 20 chars

    enriched = _enrich_config_with_language_defaults(config, FIXTURES_DIR)

    # Should generate long command names
    assert "verylongscopename12_test" in enriched["commands"]  # 25 chars
    assert "verylongscopename12_lint" in enriched["commands"]  # 25 chars
    assert "verylongscopename12_typecheck" in enriched["commands"]  # 31 chars

    # Commands should work
    assert enriched["commands"]["verylongscopename12_test"]["command"] == "pytest"


# Test 6.4: Config without commands key gets commands dict initialized
def test_config_without_commands_key_gets_initialized():
    """When config has no commands key, enrichment initializes empty dict."""
    config = {
        "name": "test-project",
        "repo": {
            "title": "Test Project",
            "language": {"python": "all"},
        },
        "capabilities": {
            "hasUI": False,
            "hasDB": False,
        },
        # No "commands" key at all
    }

    enriched = _enrich_config_with_language_defaults(config, FIXTURES_DIR)

    # Commands dict should be created and populated with defaults
    assert "commands" in enriched
    assert "test" in enriched["commands"]
    assert enriched["commands"]["test"]["command"] == "pytest"
