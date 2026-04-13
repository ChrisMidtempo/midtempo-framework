"""Tests for Stage 4 UI static files: ui/index.html, ui/style.css, ui/form.js.

Covers:
- T1.1: #entry-screen section present (B1)
- T1.2: #editor with class hidden present (B2)
- T1.3: #form-panel div inside #editor (B3)
- T1.4: #yaml-panel div inside #editor (B4)
- T1.5: #modal with class hidden present (B5)
- T1.6: ajv CDN script tag present (B6)
- T1.7: js-yaml CDN script tag present (B7)
- T1.8: form.js module script present (B8)
- T2.1: :root defines --colour-brand (B9)
- T2.2: :root defines --space-200 (B10)
- T2.3: .hidden sets display: none (B11)
- T2.4: @media max-width 1024px block exists (B12)
- T2.5: #editor defines display: flex (B13)
- T3.1: NAME_PATTERN regex equals expected pattern (B14)
- T3.2: Valid names match NAME_PATTERN (B15)
- T3.3: Invalid names rejected by NAME_PATTERN (B16)
- T3.4: routeNewFlow function defined (B17)
- T3.5: routeExistingFlow function defined (B18)
"""

import re
from html.parser import HTMLParser
from pathlib import Path

# File paths — tests run from project root where npm run test:python is invoked
HTML_FILE = Path("ui/index.html")
CSS_FILE = Path("ui/css/style.css")
JS_FILE = Path("ui/js/form.js")
NAME_JS_FILE = Path("ui/js/name-field.js")  # NAME_PATTERN, updateNamePreview, and name utilities


class _ElementCollector(HTMLParser):
    """Minimal SAX-style HTML parser that records elements with IDs and their parent chain."""

    def __init__(self):
        super().__init__()
        self._elements = []
        self._stack = []  # list of (tag, id, classes, src, type)

    def handle_starttag(self, tag, attrs):
        attr_dict = dict(attrs)
        element_id = attr_dict.get("id", "")
        classes = attr_dict.get("class", "").split()
        src = attr_dict.get("src", "")
        el_type = attr_dict.get("type", "")
        parent_ids = [p[1] for p in self._stack if p[1]]
        self._elements.append(
            {
                "tag": tag,
                "id": element_id,
                "classes": classes,
                "src": src,
                "type": el_type,
                "parent_ids": parent_ids,
            }
        )
        self._stack.append((tag, element_id, classes, src, el_type))

    def handle_endtag(self, tag):
        for i in range(len(self._stack) - 1, -1, -1):
            if self._stack[i][0] == tag:
                self._stack.pop(i)
                break

    def find_by_id(self, element_id):
        return [e for e in self._elements if e["id"] == element_id]

    def find_scripts(self):
        return [e for e in self._elements if e["tag"] == "script"]


def _parse_html():
    """Parse ui/index.html and return an _ElementCollector with recorded elements."""
    content = HTML_FILE.read_text()
    parser = _ElementCollector()
    parser.feed(content)
    return parser


def _extract_name_pattern():
    """Extract the NAME_PATTERN regex literal body from ui/name-field.js."""
    content = NAME_JS_FILE.read_text()
    match = re.search(r"NAME_PATTERN\s*=\s*/([^/]+)/", content)
    assert match is not None, "NAME_PATTERN not found in name-field.js"
    return match.group(1)


class TestIndexHtml:
    """Tests for ui/index.html landmark structure and script tags."""

    def test_entry_screen_section_exists(self):
        """#entry-screen section element is present. (T1.1, B1)"""
        parser = _parse_html()
        matches = parser.find_by_id("entry-screen")
        assert len(matches) == 1

    def test_editor_section_exists_with_class_hidden(self):
        """#editor element exists and carries the class hidden. (T1.2, B2)"""
        parser = _parse_html()
        matches = parser.find_by_id("editor")
        assert len(matches) == 1
        assert "hidden" in matches[0]["classes"]

    def test_form_panel_div_exists_inside_editor(self):
        """#form-panel element is a descendant of #editor. (T1.3, B3)"""
        parser = _parse_html()
        matches = parser.find_by_id("form-panel")
        assert len(matches) == 1
        assert "editor" in matches[0]["parent_ids"]

    def test_yaml_panel_div_exists_inside_editor(self):
        """#yaml-panel element is a descendant of #editor. (T1.4, B4)"""
        parser = _parse_html()
        matches = parser.find_by_id("yaml-panel")
        assert len(matches) == 1
        assert "editor" in matches[0]["parent_ids"]

    def test_modal_element_exists_with_class_hidden(self):
        """#modal element exists and carries the class hidden. (T1.5, B5)"""
        parser = _parse_html()
        matches = parser.find_by_id("modal")
        assert len(matches) == 1
        assert "hidden" in matches[0]["classes"]

    def test_ajv_no_script_tag_in_index_html(self):
        """No ajv <script> tag in index.html — ajv is imported as ESM in form.js. (BUG-4a)

        ajv 8.x dist/ajv.min.js is a CommonJS bundle; loading it as a browser <script>
        throws 'exports is not defined'. Since form.js is type="module", Ajv must be
        imported directly via an ESM URL inside form.js.
        """
        parser = _parse_html()
        scripts = parser.find_scripts()
        ajv_scripts = [s for s in scripts if "ajv" in s["src"]]
        assert len(ajv_scripts) == 0, (
            f"ajv must not be loaded via a <script> tag (CJS bundle, browser-incompatible). "
            f"Found: {[s['src'] for s in ajv_scripts]}"
        )

    def test_ajv_imported_as_esm_in_form_js(self):
        """form.js imports Ajv via ESM import statement from vendor bundle. (BUG-4a)

        ajv 8.x has no UMD browser bundle. Since form.js is type="module",
        the correct pattern is: import Ajv from '<local-esm-path>'.
        """
        content = JS_FILE.read_text()
        assert re.search(
            r"import\s+Ajv\s+from\s+['\"][^'\"]*vendor/ajv[^'\"]*['\"]", content
        ), "form.js must import Ajv via an ESM import statement from the local vendor bundle"

    def test_js_yaml_cdn_script_tag_present(self):
        """A script tag with src containing 'js-yaml' is present. (T1.7, B7)"""
        parser = _parse_html()
        scripts = parser.find_scripts()
        yaml_scripts = [s for s in scripts if "js-yaml" in s["src"]]
        assert len(yaml_scripts) >= 1

    def test_form_js_loaded_as_module_script(self):
        """A script tag with type=module and src=form.js is present. (T1.8, B8)"""
        parser = _parse_html()
        scripts = parser.find_scripts()
        module_scripts = [s for s in scripts if s["type"] == "module" and s["src"] == "js/form.js"]
        assert len(module_scripts) >= 1


class TestStyleCss:
    """Tests for ui/style.css design tokens and selectors."""

    def test_root_block_defines_colour_brand_token(self):
        """--colour-brand is declared inside a :root block. (T2.1, B9)"""
        content = CSS_FILE.read_text()
        root_match = re.search(r":root\s*\{([^}]+)\}", content, re.DOTALL)
        assert root_match is not None, ":root block not found in style.css"
        assert "--colour-brand" in root_match.group(1)

    def test_root_block_defines_space_200_token(self):
        """--space-200 is declared inside a :root block. (T2.2, B10)"""
        content = CSS_FILE.read_text()
        root_match = re.search(r":root\s*\{([^}]+)\}", content, re.DOTALL)
        assert root_match is not None, ":root block not found in style.css"
        assert "--space-200" in root_match.group(1)

    def test_hidden_rule_sets_display_none(self):
        """.hidden rule contains display: none. (T2.3, B11)"""
        content = CSS_FILE.read_text()
        assert re.search(r"\.hidden\s*\{[^}]*display\s*:\s*none", content, re.DOTALL)

    def test_media_block_at_max_width_1024px_exists(self):
        """An @media block with max-width: 1024px is present. (T2.4, B12)"""
        content = CSS_FILE.read_text()
        assert re.search(r"@media[^{]*max-width\s*:\s*1024px", content)

    def test_editor_not_hidden_rule_defines_display_flex(self):
        """#editor:not(.hidden) rule contains display: flex. (T2.5, B13, BUG-3)

        display: flex must live in the :not(.hidden) selector so the .hidden utility class
        (specificity 0-1-0) is not overridden by the #editor ID selector (specificity 1-0-0).
        """
        content = CSS_FILE.read_text()
        assert re.search(r"#editor:not\(\.hidden\)\s*\{[^}]*display\s*:\s*flex", content, re.DOTALL)

    def test_editor_base_rule_does_not_set_display(self):
        """#editor base rule must not set display — ID selector specificity (100) beats .hidden
        class (10), so display: flex in #editor overrides .hidden and the editor is always visible
        on page load. display: flex must live in #editor:not(.hidden). (BUG-3)"""
        content = CSS_FILE.read_text()
        editor_base = re.search(r"#editor\s*\{([^}]+)\}", content, re.DOTALL)
        assert editor_base is not None, "#editor rule not found in style.css"
        assert not re.search(r"display\s*:", editor_base.group(1)), (
            "#editor base rule sets display — ID specificity overrides .hidden; "
            "move display: flex to #editor:not(.hidden)"
        )

    def test_editor_not_hidden_selector_sets_display_flex(self):
        """#editor:not(.hidden) must set display: flex so the editor is flex when visible
        without conflicting with the .hidden utility class. (BUG-3)"""
        content = CSS_FILE.read_text()
        assert re.search(
            r"#editor:not\(\.hidden\)\s*\{[^}]*display\s*:\s*flex", content, re.DOTALL
        ), "#editor:not(.hidden) { display: flex } rule not found in style.css"

    def test_entry_screen_base_rule_does_not_set_display(self):
        """#entry-screen base rule must not set display — ID selector specificity (100) beats
        .hidden class (10), so display: flex in #entry-screen overrides .hidden when showEditor()
        hides it. display: flex must live in #entry-screen:not(.hidden). (BUG-3)"""
        content = CSS_FILE.read_text()
        entry_base = re.search(r"#entry-screen\s*\{([^}]+)\}", content, re.DOTALL)
        assert entry_base is not None, "#entry-screen rule not found in style.css"
        assert not re.search(r"display\s*:", entry_base.group(1)), (
            "#entry-screen base rule sets display — ID specificity overrides .hidden; "
            "move display: flex to #entry-screen:not(.hidden)"
        )

    def test_entry_screen_not_hidden_selector_sets_display_flex(self):
        """#entry-screen:not(.hidden) must set display: flex so the entry screen is flex when
        visible without conflicting with the .hidden utility class. (BUG-3)"""
        content = CSS_FILE.read_text()
        assert re.search(
            r"#entry-screen:not\(\.hidden\)\s*\{[^}]*display\s*:\s*flex", content, re.DOTALL
        ), "#entry-screen:not(.hidden) { display: flex } rule not found in style.css"

    def test_modal_base_rule_does_not_set_display(self):
        """#modal base rule must not set display — ID selector specificity (100) beats .hidden
        class (10), so display: flex in #modal overrides .hidden and the modal is always visible.
        display: flex must live in #modal:not(.hidden) so .hidden can hide it. (BUG-2)"""
        content = CSS_FILE.read_text()
        # Allow comma-grouped selector (#modal, #command-modal {) or standalone (#modal {)
        modal_base = re.search(r"#modal[^{]*\{([^}]+)\}", content, re.DOTALL)
        assert modal_base is not None, "#modal rule not found in style.css"
        assert not re.search(r"display\s*:", modal_base.group(1)), (
            "#modal base rule sets display — ID specificity overrides .hidden; "
            "move display: flex to #modal:not(.hidden)"
        )

    def test_modal_not_hidden_selector_sets_display_flex(self):
        """#modal:not(.hidden) must set display: flex so the modal is flex when visible
        without conflicting with the .hidden utility class. (BUG-2)"""
        content = CSS_FILE.read_text()
        # Allow comma-grouped selector or standalone form
        assert re.search(
            r"#modal:not\(\.hidden\)[^{]*\{[^}]*display\s*:\s*flex", content, re.DOTALL
        ), "#modal:not(.hidden) { display: flex } rule not found in style.css"

    def test_editor_base_rule_uses_height_not_min_height(self):
        """#editor base rule must use height: 100vh, not min-height: 100vh.
        min-height allows the editor to grow past the viewport; height pins it so both
        panels scroll independently within their own overflow containers."""
        content = CSS_FILE.read_text()
        editor_base = re.search(r"#editor\s*\{([^}]+)\}", content, re.DOTALL)
        assert editor_base is not None, "#editor rule not found in style.css"
        assert re.search(
            r"height\s*:\s*100vh", editor_base.group(1)
        ), "#editor base rule does not set height: 100vh"
        assert not re.search(
            r"min-height\s*:", editor_base.group(1)
        ), "#editor base rule sets min-height — replace with height: 100vh"

    def test_form_panel_rule_has_height_100vh(self):
        """#form-panel rule must set height: 100vh to pin the panel to viewport height.
        Without a height constraint, overflow-y: auto never triggers and the page scrolls
        instead of the panel."""
        content = CSS_FILE.read_text()
        form_panel = re.search(r"#form-panel\s*\{([^}]+)\}", content, re.DOTALL)
        assert form_panel is not None, "#form-panel rule not found in style.css"
        assert re.search(
            r"height\s*:\s*100vh", form_panel.group(1)
        ), "#form-panel rule does not set height: 100vh"


class TestFormJs:
    """Tests for ui/form.js regex pattern and function definitions."""

    def test_name_pattern_regex_defined_with_correct_pattern(self):
        """NAME_PATTERN regex body equals ^[a-zA-Z0-9][a-zA-Z0-9._-]*$. (T3.1, B14)"""
        content = NAME_JS_FILE.read_text()
        match = re.search(r"NAME_PATTERN\s*=\s*/([^/]+)/", content)
        assert match is not None, "NAME_PATTERN not found in name-field.js"
        assert match.group(1) == r"^[a-zA-Z0-9][a-zA-Z0-9._-]*$"

    def test_valid_names_match_name_pattern(self):
        """Valid repo names myrepo, my-repo, my_repo.1, A1 all match NAME_PATTERN. (T3.2, B15)"""
        pattern = _extract_name_pattern()
        valid_names = ["myrepo", "my-repo", "my_repo.1", "A1"]
        for name in valid_names:
            assert re.match(pattern, name) is not None, f"{name!r} should match but did not"

    def test_invalid_names_rejected_by_name_pattern(self):
        """Invalid names -repo, 'my repo', empty string do not match NAME_PATTERN. (T3.3, B16)"""
        pattern = _extract_name_pattern()
        invalid_names = ["-repo", "my repo", ""]
        for name in invalid_names:
            assert re.match(pattern, name) is None, f"{name!r} should not match but did"

    def test_route_new_flow_function_defined(self):
        """routeNewFlow is defined as a function in form.js. (T3.4, B17)"""
        content = JS_FILE.read_text()
        assert re.search(r"function\s+routeNewFlow|routeNewFlow\s*=\s*(function|\()", content)

    def test_route_existing_flow_function_defined(self):
        """routeExistingFlow is defined as a function in form.js. (T3.5, B18)"""
        content = JS_FILE.read_text()
        assert re.search(
            r"function\s+routeExistingFlow|routeExistingFlow\s*=\s*(function|\()", content
        )
