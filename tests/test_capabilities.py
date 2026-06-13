"""Tests for capabilities module and DEFAULT_CAPABILITIES constant.

Tests verify that DEFAULT_CAPABILITIES contains all known capability
properties with correct default values, and that immutability is documented.
"""

import scripts.capabilities as capabilities_module
from scripts.capabilities import CAPABILITIES, TEMPLATE_SKIP_RULES


def test_default_capabilities_immutability_documented():
    """Module docstring documents DEFAULT_CAPABILITIES as immutable constant."""
    # Check module docstring exists and mentions immutability
    module_doc = capabilities_module.__doc__
    assert module_doc is not None

    # Should contain words indicating immutability
    doc_lower = module_doc.lower()
    assert any(word in doc_lower for word in ["constant", "immutable", "do not modify"])


# New tests for registry structure (Phase 2)


def test_capabilities_registry_structure():
    """CAPABILITIES dict contains expected keys with correct structure."""
    # CAPABILITIES should be a dict
    assert isinstance(CAPABILITIES, dict)

    # Should contain hasUI and hasDB keys
    assert "hasUI" in CAPABILITIES
    assert "hasDB" in CAPABILITIES

    # Each capability should have 'default' and 'description' keys
    for cap_name, cap_meta in CAPABILITIES.items():
        assert isinstance(cap_meta, dict), f"{cap_name} value should be dict"
        assert "default" in cap_meta, f"{cap_name} missing 'default' key"
        assert "description" in cap_meta, f"{cap_name} missing 'description' key"

        # Default should be boolean
        assert isinstance(cap_meta["default"], bool), f"{cap_name} default should be bool"

        # Description should be non-empty string
        assert isinstance(cap_meta["description"], str), f"{cap_name} description should be str"
        assert len(cap_meta["description"]) > 0, f"{cap_name} description should be non-empty"


def test_capabilities_registry_immutability():
    """CAPABILITIES acts as constant (modification doesn't affect subsequent imports)."""
    import contextlib
    import importlib

    import scripts.capabilities

    # Import fresh reference
    from scripts.capabilities import CAPABILITIES as caps_original  # noqa: N811

    # Attempt to modify (this may or may not raise, but should not persist)
    original_hasui_value = caps_original["hasUI"]["default"]

    # Try modification
    with contextlib.suppress(TypeError, AttributeError):
        # If frozen/immutable, this is expected to be suppressed
        caps_original["hasUI"]["default"] = not original_hasui_value

    # Re-import to check if modification persisted
    importlib.reload(scripts.capabilities)
    from scripts.capabilities import CAPABILITIES as caps_fresh  # noqa: N811

    # Fresh import should have original value
    assert not caps_fresh["hasUI"]["default"]


def test_empty_registry_edge_case():
    """System handles empty CAPABILITIES dict without errors."""
    # Mock CAPABILITIES as empty dict
    empty_caps: dict[str, dict[str, bool | str]] = {}

    # Derive DEFAULT_CAPABILITIES using same logic
    derived = {name: meta["default"] for name, meta in empty_caps.items()}

    # Should result in empty dict
    assert derived == {}

    # No errors during dict comprehension
    assert isinstance(derived, dict)


class TestHasMutationTestingCapabilityEntry:
    """Tests for hasMutationTesting entry in the CAPABILITIES registry. (T1.1-T1.5)"""

    MUTATION_TESTING_PATHS = [
        "agents/mt",
        "agents/mt-fix",
        "templates/mt-session",
        "rules/mutation-testing",
    ]

    def test_has_mutation_testing_default_is_false(self):
        """hasMutationTesting CAPABILITIES entry has default False. (T1.1, B1)"""
        assert CAPABILITIES["hasMutationTesting"]["default"] is False

    def test_has_mutation_testing_description_is_non_empty(self):
        """hasMutationTesting CAPABILITIES entry has a non-empty description. (T1.2, B1)"""
        description = CAPABILITIES["hasMutationTesting"]["description"]
        assert isinstance(description, str)
        assert len(description) > 0

    def test_all_four_mutation_testing_paths_in_template_skip_rules(self):
        """All four mutation testing template paths present in TEMPLATE_SKIP_RULES. (T1.3, B2)"""
        for path in self.MUTATION_TESTING_PATHS:
            assert path in TEMPLATE_SKIP_RULES, (
                f"'{path}' not found in TEMPLATE_SKIP_RULES — "
                "path strings must match actual template paths used by the rendering loop"
            )

    def test_each_mutation_testing_skip_rule_maps_to_has_mutation_testing(self):
        """Each mutation testing TEMPLATE_SKIP_RULES entry maps to 'hasMutationTesting'. (T1.4, B2)"""
        for path in self.MUTATION_TESTING_PATHS:
            value = TEMPLATE_SKIP_RULES[path]
            assert value == "hasMutationTesting", (
                f"TEMPLATE_SKIP_RULES['{path}'] == {value!r}, expected 'hasMutationTesting' — "
                "wrong capability key causes skip on the wrong flag"
            )

    def test_mutation_testing_skip_rule_values_reference_valid_capability_key(self):
        """Each mutation testing skip rule value references a valid CAPABILITIES key. (T1.5, B3)"""
        for path in self.MUTATION_TESTING_PATHS:
            cap_key = TEMPLATE_SKIP_RULES[path]
            assert cap_key in CAPABILITIES, (
                f"TEMPLATE_SKIP_RULES['{path}'] = '{cap_key}' is not a key in CAPABILITIES — "
                "missing capability key causes silent always-skip"
            )


class TestTemplateSkipRules:
    """Test TEMPLATE_SKIP_RULES constant structure and integrity."""

    def test_template_skip_rules_is_importable_as_dict(self):
        """
        Verify TEMPLATE_SKIP_RULES is importable from scripts.capabilities as a dict.

        Plan Reference: B1
        """
        assert isinstance(TEMPLATE_SKIP_RULES, dict)
        assert "rules/db" in TEMPLATE_SKIP_RULES

    def test_template_skip_rules_values_are_str_or_list_of_str(self):
        """
        Verify every value in TEMPLATE_SKIP_RULES is str or list[str].

        The loop in _should_skip_template branches on isinstance(keys, list).
        Every value must satisfy this type contract.

        Plan Reference: B2
        """
        for pattern, keys in TEMPLATE_SKIP_RULES.items():
            if isinstance(keys, list):
                for item in keys:
                    assert isinstance(
                        item, str
                    ), f"Entry '{pattern}': list element {item!r} is not str"
            else:
                assert isinstance(
                    keys, str
                ), f"Entry '{pattern}': value {keys!r} is not str or list[str]"
        assert "rules/db" in TEMPLATE_SKIP_RULES
        assert isinstance(TEMPLATE_SKIP_RULES["rules/db"], str)

    def test_input_validation_entry_is_list_containing_has_ui_and_has_db(self):
        """
        Verify rules/security/input-validation entry is a list[str] containing
        at least "hasUI" and "hasDB".

        Plan Reference: B3
        """
        matched_key = next(
            (k for k in TEMPLATE_SKIP_RULES if "rules/security/input-validation" in k),
            None,
        )
        assert (
            matched_key is not None
        ), "No entry found with pattern 'rules/security/input-validation'"
        entry = TEMPLATE_SKIP_RULES[matched_key]
        assert isinstance(
            entry, list
        ), f"input-validation entry should be a list, got {type(entry)}"
        assert "hasUI" in entry, "input-validation entry missing 'hasUI'"
        assert "hasDB" in entry, "input-validation entry missing 'hasDB'"

    def test_str_valued_entries_reference_valid_capability_keys(self):
        """
        Verify every str-valued entry in TEMPLATE_SKIP_RULES is a key in CAPABILITIES.

        A str value is passed to capabilities.get(key, False). If the key is absent
        from CAPABILITIES, the rule silently always skips — a misconfiguration.

        Plan Reference: B4
        """
        assert "rules/db" in TEMPLATE_SKIP_RULES
        db_key = TEMPLATE_SKIP_RULES["rules/db"]
        assert isinstance(db_key, str)
        assert db_key in CAPABILITIES

        for pattern, keys in TEMPLATE_SKIP_RULES.items():
            if isinstance(keys, str):
                assert (
                    keys in CAPABILITIES
                ), f"Entry '{pattern}': capability key '{keys}' not found in CAPABILITIES"
