"""Tests for Jinja2 instructions filter and schema validation.

Tests verify filter extracts page value and formats READ directive, raises KeyError
for undeclared instructions, template conditionals evaluate false for missing
instructions, schema validation enforces structure, and end-to-end integration works.
"""

import tempfile
from pathlib import Path

import jsonschema

from scripts.generate_docs import setup_jinja_environment


class InstructionsNamespace:
    """Dict wrapper supporting attribute access that returns empty dict for missing keys."""

    def __init__(self, data: dict):
        self._data = data

    def __getattr__(self, name: str):
        """Return instruction metadata or empty dict for missing keys."""
        return self._data.get(name, {})

    def __contains__(self, name: str):
        """Support 'in' operator for dict-style checks."""
        return name in self._data

    def __getitem__(self, name: str):
        """Support subscript access for dict-style access."""
        return self._data[name]

    def get(self, name: str, default=None):
        """Support dict-style get method."""
        return self._data.get(name, default)


def test_filter_extracts_page_value_and_formats_read_directive():
    """Filter extracts page and description from config and formats as path with comment."""
    # Setup Jinja2 environment with instructions filter
    template_dir = Path(tempfile.gettempdir())
    env = setup_jinja_environment(template_dir)

    # Template using instructions filter
    template_str = '{{ "db" | instructions }}'
    template = env.from_string(template_str)

    # Config with instructions namespace wrapper
    config = {
        "instructions": InstructionsNamespace(
            {"db": {"page": "db.md", "description": "Database patterns"}}
        )
    }

    # Render template
    result = template.render(config)

    # Should format as backtick-wrapped path with description comment
    assert result == "`/midtempo-framework/instructions/db.md` # Database patterns"


def test_filter_raises_key_error_when_instruction_not_declared():
    """Filter raises clear KeyError when instruction missing from config."""
    # Setup environment
    template_dir = Path(tempfile.gettempdir())
    env = setup_jinja_environment(template_dir)

    # Template requesting instruction
    template_str = '{{ "db" | instructions }}'
    template = env.from_string(template_str)

    # Config with empty instructions namespace
    config = {"instructions": InstructionsNamespace({})}

    # Should raise KeyError
    try:
        template.render(config)
        raise AssertionError("Expected KeyError for missing instruction")
    except KeyError as e:
        error_msg = str(e).lower()
        assert "db" in error_msg
        assert "not found" in error_msg or "instruction" in error_msg


def test_conditional_check_evaluates_false_for_missing_instruction():
    """Jinja2 conditional evaluates false when instruction key missing from config."""
    # Setup environment
    template_dir = Path(tempfile.gettempdir())
    env = setup_jinja_environment(template_dir)

    # Template with conditional check using attribute access
    template_str = "{% if instructions.db %}READ instructions{% else %}No instruction{% endif %}"
    template = env.from_string(template_str)

    # Config with instructions namespace wrapper
    config = {"instructions": InstructionsNamespace({})}

    # Render template
    result = template.render(config)

    # Conditional should evaluate false, else block renders
    assert result == "No instruction"


# Schema Validation Tests


def test_valid_instruction_declaration_passes_validation():
    """jsonschema accepts config with valid instruction structure."""
    # Schema with instruction patternProperties
    schema = {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "type": "object",
        "properties": {
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
            }
        },
    }

    # Config with valid instruction
    config = {"instructions": {"db": {"page": "db.md", "description": "Database patterns"}}}

    # Should pass validation
    jsonschema.validate(config, schema)


def test_missing_page_field_fails_validation():
    """Schema rejects instruction without required page field."""
    schema = {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "type": "object",
        "properties": {
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
            }
        },
    }

    # Config with instruction missing page field
    config = {"instructions": {"db": {"description": "Database patterns"}}}

    # Should raise ValidationError
    try:
        jsonschema.validate(config, schema)
        raise AssertionError("Expected ValidationError for missing page")
    except jsonschema.ValidationError as e:
        error_msg = str(e).lower()
        assert "page" in error_msg or "required" in error_msg


def test_missing_description_field_fails_validation():
    """Schema rejects instruction without required description field."""
    schema = {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "type": "object",
        "properties": {
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
            }
        },
    }

    # Config with instruction missing description field
    config = {"instructions": {"db": {"page": "db.md"}}}

    # Should raise ValidationError
    try:
        jsonschema.validate(config, schema)
        raise AssertionError("Expected ValidationError for missing description")
    except jsonschema.ValidationError as e:
        error_msg = str(e).lower()
        assert "description" in error_msg or "required" in error_msg


def test_invalid_instruction_key_name_fails_validation():
    """patternProperties reject instruction keys not matching kebab-case pattern."""
    schema = {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "type": "object",
        "properties": {
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
            }
        },
    }

    # Config with uppercase instruction key (invalid)
    config = {"instructions": {"DB": {"page": "db.md", "description": "Database"}}}

    # Should raise ValidationError
    try:
        jsonschema.validate(config, schema)
        raise AssertionError("Expected ValidationError for invalid key name")
    except jsonschema.ValidationError as e:
        error_msg = str(e).lower()
        # Error could be about pattern or additionalProperties
        assert "additional" in error_msg or "pattern" in error_msg or "property" in error_msg


def test_extra_fields_in_instruction_fail_validation():
    """Schema rejects instruction with unexpected properties."""
    schema = {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "type": "object",
        "properties": {
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
            }
        },
    }

    # Config with instruction having extra field
    config = {
        "instructions": {
            "db": {
                "page": "db.md",
                "description": "Database",
                "extra": "value",
            }
        }
    }

    # Should raise ValidationError
    try:
        jsonschema.validate(config, schema)
        raise AssertionError("Expected ValidationError for extra fields")
    except jsonschema.ValidationError as e:
        error_msg = str(e).lower()
        assert "additional" in error_msg or "extra" in error_msg


def test_empty_instructions_dict_passes_validation():
    """Schema accepts config with empty instructions dict (instructions optional)."""
    schema = {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "type": "object",
        "properties": {
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
            }
        },
    }

    # Config with empty instructions object
    config: dict[str, dict] = {"instructions": {}}

    # Should pass validation
    jsonschema.validate(config, schema)


# End-to-End Integration Tests


def test_template_conditional_renders_instruction_reference():
    """Full workflow from config declaration to rendered documentation with instruction reference."""
    # Setup environment
    template_dir = Path(tempfile.gettempdir())
    env = setup_jinja_environment(template_dir)

    # Template with conditional and attribute access (as specified in plan)
    template_str = (
        "{% if instructions.db %}READ: `instructions/{{ instructions.db.page }}`{% endif %}"
    )
    template = env.from_string(template_str)

    # Valid config dict for schema validation
    config_dict = {"instructions": {"db": {"page": "db.md", "description": "Database patterns"}}}

    # Validate with schema first
    schema = {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "type": "object",
        "properties": {
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
            }
        },
    }
    jsonschema.validate(config_dict, schema)

    # Wrap instructions for template rendering
    config_for_rendering = {"instructions": InstructionsNamespace(config_dict["instructions"])}

    # Render template
    result = template.render(config_for_rendering)

    # Should render instruction reference
    assert result == "READ: `instructions/db.md`"


def test_template_skips_undeclared_instruction():
    """Template gracefully handles missing optional instruction without error."""
    # Setup environment
    template_dir = Path(tempfile.gettempdir())
    env = setup_jinja_environment(template_dir)

    # Template checking for instructions.db using attribute access
    template_str = (
        "{% if instructions.db %}READ: `instructions/{{ instructions.db.page }}`{% endif %}"
    )
    template = env.from_string(template_str)

    # Config declares instructions.api only (not db)
    config = {
        "instructions": InstructionsNamespace({"api": {"page": "api.md", "description": "API"}})
    }

    # Render template
    result = template.render(config)

    # Conditional should evaluate false, no output from if block
    assert result == ""


def test_config_without_instructions_key_enriched_to_empty_dict():
    """Config enrichment provides empty dict when instructions key missing.

    Integration test verifying configs without instructions key get enriched
    with empty dict for backward compatibility with existing configs.

    Gate 1: Testing real behaviour (config enriched after generation) → VALID
    Gate 2: No test-only methods → VALID
    Gate 3: No mocks → VALID
    Gate 4: N/A → VALID
    Gate 5: Test isolated with temp files → VALID
    Gate 6: Boundary condition (missing instructions) and happy path → VALID
    """
    from scripts.generate_docs import generate_documentation_with_timing

    # Create minimal config without instructions key
    config_content = """
name: test-repo
repo:
  language:
    python: all
"""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".yml", delete=False) as f:
        f.write(config_content)
        config_path = Path(f.name)

    # Create template that checks instructions.db
    template_content = "{% if instructions.db %}DB FOUND{% else %}NO DB{% endif %}"
    template_dir = Path(tempfile.mkdtemp())
    agents_dir = template_dir / "agents"
    agents_dir.mkdir()
    (agents_dir / "test.md.j2").write_text(template_content)

    # Create output directory
    output_dir = Path(tempfile.mkdtemp())

    try:
        # Generate documentation - should not raise UndefinedError
        # After enrichment, config will have instructions: {}
        generate_documentation_with_timing(config_path, output_dir, template_dir)

        # Verify template rendered successfully
        output_file = output_dir / "agents" / "test-repo" / "test.md"
        assert output_file.exists(), f"Output file not found at {output_file}"
        content = output_file.read_text()
        assert content == "NO DB"
    finally:
        # Cleanup
        config_path.unlink()
        import shutil

        shutil.rmtree(template_dir)
        shutil.rmtree(output_dir)
