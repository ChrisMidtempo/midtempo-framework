"""Backward compatibility tests for DEFAULT_CAPABILITIES export.

Tests ensure existing import statements and merge patterns continue working
after registry refactor.
"""

from scripts.capabilities import DEFAULT_CAPABILITIES
from tests.helpers.config_factory import create_valid_config


def test_config_factory_imports_default_capabilities():
    """Verifies existing import statements continue working after registry refactor."""
    # Import succeeds (already done at module level)
    assert DEFAULT_CAPABILITIES is not None

    # Should be dict type
    assert isinstance(DEFAULT_CAPABILITIES, dict)

    # All keys should be strings
    for key in DEFAULT_CAPABILITIES:
        assert isinstance(key, str)

    # All values should be booleans
    for value in DEFAULT_CAPABILITIES.values():
        assert isinstance(value, bool)

    # Should contain expected keys
    assert "hasUI" in DEFAULT_CAPABILITIES
    assert "hasDB" in DEFAULT_CAPABILITIES


def test_merge_pattern_works_with_derived_export():
    """Validates the merge pattern used throughout codebase continues working."""
    # User capabilities override
    user_capabilities = {"hasUI": True}

    # Merge pattern (used in config_factory.py and init_framework.py)
    result = {**DEFAULT_CAPABILITIES, **user_capabilities}

    # User override should take precedence
    assert result["hasUI"] is True

    # Default for hasDB should be preserved
    assert result["hasDB"] is False


def test_test_factory_creates_valid_config():
    """Ensures config factory helper continues producing valid configs."""
    # Call factory function
    config = create_valid_config()

    # Config should include capabilities dict
    assert "capabilities" in config
    assert isinstance(config["capabilities"], dict)

    # Test factories provide empty dict by default for decoupling
    # Tests specify capabilities they explicitly test
    assert config["capabilities"] == {}
