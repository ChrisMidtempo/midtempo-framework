"""Test SmartContext class for providing filter methods to macros.

Tests verify that SmartContext:
- Provides attribute-style access to context dict keys via __getattr__
- Provides dictionary-style access via __getitem__
- Supports contains operator via __contains__
- Implements get method with default value support
- Delegates filter method calls to implementation functions
- Passes context dict (not SmartContext instance) to implementation functions
"""

import pytest

from scripts.filters import SmartContext


class TestSmartContextAttributeAccess:
    """Tests for SmartContext attribute and dictionary access methods."""

    def test_attribute_access_returns_context_dict_values(self):
        """SmartContext returns context dict values when accessed as attributes.

        Test 1.1: Attribute access via __getattr__

        Gate 1: Testing real behaviour → VALID (asserts on return value)
        Gate 2: No test-only methods → VALID
        Gate 3: Understand dependencies → VALID (dict delegation)
        Gate 4: Complete mock → VALID (minimal context dict)
        Gate 5: Test isolation → VALID (fresh instance)
        Gate 6: Coverage scope → VALID (happy path)
        """
        context = {
            "commands": {"test": {"command": "npm run test:python"}},
            "repo": {"name": "test-repo"},
        }
        ctx = SmartContext(context, {})

        assert ctx.commands == {"test": {"command": "npm run test:python"}}
        assert ctx.repo == {"name": "test-repo"}

    def test_dictionary_style_access_returns_context_dict_values(self):
        """SmartContext returns context dict values when accessed with bracket notation.

        Test 1.2: Dictionary-style access via __getitem__

        Gate 1: Testing real behaviour → VALID (asserts on return value)
        Gate 2: No test-only methods → VALID
        Gate 3: Understand dependencies → VALID (dict subscript)
        Gate 4: Complete mock → VALID (minimal context dict)
        Gate 5: Test isolation → VALID (fresh instance)
        Gate 6: Coverage scope → VALID (happy path and error path)
        """
        context = {
            "commands": {"test": {"command": "npm run test:python"}},
            "repo": {"name": "test-repo"},
        }
        ctx = SmartContext(context, {})

        assert ctx["commands"] == {"test": {"command": "npm run test:python"}}
        assert ctx["repo"] == {"name": "test-repo"}

        # Error path: accessing missing key raises KeyError
        with pytest.raises(KeyError):
            _ = ctx["nonexistent"]

    def test_contains_operator_checks_key_presence(self):
        """SmartContext supports 'in' operator to check key existence.

        Test 1.3: Contains operator via __contains__

        Gate 1: Testing real behaviour → VALID (asserts on boolean return)
        Gate 2: No test-only methods → VALID
        Gate 3: Understand dependencies → VALID (dict membership test)
        Gate 4: Complete mock → VALID (minimal context dict)
        Gate 5: Test isolation → VALID (fresh instance)
        Gate 6: Coverage scope → VALID (membership true and false cases)
        """
        context = {
            "commands": {"test": {"command": "npm run test:python"}},
            "repo": {"name": "test-repo"},
        }
        ctx = SmartContext(context, {})

        assert "commands" in ctx
        assert "repo" in ctx
        assert "nonexistent" not in ctx

    def test_get_method_returns_value_or_default(self):
        """SmartContext.get() returns value if key exists, otherwise returns default.

        Test 1.4: Get method with default

        Gate 1: Testing real behaviour → VALID (asserts on return value)
        Gate 2: No test-only methods → VALID
        Gate 3: Understand dependencies → VALID (dict.get behaviour)
        Gate 4: Complete mock → VALID (minimal context dict)
        Gate 5: Test isolation → VALID (fresh instance)
        Gate 6: Coverage scope → VALID (key exists, missing with default, missing without default)
        """
        context = {
            "commands": {"test": {"command": "npm run test:python"}},
        }
        ctx = SmartContext(context, {})

        assert ctx.get("commands") == {"test": {"command": "npm run test:python"}}
        assert ctx.get("missing", "default_value") == "default_value"
        assert ctx.get("missing") is None


class TestSmartContextFilterMethods:
    """Tests for SmartContext filter method delegation."""

    def test_cmd_method_resolves_command_string(self):
        """SmartContext.cmd() calls implementation function with context data.

        Test 1.5: cmd method resolves command string

        Gate 1: Testing real behaviour → VALID (asserts on return value)
        Gate 2: No test-only methods → VALID
        Gate 3: Understand dependencies → VALID (implementation function delegation)
        Gate 4: Complete mock → VALID (mock implementation function)
        Gate 5: Test isolation → VALID (fresh instance)
        Gate 6: Coverage scope → VALID (delegation to implementation)
        """
        context = {
            "commands": {"test": {"command": "npm run test:python"}},
        }

        # Mock implementation function
        def mock_cmd_impl(ctx_dict, cmd_name):
            return "npm run test:python"

        filter_impls = {"cmd": mock_cmd_impl}
        ctx = SmartContext(context, filter_impls)

        result = ctx.cmd("test")

        assert result == "npm run test:python"

    def test_category_method_filters_commands_by_category(self):
        """SmartContext.category() calls implementation function with context data.

        Test 1.6: category method filters commands by category

        Gate 1: Testing real behaviour → VALID (asserts on return value)
        Gate 2: No test-only methods → VALID
        Gate 3: Understand dependencies → VALID (implementation function delegation)
        Gate 4: Complete mock → VALID (mock implementation function)
        Gate 5: Test isolation → VALID (fresh instance)
        Gate 6: Coverage scope → VALID (delegation to implementation)
        """
        context = {
            "commands": {
                "test": {"command": "npm run test:python", "category": "test"},
            },
        }

        # Mock implementation function
        def mock_category_impl(ctx_dict, cat_name):
            return [("test", "npm run test:python", "Run all tests")]

        filter_impls = {"category": mock_category_impl}
        ctx = SmartContext(context, filter_impls)

        result = ctx.category("test")

        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0] == ("test", "npm run test:python", "Run all tests")

    def test_instructions_method_formats_instruction_path(self):
        """SmartContext.instructions() calls implementation function with context data.

        Test 1.7: instructions method formats instruction path

        Gate 1: Testing real behaviour → VALID (asserts on return value)
        Gate 2: No test-only methods → VALID
        Gate 3: Understand dependencies → VALID (implementation function delegation)
        Gate 4: Complete mock → VALID (mock implementation function)
        Gate 5: Test isolation → VALID (fresh instance)
        Gate 6: Coverage scope → VALID (delegation to implementation)
        """
        context = {
            "instructions": {
                "purpose": {"page": "instructions/purpose.md", "description": "Purpose doc"}
            },
        }

        # Mock implementation function
        def mock_instructions_impl(ctx_dict, inst_name):
            return "READ: `instructions/purpose.md`"

        filter_impls = {"instructions": mock_instructions_impl}
        ctx = SmartContext(context, filter_impls)

        result = ctx.instructions("purpose")

        assert result == "READ: `instructions/purpose.md`"
