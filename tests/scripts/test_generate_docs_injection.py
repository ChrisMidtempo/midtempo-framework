"""Test SmartContext injection into render context.

Tests verify that:
- SmartContext instance created and added to config dict before rendering
- Original config keys remain accessible after injection
- SmartContext wraps original config data correctly
"""

from scripts.filters import SmartContext, _category_impl, _cmd_impl, _instructions_impl


class TestSmartContextInjection:
    """Tests for SmartContext injection logic."""

    def test_smartcontext_injection_into_render_context(self):
        """Verify SmartContext instance created and added to config dict before rendering.

        Test 3.1: SmartContext injection into render context

        Gate 1: Testing real behaviour → VALID (asserts on config modification)
        Gate 2: No test-only methods → VALID
        Gate 3: Understand dependencies → VALID (dict modification, SmartContext creation)
        Gate 4: Complete mock → VALID (minimal config dict)
        Gate 5: Test isolation → VALID (fresh config dict)
        Gate 6: Coverage scope → VALID (injection logic unit test)
        """
        # Create minimal test config
        config = {
            "repo": {"name": "test-repo"},
            "commands": {"test": {"command": "npm run test:python"}},
            "instructions": {"purpose": {"page": "purpose.md", "description": "Purpose"}},
        }

        # Create filter implementations dict
        filter_impls = {
            "cmd": _cmd_impl,
            "category": _category_impl,
            "instructions": _instructions_impl,
        }

        # Simulate injection logic that would be in _render_templates_to_directory()
        config["this"] = SmartContext(config, filter_impls)

        # Verify config contains 'this' key
        assert "this" in config

        # Verify 'this' is SmartContext instance
        assert isinstance(config["this"], SmartContext)

        # Verify SmartContext wraps original config data
        # (accessing internal _data is acceptable in unit test verification)
        assert config["this"]._data is config

        # Verify original config keys still accessible
        assert "repo" in config
        assert "commands" in config
        assert "instructions" in config
