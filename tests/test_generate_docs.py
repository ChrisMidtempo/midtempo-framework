"""
Tests for _cmd_filter function in generate_docs.py.

Tests verify pattern-matching capability for multi-language command discovery
while preserving fast-path behaviour for mono-language repos.
"""

import pytest

from scripts.filters import _cmd_filter


def build_context(commands: dict, languages: dict) -> dict:
    """Build mock Jinja2 context for _cmd_filter tests."""
    return {"commands": commands, "repo": {"language": languages}}


class TestCmdFilterFastPath:
    """Test fast path (O(1) exact key lookup) for mono-language configs."""

    def test_fast_path_exact_key_match_mono_language(self):
        """
        Verify exact key match returns command immediately without pattern matching.

        Gate 1: Asserting on real behaviour (function return value) → VALID
        Gate 2: No test-only methods needed → VALID
        Gate 3: No mocks needed (pure function with dict input) → VALID
        Gate 4: N/A (no mocks) → VALID
        Gate 5: Test is isolated with fresh context dict per test → VALID
        Gate 6: Happy path covered → VALID
        """
        # Given: Context with bare "lint" key in mono-language config
        context = build_context(
            commands={"lint": {"command": "ruff check scripts/ tests/"}},
            languages={"python": "all"},
        )

        # When: Filter called with "lint"
        result = _cmd_filter(context, "lint")

        # Then: Returns command string immediately (fast path, no formatting)
        assert result == "ruff check scripts/ tests/"


class TestCmdFilterPatternDiscovery:
    """Test pattern matching for multi-language configs with scoped commands."""

    def test_pattern_discovers_scoped_variants_lint(self):
        """
        Verify pattern discovery for scoped lint variants with formatted output.

        Gate 1: Asserting on real behaviour (formatted string output) → VALID
        Gate 2: No test-only methods → VALID
        Gate 3: No mocks → VALID
        Gate 4: N/A → VALID
        Gate 5: Isolated test with fresh context → VALID
        Gate 6: Happy path for pattern discovery → VALID
        """
        # Given: Context with scoped lint commands for multi-language config
        context = build_context(
            commands={
                "backend_lint": {"command": "ruff check scripts/ tests/"},
                "frontend_lint": {"command": "npm run lint"},
            },
            languages={"python": "backend", "typescript": "frontend"},
        )

        # When: Filter called with "lint"
        result = _cmd_filter(context, "lint")

        # Then: Returns formatted multi-command string ordered by language declaration
        assert result == "`ruff check scripts/ tests/` (python), `npm run lint` (typescript)"

    def test_pattern_discovers_scoped_variants_test(self):
        """
        Verify pattern discovery works for test command.

        Gate 1: Real behaviour (return value) → VALID
        Gate 2: No test-only methods → VALID
        Gate 3: No mocks → VALID
        Gate 4: N/A → VALID
        Gate 5: Isolated → VALID
        Gate 6: Happy path for test command → VALID
        """
        # Given: Context with scoped test commands
        context = build_context(
            commands={
                "backend_test": {"command": "pytest tests/"},
                "frontend_test": {"command": "npm test"},
            },
            languages={"python": "backend", "typescript": "frontend"},
        )

        # When: Filter called with "test"
        result = _cmd_filter(context, "test")

        # Then: Returns formatted string with both test commands
        assert result == "`pytest tests/` (python), `npm test` (typescript)"

    def test_pattern_discovers_scoped_variants_typecheck(self):
        """
        Verify pattern discovery works for typecheck command.

        Gate 1: Real behaviour → VALID
        Gate 2: No test-only methods → VALID
        Gate 3: No mocks → VALID
        Gate 4: N/A → VALID
        Gate 5: Isolated → VALID
        Gate 6: Happy path for typecheck command → VALID
        """
        # Given: Context with scoped typecheck commands
        context = build_context(
            commands={
                "backend_typecheck": {"command": "mypy scripts/ tests/"},
                "frontend_typecheck": {"command": "npm run typecheck"},
            },
            languages={"python": "backend", "typescript": "frontend"},
        )

        # When: Filter called with "typecheck"
        result = _cmd_filter(context, "typecheck")

        # Then: Returns formatted string with both typecheck commands
        assert result == "`mypy scripts/ tests/` (python), `npm run typecheck` (typescript)"


class TestCmdFilterOrdering:
    """Test output ordering follows repo.language declaration order."""

    def test_ordering_follows_language_declaration_not_alphabetical(self):
        """
        Verify output order matches repo.language declaration order, not key order.

        Gate 1: Real behaviour (output ordering) → VALID
        Gate 2: No test-only methods → VALID
        Gate 3: No mocks → VALID
        Gate 4: N/A → VALID
        Gate 5: Isolated → VALID
        Gate 6: Happy path with specific ordering verification → VALID
        """
        # Given: Commands in alphabetical order (frontend before backend)
        # But languages declared python first
        context = build_context(
            commands={
                "frontend_lint": {"command": "npm run lint"},
                "backend_lint": {"command": "ruff check scripts/ tests/"},
            },
            languages={"python": "backend", "typescript": "frontend"},  # python FIRST
        )

        # When: Filter called with "lint"
        result = _cmd_filter(context, "lint")

        # Then: Python command appears first despite alphabetical ordering
        assert result == "`ruff check scripts/ tests/` (python), `npm run lint` (typescript)"


class TestCmdFilterEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_single_scope_in_multi_language_config(self):
        """
        Verify single scoped command returns single formatted entry without comma.

        Gate 1: Real behaviour → VALID
        Gate 2: No test-only methods → VALID
        Gate 3: No mocks → VALID
        Gate 4: N/A → VALID
        Gate 5: Isolated → VALID
        Gate 6: Boundary condition (single match) → VALID
        """
        # Given: Only backend_lint defined in multi-language config
        context = build_context(
            commands={
                "backend_lint": {"command": "ruff check scripts/ tests/"}
                # No frontend_lint
            },
            languages={"python": "backend", "typescript": "frontend"},
        )

        # When: Filter called with "lint"
        result = _cmd_filter(context, "lint")

        # Then: Single entry formatted with no trailing comma
        assert result == "`ruff check scripts/ tests/` (python)"

    def test_malformed_command_key_without_underscore(self):
        """
        Verify malformed keys (no underscore) are ignored during pattern matching.

        Gate 1: Real behaviour (error due to no valid matches) → VALID
        Gate 2: No test-only methods → VALID
        Gate 3: No mocks → VALID
        Gate 4: N/A → VALID
        Gate 5: Isolated → VALID
        Gate 6: Boundary condition (malformed key) → VALID
        """
        # Given: Command key without underscore separator
        context = build_context(
            commands={"backendlint": {"command": "ruff check scripts/ tests/"}},
            languages={"python": "backend"},
        )

        # When/Then: Filter raises KeyError (malformed key ignored)
        with pytest.raises(KeyError, match="Command 'lint' not found in config"):
            _cmd_filter(context, "lint")


class TestCmdFilterErrorHandling:
    """Test error handling for config issues."""

    def test_non_core_command_uses_exact_match_only(self):
        """
        Verify non-core commands don't trigger pattern matching.

        Gate 1: Real behaviour (error thrown) → VALID
        Gate 2: No test-only methods → VALID
        Gate 3: No mocks → VALID
        Gate 4: N/A → VALID
        Gate 5: Isolated → VALID
        Gate 6: Error path for non-core command → VALID
        """
        # Given: Scoped "build" commands (not in core set)
        context = build_context(
            commands={
                "backend_build": {"command": "npm run build:backend"},
                "frontend_build": {"command": "npm run build:frontend"},
            },
            languages={"python": "backend", "typescript": "frontend"},
        )

        # When/Then: Pattern matching not applied, raises KeyError
        with pytest.raises(KeyError, match="Command 'build' not found in config"):
            _cmd_filter(context, "build")

    def test_core_command_with_no_matches(self):
        """
        Verify core command with zero matches raises clear KeyError.

        Gate 1: Real behaviour (error) → VALID
        Gate 2: No test-only methods → VALID
        Gate 3: No mocks → VALID
        Gate 4: N/A → VALID
        Gate 5: Isolated → VALID
        Gate 6: Error path for missing command → VALID
        """
        # Given: No lint/test/typecheck keys present
        context = build_context(
            commands={"backend_build": {"command": "npm run build:backend"}},
            languages={"python": "backend"},
        )

        # When/Then: Filter raises KeyError for missing command
        with pytest.raises(KeyError, match="Command 'lint' not found in config"):
            _cmd_filter(context, "lint")

    def test_repo_language_missing_from_context(self):
        """
        Verify missing repo.language raises clear KeyError.

        Gate 1: Real behaviour (error) → VALID
        Gate 2: No test-only methods → VALID
        Gate 3: No mocks → VALID
        Gate 4: N/A → VALID
        Gate 5: Isolated → VALID
        Gate 6: Error path for missing config → VALID
        """
        # Given: Context without repo.language key
        context = {"commands": {"backend_lint": {"command": "ruff check scripts/ tests/"}}}

        # When/Then: Filter raises KeyError for missing repo key
        with pytest.raises(KeyError):
            _cmd_filter(context, "lint")

    def test_scope_not_in_repo_language_values(self):
        """
        Verify unmapped scope prefix raises clear KeyError.

        Gate 1: Real behaviour (error) → VALID
        Gate 2: No test-only methods → VALID
        Gate 3: No mocks → VALID
        Gate 4: N/A → VALID
        Gate 5: Isolated → VALID
        Gate 6: Error path for config mismatch → VALID
        """
        # Given: Scope "unknown" not in repo.language values
        context = build_context(
            commands={"unknown_lint": {"command": "custom-linter"}},
            languages={"python": "backend"},  # No "unknown" scope
        )

        # When/Then: Filter raises KeyError for unmapped scope
        with pytest.raises(KeyError):
            _cmd_filter(context, "lint")
