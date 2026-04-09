"""Tests for YAML panel syntax highlighting refinement.

Covers:
- T1: highlight.js <script> tag present in index.html
- T2: highlight.js CSS <link> tag present in index.html
- T3: refreshYAML body calls hljs.highlight
- T4: refreshYAML sets innerHTML (not textContent alone)
"""

import re
from pathlib import Path

HTML_FILE = Path("ui/index.html")
CSS_FILE = Path("ui/css/style.css")
JS_FILE = Path("ui/js/form.js")


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


class TestYamlPanelHighlighting:
    """Tests for highlight.js integration in the YAML panel."""

    def test_highlight_js_script_tag_present(self):
        """A <script> tag with a highlight.js src is present in index.html. (T1)"""
        content = HTML_FILE.read_text()
        assert re.search(
            r'<script[^>]+src=["\'][^"\']*highlight[^"\']*["\']', content
        ), "No <script> tag with highlight.js src found in index.html"

    def test_highlight_js_cdn_css_not_in_index_html(self):
        """No highlight.js CDN CSS <link> in index.html — token colours defined in style.css. (T2)"""
        content = HTML_FILE.read_text()
        assert not re.search(
            r'<link[^>]+href=["\'][^"\']*highlight[^"\']*["\']', content
        ), "highlight.js CDN CSS link found in index.html — remove it and use style.css instead"

    def test_refresh_yaml_calls_hljs_highlight(self):
        """refreshYAML body calls hljs.highlight to colorise YAML output. (T3)"""
        content = JS_FILE.read_text()
        body = _extract_function_body(content, "refreshYAML")
        assert body, "refreshYAML function body not found in form.js"
        assert (
            "hljs.highlight" in body
        ), "refreshYAML does not call hljs.highlight — syntax highlighting not applied"

    def test_refresh_yaml_sets_inner_html(self):
        """refreshYAML sets innerHTML to render highlight.js span markup. (T4)"""
        content = JS_FILE.read_text()
        body = _extract_function_body(content, "refreshYAML")
        assert body, "refreshYAML function body not found in form.js"
        assert (
            "innerHTML" in body
        ), "refreshYAML does not set innerHTML — highlighted markup cannot render as HTML"

    def test_style_css_defines_hljs_attr_colour(self):
        """style.css defines a colour rule for .hljs-attr (YAML keys). (T5)"""
        content = CSS_FILE.read_text()
        assert re.search(
            r"\.hljs-attr\b[^{]*\{[^}]*color\s*:", content
        ), "style.css does not define a colour for .hljs-attr — YAML keys will be unstyled"

    def test_style_css_defines_hljs_string_colour(self):
        """style.css defines a colour rule for .hljs-string (YAML string values). (T6)"""
        content = CSS_FILE.read_text()
        assert re.search(
            r"\.hljs-string\b[^{]*\{[^}]*color\s*:", content
        ), "style.css does not define a colour for .hljs-string — string values will be unstyled"

    def test_style_css_defines_hljs_literal_colour(self):
        """style.css defines a colour rule for .hljs-literal (booleans and null). (T7)"""
        content = CSS_FILE.read_text()
        assert re.search(
            r"\.hljs-literal\b[^{]*\{[^}]*color\s*:", content
        ), "style.css does not define a colour for .hljs-literal — booleans will be unstyled"

    def test_style_css_defines_hljs_number_colour(self):
        """style.css defines a colour rule for .hljs-number (numeric values). (T8)"""
        content = CSS_FILE.read_text()
        assert re.search(
            r"\.hljs-number\b[^{]*\{[^}]*color\s*:", content
        ), "style.css does not define a colour for .hljs-number — numbers will be unstyled"
