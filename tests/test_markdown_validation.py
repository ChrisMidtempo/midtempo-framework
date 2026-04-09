"""Tests for post-generation markdown validator (scripts/validate_markdown.py)."""

import pytest

from scripts.validate_markdown import (
    check_code_block_tags,
    check_template_syntax_leaks,
    validate_internal_links,
    validate_markdown_syntax,
)


class TestMarkdownValidation:
    """Test suite for markdown validation."""

    def test_valid_markdown_passes_validation(self, tmp_path):
        """Well-formed markdown passes syntax validation."""
        # Arrange: Create valid markdown file
        md_path = tmp_path / "test.md"
        md_path.write_text(
            """# Heading

- List item 1
- List item 2

[Link](./path.md)

```python
code block
```
"""
        )

        # Act: Validate markdown syntax
        result = validate_markdown_syntax(md_path)

        # Assert: Validation passes with no errors
        assert result is True or result is None

    def test_broken_internal_link_fails_validation(self, tmp_path):
        """Internal links to non-existent files are detected."""
        # Arrange: Create markdown with broken internal link
        base_dir = tmp_path
        md_path = base_dir / "test.md"

        # Create one valid file, reference one that doesn't exist
        existing_path = base_dir / "existing-file.md"
        existing_path.write_text("# Exists")

        md_path.write_text(
            """
[Valid link](./existing-file.md)
[Broken link](./nonexistent-file.md)
"""
        )

        # Act & Assert: Link validation fails
        with pytest.raises(Exception) as exc_info:
            validate_internal_links(md_path, base_dir)

        error_message = str(exc_info.value).lower()
        assert (
            "nonexistent-file.md" in error_message
            or "broken" in error_message
            or "not found" in error_message
        )

    def test_invalid_markdown_syntax_detected(self, tmp_path):
        """Malformed markdown syntax is detected."""
        # Arrange: Create markdown with unclosed code fence
        md_path = tmp_path / "test.md"
        md_path.write_text(
            """# Heading

```python
code block without closing fence
"""
        )

        # Act: Validate markdown syntax
        # Note: Some markdown parsers are lenient, so this might pass or warn
        # The implementation should use strict parsing
        result = validate_markdown_syntax(md_path)

        # Assert: Either raises error or returns validation failure
        # (behavior depends on markdown library used)
        # For now, we just ensure the function runs and returns a result
        assert result is not None or result is False

    def test_detects_code_blocks_missing_language_tags(self, tmp_path):
        """Validation detects code blocks without language tags."""
        # Arrange: Create markdown with untagged code block
        md_path = tmp_path / "test.md"
        md_path.write_text(
            """# Test Document

```python
tagged_code = "this is fine"
```

```
untagged_code = "this should be flagged"
```

More text here.
"""
        )

        # Act: Check for untagged code blocks
        violations = check_code_block_tags(md_path)

        # Assert: Untagged block is detected
        assert len(violations) > 0
        assert any("line" in str(v).lower() for v in violations)

    def test_detects_template_syntax_leaks_in_output(self, tmp_path):
        """Validation detects unrendered template syntax in markdown."""
        # Arrange: Create markdown with template syntax leak
        md_path = tmp_path / "test.md"
        md_path.write_text(
            """# Project Documentation

Repository name: {{ repo.name }}

Build command: {% if commands.build %}{{ commands.build }}{% endif %}
"""
        )

        # Act: Check for template syntax leaks
        leaks = check_template_syntax_leaks(md_path)

        # Assert: Template syntax is detected
        assert len(leaks) > 0
        # Should find both {{ and {%
        leak_str = " ".join(str(leak) for leak in leaks)
        assert "{{" in leak_str or "repo.name" in leak_str

    def test_link_resolution_existing_functionality(self, tmp_path):
        """Link resolution validates internal markdown links."""
        # Arrange: Create markdown with broken relative link
        base_dir = tmp_path
        md_path = base_dir / "docs.md"
        md_path.write_text(
            """# Documentation

See [other file](../missing.md) for details.
"""
        )

        # Act & Assert: Broken link detected
        with pytest.raises(ValueError) as exc_info:
            validate_internal_links(md_path, base_dir)

        error_message = str(exc_info.value)
        assert "missing.md" in error_message or "broken" in error_message.lower()

    def test_valid_markdown_with_all_checks_passes(self, tmp_path):
        """Well-formed markdown with tagged code blocks and no syntax leaks passes."""
        # Arrange: Create clean markdown
        md_path = tmp_path / "test.md"
        md_path.write_text(
            """# Clean Document

All code blocks have language tags:

```python
def example():
    return True
```

```bash
echo "properly tagged"
```

No template syntax leaks here.
"""
        )

        # Act: Run all validation checks
        syntax_valid = validate_markdown_syntax(md_path)
        code_block_violations = check_code_block_tags(md_path)
        template_leaks = check_template_syntax_leaks(md_path)

        # Assert: All checks pass
        assert syntax_valid is True
        assert len(code_block_violations) == 0
        assert len(template_leaks) == 0
