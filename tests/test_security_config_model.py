"""Tests for security config model.

Tests verify security capability flags in the capabilities registry,
schema validation for security capabilities and security section,
schema generation for security section, config factory security support,
and integration with the generation pipeline.
"""

import json
import tempfile
from pathlib import Path
from typing import Any

import pytest
from jsonschema import ValidationError

from scripts.capabilities import CAPABILITIES, DEFAULT_CAPABILITIES
from scripts.generate_schema import generate_schema
from tests.fixtures.schemas import load_test_schema, validate_test_config
from tests.helpers.config_factory import (
    create_config_with_language,
    create_invalid_scope_config,
    create_valid_config,
)


def _assert_schema_accepts(config: dict) -> None:
    """Assert config passes schema validation, failing with clear message if not."""
    try:
        validate_test_config(config)
    except ValidationError as e:
        pytest.fail(f"Schema should accept config but validation failed: {e.message}")


# --- Section 1: Capabilities Registry ---


class TestCapabilitiesRegistry:
    """Tests for security capability flags in the CAPABILITIES registry."""

    # Test 1.1
    def test_registry_contains_is_public_facing_with_correct_metadata(self):
        """Registry contains isPublicFacing with default: False and string description."""
        assert "isPublicFacing" in CAPABILITIES
        entry = CAPABILITIES["isPublicFacing"]
        assert entry["default"] is False
        assert isinstance(entry["description"], str)
        assert len(entry["description"]) > 0

    # Test 1.2
    def test_registry_contains_handles_confidential_data_with_correct_metadata(self):
        """Registry contains handlesConfidentialData with default: False and string description."""
        assert "handlesConfidentialData" in CAPABILITIES
        entry = CAPABILITIES["handlesConfidentialData"]
        assert entry["default"] is False
        assert isinstance(entry["description"], str)
        assert len(entry["description"]) > 0

    # Test 1.3
    def test_registry_contains_has_authentication_with_correct_metadata(self):
        """Registry contains hasAuthentication with default: False and string description."""
        assert "hasAuthentication" in CAPABILITIES
        entry = CAPABILITIES["hasAuthentication"]
        assert entry["default"] is False
        assert isinstance(entry["description"], str)
        assert len(entry["description"]) > 0

    # Test 1.4
    def test_default_capabilities_includes_all_security_flags(self):
        """DEFAULT_CAPABILITIES includes all 3 security flags as False."""
        assert "isPublicFacing" in DEFAULT_CAPABILITIES
        assert DEFAULT_CAPABILITIES["isPublicFacing"] is False
        assert "handlesConfidentialData" in DEFAULT_CAPABILITIES
        assert DEFAULT_CAPABILITIES["handlesConfidentialData"] is False
        assert "hasAuthentication" in DEFAULT_CAPABILITIES
        assert DEFAULT_CAPABILITIES["hasAuthentication"] is False

    # Test 1.5
    def test_registry_has_exactly_six_entries(self):
        """Registry has exactly 6 entries (3 existing + 3 new)."""
        assert len(CAPABILITIES) == 6


# --- Section 2: Schema Validation — Security Capabilities ---


class TestSchemaSecurityCapabilities:
    """Tests for schema validation of security capability flags."""

    # Test 2.1
    def test_schema_accepts_is_public_facing_true(self):
        """Schema accepts a config with isPublicFacing: True in capabilities."""
        config = create_valid_config({"isPublicFacing": True})
        _assert_schema_accepts(config)

    # Test 2.2
    def test_schema_accepts_handles_confidential_data_true(self):
        """Schema accepts a config with handlesConfidentialData: True in capabilities."""
        config = create_valid_config({"handlesConfidentialData": True})
        _assert_schema_accepts(config)

    # Test 2.3
    def test_schema_accepts_has_authentication_true(self):
        """Schema accepts a config with hasAuthentication: True in capabilities."""
        config = create_valid_config({"hasAuthentication": True})
        _assert_schema_accepts(config)

    # Test 2.4
    def test_schema_accepts_all_security_flags_combined(self):
        """Schema accepts a config with all 3 security flags set to True."""
        config = create_valid_config(
            {
                "isPublicFacing": True,
                "handlesConfidentialData": True,
                "hasAuthentication": True,
            }
        )
        _assert_schema_accepts(config)

    # Test 2.5
    def test_schema_rejects_non_boolean_security_flag(self):
        """Schema rejects a string value where a boolean is expected for a security flag."""
        config = create_valid_config({"isPublicFacing": "yes"})  # type: ignore[dict-item]
        with pytest.raises(ValidationError) as exc_info:
            validate_test_config(config)
        error = str(exc_info.value.message)
        assert "is not of type" in error


# --- Section 3: Schema Validation — Security Section ---


class TestSchemaSecuritySection:
    """Tests for schema validation of the security section."""

    # Test 3.1
    def test_schema_accepts_valid_security_section_one_domain(self):
        """Schema accepts a config with a single valid security domain entry."""
        schema = load_test_schema()
        assert "security" in schema["properties"], "Schema must define security section"

        config = create_valid_config()
        config["security"] = {
            "owasp-top-10": {"page": "owasp.md", "description": "OWASP Top 10 rules"}
        }
        _assert_schema_accepts(config)

    # Test 3.2
    def test_schema_accepts_valid_security_section_multiple_domains(self):
        """Schema accepts a config with 2+ domain entries in the security section."""
        schema = load_test_schema()
        assert "security" in schema["properties"], "Schema must define security section"

        config = create_valid_config()
        config["security"] = {
            "owasp-top-10": {"page": "owasp.md", "description": "OWASP Top 10"},
            "auth-rules": {"page": "auth.md", "description": "Auth rules"},
        }
        _assert_schema_accepts(config)

    # Test 3.3
    def test_schema_accepts_empty_security_section(self):
        """Schema accepts an empty security section with zero domain entries."""
        schema = load_test_schema()
        assert "security" in schema["properties"], "Schema must define security section"

        config = create_valid_config()
        config["security"] = {}
        _assert_schema_accepts(config)

    # Test 3.4
    def test_config_without_security_section_passes_validation(self):
        """Config without a security section passes validation (backward compatible)."""
        schema = load_test_schema()
        assert "security" in schema["properties"], "Schema must define security section"

        config = create_valid_config()
        assert "security" not in config
        _assert_schema_accepts(config)

    # Test 3.5
    def test_schema_rejects_security_entry_missing_page(self):
        """Schema rejects a security domain entry that omits the required page field."""
        config = create_valid_config()
        config["security"] = {"domain": {"description": "desc"}}
        with pytest.raises(ValidationError):
            validate_test_config(config)

    # Test 3.6
    def test_schema_rejects_security_entry_missing_description(self):
        """Schema rejects a security domain entry that omits the required description field."""
        config = create_valid_config()
        config["security"] = {"domain": {"page": "file.md"}}
        with pytest.raises(ValidationError):
            validate_test_config(config)

    # Test 3.7
    def test_schema_rejects_security_entry_with_extra_properties(self):
        """additionalProperties: false blocks extra fields on security entries."""
        config = create_valid_config()
        config["security"] = {"domain": {"page": "f.md", "description": "d", "extra": "x"}}
        with pytest.raises(ValidationError):
            validate_test_config(config)

    # Test 3.8
    def test_schema_rejects_security_domain_key_with_uppercase(self):
        """patternProperties regex rejects uppercase domain keys."""
        config = create_valid_config()
        config["security"] = {"OWASP": {"page": "f.md", "description": "d"}}
        with pytest.raises(ValidationError):
            validate_test_config(config)

    # Test 3.9
    def test_schema_rejects_security_domain_key_starting_with_number(self):
        """patternProperties regex rejects keys starting with a digit."""
        config = create_valid_config()
        config["security"] = {"2fa-rules": {"page": "f.md", "description": "d"}}
        with pytest.raises(ValidationError):
            validate_test_config(config)


# --- Section 4: Schema Generation ---


class TestSchemaGeneration:
    """Tests for generate_schema writing security section to schema output."""

    def _create_temp_schema_with_existing_sections(self) -> str:
        """Create a temp schema file with existing capabilities and instructions sections."""
        test_schema = {
            "properties": {
                "capabilities": {
                    "properties": {
                        "hasUI": {"type": "boolean", "description": "UI"},
                        "hasDB": {"type": "boolean", "description": "DB"},
                        "hasTypecheck": {"type": "boolean", "description": "Typecheck"},
                    }
                },
                "instructions": {
                    "type": "object",
                    "additionalProperties": False,
                    "patternProperties": {
                        "^[a-z][a-z0-9_-]*$": {
                            "type": "object",
                            "required": ["page", "description"],
                            "properties": {
                                "page": {"type": "string", "minLength": 1},
                                "description": {"type": "string", "minLength": 1},
                            },
                            "additionalProperties": False,
                        }
                    },
                },
            }
        }
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(test_schema, f)
            return f.name

    def _run_generation_and_load(self, schema_path: str) -> dict[str, Any]:
        """Run schema generation with full registry and load result."""
        test_registry: dict[str, dict[str, bool | str]] = {
            "hasUI": {"default": False, "description": "UI"},
            "hasDB": {"default": False, "description": "DB"},
            "hasTypecheck": {"default": True, "description": "Typecheck"},
            "isPublicFacing": {"default": False, "description": "Public facing"},
            "handlesConfidentialData": {
                "default": False,
                "description": "Confidential data",
            },
            "hasAuthentication": {"default": False, "description": "Authentication"},
        }
        test_instructions: dict[str, dict[str, str]] = {
            "purpose": {"page": "purpose.md", "description": "Purpose"},
        }
        generate_schema(test_registry, schema_path, test_instructions)

        with Path(schema_path).open() as f:
            result: dict[str, Any] = json.load(f)
            return result

    # Test 4.1
    def test_generate_schema_writes_security_section(self):
        """generate_schema() produces a schema containing properties.security with patternProperties."""
        schema_path = self._create_temp_schema_with_existing_sections()
        try:
            result = self._run_generation_and_load(schema_path)
            assert "security" in result["properties"]
            assert "patternProperties" in result["properties"]["security"]
        finally:
            Path(schema_path).unlink()

    # Test 4.2
    def test_security_schema_has_correct_pattern_properties_regex(self):
        """Security section uses ^[a-z][a-z0-9_-]*$ as the patternProperties key."""
        schema_path = self._create_temp_schema_with_existing_sections()
        try:
            result = self._run_generation_and_load(schema_path)
            assert "security" in result["properties"], "Schema must contain security section"
            security = result["properties"]["security"]
            assert "^[a-z][a-z0-9_-]*$" in security["patternProperties"]
        finally:
            Path(schema_path).unlink()

    # Test 4.3
    def test_security_schema_requires_page_and_description(self):
        """Security entry schema declares page and description as required."""
        schema_path = self._create_temp_schema_with_existing_sections()
        try:
            result = self._run_generation_and_load(schema_path)
            assert "security" in result["properties"], "Schema must contain security section"
            entry_schema = result["properties"]["security"]["patternProperties"][
                "^[a-z][a-z0-9_-]*$"
            ]
            assert "required" in entry_schema
            assert "page" in entry_schema["required"]
            assert "description" in entry_schema["required"]
        finally:
            Path(schema_path).unlink()

    # Test 4.4
    def test_security_schema_has_additional_properties_false(self):
        """Both the security object and entry object set additionalProperties: false."""
        schema_path = self._create_temp_schema_with_existing_sections()
        try:
            result = self._run_generation_and_load(schema_path)
            assert "security" in result["properties"], "Schema must contain security section"
            security = result["properties"]["security"]
            assert security["additionalProperties"] is False
            entry_schema = security["patternProperties"]["^[a-z][a-z0-9_-]*$"]
            assert entry_schema["additionalProperties"] is False
        finally:
            Path(schema_path).unlink()

    # Test 4.5
    def test_schema_generation_preserves_existing_sections(self):
        """Schema generation with security does not alter existing capabilities or instructions."""
        schema_path = self._create_temp_schema_with_existing_sections()
        try:
            result = self._run_generation_and_load(schema_path)

            # Capabilities preserved (updated with registry)
            caps = result["properties"]["capabilities"]["properties"]
            assert "hasUI" in caps
            assert "hasDB" in caps
            assert "hasTypecheck" in caps

            # Instructions preserved
            assert "instructions" in result["properties"]
            assert "patternProperties" in result["properties"]["instructions"]

            # Security section added alongside both
            assert "security" in result["properties"]
        finally:
            Path(schema_path).unlink()


# --- Section 5: Config Factory ---


class TestConfigFactory:
    """Tests for config factory security parameter support."""

    # Test 5.1
    def test_create_valid_config_without_security_omits_key(self):
        """Factory omits the security key when no security parameter is passed."""
        config = create_valid_config()
        assert "security" not in config

    # Test 5.2
    def test_create_valid_config_with_security_includes_section(self):
        """Factory includes the security key when a security parameter is passed."""
        security_input = {"auth": {"page": "auth.md", "description": "Auth rules"}}
        config = create_valid_config(security=security_input)
        assert "security" in config
        assert config["security"] == security_input

    # Test 5.3
    def test_existing_factory_calls_remain_valid(self):
        """All existing factory functions produce valid configs without passing security parameter."""
        config1 = create_valid_config()
        assert isinstance(config1, dict)
        assert "security" not in config1

        config2 = create_config_with_language({"python": "all"})
        assert isinstance(config2, dict)
        assert "security" not in config2

        config3 = create_invalid_scope_config("Backend")
        assert isinstance(config3, dict)
        assert "security" not in config3


# --- Section 6: Integration ---


class TestIntegration:
    """Integration tests for security config model."""

    # Test 6.1
    def test_capability_defaults_merge_includes_security_flags(self):
        """DEFAULT_CAPABILITIES merge produces enriched capabilities with security flags."""
        config_capabilities: dict[str, bool] = {}
        enriched = {**DEFAULT_CAPABILITIES, **config_capabilities}

        assert "isPublicFacing" in enriched
        assert enriched["isPublicFacing"] is False
        assert "handlesConfidentialData" in enriched
        assert enriched["handlesConfidentialData"] is False
        assert "hasAuthentication" in enriched
        assert enriched["hasAuthentication"] is False
