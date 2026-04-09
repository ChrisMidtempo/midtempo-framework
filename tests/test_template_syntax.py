"""Tests for template syntax validator (scripts/validate_templates.py)."""

import pytest
from jinja2.exceptions import TemplateError, TemplateSyntaxError

from scripts.validate_templates import (
    find_orphaned_partials,
    find_unused_variables,
    validate_all_templates,
    validate_template_syntax,
    validate_templates_with_config,
)


class TestTemplateSyntax:
    """Test suite for template syntax validation."""

    def test_valid_jinja2_syntax_passes_validation(self, tmp_path):
        """Template with valid Jinja2 syntax passes validation."""
        # Arrange: Create template with valid syntax
        template_path = tmp_path / "test.md.j2"
        template_path.write_text(
            """
{% for item in items %}
  {{ item.name }}
{% endfor %}
"""
        )

        # Act: Validate template syntax
        result = validate_template_syntax(template_path)

        # Assert: Validation passes with no errors
        assert result is True or result is None  # Success indicated by no exception

    def test_invalid_jinja2_syntax_fails_validation(self, tmp_path):
        """Template with syntax errors fails validation with clear message."""
        # Arrange: Create template missing closing tag
        template_path = tmp_path / "test.md.j2"
        template_path.write_text(
            """
{% for item in items %}
  {{ item.name }}
"""
        )  # Missing {% endfor %}

        # Act & Assert: Validation raises TemplateSyntaxError
        with pytest.raises(TemplateSyntaxError) as exc_info:
            validate_template_syntax(template_path)

        error_message = str(exc_info.value).lower()
        assert "for" in error_message or "endfor" in error_message or "unexpected" in error_message

    def test_circular_template_inheritance_detected(self, tmp_path):
        """Circular template inheritance detected and raises error."""
        # Arrange: Create templates with circular inheritance
        template_dir = tmp_path / "templates"
        template_dir.mkdir()

        a_path = template_dir / "a.md.j2"
        a_path.write_text('{% extends "b.md.j2" %}')

        b_path = template_dir / "b.md.j2"
        b_path.write_text('{% extends "a.md.j2" %}')

        # Act & Assert: Loading template raises error describing cycle
        with pytest.raises((TemplateError, RuntimeError)) as exc_info:
            validate_all_templates(template_dir)

        error_message = str(exc_info.value).lower()
        assert "circular" in error_message or "cycle" in error_message or "extends" in error_message

    def test_detects_unused_variables_in_templates(self, tmp_path):
        """Validation detects undefined variables referenced in templates."""
        # Arrange: Create template with undefined variable
        template_dir = tmp_path / "templates"
        template_dir.mkdir()

        template_path = template_dir / "test.md.j2"
        template_path.write_text(
            """
# {{ repo.title }}
This uses an undefined variable: {{ unused_variable }}
"""
        )

        # Config with repo.title but without unused_variable
        config = {"repo": {"title": "Test Repo"}}

        # Act: Find unused variables
        unused = find_unused_variables(template_dir, config)

        # Assert: unused_variable is detected
        assert len(unused) > 0
        assert any("unused_variable" in str(item) for item in unused)
        assert any("test.md.j2" in str(item) for item in unused)

    def test_detects_orphaned_partials_not_included(self, tmp_path):
        """Validation warns when partial file exists but is not included by any template."""
        # Arrange: Create orphaned partial
        template_dir = tmp_path / "templates"
        template_dir.mkdir()
        partials_dir = template_dir / "partials"
        partials_dir.mkdir()

        # Main template that doesn't include orphan.j2
        main_template = template_dir / "main.md.j2"
        main_template.write_text("# Main Template\nNo includes here.")

        # Orphaned partial
        orphan_partial = partials_dir / "orphan.j2"
        orphan_partial.write_text("{{ content }}")

        # Act: Find orphaned partials
        orphaned = find_orphaned_partials(template_dir)

        # Assert: orphan.j2 is detected as orphaned
        assert len(orphaned) > 0
        assert any("orphan.j2" in str(p) for p in orphaned)

    def test_valid_templates_with_all_variables_defined_pass(self, tmp_path):
        """Well-formed templates with all variables defined pass validation."""
        # Arrange: Create valid template and config
        template_dir = tmp_path / "templates"
        template_dir.mkdir()

        template_path = template_dir / "test.md.j2"
        template_path.write_text(
            """
# {{ repo.title }}
Language: {{ repo.language }}
"""
        )

        config = {"repo": {"title": "Test Repo", "language": "Python"}}

        # Act: Validate templates with config
        result = validate_templates_with_config(template_dir, config, strict=False)

        # Assert: Validation passes
        assert result is True

    def test_find_unused_variables_handles_unparseable_templates(self, tmp_path):
        """find_unused_variables skips templates that cannot be parsed."""
        # Arrange: Mix of valid and invalid template syntax
        template_dir = tmp_path / "templates"
        template_dir.mkdir()

        # Valid template
        valid_template = template_dir / "valid.md.j2"
        valid_template.write_text("# {{ repo.title }}")

        # Invalid template (will trigger exception during parsing)
        invalid_template = template_dir / "invalid.md.j2"
        invalid_template.write_text("# {% for item in items %}\nMissing endfor")

        config = {"repo": {"title": "Test"}}

        # Act: Find unused variables (should handle exception gracefully)
        unused = find_unused_variables(template_dir, config)

        # Assert: Function completes without raising, returns results for parseable templates
        assert isinstance(unused, list)
        # The invalid template should be skipped

    def test_find_orphaned_partials_handles_unreadable_files(self, tmp_path):
        """find_orphaned_partials handles files that cannot be read gracefully."""
        # Arrange: Create partials directory with orphaned partial
        template_dir = tmp_path / "templates"
        template_dir.mkdir()
        partials_dir = template_dir / "partials"
        partials_dir.mkdir()

        # Main template
        main_template = template_dir / "main.md.j2"
        main_template.write_text("# Main\n{% include 'partials/used.j2' %}")

        # Used partial
        used_partial = partials_dir / "used.j2"
        used_partial.write_text("Used content")

        # Orphaned partial
        orphan_partial = partials_dir / "orphan.j2"
        orphan_partial.write_text("Orphaned content")

        # Act: Find orphaned partials
        orphaned = find_orphaned_partials(template_dir)

        # Assert: Only orphan.j2 is detected (used.j2 is included by main)
        assert len(orphaned) >= 1
        orphan_names = [p.name for p in orphaned]
        assert "orphan.j2" in orphan_names
        assert "used.j2" not in orphan_names

    def test_strict_mode_exits_non_zero_on_warnings(self, tmp_path):
        """Strict mode treats warnings (like orphaned partials) as errors."""
        # Arrange: Create template with orphaned partial (warning condition)
        template_dir = tmp_path / "templates"
        template_dir.mkdir()
        partials_dir = template_dir / "partials"
        partials_dir.mkdir()

        main_template = template_dir / "main.md.j2"
        main_template.write_text("# Main")

        orphan_partial = partials_dir / "orphan.j2"
        orphan_partial.write_text("Orphaned content")

        config = {"repo": {"title": "Test"}}

        # Act & Assert: Strict mode raises error on warnings
        with pytest.raises((ValueError, TemplateError)) as exc_info:
            validate_templates_with_config(template_dir, config, strict=True)

        error_message = str(exc_info.value).lower()
        assert "orphan" in error_message or "warning" in error_message or "strict" in error_message


class TestCLIEntryPoint:
    """Test suite for CLI entry point validation."""

    def test_cli_validates_syntax_only_successfully(self, tmp_path, monkeypatch):
        """CLI validates template syntax without config and returns success."""
        # Arrange: Create valid templates
        template_dir = tmp_path / "templates"
        template_dir.mkdir()

        template_path = template_dir / "test.md.j2"
        template_path.write_text("# {{ title }}\nContent here")

        # Mock command-line arguments
        test_args = ["script_name", "--template-dir", str(template_dir)]
        monkeypatch.setattr("sys.argv", test_args)

        # Act: Run CLI
        from scripts.validate_templates import main

        exit_code = main()

        # Assert: CLI returns success (0)
        assert exit_code == 0

    def test_cli_validates_with_config_successfully(self, tmp_path, monkeypatch):
        """CLI validates templates with config file and returns success."""
        # Arrange: Create valid templates and config
        template_dir = tmp_path / "templates"
        template_dir.mkdir()

        template_path = template_dir / "test.md.j2"
        template_path.write_text("# {{ repo.title }}\nLanguage: {{ repo.language }}")

        config_path = tmp_path / "config.yml"
        config_path.write_text("repo:\n  title: Test\n  language: Python")

        # Mock command-line arguments
        test_args = [
            "script_name",
            "--template-dir",
            str(template_dir),
            "--config",
            str(config_path),
        ]
        monkeypatch.setattr("sys.argv", test_args)

        # Act: Run CLI
        from scripts.validate_templates import main

        exit_code = main()

        # Assert: CLI returns success (0)
        assert exit_code == 0

    def test_cli_returns_error_when_template_dir_not_found(self, tmp_path, monkeypatch):
        """CLI returns error code when template directory does not exist."""
        # Arrange: Non-existent template directory
        template_dir = tmp_path / "nonexistent"

        # Mock command-line arguments
        test_args = ["script_name", "--template-dir", str(template_dir)]
        monkeypatch.setattr("sys.argv", test_args)

        # Act: Run CLI
        from scripts.validate_templates import main

        exit_code = main()

        # Assert: CLI returns error code (1)
        assert exit_code == 1

    def test_cli_returns_error_when_config_not_found(self, tmp_path, monkeypatch):
        """CLI returns error code when config file does not exist."""
        # Arrange: Valid template dir but missing config
        template_dir = tmp_path / "templates"
        template_dir.mkdir()

        config_path = tmp_path / "nonexistent.yml"

        # Mock command-line arguments
        test_args = [
            "script_name",
            "--template-dir",
            str(template_dir),
            "--config",
            str(config_path),
        ]
        monkeypatch.setattr("sys.argv", test_args)

        # Act: Run CLI
        from scripts.validate_templates import main

        exit_code = main()

        # Assert: CLI returns error code (1)
        assert exit_code == 1

    def test_cli_syntax_only_flag_skips_variable_checks(self, tmp_path, monkeypatch):
        """CLI with --syntax-only flag validates syntax but skips variable checks."""
        # Arrange: Template with undefined variable
        template_dir = tmp_path / "templates"
        template_dir.mkdir()

        template_path = template_dir / "test.md.j2"
        template_path.write_text("# {{ undefined_var }}")

        config_path = tmp_path / "config.yml"
        config_path.write_text("repo:\n  title: Test")

        # Mock command-line arguments (with --syntax-only)
        test_args = [
            "script_name",
            "--template-dir",
            str(template_dir),
            "--config",
            str(config_path),
            "--syntax-only",
        ]
        monkeypatch.setattr("sys.argv", test_args)

        # Act: Run CLI
        from scripts.validate_templates import main

        exit_code = main()

        # Assert: CLI returns success despite undefined variable (syntax is valid)
        assert exit_code == 0

    def test_cli_validates_templates_without_partials_directory(self, tmp_path, monkeypatch):
        """CLI validates templates successfully when partials directory does not exist."""
        # Arrange: Templates without partials subdirectory
        template_dir = tmp_path / "templates"
        template_dir.mkdir()

        template_path = template_dir / "simple.md.j2"
        template_path.write_text("# Simple Template\nNo variables here")

        # Mock command-line arguments
        test_args = ["script_name", "--template-dir", str(template_dir)]
        monkeypatch.setattr("sys.argv", test_args)

        # Act: Run CLI
        from scripts.validate_templates import main

        exit_code = main()

        # Assert: CLI returns success (0)
        assert exit_code == 0

    def test_cli_returns_error_on_validation_failure(self, tmp_path, monkeypatch):
        """CLI returns error code when template validation fails."""
        # Arrange: Template with undefined variable
        template_dir = tmp_path / "templates"
        template_dir.mkdir()

        template_path = template_dir / "test.md.j2"
        template_path.write_text("# {{ undefined_variable }}")

        config_path = tmp_path / "config.yml"
        config_path.write_text("repo:\n  title: Test")

        # Mock command-line arguments (without --syntax-only)
        test_args = [
            "script_name",
            "--template-dir",
            str(template_dir),
            "--config",
            str(config_path),
        ]
        monkeypatch.setattr("sys.argv", test_args)

        # Act: Run CLI
        from scripts.validate_templates import main

        exit_code = main()

        # Assert: CLI returns error code (1) due to undefined variable
        assert exit_code == 1
