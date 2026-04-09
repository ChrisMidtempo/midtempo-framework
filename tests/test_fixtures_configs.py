"""Tests for test fixture factories decoupled from schema structure.

Tests verify fixtures accept optional capabilities parameters so tests
specify only capabilities they explicitly test, achieving decoupling from
schema structure changes.
"""

from tests.fixtures.configs import (
    _create_minimal_config_base,
    create_full_test_config,
    create_incomplete_command,
    create_string_format_command,
    create_valid_command,
)


def test_base_fixture_provides_empty_capabilities_by_default():
    """Base fixture provides empty capabilities dict when none specified."""
    config = _create_minimal_config_base()

    # Should have capabilities object but empty - maximum decoupling
    assert "capabilities" in config
    assert config["capabilities"] == {}


def test_base_fixture_accepts_specific_capabilities():
    """Base fixture accepts capabilities dict and uses it exactly."""
    config = _create_minimal_config_base(capabilities={"hasUI": True})

    assert "capabilities" in config
    assert config["capabilities"] == {"hasUI": True}
    # Should not add other capabilities
    assert "hasDB" not in config["capabilities"]


def test_base_fixture_accepts_empty_capabilities_dict():
    """Base fixture accepts explicit empty dict."""
    config = _create_minimal_config_base(capabilities={})

    assert "capabilities" in config
    assert config["capabilities"] == {}


def test_create_valid_command_accepts_capabilities():
    """create_valid_command accepts optional capabilities parameter."""
    config = create_valid_command(
        name="test",
        command="pytest",
        description="Run tests",
        category="test",
        capabilities={"hasDB": True},
    )

    assert config["capabilities"] == {"hasDB": True}


def test_create_string_format_command_accepts_capabilities():
    """create_string_format_command accepts optional capabilities parameter."""
    config = create_string_format_command(
        name="test", command="pytest", capabilities={"hasUI": True}
    )

    assert config["capabilities"] == {"hasUI": True}


def test_create_incomplete_command_accepts_capabilities():
    """create_incomplete_command accepts optional capabilities parameter."""
    config = create_incomplete_command(name="test", command="pytest", capabilities={"hasDB": False})

    assert config["capabilities"] == {"hasDB": False}


def test_create_full_test_config_accepts_capabilities():
    """create_full_test_config accepts optional capabilities parameter."""
    config = create_full_test_config(capabilities={"hasUI": True, "hasDB": True})

    assert config["capabilities"] == {"hasUI": True, "hasDB": True}
