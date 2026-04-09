"""Tests for GET /api/docs/{filename} endpoint in server/app.py.

Covers:
- GET returns 200 with raw markdown for each whitelisted file (B1)
- GET returns 404 for non-whitelisted filename with path traversal protection (B2)
- Non-GET methods return 405 with Allow: GET header (B3)
- CORSMiddleware allow_methods includes GET (B4)
"""

from unittest.mock import patch

from fastapi.testclient import TestClient

from server.app import app


def _json_body(response) -> dict:
    """Safely decode JSON response body; returns {} on parse failure.

    Prevents JSONDecodeError from becoming a test error when the endpoint
    under test returns a non-JSON body (e.g. StaticFiles 404 in RED state).
    """
    try:
        body: dict = response.json()
        return body
    except Exception:
        return {}


class TestDocsEndpointSuccess:
    """B1 — GET /api/docs/{filename} returns 200 with raw markdown for each whitelisted file."""

    def test_get_readme_returns_200_with_plain_text_content(self):
        """GET /api/docs/README.md returns HTTP 200 with text/plain content. (B1, T1.1)"""
        with patch("server.app.Path.read_text", return_value="# README content"):
            client = TestClient(app)
            response = client.get("/api/docs/README.md")
        assert response.status_code == 200
        assert response.headers["content-type"].startswith("text/plain")
        assert response.text == "# README content"

    def test_get_guide_returns_200_with_content(self):
        """GET /api/docs/GUIDE.md returns HTTP 200 with the file body. (B1, T1.2)"""
        with patch("server.app.Path.read_text", return_value="# GUIDE content"):
            client = TestClient(app)
            response = client.get("/api/docs/GUIDE.md")
        assert response.status_code == 200
        assert response.text == "# GUIDE content"

    def test_get_install_returns_200_with_content(self):
        """GET /api/docs/INSTALL.md returns HTTP 200 with the file body. (B1, T1.3)"""
        with patch("server.app.Path.read_text", return_value="# INSTALL content"):
            client = TestClient(app)
            response = client.get("/api/docs/INSTALL.md")
        assert response.status_code == 200
        assert response.text == "# INSTALL content"


class TestDocsEndpointNotFound:
    """B2 — GET returns 404 for non-whitelisted filenames; no filesystem access occurs."""

    def test_get_non_whitelisted_filename_returns_404_without_file_read(self):
        """GET /api/docs/secrets.env returns 404 JSON and does not read the filesystem. (B2, T1.4)"""
        with patch("server.app.Path.read_text") as mock_read:
            client = TestClient(app)
            response = client.get("/api/docs/secrets.env")
        assert response.status_code == 404
        assert _json_body(response) == {"error": "Not found"}
        mock_read.assert_not_called()

    def test_get_path_traversal_returns_404_without_file_read(self):
        """GET /api/docs/..%2F..%2F..%2Fetc%2Fpasswd returns 404 without reading filesystem. (B2, T1.5)"""
        with patch("server.app.Path.read_text") as mock_read:
            client = TestClient(app)
            response = client.get("/api/docs/..%2F..%2F..%2Fetc%2Fpasswd")
        assert response.status_code == 404
        assert _json_body(response) == {"error": "Not found"}
        mock_read.assert_not_called()


class TestDocsEndpointMethodNotAllowed:
    """B3 — Non-GET methods on /api/docs/{filename} return 405 with Allow: GET header."""

    def test_post_returns_405_with_allow_get_header(self):
        """POST /api/docs/README.md returns 405 with Allow: GET response header. (B3, T1.6)"""
        client = TestClient(app)
        response = client.post("/api/docs/README.md")
        assert response.status_code == 405
        assert response.headers.get("Allow") == "GET"

    def test_put_patch_delete_head_all_return_405(self):
        """PUT, PATCH, DELETE, and HEAD on /api/docs/README.md all return HTTP 405. (B3, T1.7)"""
        client = TestClient(app)
        assert client.put("/api/docs/README.md").status_code == 405
        assert client.patch("/api/docs/README.md").status_code == 405
        assert client.delete("/api/docs/README.md").status_code == 405
        assert client.head("/api/docs/README.md").status_code == 405


class TestDocsCors:
    """B4 — CORSMiddleware allow_methods includes GET."""

    def test_cors_preflight_response_includes_get_in_allowed_methods(self):
        """OPTIONS preflight for /api/docs/README.md returns GET in Access-Control-Allow-Methods. (B4, T1.8)"""
        client = TestClient(app)
        response = client.options(
            "/api/docs/README.md",
            headers={
                "Origin": "http://localhost:8000",
                "Access-Control-Request-Method": "GET",
            },
        )
        assert "GET" in response.headers.get("Access-Control-Allow-Methods", "")
