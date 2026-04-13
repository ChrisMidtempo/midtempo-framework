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


class TestConfigurationAnchorLink:
    """A link that opens the docs modal at the Overview #configuration anchor."""

    def test_configuration_anchor_link_present_in_index_html(self):
        """index.html contains an element with data-testid="docs-link-configuration"."""
        content = HTML_FILE.read_text()
        assert 'data-testid="docs-link-configuration"' in content, (
            'index.html must contain an element with data-testid="docs-link-configuration"'
        )

    def test_configuration_link_has_no_inline_onclick(self):
        """The docs-link-configuration element uses no inline onclick handler."""
        content = HTML_FILE.read_text()
        match = re.search(r'<[^>]*data-testid="docs-link-configuration"[^>]*>', content)
        assert match, 'element with data-testid="docs-link-configuration" not found'
        tag = match.group(0)
        assert "onclick" not in tag, (
            "docs-link-configuration must not use an inline onclick handler — "
            "wire via event-wiring.js"
        )


class TestExamplesTabGroup:
    """Examples tab group renders in the docs-modal header with a non-clickable label."""

    def test_examples_tabs_have_correct_data_tab_values(self):
        """index.html contains tab buttons with data-tab="decisions", "design", "plan", "tests"."""
        content = HTML_FILE.read_text()
        assert 'data-tab="decisions"' in content, (
            'tab button with data-tab="decisions" missing from index.html'
        )
        assert 'data-tab="design"' in content, (
            'tab button with data-tab="design" missing from index.html'
        )
        assert 'data-tab="plan"' in content, (
            'tab button with data-tab="plan" missing from index.html'
        )
        assert 'data-tab="tests"' in content, (
            'tab button with data-tab="tests" missing from index.html'
        )

    def test_examples_label_element_present(self):
        """index.html contains a docs-examples-label element with the text 'Examples:'."""
        content = HTML_FILE.read_text()
        assert "docs-examples-label" in content, (
            "docs-examples-label class missing from index.html — "
            "the Examples group requires a styled non-clickable label"
        )
        assert "Examples:" in content, (
            "index.html must contain the literal text 'Examples:' "
            "for the Examples tab group label"
        )

    def test_examples_tabs_group_wrapper_present(self):
        """index.html contains a docs-examples-tabs wrapper holding the label and four tabs."""
        content = HTML_FILE.read_text()
        assert "docs-examples-tabs" in content, (
            "docs-examples-tabs wrapper missing from index.html — "
            "needed for CSS selector to push the group to the right of the header"
        )

    def test_examples_tabs_source_order_follows_install_and_precedes_close(self):
        """Source order: Examples label and tabs follow the install tab and precede docs-modal-close."""
        content = HTML_FILE.read_text()
        install_idx = content.index('data-tab="install"')
        label_idx = content.index("docs-examples-label")
        decisions_idx = content.index('data-tab="decisions"')
        close_idx = content.index("docs-modal-close")
        assert install_idx < label_idx, (
            "docs-examples-label must appear after the install tab in source order"
        )
        assert label_idx < decisions_idx, (
            "docs-examples-label must appear before the decisions tab in source order"
        )
        assert decisions_idx < close_idx, (
            "example tabs must appear before the docs-modal-close button in source order"
        )


class TestMobileHamburgerHTML:
    """Mobile hamburger button and dropdown present in index.html."""

    def test_hamburger_button_element_present(self):
        """index.html contains a button with data-testid="docs-examples-hamburger"."""
        content = HTML_FILE.read_text()
        assert 'data-testid="docs-examples-hamburger"' in content, (
            'index.html must contain a button with data-testid="docs-examples-hamburger" — '
            "the hamburger replaces the examples tab group on mobile"
        )

    def test_hamburger_button_has_id(self):
        """index.html hamburger button has id="docs-examples-hamburger"."""
        content = HTML_FILE.read_text()
        assert 'id="docs-examples-hamburger"' in content, (
            'index.html must contain id="docs-examples-hamburger" — '
            "docs-modal.js wires the hamburger toggle by this ID"
        )

    def test_examples_dropdown_element_present(self):
        """index.html contains an element with id="docs-examples-dropdown"."""
        content = HTML_FILE.read_text()
        assert 'id="docs-examples-dropdown"' in content, (
            'index.html must contain an element with id="docs-examples-dropdown" — '
            "the dropdown holds the four example tab buttons on mobile"
        )

    def test_examples_dropdown_contains_example_tab_buttons(self):
        """index.html #docs-examples-dropdown contains tab buttons for all four examples."""
        content = HTML_FILE.read_text()
        dropdown_start = content.find('id="docs-examples-dropdown"')
        assert dropdown_start != -1, 'id="docs-examples-dropdown" missing from index.html'
        # Find content inside the dropdown div (up to its closing tag)
        dropdown_section = content[dropdown_start: dropdown_start + 800]
        for tab in ("decisions", "design", "plan", "tests"):
            assert f'data-tab="{tab}"' in dropdown_section, (
                f'data-tab="{tab}" button missing from #docs-examples-dropdown'
            )

    def test_examples_dropdown_contains_title(self):
        """index.html #docs-examples-dropdown contains a title element with text 'Example Docs'."""
        content = HTML_FILE.read_text()
        dropdown_start = content.find('id="docs-examples-dropdown"')
        assert dropdown_start != -1, 'id="docs-examples-dropdown" missing from index.html'
        dropdown_section = content[dropdown_start: dropdown_start + 800]
        assert "docs-examples-dropdown-title" in dropdown_section, (
            "docs-examples-dropdown-title class missing from #docs-examples-dropdown — "
            "dropdown needs a title so users know what the menu contains"
        )
        assert "Example Docs" in dropdown_section, (
            "'Example Docs' text missing from #docs-examples-dropdown — "
            "the title must read 'Example Docs'"
        )


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
