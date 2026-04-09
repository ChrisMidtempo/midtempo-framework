"""Tests for Stage 7 UI: server calls, modal, error rendering, HTML banner slots, E2E integration.

Covers:
- T1.1:  callInit function defined in form.js (B1)
- T1.2:  callGenerate function defined in form.js (B2)
- T1.3:  callInit body references /api/init endpoint (B3)
- T1.4:  callGenerate body references /api/generate endpoint (B4)
- T1.5:  callGenerate body uses URL.createObjectURL (B5)
- T1.6:  No dynamic innerHTML assignment in server-calls or modal groups (B6, CG-IV6)
- T1.7:  showModal function defined in form.js (B7)
- T1.8:  hideModal function defined in form.js (B8)
- T1.9:  showModal body references modal-download (B9)
- T2.1:  data-testid="init-error" element present in index.html (B10)
- T2.2:  data-testid="generate-error" element present in index.html (B11)
- T3.1:  POST /api/init (valid) → 200 + yml; POST /api/generate → 200 + zip binary (B12)
- T3.2:  Extracted zip config passes validate_config_with_enhanced_errors (B13)
- T3.3:  POST /api/generate with invalid config → 422 + {"error": string} (B14)
"""

import re
import zipfile
from html.parser import HTMLParser
from pathlib import Path

import pytest
import yaml
from fastapi.testclient import TestClient

from scripts.validate_config import validate_config_with_enhanced_errors
from server.app import create_app
from tests.helpers.config_factory import create_valid_config

JS_FILE = Path("ui/js/form.js")
HTML_FILE = Path("ui/index.html")


def _extract_function_body(content: str, fn_name: str) -> str:
    """Extract the body of a named function from JS source using brace-matching.

    Handles both declaration form (function name(...) {) and assignment form
    (name = function(...) { or async function name(...) {).
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


class _TestidCollector(HTMLParser):
    """Collect all data-testid attribute values from parsed HTML."""

    def __init__(self) -> None:
        super().__init__()
        self.testids: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        for name, value in attrs:
            if name == "data-testid" and value is not None:
                self.testids.append(value)


class TestFormJsStage7:
    """Tests for Stage 7 form.js additions: server calls, modal, error rendering."""

    def test_call_init_function_defined(self):
        """callInit is declared as a function in form.js. (T1.1, B1)"""
        content = JS_FILE.read_text()
        assert re.search(
            r"(?:async\s+)?function\s+callInit\b", content
        ), "callInit function not defined in form.js"

    def test_call_generate_function_defined(self):
        """callGenerate is declared as a function in form.js. (T1.2, B2)"""
        content = JS_FILE.read_text()
        assert re.search(
            r"(?:async\s+)?function\s+callGenerate\b", content
        ), "callGenerate function not defined in form.js"

    def test_call_init_body_references_api_init_endpoint(self):
        """callInit body contains the /api/init fetch target. (T1.3, B3)"""
        content = JS_FILE.read_text()
        body = _extract_function_body(content, "callInit")
        assert body, "callInit function body not found in form.js"
        assert "/api/init" in body, "callInit body does not reference /api/init"

    def test_call_generate_body_references_api_generate_endpoint(self):
        """callGenerate body contains the /api/generate fetch target. (T1.4, B4)"""
        content = JS_FILE.read_text()
        body = _extract_function_body(content, "callGenerate")
        assert body, "callGenerate function body not found in form.js"
        assert "/api/generate" in body, "callGenerate body does not reference /api/generate"

    def test_call_generate_body_uses_url_create_object_url(self):
        """callGenerate body references URL.createObjectURL for blob-to-download-URL. (T1.5, B5)"""
        content = JS_FILE.read_text()
        body = _extract_function_body(content, "callGenerate")
        assert body, "callGenerate function body not found in form.js"
        assert (
            "URL.createObjectURL" in body
        ), "callGenerate body does not reference URL.createObjectURL"

    def test_no_dynamic_inner_html_in_server_calls_or_modal_groups(self):
        """No innerHTML assignment carries an unvetted variable or expression. (T1.6, B6, CG-IV6)

        Three innerHTML assignments are permitted:
        - card.innerHTML = "" — clears fixed modal structure; no user content
        - panel.innerHTML = hljs.highlight(...).value — highlight.js escapes HTML entities
          in the input before adding span markup, so user-derived YAML values cannot inject HTML
        - panel.innerHTML = highlighted.replace(...) — highlighted is the already-escaped output
          of hljs.highlight(); .replace() only inserts a fixed class name string; no user content
          reaches innerHTML
        """
        content = JS_FILE.read_text()
        _approved = {
            '""',
            "''",
            'hljs.highlight(yaml, { language: "yaml" }).value',
            "highlighted.replace(",
        }
        matches = re.findall(r"\.innerHTML\s*=\s*(.+)", content)
        for rhs in matches:
            rhs_stripped = rhs.strip().rstrip(";").strip()
            assert rhs_stripped in _approved, (
                f"Unapproved innerHTML assignment found — value: {rhs_stripped!r}. "
                "User-derived content must use textContent or an approved escaped source (CG-IV6)."
            )

    def test_show_modal_function_defined(self):
        """showModal is declared as a function in form.js. (T1.7, B7)"""
        content = JS_FILE.read_text()
        assert re.search(
            r"function\s+showModal\b", content
        ), "showModal function not defined in form.js"

    def test_hide_modal_function_defined(self):
        """hideModal is declared as a function in form.js. (T1.8, B8)"""
        content = JS_FILE.read_text()
        assert re.search(
            r"function\s+hideModal\b", content
        ), "hideModal function not defined in form.js"

    def test_show_modal_body_references_modal_download(self):
        """showModal body references modal-download, confirming the download anchor is built. (T1.9, B9)"""
        content = JS_FILE.read_text()
        body = _extract_function_body(content, "showModal")
        assert body, "showModal function body not found in form.js"
        assert "modal-download" in body, "showModal body does not reference modal-download"

    def test_modal_icon_is_appended_to_filename_element(self):
        """showModal appends the icon span into nameEl so icon and filename render on one line. (T1.10)"""
        content = JS_FILE.read_text()
        body = _extract_function_body(content, "showModal")
        assert body, "showModal function body not found in form.js"
        assert re.search(
            r"nameEl\.(?:append|prepend)\s*\(\s*icon\b", body
        ), "showModal does not append/prepend icon into nameEl — icon must be the first child of modal-filename"

    def test_call_generate_filename_uses_name_only(self):
        """callGenerate constructs the download filename as {name}.zip with no suffix."""
        content = JS_FILE.read_text()
        body = _extract_function_body(content, "callGenerate")
        assert body, "callGenerate function body not found in form.js"
        assert re.search(
            r"`\$\{.*?\}\.zip`", body
        ), "callGenerate does not construct filename as `${...}.zip`"
        assert (
            "midtempo-framework" not in body.split(".zip")[0].split("`${")[-1]
        ), "callGenerate filename contains unexpected suffix before .zip"


class TestIndexHtmlStage7:
    """Tests for Stage 7 index.html additions: error banner slot elements."""

    def test_init_error_testid_present_in_html(self):
        """index.html contains an element with data-testid="init-error". (T2.1, B10)"""
        content = HTML_FILE.read_text()
        collector = _TestidCollector()
        collector.feed(content)
        assert (
            "init-error" in collector.testids
        ), 'data-testid="init-error" element not present in index.html'

    def test_generate_error_testid_present_in_html(self):
        """index.html contains an element with data-testid="generate-error". (T2.2, B11)"""
        content = HTML_FILE.read_text()
        collector = _TestidCollector()
        collector.feed(content)
        assert (
            "generate-error" in collector.testids
        ), 'data-testid="generate-error" element not present in index.html'


@pytest.mark.integration
class TestServerCallsE2E:
    """End-to-end integration tests for Stage 7 server contracts."""

    def test_new_flow_init_then_generate_returns_zip(self, tmp_path):
        """POST /api/init → yml; POST /api/generate → 200 + zip binary. (T3.1, B12)"""
        client = TestClient(create_app(ui_dir=tmp_path))

        init_response = client.post(
            "/api/init",
            json={"name": "test-repo", "language": "python"},
        )
        assert init_response.status_code == 200
        init_data = init_response.json()
        assert "yml" in init_data, "init response JSON missing 'yml' key"
        assert init_data["yml"], "init response 'yml' value is empty"

        config_dict = yaml.safe_load(init_data["yml"])

        generate_response = client.post("/api/generate", json={"config": config_dict})
        assert generate_response.status_code == 200
        content_type = generate_response.headers.get("Content-Type", "")
        assert (
            "zip" in content_type or "octet-stream" in content_type
        ), f"Expected zip or octet-stream content type, got: {content_type}"
        assert len(generate_response.content) > 0, "generate response body is empty"

    def test_extracted_zip_config_passes_validation(self, tmp_path):
        """Zip extracted from /api/generate contains a config that passes validate_config_with_enhanced_errors. (T3.2, B13)"""
        client = TestClient(create_app(ui_dir=tmp_path))
        config_dict = create_valid_config()

        generate_response = client.post("/api/generate", json={"config": config_dict})
        assert generate_response.status_code == 200

        zip_path = tmp_path / "output.zip"
        zip_path.write_bytes(generate_response.content)

        extract_dir = tmp_path / "extracted"
        with zipfile.ZipFile(zip_path) as zf:
            zf.extractall(extract_dir)

        yml_files = list(extract_dir.rglob(".midtempo-framework.yml"))
        assert yml_files, ".midtempo-framework.yml not found in extracted zip"

        validate_config_with_enhanced_errors(yml_files[0])

    def test_generate_with_invalid_config_returns_422_with_error_key(self, tmp_path):
        """POST /api/generate with invalid config returns 422 and {"error": string}. (T3.3, B14)"""
        client = TestClient(create_app(ui_dir=tmp_path))

        response = client.post("/api/generate", json={"config": {"name": "x"}})

        assert response.status_code == 422
        body = response.json()
        assert "error" in body, "422 response body missing 'error' key"
        assert isinstance(body["error"], str), "'error' value is not a string"
        assert body["error"], "'error' value is empty"
        assert (
            "detail" not in body
        ), "422 response contains 'detail' key — FastAPI default not overridden per architecture §2.7"
