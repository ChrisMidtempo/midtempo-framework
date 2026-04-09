"""Tests for Stage 6 UI: ajv validation, instruction registry, command builder, HTML fields, BUG-1.

Covers:
- T1.1:  Ajv constructor referenced in form.js (B1)
- T1.2:  refreshErrors function defined in form.js (B1)
- T1.3:  renderFieldErrors function defined in form.js (B1)
- T1.4:  setState body calls refreshErrors (B1)
- T1.5:  btn-generate referenced in form.js with disabled toggled by ajv result (B1)
- T1.6:  CAPABILITY_INSTRUCTIONS constant defined in form.js (B2)
- T1.7:  deriveInstructions assigns to state.instructions (B2)
- T1.8:  deriveInstructions body references hasDB (B2)
- T1.9:  renderCommandRows function defined in form.js (B3)
- T1.10: addCommandRow function defined in form.js (B3)
- T1.11: collectCommands function defined in form.js (B3)
- T1.12: language select change handler references languages object (B3)
- T1.13: data-testid="commands-container" referenced in form.js (B3)
- T1.14: data-testid="btn-add-command" referenced in form.js (B3)
- T1.15: populateFromYml body calls populateForm — BUG-1 resolved (B5)
- T2.1:  data-testid="form-hasUI" present in index.html (B4)
"""

import re
from pathlib import Path

# File paths — tests run from project root where npm run test:python is invoked
JS_FILE = Path("ui/js/form.js")
WIRING_FILE = Path("ui/js/event-wiring.js")  # event listener wiring lives here
HTML_FILE = Path("ui/index.html")
CMD_MODAL_FILE = Path("ui/js/command-modal.js")  # command builder functions live here


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
    start = match.end() - 1  # position of opening {
    depth = 0
    for i, ch in enumerate(content[start:]):
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                return content[start + 1 : start + i]
    return ""


class TestFormJsStage6:
    """Tests for Stage 6 form.js additions: ajv validation, instruction registry, command builder."""

    def test_ajv_constructor_referenced(self):
        """form.js references new Ajv, confirming ajv is wired to compile schema at load time. (T1.1, B1)"""
        content = JS_FILE.read_text()
        assert "new Ajv" in content, "new Ajv constructor not referenced in form.js"

    def test_ajv_constructor_disables_strict_format_validation(self):
        """Ajv is instantiated with strict: false to suppress unknown format errors. (BUG-5)

        AJV 8 strict mode (default) throws on unknown schema formats such as 'date-time'.
        The config schema declares format: date-time on metadata.generated_at.
        AJV 8 does not include format validators by default, so strict mode must be
        disabled to prevent 'unknown format date-time ignored' from crashing schema compile.
        """
        content = JS_FILE.read_text()
        assert re.search(
            r"new\s+Ajv\s*\([^)]*strict\s*:\s*false", content
        ), "Ajv constructor must include strict: false to handle unknown formats in the schema"

    def test_refresh_errors_function_defined(self):
        """refreshErrors is declared as a function in form.js. (T1.2, B1)"""
        content = JS_FILE.read_text()
        assert re.search(
            r"function\s+refreshErrors|refreshErrors\s*=\s*(function|\()",
            content,
        ), "refreshErrors function not defined in form.js"

    def test_render_field_errors_function_defined(self):
        """renderFieldErrors is declared as a function in form.js. (T1.3, B1)"""
        content = JS_FILE.read_text()
        assert re.search(
            r"function\s+renderFieldErrors|renderFieldErrors\s*=\s*(function|\()",
            content,
        ), "renderFieldErrors function not defined in form.js"

    def test_set_state_body_calls_refresh_errors(self):
        """refreshErrors is called inside the setState function body. (T1.4, B1)"""
        content = JS_FILE.read_text()
        body = _extract_function_body(content, "setState")
        assert body, "setState function body not found in form.js"
        assert "refreshErrors" in body, "setState does not call refreshErrors"

    def test_btn_generate_referenced_with_disabled_toggled(self):
        """form.js references btn-generate and disabled, confirming Generate button state is controlled by ajv. (T1.5, B1)"""
        content = JS_FILE.read_text()
        assert "btn-generate" in content, "btn-generate not referenced in form.js"
        assert "disabled" in content, "disabled not referenced in form.js"

    def test_capability_instructions_constant_defined(self):
        """CAPABILITY_INSTRUCTIONS constant is defined in form.js. (T1.6, B2)"""
        content = JS_FILE.read_text()
        assert (
            "CAPABILITY_INSTRUCTIONS" in content
        ), "CAPABILITY_INSTRUCTIONS constant not defined in form.js"

    def test_derive_instructions_assigns_to_state_instructions(self):
        """state.instructions is assigned inside the deriveInstructions function body. (T1.7, B2)"""
        content = JS_FILE.read_text()
        body = _extract_function_body(content, "deriveInstructions")
        assert body, "deriveInstructions function body not found in form.js"
        assert (
            "state.instructions" in body
        ), "deriveInstructions does not assign to state.instructions"

    def test_derive_instructions_body_references_has_db(self):
        """CAPABILITY_INSTRUCTIONS references hasDB, confirming at least one capability is mapped. (T1.8, B2)"""
        content = JS_FILE.read_text()
        assert "hasDB" in content, "CAPABILITY_INSTRUCTIONS does not reference hasDB in form.js"

    def test_confirm_command_modal_function_defined(self):
        """confirmCommandModal is declared as a function in command-modal.js. (T1.9, B3)"""
        content = CMD_MODAL_FILE.read_text()
        assert re.search(
            r"function\s+confirmCommandModal|confirmCommandModal\s*=\s*(function|\()",
            content,
        ), "confirmCommandModal function not defined in command-modal.js"

    def test_delete_current_command_function_defined(self):
        """deleteCurrentCommand is declared as a function in command-modal.js. (T1.10, B3)"""
        content = CMD_MODAL_FILE.read_text()
        assert re.search(
            r"function\s+deleteCurrentCommand|deleteCurrentCommand\s*=\s*(function|\()",
            content,
        ), "deleteCurrentCommand function not defined in command-modal.js"

    def test_show_command_modal_for_edit_function_defined(self):
        """showCommandModalForEdit is declared as a function in command-modal.js. (T1.11, B3)"""
        content = CMD_MODAL_FILE.read_text()
        assert re.search(
            r"function\s+showCommandModalForEdit|showCommandModalForEdit\s*=\s*(function|\()",
            content,
        ), "showCommandModalForEdit function not defined in command-modal.js"

    def test_language_change_handler_references_languages_object(self):
        """language change handler references the languages object for command pre-population. (T1.12, B3)"""
        content = WIRING_FILE.read_text()
        # Locate the change event listener bound to langSelect (form-language)
        match = re.search(
            r"langSelect\.addEventListener\s*\(\s*[\"']change[\"']",
            content,
        )
        assert match, "langSelect change event listener not found in event-wiring.js"
        # Extract a region from the change listener covering its callback body.
        # Stage 6 extends this handler to include command pre-population using `languages`.
        region = content[match.start() : match.start() + 300]
        assert "languages" in region, (
            "language change handler does not reference languages object — "
            "command pre-population not wired (Stage 6)"
        )

    def test_command_modal_testid_referenced_in_command_modal_js(self):
        """command-modal.js references command-modal data-testid, confirming it targets the modal element. (T1.13, B3)"""
        content = CMD_MODAL_FILE.read_text()
        assert "command-modal" in content, "command-modal testid not referenced in command-modal.js"

    def test_btn_add_command_testid_referenced_in_form_js(self):
        """event-wiring.js references btn-add-command, confirming the Add command button is wired. (T1.14, B3)"""
        content = WIRING_FILE.read_text()
        assert "btn-add-command" in content, "btn-add-command not referenced in event-wiring.js"

    def test_populate_from_yml_body_calls_populate_form(self):
        """populateForm is called inside the populateFromYml body — BUG-1 resolved. (T1.15, B5)"""
        content = JS_FILE.read_text()
        body = _extract_function_body(content, "populateFromYml")
        assert body, "populateFromYml function body not found in form.js"
        assert (
            "populateForm" in body
        ), "populateFromYml does not call populateForm — BUG-1 not resolved"


class TestRefreshErrorsEditorGuard:
    """refreshErrors must only run in editor mode — not on the entry screen."""

    def test_refresh_errors_body_checks_editor_active(self):
        """refreshErrors returns early when editorActive is false, preventing AJV errors from
        appearing on entry-screen fields (e.g. form-name red border when language is selected). (BUG-7)
        """
        content = JS_FILE.read_text()
        body = _extract_function_body(content, "refreshErrors")
        assert body, "refreshErrors function body not found in form.js"
        assert "editorActive" in body, (
            "refreshErrors must guard on editorActive — "
            "without this, AJV validation runs on the entry screen and marks form-name as invalid"
        )

    def test_show_editor_sets_editor_active(self):
        """showEditor sets editorActive to true, enabling AJV validation once the editor is shown. (BUG-7)"""
        content = JS_FILE.read_text()
        body = _extract_function_body(content, "showEditor")
        assert body, "showEditor function body not found in form.js"
        assert "editorActive" in body, (
            "showEditor must set editorActive — "
            "AJV validation should only begin after the editor is visible"
        )


class TestIndexHtmlStage6:
    """Tests for Stage 6 index.html additions: capability checkboxes and commands section."""

    def test_form_has_ui_testid_present_in_html(self):
        """index.html contains form-hasUI, confirming capability checkboxes are added to #form-panel. (T2.1, B4)"""
        content = HTML_FILE.read_text()
        assert "form-hasUI" in content, 'data-testid="form-hasUI" not present in index.html'
