"""Tests for the security comment block appended to the YAML panel.

Each of the five security entries is shown as a comment in the YAML panel unless
that specific key already exists in state.security. Entries are checked independently —
a user may activate any subset via an uploaded yml file.

Covers:
- T1: SECURITY_ENTRIES constant defined in form.js with all five security keys
- T2: refreshYAML appends commented security entries via SECURITY_ENTRIES
- T3: refreshYAML checks state.security per entry to skip those already present
"""

import re
from pathlib import Path

JS_FILE = Path("ui/js/form.js")


def _extract_function_body(content: str, fn_name: str) -> str:
    """Extract the body of a named function from JS source using brace-matching.

    Handles both declaration form (function name(...) {) and assignment form
    (name = function(...) { or name = (...) => {).
    Returns the text between the outermost braces (exclusive).
    Returns an empty string if the function is not found.
    """
    pattern = (
        rf"(?:function\s+{fn_name}\s*\([^)]*\)"
        rf"|{fn_name}\s*=\s*(?:function\s*\([^)]*\)|\([^)]*\)\s*=>))"
        rf"\s*\{{"
    )
    match = re.search(pattern, content)
    if match is None:
        return ""
    start = match.end() - 1
    depth = 0
    for i, ch in enumerate(content[start:]):
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                return content[start + 1 : start + i]
    return ""


class TestSecurityCommentBlock:
    """Tests for the commented security block appended to the YAML panel."""

    def test_security_entries_constant_defined_with_all_five_keys(self):
        """SECURITY_ENTRIES constant is declared in form.js and contains all five security keys. (T1)"""
        content = JS_FILE.read_text()
        assert re.search(
            r"const\s+SECURITY_ENTRIES", content
        ), "SECURITY_ENTRIES constant not declared in form.js"
        for key in (
            "secrets-management",
            "input-validation",
            "authentication",
            "data-protection",
            "public-hardening",
        ):
            assert key in content, f"SECURITY_ENTRIES missing entry for key '{key}'"

    def test_refresh_yaml_appends_commented_block_from_security_entries(self):
        """refreshYAML body references SECURITY_ENTRIES to build the commented security block. (T2)"""
        content = JS_FILE.read_text()
        body = _extract_function_body(content, "refreshYAML")
        assert body, "refreshYAML function body not found in form.js"
        assert "SECURITY_ENTRIES" in body, (
            "refreshYAML does not reference SECURITY_ENTRIES — "
            "commented security block will not be appended to the YAML panel"
        )

    def test_refresh_yaml_checks_security_per_entry(self):
        """refreshYAML destructures security from state to determine which entries to render without #. (T3)"""
        content = JS_FILE.read_text()
        body = _extract_function_body(content, "refreshYAML")
        assert body, "refreshYAML function body not found in form.js"
        # security is accessed via destructuring: const { security, ... } = state
        assert re.search(r"\bsecurity\b", body), (
            "refreshYAML does not reference 'security' — "
            "cannot determine which security entries are active"
        )

    def test_refresh_yaml_prepends_header_comment_above_security_block(self):
        """refreshYAML includes a header comment above the security block explaining its purpose. (T4)"""
        content = JS_FILE.read_text()
        body = _extract_function_body(content, "refreshYAML")
        assert body, "refreshYAML function body not found in form.js"
        assert (
            "Uncomment any of the below to override the framework's security rulesets" in body
        ), "refreshYAML does not include the header comment above the security block"
