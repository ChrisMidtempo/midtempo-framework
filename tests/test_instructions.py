"""Tests for instruction registry structure.

Tests verify INSTRUCTIONS registry has correct type structure with page and
description fields, all entries have required non-empty fields, and no malformed
entries exist.
"""

from scripts.instructions import INSTRUCTIONS


def test_registry_has_correct_type_structure():
    """Registry has dict[str, dict[str, str]] structure with page and description keys."""
    # Registry must be dict
    assert isinstance(INSTRUCTIONS, dict)

    # Registry must not be empty (at least one example for schema generation)
    assert len(INSTRUCTIONS) > 0, "Registry must contain at least one example instruction"

    # Each key maps to dict value
    for name, metadata in INSTRUCTIONS.items():
        assert isinstance(metadata, dict), f"Instruction '{name}' metadata must be dict"

        # Each nested dict contains 'page' key (string)
        assert "page" in metadata, f"Instruction '{name}' missing 'page' field"
        assert isinstance(metadata["page"], str), f"Instruction '{name}' page must be string"

        # Each nested dict contains 'description' key (string)
        assert "description" in metadata, f"Instruction '{name}' missing 'description' field"
        assert isinstance(
            metadata["description"], str
        ), f"Instruction '{name}' description must be string"


def test_registry_entries_have_required_fields():
    """Every instruction entry has non-empty page and description fields."""
    # Iterate all entries
    for name, metadata in INSTRUCTIONS.items():
        # Page field must be non-empty string
        assert len(metadata["page"]) > 0, f"Instruction '{name}' has empty page field"

        # Description field must be non-empty string
        assert len(metadata["description"]) > 0, f"Instruction '{name}' has empty description field"

        # No null values (covered by type check above)
        assert metadata["page"] is not None, f"Instruction '{name}' page is None"
        assert metadata["description"] is not None, f"Instruction '{name}' description is None"
