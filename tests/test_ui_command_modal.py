"""Tests for the command-entry modal refinement.

Covers three acceptance criteria:

AC1 — "Add command" opens a modal with name, command, description, and category
      <select> containing all nine valid category values.
AC2 — "Confirm" appends the row with modal values and closes the modal.
AC3 — "Cancel" or backdrop click closes the modal without adding a row.

Refinement — Delete button (06/04/2026):

AC-delete-1 — Edit modal shows a Delete button; disabled when the command name
              (YAML key) is "lint", "test", or "typecheck".
AC-delete-2 — Clicking an enabled Delete removes the command from state and
              closes the modal.
AC-delete-3 — .modal-actions buttons have a gap and margin-top in style.css.
"""

import re
from pathlib import Path

JS_FILE = Path("ui/js/form.js")
WIRING_FILE = Path("ui/js/event-wiring.js")
HTML_FILE = Path("ui/index.html")
CMD_MODAL_FILE = Path("ui/js/command-modal.js")  # command builder and modal functions live here

_VALID_CATEGORIES = (
    "test",
    "lint",
    "typecheck",
    "format",
    "docs",
    "docker",
    "db",
    "utilities",
    "discovery",
)


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


class TestCommandModalStructure:
    """AC1 — modal element and category select present in index.html; modal shown on button click."""

    def test_command_modal_element_present_in_html(self):
        """index.html contains an element with data-testid="command-modal". (AC1)"""
        content = HTML_FILE.read_text()
        assert (
            'data-testid="command-modal"' in content
        ), "command-modal element missing from index.html"

    def test_command_modal_has_category_select_element(self):
        """index.html contains a <select> with data-testid="cmd-modal-category". (AC1)"""
        content = HTML_FILE.read_text()
        assert (
            'data-testid="cmd-modal-category"' in content
        ), "cmd-modal-category select missing from index.html"
        assert re.search(
            r'<select[^>]*data-testid="cmd-modal-category"', content
        ), "cmd-modal-category must be a <select> element"

    def test_category_select_contains_all_valid_options(self):
        """index.html category select includes all nine valid category values. (AC1)"""
        content = HTML_FILE.read_text()
        for category in _VALID_CATEGORIES:
            assert (
                f'value="{category}"' in content
            ), f"category option '{category}' missing from index.html"

    def test_show_command_modal_function_defined(self):
        """showCommandModal function defined in event-wiring.js. (AC1)"""
        content = WIRING_FILE.read_text()
        assert "showCommandModal" in content, "showCommandModal not defined in event-wiring.js"

    def test_btn_add_command_handler_calls_show_command_modal(self):
        """btn-add-command click handler calls showCommandModal, not addCommandRow directly. (AC1)"""
        content = WIRING_FILE.read_text()
        # Locate the btn-add-command wiring block
        idx = content.find("btn-add-command")
        assert idx != -1, "btn-add-command not referenced in event-wiring.js"
        # The 200 chars following the testid reference contain the listener body
        wiring_snippet = content[idx : idx + 200]
        assert (
            "showCommandModal" in wiring_snippet
        ), "btn-add-command click handler must call showCommandModal"
        assert (
            "addCommandRow" not in wiring_snippet
        ), "btn-add-command click handler must not call addCommandRow directly"


class TestCommandModalConfirm:
    """AC2 — Confirm commits the command to state and closes the modal.

    Commands are managed entirely in state and surfaced via the YAML panel.
    No inline DOM rows are ever created in commands-container — neither addCommandRow
    nor renderCommandRows is called from any confirm or delete path.
    """

    def test_command_modal_confirm_button_present_in_html(self):
        """index.html contains a button with data-testid="cmd-modal-confirm". (AC2)"""
        content = HTML_FILE.read_text()
        assert (
            'data-testid="cmd-modal-confirm"' in content
        ), "cmd-modal-confirm button missing from index.html"

    def test_confirm_command_modal_function_defined(self):
        """confirmCommandModal function defined in event-wiring.js. (AC2)"""
        content = WIRING_FILE.read_text()
        assert "confirmCommandModal" in content, "confirmCommandModal not defined in event-wiring.js"

    def test_confirm_add_path_calls_set_state_with_new_command(self):
        """confirmCommandModal add path calls setState to commit the new command. (AC2)

        The add path must update state.commands directly via setState — no addCommandRow,
        no collectCommands, no DOM row creation.
        """
        content = CMD_MODAL_FILE.read_text()
        body = _extract_function_body(content, "confirmCommandModal")
        assert body, "confirmCommandModal function body not found in command-modal.js"
        assert (
            "setState" in body
        ), "confirmCommandModal must call setState to commit the command to state"

    def test_confirm_add_path_does_not_call_add_command_row(self):
        """confirmCommandModal body does not call addCommandRow — no inline rows. (AC2)

        Commands live in state and are displayed only in the YAML panel.
        addCommandRow creates unwanted DOM inputs in commands-container.
        """
        content = CMD_MODAL_FILE.read_text()
        body = _extract_function_body(content, "confirmCommandModal")
        assert body, "confirmCommandModal function body not found in command-modal.js"
        assert "addCommandRow" not in body, (
            "confirmCommandModal must not call addCommandRow — "
            "commands are committed via setState, not rendered as DOM rows"
        )

    def test_confirm_edit_path_does_not_call_render_command_rows(self):
        """confirmCommandModal edit path does not call renderCommandRows — no inline rows. (AC2)

        After an edit, setState already refreshes the YAML panel.
        renderCommandRows creates unwanted DOM inputs in commands-container.
        """
        content = CMD_MODAL_FILE.read_text()
        body = _extract_function_body(content, "confirmCommandModal")
        assert body, "confirmCommandModal function body not found in command-modal.js"
        assert "renderCommandRows" not in body, (
            "confirmCommandModal must not call renderCommandRows — "
            "the YAML panel reflects state; no DOM rows are needed"
        )

    def test_confirm_handler_hides_command_modal(self):
        """confirmCommandModal body calls hideCommandModal. (AC2)"""
        content = CMD_MODAL_FILE.read_text()
        body = _extract_function_body(content, "confirmCommandModal")
        assert body, "confirmCommandModal function body not found in command-modal.js"
        assert "hideCommandModal" in body, "confirmCommandModal must call hideCommandModal"


class TestDeleteCurrentCommand:
    """AC-delete-2 — deleteCurrentCommand removes the command from state; no DOM rows created."""

    def test_delete_current_command_does_not_call_render_command_rows(self):
        """deleteCurrentCommand body does not call renderCommandRows — no inline rows. (AC-delete-2)

        After deletion, setState already refreshes the YAML panel.
        renderCommandRows creates unwanted DOM inputs in commands-container.
        """
        content = CMD_MODAL_FILE.read_text()
        body = _extract_function_body(content, "deleteCurrentCommand")
        assert body, "deleteCurrentCommand function body not found in command-modal.js"
        assert "renderCommandRows" not in body, (
            "deleteCurrentCommand must not call renderCommandRows — "
            "the YAML panel reflects state; no DOM rows are needed"
        )


class TestCommandModalCancel:
    """AC3 — Cancel and backdrop click close the modal without adding a row."""

    def test_command_modal_cancel_button_present_in_html(self):
        """index.html contains a button with data-testid="cmd-modal-cancel". (AC3)"""
        content = HTML_FILE.read_text()
        assert (
            'data-testid="cmd-modal-cancel"' in content
        ), "cmd-modal-cancel button missing from index.html"

    def test_cancel_handler_hides_command_modal(self):
        """cmd-modal-cancel click handler closes the command modal. (AC3)"""
        content = WIRING_FILE.read_text()
        idx = content.find("cmd-modal-cancel")
        assert idx != -1, "cmd-modal-cancel not referenced in event-wiring.js"
        snippet = content[idx : idx + 300]
        assert "hideCommandModal" in snippet, "cancel handler must call hideCommandModal"

    def test_cancel_handler_does_not_call_add_command_row(self):
        """cmd-modal-cancel click handler does not call addCommandRow. (AC3)"""
        content = WIRING_FILE.read_text()
        idx = content.find("cmd-modal-cancel")
        assert idx != -1, "cmd-modal-cancel not referenced in event-wiring.js"
        snippet = content[idx : idx + 300]
        assert "addCommandRow" not in snippet, "cancel handler must not call addCommandRow"

    def test_backdrop_click_closes_command_modal(self):
        """Backdrop click on command-modal is wired to hideCommandModal in event wiring. (AC3)"""
        content = WIRING_FILE.read_text()
        # Use rfind to locate the last reference to command-modal,
        # which is where the backdrop addEventListener call lives
        idx = content.rfind("command-modal")
        assert idx != -1, "command-modal not referenced in event-wiring.js"
        region = content[idx : idx + 200]
        assert (
            "hideCommandModal" in region
        ), "command-modal backdrop click must wire hideCommandModal"


class TestCommandModalNameBlurValidation:
    """AC4b — Name field shows duplicate error on blur, not only on Confirm."""

    def test_cmd_modal_name_has_blur_listener_in_event_wiring(self):
        """event-wiring.js wires a blur listener on cmd-modal-name. (AC4b)"""
        content = WIRING_FILE.read_text()
        # cmd-modal-name and "blur" must appear within 300 chars of each other
        assert re.search(
            r"cmd-modal-name.{0,300}blur", content, re.DOTALL
        ), "blur listener not wired for cmd-modal-name in event-wiring.js"

    def test_blur_handler_calls_validate_command_name(self):
        """Blur handler on cmd-modal-name calls validateCommandName. (AC4b)"""
        content = WIRING_FILE.read_text()
        assert re.search(
            r"cmd-modal-name.{0,300}validateCommandName", content, re.DOTALL
        ), "blur handler must call validateCommandName"

    def test_keydown_clears_name_error(self):
        """keydown on cmd-modal-name clears cmd-modal-name-error. (AC4c)"""
        content = WIRING_FILE.read_text()
        assert re.search(
            r"cmd-modal-name.{0,400}keydown", content, re.DOTALL
        ), "keydown listener not wired for cmd-modal-name in event-wiring.js"
        assert re.search(
            r"keydown.{0,200}cmd-modal-name-error", content, re.DOTALL
        ), "keydown handler must clear cmd-modal-name-error"


class TestCommandModalDuplicateKeyValidation:
    """AC4 — Confirm rejects a name already present in state.commands."""

    def test_command_modal_name_error_element_present_in_html(self):
        """index.html contains a name-error span inside the command modal. (AC4)"""
        content = HTML_FILE.read_text()
        assert (
            'data-testid="cmd-modal-name-error"' in content
        ), "cmd-modal-name-error span missing from index.html"

    def test_validate_command_name_function_defined(self):
        """validateCommandName function defined in event-wiring.js. (AC4)"""
        content = WIRING_FILE.read_text()
        assert "validateCommandName" in content, "validateCommandName not defined in event-wiring.js"

    def test_validate_command_name_checks_state_commands(self):
        """validateCommandName body checks state.commands for the entered name. (AC4)"""
        content = CMD_MODAL_FILE.read_text()
        body = _extract_function_body(content, "validateCommandName")
        assert body, "validateCommandName function body not found in command-modal.js"
        assert (
            "state.commands" in body
        ), "validateCommandName must reference state.commands for duplicate check"

    def test_validate_command_name_renders_error_on_duplicate(self):
        """validateCommandName body writes to cmd-modal-name-error on duplicate. (AC4)"""
        content = CMD_MODAL_FILE.read_text()
        body = _extract_function_body(content, "validateCommandName")
        assert body, "validateCommandName function body not found in command-modal.js"
        assert (
            "cmd-modal-name-error" in body
        ), "validateCommandName must render the name-error element on duplicate"

    def test_confirm_command_modal_calls_validate_command_name(self):
        """confirmCommandModal body calls validateCommandName. (AC4)"""
        content = CMD_MODAL_FILE.read_text()
        body = _extract_function_body(content, "confirmCommandModal")
        assert body, "confirmCommandModal function body not found in command-modal.js"
        assert (
            "validateCommandName" in body
        ), "confirmCommandModal must delegate to validateCommandName"

    def test_show_command_modal_clears_name_error(self):
        """showCommandModal delegates field clearing to clearCommandModalFields, which clears
        cmd-modal-name-error. Verifies both the delegation and the clearing. (AC4)"""
        content = CMD_MODAL_FILE.read_text()
        body = _extract_function_body(content, "showCommandModal")
        assert body, "showCommandModal function body not found in command-modal.js"
        assert (
            "clearCommandModalFields" in body
        ), "showCommandModal must call clearCommandModalFields to reset fields and clear the name error"
        helper_body = _extract_function_body(content, "clearCommandModalFields")
        assert helper_body, "clearCommandModalFields helper not found in command-modal.js"
        assert (
            "cmd-modal-name-error" in helper_body
        ), "clearCommandModalFields must clear cmd-modal-name-error"


class TestCommandModalEditFlow:
    """AC-edit — Double-clicking a command block in the YAML panel opens the modal pre-filled.

    AC-edit-1: resolveCommandKey, showCommandModalForEdit, and openCommandModalFromYaml defined.
    AC-edit-2: yaml-panel dblclick listener wired; calls openCommandModalFromYaml.
    AC-edit-3: showCommandModalForEdit pre-fills modal fields and sets _editingCommandKey.
    AC-edit-4: validateCommandName bypasses duplicate check for _editingCommandKey.
    AC-edit-5: confirmCommandModal replaces old command entry on edit; resets _editingCommandKey.
    AC-edit-6: showCommandModal resets _editingCommandKey to null on fresh open.
    """

    def test_resolve_command_key_function_defined(self):
        """resolveCommandKey function defined in command-modal.js. (AC-edit-1)"""
        content = CMD_MODAL_FILE.read_text()
        assert "resolveCommandKey" in content, "resolveCommandKey not defined in command-modal.js"

    def test_show_command_modal_for_edit_function_defined(self):
        """showCommandModalForEdit function defined in command-modal.js. (AC-edit-1)"""
        content = CMD_MODAL_FILE.read_text()
        assert (
            "showCommandModalForEdit" in content
        ), "showCommandModalForEdit not defined in command-modal.js"

    def test_open_command_modal_from_yaml_function_defined(self):
        """openCommandModalFromYaml function defined in form.js. (AC-edit-1)"""
        content = JS_FILE.read_text()
        assert (
            "openCommandModalFromYaml" in content
        ), "openCommandModalFromYaml not defined in form.js"

    def test_yaml_panel_dblclick_wired_in_event_wiring(self):
        """Event wiring attaches a dblclick listener to yaml-panel. (AC-edit-2)"""
        content = WIRING_FILE.read_text()
        assert re.search(
            r"yaml-panel.{0,300}dblclick", content, re.DOTALL
        ), "dblclick listener not wired on yaml-panel in event-wiring.js"

    def test_yaml_panel_dblclick_calls_handle_yaml_dblclick(self):
        """dblclick handler on yaml-panel calls handleYamlDblclick, which falls through to openCommandModalFromYaml. (AC-edit-2)"""
        content = WIRING_FILE.read_text()
        assert re.search(
            r"yaml-panel.{0,300}handleYamlDblclick", content, re.DOTALL
        ), "dblclick handler on yaml-panel must call handleYamlDblclick"

    def test_show_command_modal_for_edit_sets_editing_key(self):
        """showCommandModalForEdit body assigns _editingCommandKey. (AC-edit-3)"""
        content = CMD_MODAL_FILE.read_text()
        body = _extract_function_body(content, "showCommandModalForEdit")
        assert body, "showCommandModalForEdit function body not found in command-modal.js"
        assert "_editingCommandKey" in body, "showCommandModalForEdit must set _editingCommandKey"

    def test_show_command_modal_for_edit_prefills_name_field(self):
        """showCommandModalForEdit body writes the command key to cmd-modal-name. (AC-edit-3)"""
        content = CMD_MODAL_FILE.read_text()
        body = _extract_function_body(content, "showCommandModalForEdit")
        assert body, "showCommandModalForEdit function body not found in command-modal.js"
        assert (
            "cmd-modal-name" in body
        ), "showCommandModalForEdit must reference cmd-modal-name to pre-fill the name field"

    def test_show_command_modal_for_edit_prefills_command_field(self):
        """showCommandModalForEdit body writes the command value to cmd-modal-command. (AC-edit-3)"""
        content = CMD_MODAL_FILE.read_text()
        body = _extract_function_body(content, "showCommandModalForEdit")
        assert body, "showCommandModalForEdit function body not found in command-modal.js"
        assert (
            "cmd-modal-command" in body
        ), "showCommandModalForEdit must reference cmd-modal-command to pre-fill the command field"

    def test_editing_command_key_declared_as_module_variable(self):
        """_editingCommandKey is declared as a module-level variable in command-modal.js. (AC-edit-4)"""
        content = CMD_MODAL_FILE.read_text()
        assert re.search(
            r"let\s+_editingCommandKey", content
        ), "_editingCommandKey must be declared as a module-level let variable in command-modal.js"

    def test_validate_command_name_references_editing_key(self):
        """validateCommandName body references _editingCommandKey to bypass check for original name. (AC-edit-4)"""
        content = CMD_MODAL_FILE.read_text()
        body = _extract_function_body(content, "validateCommandName")
        assert body, "validateCommandName function body not found in command-modal.js"
        assert (
            "_editingCommandKey" in body
        ), "validateCommandName must reference _editingCommandKey to allow original name through"

    def test_confirm_command_modal_references_editing_key(self):
        """confirmCommandModal body branches on _editingCommandKey for the edit path. (AC-edit-5)"""
        content = CMD_MODAL_FILE.read_text()
        body = _extract_function_body(content, "confirmCommandModal")
        assert body, "confirmCommandModal function body not found in command-modal.js"
        assert (
            "_editingCommandKey" in body
        ), "confirmCommandModal must reference _editingCommandKey to handle the edit path"

    def test_confirm_command_modal_calls_set_state_on_edit(self):
        """confirmCommandModal body calls setState to update commands on the edit path. (AC-edit-5)"""
        content = CMD_MODAL_FILE.read_text()
        body = _extract_function_body(content, "confirmCommandModal")
        assert body, "confirmCommandModal function body not found in command-modal.js"
        assert (
            "setState" in body
        ), "confirmCommandModal must call setState to update state.commands on edit"

    def test_show_command_modal_resets_editing_key_to_null(self):
        """showCommandModal body sets _editingCommandKey to null on fresh open. (AC-edit-6)"""
        content = CMD_MODAL_FILE.read_text()
        body = _extract_function_body(content, "showCommandModal")
        assert body, "showCommandModal function body not found in command-modal.js"
        assert (
            "_editingCommandKey" in body
        ), "showCommandModal must reset _editingCommandKey to null when opening a fresh modal"

    def test_open_command_modal_from_yaml_uses_tree_walker(self):
        """openCommandModalFromYaml delegates to resolveYamlClickedLine, which uses createTreeWalker. (bug-fix)"""
        content = CMD_MODAL_FILE.read_text()
        body = _extract_function_body(content, "resolveYamlClickedLine")
        assert body, "resolveYamlClickedLine function body not found in command-modal.js"
        assert "createTreeWalker" in body, (
            "resolveYamlClickedLine must use createTreeWalker — caretRangeFromPoint "
            "returns null on span boundaries and breaks the dblclick handler"
        )

    def test_nullish_coalescing_parenthesised_in_show_command_modal_for_edit(self):
        """showCommandModalForEdit parenthesises ?? when combined with ||. (syntax)"""
        content = CMD_MODAL_FILE.read_text()
        body = _extract_function_body(content, "showCommandModalForEdit")
        assert body, "showCommandModalForEdit function body not found in command-modal.js"
        assert re.search(
            r"\|\|\s*\(", body
        ), "?? must be parenthesised when combined with || — use: expr || (x?.y ?? fallback)"


class TestCommandModalEditModeLabels:
    """AC-label — Modal title and confirm button text reflect edit vs add mode.

    AC-label-1: index.html <h2> in command modal has data-testid="cmd-modal-title".
    AC-label-2: showCommandModalForEdit sets title to "Edit command" and confirm button to "Edit".
    AC-label-3: showCommandModal sets title to "Add command" and confirm button to "Add".
    """

    def test_command_modal_title_h2_has_testid(self):
        """index.html <h2> inside command-modal has data-testid="cmd-modal-title". (AC-label-1)"""
        content = HTML_FILE.read_text()
        assert re.search(
            r"<h2[^>]*data-testid=\"cmd-modal-title\"", content
        ), 'command modal <h2> must have data-testid="cmd-modal-title" in index.html'

    def test_show_command_modal_for_edit_sets_title_to_edit_command(self):
        """showCommandModalForEdit body sets cmd-modal-title textContent to "Edit command". (AC-label-2)"""
        content = CMD_MODAL_FILE.read_text()
        body = _extract_function_body(content, "showCommandModalForEdit")
        assert body, "showCommandModalForEdit function body not found in command-modal.js"
        assert (
            "cmd-modal-title" in body
        ), "showCommandModalForEdit must reference cmd-modal-title to update the modal heading"
        assert (
            "Edit command" in body
        ), 'showCommandModalForEdit must set the modal title to "Edit command"'

    def test_show_command_modal_for_edit_sets_confirm_button_to_edit(self):
        """showCommandModalForEdit body sets cmd-modal-confirm textContent to "Edit". (AC-label-2)"""
        content = CMD_MODAL_FILE.read_text()
        body = _extract_function_body(content, "showCommandModalForEdit")
        assert body, "showCommandModalForEdit function body not found in command-modal.js"
        assert (
            "cmd-modal-confirm" in body
        ), "showCommandModalForEdit must reference cmd-modal-confirm to update the button label"

    def test_show_command_modal_resets_title_to_add_command(self):
        """showCommandModal body sets cmd-modal-title textContent to "Add command". (AC-label-3)"""
        content = CMD_MODAL_FILE.read_text()
        body = _extract_function_body(content, "showCommandModal")
        assert body, "showCommandModal function body not found in command-modal.js"
        assert (
            "cmd-modal-title" in body
        ), "showCommandModal must reference cmd-modal-title to restore the modal heading"
        assert "Add command" in body, 'showCommandModal must set the modal title to "Add command"'

    def test_show_command_modal_resets_confirm_button_to_add(self):
        """showCommandModal body sets cmd-modal-confirm textContent to "Add". (AC-label-3)"""
        content = CMD_MODAL_FILE.read_text()
        body = _extract_function_body(content, "showCommandModal")
        assert body, "showCommandModal function body not found in command-modal.js"
        assert (
            "cmd-modal-confirm" in body
        ), "showCommandModal must reference cmd-modal-confirm to restore the button label"


_PROTECTED_CATEGORIES = ("lint", "test", "typecheck")


class TestCommandModalDelete:
    """AC-delete-1 — Edit modal shows Delete button; disabled for protected categories.

    AC-delete-1: index.html has data-testid="cmd-modal-delete" button in command modal.
    AC-delete-1: showCommandModalForEdit shows the Delete button and disables it when
                 the command name (YAML key) is "lint", "test", or "typecheck".
    AC-delete-1: showCommandModal hides the Delete button (add mode has no delete action).
    """

    def test_delete_button_present_in_html(self):
        """index.html command modal contains a button with data-testid="cmd-modal-delete". (AC-delete-1)"""
        content = HTML_FILE.read_text()
        assert (
            'data-testid="cmd-modal-delete"' in content
        ), "cmd-modal-delete button missing from index.html"

    def test_delete_button_is_a_button_element(self):
        """cmd-modal-delete is a <button> element in index.html. (AC-delete-1)"""
        content = HTML_FILE.read_text()
        assert re.search(
            r"<button[^>]*data-testid=\"cmd-modal-delete\"", content
        ), "cmd-modal-delete must be a <button> element"

    def test_show_command_modal_for_edit_references_delete_button(self):
        """showCommandModalForEdit body references cmd-modal-delete to show/disable it. (AC-delete-1)"""
        content = CMD_MODAL_FILE.read_text()
        body = _extract_function_body(content, "showCommandModalForEdit")
        assert body, "showCommandModalForEdit function body not found in command-modal.js"
        assert "cmd-modal-delete" in body, "showCommandModalForEdit must reference cmd-modal-delete"

    def test_show_command_modal_for_edit_disables_delete_for_protected_names(self):
        """showCommandModalForEdit disables Delete when the command name is a protected tag. (AC-delete-1)"""
        content = CMD_MODAL_FILE.read_text()
        body = _extract_function_body(content, "showCommandModalForEdit")
        assert body, "showCommandModalForEdit function body not found in command-modal.js"
        # Must reference all three protected name values
        for name in _PROTECTED_CATEGORIES:
            assert (
                name in body
            ), f"showCommandModalForEdit must check protected command name '{name}'"

    def test_show_command_modal_hides_delete_button_in_add_mode(self):
        """showCommandModal adds 'hidden' to cmd-modal-delete — Delete is never visible in add mode. (AC-delete-1)"""
        content = CMD_MODAL_FILE.read_text()
        body = _extract_function_body(content, "showCommandModal")
        assert body, "showCommandModal function body not found in command-modal.js"
        # Must explicitly add hidden — not merely reference the element
        assert re.search(
            r"cmd-modal-delete.{0,200}add\(.{0,20}hidden", body, re.DOTALL
        ), "showCommandModal must call classList.add('hidden') on cmd-modal-delete"

    def test_show_command_modal_for_edit_reveals_delete_button(self):
        """showCommandModalForEdit removes 'hidden' from cmd-modal-delete — Delete is visible in edit mode only. (AC-delete-1)"""
        content = CMD_MODAL_FILE.read_text()
        body = _extract_function_body(content, "showCommandModalForEdit")
        assert body, "showCommandModalForEdit function body not found in command-modal.js"
        assert re.search(
            r"cmd-modal-delete.{0,200}remove\(.{0,20}hidden", body, re.DOTALL
        ), "showCommandModalForEdit must call classList.remove('hidden') on cmd-modal-delete"


class TestCommandModalDeleteAction:
    """AC-delete-2 — Delete removes the command from state and closes the modal."""

    def test_delete_current_command_function_defined(self):
        """deleteCurrentCommand function defined in command-modal.js. (AC-delete-2)"""
        content = CMD_MODAL_FILE.read_text()
        assert (
            "deleteCurrentCommand" in content
        ), "deleteCurrentCommand not defined in command-modal.js"

    def test_delete_current_command_removes_from_state(self):
        """deleteCurrentCommand body deletes the key from state.commands and calls setState. (AC-delete-2)"""
        content = CMD_MODAL_FILE.read_text()
        body = _extract_function_body(content, "deleteCurrentCommand")
        assert body, "deleteCurrentCommand function body not found in command-modal.js"
        assert (
            "state.commands" in body or "setState" in body
        ), "deleteCurrentCommand must modify state.commands via setState"
        assert "setState" in body, "deleteCurrentCommand must call setState to update state"

    def test_delete_current_command_calls_hide_command_modal(self):
        """deleteCurrentCommand body calls hideCommandModal to close the modal. (AC-delete-2)"""
        content = CMD_MODAL_FILE.read_text()
        body = _extract_function_body(content, "deleteCurrentCommand")
        assert body, "deleteCurrentCommand function body not found in command-modal.js"
        assert (
            "hideCommandModal" in body
        ), "deleteCurrentCommand must call hideCommandModal after deletion"

    def test_delete_current_command_does_not_call_render_command_rows(self):
        """deleteCurrentCommand body does not call renderCommandRows — no inline rows. (AC-delete-2)

        setState refreshes the YAML panel; no DOM rows are needed in commands-container.
        """
        content = CMD_MODAL_FILE.read_text()
        body = _extract_function_body(content, "deleteCurrentCommand")
        assert body, "deleteCurrentCommand function body not found in command-modal.js"
        assert "renderCommandRows" not in body, (
            "deleteCurrentCommand must not call renderCommandRows — "
            "the YAML panel reflects state; no DOM rows are needed"
        )

    def test_delete_button_click_wired_in_event_wiring(self):
        """event-wiring.js wires cmd-modal-delete click to deleteCurrentCommand. (AC-delete-2)"""
        content = WIRING_FILE.read_text()
        assert re.search(
            r"cmd-modal-delete.{0,300}deleteCurrentCommand", content, re.DOTALL
        ), "cmd-modal-delete click handler must call deleteCurrentCommand in event-wiring.js"


class TestModalActionsSpacing:
    """AC-delete-3 — .modal-actions buttons have gap and margin-top in style.css."""

    def test_modal_actions_class_defined_in_css(self):
        """.modal-actions selector defined in style.css. (AC-delete-3)"""
        content = Path("ui/css/style.css").read_text()
        assert ".modal-actions" in content, ".modal-actions selector missing from style.css"

    def test_modal_actions_has_gap(self):
        """.modal-actions rule includes a gap property. (AC-delete-3)"""
        content = Path("ui/css/style.css").read_text()
        assert re.search(
            r"\.modal-actions\s*\{[^}]*gap\s*:", content, re.DOTALL
        ), ".modal-actions must define a gap property to space buttons"

    def test_modal_actions_has_margin_top(self):
        """.modal-actions rule includes a margin-top property. (AC-delete-3)"""
        content = Path("ui/css/style.css").read_text()
        assert re.search(
            r"\.modal-actions\s*\{[^}]*margin-top\s*:", content, re.DOTALL
        ), ".modal-actions must define margin-top to separate it from the fields above"

    def test_btn_danger_defined_in_css(self):
        """.btn-danger selector defined in style.css. (AC-delete-3)"""
        content = Path("ui/css/style.css").read_text()
        assert ".btn-danger" in content, ".btn-danger selector missing from style.css"

    def test_btn_danger_uses_danger_colour_token(self):
        """.btn-danger uses --danger-strong colour token. (AC-delete-3)"""
        content = Path("ui/css/style.css").read_text()
        assert re.search(
            r"\.btn-danger\s*\{[^}]*--danger-strong", content, re.DOTALL
        ), ".btn-danger must use --danger-strong colour token"

    def test_btn_hidden_overrides_btn_display(self):
        """.btn.hidden sets display: none — prevents .btn inline-flex from winning at equal specificity. (AC-delete-3)"""
        content = Path("ui/css/style.css").read_text()
        assert re.search(r"\.btn\.hidden\s*\{[^}]*display\s*:\s*none", content, re.DOTALL), (
            ".btn.hidden must set display: none — .btn { display: inline-flex } "
            "outranks .hidden at equal specificity and keeps hidden buttons visible"
        )
