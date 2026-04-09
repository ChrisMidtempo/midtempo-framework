"""Test to verify development environment setup."""


def test_basic_imports() -> None:
    """Verify core dependencies are importable."""
    import jinja2  # noqa: F401
    import jsonschema  # noqa: F401
    import yaml  # noqa: F401

    assert True


def test_python_version() -> None:
    """Verify Python version is 3.9 or higher."""
    import sys

    assert sys.version_info >= (3, 9), f"Python 3.9+ required, got {sys.version}"
