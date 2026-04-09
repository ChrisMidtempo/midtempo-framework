"""Tests for documentation modal HTML structure in ui/index.html.

Covers:
- <header id="app-header"> present as first child of <body> (B17)
- Documentation button present inside #app-header (B17)
- <div id="docs-modal"> present (B18)
- #docs-modal-close button present (B18)
- Three tab buttons with correct data-tab values (B19)
- #docs-modal-content pane present (B18)
- marked.js script tag appears before form.js module tag (B20)
"""

import re
from pathlib import Path

HTML_FILE = Path("ui/index.html")


class TestAppHeaderStructure:
    """B17 — <header id="app-header"> present as first child of <body> in index.html."""

    def test_app_header_element_present_before_entry_screen(self):
        """index.html contains <header id="app-header"> and its offset precedes #entry-screen. (B17, T3.1)"""
        content = HTML_FILE.read_text()
        assert re.search(
            r'<header[^>]*id="app-header"', content
        ), '<header id="app-header"> missing from index.html'
        assert content.index("app-header") < content.index(
            "entry-screen"
        ), "#app-header must appear before #entry-screen in source order"

    def test_docs_btn_present_inside_app_header(self):
        """index.html contains a docs-btn class button inside #app-header. (B17, T3.2)"""
        content = HTML_FILE.read_text()
        assert "docs-btn" in content, "docs-btn class missing from index.html"
        assert content.index("docs-btn") > content.index(
            "app-header"
        ), "docs-btn must appear after app-header in source order"

    def test_midtempo_logo_present_in_app_header(self):
        """index.html contains an <img> referencing midtempo-logo inside #app-header, before the docs-btn."""
        content = HTML_FILE.read_text()
        assert "midtempo-logo" in content, "midtempo-logo img reference missing from index.html"
        assert content.index("midtempo-logo") > content.index("app-header"), (
            "midtempo-logo must appear after the #app-header opening tag"
        )
        assert content.index("midtempo-logo") < content.index("docs-btn"), (
            "midtempo-logo must appear before docs-btn — logo is on the left side of the header"
        )


class TestDocsModalStructure:
    """B18, B19 — #docs-modal element with close button, tabs, and content pane present."""

    def test_docs_modal_div_present(self):
        """index.html contains <div id="docs-modal">. (B18, T3.3)"""
        content = HTML_FILE.read_text()
        assert re.search(
            r'<div[^>]*id="docs-modal"', content
        ), '<div id="docs-modal"> missing from index.html'

    def test_docs_modal_close_button_present(self):
        """index.html contains a button with id="docs-modal-close". (B18, T3.4)"""
        content = HTML_FILE.read_text()
        assert (
            'id="docs-modal-close"' in content
        ), 'button with id="docs-modal-close" missing from index.html'

    def test_three_tab_buttons_with_correct_data_tab_values_present(self):
        """index.html contains tab buttons with data-tab="overview", "guide", and "install". (B19, T3.5)"""
        content = HTML_FILE.read_text()
        assert (
            'data-tab="overview"' in content
        ), 'tab button with data-tab="overview" missing from index.html'
        assert (
            'data-tab="guide"' in content
        ), 'tab button with data-tab="guide" missing from index.html'
        assert (
            'data-tab="install"' in content
        ), 'tab button with data-tab="install" missing from index.html'

    def test_docs_modal_content_pane_present(self):
        """index.html contains <div id="docs-modal-content">. (B18, T3.6)"""
        content = HTML_FILE.read_text()
        assert (
            'id="docs-modal-content"' in content
        ), 'element with id="docs-modal-content" missing from index.html'


class TestScriptOrder:
    """B20 — marked.js script tag appears before form.js module tag in index.html."""

    def test_marked_script_tag_appears_before_form_js_tag(self):
        """marked.js CDN <script> tag appears earlier in source than the form.js <script> tag. (B20, T3.7)"""
        content = HTML_FILE.read_text()
        assert "marked" in content, "marked CDN script tag missing from index.html"
        assert "form.js" in content, "form.js script tag missing from index.html"
        assert content.index("marked") < content.index("form.js"), (
            "marked.js script tag must appear before form.js in source order "
            "so window.marked exists when docs-modal.js calls marked.parse()"
        )
