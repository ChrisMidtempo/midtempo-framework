"""Tests for server/models.py — InitRequest and GenerateRequest Pydantic models.

Covers:
- InitRequest valid instantiation (B1)
- InitRequest name regex pattern enforcement (B2)
- InitRequest name max_length enforcement (B3)
- InitRequest language max_length enforcement (B4)
- InitRequest required field enforcement (B5)
- GenerateRequest accepts valid config dict (B1/Stage3)
- GenerateRequest rejects missing or wrong-type config field (B2/Stage3)
"""

from typing import Any

import pytest
from pydantic import ValidationError

from server.models import GenerateRequest, InitRequest


class TestInitRequestValid:
    """Test valid InitRequest instantiation."""

    def test_valid_name_and_language_instantiates_successfully(self):
        """InitRequest accepts a valid name and language."""
        # T1.1 — B1 happy path
        request = InitRequest(name="my-project", language="python")

        assert request.name == "my-project"
        assert request.language == "python"

    def test_name_with_special_characters_accepted(self):
        """InitRequest accepts names with dots, hyphens, and underscores after first character."""
        # T1.2 — B1 boundary: pattern allows . - _ after first char
        request = InitRequest(name="my.project_v2-final", language="python")

        assert request.name == "my.project_v2-final"


class TestInitRequestNamePatternValidation:
    """Test InitRequest name regex pattern enforcement."""

    def test_name_failing_regex_pattern_raises_validation_error(self):
        """InitRequest rejects a name starting with a special character."""
        # T1.3 — B2, CG-IV1
        with pytest.raises(ValidationError) as exc_info:
            InitRequest(name="-invalid", language="python")

        errors = exc_info.value.errors()
        assert any(e["loc"] == ("name",) for e in errors)

    def test_empty_name_raises_validation_error(self):
        """InitRequest rejects an empty string for name."""
        # T1.4 — B2, CG-IV1: empty string fails ^[a-zA-Z0-9][a-zA-Z0-9._-]*$
        with pytest.raises(ValidationError) as exc_info:
            InitRequest(name="", language="python")

        errors = exc_info.value.errors()
        assert any(e["loc"] == ("name",) for e in errors)


class TestInitRequestNameLengthValidation:
    """Test InitRequest name max_length enforcement."""

    def test_name_exceeding_100_characters_raises_validation_error(self):
        """InitRequest rejects a name of 101 characters."""
        # T1.5 — B3, CG-IV2
        with pytest.raises(ValidationError) as exc_info:
            InitRequest(name="a" * 101, language="python")

        errors = exc_info.value.errors()
        assert any(e["loc"] == ("name",) for e in errors)

    def test_name_at_exactly_100_characters_accepted(self):
        """InitRequest accepts a name of exactly 100 characters."""
        # T1.6 — B3, CG-IV2 boundary: exactly 100 chars must pass
        request = InitRequest(name="a" * 100, language="python")

        assert request.name is not None
        assert len(request.name) == 100


class TestInitRequestLanguageLengthValidation:
    """Test InitRequest language max_length enforcement."""

    def test_language_exceeding_50_characters_raises_validation_error(self):
        """InitRequest rejects a language string of 51 characters."""
        # T1.7 — B4, CG-IV2
        with pytest.raises(ValidationError) as exc_info:
            InitRequest(name="my-project", language="a" * 51)

        errors = exc_info.value.errors()
        assert any(e["loc"] == ("language",) for e in errors)


class TestInitRequestRequiredFields:
    """Test InitRequest required field enforcement."""

    def test_missing_name_field_raises_validation_error(self):
        """InitRequest rejects a payload with no name field."""
        # T1.8 — B5, CG-IV3
        with pytest.raises(ValidationError) as exc_info:
            InitRequest.model_validate({"language": "python"})

        errors = exc_info.value.errors()
        assert any(e["loc"] == ("name",) for e in errors)

    def test_missing_language_field_raises_validation_error(self):
        """InitRequest rejects a payload with no language field."""
        # T1.9 — B5, CG-IV3
        with pytest.raises(ValidationError) as exc_info:
            InitRequest.model_validate({"name": "my-project"})

        errors = exc_info.value.errors()
        assert any(e["loc"] == ("language",) for e in errors)


class TestGenerateRequestValid:
    """Test valid GenerateRequest instantiation."""

    def test_generate_request_accepts_valid_config_dict(self):
        """GenerateRequest parses a request body with a non-empty config dict."""
        # T1.1 — B1: happy path; Pydantic accepts any dict at model level
        body = {"config": {"name": "my-project", "language": "python"}}

        request = GenerateRequest(**body)

        assert request.config == {"name": "my-project", "language": "python"}

    def test_generate_request_accepts_empty_dict_as_config_value(self):
        """GenerateRequest accepts an empty dict as the config value."""
        # T1.2 — B1: boundary; schema validation is the route handler's responsibility
        body: dict[str, Any] = {"config": {}}

        request = GenerateRequest(**body)

        assert request.config == {}


class TestGenerateRequestRejection:
    """Test GenerateRequest validation failures."""

    def test_generate_request_rejects_missing_config_field(self):
        """GenerateRequest raises ValidationError when config key is absent."""
        # T1.3 — B2: missing required field raises ValidationError
        body: dict[str, Any] = {}

        with pytest.raises(ValidationError) as exc_info:
            GenerateRequest(**body)

        errors = exc_info.value.errors()
        assert any(e["loc"] == ("config",) for e in errors)

    def test_generate_request_rejects_non_dict_config_value(self):
        """GenerateRequest raises ValidationError when config is a string."""
        # T1.4 — B2: wrong type raises ValidationError
        body: dict[str, Any] = {"config": "not-a-dict"}

        with pytest.raises(ValidationError) as exc_info:
            GenerateRequest(**body)

        errors = exc_info.value.errors()
        assert any(e["loc"] == ("config",) for e in errors)
