"""Tests for ui/js/docs-modal.js companion module.

Covers static analysis of JS source to verify:
- init() exported and binds all event listeners (B5)
- openModal() activates overview tab by default (B7)
- closeModal() restores focus to Documentation button (B12)
- fetchDoc() disables tab button; re-enables in all paths; stores result in cache (B8, B9)
- activateTab() skips fetch when cache entry exists (B8)
- Fetch failure sets error via textContent not innerHTML (B13)
- No console.log in source (B14)
- Module-level cache object and DOCS constant declared (B8)
"""

import re
from pathlib import Path

DOCS_MODAL_FILE = Path("ui/js/docs-modal.js")


def _extract_function_body(content: str, fn_name: str) -> str:
    """Return the body of a named function from JS source using brace-matching.

    Handles:
    - declaration form: function name(...) {
    - async declaration: async function name(...) {
    - assignment form: name = function(...) { or name = (...) => {
    Returns the text between the outermost braces (exclusive).
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


class TestDocsModalInit:
    """B5 — init() exported and binds all event listeners."""

    def test_init_function_is_a_named_export_without_default_export(self):
        """docs-modal.js contains export function init (named export; no default export). (B5, T4.1)"""
        content = DOCS_MODAL_FILE.read_text()
        assert re.search(
            r"export\s+function\s+init\b", content
        ), "docs-modal.js must export a named function 'init'"
        assert (
            "export default" not in content
        ), "docs-modal.js must not use export default — named exports only"

    def test_init_body_binds_documentation_button_click_to_open_modal(self):
        """init() body wires a click listener that calls openModal. (B5, B6, T4.2)"""
        content = DOCS_MODAL_FILE.read_text()
        body = _extract_function_body(content, "init")
        assert "openModal" in body, "init() must wire a click listener that calls openModal"
        assert "click" in body, "init() must bind a click event listener"

    def test_init_body_binds_close_button_click_to_close_modal(self):
        """init() body wires docs-modal-close click to closeModal. (B5, B10, T4.3)"""
        content = DOCS_MODAL_FILE.read_text()
        body = _extract_function_body(content, "init")
        assert (
            "docs-modal-close" in body
        ), "init() must reference docs-modal-close to wire the close button"
        assert "closeModal" in body, "init() must call closeModal from the close button listener"

    def test_init_body_binds_escape_keydown_to_close_modal(self):
        """init() body wires a keydown listener that calls closeModal on Escape. (B5, B11, T4.4)"""
        content = DOCS_MODAL_FILE.read_text()
        body = _extract_function_body(content, "init")
        assert "keydown" in body, "init() must bind a keydown listener"
        assert "Escape" in body, "init() keydown listener must check for Escape key"
        assert "closeModal" in body, "init() must call closeModal when Escape is pressed"

    def test_init_body_binds_tab_button_clicks_to_activate_tab(self):
        """init() body wires click listeners on tab buttons that call activateTab. (B5, B8, T4.5)"""
        content = DOCS_MODAL_FILE.read_text()
        body = _extract_function_body(content, "init")
        assert "activateTab" in body, "init() must wire tab button clicks to call activateTab"
        assert "data-tab" in body, "init() must query tab buttons by data-tab attribute"


class TestOpenModal:
    """B7 — Overview tab activates by default when modal opens."""

    def test_open_modal_activates_overview_tab_by_default(self):
        """openModal() body calls activateTab with 'overview'. (B7, T4.6)"""
        content = DOCS_MODAL_FILE.read_text()
        body = _extract_function_body(content, "openModal")
        assert (
            "activateTab" in body
        ), "openModal() must call activateTab to activate the default tab"
        assert "overview" in body, "openModal() must activate the 'overview' tab by default"


class TestCloseModal:
    """B12 — Focus returns to Documentation button on close."""

    def test_close_modal_restores_focus_to_documentation_button(self):
        """closeModal() body calls .focus() on the Documentation button element. (B12, T4.7)"""
        content = DOCS_MODAL_FILE.read_text()
        body = _extract_function_body(content, "closeModal")
        assert (
            "focus" in body
        ), "closeModal() must call .focus() to return focus to the Documentation button"
        assert (
            "docs-btn" in body
        ), "closeModal() must reference the docs-btn element to restore focus"


class TestFetchDoc:
    """B9, B8, B13 — fetchDoc disables tab button in all paths; stores in cache; uses textContent on error."""

    def test_fetch_doc_disables_tab_button_and_re_enables_in_all_paths(self):
        """fetchDoc() sets disabled before fetch and clears it in a finally block or both branches. (B9, T4.8)"""
        content = DOCS_MODAL_FILE.read_text()
        body = _extract_function_body(content, "fetchDoc")
        assert "disabled" in body, "fetchDoc() must set disabled = true before the fetch call"
        assert "finally" in body or body.count("disabled") >= 2, (
            "fetchDoc() must re-enable the tab button in all paths "
            "(via finally block or both success and catch branches)"
        )

    def test_fetch_doc_stores_parsed_result_in_cache(self):
        """fetchDoc() body writes the parsed result to cache[key]. (B8, T4.9)"""
        content = DOCS_MODAL_FILE.read_text()
        body = _extract_function_body(content, "fetchDoc")
        assert "cache" in body, "fetchDoc() must write the result to the cache object"
        assert re.search(
            r"cache\[", body
        ), "fetchDoc() must assign to cache[key] to store the fetched document"

    def test_fetch_failure_sets_error_via_text_content(self):
        """fetchDoc() catch path sets #docs-modal-content textContent to the error message. (B13, T4.11)"""
        content = DOCS_MODAL_FILE.read_text()
        body = _extract_function_body(content, "fetchDoc")
        assert (
            "textContent" in body
        ), "fetchDoc() must use textContent (not innerHTML) to render the error message"
        assert "Failed to load" in body, "fetchDoc() error message must contain 'Failed to load'"

    def test_fetch_doc_resets_scroll_to_top_after_render(self):
        """fetchDoc() sets contentEl.scrollTop = 0 after rendering fetched content.

        Without this, fetching a new tab after scrolling a previous tab leaves the pane at
        the old scroll position. The user expects new content to start at the top.
        """
        content = DOCS_MODAL_FILE.read_text()
        body = _extract_function_body(content, "fetchDoc")
        assert "scrollTop" in body, (
            "fetchDoc() must set scrollTop = 0 after rendering fetched content"
        )


class TestActivateTab:
    """B8 — activateTab() skips fetch when cache entry exists; resets scroll on every activation."""

    def test_activate_tab_checks_cache_before_calling_fetch_doc(self):
        """activateTab() body checks cache before calling fetchDoc. (B8, T4.10)"""
        content = DOCS_MODAL_FILE.read_text()
        body = _extract_function_body(content, "activateTab")
        assert "cache" in body, "activateTab() must check the cache before fetching"
        assert "fetchDoc" in body, "activateTab() must call fetchDoc when the cache is empty"
        assert body.index("cache") < body.index(
            "fetchDoc"
        ), "activateTab() must check cache BEFORE calling fetchDoc"

    def test_activate_tab_resets_scroll_to_top_on_cache_hit(self):
        """activateTab() sets contentEl.scrollTop = 0 after rendering cached content.

        Without this, switching tabs after scrolling leaves the content pane at the previous
        scroll position. The user expects fresh content to start at the top.
        """
        content = DOCS_MODAL_FILE.read_text()
        body = _extract_function_body(content, "activateTab")
        assert "scrollTop" in body, (
            "activateTab() must set scrollTop = 0 after rendering cached content"
        )


class TestDocsModalSource:
    """B14, B8 — Source-level checks: no console.log; cache and DOCS declared at module level."""

    def test_no_console_log_in_docs_modal_source(self):
        """docs-modal.js contains no console.log call. (B14, T4.12)

        Known-pass: absence of console.log is satisfied by the scaffolding and maintained
        by the no-console-log rule throughout implementation. Pre-approved as a law enforcement check.
        """
        content = DOCS_MODAL_FILE.read_text()
        assert (
            "console.log" not in content
        ), "docs-modal.js must not contain console.log — use console.warn or console.error only"

    def test_cache_object_declared_at_module_level(self):
        """docs-modal.js declares cache as a module-level object (const cache = {}). (B8, T4.13)"""
        content = DOCS_MODAL_FILE.read_text()
        assert re.search(
            r"^const\s+cache\s*=\s*\{\}", content, re.MULTILINE
        ), "docs-modal.js must declare 'const cache = {}' at module level"

    def test_docs_constant_declared_at_module_level_with_three_keys(self):
        """docs-modal.js declares DOCS at module level containing overview, guide, and install keys. (B8, B7, T4.14)"""
        content = DOCS_MODAL_FILE.read_text()
        assert "DOCS" in content, "docs-modal.js must declare a module-level DOCS constant"
        assert "overview" in content, "DOCS constant must contain an 'overview' key"
        assert "guide" in content, "DOCS constant must contain a 'guide' key"
        assert "install" in content, "DOCS constant must contain an 'install' key"


class TestTocAnchorLinks:
    """ToC anchor links scroll within the modal content pane."""

    def test_docs_modal_assigns_id_to_heading_elements(self):
        """docs-modal.js queries heading elements and assigns id attributes for ToC navigation."""
        content = DOCS_MODAL_FILE.read_text()
        assert re.search(r"querySelectorAll\(['\"]h1", content), (
            "docs-modal.js must querySelectorAll heading elements to add id attributes"
        )
        assert re.search(r"\.id\s*=", content), (
            "docs-modal.js must assign .id to heading elements"
        )

    def test_anchor_link_click_calls_scroll_into_view(self):
        """docs-modal.js click handler calls scrollIntoView for href-starting-with-# links."""
        content = DOCS_MODAL_FILE.read_text()
        assert "scrollIntoView" in content, (
            "docs-modal.js must call scrollIntoView to scroll to a ToC target heading"
        )
        assert re.search(r'startsWith\(["\']#["\']', content), (
            "docs-modal.js must check startsWith('#') to identify anchor links"
        )


class TestCrossDocLinks:
    """Cross-doc links switch to the corresponding tab instead of navigating away."""

    def test_cross_doc_link_uses_get_attribute_and_calls_prevent_default(self):
        """docs-modal.js uses getAttribute('href') and preventDefault to intercept cross-doc links."""
        content = DOCS_MODAL_FILE.read_text()
        assert re.search(r"getAttribute\(['\"]href['\"]\)", content), (
            "docs-modal.js must use getAttribute('href') to read the raw relative href"
        )
        assert "preventDefault" in content, (
            "docs-modal.js must call preventDefault to stop browser navigation for intercepted links"
        )


class TestExternalLinkDetection:
    """applyExternalLinks must check raw href, not the resolved absolute URL."""

    def test_apply_external_links_checks_raw_href_not_resolved_url(self):
        """applyExternalLinks uses getAttribute('href') to detect external links.

        a.href is the resolved absolute URL — for <a href="#hash">,
        a.href = 'http://localhost:8000/#hash', which starts with 'http'.
        This incorrectly marks anchor links as external, setting target='_blank'
        and causing the browser to open a new tab (or refresh the current tab
        if popup blocking is active) rather than scrolling within the modal.
        Fix: use getAttribute('href') which returns the raw '#hash' value.
        """
        content = DOCS_MODAL_FILE.read_text()
        body = _extract_function_body(content, "applyExternalLinks")
        assert re.search(r"getAttribute\(['\"]href['\"]\)", body), (
            "applyExternalLinks must use getAttribute('href') not a.href — "
            "a.href resolves to an absolute URL and incorrectly matches anchor links"
        )

    def test_anchor_click_handler_strips_hash_before_element_lookup(self):
        """docs-modal.js click handler strips '#' before querying for the scroll target.

        querySelector('#4-rule') throws a DOMException for IDs starting with a digit.
        Stripping the '#' with href.slice(1) and using an attribute selector
        [id='...'] avoids the CSS identifier restriction.
        """
        content = DOCS_MODAL_FILE.read_text()
        assert re.search(r"href\.slice\(1\)|href\.substring\(1\)", content), (
            "docs-modal.js must strip the '#' from href before the scroll-target lookup"
        )
