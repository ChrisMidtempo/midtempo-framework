"""Tests for config factory functions decoupled from schema structure.

Tests verify factory functions accept optional capabilities parameters so tests
specify only capabilities they explicitly test, achieving decoupling from
schema structure changes.
"""

from scripts.capabilities import DEFAULT_CAPABILITIES
from tests.helpers.config_factory import (
    create_config_with_language,
    create_config_with_language_and_commands,
    create_standard_config,
    create_valid_config,
)


def test_create_standard_config_merges_enabled_capabilities_over_defaults():
    """create_standard_config merges enabled capabilities over DEFAULT_CAPABILITIES."""
    # Call with hasUI enabled
    config = create_standard_config("python", capabilities={"hasUI"})

    # Should have capabilities object with hasUI=True and others from defaults
    assert "capabilities" in config
    assert config["capabilities"]["hasUI"] is True
    assert config["capabilities"]["hasDB"] is False

    # All DEFAULT_CAPABILITIES keys should be present
    for key in DEFAULT_CAPABILITIES:
        assert key in config["capabilities"]


def test_create_standard_config_uses_defaults_when_no_capabilities_specified():
    """create_standard_config uses DEFAULT_CAPABILITIES when no capabilities specified."""
    # Call with no capabilities argument
    config = create_standard_config("python")

    # Should have capabilities object equal to DEFAULT_CAPABILITIES
    assert "capabilities" in config
    assert config["capabilities"] == DEFAULT_CAPABILITIES


def test_create_valid_config_provides_empty_capabilities_by_default():
    """create_valid_config provides empty capabilities dict when none specified."""
    config = create_valid_config()

    # Should have capabilities object but empty - maximum decoupling
    assert "capabilities" in config
    assert config["capabilities"] == {}


def test_create_valid_config_accepts_specific_capabilities():
    """create_valid_config accepts capabilities dict and uses it exactly."""
    config = create_valid_config(capabilities={"hasUI": True})

    assert "capabilities" in config
    assert config["capabilities"] == {"hasUI": True}


def test_create_config_with_language_provides_empty_capabilities_by_default():
    """create_config_with_language provides empty capabilities by default."""
    config = create_config_with_language({"python": "backend"})

    assert "capabilities" in config
    assert config["capabilities"] == {}


def test_create_config_with_language_accepts_capabilities():
    """create_config_with_language accepts optional capabilities parameter."""
    config = create_config_with_language({"python": "backend"}, capabilities={"hasDB": True})

    assert "capabilities" in config
    assert config["capabilities"] == {"hasDB": True}


def test_create_config_with_language_and_commands_provides_empty_capabilities():
    """create_config_with_language_and_commands provides empty capabilities by default."""
    config = create_config_with_language_and_commands({"python": "backend"}, {})

    assert "capabilities" in config
    assert config["capabilities"] == {}


def test_create_config_with_language_and_commands_accepts_capabilities():
    """create_config_with_language_and_commands accepts optional capabilities parameter."""
    config = create_config_with_language_and_commands(
        {"python": "backend"}, {}, capabilities={"hasUI": True, "hasDB": False}
    )

    assert "capabilities" in config
    assert config["capabilities"] == {"hasUI": True, "hasDB": False}
