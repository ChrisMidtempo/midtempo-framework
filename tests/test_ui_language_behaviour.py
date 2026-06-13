"""Tests for language-specific UI behaviour: hasTypecheck derivation and language select grouping.

Covers:
- T5.1:  Language change handler calls setState with hasTypecheck derived from language data
- T5.2:  Language change handler derives hasTypecheck by checking for typecheck-category commands
- T6.1:  LANGUAGE_GROUPS defined in name-field.js with JS/TS as first group
- T6.2:  populateLanguageSelect body creates optgroup elements
- T6.3:  populateLanguageSelect body appends ungrouped languages to an "Other" group
"""

import re
from pathlib import Path

from tests.helpers.js_helpers import _extract_function_body

WIRING_FILE = Path("ui/js/event-wiring.js")
NAME_JS_FILE = Path("ui/js/name-field.js")


class TestHasTypecheckDerivedFromLanguage:
    """Tests that hasTypecheck is derived from language data, not a user-editable checkbox. (T5.x)

    hasTypecheck is a language-stack flag — it controls Jinja2 template rendering and is
    determined by the selected language, not by the user.  The capability change listener
    must not include hasTypecheck; the language change handler must derive it instead.
    """

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
