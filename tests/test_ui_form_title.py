"""Tests for form-title, logfile, and agentFile field wiring: population, state linkage, validation, and error reset.

Covers:
- T1.1: index.html has data-testid="form-title-error" span
- T1.2: populateForm body references form-title data-testid
- T1.3: DOMContentLoaded wires form-title input to setState with repo key
- T1.4: DOMContentLoaded wires form-title blur to validate against NAME_PATTERN
- T1.5: DOMContentLoaded wires form-title keydown to clear form-title-error
- T2.1: index.html has form-logfile input below form-title
- T2.2: index.html has form-logfile-error span
- T2.3: populateForm references form-logfile data-testid
- T2.4: DOMContentLoaded wires form-logfile input to setState with repo key
- T2.5: DOMContentLoaded wires form-logfile blur to file path validation
- T3.1: index.html has form-agentFile radio inputs (AGENTS and CLAUDE values)
- T3.2: populateForm references form-agentFile data-testid
- T3.3: DOMContentLoaded wires form-agentFile radios to setState with repo key
"""

import re
from html.parser import HTMLParser
from pathlib import Path

JS_FILE = Path("ui/js/form.js")
WIRING_FILE = Path("ui/js/event-wiring.js")  # event listener wiring lives here
HTML_FILE = Path("ui/index.html")


def _extract_function_body(content: str, fn_name: str) -> str:
    """Extract the body of a named function from JS source using brace-matching.

    Handles both declaration form (function name(...) {) and assignment form
    (name = function(...) { or name = (...) => {).
    Returns the text between the outermost braces (exclusive).
    Returns an empty string if the function is not found.
    """
    pattern = (
        rf"(?:async\s+)?(?:function\s+{fn_name}\s*\([^)]*\)"
        rf"|{fn_name}\s*=\s*(?:async\s+)?(?:function\s*\([^)]*\)|\([^)]*\)\s*=>))"
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


def _extract_dom_content_loaded_body(content: str) -> str:
    """Extract the body of the DOMContentLoaded async arrow function."""
    marker = 'document.addEventListener("DOMContentLoaded"'
    idx = content.find(marker)
    if idx == -1:
        return ""
    brace_start = content.find("{", idx)
    if brace_start == -1:
        return ""
    depth = 0
    for i, ch in enumerate(content[brace_start:]):
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                return content[brace_start + 1 : brace_start + i]
    return ""


class _TestidCollector(HTMLParser):
    """Collect all data-testid attribute values from parsed HTML."""

    def __init__(self) -> None:
        super().__init__()
        self.testids: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        for name, value in attrs:
            if name == "data-testid" and value is not None:
                self.testids.append(value)


class TestFormTitleHtml:
    """HTML structure tests for the form-title error slot."""

    def test_form_title_error_span_present_in_index_html(self):
        """index.html has a data-testid="form-title-error" element. (T1.1)"""
        collector = _TestidCollector()
        collector.feed(HTML_FILE.read_text())
        assert (
            "form-title-error" in collector.testids
        ), "data-testid='form-title-error' span not found in index.html"


class TestFormTitlePopulate:
    """form.js populateForm population tests."""

    def test_populate_form_references_form_title(self):
        """populateForm body references form-title data-testid. (T1.2)"""
        content = JS_FILE.read_text()
        body = _extract_function_body(content, "populateForm")
        assert body, "populateForm function body not found in form.js"
        assert "form-title" in body, "populateForm body does not reference form-title data-testid"


class TestFormTitleEventWiring:
    """DOMContentLoaded event wiring tests for form-title."""

    def test_form_title_input_wired_to_set_state_with_repo(self):
        """event-wiring.js wires form-title input to setState with a repo patch. (T1.3)"""
        body = WIRING_FILE.read_text()
        assert "form-title" in body, "form-title not referenced in event-wiring.js"
        assert re.search(
            r"setState\s*\(\s*\{[^}]*repo", body
        ), "setState with repo key not called in event-wiring.js"

    def test_form_title_blur_validates_against_name_pattern(self):
        """event-wiring.js wires form-title blur to validate against NAME_PATTERN. (T1.4)"""
        body = WIRING_FILE.read_text()
        assert re.search(
            r"form-title.*blur|blur.*form-title", body, re.DOTALL
        ), "form-title blur listener not wired in event-wiring.js"
        assert (
            "NAME_PATTERN" in body or "validateNameField" in body
        ), "blur handler does not reference NAME_PATTERN or validateNameField"

    def test_form_title_keydown_clears_error(self):
        """event-wiring.js wires form-title keydown to clear the form-title-error element. (T1.5)"""
        body = WIRING_FILE.read_text()
        assert re.search(
            r"form-title.*keydown|keydown.*form-title", body, re.DOTALL
        ), "form-title keydown listener not wired in event-wiring.js"
        assert "form-title-error" in body, "keydown handler does not reference form-title-error"


class TestFormLogfileHtml:
    """HTML structure tests for the logfile field."""

    def test_form_logfile_input_present_in_index_html(self):
        """index.html has a data-testid="form-logfile" input element. (T2.1)"""
        collector = _TestidCollector()
        collector.feed(HTML_FILE.read_text())
        assert (
            "form-logfile" in collector.testids
        ), "data-testid='form-logfile' input not found in index.html"

    def test_form_logfile_error_span_present_in_index_html(self):
        """index.html has a data-testid="form-logfile-error" element. (T2.2)"""
        collector = _TestidCollector()
        collector.feed(HTML_FILE.read_text())
        assert (
            "form-logfile-error" in collector.testids
        ), "data-testid='form-logfile-error' span not found in index.html"


class TestFormLogfilePopulate:
    """form.js populateForm population tests for logfile."""

    def test_populate_form_references_form_logfile(self):
        """populateForm body references form-logfile data-testid. (T2.3)"""
        content = JS_FILE.read_text()
        body = _extract_function_body(content, "populateForm")
        assert body, "populateForm function body not found in form.js"
        assert (
            "form-logfile" in body
        ), "populateForm body does not reference form-logfile data-testid"


class TestFormLogfileEventWiring:
    """DOMContentLoaded event wiring tests for logfile."""

    def test_form_logfile_input_wired_to_set_state_with_repo(self):
        """event-wiring.js wires form-logfile input to setState with a repo patch. (T2.4)"""
        body = WIRING_FILE.read_text()
        assert "form-logfile" in body, "form-logfile not referenced in event-wiring.js"
        assert re.search(
            r"setState\s*\(\s*\{[^}]*repo", body
        ), "setState with repo key not called in event-wiring.js"

    def test_form_logfile_blur_validates_file_path(self):
        """event-wiring.js wires form-logfile blur to file path validation. (T2.5)"""
        body = WIRING_FILE.read_text()
        assert re.search(
            r"form-logfile.*blur|blur.*form-logfile", body, re.DOTALL
        ), "form-logfile blur listener not wired in event-wiring.js"
        assert "form-logfile-error" in body, "blur handler does not reference form-logfile-error"


class TestFormAgentFileHtml:
    """HTML structure tests for the agentFile radio group."""

    def test_form_agent_file_radios_present_in_index_html(self):
        """index.html has radio inputs with data-testid="form-agentFile" for AGENTS and CLAUDE. (T3.1)"""
        html = HTML_FILE.read_text()
        assert "form-agentFile" in html, "data-testid='form-agentFile' not found in index.html"
        assert 'value="AGENTS"' in html, "radio value='AGENTS' not found in index.html"
        assert 'value="CLAUDE"' in html, "radio value='CLAUDE' not found in index.html"


class TestFormAgentFilePopulate:
    """form.js populateForm population tests for agentFile."""

    def test_populate_form_references_form_agent_file(self):
        """populateForm body references form-agentFile data-testid. (T3.2)"""
        content = JS_FILE.read_text()
        body = _extract_function_body(content, "populateForm")
        assert body, "populateForm function body not found in form.js"
        assert (
            "form-agentFile" in body
        ), "populateForm body does not reference form-agentFile data-testid"


class TestFormAgentFileEventWiring:
    """DOMContentLoaded event wiring tests for agentFile."""

    def test_form_agent_file_change_wired_to_set_state_with_repo(self):
        """event-wiring.js wires form-agentFile radios to setState with a repo patch. (T3.3)"""
        body = WIRING_FILE.read_text()
        assert "form-agentFile" in body, "form-agentFile not referenced in event-wiring.js"
        assert re.search(
            r"setState\s*\(\s*\{[^}]*repo", body
        ), "setState with repo key not called in event-wiring.js"
