"""Tests for build_ui_manifest() function (scripts/build_ui_manifest.py).

This test file covers:
- Discovery of commands/*.yml.j2 templates
- Rendering each template with base_config=""
- Extraction of commands section
- Writing ui/json/languages.json with correct structure
- Skipping invalid/incomplete templates
- Error handling for missing commands/ directory
"""

import json
import logging
import shutil
from unittest import mock

import pytest

from scripts.build_ui_manifest import build_ui_manifest
from scripts.paths import PROJECT_ROOT


class TestBuildUiManifest:
    """Test suite for build_ui_manifest() function."""

    def test_writes_languages_json_with_correct_structure_and_creates_ui_dir(self, tmp_path):
        """build_ui_manifest() creates ui/ directory and writes ui/json/languages.json keyed by language."""
        # Arrange
        commands_dir = tmp_path / "commands"
        commands_dir.mkdir()
        (commands_dir / "python.yml.j2").write_text(
            "{{ base_config }}\ncommands:\n"
            "  test:\n    command: pytest\n    description: Run all tests\n    category: test\n"
            "  lint:\n    command: ruff check scripts/\n    description: Run linter\n    category: lint\n"
        )

        # Act
        with mock.patch("scripts.build_ui_manifest.PROJECT_ROOT", tmp_path):
            build_ui_manifest()

        # Assert: ui/ directory created
        assert (tmp_path / "ui").is_dir()
        # Assert: languages.json created
        assert (
            tmp_path / "ui" / "json" / "languages.json"
        ).exists(), "languages.json was not created"
        content = json.loads((tmp_path / "ui" / "json" / "languages.json").read_text())
        assert "python" in content
        lang_data = content["python"]
        assert isinstance(lang_data, dict)
        entries = lang_data["commands"]
        assert isinstance(entries, list)
        # Every entry has required keys
        for entry in entries:
            assert "name" in entry
            assert "command" in entry
            assert "description" in entry
            assert "category" in entry
        # Verify both commands from the fixture are present
        test_entry = next((e for e in entries if e["name"] == "test"), None)
        assert test_entry is not None
        assert test_entry["command"] == "pytest"
        assert test_entry["category"] == "test"
        lint_entry = next((e for e in entries if e["name"] == "lint"), None)
        assert lint_entry is not None
        assert lint_entry["command"] == "ruff check scripts/"
        assert lint_entry["category"] == "lint"

    def test_overwrites_existing_languages_json(self, tmp_path):
        """build_ui_manifest() replaces existing ui/json/languages.json with freshly generated content."""
        # Arrange
        commands_dir = tmp_path / "commands"
        commands_dir.mkdir()
        (commands_dir / "python.yml.j2").write_text(
            "{{ base_config }}\ncommands:\n"
            "  test:\n    command: pytest\n    description: Run all tests\n    category: test\n"
        )
        ui_dir = tmp_path / "ui" / "json"
        ui_dir.mkdir(parents=True)
        (ui_dir / "languages.json").write_text(json.dumps({"stale": []}))

        # Act
        with mock.patch("scripts.build_ui_manifest.PROJECT_ROOT", tmp_path):
            build_ui_manifest()

        # Assert
        assert (
            tmp_path / "ui" / "json" / "languages.json"
        ).exists(), "languages.json was not written"
        content = json.loads((tmp_path / "ui" / "json" / "languages.json").read_text())
        assert "stale" not in content
        assert "python" in content

    def test_handles_multiple_language_templates(self, tmp_path):
        """build_ui_manifest() produces one key per language when multiple templates exist."""
        # Arrange
        commands_dir = tmp_path / "commands"
        commands_dir.mkdir()
        (commands_dir / "python.yml.j2").write_text(
            "{{ base_config }}\ncommands:\n"
            "  test:\n    command: pytest\n    description: Run tests\n    category: test\n"
        )
        (commands_dir / "typescript.yml.j2").write_text(
            "{{ base_config }}\ncommands:\n"
            "  test:\n    command: npm test\n    description: Run tests\n    category: test\n"
        )

        # Act
        with mock.patch("scripts.build_ui_manifest.PROJECT_ROOT", tmp_path):
            build_ui_manifest()

        # Assert
        assert (
            tmp_path / "ui" / "json" / "languages.json"
        ).exists(), "languages.json was not created"
        content = json.loads((tmp_path / "ui" / "json" / "languages.json").read_text())
        assert "python" in content
        assert "typescript" in content
        assert isinstance(content["python"]["commands"], list)
        assert len(content["python"]["commands"]) >= 1
        assert isinstance(content["typescript"]["commands"], list)
        assert len(content["typescript"]["commands"]) >= 1

    def test_skips_template_that_fails_to_parse_and_logs_warning(self, tmp_path, caplog):
        """build_ui_manifest() skips invalid templates, logs a warning, still processes valid ones."""
        # Arrange
        commands_dir = tmp_path / "commands"
        commands_dir.mkdir()
        (commands_dir / "python.yml.j2").write_text(
            "{{ base_config }}\ncommands:\n"
            "  test:\n    command: pytest\n    description: Run tests\n    category: test\n"
        )
        # Template that produces invalid YAML after rendering
        (commands_dir / "badlang.yml.j2").write_text(
            "{{ base_config }}\n  bad:\n indent: [unclosed\n"
        )

        # Act
        with (
            mock.patch("scripts.build_ui_manifest.PROJECT_ROOT", tmp_path),
            caplog.at_level(logging.WARNING),
        ):
            build_ui_manifest()

        # Assert: valid language still present
        assert (
            tmp_path / "ui" / "json" / "languages.json"
        ).exists(), "languages.json was not created"
        content = json.loads((tmp_path / "ui" / "json" / "languages.json").read_text())
        assert "python" in content
        # Invalid template skipped
        assert "badlang" not in content
        # Warning was logged for the skipped language
        assert any("badlang" in record.message for record in caplog.records)

    def test_skips_template_with_no_commands_key(self, tmp_path):
        """build_ui_manifest() omits a language from output when its template has no 'commands' key."""
        # Arrange
        commands_dir = tmp_path / "commands"
        commands_dir.mkdir()
        (commands_dir / "python.yml.j2").write_text(
            "{{ base_config }}\ncommands:\n"
            "  test:\n    command: pytest\n    description: Run tests\n    category: test\n"
        )
        (commands_dir / "nocommands.yml.j2").write_text("{{ base_config }}\nname: nocommands\n")

        # Act
        with mock.patch("scripts.build_ui_manifest.PROJECT_ROOT", tmp_path):
            build_ui_manifest()

        # Assert
        assert (
            tmp_path / "ui" / "json" / "languages.json"
        ).exists(), "languages.json was not created"
        content = json.loads((tmp_path / "ui" / "json" / "languages.json").read_text())
        assert "python" in content
        assert "nocommands" not in content

    def test_raises_file_not_found_error_when_commands_dir_missing(self, tmp_path):
        """build_ui_manifest() raises FileNotFoundError when PROJECT_ROOT / 'commands' does not exist."""
        # Arrange: tmp_path has no commands/ directory

        # Act & Assert
        with (
            mock.patch("scripts.build_ui_manifest.PROJECT_ROOT", tmp_path),
            pytest.raises(FileNotFoundError),
        ):
            build_ui_manifest()

    @pytest.mark.integration
    @pytest.mark.parametrize(
        "language",
        [
            "javascript",
            "javascript-npm",
            "kotlin-maven",
            "python-poetry",
            "python-uv",
        ],
    )
    def test_new_language_template_included_in_manifest(self, tmp_path, language):
        """New language template renders with test, lint, and typecheck core commands."""
        shutil.copytree(PROJECT_ROOT / "commands", tmp_path / "commands")

        with mock.patch("scripts.build_ui_manifest.PROJECT_ROOT", tmp_path):
            build_ui_manifest()

        content = json.loads((tmp_path / "ui" / "json" / "languages.json").read_text())
        assert language in content, f"Expected '{language}' in languages.json"
        entries = content[language]["commands"]
        categories = {e["category"] for e in entries}
        assert "test" in categories, f"'{language}' missing test command"
        assert "lint" in categories, f"'{language}' missing lint command"
        assert "typecheck" in categories, f"'{language}' missing typecheck command"
        for entry in entries:
            assert entry["command"] != "", f"Empty command in '{language}' entry: {entry['name']}"

    def test_language_entry_has_commands_and_mutation_commands_keys(self, tmp_path):
        """build_ui_manifest() wraps each language in {commands: [...], mutationCommands: {...}}."""
        commands_dir = tmp_path / "commands"
        commands_dir.mkdir()
        (commands_dir / "python.yml.j2").write_text(
            "{{ base_config }}\ncommands:\n"
            "  test:\n    command: pytest\n    description: Run all tests\n    category: test\n"
        )

        with mock.patch("scripts.build_ui_manifest.PROJECT_ROOT", tmp_path):
            build_ui_manifest()

        content = json.loads((tmp_path / "ui" / "json" / "languages.json").read_text())
        assert "python" in content
        lang_data = content["python"]
        assert isinstance(lang_data, dict), "language entry must be a dict with 'commands' and 'mutationCommands'"
        assert "commands" in lang_data
        assert "mutationCommands" in lang_data
        assert isinstance(lang_data["commands"], list)
        assert isinstance(lang_data["mutationCommands"], dict)

    def test_extracts_single_mutation_command_stub_into_mutation_commands(self, tmp_path):
        """build_ui_manifest() extracts a commented mutate stub into mutationCommands."""
        commands_dir = tmp_path / "commands"
        commands_dir.mkdir()
        (commands_dir / "python.yml.j2").write_text(
            "{{ base_config }}\ncommands:\n"
            "  test:\n    command: pytest\n    description: Run all tests\n    category: test\n"
            "\n"
            "  # mutate:\n"
            "  #   command: mutmut run\n"
            "  #   description: Run mutation tests\n"
            "  #   category: test\n"
        )

        with mock.patch("scripts.build_ui_manifest.PROJECT_ROOT", tmp_path):
            build_ui_manifest()

        content = json.loads((tmp_path / "ui" / "json" / "languages.json").read_text())
        mutation_cmds = content["python"]["mutationCommands"]
        assert "mutate" in mutation_cmds
        assert mutation_cmds["mutate"]["command"] == "mutmut run"
        assert mutation_cmds["mutate"]["description"] == "Run mutation tests"
        assert mutation_cmds["mutate"]["category"] == "test"

    def test_extracts_mutate_and_mutate_diff_stubs_for_typescript_style_language(self, tmp_path):
        """build_ui_manifest() extracts both mutate and mutate_diff stubs when both are present."""
        commands_dir = tmp_path / "commands"
        commands_dir.mkdir()
        (commands_dir / "typescript.yml.j2").write_text(
            "{{ base_config }}\ncommands:\n"
            "  test:\n    command: npm test\n    description: Run all tests\n    category: test\n"
            "\n"
            "  # mutate:\n"
            "  #   command: npx stryker run\n"
            "  #   description: Run mutation tests\n"
            "  #   category: test\n"
            "\n"
            "  # mutate_diff:\n"
            "  #   command: npx stryker run --since HEAD~1\n"
            "  #   description: Run mutation tests on changed files since last commit\n"
            "  #   category: test\n"
        )

        with mock.patch("scripts.build_ui_manifest.PROJECT_ROOT", tmp_path):
            build_ui_manifest()

        content = json.loads((tmp_path / "ui" / "json" / "languages.json").read_text())
        mutation_cmds = content["typescript"]["mutationCommands"]
        assert "mutate" in mutation_cmds
        assert mutation_cmds["mutate"]["command"] == "npx stryker run"
        assert "mutate_diff" in mutation_cmds
        assert mutation_cmds["mutate_diff"]["command"] == "npx stryker run --since HEAD~1"

    def test_extracts_mutate_targeted_stub_for_stryker_style_language(self, tmp_path):
        """build_ui_manifest() extracts the mutate_targeted stub alongside mutate and mutate_diff."""
        commands_dir = tmp_path / "commands"
        commands_dir.mkdir()
        (commands_dir / "typescript.yml.j2").write_text(
            "{{ base_config }}\ncommands:\n"
            "  test:\n    command: npm test\n    description: Run all tests\n    category: test\n"
            "\n"
            "  # mutate:\n"
            "  #   command: npx stryker run\n"
            "  #   description: Run mutation tests\n"
            "  #   category: test\n"
            "\n"
            "  # mutate_diff:\n"
            "  #   command: npx stryker run --since HEAD~1\n"
            "  #   description: Run mutation tests on changed files since last commit\n"
            "  #   category: test\n"
            "\n"
            "  # mutate_targeted:\n"
            "  #   command: npx stryker run --mutate\n"
            "  #   description: Run mutation tests on supplied paths\n"
            "  #   category: test\n"
        )

        with mock.patch("scripts.build_ui_manifest.PROJECT_ROOT", tmp_path):
            build_ui_manifest()

        content = json.loads((tmp_path / "ui" / "json" / "languages.json").read_text())
        mutation_cmds = content["typescript"]["mutationCommands"]
        assert "mutate_targeted" in mutation_cmds
        assert mutation_cmds["mutate_targeted"]["command"] == "npx stryker run --mutate"
        assert mutation_cmds["mutate_targeted"]["category"] == "test"

    def test_mutation_commands_empty_when_no_stubs_in_template(self, tmp_path):
        """build_ui_manifest() produces empty mutationCommands when template has no mutation stubs."""
        commands_dir = tmp_path / "commands"
        commands_dir.mkdir()
        (commands_dir / "go.yml.j2").write_text(
            "{{ base_config }}\ncommands:\n"
            "  test:\n    command: go test ./...\n    description: Run all tests\n    category: test\n"
        )

        with mock.patch("scripts.build_ui_manifest.PROJECT_ROOT", tmp_path):
            build_ui_manifest()

        content = json.loads((tmp_path / "ui" / "json" / "languages.json").read_text())
        assert content["go"]["mutationCommands"] == {}

    def test_mutation_command_with_inline_yaml_comment_in_command_value(self, tmp_path):
        """build_ui_manifest() strips inline YAML comment from command value in mutation stub."""
        commands_dir = tmp_path / "commands"
        commands_dir.mkdir()
        (commands_dir / "python.yml.j2").write_text(
            "{{ base_config }}\ncommands:\n"
            "  test:\n    command: pytest\n    description: Run all tests\n    category: test\n"
            "\n"
            '  # mutate:\n'
            '  #   command: "mutmut run"  # not validated; review before use\n'
            "  #   description: Run mutation tests\n"
            "  #   category: test\n"
        )

        with mock.patch("scripts.build_ui_manifest.PROJECT_ROOT", tmp_path):
            build_ui_manifest()

        content = json.loads((tmp_path / "ui" / "json" / "languages.json").read_text())
        mutation_cmds = content["python"]["mutationCommands"]
        assert "mutate" in mutation_cmds
        assert mutation_cmds["mutate"]["command"] == "mutmut run"

    @pytest.mark.integration
    def test_integration_produces_valid_json_from_real_commands_dir(self, tmp_path):
        """build_ui_manifest() produces valid ui/json/languages.json from real commands/*.yml.j2 files."""
        # Arrange: copy real commands/ into tmp_path for filesystem isolation
        real_commands_dir = PROJECT_ROOT / "commands"
        shutil.copytree(real_commands_dir, tmp_path / "commands")

        # Act
        with mock.patch("scripts.build_ui_manifest.PROJECT_ROOT", tmp_path):
            build_ui_manifest()

        # Assert: file written and is valid JSON
        json_path = tmp_path / "ui" / "json" / "languages.json"
        assert json_path.exists(), "ui/json/languages.json was not created"
        content = json.loads(json_path.read_text())
        assert isinstance(content, dict)
        # At least python is present
        assert "python" in content
        # Each language maps to a dict with commands and mutationCommands
        for language, lang_data in content.items():
            assert isinstance(lang_data, dict), f"{language} entry should be a dict"
            assert "commands" in lang_data, f"{language} missing 'commands' key"
            assert "mutationCommands" in lang_data, f"{language} missing 'mutationCommands' key"
            entries = lang_data["commands"]
            assert isinstance(entries, list), f"{language} commands should be a list"
            assert len(entries) > 0, f"{language} commands should not be empty"
            # Each entry has required keys and no empty command
            for entry in entries:
                assert "name" in entry
                assert "command" in entry
                assert "description" in entry
                assert "category" in entry
                assert entry["command"] != "", f"Empty command in {language} entry: {entry['name']}"
