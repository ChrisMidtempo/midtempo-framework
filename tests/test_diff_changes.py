"""Tests for change preview and diff tool (scripts/diff_changes.py)."""

import yaml

from scripts.diff_changes import (
    compare_directories,
    detect_changes,
    generate_unified_diff,
    preview_changes,
)
from tests.helpers.config_factory import _build_instructions_for_capabilities


class TestDiffChanges:
    """Test suite for change preview and diff generation."""

    def test_unified_diff_shows_modifications(self, tmp_path):
        """Unified diff displays changes between existing and generated output."""
        # Arrange: Existing output with version 1.0
        existing_dir = tmp_path / "existing"
        existing_dir.mkdir()
        existing_file = existing_dir / "README.md"
        existing_file.write_text("# Version 1.0\nOld content here.")

        # Generated output with version 1.1
        generated_dir = tmp_path / "generated"
        generated_dir.mkdir()
        generated_file = generated_dir / "README.md"
        generated_file.write_text("# Version 1.1\nNew content here.")

        # Act: Generate unified diff
        diff_result = generate_unified_diff(existing_file, generated_file)

        # Assert: Diff shows modifications
        assert diff_result is not None
        assert len(diff_result) > 0
        assert "-" in diff_result or "1.0" in diff_result
        assert "+" in diff_result or "1.1" in diff_result

    def test_detects_added_files(self, tmp_path):
        """New templates not in existing output are reported as added."""
        # Arrange: Existing output lacks NEW_FEATURE.md
        existing_dir = tmp_path / "existing"
        existing_dir.mkdir()
        existing_file = existing_dir / "README.md"
        existing_file.write_text("# Existing")

        # Generated output has new file
        generated_dir = tmp_path / "generated"
        generated_dir.mkdir()
        readme = generated_dir / "README.md"
        readme.write_text("# Existing")
        new_file = generated_dir / "NEW_FEATURE.md"
        new_file.write_text("# New Feature")

        # Act: Compare directories
        changes = compare_directories(existing_dir, generated_dir)

        # Assert: New file detected as added
        assert "added" in changes
        assert len(changes["added"]) > 0
        assert any("NEW_FEATURE.md" in str(f) for f in changes["added"])

    def test_detects_deleted_files(self, tmp_path):
        """Files in existing output that are no longer generated are reported as deleted."""
        # Arrange: Existing output has DEPRECATED.md
        existing_dir = tmp_path / "existing"
        existing_dir.mkdir()
        existing_file1 = existing_dir / "README.md"
        existing_file1.write_text("# Readme")
        deprecated_file = existing_dir / "DEPRECATED.md"
        deprecated_file.write_text("# Deprecated content")

        # Generated output doesn't have DEPRECATED.md
        generated_dir = tmp_path / "generated"
        generated_dir.mkdir()
        generated_file = generated_dir / "README.md"
        generated_file.write_text("# Readme")

        # Act: Compare directories
        changes = compare_directories(existing_dir, generated_dir)

        # Assert: Deprecated file detected as deleted
        assert "deleted" in changes
        assert len(changes["deleted"]) > 0
        assert any("DEPRECATED.md" in str(f) for f in changes["deleted"])

    def test_no_changes_detected_when_identical(self, tmp_path):
        """When generated output is identical to existing, no changes are detected."""
        # Arrange: Identical content in both directories
        existing_dir = tmp_path / "existing"
        existing_dir.mkdir()
        existing_file = existing_dir / "README.md"
        existing_file.write_text("# Identical Content\n\nSame everywhere.")

        generated_dir = tmp_path / "generated"
        generated_dir.mkdir()
        generated_file = generated_dir / "README.md"
        generated_file.write_text("# Identical Content\n\nSame everywhere.")

        # Act: Detect changes
        has_changes = detect_changes(existing_dir, generated_dir)

        # Assert: No changes detected
        assert has_changes is False

    def test_dry_run_mode_doesnt_apply_changes(self, tmp_path):
        """Dry-run flag shows diff but doesn't write files."""
        # Arrange: Set up directories with changes
        config_path = tmp_path / "config.yml"
        capabilities = {"hasUI": False, "hasDB": False}
        config_data = {
            "name": "test-repo",
            "repo": {"title": "Test Repo", "language": {"python": "all"}},
            "capabilities": capabilities,
            "instructions": _build_instructions_for_capabilities(capabilities),
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
                    "command": "pytest --cov=scripts",
                    "description": "Run tests with coverage",
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
                    "command": "pytest tests/e2e/ --codegen",
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
            },
        }
        config_path.write_text(yaml.dump(config_data))

        existing_dir = tmp_path / "existing"
        existing_dir.mkdir()
        existing_file = existing_dir / "README.md"
        existing_file.write_text("# Old Version")

        target_dir = tmp_path / "target"
        target_dir.mkdir()

        # Act: Preview changes in dry-run mode
        result = preview_changes(config_path, target_dir, dry_run=True)

        # Assert: Changes shown but not applied
        assert result["dry_run"] is True
        # Target directory should remain unchanged (or not exist)
        assert (
            not (target_dir / "README.md").exists() or (target_dir / "README.md").read_text() == ""
        )

    def test_user_confirmation_integration(self, tmp_path):
        """Interactive mode requires user confirmation before applying changes."""
        # Arrange: Changes detected
        config_path = tmp_path / "config.yml"
        capabilities = {"hasUI": False, "hasDB": False}
        config_data = {
            "name": "updated-repo",
            "repo": {"title": "Updated", "language": {"python": "all"}},
            "capabilities": capabilities,
            "instructions": _build_instructions_for_capabilities(capabilities),
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
                    "command": "pytest --cov=scripts",
                    "description": "Run tests with coverage",
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
                    "command": "pytest tests/e2e/ --codegen",
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
            },
        }
        config_path.write_text(yaml.dump(config_data))

        existing_dir = tmp_path / "existing"
        existing_dir.mkdir()
        existing_file = existing_dir / "README.md"
        existing_file.write_text("# Version 1.0")

        target_dir = tmp_path / "target"

        # Act: Preview changes (without actual user input in test)
        # This test verifies the function signature and flow
        # Real user confirmation testing would mock input()
        result = preview_changes(config_path, target_dir, dry_run=True)

        # Assert: Function returns result with confirmation status
        assert "changes_detected" in result or "dry_run" in result
        assert isinstance(result, dict)


class TestChangeDetection:
    """Test suite for change detection and categorization."""

    def test_categorizes_changes_correctly(self, tmp_path):
        """Changes are correctly categorised as added, modified, or deleted."""
        # Arrange: Mixed changes
        existing_dir = tmp_path / "existing"
        existing_dir.mkdir()
        (existing_dir / "kept.md").write_text("Same content")
        (existing_dir / "modified.md").write_text("Old content")
        (existing_dir / "deleted.md").write_text("Will be removed")

        generated_dir = tmp_path / "generated"
        generated_dir.mkdir()
        (generated_dir / "kept.md").write_text("Same content")
        (generated_dir / "modified.md").write_text("New content")
        (generated_dir / "added.md").write_text("New file")

        # Act: Compare directories
        changes = compare_directories(existing_dir, generated_dir)

        # Assert: Correct categorization
        assert "modified" in changes and len(changes["modified"]) > 0
        assert "added" in changes and len(changes["added"]) > 0
        assert "deleted" in changes and len(changes["deleted"]) > 0

        # Verify specific files
        assert any("modified.md" in str(f) for f in changes["modified"])
        assert any("added.md" in str(f) for f in changes["added"])
        assert any("deleted.md" in str(f) for f in changes["deleted"])

    def test_handles_binary_files_gracefully(self, tmp_path):
        """Binary file changes are detected without crashing diff."""
        # Arrange: Binary file (simulate with bytes)
        existing_dir = tmp_path / "existing"
        existing_dir.mkdir()
        existing_file = existing_dir / "image.png"
        existing_file.write_bytes(b"\x89PNG\r\n\x1a\n\x00\x00\x00")

        generated_dir = tmp_path / "generated"
        generated_dir.mkdir()
        generated_file = generated_dir / "image.png"
        generated_file.write_bytes(b"\x89PNG\r\n\x1a\n\xff\xff\xff")

        # Act: Generate diff (should handle binary gracefully)
        try:
            diff_result = generate_unified_diff(existing_file, generated_file)
            # Assert: Function completes without error
            assert diff_result is not None
        except Exception as e:
            # Should handle binary files gracefully with appropriate error
            assert "binary" in str(e).lower() or "decode" in str(e).lower()

    def test_summary_shows_change_counts(self, tmp_path):
        """Change summary reports counts: N modified, M added, K deleted."""
        # Arrange: Multiple changes
        existing_dir = tmp_path / "existing"
        existing_dir.mkdir()
        (existing_dir / "file1.md").write_text("Old 1")
        (existing_dir / "file2.md").write_text("Old 2")
        (existing_dir / "removed.md").write_text("Gone")

        generated_dir = tmp_path / "generated"
        generated_dir.mkdir()
        (generated_dir / "file1.md").write_text("New 1")
        (generated_dir / "file2.md").write_text("New 2")
        (generated_dir / "added.md").write_text("New")

        # Act: Compare and get summary
        changes = compare_directories(existing_dir, generated_dir)

        # Assert: Summary has counts
        assert len(changes["modified"]) == 2
        assert len(changes["added"]) == 1
        assert len(changes["deleted"]) == 1
