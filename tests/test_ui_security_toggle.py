"""Tests for the security entry toggle via double-click on the YAML panel.

Double-clicking a commented security entry activates it (removes # prefix).
Double-clicking an active security entry deactivates it (restores # prefix).
Non-security double-clicks fall through to openCommandModalFromYaml.

Covers:
- T1: resolveYamlClickedLine exported from command-modal.js and uses TreeWalker
- T2: openCommandModalFromYaml delegates line resolution to resolveYamlClickedLine
- T3: handleYamlDblclick exists in form.js and checks SECURITY_ENTRIES keys
- T4: handleYamlDblclick calls setState with a security patch
- T5: handleYamlDblclick falls through to openCommandModalFromYaml for non-security lines
- T6: refreshYAML excludes state.security from the main jsyaml.dump
- T7: refreshYAML renders the security header without # when any entry is active
- T8: dblclick on yaml-panel is wired to handleYamlDblclick
"""

import re
from pathlib import Path

FORM_JS = Path("ui/js/form.js")
WIRING_FILE = Path("ui/js/event-wiring.js")  # event listener wiring lives here
CMD_MODAL_JS = Path("ui/js/command-modal.js")


def _extract_function_body(content: str, fn_name: str) -> str:
    """Return the body of a named function from JS source using brace-matching.

    Handles declaration form (function name(...) {) and assignment form
    (name = function(...) { or name = (...) => {).
    Returns the text between the outermost braces (exclusive).
    Returns an empty string when the function is not found.
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


class TestResolveYamlClickedLine:
    """T1 — resolveYamlClickedLine is exported from command-modal.js and uses TreeWalker."""

    def test_resolve_yaml_clicked_line_is_exported(self):
        """command-modal.js exports resolveYamlClickedLine. (T1)"""
        content = CMD_MODAL_JS.read_text()
        assert re.search(
            r"export\s+function\s+resolveYamlClickedLine", content
        ), "resolveYamlClickedLine not exported from command-modal.js"

    def test_resolve_yaml_clicked_line_uses_tree_walker(self):
        """resolveYamlClickedLine body uses createTreeWalker for line resolution. (T1)"""
        content = CMD_MODAL_JS.read_text()
        body = _extract_function_body(content, "resolveYamlClickedLine")
        assert body, "resolveYamlClickedLine function body not found in command-modal.js"
        assert "createTreeWalker" in body, (
            "resolveYamlClickedLine does not use createTreeWalker — "
            "line resolution will not work on highlight.js span elements"
        )


class TestOpenCommandModalFromYamlDelegates:
    """T2 — openCommandModalFromYaml delegates line resolution to resolveYamlClickedLine."""

    def test_open_command_modal_calls_resolve_yaml_clicked_line(self):
        """openCommandModalFromYaml calls resolveYamlClickedLine instead of inlining TreeWalker logic. (T2)"""
        content = CMD_MODAL_JS.read_text()
        body = _extract_function_body(content, "openCommandModalFromYaml")
        assert body, "openCommandModalFromYaml function body not found in command-modal.js"
        assert "resolveYamlClickedLine" in body, (
            "openCommandModalFromYaml does not call resolveYamlClickedLine — "
            "line resolution logic is not shared with handleYamlDblclick"
        )


class TestResolveSecurityKey:
    """T3a — resolveSecurityKey walks backward from any security block line to find the entry key."""

    def test_resolve_security_key_function_exists(self):
        """form.js declares resolveSecurityKey. (T3a)"""
        content = FORM_JS.read_text()
        assert re.search(
            r"function\s+resolveSecurityKey", content
        ), "resolveSecurityKey function not found in form.js"

    def test_resolve_security_key_references_security_entries(self):
        """resolveSecurityKey body references SECURITY_ENTRIES to match entry key lines. (T3a)"""
        content = FORM_JS.read_text()
        body = _extract_function_body(content, "resolveSecurityKey")
        assert body, "resolveSecurityKey function body not found in form.js"
        assert "SECURITY_ENTRIES" in body, (
            "resolveSecurityKey does not reference SECURITY_ENTRIES — "
            "entry keys will not be detected during the backward walk"
        )

    def test_resolve_security_key_walks_backward(self):
        """resolveSecurityKey walks backward through lines (i-- or i >= 0 loop). (T3a)"""
        content = FORM_JS.read_text()
        body = _extract_function_body(content, "resolveSecurityKey")
        assert body, "resolveSecurityKey function body not found in form.js"
        assert re.search(
            r"i--", body
        ), "resolveSecurityKey does not decrement i — backward walk not implemented"


class TestHandleYamlDblclick:
    """T3-T5 — handleYamlDblclick exists in form.js, delegates to resolveSecurityKey, and falls through."""

    def test_handle_yaml_dblclick_function_exists(self):
        """form.js declares handleYamlDblclick. (T3)"""
        content = FORM_JS.read_text()
        assert re.search(
            r"function\s+handleYamlDblclick", content
        ), "handleYamlDblclick function not found in form.js"

    def test_handle_yaml_dblclick_calls_resolve_security_key(self):
        """handleYamlDblclick delegates security line detection to resolveSecurityKey. (T3)"""
        content = FORM_JS.read_text()
        body = _extract_function_body(content, "handleYamlDblclick")
        assert body, "handleYamlDblclick function body not found in form.js"
        assert "resolveSecurityKey" in body, (
            "handleYamlDblclick does not call resolveSecurityKey — "
            "page and description lines within security entries will not be detected"
        )

    def test_handle_yaml_dblclick_calls_set_state_with_security(self):
        """handleYamlDblclick calls setState with a security patch when a security line is clicked. (T4)"""
        content = FORM_JS.read_text()
        body = _extract_function_body(content, "handleYamlDblclick")
        assert body, "handleYamlDblclick function body not found in form.js"
        assert "setState" in body, (
            "handleYamlDblclick does not call setState — "
            "security toggle will not update state or re-render the YAML panel"
        )
        assert "security" in body, (
            "handleYamlDblclick does not reference 'security' — "
            "setState patch will not update state.security"
        )

    def test_handle_yaml_dblclick_falls_through_to_command_modal(self):
        """handleYamlDblclick calls openCommandModalFromYaml for non-security lines. (T5)"""
        content = FORM_JS.read_text()
        body = _extract_function_body(content, "handleYamlDblclick")
        assert body, "handleYamlDblclick function body not found in form.js"
        assert "openCommandModalFromYaml" in body, (
            "handleYamlDblclick does not call openCommandModalFromYaml — "
            "command block double-click will stop working"
        )


class TestRefreshYamlSecurityRendering:
    """T6-T7 — refreshYAML excludes state.security from jsyaml.dump and renders active entries without #."""

    def test_refresh_yaml_excludes_security_from_main_dump(self):
        """refreshYAML destructures state.security out before calling jsyaml.dump. (T6)"""
        content = FORM_JS.read_text()
        body = _extract_function_body(content, "refreshYAML")
        assert body, "refreshYAML function body not found in form.js"
        # Destructuring pattern: const { security, ...rest } = state  or  const { security } = state
        assert re.search(r"const\s*\{[^}]*security[^}]*\}\s*=\s*state", body), (
            "refreshYAML does not destructure state.security before jsyaml.dump — "
            "active security entries will appear twice (in main dump and security block)"
        )

    def test_refresh_yaml_renders_active_entry_without_hash(self):
        """refreshYAML renders active security entries (in state.security) without a # prefix. (T7)"""
        content = FORM_JS.read_text()
        body = _extract_function_body(content, "refreshYAML")
        assert body, "refreshYAML function body not found in form.js"
        # Active entries render as `  key:` (indented, no #)
        # The body should push lines without leading # for active entries
        # Check that the body has a branch that pushes a line NOT starting with #
        # and references entry.key — this indicates the active (uncommented) path
        assert re.search(r"push\(`\s+\$\{entry\.key\}", body), (
            "refreshYAML does not render active security entries without # — "
            "activated entries will still appear commented"
        )

    def test_refresh_yaml_renders_security_header_without_hash_when_active(self):
        """refreshYAML renders 'security:' (no #) as the block header when any entry is active. (T7)"""
        content = FORM_JS.read_text()
        body = _extract_function_body(content, "refreshYAML")
        assert body, "refreshYAML function body not found in form.js"
        # The header line must be conditional — not always "# security:"
        assert re.search(r'"security:"', body), (
            "refreshYAML never renders 'security:' without # — "
            "the block header will not uncomment when entries are activated"
        )


class TestDblclickWiring:
    """T8 — the yaml-panel dblclick listener is wired to handleYamlDblclick."""

    def test_yaml_panel_dblclick_wired_to_handle_yaml_dblclick(self):
        """event-wiring.js wires the yaml-panel dblclick to handleYamlDblclick. (T8)"""
        content = WIRING_FILE.read_text()
        assert re.search(
            r'addEventListener\s*\(\s*["\']dblclick["\']\s*,\s*handleYamlDblclick\s*\)',
            content,
        ), "yaml-panel dblclick listener not wired to handleYamlDblclick in event-wiring.js"
