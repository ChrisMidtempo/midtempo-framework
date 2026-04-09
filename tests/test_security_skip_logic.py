"""
Tests for security domain template skip logic in generate_docs.py.

Tests verify _should_skip_template() correctly skips security sub-documents
based on capability flags, following the conditional rendering pattern.

Gate 1: Asserts on real behaviour (function return value) → VALID
Gate 2: No test-only methods needed → VALID
Gate 3: No mocks needed (pure function with dict input) → VALID
Gate 4: N/A (no mocks) → VALID
Gate 5: Test isolated with fresh config dict per test → VALID
Gate 6: Happy path and boundary conditions covered → VALID
"""

from pathlib import Path
from typing import Any

from scripts.generate_docs import _should_skip_template


class TestSkipRulesLoop:
    """Test edge cases of the loop-based skip rule evaluation in _should_skip_template."""

    def test_missing_capability_key_skips_template(self):
        """
        Verify missing capability key in config defaults to False (safe skip).

        When the capabilities dict is empty and the path matches a
        TEMPLATE_SKIP_RULES entry, capabilities.get(key, False) returns False,
        so not False causes a skip. Unset capability = absent = skip.

        Plan Reference: B8
        """
        # Given: Empty capabilities (key absent entirely)
        config: dict[str, Any] = {"capabilities": {}}
        template_path = Path("rules/security/authentication.md.j2")

        # When: Check if template should skip
        result = _should_skip_template(template_path, config)

        # Then: Should skip — missing key treated as False
        assert result is True

    def test_unknown_path_returns_false(self):
        """
        Verify path matching no TEMPLATE_SKIP_RULES entry and no always-skip rule
        falls through to return False.

        Plan Reference: B9
        """
        # Given: Path that matches no skip rule
        config: dict[str, Any] = {"capabilities": {}}
        template_path = Path("agents/deliver.md.j2")

        # When: Check if template should skip
        result = _should_skip_template(template_path, config)

        # Then: Should NOT skip — unknown paths always generate
        assert result is False


class TestSecurityInputValidationSkip:
    """Test input-validation template skips when hasUI=false AND hasDB=false."""

    def test_skips_input_validation_when_no_ui_and_no_db(self):
        """
        Verify input-validation skips when both hasUI and hasDB are false.

        Input validation applies to user input (UI) and database queries (DB).
        When project has neither, skip the template.
        """
        # Given: Config with hasUI=false and hasDB=false
        config = {"capabilities": {"hasUI": False, "hasDB": False}}
        template_path = Path("rules/security/input-validation.md.j2")

        # When: Check if template should skip
        result = _should_skip_template(template_path, config)

        # Then: Should skip (no UI or DB means no input validation needed)
        assert result is True

    def test_generates_input_validation_when_has_ui(self):
        """
        Verify input-validation generates when hasUI is true.

        UI projects need input validation rules.
        """
        # Given: Config with hasUI=true (hasDB=false)
        config = {"capabilities": {"hasUI": True, "hasDB": False}}
        template_path = Path("rules/security/input-validation.md.j2")

        # When: Check if template should skip
        result = _should_skip_template(template_path, config)

        # Then: Should NOT skip (UI requires input validation)
        assert result is False

    def test_generates_input_validation_when_has_db(self):
        """
        Verify input-validation generates when hasDB is true.

        Database projects need input validation to prevent SQL injection.
        """
        # Given: Config with hasDB=true (hasUI=false)
        config = {"capabilities": {"hasUI": False, "hasDB": True}}
        template_path = Path("rules/security/input-validation.md.j2")

        # When: Check if template should skip
        result = _should_skip_template(template_path, config)

        # Then: Should NOT skip (DB requires input validation)
        assert result is False

    def test_generates_input_validation_when_has_both_ui_and_db(self):
        """
        Verify input-validation generates when both hasUI and hasDB are true.
        """
        # Given: Config with both hasUI=true and hasDB=true
        config = {"capabilities": {"hasUI": True, "hasDB": True}}
        template_path = Path("rules/security/input-validation.md.j2")

        # When: Check if template should skip
        result = _should_skip_template(template_path, config)

        # Then: Should NOT skip
        assert result is False


class TestSecurityAuthenticationSkip:
    """Test authentication template skips when hasAuthentication=false."""

    def test_skips_authentication_when_flag_false(self):
        """
        Verify authentication skips when hasAuthentication is false.

        Projects without authentication don't need authentication security rules.
        """
        # Given: Config with hasAuthentication=false
        config = {"capabilities": {"hasAuthentication": False}}
        template_path = Path("rules/security/authentication.md.j2")

        # When: Check if template should skip
        result = _should_skip_template(template_path, config)

        # Then: Should skip
        assert result is True

    def test_generates_authentication_when_flag_true(self):
        """
        Verify authentication generates when hasAuthentication is true.
        """
        # Given: Config with hasAuthentication=true
        config = {"capabilities": {"hasAuthentication": True}}
        template_path = Path("rules/security/authentication.md.j2")

        # When: Check if template should skip
        result = _should_skip_template(template_path, config)

        # Then: Should NOT skip
        assert result is False


class TestSecurityDataProtectionSkip:
    """Test data-protection template skips when handlesConfidentialData=false."""

    def test_skips_data_protection_when_flag_false(self):
        """
        Verify data-protection skips when handlesConfidentialData is false.

        Projects without confidential data don't need data protection rules.
        """
        # Given: Config with handlesConfidentialData=false
        config = {"capabilities": {"handlesConfidentialData": False}}
        template_path = Path("rules/security/data-protection.md.j2")

        # When: Check if template should skip
        result = _should_skip_template(template_path, config)

        # Then: Should skip
        assert result is True

    def test_generates_data_protection_when_flag_true(self):
        """
        Verify data-protection generates when handlesConfidentialData is true.
        """
        # Given: Config with handlesConfidentialData=true
        config = {"capabilities": {"handlesConfidentialData": True}}
        template_path = Path("rules/security/data-protection.md.j2")

        # When: Check if template should skip
        result = _should_skip_template(template_path, config)

        # Then: Should NOT skip
        assert result is False


class TestSecurityPublicHardeningSkip:
    """Test public-hardening template skips when isPublicFacing=false."""

    def test_skips_public_hardening_when_flag_false(self):
        """
        Verify public-hardening skips when isPublicFacing is false.

        Internal-only projects don't need public-facing hardening rules.
        """
        # Given: Config with isPublicFacing=false
        config = {"capabilities": {"isPublicFacing": False}}
        template_path = Path("rules/security/public-hardening.md.j2")

        # When: Check if template should skip
        result = _should_skip_template(template_path, config)

        # Then: Should skip
        assert result is True

    def test_generates_public_hardening_when_flag_true(self):
        """
        Verify public-hardening generates when isPublicFacing is true.
        """
        # Given: Config with isPublicFacing=true
        config = {"capabilities": {"isPublicFacing": True}}
        template_path = Path("rules/security/public-hardening.md.j2")

        # When: Check if template should skip
        result = _should_skip_template(template_path, config)

        # Then: Should NOT skip
        assert result is False


class TestSecuritySecretsManagementUniversal:
    """Test secrets-management template NEVER skips (universal domain)."""

    def test_generates_secrets_management_with_all_flags_false(self):
        """
        Verify secrets-management generates even when all security flags are false.

        Secrets management is universal - all projects need it.
        """
        # Given: Config with all security capability flags false
        config = {
            "capabilities": {
                "hasUI": False,
                "hasDB": False,
                "hasAuthentication": False,
                "handlesConfidentialData": False,
                "isPublicFacing": False,
            }
        }
        template_path = Path("rules/security/secrets-management.md.j2")

        # When: Check if template should skip
        result = _should_skip_template(template_path, config)

        # Then: Should NOT skip (universal domain)
        assert result is False

    def test_generates_secrets_management_with_minimal_config(self):
        """
        Verify secrets-management generates with minimal capabilities config.

        Even with no security flags defined, secrets management still applies.
        """
        # Given: Minimal config with empty capabilities
        config: dict[str, Any] = {"capabilities": {}}
        template_path = Path("rules/security/secrets-management.md.j2")

        # When: Check if template should skip
        result = _should_skip_template(template_path, config)

        # Then: Should NOT skip
        assert result is False


class TestExistingSkipLogicUnchanged:
    """Verify existing skip logic still works after security additions."""

    def test_existing_db_skip_logic_unchanged(self):
        """
        Verify existing db skip logic still works.
        """
        # Given: Config with hasDB=false
        config = {"capabilities": {"hasDB": False}}
        template_path = Path("rules/db.md.j2")

        # When: Check if template should skip
        result = _should_skip_template(template_path, config)

        # Then: Should skip (existing behaviour)
        assert result is True

    def test_base_templates_still_skipped(self):
        """
        Verify base templates still skip (inheritance only).
        """
        # Given: Any config
        config: dict[str, Any] = {"capabilities": {}}
        template_path = Path("base/skill.md.j2")

        # When: Check if template should skip
        result = _should_skip_template(template_path, config)

        # Then: Should skip
        assert result is True

    def test_macros_still_skipped(self):
        """
        Verify macros.j2 still skips (utility file).
        """
        # Given: Any config
        config: dict[str, Any] = {"capabilities": {}}
        template_path = Path("macros.j2")

        # When: Check if template should skip
        result = _should_skip_template(template_path, config)

        # Then: Should skip
        assert result is True
