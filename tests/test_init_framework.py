"""Tests for framework initialization API (scripts/init_framework.py).

This test file covers the simplified template-based initialization:
- _build_base_config(): Build base configuration dict
- _discover_languages(): Scan for .yml.j2 template files
- Template rendering: Jinja2 template rendering with base_config
- initialize_framework(): Main entry point integration
"""

from unittest import mock

import pytest
import yaml

from scripts.init_framework import (
    _build_base_config,
    _discover_languages,
    initialize_framework,
    render_config_string,
)
from scripts.validate_config import validate_config


class TestBuildBaseConfig:
    """Test suite for _build_base_config() function."""

    def test_returns_dict_with_required_fields(self):
        """_build_base_config() returns dict with name, repo.title, repo.language, capabilities."""
        # Arrange
        folder_name = "my-project"
        language = "python"

        # Act
        result = _build_base_config(folder_name, language)

        # Assert: All required fields present
        assert isinstance(result, dict)
        assert result["name"] == "my-project"
        assert result["repo"]["title"] == "my-project"
        assert result["repo"]["language"] == {"python": "all"}
        assert "capabilities" in result

    def test_merges_default_capabilities(self):
        """_build_base_config() includes all capability flags from DEFAULT_CAPABILITIES."""
        # Arrange
        folder_name = "test-proj"
        language = "python"

        # Act
        result = _build_base_config(folder_name, language)

        # Assert: All default capabilities present with correct values
        assert result["capabilities"]["hasUI"] is False
        assert result["capabilities"]["hasDB"] is False
        assert result["capabilities"]["hasTypecheck"] is True
        assert result["capabilities"]["isPublicFacing"] is False
        assert result["capabilities"]["handlesConfidentialData"] is False
        assert result["capabilities"]["hasAuthentication"] is False
        # Verify count matches DEFAULT_CAPABILITIES
        assert len(result["capabilities"]) == 6

    def test_empty_folder_name_raises_value_error(self):
        """_build_base_config() raises ValueError when folder_name is empty string."""
        # Arrange
        folder_name = ""
        language = "python"

        # Act & Assert
        with pytest.raises(ValueError) as exc_info:
            _build_base_config(folder_name, language)

        error_message = str(exc_info.value)
        assert "folder" in error_message.lower() or "name" in error_message.lower()


class TestDiscoverLanguages:
    """Test suite for _discover_languages() function."""

    def test_finds_yml_j2_files(self, tmp_path):
        """_discover_languages() scans commands/ and returns language names from .yml.j2 files."""
        # Arrange: Create mock commands directory with .yml.j2 files
        mock_commands_dir = tmp_path / "commands"
        mock_commands_dir.mkdir()
        (mock_commands_dir / "python.yml.j2").write_text("# Python template")
        (mock_commands_dir / "typescript.yml.j2").write_text("# TypeScript template")

        # Act
        with mock.patch("scripts.init_framework.PROJECT_ROOT", tmp_path):
            languages = _discover_languages()

        # Assert: Returns sorted list of language names
        assert languages == ["python", "typescript"]

    def test_empty_directory_returns_empty_list(self, tmp_path):
        """_discover_languages() returns empty list when no .yml.j2 files exist."""
        # Arrange: Create empty commands directory
        mock_commands_dir = tmp_path / "commands"
        mock_commands_dir.mkdir()

        # Act
        with mock.patch("scripts.init_framework.PROJECT_ROOT", tmp_path):
            languages = _discover_languages()

        # Assert
        assert languages == []


class TestTemplateRendering:
    """Test suite for template rendering functionality."""

    def test_placeholder_replaced_with_yaml(self, tmp_path):
        """Template rendering replaces {{ base_config }} with formatted YAML string."""
        # Arrange: Create template with placeholder
        mock_commands_dir = tmp_path / "commands"
        mock_commands_dir.mkdir()
        template_content = """{{ base_config }}
commands:
  test: pytest
"""
        (mock_commands_dir / "python.yml.j2").write_text(template_content)

        # Create agents directory for output
        agents_dir = tmp_path / "agents"
        agents_dir.mkdir()

        # Act: Mock _discover_languages to return python so we get past validation
        with (
            mock.patch("scripts.init_framework.PROJECT_ROOT", tmp_path),
            mock.patch("scripts.init_framework._discover_languages", return_value=["python"]),
        ):
            initialize_framework("test-project", "python")

        # Assert: Output contains base config YAML
        config_path = agents_dir / "test-project" / "midtempo-framework.yml"
        output = config_path.read_text()

        assert "name: test-project" in output
        assert "repo:" in output
        assert "commands:" in output

    def test_template_content_preserved_after_placeholder(self, tmp_path):
        """Content after {{ base_config }} placeholder appears unchanged in output."""
        # Arrange: Create template with content after placeholder
        mock_commands_dir = tmp_path / "commands"
        mock_commands_dir.mkdir()
        template_content = """{{ base_config }}
commands:
  test:
    command: "pytest"
    description: "Run all tests"
  custom_command:
    command: "echo hello"
    description: "Custom command"
"""
        (mock_commands_dir / "python.yml.j2").write_text(template_content)

        # Create agents directory
        agents_dir = tmp_path / "agents"
        agents_dir.mkdir()

        # Act: Mock _discover_languages to return python so we get past validation
        with (
            mock.patch("scripts.init_framework.PROJECT_ROOT", tmp_path),
            mock.patch("scripts.init_framework._discover_languages", return_value=["python"]),
        ):
            initialize_framework("test-project", "python")

        # Assert: Commands section preserved from template
        config_path = agents_dir / "test-project" / "midtempo-framework.yml"
        output = config_path.read_text()

        assert "custom_command:" in output
        assert 'command: "echo hello"' in output or "command: echo hello" in output


class TestInitializeFramework:
    """Test suite for initialize_framework() main entry point."""

    def test_creates_valid_config_from_python_template(self, tmp_path):
        """initialize_framework() with 'python' creates midtempo-framework.yml with merged content."""
        # Arrange: Create template
        mock_commands_dir = tmp_path / "commands"
        mock_commands_dir.mkdir()
        template_content = """{{ base_config }}
commands:
  test:
    command: "pytest"
    description: "Run all tests"
    category: "test"
  lint:
    command: "ruff check"
    description: "Run linter"
    category: "lint"
  typecheck:
    command: "mypy"
    description: "Type check"
    category: "typecheck"
"""
        (mock_commands_dir / "python.yml.j2").write_text(template_content)

        # Create agents directory
        agents_dir = tmp_path / "agents"
        agents_dir.mkdir()

        # Act: Mock _discover_languages to return python so we get past validation
        with (
            mock.patch("scripts.init_framework.PROJECT_ROOT", tmp_path),
            mock.patch("scripts.init_framework._discover_languages", return_value=["python"]),
        ):
            result = initialize_framework("my-python-project", "python")

        # Assert
        assert result is True
        config_path = agents_dir / "my-python-project" / "midtempo-framework.yml"
        assert config_path.exists()

        with config_path.open() as f:
            config = yaml.safe_load(f)

        assert config["name"] == "my-python-project"
        assert "repo" in config
        assert config["repo"]["title"] == "my-python-project"
        assert config["repo"]["language"] == {"python": "all"}
        assert "capabilities" in config
        assert "commands" in config

    def test_rejects_unknown_language(self, tmp_path):
        """initialize_framework() raises ValueError for unsupported language."""
        # Arrange: Create commands dir with only python template
        mock_commands_dir = tmp_path / "commands"
        mock_commands_dir.mkdir()
        (mock_commands_dir / "python.yml.j2").write_text("{{ base_config }}")
        (mock_commands_dir / "typescript.yml.j2").write_text("{{ base_config }}")

        # Act & Assert: Mock _discover_languages to return real languages
        with (
            mock.patch("scripts.init_framework.PROJECT_ROOT", tmp_path),
            mock.patch(
                "scripts.init_framework._discover_languages",
                return_value=["python", "typescript"],
            ),
            pytest.raises(ValueError) as exc_info,
        ):
            initialize_framework("project", "cobol")

        error_message = str(exc_info.value)
        assert "cobol" in error_message
        assert "python" in error_message.lower()
        assert "typescript" in error_message.lower()

    def test_rejects_reserved_name(self, tmp_path):
        """initialize_framework() raises ValueError for reserved name 'midtempo-framework'."""
        # Arrange
        mock_commands_dir = tmp_path / "commands"
        mock_commands_dir.mkdir()
        (mock_commands_dir / "python.yml.j2").write_text("{{ base_config }}")

        # Act & Assert: Reserved name check happens before language validation
        with (
            mock.patch("scripts.init_framework.PROJECT_ROOT", tmp_path),
            pytest.raises(ValueError) as exc_info,
        ):
            initialize_framework("midtempo-framework", "python")

        error_message = str(exc_info.value)
        assert "midtempo-framework" in error_message
        assert "reserved" in error_message.lower()


class TestIntegration:
    """Integration test for full initialization flow."""

    def test_generated_config_passes_json_schema_validation(self, tmp_path):
        """End-to-end: generated config validates against JSON Schema."""
        # Arrange: Create template with all required fields
        mock_commands_dir = tmp_path / "commands"
        mock_commands_dir.mkdir()
        template_content = """{{ base_config }}
commands:
  test:
    command: "pytest"
    description: "Run all tests"
    category: "test"
  lint:
    command: "ruff check"
    description: "Run linter"
    category: "lint"
  typecheck:
    command: "mypy"
    description: "Type check"
    category: "typecheck"
"""
        (mock_commands_dir / "python.yml.j2").write_text(template_content)

        # Create agents directory
        agents_dir = tmp_path / "agents"
        agents_dir.mkdir()

        # Act: Mock _discover_languages to return python so we get past validation
        with (
            mock.patch("scripts.init_framework.PROJECT_ROOT", tmp_path),
            mock.patch("scripts.init_framework._discover_languages", return_value=["python"]),
        ):
            initialize_framework("test-project", "python")

        # Assert: Config passes validation
        config_path = agents_dir / "test-project" / "midtempo-framework.yml"
        validated_config = validate_config(config_path)
        assert validated_config is not None
        assert validated_config["repo"]["language"] == {"python": "all"}

    def test_malformed_template_raises_value_error(self, tmp_path):
        """initialize_framework() raises ValueError when template produces invalid YAML."""
        # Arrange: Create template that produces invalid YAML (malformed indentation)
        mock_commands_dir = tmp_path / "commands"
        mock_commands_dir.mkdir()
        template_content = """{{ base_config }}
commands:
  test:
  command: "pytest"
    description: "Run tests"
"""
        (mock_commands_dir / "python.yml.j2").write_text(template_content)

        # Create agents directory
        agents_dir = tmp_path / "agents"
        agents_dir.mkdir()

        # Act & Assert: Should raise ValueError about invalid YAML
        with (
            mock.patch("scripts.init_framework.PROJECT_ROOT", tmp_path),
            mock.patch("scripts.init_framework._discover_languages", return_value=["python"]),
            pytest.raises(ValueError) as exc_info,
        ):
            initialize_framework("test-project", "python")

        error_message = str(exc_info.value)
        assert "invalid" in error_message.lower() or "yaml" in error_message.lower()


class TestRenderConfigString:
    """Test suite for render_config_string() function."""

    def test_returns_rendered_yaml_string_for_valid_inputs(self, tmp_path):
        """render_config_string() returns str containing rendered template output for valid inputs."""
        # Arrange
        commands_dir = tmp_path / "commands"
        commands_dir.mkdir()
        (commands_dir / "python.yml.j2").write_text(
            "{{ base_config }}\ncommands:\n  test:\n    command: pytest\n    description: Run tests\n    category: test\n"
        )

        # Act
        with mock.patch("scripts.init_framework.PROJECT_ROOT", tmp_path):
            result = render_config_string("my-project", "python")

        # Assert
        assert isinstance(result, str)
        assert "name: my-project" in result
        assert "commands:" in result
        assert not any(
            p
            for p in tmp_path.rglob("*")
            if p not in (commands_dir, commands_dir / "python.yml.j2")
        )

    def test_returned_string_is_valid_yaml(self, tmp_path):
        """render_config_string() returns a string that parses as a dict under yaml.safe_load()."""
        # Arrange
        commands_dir = tmp_path / "commands"
        commands_dir.mkdir()
        (commands_dir / "python.yml.j2").write_text(
            "{{ base_config }}\ncommands:\n  test:\n    command: pytest\n    description: Run tests\n    category: test\n"
        )

        # Act
        with mock.patch("scripts.init_framework.PROJECT_ROOT", tmp_path):
            result = render_config_string("my-project", "python")

        # Assert
        parsed = yaml.safe_load(result)
        assert isinstance(parsed, dict)

    def test_does_not_create_directories_or_files(self, tmp_path):
        """render_config_string() leaves tmp_path unchanged — creates no directories or files."""
        # Arrange
        commands_dir = tmp_path / "commands"
        commands_dir.mkdir()
        (commands_dir / "python.yml.j2").write_text(
            "{{ base_config }}\ncommands:\n  test:\n    command: pytest\n    description: Run tests\n    category: test\n"
        )
        before = sorted(str(p) for p in tmp_path.rglob("*"))

        # Act
        with mock.patch("scripts.init_framework.PROJECT_ROOT", tmp_path):
            render_config_string("my-project", "python")

        # Assert
        after = sorted(str(p) for p in tmp_path.rglob("*"))
        assert after == before

    def test_raises_value_error_for_reserved_name(self, tmp_path):
        """render_config_string() raises ValueError containing 'reserved' for name='midtempo-framework'."""
        # Arrange — no template setup required; guard fires before template access

        # Act & Assert
        with (
            mock.patch("scripts.init_framework.PROJECT_ROOT", tmp_path),
            pytest.raises(ValueError) as exc_info,
        ):
            render_config_string("midtempo-framework", "python")

        error_message = str(exc_info.value)
        assert "midtempo-framework" in error_message
        assert "reserved" in error_message.lower()

    def test_raises_value_error_for_unknown_language(self, tmp_path):
        """render_config_string() raises ValueError naming the invalid language and listing available options."""
        # Arrange

        # Act & Assert
        with (
            mock.patch(
                "scripts.init_framework._discover_languages", return_value=["python", "typescript"]
            ),
            mock.patch("scripts.init_framework.PROJECT_ROOT", tmp_path),
            pytest.raises(ValueError) as exc_info,
        ):
            render_config_string("my-project", "cobol")

        error_message = str(exc_info.value)
        assert "cobol" in error_message
        assert "python" in error_message
        assert "typescript" in error_message

    def test_raises_value_error_for_invalid_yaml_template(self, tmp_path):
        """render_config_string() raises ValueError containing 'invalid' or 'YAML' for malformed template."""
        # Arrange
        commands_dir = tmp_path / "commands"
        commands_dir.mkdir()
        (commands_dir / "python.yml.j2").write_text("{{ base_config }}\n  bad_indent: [unclosed\n")

        # Act & Assert
        with (
            mock.patch("scripts.init_framework.PROJECT_ROOT", tmp_path),
            mock.patch("scripts.init_framework._discover_languages", return_value=["python"]),
            pytest.raises(ValueError) as exc_info,
        ):
            render_config_string("my-project", "python")

        error_message = str(exc_info.value)
        assert "invalid" in error_message.lower() or "yaml" in error_message.lower()

    def test_reserved_name_check_fires_before_language_check(self, tmp_path):
        """When name is reserved and language unknown, ValueError mentions 'reserved' not the language."""
        # Arrange

        # Act & Assert
        with (
            mock.patch("scripts.init_framework._discover_languages", return_value=["python"]),
            mock.patch("scripts.init_framework.PROJECT_ROOT", tmp_path),
            pytest.raises(ValueError) as exc_info,
        ):
            render_config_string("midtempo-framework", "cobol")

        error_message = str(exc_info.value)
        assert "reserved" in error_message.lower()
        assert "cobol" not in error_message
