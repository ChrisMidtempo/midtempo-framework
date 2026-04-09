"""Integration tests for end-to-end documentation generation."""

import pytest
import yaml

from scripts.generate_docs import generate_documentation
from tests.helpers.config_factory import create_standard_config


@pytest.mark.integration
class TestIntegration:
    """Test suite for end-to-end generation workflow."""

    def test_end_to_end_generation_typescript_ui_db(self, tmp_path):
        """Complete generation workflow for TypeScript+UI+DB repository."""
        # Arrange: Create TypeScript+UI+DB config
        config_path = tmp_path / "config.yml"
        config_data = create_standard_config("typescript", {"hasUI", "hasDB"})
        config_data["name"] = "example-app"
        config_data["repo"]["title"] = "example.app"
        # Add db_query command (repo-specific, not in commands/typescript.yml)
        config_data["commands"]["db_query"] = {
            "command": "npm run db:query",
            "description": "Run database query",
            "category": "db",
        }
        config_path.write_text(yaml.dump(config_data))

        output_dir = tmp_path / "output"
        output_dir.mkdir()

        # Act: Run full generation pipeline
        result = generate_documentation(config_path, output_dir)

        # Assert: Generation succeeds and produces expected output
        assert result is True
        assert output_dir.exists()
        # Generated files should exist (specific files depend on templates)
        generated_files = list(output_dir.rglob("*.md"))
        assert len(generated_files) > 0

        # Check that at least some files contain language-specific content
        language_specific_count = 0
        for md_file in generated_files:
            content = md_file.read_text()
            # Count files with TypeScript-specific content
            if "typescript" in content.lower() or "npm" in content.lower():
                language_specific_count += 1

        # At least some files should have language-specific content (not all files need it)
        assert language_specific_count > 0, "No files contain TypeScript/npm-specific content"

    def test_end_to_end_generation_python_db_only(self, tmp_path):
        """Generation workflow for Python+DB repository excludes UI sections."""
        # Arrange: Create Python+DB config (no UI)
        config_path = tmp_path / "config.yml"
        config_data = create_standard_config("python", {"hasDB"})
        config_data["name"] = "example-service"
        config_data["repo"]["title"] = "example.service"
        # Add db_query command (repo-specific, not in commands/python.yml)
        config_data["commands"]["db_query"] = {
            "command": "python -m app.db.query",
            "description": "Run database query",
            "category": "db",
        }
        config_path.write_text(yaml.dump(config_data))

        output_dir = tmp_path / "output"
        output_dir.mkdir()

        # Act: Run full generation pipeline
        result = generate_documentation(config_path, output_dir)

        # Assert: Generation succeeds with Python-specific content
        assert result is True
        generated_files = list(output_dir.rglob("*.md"))
        assert len(generated_files) > 0

        # Check that at least some files contain Python-specific content
        language_specific_count = 0
        for md_file in generated_files:
            content = md_file.read_text()
            # Count files with Python-specific content
            if "python" in content.lower() or "pytest" in content.lower():
                language_specific_count += 1

        # At least some files should have language-specific content (not all files need it)
        assert language_specific_count > 0, "No files contain Python/pytest-specific content"

    def test_idempotent_generation(self, tmp_path):
        """Running generation twice with same config produces identical output."""
        # Arrange: Create config
        config_path = tmp_path / "config.yml"
        config_data = create_standard_config("typescript", {"hasUI"})
        config_data["name"] = "example-app"
        config_data["repo"]["title"] = "example.app"
        config_path.write_text(yaml.dump(config_data))

        output_dir_1 = tmp_path / "output1"
        output_dir_1.mkdir()
        output_dir_2 = tmp_path / "output2"
        output_dir_2.mkdir()

        # Act: Run generation twice
        result1 = generate_documentation(config_path, output_dir_1)
        result2 = generate_documentation(config_path, output_dir_2)

        # Assert: Both runs succeed
        assert result1 is True
        assert result2 is True

        # Compare outputs are identical
        files1 = sorted(output_dir_1.rglob("*.md"))
        files2 = sorted(output_dir_2.rglob("*.md"))

        assert len(files1) == len(files2)
        assert len(files1) > 0

        for file1, file2 in zip(files1, files2, strict=False):
            content1 = file1.read_text()
            content2 = file2.read_text()
            assert content1 == content2, f"Files differ: {file1.name} vs {file2.name}"


@pytest.mark.integration
class TestNamespacedGeneration:
    """Test suite for namespaced output structure (Module 4)."""

    def test_full_generation_to_namespaced_directory(self, tmp_path):
        """Verify that complete generation process outputs all files to generated/{name}/ with correct path remapping."""
        # Arrange - create template files in all directories
        template_dir = tmp_path / "templates"
        (template_dir / "instructions").mkdir(parents=True)
        (template_dir / "rules").mkdir(parents=True)
        (template_dir / "templates").mkdir(parents=True)
        (template_dir / "agents").mkdir(parents=True)

        # Create minimal templates
        (template_dir / "instructions" / "test.md.j2").write_text("# Instructions\n{{ name }}")
        (template_dir / "rules" / "test.md.j2").write_text("# Rules\n{{ name }}")
        (template_dir / "templates" / "test.md.j2").write_text("# Template\n{{ name }}")
        (template_dir / "agents" / "test.md.j2").write_text("# Agent\n{{ name }}")

        # Create config
        config_path = tmp_path / "config.yml"
        config_data = create_standard_config("python")
        config_data["name"] = "example"
        config_data["repo"]["title"] = "example.app"
        config_path.write_text(yaml.dump(config_data))

        output_base = tmp_path / "output"

        # Act - would normally use generate_documentation, but we need to test the orchestrator
        # For Phase 2, we're just verifying the test fails correctly
        from scripts.generate_docs import generate_documentation_with_timing

        generate_documentation_with_timing(config_path, output_base, template_dir)

        # Assert - files at correct locations in agents/example/ subdirectory
        namespaced_dir = output_base / "agents" / "example"
        assert (namespaced_dir / "test.md").exists()  # agents/test.md → test.md
        assert (namespaced_dir / "instructions" / "test.md").exists()
        assert (namespaced_dir / "rules" / "test.md").exists()
        assert (namespaced_dir / "templates" / "test.md").exists()

    def test_config_file_created_after_template_generation(self, tmp_path):
        """Verify that config file with metadata is created at correct location after templates rendered."""
        # Arrange - minimal setup
        template_dir = tmp_path / "templates"
        template_dir.mkdir()
        (template_dir / "test.md.j2").write_text("# {{ name }}")

        config_path = tmp_path / "config.yml"
        config_data = create_standard_config("python")
        config_data["name"] = "example"
        config_data["repo"]["title"] = "example.app"
        config_path.write_text(yaml.dump(config_data))

        output_base = tmp_path / "output"

        # Act
        from scripts.generate_docs import generate_documentation_with_timing

        generate_documentation_with_timing(config_path, output_base, template_dir)

        # Assert - input config file updated with metadata
        assert config_path.exists()
        parsed = yaml.safe_load(config_path.read_text())
        assert "metadata" in parsed
        assert "generated_at" in parsed["metadata"]
        assert "framework_version" in parsed["metadata"]

        # Assert - no separate output config file created
        output_config = output_base / "example-agents.yml"
        assert not output_config.exists()

    def test_templates_directory_no_longer_skipped(self, tmp_path):
        """Verify that templates in templates/ directory are now processed (not skipped) and output to planning/."""
        # Arrange
        template_dir = tmp_path / "templates"
        (template_dir / "templates").mkdir(parents=True)
        (template_dir / "templates" / "design.md.j2").write_text("# Design\n{{ name }}")

        config_path = tmp_path / "config.yml"
        config_data = {
            "name": "test-config",
            "repo": {"title": "test.app", "language": {"python": "all"}},
            "capabilities": {"hasUI": False, "hasDB": False},
            "commands": {
                "test": {"command": "pytest", "description": "Run tests", "category": "test"},
                "test_unit": {
                    "command": "pytest tests/unit/",
                    "description": "Run unit tests",
                    "category": "test",
                },
                "test_integration": {
                    "command": "pytest tests/integration/",
                    "description": "Run integration tests",
                    "category": "test",
                },
                "test_coverage": {
                    "command": "pytest --cov",
                    "description": "Run tests with coverage",
                    "category": "test",
                },
                "lint": {
                    "command": "ruff check",
                    "description": "Run linter",
                    "category": "quality",
                },
                "typecheck": {
                    "command": "mypy",
                    "description": "Run type checker",
                    "category": "quality",
                },
                "test_e2e": {
                    "command": "pytest tests/e2e/",
                    "description": "Run e2e tests",
                    "category": "test",
                },
                "test_e2e_ui": {
                    "command": "pytest tests/e2e/ --headed",
                    "description": "Run e2e tests with UI",
                    "category": "test",
                },
                "test_e2e_headed": {
                    "command": "pytest tests/e2e/ --headed",
                    "description": "Run e2e tests headed",
                    "category": "test",
                },
                "test_e2e_codegen": {
                    "command": "pytest --codegen",
                    "description": "Run e2e tests with codegen",
                    "category": "test",
                },
                "docs": {
                    "command": "python -m scripts.generate_docs",
                    "description": "Generate docs",
                    "category": "docs",
                },
                "dev": {
                    "command": "python -m app.main",
                    "description": "Run dev server",
                    "category": "dev",
                },
                "typedoc": {
                    "command": "python -m pydoc",
                    "description": "Generate type docs",
                    "category": "docs",
                },
                "simulate": {
                    "command": "python -m app.simulate",
                    "description": "Run simulation",
                    "category": "dev",
                },
                "db_query": {
                    "command": "python -m app.db.query",
                    "description": "Run database query",
                    "category": "dev",
                },
            },
        }
        config_path.write_text(yaml.dump(config_data))

        output_base = tmp_path / "output"

        # Act
        from scripts.generate_docs import generate_documentation_with_timing

        generate_documentation_with_timing(config_path, output_base, template_dir)

        # Assert - file created in agents/test-config/templates/ subdirectory
        namespaced_dir = output_base / "agents" / "test-config"
        template_file = namespaced_dir / "templates" / "design.md"
        assert template_file.exists()
        assert "Design" in template_file.read_text()

    def test_generated_config_is_valid_input_for_regeneration(self, tmp_path):
        """Verify that generated config file can be used as input for a second generation run (config-as-source-of-truth)."""
        # Arrange - first generation
        template_dir = tmp_path / "templates"
        template_dir.mkdir()
        (template_dir / "test.md.j2").write_text("# {{ name }}")

        config_path_1 = tmp_path / "config1.yml"
        config_data = create_standard_config("python")
        config_data["name"] = "example"
        config_data["repo"]["title"] = "example.app"
        config_path_1.write_text(yaml.dump(config_data))

        output_base_1 = tmp_path / "output1"

        # Act - first generation
        from scripts.generate_docs import generate_documentation_with_timing

        generate_documentation_with_timing(config_path_1, output_base_1, template_dir)

        # Verify input config now has metadata
        parsed = yaml.safe_load(config_path_1.read_text())
        assert "metadata" in parsed

        # Act - second generation using same config (now with metadata)
        output_base_2 = tmp_path / "output2"
        result = generate_documentation_with_timing(config_path_1, output_base_2, template_dir)

        # Assert - second generation succeeds
        assert result["file_count"] > 0
        # Input config still has metadata (updated again)
        parsed_2 = yaml.safe_load(config_path_1.read_text())
        assert "metadata" in parsed_2
        # No output config file created
        assert not (output_base_2 / "example-agents.yml").exists()

    def test_multiple_configs_generate_to_separate_namespaces(self, tmp_path):
        """Verify that multiple configs with different names generate to separate directories without interference."""
        # Arrange - template
        template_dir = tmp_path / "templates"
        template_dir.mkdir()
        (template_dir / "test.md.j2").write_text("# {{ name }}")

        # Config A
        config_path_a = tmp_path / "config_a.yml"
        config_a = create_standard_config("python")
        config_a["name"] = "config-a"
        config_a["repo"]["title"] = "a.app"
        config_path_a.write_text(yaml.dump(config_a))

        # Config B
        config_path_b = tmp_path / "config_b.yml"
        config_b = create_standard_config("python")
        config_b["name"] = "config-b"
        config_b["repo"]["title"] = "b.app"
        config_path_b.write_text(yaml.dump(config_b))

        # User controls isolation by choosing separate output directories
        output_dir_a = tmp_path / "output-a"
        output_dir_b = tmp_path / "output-b"

        # Act - generate both to separate directories
        from scripts.generate_docs import generate_documentation_with_timing

        generate_documentation_with_timing(config_path_a, output_dir_a, template_dir)
        generate_documentation_with_timing(config_path_b, output_dir_b, template_dir)

        # Assert - each output directory exists
        assert output_dir_a.exists()
        assert output_dir_b.exists()

        # Assert - input configs updated with metadata
        config_a_parsed = yaml.safe_load(config_path_a.read_text())
        config_b_parsed = yaml.safe_load(config_path_b.read_text())

        # Verify each config has metadata
        assert "metadata" in config_a_parsed
        assert "metadata" in config_b_parsed

        # Verify no separate output config files created
        assert not (output_dir_a / "config-a-agents.yml").exists()
        assert not (output_dir_b / "config-b-agents.yml").exists()

        # Verify no cross-contamination

        assert config_a_parsed["name"] == "config-a"
        assert config_b_parsed["name"] == "config-b"

    def test_name_field_validation_prevents_path_traversal(self, tmp_path):
        """Verify that config schema validation rejects invalid name values that could cause path traversal."""
        # Arrange - configs with invalid names
        from scripts.validate_config import validate_config_with_enhanced_errors

        config_path = tmp_path / "config.yml"

        # Base config with required fields
        base_config = """repo:
  name: "test"
  language: "python"
capabilities:
  hasUI: false
  hasDB: false
commands:
  test: "pytest"
  lint: "ruff check"
"""

        # Test 1: Path traversal attempt
        config_path.write_text('name: "../escape"\n' + base_config)

        # Act & Assert
        with pytest.raises(ValueError):
            validate_config_with_enhanced_errors(config_path)

        # Test 2: Absolute path
        config_path.write_text('name: "/absolute/path"\n' + base_config)

        with pytest.raises(ValueError):
            validate_config_with_enhanced_errors(config_path)

        # Test 3: Slash in name
        config_path.write_text('name: "has/slash"\n' + base_config)

        with pytest.raises(ValueError):
            validate_config_with_enhanced_errors(config_path)

    def test_auto_prefix_agents_folder_for_non_framework_projects(self, tmp_path):
        """Verify that generation auto-prefixes output_dir with 'agents/[name]/' when name != 'midtempo.framework'."""
        # Arrange
        template_dir = tmp_path / "templates"
        template_dir.mkdir()
        (template_dir / "test.md.j2").write_text("# Test\n{{ name }}")

        config_path = tmp_path / "config.yml"
        config_data = create_standard_config("python")
        config_data["name"] = "my-project"
        config_data["repo"]["title"] = "my.project"
        config_path.write_text(yaml.dump(config_data))

        # User provides output_dir without agents/ prefix
        output_base = tmp_path / "output"

        # Act
        from scripts.generate_docs import generate_documentation_with_timing

        generate_documentation_with_timing(config_path, output_base, template_dir)

        # Assert: Files created in agents/my-project/ subdirectory
        expected_output_dir = output_base / "agents" / "my-project"
        assert expected_output_dir.exists()
        assert (expected_output_dir / "test.md").exists()

    def test_no_auto_prefix_for_agentic_framework_itself(self, tmp_path):
        """Verify that generation does NOT auto-prefix when name == 'midtempo-framework'."""
        # Arrange
        template_dir = tmp_path / "templates"
        template_dir.mkdir()
        (template_dir / "test.md.j2").write_text("# Framework\n{{ name }}")

        config_path = tmp_path / "config.yml"
        config_data = create_standard_config("python")
        config_data["name"] = "midtempo-framework"
        config_data["repo"]["title"] = "Midtempo Framework"
        config_path.write_text(yaml.dump(config_data))

        # User provides output_dir
        output_base = tmp_path / "framework-output"

        # Act
        from scripts.generate_docs import generate_documentation_with_timing

        generate_documentation_with_timing(config_path, output_base, template_dir)

        # Assert: Files created in midtempo-framework/ subdirectory (no agents/ prefix)
        assert (output_base / "midtempo-framework" / "test.md").exists()
        # Should NOT create agents/ subdirectory
        agents_dir = output_base / "agents"
        assert not agents_dir.exists()
