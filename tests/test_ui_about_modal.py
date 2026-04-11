"""Tests for About modal HTML, CSS, and JS structure.

Covers:
- about-btn present in #app-header to the right of docs-btn, inside a .header-nav wrapper (AC1)
- #about-modal HTML structure with heading and close button (AC1)
- docs-modal.js exports closeModal so about-modal.js can import it (AC2)
- about-modal.js exports init(), wires about-btn click, wires close button, wires Escape key (AC2, AC3)
- about-modal.js openModal() calls the imported closeDocsModal (AC2)
- about-modal.js closeModal() returns focus to .about-btn (AC3)
- form.js imports init from about-modal.js and calls it at DOMContentLoaded (AC2)
- CSS: .header-nav flex layout, .about-btn uses --colour-text-on-brand, #about-modal z-index 200 (AC1)
"""

import re
from pathlib import Path

HTML_FILE = Path("ui/index.html")
CSS_FILE = Path("ui/css/style.css")
ABOUT_MODAL_FILE = Path("ui/js/about-modal.js")
DOCS_MODAL_FILE = Path("ui/js/docs-modal.js")
FORM_FILE = Path("ui/js/form.js")


def _extract_function_body(content: str, fn_name: str) -> str:
    """Return the body of a named JS function using brace-matching.

    Handles declaration, async declaration, and assignment forms.
    Returns an empty string when the function is not found.
    """
    pattern = (
        rf"(?:async\s+function\s+{fn_name}\s*\([^)]*\)"
        rf"|function\s+{fn_name}\s*\([^)]*\)"
        rf"|{fn_name}\s*=\s*(?:async\s+function\s*\([^)]*\)|function\s*\([^)]*\)|\([^)]*\)\s*=>))"
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


# ── HTML ──────────────────────────────────────────────────────────────────────


class TestAboutButtonInHeader:
    """AC1 — About button present in #app-header, inside .header-nav, to the right of docs-btn."""

    def test_header_nav_wrapper_present_in_app_header(self):
        """index.html contains a .header-nav element after the #app-header opening tag."""
        content = HTML_FILE.read_text()
        assert "header-nav" in content, (
            ".header-nav wrapper missing from index.html — "
            "needed to group Documentation and About buttons in the header"
        )
        assert content.index("header-nav") > content.index("app-header"), (
            ".header-nav must appear after the #app-header opening tag in source order"
        )

    def test_about_btn_present_in_header(self):
        """index.html contains a button with class about-btn inside #app-header."""
        content = HTML_FILE.read_text()
        assert "about-btn" in content, "about-btn class missing from index.html"
        assert content.index("about-btn") > content.index("app-header"), (
            "about-btn must appear after the #app-header opening tag in source order"
        )

    def test_about_btn_appears_after_docs_btn_in_source_order(self):
        """about-btn offset in index.html exceeds docs-btn offset — About is to the right of Documentation."""
        content = HTML_FILE.read_text()
        assert "docs-btn" in content, "docs-btn missing from index.html"
        assert "about-btn" in content, "about-btn missing from index.html"
        assert content.index("about-btn") > content.index("docs-btn"), (
            "about-btn must appear after docs-btn in source order — About is to the right of Documentation"
        )


class TestAboutModalHTMLStructure:
    """AC1 — #about-modal present in index.html with a close button."""

    def test_about_modal_div_present(self):
        """index.html contains <div id="about-modal">."""
        content = HTML_FILE.read_text()
        assert re.search(
            r'<div[^>]*id="about-modal"', content
        ), '<div id="about-modal"> missing from index.html'

    def test_about_modal_has_hidden_class_by_default(self):
        """The #about-modal element carries the hidden class in index.html."""
        content = HTML_FILE.read_text()
        match = re.search(r'<div[^>]*id="about-modal"[^>]*>', content)
        assert match, '<div id="about-modal"> missing from index.html'
        tag = match.group(0)
        assert "hidden" in tag, (
            '#about-modal must carry class="hidden" by default — '
            "the JS removes it on open"
        )

    def test_about_modal_close_button_present(self):
        """index.html contains a button with id="about-modal-close"."""
        content = HTML_FILE.read_text()
        assert 'id="about-modal-close"' in content, (
            'button with id="about-modal-close" missing from index.html'
        )

    def test_about_modal_precedes_entry_screen_in_source_order(self):
        """#about-modal offset precedes #entry-screen offset in index.html."""
        content = HTML_FILE.read_text()
        assert "about-modal" in content, "#about-modal missing from index.html"
        assert content.index("about-modal") < content.index("entry-screen"), (
            "#about-modal must appear before #entry-screen in source order"
        )


# ── docs-modal.js ─────────────────────────────────────────────────────────────


class TestDocsModalExportsCloseModal:
    """AC2 — docs-modal.js exports closeModal so about-modal.js can call it."""

    def test_close_modal_is_exported_from_docs_modal(self):
        """docs-modal.js contains 'export function closeModal' or 'export { closeModal }'."""
        content = DOCS_MODAL_FILE.read_text()
        assert re.search(
            r"export\s+function\s+closeModal\b|export\s+\{[^}]*closeModal[^}]*\}",
            content,
        ), (
            "docs-modal.js must export closeModal so about-modal.js can close "
            "the docs modal when the About modal opens"
        )


# ── about-modal.js ────────────────────────────────────────────────────────────


class TestAboutModalModuleExists:
    """about-modal.js companion module exists."""

    def test_about_modal_js_file_exists(self):
        """ui/js/about-modal.js exists as a companion module."""
        assert ABOUT_MODAL_FILE.exists(), (
            "ui/js/about-modal.js must exist — "
            "About modal logic belongs in a dedicated companion module"
        )


class TestAboutModalInit:
    """AC2, AC3 — about-modal.js init() exports and wires all event listeners."""

    def test_init_is_a_named_export(self):
        """about-modal.js exports a named function init with no default export."""
        content = ABOUT_MODAL_FILE.read_text()
        assert re.search(
            r"export\s+function\s+init\b", content
        ), "about-modal.js must export a named function 'init'"
        assert "export default" not in content, (
            "about-modal.js must not use export default — named exports only"
        )

    def test_init_binds_about_btn_click(self):
        """init() wires a click listener on .about-btn."""
        content = ABOUT_MODAL_FILE.read_text()
        body = _extract_function_body(content, "init")
        assert "about-btn" in body, "init() must reference .about-btn to wire the click listener"
        assert "click" in body, "init() must bind a click event listener"

    def test_init_binds_about_modal_close_button_click(self):
        """init() wires about-modal-close click to closeModal."""
        content = ABOUT_MODAL_FILE.read_text()
        body = _extract_function_body(content, "init")
        assert "about-modal-close" in body, (
            "init() must reference about-modal-close to wire the close button"
        )
        assert "closeModal" in body, (
            "init() must call closeModal from the close button listener"
        )

    def test_init_binds_escape_key_to_close_modal(self):
        """init() binds a keydown Escape listener that calls closeModal."""
        content = ABOUT_MODAL_FILE.read_text()
        body = _extract_function_body(content, "init")
        assert "Escape" in body, "init() must handle the Escape key"
        assert "closeModal" in body, "init() Escape handler must call closeModal"


class TestAboutModalOpenBehaviour:
    """AC2 — opening the About modal closes the docs modal first."""

    def test_about_modal_imports_close_modal_from_docs_modal(self):
        """about-modal.js imports closeModal (or an alias) from ./docs-modal.js."""
        content = ABOUT_MODAL_FILE.read_text()
        assert re.search(
            r"import\s+\{[^}]*closeModal[^}]*\}\s+from\s+['\"]./docs-modal\.js['\"]",
            content,
        ), (
            "about-modal.js must import closeModal from './docs-modal.js' "
            "to close the docs modal when the About modal opens"
        )

    def test_open_modal_calls_close_docs_modal(self):
        """The openModal function in about-modal.js calls the imported close function."""
        content = ABOUT_MODAL_FILE.read_text()
        body = _extract_function_body(content, "openModal")
        assert body, "openModal function not found in about-modal.js"
        # The import may alias closeModal as closeDocsModal
        assert re.search(r"close\w*Modal\b", body), (
            "openModal() must call the imported closeModal (or its alias) "
            "to close the docs modal before showing the About modal"
        )

    def test_open_modal_removes_hidden_class_from_about_modal(self):
        """openModal() removes the hidden class from #about-modal."""
        content = ABOUT_MODAL_FILE.read_text()
        body = _extract_function_body(content, "openModal")
        assert body, "openModal function not found in about-modal.js"
        assert "remove" in body and "hidden" in body, (
            "openModal() must call classList.remove('hidden') on #about-modal"
        )


class TestAboutModalCloseBehaviour:
    """AC3 — closing the About modal returns focus to the About button."""

    def test_close_modal_adds_hidden_class_to_about_modal(self):
        """closeModal() adds the hidden class to #about-modal."""
        content = ABOUT_MODAL_FILE.read_text()
        body = _extract_function_body(content, "closeModal")
        assert body, "closeModal function not found in about-modal.js"
        assert "add" in body and "hidden" in body, (
            "closeModal() must call classList.add('hidden') on #about-modal"
        )

    def test_close_modal_returns_focus_to_about_btn(self):
        """closeModal() calls focus() on the .about-btn element."""
        content = ABOUT_MODAL_FILE.read_text()
        body = _extract_function_body(content, "closeModal")
        assert body, "closeModal function not found in about-modal.js"
        assert "about-btn" in body, (
            "closeModal() must query .about-btn to return focus"
        )
        assert "focus" in body, (
            "closeModal() must call focus() on .about-btn after closing the modal"
        )

    def test_no_console_log_in_about_modal_js(self):
        """about-modal.js contains no console.log calls."""
        content = ABOUT_MODAL_FILE.read_text()
        assert "console.log" not in content, (
            "about-modal.js must not use console.log — use console.warn or console.error only"
        )


# ── form.js ───────────────────────────────────────────────────────────────────


class TestFormJsWiresAboutModal:
    """AC2 — form.js imports and calls aboutModalInit() at DOMContentLoaded."""

    def test_form_js_imports_init_from_about_modal(self):
        """form.js imports init from ./about-modal.js."""
        content = FORM_FILE.read_text()
        assert re.search(
            r"import\s+\{[^}]*init[^}]*\}\s+from\s+['\"]./about-modal\.js['\"]",
            content,
        ), "form.js must import { init ... } from './about-modal.js'"

    def test_form_js_calls_about_modal_init_at_dom_content_loaded(self):
        """form.js calls aboutModalInit() inside the DOMContentLoaded listener."""
        content = FORM_FILE.read_text()
        assert re.search(r"aboutModalInit\b", content), (
            "form.js must call aboutModalInit() at DOMContentLoaded"
        )
        assert re.search(
            r"DOMContentLoaded.{0,500}aboutModalInit",
            content,
            re.DOTALL,
        ), "aboutModalInit() must be called inside the DOMContentLoaded listener"

    def test_about_modal_does_not_import_from_form_js(self):
        """about-modal.js contains no import from form.js — coupling flows one way."""
        content = ABOUT_MODAL_FILE.read_text()
        assert "form.js" not in content, (
            "about-modal.js must not import from form.js — "
            "companion modules are dependencies of form.js, not peers"
        )


# ── CSS ───────────────────────────────────────────────────────────────────────


class TestAboutModalCSS:
    """AC1 — CSS rules for .header-nav, .about-btn, and #about-modal present in style.css."""

    def test_header_nav_has_flex_layout(self):
        """style.css contains a .header-nav rule with display: flex."""
        content = CSS_FILE.read_text()
        match = re.search(r"\.header-nav\s*\{([^}]*)\}", content, re.DOTALL)
        assert match, ".header-nav rule missing from style.css"
        block = match.group(1)
        assert "flex" in block, ".header-nav must use display: flex"

    def test_about_btn_colour_is_text_on_brand(self):
        """style.css .about-btn rule uses --colour-text-on-brand for color."""
        content = CSS_FILE.read_text()
        match = re.search(r"\.about-btn\s*\{([^}]*)\}", content, re.DOTALL)
        assert match, ".about-btn rule missing from style.css"
        block = match.group(1)
        assert "--colour-text-on-brand" in block, (
            ".about-btn must use var(--colour-text-on-brand) — "
            "the button sits on the brand-coloured header"
        )

    def test_about_btn_has_hover_state(self):
        """style.css contains a .about-btn:hover rule."""
        content = CSS_FILE.read_text()
        assert re.search(r"\.about-btn\s*:\s*hover\s*\{", content), (
            ".about-btn:hover rule missing from style.css — "
            "all interactive elements require a hover state"
        )

    def test_about_btn_has_focus_visible_state(self):
        """style.css contains a .about-btn:focus-visible rule."""
        content = CSS_FILE.read_text()
        assert re.search(r"\.about-btn\s*:\s*focus-visible\s*\{", content), (
            ".about-btn:focus-visible rule missing from style.css — "
            "all interactive elements require a focus-visible state"
        )

    def test_about_modal_has_z_index_200(self):
        """style.css #about-modal rule contains z-index: 200."""
        content = CSS_FILE.read_text()
        match = re.search(r"#about-modal\s*\{([^}]*)\}", content, re.DOTALL)
        assert match, "#about-modal rule missing from style.css"
        block = match.group(1)
        assert re.search(r"z-index\s*:\s*200", block), (
            "#about-modal must have z-index: 200 — "
            "positions the About modal above command-modal (z-index 100)"
        )

    def test_about_modal_not_hidden_selector_uses_display_flex(self):
        """style.css contains #about-modal:not(.hidden) { display: flex }."""
        content = CSS_FILE.read_text()
        assert re.search(
            r"#about-modal\s*:\s*not\s*\(\s*\.hidden\s*\)\s*\{[^}]*display\s*:\s*flex",
            content,
            re.DOTALL,
        ), (
            "#about-modal:not(.hidden) rule with display: flex missing from style.css — "
            "follow the established :not(.hidden) pattern for modal visibility"
        )
