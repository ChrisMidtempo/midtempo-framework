"""Tests for Stage 5 UI: ui/form.js state machinery, form population, YAML panel, and event wiring.

Covers:
- T1.1:  state object defined with top-level keys name, repo, capabilities, commands, instructions (B1)
- T1.2:  state.capabilities declares all six capability flags (B2)
- T1.3:  setState function defined (B3)
- T1.4:  deriveInstructions function defined (B4)
- T1.5:  setState body calls refreshYAML (B5)
- T1.6:  populateFromYml function defined (B6)
- T1.7:  populateFromYml body calls jsyaml.load (B7)
- T1.8:  populateForm function defined (B8)
- T1.9:  refreshYAML function defined (B9)
- T1.10: refreshYAML body calls jsyaml.dump (B10)
- T1.11: fetch call to /languages.json present (B11)
- T1.12: Promise.all present in form.js (B12)
- T1.13: upload error assigned via textContent not innerHTML (B13)
- T1.14: showEditor called inside populateFromYml body (B14)
- T1.15: data-testid upload-error referenced in form.js (B15)

Refinement — Language select optgroup grouping:
- T6.1:  LANGUAGE_GROUPS defined in name-field.js with JS/TS as first group
- T6.2:  populateLanguageSelect body creates optgroup elements
- T6.3:  populateLanguageSelect body appends ungrouped languages to an "Other" group
"""

import re
from pathlib import Path

# File paths — tests run from project root where npm run test:python is invoked
JS_FILE = Path("ui/js/form.js")
WIRING_FILE = Path("ui/js/event-wiring.js")  # event listener wiring lives here
NAME_JS_FILE = Path("ui/js/name-field.js")  # handleFileUpload and upload-error live here


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


class TestFormJsStage5:
    """Tests for Stage 5 form.js additions: state object, functions, and event wiring."""

    def test_state_object_defined_with_required_top_level_keys(self):
        """state const defines all five required top-level keys. (T1.1, B1)"""
        content = JS_FILE.read_text()
        assert "const state" in content, "state object not defined in form.js"
        for key in ("name", "repo", "capabilities", "commands", "instructions"):
            assert re.search(rf"\b{key}\s*:", content), f"state.{key} key missing in form.js"

    def test_state_capabilities_declares_all_six_flags(self):
        """state.capabilities declares all six capability flags. (T1.2, B2)"""
        content = JS_FILE.read_text()
        flags = (
            "hasUI",
            "hasDB",
            "hasTypecheck",
            "isPublicFacing",
            "handlesConfidentialData",
            "hasAuthentication",
        )
        for flag in flags:
            assert flag in content, f"capability flag '{flag}' missing from form.js"

    def test_set_state_function_defined(self):
        """setState is declared as a function in form.js. (T1.3, B3)"""
        content = JS_FILE.read_text()
        assert re.search(
            r"function\s+setState|setState\s*=\s*(function|\()",
            content,
        ), "setState function not defined in form.js"

    def test_derive_instructions_function_defined(self):
        """deriveInstructions is declared as a function in form.js. (T1.4, B4)"""
        content = JS_FILE.read_text()
        assert re.search(
            r"function\s+deriveInstructions|deriveInstructions\s*=\s*(function|\()",
            content,
        ), "deriveInstructions function not defined in form.js"

    def test_set_state_body_calls_refresh_yaml(self):
        """refreshYAML is called inside the setState function body. (T1.5, B5)"""
        content = JS_FILE.read_text()
        body = _extract_function_body(content, "setState")
        assert body, "setState function body not found in form.js"
        assert "refreshYAML" in body, "setState does not call refreshYAML"

    def test_populate_from_yml_function_defined(self):
        """populateFromYml is declared as a function in form.js. (T1.6, B6)"""
        content = JS_FILE.read_text()
        assert re.search(
            r"function\s+populateFromYml|populateFromYml\s*=\s*(function|\()",
            content,
        ), "populateFromYml function not defined in form.js"

    def test_populate_from_yml_body_calls_jsyaml_load(self):
        """jsyaml.load is called inside the populateFromYml function body. (T1.7, B7)"""
        content = JS_FILE.read_text()
        body = _extract_function_body(content, "populateFromYml")
        assert body, "populateFromYml function body not found in form.js"
        assert "jsyaml.load" in body, "populateFromYml does not call jsyaml.load"

    def test_populate_form_function_defined(self):
        """populateForm is declared as a function in form.js. (T1.8, B8)"""
        content = JS_FILE.read_text()
        assert re.search(
            r"function\s+populateForm|populateForm\s*=\s*(function|\()",
            content,
        ), "populateForm function not defined in form.js"

    def test_refresh_yaml_function_defined(self):
        """refreshYAML is declared as a function in form.js. (T1.9, B9)"""
        content = JS_FILE.read_text()
        assert re.search(
            r"function\s+refreshYAML|refreshYAML\s*=\s*(function|\()",
            content,
        ), "refreshYAML function not defined in form.js"

    def test_refresh_yaml_body_calls_jsyaml_dump(self):
        """jsyaml.dump is called inside the refreshYAML function body. (T1.10, B10)"""
        content = JS_FILE.read_text()
        body = _extract_function_body(content, "refreshYAML")
        assert body, "refreshYAML function body not found in form.js"
        assert "jsyaml.dump" in body, "refreshYAML does not call jsyaml.dump"

    def test_fetch_languages_json_call_present(self):
        """form.js contains a fetch call referencing /languages.json. (T1.11, B11)"""
        content = JS_FILE.read_text()
        assert "languages.json" in content, "fetch('/languages.json') not found in form.js"

    def test_promise_all_present(self):
        """Promise.all is present in form.js confirming concurrent load pattern. (T1.12, B12)"""
        content = JS_FILE.read_text()
        assert "Promise.all" in content, "Promise.all not found in form.js"

    def test_upload_error_assigned_via_text_content_not_inner_html(self):
        """Upload error slot uses textContent not innerHTML — XSS prevention CG-IV6. (T1.13, B13)

        handleFileUpload lives in name-field.js; upload-error DOM interaction is there.
        """
        content = NAME_JS_FILE.read_text()
        # The upload-error element may be cached in a local variable (e.g. uploadErrorEl).
        # Collect all lines that reference either the selector or any derived variable name.
        upload_related_lines = [
            line
            for line in content.splitlines()
            if "upload-error" in line or "uploadErrorEl" in line
        ]
        assert any(
            ".textContent" in line for line in upload_related_lines
        ), "upload-error element not assigned via .textContent in name-field.js"
        assert not any(
            ".innerHTML" in line for line in upload_related_lines
        ), "upload-error element assigned via .innerHTML (XSS risk) in name-field.js"

    def test_populate_from_yml_body_calls_show_editor(self):
        """showEditor is called inside the populateFromYml function body. (T1.14, B14)"""
        content = JS_FILE.read_text()
        body = _extract_function_body(content, "populateFromYml")
        assert body, "populateFromYml function body not found in form.js"
        assert "showEditor" in body, "populateFromYml does not call showEditor"

    def test_show_editor_called_before_set_state_in_populate_from_yml(self):
        """showEditor is called before setState in populateFromYml so editorActive is true when refreshErrors runs. (T1.16)

        refreshErrors guards on editorActive — if setState runs first (while editorActive is false),
        the Generate button stays disabled on first load until the next state change.
        Root cause: showEditor() must set editorActive = true before setState() triggers refreshErrors().
        """
        content = JS_FILE.read_text()
        body = _extract_function_body(content, "populateFromYml")
        assert body, "populateFromYml function body not found in form.js"
        assert "showEditor" in body, "populateFromYml does not call showEditor"
        assert "setState" in body, "populateFromYml does not call setState"
        show_editor_pos = body.index("showEditor")
        set_state_pos = body.index("setState")
        assert show_editor_pos < set_state_pos, (
            "showEditor() must be called before setState() in populateFromYml — "
            "editorActive must be true before refreshErrors runs, otherwise the Generate button "
            "stays disabled on first load"
        )

    def test_upload_error_testid_referenced_in_name_field_js(self):
        """name-field.js queries the upload-error testid element via handleFileUpload. (T1.15, B15)"""
        content = NAME_JS_FILE.read_text()
        assert "upload-error" in content, "data-testid upload-error not referenced in name-field.js"


class TestCapabilityInstructions:
    """Tests for the correct CAPABILITY_INSTRUCTIONS and BASE_INSTRUCTIONS constants."""

    def _extract_const_block(self, content: str, const_name: str) -> str:
        """Extract the value block of a const declaration by brace-matching.

        Returns the text between the outermost braces (exclusive), or an empty string
        when the constant is not found.
        """
        pattern = rf"const\s+{const_name}\s*=\s*\{{"
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

    def test_base_instructions_constant_defined(self):
        """BASE_INSTRUCTIONS const is declared in form.js. (T2.1)"""
        content = JS_FILE.read_text()
        assert re.search(
            r"const\s+BASE_INSTRUCTIONS\s*=", content
        ), "BASE_INSTRUCTIONS constant not declared in form.js"

    def test_base_instructions_contains_purpose(self):
        """BASE_INSTRUCTIONS includes a purpose entry with page purpose.md. (T2.2)"""
        content = JS_FILE.read_text()
        block = self._extract_const_block(content, "BASE_INSTRUCTIONS")
        assert block, "BASE_INSTRUCTIONS block not extractable from form.js"
        assert "purpose" in block, "BASE_INSTRUCTIONS missing purpose entry"
        assert "purpose.md" in block, "BASE_INSTRUCTIONS purpose entry missing purpose.md page"

    def test_base_instructions_contains_architecture(self):
        """BASE_INSTRUCTIONS includes an architecture entry with page architecture.md. (T2.3)"""
        content = JS_FILE.read_text()
        block = self._extract_const_block(content, "BASE_INSTRUCTIONS")
        assert block, "BASE_INSTRUCTIONS block not extractable from form.js"
        assert "architecture" in block, "BASE_INSTRUCTIONS missing architecture entry"
        assert (
            "architecture.md" in block
        ), "BASE_INSTRUCTIONS architecture entry missing architecture.md page"

    def test_base_instructions_contains_error_handling(self):
        """BASE_INSTRUCTIONS includes an error-handling entry with page error-handling.md. (T2.4)"""
        content = JS_FILE.read_text()
        block = self._extract_const_block(content, "BASE_INSTRUCTIONS")
        assert block, "BASE_INSTRUCTIONS block not extractable from form.js"
        assert "error-handling" in block, "BASE_INSTRUCTIONS missing error-handling entry"
        assert (
            "error-handling.md" in block
        ), "BASE_INSTRUCTIONS error-handling entry missing error-handling.md page"

    def test_capability_instructions_hasdb_maps_to_db(self):
        """CAPABILITY_INSTRUCTIONS maps hasDB to a single db entry with page db.md. (T2.5)"""
        content = JS_FILE.read_text()
        block = self._extract_const_block(content, "CAPABILITY_INSTRUCTIONS")
        assert block, "CAPABILITY_INSTRUCTIONS block not extractable from form.js"
        assert "hasDB" in block, "CAPABILITY_INSTRUCTIONS missing hasDB key"
        assert "db.md" in block, "CAPABILITY_INSTRUCTIONS hasDB entry missing db.md page"

    def test_capability_instructions_hasui_maps_to_frontend_design(self):
        """CAPABILITY_INSTRUCTIONS maps hasUI to include frontend-design with page frontend-design.md. (T2.6)"""
        content = JS_FILE.read_text()
        block = self._extract_const_block(content, "CAPABILITY_INSTRUCTIONS")
        assert block, "CAPABILITY_INSTRUCTIONS block not extractable from form.js"
        assert "hasUI" in block, "CAPABILITY_INSTRUCTIONS missing hasUI key"
        assert (
            "frontend-design.md" in block
        ), "CAPABILITY_INSTRUCTIONS hasUI entry missing frontend-design.md page"

    def test_capability_instructions_hasui_maps_to_new_page(self):
        """CAPABILITY_INSTRUCTIONS maps hasUI to include new-page with page new-page.md. (T2.7)"""
        content = JS_FILE.read_text()
        block = self._extract_const_block(content, "CAPABILITY_INSTRUCTIONS")
        assert block, "CAPABILITY_INSTRUCTIONS block not extractable from form.js"
        assert (
            "new-page.md" in block
        ), "CAPABILITY_INSTRUCTIONS hasUI entry missing new-page.md page"

    def test_capability_instructions_hasui_maps_to_style_guide(self):
        """CAPABILITY_INSTRUCTIONS maps hasUI to include style-guide with page style-guide.md. (T2.8)"""
        content = JS_FILE.read_text()
        block = self._extract_const_block(content, "CAPABILITY_INSTRUCTIONS")
        assert block, "CAPABILITY_INSTRUCTIONS block not extractable from form.js"
        assert (
            "style-guide.md" in block
        ), "CAPABILITY_INSTRUCTIONS hasUI entry missing style-guide.md page"

    def test_capability_instructions_does_not_contain_hastypecheck(self):
        """CAPABILITY_INSTRUCTIONS does not map hasTypecheck — it is a language-stack flag, not an instruction source. (T2.9)"""
        content = JS_FILE.read_text()
        block = self._extract_const_block(content, "CAPABILITY_INSTRUCTIONS")
        assert block, "CAPABILITY_INSTRUCTIONS block not extractable from form.js"
        assert (
            "hasTypecheck" not in block
        ), "CAPABILITY_INSTRUCTIONS must not contain hasTypecheck — it produces no instruction files"

    def test_capability_instructions_does_not_contain_security_flags(self):
        """CAPABILITY_INSTRUCTIONS does not map isPublicFacing, handlesConfidentialData, or hasAuthentication — these are security template flags, not instruction sources. (T2.10)"""
        content = JS_FILE.read_text()
        block = self._extract_const_block(content, "CAPABILITY_INSTRUCTIONS")
        assert block, "CAPABILITY_INSTRUCTIONS block not extractable from form.js"
        for flag in ("isPublicFacing", "handlesConfidentialData", "hasAuthentication"):
            assert (
                flag not in block
            ), f"CAPABILITY_INSTRUCTIONS must not contain {flag} — it controls security template rendering, not instruction files"

    def test_derive_instructions_starts_from_base_instructions(self):
        """deriveInstructions body references BASE_INSTRUCTIONS — base entries always present. (T2.11)"""
        content = JS_FILE.read_text()
        body = _extract_function_body(content, "deriveInstructions")
        assert body, "deriveInstructions function body not found in form.js"
        assert (
            "BASE_INSTRUCTIONS" in body
        ), "deriveInstructions must spread or iterate BASE_INSTRUCTIONS to guarantee always-present entries"


class TestCapabilityCheckboxWiring:
    """Tests for capability checkbox change event wiring inside DOMContentLoaded. (T3.x)"""

    def _extract_dom_content_loaded_body(self, content: str) -> str:
        """Extract the body of the DOMContentLoaded arrow function handler.

        Locates the addEventListener('DOMContentLoaded', ...) call and returns
        the text between its outermost braces (exclusive).
        Returns an empty string if not found.
        """
        pattern = (
            r'addEventListener\s*\(\s*["\']DOMContentLoaded["\']\s*,\s*async\s*\(\s*\)\s*=>\s*\{'
        )
        match = re.search(pattern, content)
        if match is None:
            return ""
        start = content.index("{", match.start())
        depth = 0
        for i, ch in enumerate(content[start:]):
            if ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0:
                    return content[start + 1 : start + i]
        return ""

    def test_dom_content_loaded_queries_user_editable_capability_checkboxes(self):
        """event-wiring.js queries the five user-editable capability checkbox data-testids. (T3.1)

        hasTypecheck is excluded — it is language-derived, not user-editable.
        """
        body = WIRING_FILE.read_text()
        for testid in (
            "form-hasUI",
            "form-hasDB",
            "form-isPublicFacing",
            "form-handlesConfidentialData",
            "form-hasAuthentication",
        ):
            assert (
                testid in body
            ), f"event-wiring.js does not query checkbox data-testid '{testid}'"

    def test_dom_content_loaded_reads_checkbox_checked_state(self):
        """event-wiring.js reads .checked from checkbox elements — proves change listeners read DOM state. (T3.2)"""
        body = WIRING_FILE.read_text()
        assert ".checked" in body, (
            "event-wiring.js does not read .checked from any element — "
            "capability checkbox change listeners must read .checked to build the capabilities object"
        )

    def test_capability_change_listener_calls_set_state_with_full_capabilities(self):
        """The capability change listener calls setState with a capabilities object containing all six flags. (T3.3)

        hasTypecheck is preserved from state.capabilities (language-derived) rather than read from a checkbox.
        """
        body = WIRING_FILE.read_text()
        assert "setState" in body, "event-wiring.js does not call setState for capabilities"
        assert (
            "capabilities" in body
        ), "setState call in event-wiring.js does not pass a capabilities key"
        for flag in (
            "hasUI",
            "hasDB",
            "hasTypecheck",
            "isPublicFacing",
            "handlesConfidentialData",
            "hasAuthentication",
        ):
            assert (
                flag in body
            ), f"Capability flag '{flag}' not present in event-wiring.js setState call"


class TestHasTypecheckDerivedFromLanguage:
    """Tests that hasTypecheck is derived from language data, not a user-editable checkbox. (T5.x)

    hasTypecheck is a language-stack flag — it controls Jinja2 template rendering and is
    determined by the selected language, not by the user.  The capability change listener
    must not include hasTypecheck; the language change handler must derive it instead.
    """

    def _extract_dom_content_loaded_body(self, content: str) -> str:
        """Extract the body of the DOMContentLoaded arrow function handler."""
        pattern = (
            r'addEventListener\s*\(\s*["\']DOMContentLoaded["\']\s*,\s*async\s*\(\s*\)\s*=>\s*\{'
        )
        match = re.search(pattern, content)
        if not match:
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

    def test_language_change_handler_sets_has_typecheck(self):
        """Language change handler calls setState with hasTypecheck derived from language data. (T5.1)"""
        body = WIRING_FILE.read_text()
        lang_handler_start = body.find("langSelect.addEventListener")
        assert lang_handler_start >= 0, "langSelect change handler not found in event-wiring.js"
        lang_handler_slice = body[lang_handler_start : lang_handler_start + 600]
        assert "hasTypecheck" in lang_handler_slice, (
            "Language change handler must set state.capabilities.hasTypecheck — "
            "hasTypecheck is language-derived, not user-editable"
        )

    def test_language_change_handler_derives_typecheck_from_commands(self):
        """Language change handler derives hasTypecheck by checking for typecheck-category commands. (T5.2)"""
        body = WIRING_FILE.read_text()
        lang_handler_start = body.find("langSelect.addEventListener")
        assert lang_handler_start >= 0, "langSelect change handler not found in event-wiring.js"
        lang_handler_slice = body[lang_handler_start : lang_handler_start + 600]
        assert "typecheck" in lang_handler_slice, (
            "Language change handler must derive hasTypecheck by checking for typecheck-category "
            "commands in the language data"
        )


class TestLanguageSelectOptgroups:
    """Tests that populateLanguageSelect groups options by ecosystem using <optgroup>. (T6.x)

    A flat alphabetical list buries TypeScript at the bottom — the most common language choice
    is hidden below the scroll threshold.  Grouping by ecosystem puts JS/TS first and gives the
    list visible structure that helps users orient themselves.

    LANGUAGE_GROUPS is a module-level constant in name-field.js: an ordered array of
    [label, [key, ...]] pairs.  populateLanguageSelect iterates it, creates one <optgroup>
    per entry, and collects any keys not covered by any group into an "Other" optgroup.
    """

    def test_language_groups_constant_defined_in_name_field_js(self):
        """LANGUAGE_GROUPS is declared as a module-level constant in name-field.js. (T6.1)"""
        content = NAME_JS_FILE.read_text()
        assert "LANGUAGE_GROUPS" in content, "LANGUAGE_GROUPS constant not found in name-field.js"

    def test_language_groups_first_entry_is_javascript_typescript(self):
        """The first entry in LANGUAGE_GROUPS covers the JavaScript / TypeScript ecosystem. (T6.1)

        typescript and typescript-npm must appear in the first group so they are visible
        without scrolling when the <select> opens.  The first group label must reference
        TypeScript; both language keys must appear before any second-group key (java-gradle).
        """
        content = NAME_JS_FILE.read_text()
        assert "LANGUAGE_GROUPS" in content, "LANGUAGE_GROUPS not found in name-field.js"
        # First group label must reference TypeScript
        first_label_match = re.search(r'LANGUAGE_GROUPS\s*=\s*\[\s*\[\s*"([^"]+)"', content)
        assert first_label_match, "Could not extract first group label from LANGUAGE_GROUPS"
        assert "TypeScript" in first_label_match.group(
            1
        ), f"First LANGUAGE_GROUPS label must reference TypeScript, got: {first_label_match.group(1)!r}"
        # Both typescript keys must appear before the second group's first key
        ts_pos = content.find('"typescript"')
        java_pos = content.find('"java-gradle"')
        assert ts_pos > 0, '"typescript" key not found in name-field.js'
        assert java_pos > 0, '"java-gradle" key not found in name-field.js'
        assert ts_pos < java_pos, '"typescript" must appear before "java-gradle" in LANGUAGE_GROUPS'

    def test_populate_language_select_body_creates_optgroup_elements(self):
        """populateLanguageSelect body calls createElement with 'optgroup'. (T6.2)"""
        content = NAME_JS_FILE.read_text()
        body = _extract_function_body(content, "populateLanguageSelect")
        assert body, "populateLanguageSelect function body not found in name-field.js"
        assert "optgroup" in body, (
            "populateLanguageSelect must create <optgroup> elements — "
            "'optgroup' not found in function body"
        )

    def test_populate_language_select_body_handles_ungrouped_languages(self):
        """populateLanguageSelect appends languages not in any group to an 'Other' fallback. (T6.3)"""
        content = NAME_JS_FILE.read_text()
        body = _extract_function_body(content, "populateLanguageSelect")
        assert body, "populateLanguageSelect function body not found in name-field.js"
        assert "Other" in body, (
            "populateLanguageSelect must collect ungrouped languages into an 'Other' group — "
            "'Other' not found in function body"
        )


class TestPopulateFromYmlDoesNotRenderCommandRows:
    """Tests that populateFromYml does NOT call renderCommandRows. (T4.x)

    Commands are managed in state and surfaced only through the YAML panel and the
    command-entry modal.  The commands-container in the form panel must always be empty —
    no inline DOM rows are ever created.  populateFromYml must not call renderCommandRows.
    """

    def test_populate_from_yml_body_does_not_call_render_command_rows(self):
        """renderCommandRows is NOT called inside the populateFromYml function body. (T4.1)

        populateFromYml populates name, language, capabilities, and state.commands via setState.
        setState refreshes the YAML panel, which is the only place commands are displayed.
        Calling renderCommandRows would create unwanted DOM input rows in commands-container.
        """
        content = JS_FILE.read_text()
        body = _extract_function_body(content, "populateFromYml")
        assert body, "populateFromYml function body not found in form.js"
        assert "renderCommandRows" not in body, (
            "populateFromYml must not call renderCommandRows — "
            "commands are displayed via the YAML panel, not as DOM rows in commands-container"
        )
