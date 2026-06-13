"""Tests for Stage 5 UI: ui/form.js state machinery, form population, YAML panel, and event wiring.

Covers:
- T1.1:  state object defined with top-level keys name, repo, capabilities, commands, instructions (B1)
- T1.2:  state.capabilities declares all seven capability flags (B2)
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

from tests.helpers.js_helpers import _extract_function_body

# File paths — tests run from project root where npm run test:python is invoked
JS_FILE = Path("ui/js/form.js")
WIRING_FILE = Path("ui/js/event-wiring.js")  # event listener wiring lives here
NAME_JS_FILE = Path("ui/js/name-field.js")  # handleFileUpload and upload-error live here


class TestFormJsStage5:
    """Tests for Stage 5 form.js additions: state object, functions, and event wiring."""

    def test_state_object_defined_with_required_top_level_keys(self):
        """state const defines all five required top-level keys. (T1.1, B1)"""
        content = JS_FILE.read_text()
        assert "const state" in content, "state object not defined in form.js"
        for key in ("name", "repo", "capabilities", "commands", "instructions"):
            assert re.search(rf"\b{key}\s*:", content), f"state.{key} key missing in form.js"

    def test_state_capabilities_declares_all_capability_flags(self):
        """state.capabilities declares all seven capability flags. (T1.2, B2; T6.1, B13)"""
        content = JS_FILE.read_text()
        flags = (
            "hasUI",
            "hasDB",
            "hasTypecheck",
            "isPublicFacing",
            "handlesConfidentialData",
            "hasAuthentication",
            "hasMutationTesting",
        )
        for flag in flags:
            assert flag in content, f"capability flag '{flag}' missing from form.js"

    def test_has_mutation_testing_false_in_state_capabilities(self):
        """state.capabilities contains `hasMutationTesting: false` with correct default. (T6.1, B13)

        State key must mirror schema field name exactly — populateFromYml() iterates
        Object.keys(configObj.capabilities) and silently fails to populate if the key is absent.
        """
        content = JS_FILE.read_text()
        assert "hasMutationTesting: false" in content, (
            "'hasMutationTesting: false' not found in form.js — "
            "add to state.capabilities after hasAuthentication: false"
        )

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

    def test_dom_content_loaded_queries_user_editable_capability_checkboxes(self):
        """event-wiring.js queries all user-editable capability checkbox data-testids. (T3.1; T7.1, B14)

        hasTypecheck is excluded — it is language-derived, not user-editable.
        """
        body = WIRING_FILE.read_text()
        for testid in (
            "form-hasUI",
            "form-hasDB",
            "form-isPublicFacing",
            "form-handlesConfidentialData",
            "form-hasAuthentication",
            "form-hasMutationTesting",
        ):
            assert testid in body, f"event-wiring.js does not query checkbox data-testid '{testid}'"

    def test_dom_content_loaded_reads_checkbox_checked_state(self):
        """event-wiring.js reads .checked from checkbox elements — proves change listeners read DOM state. (T3.2)"""
        body = WIRING_FILE.read_text()
        assert ".checked" in body, (
            "event-wiring.js does not read .checked from any element — "
            "capability checkbox change listeners must read .checked to build the capabilities object"
        )

    def test_capability_change_listener_calls_set_state_with_full_capabilities(self):
        """The capability change listener calls setState with a capabilities object containing all seven flags. (T3.3; T7.3, B16)

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
            "hasMutationTesting",
        ):
            assert (
                flag in body
            ), f"Capability flag '{flag}' not present in event-wiring.js setState call"

    def test_has_mutation_testing_set_state_entry_with_optional_chaining(self):
        """`wireCapabilityCheckboxes` reads hasMutationTesting with `?? false` fallback. (T7.3, B16)

        The `?? false` fallback follows the pattern used by all existing capability elements.
        The value may be assigned to a const before use in setState.
        """
        body = WIRING_FILE.read_text()
        assert "hasMutationTestingEl?.checked ?? false" in body, (
            "'hasMutationTestingEl?.checked ?? false' not found in event-wiring.js — "
            "ensure hasMutationTesting reads checkbox with ?? false fallback"
        )

    def test_has_mutation_testing_el_appears_after_has_authentication_el(self):
        """`hasMutationTestingEl` appears after `hasAuthenticationEl` in positional destructuring. (T7.2, B15)

        Append-only constraint — inserting before the end shifts positional destructuring
        and silently mis-wires all existing capabilities.
        """
        body = WIRING_FILE.read_text()
        assert "hasAuthenticationEl" in body, (
            "'hasAuthenticationEl' not found in event-wiring.js — "
            "cannot verify append-only ordering without reference element"
        )
        assert "hasMutationTestingEl" in body, (
            "'hasMutationTestingEl' not found in event-wiring.js — "
            "add hasMutationTestingEl to positional destructuring at end position"
        )

        auth_pos = body.index("hasAuthenticationEl")
        mutation_pos = body.index("hasMutationTestingEl")

        assert mutation_pos > auth_pos, (
            "'hasMutationTestingEl' must appear after 'hasAuthenticationEl' in event-wiring.js — "
            "append-only constraint: inserting earlier shifts positional destructuring "
            "and silently mis-wires existing capabilities"
        )

    def test_toggling_mutation_off_deletes_mutate_targeted_command(self):
        """Toggling hasMutationTesting off removes mutate_targeted from state.commands.

        Defence-in-depth: the inject side adds every mutationCommands entry, so the
        toggle-off side must remove every one it could have added — otherwise a stale
        mutate_targeted survives a toggle-off and crashes generation downstream.
        """
        body = WIRING_FILE.read_text()
        assert "delete updatedCommands.mutate_targeted" in body, (
            "'delete updatedCommands.mutate_targeted' not found in event-wiring.js — "
            "toggling mutation testing off must remove mutate_targeted to match the inject side"
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
