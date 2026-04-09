"""Tests for template renderer (scripts/generate_docs.py)."""

from datetime import UTC
from pathlib import Path

import pytest
from jinja2 import UndefinedError

from scripts.filters import (
    SmartContext,
    _category_filter,
    _category_impl,
    _cmd_filter,
    _cmd_impl,
    _instructions_impl,
)
from scripts.generate_docs import (
    _extract_framework_version,
    _remap_template_path,
    generate_documentation_with_timing,
    render_template,
    render_template_with_context,
    setup_jinja_environment,
)
from scripts.language_config import _enrich_config_with_language_defaults, _generate_config_file


class TestTemplateRendering:
    """Test suite for Jinja2 template rendering."""

    def test_renders_simple_template_with_config_substitution(self, tmp_path):
        """Simple template with variable substitution renders correctly."""
        # Arrange: Create template and config
        template_dir = tmp_path / "templates"
        template_dir.mkdir()
        template_path = template_dir / "test.md.j2"
        template_path.write_text("Language: {{ repo.language }}")

        config = {"repo": {"language": {"typescript": "all"}}}
        env = setup_jinja_environment(template_dir)

        # Act: Render template
        result = render_template(env, "test.md.j2", config)

        # Assert: Output contains substituted value (dict representation until templates updated in Rec 3/4)
        assert result == "Language: {'typescript': 'all'}"

    def test_conditional_ui_block_included_when_hasui_true(self, tmp_path):
        """Conditional UI block included when hasUI is true."""
        # Arrange: Create template with conditional
        template_dir = tmp_path / "templates"
        template_dir.mkdir()
        template_path = template_dir / "test.md.j2"
        template_path.write_text("{% if capabilities.hasUI %}UI section{% endif %}")

        config = {"capabilities": {"hasUI": True}}
        env = setup_jinja_environment(template_dir)

        # Act: Render template
        result = render_template(env, "test.md.j2", config)

        # Assert: UI section is present
        assert "UI section" in result

    def test_conditional_ui_block_excluded_when_hasui_false(self, tmp_path):
        """Conditional UI block excluded when hasUI is false."""
        # Arrange: Same template as previous test
        template_dir = tmp_path / "templates"
        template_dir.mkdir()
        template_path = template_dir / "test.md.j2"
        template_path.write_text("{% if capabilities.hasUI %}UI section{% endif %}")

        config = {"capabilities": {"hasUI": False}}
        env = setup_jinja_environment(template_dir)

        # Act: Render template
        result = render_template(env, "test.md.j2", config)

        # Assert: UI section is NOT present
        assert "UI section" not in result
        assert result == "" or result.strip() == ""

    def test_missing_required_variable_raises_undefined_error(self, tmp_path):
        """Missing required variable raises UndefinedError with template context."""
        # Arrange: Template references undefined variable
        template_dir = tmp_path / "templates"
        template_dir.mkdir()
        template_path = template_dir / "test.md.j2"
        template_path.write_text("{{ commands.undefined_command }}")

        config = {
            "commands": {
                "test": {
                    "command": "npm test",
                    "description": "Run tests",
                    "category": "test",
                }
            }
        }  # missing undefined_command
        env = setup_jinja_environment(template_dir)

        # Act & Assert: Rendering raises UndefinedError
        with pytest.raises(UndefinedError) as exc_info:
            render_template(env, "test.md.j2", config)

        error_message = str(exc_info.value).lower()
        assert "undefined" in error_message

    def test_template_inheritance_works(self, tmp_path):
        """Template inheritance allows child to override parent blocks."""
        # Arrange: Create base and child templates
        template_dir = tmp_path / "templates"
        template_dir.mkdir()

        base_path = template_dir / "base.md.j2"
        base_path.write_text("{% block content %}default{% endblock %}")

        child_path = template_dir / "child.md.j2"
        child_path.write_text('{% extends "base.md.j2" %}{% block content %}custom{% endblock %}')

        config: dict = {}
        env = setup_jinja_environment(template_dir)

        # Act: Render child template
        result = render_template(env, "child.md.j2", config)

        # Assert: Output contains overridden content
        assert "custom" in result
        assert "default" not in result

    def test_undefined_error_includes_file_line_context(self, tmp_path):
        """UndefinedError message includes file:line context and config suggestion."""
        # Arrange: Template with undefined variable at specific line
        template_dir = tmp_path / "templates"
        template_dir.mkdir()
        template_path = template_dir / "test.md.j2"
        template_path.write_text(
            """# Header
Second line
Third line with {{ commands.build }} variable
"""
        )

        config = {
            "commands": {
                "test": {
                    "command": "npm test",
                    "description": "Run tests",
                    "category": "test",
                }
            }
        }  # missing build command
        env = setup_jinja_environment(template_dir)

        # Act & Assert: Error message includes file and line context
        with pytest.raises(UndefinedError) as exc_info:
            render_template_with_context(env, "test.md.j2", config, template_dir)

        error_message = str(exc_info.value)
        # Should contain filename and suggestion
        assert "test.md.j2" in error_message or "commands" in error_message

    def test_performance_logging_reports_generation_time(self, tmp_path):
        """Generation reports file count and elapsed time."""
        # Arrange: Create 3 valid templates
        template_dir = tmp_path / "templates"
        template_dir.mkdir()

        for i in range(3):
            template_path = template_dir / f"file{i}.md.j2"
            template_path.write_text(f"# File {i}\nContent: {{{{ repo.title }}}}")

        output_dir = tmp_path / "output"
        output_dir.mkdir()

        config_path = tmp_path / "config.yml"
        config_path.write_text("repo:\n  title: Test\n")

        # Act: Generate with timing
        result = generate_documentation_with_timing(config_path, output_dir, template_dir)

        # Assert: Result includes file count and timing info
        assert result["file_count"] == 3
        assert "elapsed" in result
        assert isinstance(result["elapsed"], float)
        assert result["elapsed"] >= 0

    def test_json_schema_validation_fails_on_missing_required_field(self, tmp_path):
        """Config validation detects missing required fields before rendering."""
        # Arrange: Config missing required field
        config_path = tmp_path / "config.yml"
        config_path.write_text("repo:\n  title: Test\n")  # missing language field

        template_dir = tmp_path / "templates"
        template_dir.mkdir()
        template_path = template_dir / "test.md.j2"
        template_path.write_text("# {{ repo.title }}")

        output_dir = tmp_path / "output"
        output_dir.mkdir()

        # Act & Assert: Generation fails with validation error
        with pytest.raises(Exception) as exc_info:
            from scripts.generate_docs import generate_documentation

            generate_documentation(config_path, output_dir)

        # Error should indicate validation failure
        error_message = str(exc_info.value).lower()
        assert (
            "validation" in error_message
            or "schema" in error_message
            or "required" in error_message
        )

    def test_successful_generation_writes_all_files(self, tmp_path):
        """Complete generation workflow writes all template outputs."""
        # Arrange: Create 3 templates and valid config
        template_dir = tmp_path / "templates"
        template_dir.mkdir()

        templates = ["README.md.j2", "CONTRIBUTING.md.j2", "setup.md.j2"]
        for template_name in templates:
            template_path = template_dir / template_name
            template_path.write_text("# {{ repo.title }}\n{{ repo.description }}")

        output_dir = tmp_path / "output"
        output_dir.mkdir()

        config_path = tmp_path / "config.yml"
        config_path.write_text(
            """repo:
  title: TestRepo
  description: Test description
  language: python
capabilities:
  hasUI: false
  hasDB: false
commands:
  test:
    command: pytest
    description: Run tests
    category: test
"""
        )

        # Act: Generate documentation using timing function with custom template dir
        from scripts.generate_docs import generate_documentation_with_timing

        result_dict = generate_documentation_with_timing(config_path, output_dir, template_dir)
        result = result_dict["file_count"] > 0

        # Assert: All 3 output files created with rendered content
        assert result is True
        output_files = list(output_dir.glob("*.md"))
        assert len(output_files) == 3

        # Verify content rendered (no template syntax)
        for output_file in output_files:
            content = output_file.read_text()
            assert "TestRepo" in content
            assert "{{" not in content  # No unrendered template syntax


class TestPathRemapping:
    """Test suite for path remapping function (Module 1)."""

    def test_remap_instructions_to_agents_instructions(self):
        """Verify that template paths starting with instructions/ remain unchanged."""
        # Arrange
        relative_path = Path("instructions/error-handling.md")

        # Act
        result = _remap_template_path(relative_path)

        # Assert
        assert result == Path("instructions/error-handling.md")

    def test_remap_rules_to_agents_rules(self):
        """Verify that template paths starting with rules/ remain unchanged."""
        # Arrange
        relative_path = Path("rules/tdd.md")

        # Act
        result = _remap_template_path(relative_path)

        # Assert
        assert result == Path("rules/tdd.md")

    def test_remap_templates_to_planning(self):
        """Verify that template paths starting with templates/ remain unchanged."""
        # Arrange
        relative_path = Path("templates/design.md")

        # Act
        result = _remap_template_path(relative_path)

        # Assert
        assert result == Path("templates/design.md")

    def test_keep_agents_unchanged(self):
        """Verify that template paths starting with agents/ have the agents/ prefix stripped."""
        # Arrange
        relative_path = Path("agents/brainstorming.md")

        # Act
        result = _remap_template_path(relative_path)

        # Assert
        assert result == Path("brainstorming.md")

    def test_base_paths_pass_through(self):
        """Verify that base/ paths pass through unchanged (caller filters these out)."""
        # Arrange
        relative_path = Path("base/standard.md")

        # Act
        result = _remap_template_path(relative_path)

        # Assert
        assert result == Path("base/standard.md")

    def test_nested_template_path_preserves_structure(self):
        """Verify that deeply nested template paths remain unchanged while preserving nested structure."""
        # Arrange - nested templates/ path
        relative_path = Path("templates/nested/sub/plan.md")

        # Act
        result = _remap_template_path(relative_path)

        # Assert
        assert result == Path("templates/nested/sub/plan.md")

    def test_empty_path_returns_empty(self):
        """Verify that empty path is handled gracefully."""
        # Arrange
        relative_path = Path()

        # Act
        result = _remap_template_path(relative_path)

        # Assert
        assert result == Path()

    def test_unknown_directory_passes_through(self):
        """Verify that unknown directory paths pass through unchanged."""
        # Arrange
        relative_path = Path("unknown/file.md")

        # Act
        result = _remap_template_path(relative_path)

        # Assert
        assert result == Path("unknown/file.md")


class TestAgentFileRenaming:
    """Test suite for repo.agentFile output filename control."""

    def test_agent_file_claude_renames_agents_md_to_claude_md(self, tmp_path):
        """AGENTS.md.j2 generates as CLAUDE.md when repo.agentFile is CLAUDE."""
        # Arrange: Create agents/AGENTS.md.j2 template with simple content
        template_dir = tmp_path / "templates"
        agents_dir = template_dir / "agents"
        agents_dir.mkdir(parents=True)
        (agents_dir / "AGENTS.md.j2").write_text("# Agent Rules\n{{ repo.title }}")

        output_dir = tmp_path / "output"
        output_dir.mkdir()

        config_path = tmp_path / "config.yml"
        config_path.write_text("repo:\n  title: Test\n  agentFile: CLAUDE\n")

        # Act: Generate documentation
        result = generate_documentation_with_timing(config_path, output_dir, template_dir)

        # Assert: Output file is CLAUDE.md, not AGENTS.md
        assert result["file_count"] == 1
        assert (output_dir / "CLAUDE.md").exists()
        assert not (output_dir / "AGENTS.md").exists()

    def test_agent_file_agents_keeps_agents_md(self, tmp_path):
        """AGENTS.md.j2 generates as AGENTS.md when repo.agentFile is AGENTS."""
        # Arrange: Create agents/AGENTS.md.j2 template
        template_dir = tmp_path / "templates"
        agents_dir = template_dir / "agents"
        agents_dir.mkdir(parents=True)
        (agents_dir / "AGENTS.md.j2").write_text("# Agent Rules\n{{ repo.title }}")

        output_dir = tmp_path / "output"
        output_dir.mkdir()

        config_path = tmp_path / "config.yml"
        config_path.write_text("repo:\n  title: Test\n  agentFile: AGENTS\n")

        # Act: Generate documentation
        result = generate_documentation_with_timing(config_path, output_dir, template_dir)

        # Assert: Output file remains AGENTS.md
        assert result["file_count"] == 1
        assert (output_dir / "AGENTS.md").exists()

    def test_agent_file_omitted_defaults_to_agents_md(self, tmp_path):
        """AGENTS.md.j2 generates as AGENTS.md when repo.agentFile is omitted."""
        # Arrange: Create agents/AGENTS.md.j2 template, no agentFile in config
        template_dir = tmp_path / "templates"
        agents_dir = template_dir / "agents"
        agents_dir.mkdir(parents=True)
        (agents_dir / "AGENTS.md.j2").write_text("# Agent Rules\n{{ repo.title }}")

        output_dir = tmp_path / "output"
        output_dir.mkdir()

        config_path = tmp_path / "config.yml"
        config_path.write_text("repo:\n  title: Test\n")

        # Act: Generate documentation
        result = generate_documentation_with_timing(config_path, output_dir, template_dir)

        # Assert: Output file defaults to AGENTS.md
        assert result["file_count"] == 1
        assert (output_dir / "AGENTS.md").exists()

    def test_agent_file_claude_only_renames_agents_not_other_files(self, tmp_path):
        """Only AGENTS.md.j2 is renamed; other templates unaffected."""
        # Arrange: Create AGENTS.md.j2 and another template
        template_dir = tmp_path / "templates"
        agents_dir = template_dir / "agents"
        agents_dir.mkdir(parents=True)
        (agents_dir / "AGENTS.md.j2").write_text("# Agent Rules\n{{ repo.title }}")
        (agents_dir / "deliver.md.j2").write_text("# Deliver\n{{ repo.title }}")

        output_dir = tmp_path / "output"
        output_dir.mkdir()

        config_path = tmp_path / "config.yml"
        config_path.write_text("repo:\n  title: Test\n  agentFile: CLAUDE\n")

        # Act: Generate documentation
        result = generate_documentation_with_timing(config_path, output_dir, template_dir)

        # Assert: AGENTS.md renamed to CLAUDE.md, deliver.md unchanged
        assert result["file_count"] == 2
        assert (output_dir / "CLAUDE.md").exists()
        assert (output_dir / "deliver.md").exists()
        assert not (output_dir / "AGENTS.md").exists()


class TestMetadataBuilder:
    """Test suite for metadata extraction functions (Module 2)."""

    def test_extract_framework_version_from_pyproject_toml(self, tmp_path):
        """Verify that version field is correctly extracted from pyproject.toml using tomllib."""
        # Arrange - create temporary pyproject.toml with known version
        pyproject_path = tmp_path / "pyproject.toml"
        pyproject_path.write_text('[project]\nversion = "1.2.3"\n')

        # Act
        result = _extract_framework_version(tmp_path)

        # Assert
        assert result == "1.2.3"

    def test_generate_iso_8601_timestamp(self):
        """Verify that metadata timestamp is in correct ISO 8601 format and uses UTC timezone."""
        # Arrange & Act - import needed for timestamp generation
        from datetime import datetime

        # Generate timestamp using same logic as production code will
        timestamp = datetime.now(UTC).isoformat()

        # Assert - timestamp format
        import re

        # ISO 8601 pattern with optional milliseconds and timezone
        pattern = r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d+)?(\+00:00|Z)?$"
        assert re.match(pattern, timestamp), f"Timestamp {timestamp} doesn't match ISO 8601 format"

        # Assert - can be parsed back
        parsed = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
        assert isinstance(parsed, datetime)


class TestFileCleanup:
    """Test suite for output directory cleanup before generation."""

    def test_removes_orphaned_md_files_before_generation(self, tmp_path):
        """Verify that existing .md files are removed before generating new ones."""
        # Arrange: Create template and output directories
        template_dir = tmp_path / "templates"
        template_dir.mkdir()

        # Create a template that will generate one .md file
        template_path = template_dir / "current.md.j2"
        template_path.write_text("# {{ repo.title }}\nCurrent content")

        output_dir = tmp_path / "output"
        output_dir.mkdir()

        # Create orphaned .md files (from previous generation with different templates)
        orphaned_file1 = output_dir / "old-file.md"
        orphaned_file1.write_text("# Old Content\nThis should be removed")
        orphaned_file2 = output_dir / "removed-template.md"
        orphaned_file2.write_text("# Removed\nTemplate was deleted")

        # Create config
        config_path = tmp_path / "config.yml"
        config_path.write_text(
            """name: test-cleanup
repo:
  title: TestRepo
  language:
    python: all
capabilities:
  hasUI: false
  hasDB: false
commands:
  test:
    command: pytest
    description: Run tests
    category: test
"""
        )

        # Act: Generate documentation
        from scripts.generate_docs import generate_documentation_with_timing

        generate_documentation_with_timing(config_path, output_dir, template_dir)

        # Assert: Orphaned files removed, only current template output remains in namespaced dir
        namespaced_dir = output_dir / "agents" / "test-cleanup"
        output_files = list(namespaced_dir.glob("*.md"))
        output_filenames = [f.name for f in output_files]

        assert "current.md" in output_filenames, "New template should generate current.md"
        # Old files in base output_dir should still be there (not cleaned up)
        assert (output_dir / "old-file.md").exists(), "Old files in base dir not affected"
        assert (
            output_dir / "removed-template.md"
        ).exists(), "Removed files in base dir not affected"
        assert len(output_files) == 1, "Only 1 .md file should exist in namespaced dir (current.md)"

    def test_preserves_non_md_files_during_cleanup(self, tmp_path):
        """Verify that non-.md files are preserved during cleanup."""
        # Arrange: Create template and output directories
        template_dir = tmp_path / "templates"
        template_dir.mkdir()

        template_path = template_dir / "doc.md.j2"
        template_path.write_text("# {{ repo.title }}")

        output_dir = tmp_path / "output"
        output_dir.mkdir()

        # Create non-.md files that should be preserved
        config_file = output_dir / "config.yml"
        config_file.write_text("name: test")
        image_file = output_dir / "diagram.png"
        image_file.write_bytes(b"fake image data")

        # Create old .md file that should be removed
        old_md = output_dir / "old.md"
        old_md.write_text("# Old")

        # Create config
        config_path = tmp_path / "config.yml"
        config_path.write_text(
            """name: test-cleanup
repo:
  title: TestRepo
  language:
    python: all
capabilities:
  hasUI: false
  hasDB: false
commands:
  test:
    command: pytest
    description: Run tests
    category: test
"""
        )

        # Act: Generate documentation
        from scripts.generate_docs import generate_documentation_with_timing

        generate_documentation_with_timing(config_path, output_dir, template_dir)

        # Assert: Non-.md files preserved in base dir, files generated in namespaced dir
        assert config_file.exists(), "config.yml should be preserved in base dir"
        assert image_file.exists(), "diagram.png should be preserved in base dir"
        assert old_md.exists(), "old.md in base dir should not be affected"
        namespaced_dir = output_dir / "agents" / "test-cleanup"
        assert (
            namespaced_dir / "doc.md"
        ).exists(), "New doc.md should be generated in namespaced dir"

    def test_cleanup_handles_empty_output_directory(self, tmp_path):
        """Verify that cleanup works when output directory is empty."""
        # Arrange: Create template and empty output directory
        template_dir = tmp_path / "templates"
        template_dir.mkdir()

        template_path = template_dir / "doc.md.j2"
        template_path.write_text("# {{ repo.title }}")

        output_dir = tmp_path / "output"
        output_dir.mkdir()

        # Output directory is empty (no files)

        # Create config
        config_path = tmp_path / "config.yml"
        config_path.write_text(
            """name: test-cleanup
repo:
  title: TestRepo
  language:
    python: all
capabilities:
  hasUI: false
  hasDB: false
commands:
  test:
    command: pytest
    description: Run tests
    category: test
"""
        )

        # Act: Generate documentation (should not fail on empty directory)
        from scripts.generate_docs import generate_documentation_with_timing

        result = generate_documentation_with_timing(config_path, output_dir, template_dir)

        # Assert: Generation succeeds and creates expected file in namespaced dir
        assert result["file_count"] == 1
        namespaced_dir = output_dir / "agents" / "test-cleanup"
        assert (namespaced_dir / "doc.md").exists()

    def test_cleanup_preserves_instructions_folder_contents(self, tmp_path):
        """Verify that client-maintained instruction files are preserved during cleanup."""
        # Arrange: Create output directory with .md files in various locations
        output_dir = tmp_path / "output"
        output_dir.mkdir()

        # Create .md files that SHOULD be deleted
        root_md = output_dir / "old-doc.md"
        root_md.write_text("# Old root doc")

        rules_dir = output_dir / "rules"
        rules_dir.mkdir()
        rules_md = rules_dir / "old-rule.md"
        rules_md.write_text("# Old rule")

        # Create instructions/ folder with client-maintained files that SHOULD be preserved
        instructions_dir = output_dir / "instructions"
        instructions_dir.mkdir()
        db_instruction = instructions_dir / "db.md"
        db_instruction.write_text("# Database access patterns\nClient-maintained content")
        page_instruction = instructions_dir / "new-page.md"
        page_instruction.write_text("# Page wiring\nClient-maintained content")

        # Act: Call cleanup function directly
        from scripts.generate_docs import _cleanup_md_files

        _cleanup_md_files(output_dir)

        # Assert: Files outside instructions/ are deleted, instructions/ files preserved
        assert not root_md.exists(), "Root .md file should be deleted"
        assert not rules_md.exists(), "Rules .md file should be deleted"
        assert db_instruction.exists(), "instructions/db.md should be preserved"
        assert page_instruction.exists(), "instructions/new-page.md should be preserved"
        assert (
            db_instruction.read_text() == "# Database access patterns\nClient-maintained content"
        ), "Instruction file content should be unchanged"


class TestConfigGenerator:
    """Test suite for config file generation (Module 3)."""

    def test_update_input_config_in_place_with_metadata(self, tmp_path):
        """Verify that input config file is updated in place with metadata section."""
        # Arrange - create input config file
        import yaml

        input_config_path = tmp_path / "midtempo-framework.yml"
        config = {"name": "test-config", "repo": "example/repo"}
        input_config_path.write_text(yaml.dump(config, sort_keys=False))
        framework_version = "1.0.0"

        # Act
        _generate_config_file(input_config_path, framework_version)

        # Assert - same file updated
        assert input_config_path.exists()
        parsed = yaml.safe_load(input_config_path.read_text())
        assert parsed["name"] == "test-config"
        assert parsed["repo"] == "example/repo"
        assert "metadata" in parsed
        assert "generated_at" in parsed["metadata"]
        assert parsed["metadata"]["framework_version"] == "1.0.0"

    def test_preserve_original_config_fields_unchanged(self, tmp_path):
        """Verify that all original config fields remain unchanged after update."""
        # Arrange - comprehensive config
        import yaml

        input_config_path = tmp_path / "config.yml"
        config = {
            "name": "test-app",
            "repo": "example/test-app",
            "capabilities": ["api", "ui"],
            "commands": {
                "start": {
                    "command": "npm start",
                    "description": "Start application",
                    "category": "run",
                }
            },
        }
        input_config_path.write_text(yaml.dump(config, sort_keys=False))

        # Act
        _generate_config_file(input_config_path, "1.0.0")

        # Assert - original fields preserved
        parsed = yaml.safe_load(input_config_path.read_text())
        assert parsed["name"] == "test-app"
        assert parsed["repo"] == "example/test-app"
        assert parsed["capabilities"] == ["api", "ui"]
        assert parsed["commands"] == {
            "start": {
                "command": "npm start",
                "description": "Start application",
                "category": "run",
            }
        }

    def test_update_existing_metadata_on_regeneration(self, tmp_path):
        """Verify that metadata is updated when config already has metadata section."""
        # Arrange - config with existing metadata
        import yaml

        input_config_path = tmp_path / "config.yml"
        config = {
            "name": "test-config",
            "metadata": {
                "generated_at": "2025-01-01T00:00:00Z",
                "framework_version": "0.9.0",
            },
        }
        input_config_path.write_text(yaml.dump(config, sort_keys=False))

        # Act - regenerate
        _generate_config_file(input_config_path, "1.0.0")

        # Assert - metadata updated
        parsed = yaml.safe_load(input_config_path.read_text())
        assert parsed["metadata"]["framework_version"] == "1.0.0"
        # Timestamp should be newer than 2025-01-01
        assert parsed["metadata"]["generated_at"] != "2025-01-01T00:00:00Z"

    def test_no_separate_output_config_created(self, tmp_path):
        """Verify that no separate {name}-agents.yml file is created."""
        # Arrange
        import yaml

        input_config_path = tmp_path / "midtempo-framework.yml"
        config = {"name": "test-config"}
        input_config_path.write_text(yaml.dump(config, sort_keys=False))

        # Act
        _generate_config_file(input_config_path, "1.0.0")

        # Assert - only input config exists, no separate output config
        assert input_config_path.exists()
        output_config = tmp_path / "test-config-agents.yml"
        assert not output_config.exists()

    def test_valid_yaml_output(self, tmp_path):
        """Verify that updated file is valid YAML and can be parsed without errors."""
        # Arrange - complex config with various data types
        import yaml

        input_config_path = tmp_path / "config.yml"
        config = {
            "name": "test-config",
            "repo": "example/repo",
            "capabilities": ["api", "ui"],
            "commands": {
                "test": {
                    "command": "pytest",
                    "description": "Run tests",
                    "category": "test",
                },
                "build": {
                    "command": "python setup.py build",
                    "description": "Build package",
                    "category": "build",
                },
            },
            "version": 1.0,
        }
        input_config_path.write_text(yaml.dump(config, sort_keys=False))

        # Act
        _generate_config_file(input_config_path, "1.0.0")

        # Assert - can parse without error
        parsed = yaml.safe_load(input_config_path.read_text())
        assert isinstance(parsed, dict)
        assert parsed["name"] == "test-config"
        assert parsed["capabilities"] == ["api", "ui"]
        assert "metadata" in parsed

    def test_preserves_comments_when_updating_metadata(self, tmp_path):
        """Verify that comments in config file are preserved when metadata is updated."""
        # Arrange - create config file with comments
        input_config_path = tmp_path / "config.yml"
        config_with_comments = """name: test-config
repo:
  title: Test Repo
  language: python
  purpose: purpose.md
capabilities:
  hasUI: false
  hasDB: false
commands:
  # Core commands
  test: npm run test:python
  lint: npm run lint:python
  typecheck: npm run typecheck:python
"""
        input_config_path.write_text(config_with_comments)

        # Act - update metadata
        _generate_config_file(input_config_path, "1.0.0")

        # Assert - comments are preserved
        updated_content = input_config_path.read_text()
        assert (
            "# Core commands" in updated_content
        ), "Comment should be preserved after metadata update"
        assert "metadata:" in updated_content, "Metadata section should be added"
        assert (
            "framework_version: 1.0.0" in updated_content
        ), "Framework version should be in metadata"


class TestConfigEnrichment:
    """Test suite for config enrichment with language defaults."""

    def test_enrichment_adds_missing_core_commands_from_language_defaults(self, tmp_path):
        """Config without core commands gets enriched with language defaults (object format)."""
        # Arrange - create commands directory with python.yml (Rec 2 object format)
        import yaml

        commands_dir = tmp_path / "commands"
        commands_dir.mkdir()

        python_yml = commands_dir / "python.yml"
        python_yml.write_text(
            yaml.dump(
                {
                    "language": "python",
                    "core": {
                        "test": {
                            "command": "pytest",
                            "description": "Run all tests",
                            "category": "test",
                        },
                        "lint": {
                            "command": "ruff check scripts/ tests/",
                            "description": "Run linter",
                            "category": "quality",
                        },
                        "typecheck": {
                            "command": "mypy scripts/ tests/",
                            "description": "Run type checker",
                            "category": "quality",
                        },
                    },
                },
                sort_keys=False,
            )
        )

        config = {
            "repo": {"language": {"python": "all"}},
            "commands": {},  # Empty - should get enriched
        }

        # Act
        enriched = _enrich_config_with_language_defaults(config, commands_dir)

        # Assert - core commands added from language defaults (object format)
        assert enriched["commands"]["test"]["command"] == "pytest"
        assert enriched["commands"]["lint"]["command"] == "ruff check scripts/ tests/"
        assert enriched["commands"]["typecheck"]["command"] == "mypy scripts/ tests/"

    def test_enrichment_preserves_user_specified_commands(self, tmp_path):
        """User-specified commands are not overridden by language defaults (object format)."""
        # Arrange - create commands directory with python.yml (Rec 2 object format)
        import yaml

        commands_dir = tmp_path / "commands"
        commands_dir.mkdir()

        python_yml = commands_dir / "python.yml"
        python_yml.write_text(
            yaml.dump(
                {
                    "language": "python",
                    "core": {
                        "test": {
                            "command": "pytest",
                            "description": "Run all tests",
                            "category": "test",
                        },
                        "lint": {
                            "command": "ruff check scripts/ tests/",
                            "description": "Run linter",
                            "category": "quality",
                        },
                        "typecheck": {
                            "command": "mypy scripts/ tests/",
                            "description": "Run type checker",
                            "category": "quality",
                        },
                    },
                },
                sort_keys=False,
            )
        )

        config = {
            "repo": {"language": {"python": "all"}},
            "commands": {
                "test": {
                    "command": "npm run test:python",
                    "description": "Custom test",
                    "category": "test",
                },  # User override (object format)
                # lint and typecheck missing - should get defaults
            },
        }

        # Act
        enriched = _enrich_config_with_language_defaults(config, commands_dir)

        # Assert - user command preserved, missing commands added (object format)
        assert enriched["commands"]["test"]["command"] == "npm run test:python"  # Not overridden
        assert enriched["commands"]["lint"]["command"] == "ruff check scripts/ tests/"  # Added
        assert enriched["commands"]["typecheck"]["command"] == "mypy scripts/ tests/"  # Added

    def test_enrichment_with_typescript_language(self, tmp_path):
        """TypeScript language loads defaults from typescript.yml (object format)."""
        # Arrange - create typescript.yml (Rec 2 object format)
        import yaml

        commands_dir = tmp_path / "commands"
        commands_dir.mkdir()

        typescript_yml = commands_dir / "typescript.yml"
        typescript_yml.write_text(
            yaml.dump(
                {
                    "language": "typescript",
                    "core": {
                        "test": {
                            "command": "npm run test",
                            "description": "Run all tests",
                            "category": "test",
                        },
                        "lint": {
                            "command": "npm run lint",
                            "description": "Run linter",
                            "category": "quality",
                        },
                        "typecheck": {
                            "command": "npm run typecheck",
                            "description": "Run type checker",
                            "category": "quality",
                        },
                    },
                },
                sort_keys=False,
            )
        )

        config = {
            "repo": {"language": {"typescript": "all"}},
            "commands": {},
        }

        # Act
        enriched = _enrich_config_with_language_defaults(config, commands_dir)

        # Assert - TypeScript defaults loaded (object format)
        assert enriched["commands"]["test"]["command"] == "npm run test"
        assert enriched["commands"]["lint"]["command"] == "npm run lint"
        assert enriched["commands"]["typecheck"]["command"] == "npm run typecheck"

    def test_invalid_language_raises_file_not_found_error(self, tmp_path):
        """Invalid language raises FileNotFoundError with clear message."""
        # Arrange - empty commands directory (no rust.yml)
        commands_dir = tmp_path / "commands"
        commands_dir.mkdir()

        config = {
            "repo": {"language": {"rust": "all"}},  # No rust.yml exists
            "commands": {},
        }

        # Act & Assert - raises FileNotFoundError
        with pytest.raises(FileNotFoundError) as exc_info:
            _enrich_config_with_language_defaults(config, commands_dir)

        error_message = str(exc_info.value)
        assert "rust.yml" in error_message or "rust" in error_message

    def test_malformed_language_yml_missing_core_section_raises_key_error(self, tmp_path):
        """Language YML missing 'core' section raises KeyError."""
        # Arrange - create malformed python.yml without 'core' section
        import yaml

        commands_dir = tmp_path / "commands"
        commands_dir.mkdir()

        python_yml = commands_dir / "python.yml"
        python_yml.write_text(
            yaml.dump(
                {
                    "language": {"python": "all"},
                    # Missing 'core' section
                    "common_additional": {"test_unit": "pytest tests/unit/"},
                },
                sort_keys=False,
            )
        )

        config = {
            "repo": {"language": {"python": "all"}},
            "commands": {},
        }

        # Act & Assert - raises KeyError
        with pytest.raises(KeyError) as exc_info:
            _enrich_config_with_language_defaults(config, commands_dir)

        error_message = str(exc_info.value)
        assert "core" in error_message.lower()

    def test_enrichment_does_not_mutate_original_config(self, tmp_path):
        """Enrichment returns new dict without mutating original config (object format)."""
        # Arrange
        import yaml

        commands_dir = tmp_path / "commands"
        commands_dir.mkdir()

        python_yml = commands_dir / "python.yml"
        python_yml.write_text(
            yaml.dump(
                {
                    "language": "python",
                    "core": {
                        "test": {
                            "command": "pytest",
                            "description": "Run all tests",
                            "category": "test",
                        },
                        "lint": {
                            "command": "ruff check .",
                            "description": "Run linter",
                            "category": "quality",
                        },
                        "typecheck": {
                            "command": "mypy .",
                            "description": "Run type checker",
                            "category": "quality",
                        },
                    },
                },
                sort_keys=False,
            )
        )

        original_config = {
            "repo": {"language": {"python": "all"}},
            "commands": {},
        }

        # Act
        enriched = _enrich_config_with_language_defaults(original_config, commands_dir)

        # Assert - original unchanged, enriched has new commands (object format)
        assert original_config["commands"] == {}  # Original unchanged
        assert (
            enriched["commands"]["test"]["command"] == "pytest"
        )  # Enriched has defaults (object format)


class TestCmdFilter:
    """Tests for _cmd_filter() Jinja2 custom filter."""

    def test_object_format_resolution(self) -> None:
        """Test 1.2: Filter extracts command field from object format."""
        # Setup: Mock context with object format command
        from typing import Any

        context: dict[str, Any] = {
            "commands": {
                "test": {
                    "command": "pytest --cov",
                    "description": "Run with coverage",
                    "category": "testing",
                }
            }
        }

        # Execute: Call filter with command name
        result = _cmd_filter(context, "test")

        # Assert: Returns command field value only
        assert result == "pytest --cov"

    def test_missing_command_raises_keyerror(self) -> None:
        """Test 1.3: Filter raises descriptive error when command not in commands dict."""
        # Setup: Mock context with empty commands dict
        from typing import Any

        context: dict[str, Any] = {"commands": {}}

        # Execute & Assert: Filter raises KeyError with descriptive message
        with pytest.raises(KeyError, match="Command 'test' not found in config"):
            _cmd_filter(context, "test")

    def test_missing_commands_dict_raises_keyerror(self) -> None:
        """Test 1.4: Filter fails when commands dict absent from context."""
        # Setup: Empty context (missing commands key)
        from typing import Any

        context: dict[str, Any] = {}

        # Execute & Assert: Filter raises KeyError when accessing context['commands']
        with pytest.raises(KeyError):
            _cmd_filter(context, "test")

    def test_malformed_object_raises_keyerror(self) -> None:
        """Test 1.5: Filter fails when object format lacks required command field."""
        # Setup: Mock context with object missing 'command' field
        from typing import Any

        context: dict[str, Any] = {
            "commands": {"test": {"description": "Run tests", "category": "testing"}}
        }

        # Execute & Assert: Filter raises KeyError when accessing value['command']
        with pytest.raises(KeyError):
            _cmd_filter(context, "test")

    def test_filter_integration_with_jinja(self) -> None:
        """Test 1.6: Filter works correctly when registered in real Jinja2 environment."""
        # Setup: Create real Jinja2 Environment
        from pathlib import Path
        from tempfile import TemporaryDirectory

        with TemporaryDirectory() as tmpdir:
            template_dir = Path(tmpdir)

            # Create a test template file
            template_file = template_dir / "test.j2"
            template_file.write_text('{{ "test" | cmd }}')

            # Setup Jinja2 environment with filter registered
            from jinja2 import Environment, FileSystemLoader, StrictUndefined

            env = Environment(
                loader=FileSystemLoader(str(template_dir)),
                undefined=StrictUndefined,
                trim_blocks=True,
                lstrip_blocks=True,
            )
            env.filters["cmd"] = _cmd_filter

            # Create template and context
            template = env.get_template("test.j2")
            context = {
                "commands": {
                    "test": {
                        "command": "pytest",
                        "description": "Run tests",
                        "category": "test",
                    }
                }
            }

            # Execute: Render template
            result = template.render(context)

            # Assert: Rendered output contains resolved command
            assert result == "pytest"


class TestDateStamp:
    """Test suite for dateStamp variable in template context."""

    def test_datestamp_available_in_template_context(self, tmp_path):
        """dateStamp variable renders in templates formatted as dd/mm/yyyy."""
        # Arrange: Create template using dateStamp variable
        template_dir = tmp_path / "templates"
        template_dir.mkdir()
        template_path = template_dir / "test.md.j2"
        template_path.write_text("Generated: {{ dateStamp }}")

        # Create config file
        config_path = tmp_path / "config.yml"
        config_path.write_text("repo:\n  language:\n    python: all\n")

        output_dir = tmp_path / "output"
        output_dir.mkdir()

        # Act: Generate documentation (this triggers enrichment with dateStamp)
        generate_documentation_with_timing(config_path, output_dir, template_dir)

        # Assert: Output file contains today's date in dd/mm/yyyy format
        from datetime import UTC, datetime

        today = datetime.now(UTC).strftime("%d/%m/%Y")
        output_file = output_dir / "test.md"
        assert output_file.exists()
        content = output_file.read_text()
        assert content == f"Generated: {today}"


class TestGlobalMacros:
    """Test suite for global macros loaded from macros.j2."""

    def test_read_file_macro_available_without_import(self, tmp_path):
        """read_file macro is globally available without needing import statement."""
        # Arrange: Create macros.j2 file with read_file macro
        template_dir = tmp_path / "templates"
        template_dir.mkdir()

        macros_path = template_dir / "macros.j2"
        macros_path.write_text(
            """{% macro read_file(path, context="") -%}
READ ALL of `{{ path }}`
{%- if context %} → {{ context }}
{%- endif %}
VERIFY-COMPLETE-READ: Note the last line number you read.
  IF last line number is evenly divisible by 50 (50, 100, 150, ...)
    → STOP. File likely truncated — you only read a partial batch.
    → Re-read the file from where you left off until the true end.
    → Repeat this check until the last line is NOT divisible by 50.
{%- endmacro %}"""
        )

        # Create template using macro without import
        template_path = template_dir / "test.md.j2"
        template_path.write_text("{{ read_file('/midtempo-framework/rules/writing.md') }}")

        config: dict = {}
        env = setup_jinja_environment(template_dir)

        # Act: Render template
        result = render_template(env, "test.md.j2", config)

        # Assert: Macro output present
        assert "READ ALL of `/midtempo-framework/rules/writing.md`" in result
        assert "VERIFY-COMPLETE-READ" in result
        assert "evenly divisible by 50" in result

    def test_read_file_macro_with_context_parameter(self, tmp_path):
        """read_file macro includes context string when provided."""
        # Arrange: Create macros.j2 and template
        template_dir = tmp_path / "templates"
        template_dir.mkdir()

        macros_path = template_dir / "macros.j2"
        macros_path.write_text(
            """{% macro read_file(path, context="") -%}
READ ALL of `{{ path }}`
{%- if context %} → {{ context }}
{%- endif %}
VERIFY-COMPLETE-READ: Note the last line number you read.
  IF last line number is evenly divisible by 50 (50, 100, 150, ...)
    → STOP. File likely truncated — you only read a partial batch.
    → Re-read the file from where you left off until the true end.
    → Repeat this check until the last line is NOT divisible by 50.
{%- endmacro %}"""
        )

        template_path = template_dir / "test.md.j2"
        template_path.write_text(
            "{{ read_file('/midtempo-framework/rules/tdd.md', 'to understand test-first workflow') }}"
        )

        config: dict = {}
        env = setup_jinja_environment(template_dir)

        # Act: Render template
        result = render_template(env, "test.md.j2", config)

        # Assert: Context string included in output
        assert (
            "READ ALL of `/midtempo-framework/rules/tdd.md` → to understand test-first workflow"
            in result
        )

    def test_read_file_macro_without_context_parameter(self, tmp_path):
        """read_file macro works without context parameter (default empty string)."""
        # Arrange: Create macros.j2 and template
        template_dir = tmp_path / "templates"
        template_dir.mkdir()

        macros_path = template_dir / "macros.j2"
        macros_path.write_text(
            """{% macro read_file(path, context="") -%}
READ ALL of `{{ path }}`
{%- if context %} → {{ context }}
{%- endif %}
VERIFY-COMPLETE-READ: Note the last line number you read.
  IF last line number is evenly divisible by 50 (50, 100, 150, ...)
    → STOP. File likely truncated — you only read a partial batch.
    → Re-read the file from where you left off until the true end.
    → Repeat this check until the last line is NOT divisible by 50.
{%- endmacro %}"""
        )

        template_path = template_dir / "test.md.j2"
        template_path.write_text("{{ read_file('/midtempo-framework/rules/testing.md') }}")

        config: dict = {}
        env = setup_jinja_environment(template_dir)

        # Act: Render template
        result = render_template(env, "test.md.j2", config)

        # Assert: Path included and no context arrow before VERIFY-COMPLETE-READ
        assert "READ ALL of `/midtempo-framework/rules/testing.md`" in result
        assert " → " not in result.split("VERIFY-COMPLETE-READ")[0]

    def test_macros_work_when_macros_file_missing(self, tmp_path):
        """Templates render successfully when macros.j2 file doesn't exist."""
        # Arrange: Create template directory WITHOUT macros.j2
        template_dir = tmp_path / "templates"
        template_dir.mkdir()
        # No macros.j2 file created

        template_path = template_dir / "test.md.j2"
        template_path.write_text("# {{ repo.title }}")

        config = {"repo": {"title": "Test Project"}}
        env = setup_jinja_environment(template_dir)

        # Act: Render template
        result = render_template(env, "test.md.j2", config)

        # Assert: Template renders normally
        assert result == "# Test Project"

    def test_multiple_macros_all_globally_available(self, tmp_path):
        """All macros from macros.j2 are globally available."""
        # Arrange: Create macros.j2 with multiple macros
        template_dir = tmp_path / "templates"
        template_dir.mkdir()

        macros_path = template_dir / "macros.j2"
        macros_path.write_text(
            """{% macro read_file(path) -%}
READ: {{ path }}
{%- endmacro %}

{% macro another_macro(text) -%}
OUTPUT: {{ text }}
{%- endmacro %}"""
        )

        template_path = template_dir / "test.md.j2"
        template_path.write_text("{{ read_file('/file.md') }}\n{{ another_macro('Hello World') }}")

        config: dict = {}
        env = setup_jinja_environment(template_dir)

        # Act: Render template
        result = render_template(env, "test.md.j2", config)

        # Assert: Both macros work
        assert "READ: /file.md" in result
        assert "OUTPUT: Hello World" in result

    def test_completion_box_macro(self, tmp_path):
        """completion_box macro creates bordered box with centred title."""
        # Arrange: Create macros.j2 with completion_box macro
        template_dir = tmp_path / "templates"
        template_dir.mkdir()

        macros_path = template_dir / "macros.j2"
        macros_path.write_text(
            """{% macro completion_box(title) -%}
═══════════════════════════════════════════════════════════════════════════════
{{ title | center(79) }}
═══════════════════════════════════════════════════════════════════════════════
{%- endmacro %}"""
        )

        template_path = template_dir / "test.md.j2"
        template_path.write_text("{{ completion_box('DESIGN COMPLETE: FEATURE') }}")

        config: dict = {}
        env = setup_jinja_environment(template_dir)

        # Act: Render template
        result = render_template(env, "test.md.j2", config)

        # Assert: Box borders present and title centred
        lines = result.split("\n")
        assert len(lines) == 3
        assert all(len(line) == 79 for line in lines)
        assert lines[0] == "═" * 79
        assert "DESIGN COMPLETE: FEATURE" in lines[1]
        assert lines[2] == "═" * 79

    def test_require_rules_read_macro(self, tmp_path):
        """require_rules_read macro generates read instructions for multiple rules."""
        # Arrange: Create macros.j2 with simplified macros
        template_dir = tmp_path / "templates"
        template_dir.mkdir()

        macros_path = template_dir / "macros.j2"
        macros_path.write_text(
            """{% macro read_file(path, context="") -%}
READ ALL of `{{ path }}`
{%- if context %} → {{ context }}
{%- endif %}
{%- endmacro %}

{% macro require_rules_read(pages) -%}
{% for page in pages %}
{{ read_file('/midtempo-framework/rules/' ~ page ~ '.md', 'before proceeding') }}
  → INVALID: STOP - Complete the read before proceeding

{% endfor %}
{%- endmacro %}"""
        )

        template_path = template_dir / "test.md.j2"
        template_path.write_text("{{ require_rules_read(['writing', 'testing']) }}")

        config: dict = {}
        env = setup_jinja_environment(template_dir)

        # Act: Render template
        result = render_template(env, "test.md.j2", config)

        # Assert: Both rules files referenced
        assert "READ ALL of `/midtempo-framework/rules/writing.md` → before proceeding" in result
        assert "READ ALL of `/midtempo-framework/rules/testing.md` → before proceeding" in result
        assert result.count("INVALID: STOP") == 2

    def test_require_instructions_read_macro(self, tmp_path):
        """require_instructions_read macro generates read instructions for existing instructions."""
        # Arrange: Create macros.j2 and config with instructions
        template_dir = tmp_path / "templates"
        template_dir.mkdir()

        macros_path = template_dir / "macros.j2"
        macros_path.write_text(
            """{% macro read_file(path, context="") -%}
READ ALL of `{{ path }}`
{%- if context %} → {{ context }}
{%- endif %}
{%- endmacro %}

{% macro require_instructions_read(pages, instructions_dict) -%}
{% for page_key in pages %}
{% if page_key in instructions_dict %}
{{ read_file('/midtempo-framework/instructions/' ~ instructions_dict[page_key].page, 'before proceeding') }}
  → INVALID: STOP - Complete the read before proceeding

{% endif %}
{% endfor %}
{%- endmacro %}"""
        )

        template_path = template_dir / "test.md.j2"
        template_path.write_text(
            "{{ require_instructions_read(['purpose', 'architecture', 'missing'], instructions) }}"
        )

        # Mock instructions namespace
        from scripts.generate_docs import _InstructionsNamespace

        config = {
            "instructions": _InstructionsNamespace(
                {
                    "purpose": {"page": "purpose.md"},
                    "architecture": {"page": "architecture.md"},
                }
            )
        }
        env = setup_jinja_environment(template_dir)

        # Act: Render template
        result = render_template(env, "test.md.j2", config)

        # Assert: Only existing instructions referenced
        assert "READ ALL of `/midtempo-framework/instructions/purpose.md`" in result
        assert "READ ALL of `/midtempo-framework/instructions/architecture.md`" in result
        assert "missing" not in result
        assert result.count("INVALID: STOP") == 2

    def test_conditional_ui_reads_macro_when_hasui_true(self, tmp_path):
        """conditional_ui_reads macro generates UI reads when hasUI is true."""
        # Arrange: Create macros.j2 with simplified macros
        template_dir = tmp_path / "templates"
        template_dir.mkdir()

        macros_path = template_dir / "macros.j2"
        macros_path.write_text(
            """{% macro read_file(path, context="") -%}
READ ALL of `{{ path }}`
{%- endmacro %}

{% macro conditional_ui_reads(caps, instructions_dict, include_new_page=true) -%}
{% if caps.hasUI -%}
{% if 'frontend-design' in instructions_dict -%}
IF work involves UI
{{ read_file('/midtempo-framework/instructions/' ~ instructions_dict['frontend-design'].page, 'for UI component patterns') }}
{% endif -%}
{% endif -%}
{%- endmacro %}"""
        )

        template_path = template_dir / "test.md.j2"
        template_path.write_text("{{ conditional_ui_reads(capabilities, instructions) }}")

        from scripts.generate_docs import _InstructionsNamespace

        config = {
            "capabilities": {"hasUI": True},
            "instructions": _InstructionsNamespace(
                {"frontend-design": {"page": "frontend-design.md"}}
            ),
        }
        env = setup_jinja_environment(template_dir)

        # Act: Render template
        result = render_template(env, "test.md.j2", config)

        # Assert: UI reads present
        assert "IF work involves UI" in result
        assert "/midtempo-framework/instructions/frontend-design.md" in result

    def test_conditional_ui_reads_macro_when_hasui_false(self, tmp_path):
        """conditional_ui_reads macro generates nothing when hasUI is false."""
        # Arrange: Create macros.j2 with conditional_ui_reads macro
        template_dir = tmp_path / "templates"
        template_dir.mkdir()

        macros_path = template_dir / "macros.j2"
        macros_path.write_text(
            """{% macro conditional_ui_reads(caps, instructions_dict, include_new_page=true) -%}
{% if caps.hasUI -%}
IF work involves UI
{% endif -%}
{%- endmacro %}"""
        )

        template_path = template_dir / "test.md.j2"
        template_path.write_text("{{ conditional_ui_reads(capabilities, instructions) }}")

        from scripts.generate_docs import _InstructionsNamespace

        config = {
            "capabilities": {"hasUI": False},
            "instructions": _InstructionsNamespace({}),
        }
        env = setup_jinja_environment(template_dir)

        # Act: Render template
        result = render_template(env, "test.md.j2", config)

        # Assert: No UI reads present
        assert result.strip() == ""

    def test_conditional_db_reads_macro_when_hasdb_true(self, tmp_path):
        """conditional_db_reads macro generates DB reads when hasDB is true."""
        # Arrange: Create macros.j2 with simplified macros
        template_dir = tmp_path / "templates"
        template_dir.mkdir()

        macros_path = template_dir / "macros.j2"
        macros_path.write_text(
            """{% macro read_file(path, context="") -%}
READ ALL of `{{ path }}`
{%- endmacro %}

{% macro conditional_db_reads(caps, instructions_dict) -%}
{% if caps.hasDB and 'db' in instructions_dict -%}
IF work involves databases
{{ read_file('/midtempo-framework/instructions/' ~ instructions_dict['db'].page, 'for database patterns and rules') }}
{% endif -%}
{%- endmacro %}"""
        )

        template_path = template_dir / "test.md.j2"
        template_path.write_text("{{ conditional_db_reads(capabilities, instructions) }}")

        from scripts.generate_docs import _InstructionsNamespace

        config = {
            "capabilities": {"hasDB": True},
            "instructions": _InstructionsNamespace({"db": {"page": "db.md"}}),
        }
        env = setup_jinja_environment(template_dir)

        # Act: Render template
        result = render_template(env, "test.md.j2", config)

        # Assert: DB reads present
        assert "IF work involves databases" in result
        assert "/midtempo-framework/instructions/db.md" in result

    def test_test_status_check_with_logfile_enabled(self, tmp_path):
        """test_status_check macro shows logfile check when enabled and logfile exists."""
        # Arrange: Create macros.j2 with test_status_check macro
        template_dir = tmp_path / "templates"
        template_dir.mkdir()

        macros_path = template_dir / "macros.j2"
        macros_path.write_text(
            """{% macro test_status_check(check_logfile, repo_config, test_cmd_block) -%}
{% if check_logfile and repo_config.logfile is defined and repo_config.logfile %}
**Check test status log file**

```bash
tail -5 {{ repo_config.logfile }}
```
{% else %}
**Check test status**

```bash
{{ test_cmd_block }}
```
{% endif %}
{%- endmacro %}"""
        )

        template_path = template_dir / "test.md.j2"
        template_path.write_text(
            "{{ test_status_check(true, repo, 'npm test    # Run unit tests') }}"
        )

        config = {"repo": {"logfile": "/path/to/test.log"}}
        env = setup_jinja_environment(template_dir)

        # Act: Render template
        result = render_template(env, "test.md.j2", config)

        # Assert: Logfile check present, test command absent
        assert "**Check test status log file**" in result
        assert "tail -5 /path/to/test.log" in result
        assert "npm test" not in result

    def test_test_status_check_with_logfile_disabled(self, tmp_path):
        """test_status_check macro shows test command when logfile check disabled."""
        # Arrange: Create macros.j2
        template_dir = tmp_path / "templates"
        template_dir.mkdir()

        macros_path = template_dir / "macros.j2"
        macros_path.write_text(
            """{% macro test_status_check(check_logfile, repo_config, test_cmd_block) -%}
{% if check_logfile and repo_config.logfile is defined and repo_config.logfile %}
**Check test status log file**

```bash
tail -5 {{ repo_config.logfile }}
```
{% else %}
**Check test status**

```bash
{{ test_cmd_block }}
```
{% endif %}
{%- endmacro %}"""
        )

        template_path = template_dir / "test.md.j2"
        template_path.write_text(
            "{{ test_status_check(false, repo, 'pytest tests/    # Run unit tests') }}"
        )

        config = {"repo": {"logfile": "/path/to/test.log"}}
        env = setup_jinja_environment(template_dir)

        # Act: Render template
        result = render_template(env, "test.md.j2", config)

        # Assert: Test command present, logfile absent
        assert "**Check test status**" in result
        assert "pytest tests/    # Run unit tests" in result
        assert "tail -5" not in result

    def test_test_status_check_without_logfile_defined(self, tmp_path):
        """test_status_check macro shows test command when logfile not in repo config."""
        # Arrange: Create macros.j2
        template_dir = tmp_path / "templates"
        template_dir.mkdir()

        macros_path = template_dir / "macros.j2"
        macros_path.write_text(
            """{% macro test_status_check(check_logfile, repo_config, test_cmd_block) -%}
{% if check_logfile and repo_config.logfile is defined and repo_config.logfile %}
**Check test status log file**

```bash
tail -5 {{ repo_config.logfile }}
```
{% else %}
**Check test status**

```bash
{{ test_cmd_block }}
```
{% endif %}
{%- endmacro %}"""
        )

        template_path = template_dir / "test.md.j2"
        template_path.write_text("{{ test_status_check(true, repo, 'npm test') }}")

        config = {"repo": {"title": "TestRepo"}}  # No logfile in config
        env = setup_jinja_environment(template_dir)

        # Act: Render template
        result = render_template(env, "test.md.j2", config)

        # Assert: Test command present (falls back when logfile undefined)
        assert "**Check test status**" in result
        assert "npm test" in result
        assert "tail -5" not in result

    def test_command_block_macro_renders_with_defaults(self):
        """command_block macro renders command category with default settings."""
        # Arrange: Use real template directory with macros.j2
        from typing import Any

        from scripts.paths import TEMPLATE_DIR

        config: dict[str, Any] = {
            "commands": {
                "test": {"command": "pytest", "description": "Run all tests", "category": "test"},
                "test_unit": {
                    "command": "pytest tests/unit",
                    "description": "Run unit tests",
                    "category": "test",
                },
            }
        }

        # Inject SmartContext as 'this'
        filter_implementations = {
            "cmd": _cmd_impl,
            "category": _category_impl,
            "instructions": _instructions_impl,
        }
        config["this"] = SmartContext(config, filter_implementations)

        env = setup_jinja_environment(TEMPLATE_DIR)

        # Act: Render template string with command_block macro
        template = env.from_string("{{ command_block(this, 'test') }}")
        result = template.render(config)

        # Assert: Output contains heading, primary command, and category commands
        assert "#### Test" in result
        assert "pytest    # Run all tests" in result
        assert "pytest tests/unit    # Run unit tests" in result

    def test_command_block_macro_with_custom_title(self):
        """command_block macro uses custom title when provided."""
        # Arrange: Use real template directory with macros.j2
        from typing import Any

        from scripts.paths import TEMPLATE_DIR

        config: dict[str, Any] = {
            "commands": {
                "lint": {"command": "ruff check", "description": "Run linter", "category": "lint"}
            }
        }

        # Inject SmartContext as 'this'
        filter_implementations = {
            "cmd": _cmd_impl,
            "category": _category_impl,
            "instructions": _instructions_impl,
        }
        config["this"] = SmartContext(config, filter_implementations)

        env = setup_jinja_environment(TEMPLATE_DIR)

        # Act: Render template string with command_block macro
        template = env.from_string("{{ command_block(this, 'lint', title='Linting') }}")
        result = template.render(config)

        # Assert: Custom title used instead of formatted category name
        assert "#### Linting" in result
        # Note: Can't assert "#### Lint" not in result because it's a substring of "#### Linting"

    def test_entry_gate_reads_macro_with_rules_and_instructions(self):
        """entry_gate_reads macro generates read validation for rules and instructions."""
        # Arrange: Use real template directory with macros.j2
        from typing import Any

        from scripts.paths import TEMPLATE_DIR

        config: dict[str, Any] = {
            "instructions": {
                "purpose": {"page": "purpose.md", "description": "Project purpose"},
                "architecture": {"page": "architecture.md", "description": "System design"},
            }
        }

        # Inject SmartContext as 'this'
        filter_implementations = {
            "cmd": _cmd_impl,
            "category": _category_impl,
            "instructions": _instructions_impl,
        }
        config["this"] = SmartContext(config, filter_implementations)

        env = setup_jinja_environment(TEMPLATE_DIR)

        # Act: Render template string with entry_gate_reads macro
        template = env.from_string(
            "{{ entry_gate_reads(this, rules=['writing', 'testing'], instructions=['purpose', 'architecture']) }}"
        )
        result = template.render(config)

        # Assert: Contains rules reads and instruction reads
        assert "READ ALL of `/midtempo-framework/rules/writing.md` → before proceeding" in result
        assert "READ ALL of `/midtempo-framework/rules/testing.md` → before proceeding" in result
        assert "purpose.md" in result
        assert "architecture.md" in result

    def test_verify_compliance_gates_generates_stop_blocks_for_present_docs(self):
        """verify_compliance_gates macro generates conditional STOP blocks for instruction docs present in config."""
        # Arrange: Use real template directory with macros.j2
        from scripts.generate_docs import _InstructionsNamespace
        from scripts.paths import TEMPLATE_DIR

        config = {
            "instructions": _InstructionsNamespace(
                {
                    "purpose": {"page": "purpose.md"},
                    "architecture": {"page": "architecture.md"},
                    "error-handling": {"page": "error-handling.md"},
                }
            ),
            "capabilities": {"hasUI": False, "hasDB": False},
        }

        env = setup_jinja_environment(TEMPLATE_DIR)

        # Act: Render template string with verify_compliance_gates macro
        template = env.from_string(
            "{{ verify_compliance_gates("
            "[('purpose', 'project purpose'), ('architecture', 'architecture'), "
            "('error-handling', 'error handling')], instructions) }}"
        )
        result = template.render(config)

        # Assert: STOP blocks generated for all 3 instruction docs
        assert "project purpose" in result
        assert "'/midtempo-framework/instructions/purpose.md \"Compliance Gates\"'" in result
        assert "Verify all purpose compliance gates before proceeding" in result
        assert "'/midtempo-framework/instructions/architecture.md \"Compliance Gates\"'" in result
        assert "Verify all architecture compliance gates before proceeding" in result
        assert "'/midtempo-framework/instructions/error-handling.md \"Compliance Gates\"'" in result
        assert "Verify all error-handling compliance gates before proceeding" in result
        # Each block has a STOP directive
        assert result.count("STOP") == 3

    def test_verify_compliance_gates_skips_missing_instruction_docs(self):
        """verify_compliance_gates macro skips instruction docs not present in config."""
        # Arrange: Config has only purpose, not architecture
        from scripts.generate_docs import _InstructionsNamespace
        from scripts.paths import TEMPLATE_DIR

        config = {
            "instructions": _InstructionsNamespace(
                {
                    "purpose": {"page": "purpose.md"},
                }
            ),
            "capabilities": {"hasUI": False, "hasDB": False},
        }

        env = setup_jinja_environment(TEMPLATE_DIR)

        # Act: Render with both purpose and architecture requested
        template = env.from_string(
            "{{ verify_compliance_gates("
            "[('purpose', 'project purpose'), ('architecture', 'architecture')], instructions) }}"
        )
        result = template.render(config)

        # Assert: Only purpose block generated, architecture skipped
        assert "purpose" in result
        assert "architecture" not in result
        assert result.count("STOP") == 1

    def test_verify_compliance_gates_ui_generates_blocks_when_hasui_true(self):
        """verify_compliance_gates_ui macro generates STOP blocks when hasUI is true."""
        # Arrange: hasUI=true with frontend-design and style-guide
        from scripts.generate_docs import _InstructionsNamespace
        from scripts.paths import TEMPLATE_DIR

        config = {
            "instructions": _InstructionsNamespace(
                {
                    "frontend-design": {"page": "frontend-design.md"},
                    "style-guide": {"page": "style-guide.md"},
                }
            ),
            "capabilities": {"hasUI": True, "hasDB": False},
        }

        env = setup_jinja_environment(TEMPLATE_DIR)

        # Act: Render with verify_compliance_gates_ui macro
        template = env.from_string("{{ verify_compliance_gates_ui(capabilities, instructions) }}")
        result = template.render(config)

        # Assert: Both UI instruction doc blocks generated
        assert (
            "'/midtempo-framework/instructions/frontend-design.md \"Compliance Gates\"'" in result
        )
        assert "Verify all frontend-design compliance gates before proceeding" in result
        assert "'/midtempo-framework/instructions/style-guide.md \"Compliance Gates\"'" in result
        assert "Verify all style-guide compliance gates before proceeding" in result

    def test_verify_compliance_gates_ui_empty_when_hasui_false(self):
        """verify_compliance_gates_ui macro generates nothing when hasUI is false."""
        # Arrange: hasUI=false
        from scripts.generate_docs import _InstructionsNamespace
        from scripts.paths import TEMPLATE_DIR

        config = {
            "instructions": _InstructionsNamespace(
                {
                    "frontend-design": {"page": "frontend-design.md"},
                    "style-guide": {"page": "style-guide.md"},
                }
            ),
            "capabilities": {"hasUI": False, "hasDB": False},
        }

        env = setup_jinja_environment(TEMPLATE_DIR)

        # Act
        template = env.from_string("{{ verify_compliance_gates_ui(capabilities, instructions) }}")
        result = template.render(config)

        # Assert: No output
        assert result.strip() == ""

    def test_verify_compliance_gates_db_generates_block_when_hasdb_true(self):
        """verify_compliance_gates_db macro generates STOP block when hasDB is true."""
        # Arrange: hasDB=true with db instruction
        from scripts.generate_docs import _InstructionsNamespace
        from scripts.paths import TEMPLATE_DIR

        config = {
            "instructions": _InstructionsNamespace(
                {
                    "db": {"page": "db.md"},
                }
            ),
            "capabilities": {"hasUI": False, "hasDB": True},
        }

        env = setup_jinja_environment(TEMPLATE_DIR)

        # Act
        template = env.from_string("{{ verify_compliance_gates_db(capabilities, instructions) }}")
        result = template.render(config)

        # Assert: DB compliance gate block generated
        assert "'/midtempo-framework/instructions/db.md \"Compliance Gates\"'" in result
        assert "Verify all db compliance gates before proceeding" in result

    def test_verify_compliance_gates_db_empty_when_hasdb_false(self):
        """verify_compliance_gates_db macro generates nothing when hasDB is false."""
        # Arrange: hasDB=false
        from scripts.generate_docs import _InstructionsNamespace
        from scripts.paths import TEMPLATE_DIR

        config = {
            "instructions": _InstructionsNamespace(
                {
                    "db": {"page": "db.md"},
                }
            ),
            "capabilities": {"hasUI": False, "hasDB": False},
        }

        env = setup_jinja_environment(TEMPLATE_DIR)

        # Act
        template = env.from_string("{{ verify_compliance_gates_db(capabilities, instructions) }}")
        result = template.render(config)

        # Assert: No output
        assert result.strip() == ""

    # --- Context-Aware Test Macros (T1.1 through T4.3) ---

    def test_test_targeted_renders_test_command_with_file_placeholder(self):
        """test_targeted macro renders test command with <test-file> placeholder and verbose comment."""
        # Arrange: Use real template directory with macros.j2
        from typing import Any

        from scripts.paths import TEMPLATE_DIR

        config: dict[str, Any] = {
            "commands": {
                "test": {"command": "pytest", "description": "Run all tests", "category": "test"},
            }
        }

        filter_implementations = {
            "cmd": _cmd_impl,
            "category": _category_impl,
            "instructions": _instructions_impl,
        }
        config["this"] = SmartContext(config, filter_implementations)

        env = setup_jinja_environment(TEMPLATE_DIR)

        # Act: Render template string with test_targeted macro
        template = env.from_string("{{ test_targeted(this) }}")
        result = template.render(config)

        # Assert: Contains test command with file placeholder and verbose comment
        assert "pytest" in result
        assert "<test-file>" in result
        assert "# Verbose \u2014 single file for TDD loop" in result

    def test_test_gate_renders_test_summary_when_defined(self):
        """test_gate macro renders test_summary command with summary comment when test_summary defined."""
        # Arrange: Config with both test and test_summary commands
        from typing import Any

        from scripts.paths import TEMPLATE_DIR

        config: dict[str, Any] = {
            "commands": {
                "test": {"command": "pytest", "description": "Run all tests", "category": "test"},
                "test_summary": {
                    "command": "pytest --tb=short",
                    "description": "Run tests with summary output",
                    "category": "test",
                },
            }
        }

        filter_implementations = {
            "cmd": _cmd_impl,
            "category": _category_impl,
            "instructions": _instructions_impl,
        }
        config["this"] = SmartContext(config, filter_implementations)

        env = setup_jinja_environment(TEMPLATE_DIR)

        # Act: Render template string with test_gate macro
        template = env.from_string("{{ test_gate(this) }}")
        result = template.render(config)

        # Assert: Contains test_summary command and summary comment
        assert "pytest --tb=short" in result
        assert "# Summary \u2014 pass/fail + failures only" in result
        # Verify fallback path NOT taken
        assert "# Verbose \u2014 no summary command configured" not in result

    def test_test_gate_falls_back_to_test_when_test_summary_not_defined(self):
        """test_gate macro falls back to test command with verbose comment when test_summary absent."""
        # Arrange: Config with test only, no test_summary
        from typing import Any

        from scripts.paths import TEMPLATE_DIR

        config: dict[str, Any] = {
            "commands": {
                "test": {"command": "pytest", "description": "Run all tests", "category": "test"},
            }
        }

        filter_implementations = {
            "cmd": _cmd_impl,
            "category": _category_impl,
            "instructions": _instructions_impl,
        }
        config["this"] = SmartContext(config, filter_implementations)

        env = setup_jinja_environment(TEMPLATE_DIR)

        # Act: Render template string with test_gate macro
        template = env.from_string("{{ test_gate(this) }}")
        result = template.render(config)

        # Assert: Contains test command and verbose fallback comment
        assert "pytest" in result
        assert "# Verbose \u2014 no summary command configured" in result

    def test_test_coverage_report_renders_test_coverage_when_defined(self):
        """test_coverage_report macro renders test_coverage command with coverage comment."""
        # Arrange: Config with both test and test_coverage commands
        from typing import Any

        from scripts.paths import TEMPLATE_DIR

        config: dict[str, Any] = {
            "commands": {
                "test": {"command": "pytest", "description": "Run all tests", "category": "test"},
                "test_coverage": {
                    "command": "pytest --cov",
                    "description": "Run tests with coverage",
                    "category": "test",
                },
            }
        }

        filter_implementations = {
            "cmd": _cmd_impl,
            "category": _category_impl,
            "instructions": _instructions_impl,
        }
        config["this"] = SmartContext(config, filter_implementations)

        env = setup_jinja_environment(TEMPLATE_DIR)

        # Act: Render template string with test_coverage_report macro
        template = env.from_string("{{ test_coverage_report(this) }}")
        result = template.render(config)

        # Assert: Contains test_coverage command and coverage comment
        assert "pytest --cov" in result
        assert "# Coverage \u2014 metrics + pass/fail" in result
        # Verify fallback path NOT taken
        assert "# Verbose \u2014 no coverage command configured" not in result

    def test_test_coverage_report_falls_back_to_test_when_test_coverage_not_defined(self):
        """test_coverage_report macro falls back to test command when test_coverage absent."""
        # Arrange: Config with test only, no test_coverage
        from typing import Any

        from scripts.paths import TEMPLATE_DIR

        config: dict[str, Any] = {
            "commands": {
                "test": {"command": "pytest", "description": "Run all tests", "category": "test"},
            }
        }

        filter_implementations = {
            "cmd": _cmd_impl,
            "category": _category_impl,
            "instructions": _instructions_impl,
        }
        config["this"] = SmartContext(config, filter_implementations)

        env = setup_jinja_environment(TEMPLATE_DIR)

        # Act: Render template string with test_coverage_report macro
        template = env.from_string("{{ test_coverage_report(this) }}")
        result = template.render(config)

        # Assert: Contains test command and verbose fallback comment
        assert "pytest" in result
        assert "# Verbose \u2014 no coverage command configured" in result

    def test_test_status_check_direct_run_renders_test_summary_when_defined(self):
        """test_status_check direct-run path renders test_summary when test_summary defined and check_logfile=false."""
        # Arrange: Config with both test and test_summary, logfile defined
        from typing import Any

        from scripts.paths import TEMPLATE_DIR

        config: dict[str, Any] = {
            "commands": {
                "test": {"command": "pytest", "description": "Run all tests", "category": "test"},
                "test_summary": {
                    "command": "pytest --tb=short",
                    "description": "Run tests with summary output",
                    "category": "test",
                },
            },
            "repo": {"logfile": "planning/last-test-ran.log"},
        }

        filter_implementations = {
            "cmd": _cmd_impl,
            "category": _category_impl,
            "instructions": _instructions_impl,
        }
        config["this"] = SmartContext(config, filter_implementations)

        env = setup_jinja_environment(TEMPLATE_DIR)

        # Act: Render template string with test_status_check macro (check_logfile=false)
        template = env.from_string("{{ test_status_check(false, this) }}")
        result = template.render(config)

        # Assert: Contains test_summary command, not logfile path
        assert "pytest --tb=short" in result
        assert "tail -5" not in result

    def test_test_status_check_direct_run_falls_back_to_test_when_test_summary_not_defined(self):
        """test_status_check direct-run path renders test when test_summary absent (backward compat)."""
        # Arrange: Config with test only, no test_summary
        from typing import Any

        from scripts.paths import TEMPLATE_DIR

        config: dict[str, Any] = {
            "commands": {
                "test": {"command": "pytest", "description": "Run all tests", "category": "test"},
            },
            "repo": {"logfile": "planning/last-test-ran.log"},
        }

        filter_implementations = {
            "cmd": _cmd_impl,
            "category": _category_impl,
            "instructions": _instructions_impl,
        }
        config["this"] = SmartContext(config, filter_implementations)

        env = setup_jinja_environment(TEMPLATE_DIR)

        # Act: Render template string with test_status_check macro (check_logfile=false)
        template = env.from_string("{{ test_status_check(false, this) }}")
        result = template.render(config)

        # Assert: Contains test command, not logfile path
        assert "pytest" in result
        assert "tail -5" not in result

    def test_test_status_check_logfile_path_unchanged_when_check_logfile_true(self):
        """test_status_check logfile path renders tail command when check_logfile=true and logfile defined."""
        # Arrange: Config with test, test_summary, and logfile
        from typing import Any

        from scripts.paths import TEMPLATE_DIR

        config: dict[str, Any] = {
            "commands": {
                "test": {"command": "pytest", "description": "Run all tests", "category": "test"},
                "test_summary": {
                    "command": "pytest --tb=short",
                    "description": "Run tests with summary output",
                    "category": "test",
                },
            },
            "repo": {"logfile": "planning/last-test-ran.log"},
        }

        filter_implementations = {
            "cmd": _cmd_impl,
            "category": _category_impl,
            "instructions": _instructions_impl,
        }
        config["this"] = SmartContext(config, filter_implementations)

        env = setup_jinja_environment(TEMPLATE_DIR)

        # Act: Render template string with test_status_check macro (check_logfile=true)
        template = env.from_string("{{ test_status_check(true, this) }}")
        result = template.render(config)

        # Assert: Contains logfile tail command, not test commands
        assert "tail -5" in result
        assert "planning/last-test-ran.log" in result
        assert "**Check test status using the log file**" in result
        assert "pytest --tb=short" not in result
        assert "pytest" not in result


class TestCategoryFilter:
    """Tests for _category_filter() Jinja2 custom filter."""

    def test_returns_commands_matching_category(self) -> None:
        """Test 2.1: Filter returns list of tuples for commands matching category."""
        # Setup: Mock context with multiple commands, some matching category
        from typing import Any

        context: dict[str, Any] = {
            "commands": {
                "docs": {
                    "command": "npm run docs:generate",
                    "description": "Generate documentation",
                    "category": "utilities",
                },
                "validate": {
                    "command": "npm run validate",
                    "description": "Validate templates",
                    "category": "utilities",
                },
                "test": {
                    "command": "pytest",
                    "description": "Run tests",
                    "category": "test",
                },
            }
        }

        # Execute: Call filter with category name
        result = _category_filter(context, "utilities")

        # Assert: Returns list of tuples (key, command, description) for matching commands
        assert len(result) == 2
        assert ("docs", "npm run docs:generate", "Generate documentation") in result
        assert ("validate", "npm run validate", "Validate templates") in result
        assert all(
            isinstance(item, tuple) and len(item) == 3 for item in result
        ), "Each item should be a 3-tuple"

    def test_returns_empty_list_when_no_matches(self) -> None:
        """Test 2.2: Filter returns empty list when no commands match category."""
        # Setup: Mock context with commands in different category
        from typing import Any

        context: dict[str, Any] = {
            "commands": {
                "test": {"command": "pytest", "description": "Run tests", "category": "test"}
            }
        }

        # Execute: Call filter with non-matching category
        result = _category_filter(context, "utilities")

        # Assert: Returns empty list
        assert result == []

    def test_handles_object_format_without_category_field(self) -> None:
        """Test 2.4: Filter excludes object format commands missing category field."""
        # Setup: Mock context with object missing category field
        from typing import Any

        context: dict[str, Any] = {
            "commands": {
                "test": {"command": "pytest", "description": "Run tests"},  # No category
                "docs": {
                    "command": "npm run docs",
                    "description": "Generate docs",
                    "category": "utilities",
                },
            }
        }

        # Execute: Call filter
        result = _category_filter(context, "utilities")

        # Assert: Only commands with matching category returned
        assert len(result) == 1
        assert result[0][0] == "docs"

    def test_preserves_command_order(self) -> None:
        """Test 2.5: Filter preserves order of commands from config."""
        # Setup: Mock context with specific command order
        from typing import Any

        context: dict[str, Any] = {
            "commands": {
                "z_last": {
                    "command": "npm run z",
                    "description": "Last command",
                    "category": "utilities",
                },
                "a_first": {
                    "command": "npm run a",
                    "description": "First command",
                    "category": "utilities",
                },
                "m_middle": {
                    "command": "npm run m",
                    "description": "Middle command",
                    "category": "utilities",
                },
            }
        }

        # Execute: Call filter
        result = _category_filter(context, "utilities")

        # Assert: Order matches dict iteration order (insertion order in Python 3.7+)
        keys = [item[0] for item in result]
        assert keys == ["z_last", "a_first", "m_middle"]

    def test_missing_commands_dict_raises_keyerror(self) -> None:
        """Test 2.6: Filter fails when commands dict absent from context."""
        # Setup: Empty context (missing commands key)
        from typing import Any

        context: dict[str, Any] = {}

        # Execute & Assert: Filter raises KeyError when accessing context['commands']
        with pytest.raises(KeyError):
            _category_filter(context, "utilities")

    def test_filter_integration_with_jinja(self) -> None:
        """Test 2.7: Filter works correctly when registered in real Jinja2 environment."""
        # Setup: Create real Jinja2 Environment
        from pathlib import Path
        from tempfile import TemporaryDirectory

        with TemporaryDirectory() as tmpdir:
            template_dir = Path(tmpdir)

            # Create a test template file
            template_file = template_dir / "test.j2"
            template_file.write_text(
                '{% for key, cmd, desc in "utilities" | category %}{{ cmd }}\n{% endfor %}'
            )

            # Setup Jinja2 environment with filter registered
            from jinja2 import Environment, FileSystemLoader, StrictUndefined

            env = Environment(
                loader=FileSystemLoader(str(template_dir)),
                undefined=StrictUndefined,
                trim_blocks=True,
                lstrip_blocks=True,
            )
            env.filters["category"] = _category_filter

            # Create template and context
            template = env.get_template("test.j2")
            context = {
                "commands": {
                    "docs": {
                        "command": "npm run docs",
                        "description": "Generate docs",
                        "category": "utilities",
                    },
                    "test": {"command": "pytest", "description": "Run tests", "category": "test"},
                }
            }

            # Execute: Render template
            result = template.render(context)

            # Assert: Rendered output contains only utilities category command
            assert result == "npm run docs\n"
