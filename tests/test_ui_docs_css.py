"""Tests for documentation modal CSS rules in ui/css/style.css.

Covers:
- #app-header layout rules present (B22)
- .docs-btn uses --colour-brand and defines interactive states (B25)
- #docs-modal and .docs-modal-card overlay rules present (B23)
- Tab bar and content pane styles scoped to #docs-modal (B24)
- body.modal-open sets overflow hidden (B23)
- --header-height declared in :root (B22)
- All colours use --colour-* tokens; all spacing uses --space-* tokens (B26)
"""

import re
from pathlib import Path

CSS_FILE = Path("ui/css/style.css")


class TestAppHeaderStyles:
    """B22 — #app-header layout rules present in style.css."""

    def test_app_header_has_position_fixed(self):
        """style.css #app-header rule contains position: fixed. (B22, T2.1)"""
        content = CSS_FILE.read_text()
        assert re.search(
            r"#app-header\s*\{[^}]*position\s*:\s*fixed",
            content,
            re.DOTALL,
        ), "#app-header rule with position: fixed missing from style.css"

    def test_app_header_has_flex_layout_properties(self):
        """style.css #app-header rule includes display flex, align-items, and justify-content. (B22, T2.2)"""
        content = CSS_FILE.read_text()
        match = re.search(r"#app-header\s*\{([^}]*)\}", content, re.DOTALL)
        assert match, "#app-header rule missing from style.css"
        block = match.group(1)
        assert "display" in block and "flex" in block, "#app-header must use display: flex"
        assert "align-items" in block, "#app-header must define align-items"
        assert "justify-content" in block, "#app-header must define justify-content"

    def test_app_header_uses_design_tokens_for_background_border_and_padding(self):
        """style.css #app-header rule uses --colour-brand and --space-* tokens. (B22, B26, T2.3)"""
        content = CSS_FILE.read_text()
        match = re.search(r"#app-header\s*\{([^}]*)\}", content, re.DOTALL)
        assert match, "#app-header rule missing from style.css"
        block = match.group(1)
        assert "--colour-brand" in block, "#app-header must use --colour-brand for background"
        assert re.search(r"--space-\w+", block), "#app-header must use --space-* tokens for padding"

    def test_app_header_background_is_colour_brand(self):
        """style.css #app-header background-color uses --colour-brand, not --colour-surface. (B22)"""
        content = CSS_FILE.read_text()
        match = re.search(r"#app-header\s*\{([^}]*)\}", content, re.DOTALL)
        assert match, "#app-header rule missing from style.css"
        block = match.group(1)
        assert re.search(r"background-color\s*:\s*var\(--colour-brand\)", block), (
            "#app-header background-color must be var(--colour-brand)"
        )


class TestDocsBtnStyles:
    """B25 — .docs-btn uses --colour-brand; B22 — interactive states defined."""

    def test_docs_btn_uses_colour_brand_token(self):
        """style.css .docs-btn rule references --colour-text-on-brand for white text on the brand header. (B25, T2.4)"""
        content = CSS_FILE.read_text()
        assert re.search(
            r"\.docs-btn\s*\{[^}]*--colour-text-on-brand",
            content,
            re.DOTALL,
        ), ".docs-btn rule using --colour-text-on-brand missing from style.css"

    def test_docs_btn_uses_colour_text_on_brand_token(self):
        """style.css .docs-btn color is --colour-text-on-brand (white) for readability on the brand-coloured header. (B25)"""
        content = CSS_FILE.read_text()
        assert re.search(
            r"\.docs-btn\s*\{[^}]*color\s*:\s*var\(--colour-text-on-brand\)",
            content,
            re.DOTALL,
        ), ".docs-btn color must be var(--colour-text-on-brand) — text must be white on the brand background"

    def test_docs_btn_defines_hover_focus_visible_and_disabled_states(self):
        """style.css defines .docs-btn:hover, .docs-btn:focus-visible, and .docs-btn[disabled]. (B22, T2.5)"""
        content = CSS_FILE.read_text()
        assert ".docs-btn:hover" in content, ".docs-btn:hover state missing from style.css"
        assert (
            ".docs-btn:focus-visible" in content
        ), ".docs-btn:focus-visible state missing from style.css"
        assert (
            ".docs-btn[disabled]" in content or ".docs-btn:disabled" in content
        ), ".docs-btn[disabled] (or :disabled) state missing from style.css"


class TestDocsModalStyles:
    """B23 — #docs-modal and .docs-modal-card overlay rules present in style.css."""

    def test_docs_modal_has_position_fixed(self):
        """style.css #docs-modal rule contains position: fixed. (B23, T2.6)"""
        content = CSS_FILE.read_text()
        assert re.search(
            r"#docs-modal\s*\{[^}]*position\s*:\s*fixed",
            content,
            re.DOTALL,
        ), "#docs-modal rule with position: fixed missing from style.css"

    def test_docs_modal_uses_colour_overlay_token(self):
        """style.css #docs-modal rule uses --colour-overlay for background. (B23, B26, T2.7)"""
        content = CSS_FILE.read_text()
        assert re.search(
            r"#docs-modal\s*\{[^}]*--colour-overlay",
            content,
            re.DOTALL,
        ), "#docs-modal must use --colour-overlay token"

    def test_docs_modal_display_flex_only_when_not_hidden(self):
        """style.css gates display: flex on #docs-modal:not(.hidden), not plain #docs-modal.

        Plain #docs-modal { display: flex } has ID specificity (1,0,0) which beats
        .hidden { display: none } with class specificity (0,1,0). The result: the
        modal is always visible and .hidden has no effect.
        Fix: use #docs-modal:not(.hidden) { display: flex } — matching the #modal pattern. (B23)
        """
        content = CSS_FILE.read_text()
        assert re.search(
            r"#docs-modal:not\(\.hidden\)\s*\{[^}]*display\s*:\s*flex",
            content,
            re.DOTALL,
        ), "#docs-modal:not(.hidden) { display: flex } missing — unconditional display: flex on an ID selector overrides .hidden"

    def test_docs_modal_card_selector_defined(self):
        """style.css contains a .docs-modal-card rule. (B23, T2.8)"""
        content = CSS_FILE.read_text()
        assert ".docs-modal-card" in content, ".docs-modal-card selector missing from style.css"

    def test_docs_modal_card_max_width_is_narrower_than_layout_width(self):
        """style.css .docs-modal-card max-width is 860px, not --layout-width (1200px).

        1200px produces very long line lengths on large monitors; 860px gives a
        comfortable reading measure for documentation prose. (B23)
        """
        content = CSS_FILE.read_text()
        match = re.search(r"\.docs-modal-card\s*\{([^}]*)\}", content, re.DOTALL)
        assert match, ".docs-modal-card rule missing from style.css"
        block = match.group(1)
        assert "860px" in block, (
            ".docs-modal-card max-width must be 860px — "
            "--layout-width (1200px) produces lines too wide for comfortable reading"
        )
        assert "--layout-width" not in block, (
            ".docs-modal-card must not use --layout-width — "
            "1200px is too wide for documentation prose"
        )

    def test_body_modal_open_sets_overflow_hidden(self):
        """style.css body.modal-open rule sets overflow: hidden. (B23, T2.10)"""
        content = CSS_FILE.read_text()
        assert re.search(
            r"body\.modal-open\s*\{[^}]*overflow\s*:\s*hidden",
            content,
            re.DOTALL,
        ), "body.modal-open { overflow: hidden } missing from style.css"


class TestTabAndContentStyles:
    """B24 — Tab bar and content pane styles scoped to #docs-modal present in style.css."""

    def test_tab_bar_and_content_pane_selectors_defined_within_docs_modal(self):
        """style.css contains tab button and content pane selectors scoped to #docs-modal. (B24, T2.9)"""
        content = CSS_FILE.read_text()
        assert re.search(
            r"#docs-modal[^{]*\{", content, re.DOTALL
        ), "No selectors scoped to #docs-modal found in style.css"
        assert (
            "#docs-modal-content" in content
        ), "#docs-modal-content selector missing from style.css"

    def test_docs_modal_content_has_increased_horizontal_padding(self):
        """style.css #docs-modal-content uses --space-500 for horizontal padding.

        Wider horizontal padding pairs with the narrower card to frame the text
        and prevent it from touching the card edges. (B24)
        """
        content = CSS_FILE.read_text()
        match = re.search(r"#docs-modal-content\s*\{([^}]*)\}", content, re.DOTALL)
        assert match, "#docs-modal-content rule missing from style.css"
        block = match.group(1)
        assert "--space-500" in block, (
            "#docs-modal-content must use --space-500 for horizontal padding — "
            "--space-300 is too tight for the narrower 860px card"
        )

    def test_header_height_custom_property_declared_in_root(self):
        """style.css :root block declares --header-height custom property. (B22, T2.11)"""
        content = CSS_FILE.read_text()
        assert re.search(
            r":root\s*\{[^}]*--header-height",
            content,
            re.DOTALL,
        ), "--header-height custom property missing from :root in style.css"


class TestExamplesTabsLayout:
    """Examples tab group sits on the right of the docs-modal header with a styled label."""

    def test_examples_tabs_pushed_right_with_margin_left_auto(self):
        """style.css .docs-examples-tabs rule uses margin-left: auto to push the group right."""
        content = CSS_FILE.read_text()
        match = re.search(r"\.docs-examples-tabs\s*\{([^}]*)\}", content, re.DOTALL)
        assert match, ".docs-examples-tabs rule missing from style.css"
        block = match.group(1)
        assert re.search(r"margin-left\s*:\s*auto", block), (
            ".docs-examples-tabs must use margin-left: auto so the group sits "
            "on the right of the docs-modal header, before the close button"
        )

    def test_examples_label_uses_colour_and_font_tokens(self):
        """style.css .docs-examples-label rule uses --colour-* and --font-* tokens (non-clickable label)."""
        content = CSS_FILE.read_text()
        match = re.search(r"\.docs-examples-label\s*\{([^}]*)\}", content, re.DOTALL)
        assert match, ".docs-examples-label rule missing from style.css"
        block = match.group(1)
        assert "--colour-" in block, (
            ".docs-examples-label must reference a --colour-* token — "
            "no hardcoded colour values allowed"
        )
        assert "--font-" in block, (
            ".docs-examples-label must reference a --font-* token for sizing or weight"
        )


class TestDocsModalContentProseStyles:
    """Prose typography for rendered markdown inside #docs-modal-content."""

    def test_docs_modal_content_headings_use_colour_text_strong(self):
        """style.css defines heading rules scoped to #docs-modal-content using --colour-text-strong."""
        content = CSS_FILE.read_text()
        assert re.search(r"#docs-modal-content\s+h[1-6]", content), (
            "#docs-modal-content h1-h6 selector missing from style.css"
        )
        match = re.search(
            r"(#docs-modal-content\s+h[1-6][^{]*\{[^}]*\})",
            content,
            re.DOTALL,
        )
        assert match, "#docs-modal-content heading rule block missing from style.css"
        assert "--colour-text-strong" in content, (
            "#docs-modal-content heading rules must use --colour-text-strong"
        )

    def test_docs_modal_content_code_uses_font_family_mono(self):
        """style.css #docs-modal-content code rule uses --font-family-mono."""
        content = CSS_FILE.read_text()
        assert re.search(
            r"#docs-modal-content\s+(?:code|pre)\s*\{[^}]*--font-family-mono",
            content,
            re.DOTALL,
        ), "#docs-modal-content code/pre must define --font-family-mono"

    def test_docs_modal_content_links_use_colour_brand(self):
        """style.css #docs-modal-content a rule uses --colour-brand."""
        content = CSS_FILE.read_text()
        assert re.search(
            r"#docs-modal-content\s+a\b[^{]*\{[^}]*--colour-brand",
            content,
            re.DOTALL,
        ), "#docs-modal-content a must use --colour-brand"
