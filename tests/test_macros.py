"""Test macros.j2 template macros."""

import pytest
from jinja2 import Environment, FileSystemLoader

from scripts.paths import PROJECT_ROOT


@pytest.fixture
def jinja_env():
    """Create a Jinja2 environment with macros.j2 loaded."""
    template_dir = PROJECT_ROOT / "jinja-templates"
    env = Environment(loader=FileSystemLoader(template_dir))
    return env


@pytest.fixture
def macros_template(jinja_env):
    """Load the macros.j2 template."""
    return jinja_env.get_template("macros.j2")


def test_conditional_security_reads_all_flags_true(jinja_env, macros_template):
    """Test conditional_security_reads with all security flags enabled."""
    # Given: All security capability flags are true
    caps = {
        "hasUI": True,
        "hasDB": True,
        "hasAuthentication": True,
        "handlesConfidentialData": True,
        "isPublicFacing": True,
    }
    security_dict: dict[str, dict[str, str]] = {}

    # When: Render the macro
    template = jinja_env.from_string(
        "{% from 'macros.j2' import conditional_security_reads %}"
        "{{ conditional_security_reads(caps, security_dict) }}"
    )
    result = template.render(caps=caps, security_dict=security_dict)

    # Then: All 5 security domains should be included
    assert "secrets-management" in result
    assert "input-validation" in result
    assert "authentication" in result
    assert "data-protection" in result
    assert "public-hardening" in result
    # READ directives should be present
    assert "READ ALL of" in result
    assert "/midtempo-framework/rules/security/" in result


def test_conditional_security_reads_minimal_flags(jinja_env, macros_template):
    """Test conditional_security_reads with minimal security flags."""
    # Given: Only hasDB is true (should trigger secrets-management + input-validation)
    caps = {
        "hasUI": False,
        "hasDB": True,
        "hasAuthentication": False,
        "handlesConfidentialData": False,
        "isPublicFacing": False,
    }
    security_dict: dict[str, dict[str, str]] = {}

    # When: Render the macro
    template = jinja_env.from_string(
        "{% from 'macros.j2' import conditional_security_reads %}"
        "{{ conditional_security_reads(caps, security_dict) }}"
    )
    result = template.render(caps=caps, security_dict=security_dict)

    # Then: Only secrets-management and input-validation should be included
    assert "secrets-management" in result
    assert "input-validation" in result
    assert "authentication" not in result
    assert "data-protection" not in result
    assert "public-hardening" not in result


def test_conditional_security_reads_respects_security_config(jinja_env, macros_template):
    """Test conditional_security_reads respects optional security config section."""
    # Given: Security config overrides with custom domains
    caps = {
        "hasUI": False,
        "hasDB": False,
        "hasAuthentication": False,
        "handlesConfidentialData": False,
        "isPublicFacing": False,
    }
    security_dict = {
        "secrets-management": {"page": "secrets.md", "description": "Secret handling"},
        "custom-domain": {"page": "custom.md", "description": "Custom security"},
    }

    # When: Render the macro
    template = jinja_env.from_string(
        "{% from 'macros.j2' import conditional_security_reads %}"
        "{{ conditional_security_reads(caps, security_dict) }}"
    )
    result = template.render(caps=caps, security_dict=security_dict)

    # Then: Should use configured domains, not auto-detected ones
    assert "secrets.md" in result
    assert "custom.md" in result


def test_verify_compliance_gates_security_all_domains(jinja_env, macros_template):
    """Test verify_compliance_gates_security with all domains applicable."""
    # Given: All security flags are true
    caps = {
        "hasUI": True,
        "hasDB": True,
        "hasAuthentication": True,
        "handlesConfidentialData": True,
        "isPublicFacing": True,
    }
    security_dict: dict[str, dict[str, str]] = {}

    # When: Render the macro
    template = jinja_env.from_string(
        "{% from 'macros.j2' import verify_compliance_gates_security %}"
        "{{ verify_compliance_gates_security(caps, security_dict) }}"
    )
    result = template.render(caps=caps, security_dict=security_dict)

    # Then: All security domains should have STOP blocks
    assert "secrets-management" in result
    assert "input-validation" in result
    assert "authentication" in result
    assert "data-protection" in result
    assert "public-hardening" in result
    # Verification pattern should be present
    assert "IF delivery scope touches" in result
    assert "Compliance Gates" in result
    assert "STOP" in result


def test_verify_compliance_gates_security_minimal_domains(jinja_env, macros_template):
    """Test verify_compliance_gates_security with minimal domains."""
    # Given: Only universal domain applies
    caps = {
        "hasUI": False,
        "hasDB": False,
        "hasAuthentication": False,
        "handlesConfidentialData": False,
        "isPublicFacing": False,
    }
    security_dict: dict[str, dict[str, str]] = {}

    # When: Render the macro
    template = jinja_env.from_string(
        "{% from 'macros.j2' import verify_compliance_gates_security %}"
        "{{ verify_compliance_gates_security(caps, security_dict) }}"
    )
    result = template.render(caps=caps, security_dict=security_dict)

    # Then: Only secrets-management should have STOP block
    assert "secrets-management" in result
    assert "authentication" not in result
    assert "data-protection" not in result
    assert "public-hardening" not in result


def test_security_cg_range_returns_correct_range(jinja_env, macros_template):
    """Test security_cg_range returns the correct compliance gate range."""
    # When: Render the macro
    template = jinja_env.from_string(
        "{% from 'macros.j2' import security_cg_range %}" "{{ security_cg_range() }}"
    )
    result = template.render()

    # Then: Should return CG-S1–CG-S5 range
    assert "CG-S1" in result
    assert "CG-S5" in result


def test_security_compliance_gates_summary_returns_gate_list(jinja_env, macros_template):
    """Test security_compliance_gates_summary returns brief gate list."""
    # When: Render the macro
    template = jinja_env.from_string(
        "{% from 'macros.j2' import security_compliance_gates_summary %}"
        "{{ security_compliance_gates_summary() }}"
    )
    result = template.render()

    # Then: Should return list of universal security gates
    assert "CG-S" in result
    # Should contain brief descriptions
    assert len(result) > 0
    # Should be compact (not full descriptions)
    assert len(result) < 500  # Reasonable limit for summary


def test_conditional_security_reads_routes_to_instructions_when_explicit_config(
    jinja_env, macros_template
):
    """Security domains with explicit config should read from instructions/ folder."""
    # Given: Explicit security config (not auto-detected)
    caps = {
        "hasUI": False,
        "hasDB": False,
        "hasAuthentication": False,
        "handlesConfidentialData": False,
        "isPublicFacing": False,
    }
    security_dict = {
        "secrets-management": {
            "page": "secrets-management.md",
            "description": "Secret handling",
        },
        "custom-domain": {"page": "custom.md", "description": "Custom security"},
    }

    # When: Render the macro
    template = jinja_env.from_string(
        "{% from 'macros.j2' import conditional_security_reads %}"
        "{{ conditional_security_reads(caps, security_dict) }}"
    )
    result = template.render(caps=caps, security_dict=security_dict)

    # Then: Should use instructions/ path for explicit config
    assert "/midtempo-framework/instructions/secrets-management.md" in result
    assert "/midtempo-framework/instructions/custom.md" in result
    # Should NOT use rules/security/ path
    assert "/midtempo-framework/rules/security/" not in result


def test_read_file_renders_single_line_without_verify_block(jinja_env):
    """read_file renders a READ line with no VERIFY-COMPLETE-READ block."""
    template = jinja_env.from_string(
        "{% from 'macros.j2' import read_file %}"
        "{{ read_file('/midtempo-framework/rules/writing.md', 'before proceeding') }}"
    )
    result = template.render()

    assert "READ ALL of `/midtempo-framework/rules/writing.md`" in result
    assert "before proceeding" in result
    assert "VERIFY-COMPLETE-READ" not in result


def test_read_file_with_context_omitted(jinja_env):
    """read_file without context renders just the READ line."""
    template = jinja_env.from_string(
        "{% from 'macros.j2' import read_file %}" "{{ read_file('/some/file.md') }}"
    )
    result = template.render()

    assert "READ ALL of `/some/file.md`" in result
    assert "VERIFY-COMPLETE-READ" not in result


def test_entry_gate_reads_emits_single_verification_header(jinja_env):
    """entry_gate_reads emits one shared verification header before file list."""
    ctx = {
        "instructions": {
            "purpose": {"page": "purpose.md"},
            "architecture": {"page": "architecture.md"},
        }
    }
    template = jinja_env.from_string(
        "{% from 'macros.j2' import entry_gate_reads %}"
        "{{ entry_gate_reads(ctx, instructions=['purpose', 'architecture']) }}"
    )
    result = template.render(ctx=ctx)

    # Should contain both file paths
    assert "purpose.md" in result
    assert "architecture.md" in result
    # Should contain exactly one VERIFY-COMPLETE-READ header
    assert result.count("VERIFY-COMPLETE-READ") == 1


def test_require_rules_read_emits_single_verification_header(jinja_env):
    """require_rules_read emits one shared verification header."""
    template = jinja_env.from_string(
        "{% from 'macros.j2' import require_rules_read %}"
        "{{ require_rules_read(['writing', 'testing']) }}"
    )
    result = template.render()

    assert "writing.md" in result
    assert "testing.md" in result
    assert result.count("VERIFY-COMPLETE-READ") == 1


def test_conditional_security_reads_emits_single_verification_header(jinja_env):
    """conditional_security_reads emits one shared verification header."""
    caps = {
        "hasUI": True,
        "hasDB": True,
        "hasAuthentication": True,
        "handlesConfidentialData": False,
        "isPublicFacing": False,
    }
    template = jinja_env.from_string(
        "{% from 'macros.j2' import conditional_security_reads %}"
        "{{ conditional_security_reads(caps, security_dict) }}"
    )
    result = template.render(caps=caps, security_dict={})

    # Multiple domains rendered
    assert "secrets-management" in result
    assert "input-validation" in result
    assert "authentication" in result
    # Only one verification header
    assert result.count("VERIFY-COMPLETE-READ") == 1


def test_conditional_security_reads_routes_to_security_when_auto_detected(
    jinja_env, macros_template
):
    """Auto-detected security domains should read from rules/security/ folder."""
    # Given: No explicit security config (auto-detection)
    caps = {
        "hasUI": False,
        "hasDB": True,  # Triggers auto-detection of input-validation
        "hasAuthentication": False,
        "handlesConfidentialData": False,
        "isPublicFacing": False,
    }
    security_dict: dict[str, dict[str, str]] = {}

    # When: Render the macro
    template = jinja_env.from_string(
        "{% from 'macros.j2' import conditional_security_reads %}"
        "{{ conditional_security_reads(caps, security_dict) }}"
    )
    result = template.render(caps=caps, security_dict=security_dict)

    # Then: Should use rules/security/ path for auto-detected domains
    assert "/midtempo-framework/rules/security/secrets-management.md" in result
    assert "/midtempo-framework/rules/security/input-validation.md" in result
    # Should NOT use instructions/ path
    assert "/midtempo-framework/instructions/" not in result


def test_exit_gate_requirements_renders_critical_requirement_block(jinja_env):
    """exit_gate_requirements renders CRITICAL_REQUIREMENT block with reason."""
    template = jinja_env.from_string(
        "{% from 'macros.j2' import exit_gate_requirements %}" "{{ exit_gate_requirements() }}"
    )
    result = template.render()

    assert '<CRITICAL_REQUIREMENT type="MANDATORY">' in result
    assert "after Exit Gate passes" in result
    assert "MUST produce this output" in result
    assert "MUST NOT skip, paraphrase, or omit any section" in result
    assert "MUST format the output for readability" in result
    assert "</CRITICAL_REQUIREMENT>" in result


def test_exit_gate_requirements_accepts_custom_reason(jinja_env):
    """exit_gate_requirements renders with custom reason text."""
    template = jinja_env.from_string(
        "{% from 'macros.j2' import exit_gate_requirements %}"
        '{{ exit_gate_requirements(reason="before closing the phase") }}'
    )
    result = template.render()

    assert "before closing the phase" in result
    assert "after Exit Gate passes" not in result


def test_exit_gate_requirements_renders_extra_rules(jinja_env):
    """exit_gate_requirements appends extra rules as additional bullets."""
    template = jinja_env.from_string(
        "{% from 'macros.j2' import exit_gate_requirements %}"
        '{{ exit_gate_requirements(extra_rules=["You MUST NOT produce this output when tests pass or error without human approval"]) }}'
    )
    result = template.render()

    # Standard rules still present
    assert "MUST produce this output" in result
    assert "MUST NOT skip, paraphrase, or omit any section" in result
    assert "MUST format the output for readability" in result
    # Extra rule appended
    assert (
        "- You MUST NOT produce this output when tests pass or error without human approval"
        in result
    )
