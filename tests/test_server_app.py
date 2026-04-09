"""Tests for server/app.py — FastAPI application.

Covers:
- POST /api/init success and error paths (B6–B11)
- Security headers middleware (B12, B13)
- Static file serving (B14, B15)
- POST /api/generate success, error paths, cleanup, CORS, and method restriction (Stage 3)
"""

import io
import zipfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from server.app import app, create_app


def fake_generate(config_path, output_dir):
    """Write one file under agents/my-project/ — mirrors real generator output structure."""
    agents_dir = output_dir / "agents" / "my-project"
    agents_dir.mkdir(parents=True, exist_ok=True)
    (agents_dir / "file.md").write_text("content")


@pytest.fixture
def temp_dir_mocks(tmp_path: Path):
    """Return two MagicMock TemporaryDirectory instances backed by real tmp subdirs."""
    (tmp_path / "config").mkdir()
    (tmp_path / "output").mkdir()
    mock_config = MagicMock()
    mock_output = MagicMock()
    mock_config.name = str(tmp_path / "config")
    mock_output.name = str(tmp_path / "output")
    return mock_config, mock_output


class TestInitEndpointSuccess:
    """Test POST /api/init success response."""

    def test_post_init_returns_yml_string_on_valid_request(self):
        """POST /api/init returns {"yml": string} HTTP 200 on valid request."""
        # T2.1 — B6 happy path
        with (
            patch("server.app._discover_languages", return_value=["python", "typescript"]),
            patch(
                "server.app.render_config_string",
                return_value="name: my-project\nlanguage: python\n",
            ),
        ):
            client = TestClient(app)
            response = client.post("/api/init", json={"name": "my-project", "language": "python"})

        assert response.status_code == 200
        assert response.json() == {"yml": "name: my-project\nlanguage: python\n"}


class TestInitEndpointValidationErrors:
    """Test POST /api/init validation error responses."""

    def test_post_init_returns_422_when_name_fails_pattern(self):
        """POST /api/init returns {"error": string} HTTP 422 when name fails regex pattern."""
        # T2.2 — B7, CG-IV1: custom RequestValidationError handler returns {"error": string}
        client = TestClient(app)
        response = client.post("/api/init", json={"name": "-bad", "language": "python"})

        assert response.status_code == 422
        body = response.json()
        assert "error" in body
        assert isinstance(body["error"], str)
        assert "detail" not in body

    def test_post_init_returns_422_when_name_exceeds_max_length(self):
        """POST /api/init returns {"error": string} HTTP 422 when name exceeds 100 characters."""
        # T2.3 — B7, CG-IV2
        client = TestClient(app)
        response = client.post("/api/init", json={"name": "a" * 101, "language": "python"})

        assert response.status_code == 422
        body = response.json()
        assert "error" in body
        assert isinstance(body["error"], str)


class TestInitEndpointLanguageCheck:
    """Test POST /api/init language allowlist enforcement."""

    def test_post_init_returns_400_when_language_not_in_discovered_list(self):
        """POST /api/init returns {"error": string} HTTP 400 when language not in discovered list."""
        # T2.4 — B8, CG-IV1: language allowlist checked before render_config_string is called
        with (
            patch("server.app._discover_languages", return_value=["python", "typescript"]),
            patch("server.app.render_config_string") as mock_render,
        ):
            client = TestClient(app)
            response = client.post("/api/init", json={"name": "my-project", "language": "cobol"})

        assert response.status_code == 400
        body = response.json()
        assert "error" in body
        assert "cobol" in body["error"]
        assert "not supported" in body["error"]
        mock_render.assert_not_called()


class TestInitEndpointErrorPaths:
    """Test POST /api/init error handling."""

    def test_post_init_returns_400_when_render_raises_value_error(self):
        """POST /api/init returns {"error": str(e)} HTTP 400 when render_config_string raises ValueError."""
        # T2.5 — B9
        with (
            patch("server.app._discover_languages", return_value=["python"]),
            patch(
                "server.app.render_config_string",
                side_effect=ValueError("template missing"),
            ),
        ):
            client = TestClient(app)
            response = client.post("/api/init", json={"name": "my-project", "language": "python"})

        assert response.status_code == 400
        assert response.json() == {"error": "template missing"}

    def test_post_init_returns_500_on_unhandled_exception(self):
        """POST /api/init returns {"error": "An unexpected error occurred"} HTTP 500 on unhandled exception."""
        # T2.6 — B10, CG-PH4: no stack trace or internal detail in 500 response
        with (
            patch("server.app._discover_languages", return_value=["python"]),
            patch(
                "server.app.render_config_string",
                side_effect=RuntimeError("internal state broken"),
            ),
        ):
            client = TestClient(app, raise_server_exceptions=False)
            response = client.post("/api/init", json={"name": "my-project", "language": "python"})

        assert response.status_code == 500
        body = response.json()
        assert body == {"error": "An unexpected error occurred"}
        assert "internal state broken" not in str(body)


class TestInitEndpointMethodRestriction:
    """Test POST /api/init HTTP method restriction."""

    def test_get_api_init_returns_405(self):
        """GET /api/init returns HTTP 405 — route restricted to POST only."""
        # T2.7 — B11, CG-PH3
        client = TestClient(app)
        response = client.get("/api/init")

        assert response.status_code == 405


class TestSecurityHeadersMiddleware:
    """Test security headers middleware on all responses."""

    def test_all_responses_carry_required_security_headers(self):
        """Security headers middleware sets all three required headers on a 200 response."""
        # T2.8 — B12, CG-PH1
        with (
            patch("server.app._discover_languages", return_value=["python"]),
            patch("server.app.render_config_string", return_value="yml: content"),
        ):
            client = TestClient(app)
            response = client.post("/api/init", json={"name": "my-project", "language": "python"})

        assert response.headers.get("X-Content-Type-Options") == "nosniff"
        assert response.headers.get("X-Frame-Options") == "DENY"
        assert response.headers.get("Referrer-Policy") == "strict-origin-when-cross-origin"

    def test_security_headers_present_on_error_responses(self):
        """Security headers are present on a 422 error response."""
        # T2.9 — B12, CG-PH1: middleware applies to all responses including 4xx
        client = TestClient(app)
        response = client.post("/api/init", json={"name": "-bad", "language": "python"})

        assert response.headers.get("X-Content-Type-Options") == "nosniff"
        assert response.headers.get("X-Frame-Options") == "DENY"
        assert response.headers.get("Referrer-Policy") == "strict-origin-when-cross-origin"

    def test_server_header_absent_from_responses(self):
        """Middleware removes the Server header from all responses."""
        # T2.10 — B13, CG-PH4
        with (
            patch("server.app._discover_languages", return_value=["python"]),
            patch("server.app.render_config_string", return_value="yml: content"),
        ):
            client = TestClient(app)
            response = client.post("/api/init", json={"name": "my-project", "language": "python"})

        assert "Server" not in response.headers


class TestStaticFileServing:
    """Test static file serving from ui/ directory."""

    def test_static_file_in_ui_directory_served_at_its_path(self, tmp_path: Path):
        """A file in ui/ is returned by GET /<filename>."""
        # T2.11 — B14: uses tmp_path isolated ui/ directory
        ui_dir = tmp_path / "ui"
        (ui_dir / "json").mkdir(parents=True)
        (ui_dir / "json" / "languages.json").write_text('{"python": {}}')

        client = TestClient(create_app(ui_dir=ui_dir))
        response = client.get("/json/languages.json")

        assert response.status_code == 200
        assert response.json() == {"python": {}}

    def test_get_root_returns_404_when_index_html_absent(self, tmp_path: Path):
        """GET / returns 404 when ui/index.html is not present."""
        # T2.12 — B15: empty ui/ dir, no index.html
        ui_dir = tmp_path / "ui"
        ui_dir.mkdir()

        client = TestClient(create_app(ui_dir=ui_dir))
        response = client.get("/")

        assert response.status_code == 404

    def test_symlinked_file_in_ui_directory_served(self, tmp_path: Path):
        """A symlink in ui/ that points to a file outside ui/ is served at its path.
        StaticFiles must use follow_symlink=True — otherwise schema.json (symlink to
        ../schema/config.schema.json) returns 404 on page load. (BUG-2)"""
        ui_dir = tmp_path / "ui"
        (ui_dir / "json").mkdir(parents=True)
        target = tmp_path / "schema.json"
        target.write_text('{"type": "object"}')
        (ui_dir / "json" / "schema.json").symlink_to(target)

        client = TestClient(create_app(ui_dir=ui_dir))
        response = client.get("/json/schema.json")

        assert response.status_code == 200
        assert response.json() == {"type": "object"}


class TestGenerateEndpointSuccess:
    """Test POST /api/generate success response."""

    def test_post_generate_returns_zip_for_valid_config(self, temp_dir_mocks):
        """POST /api/generate returns 200 with Content-Type application/zip and valid zip body."""
        # T2.1 — B3: happy path; validate_config returns None, generator writes a file
        mock_config_dir, mock_output_dir = temp_dir_mocks

        with (
            patch("server.app.validate_config_with_enhanced_errors", return_value=None),
            patch("server.app.generate_documentation_with_timing", side_effect=fake_generate),
            patch("tempfile.TemporaryDirectory", side_effect=[mock_config_dir, mock_output_dir]),
        ):
            client = TestClient(create_app())
            response = client.post("/api/generate", json={"config": {"name": "my-project"}})

        assert response.status_code == 200
        assert response.headers["Content-Type"] == "application/zip"
        assert len(response.content) > 0
        assert zipfile.ZipFile(io.BytesIO(response.content))

    def test_post_generate_zip_contains_single_root_folder(self, temp_dir_mocks):
        """POST /api/generate zip contains all files under a single midtempo-framework/ root."""
        mock_config_dir, mock_output_dir = temp_dir_mocks

        with (
            patch("server.app.validate_config_with_enhanced_errors", return_value=None),
            patch("server.app.generate_documentation_with_timing", side_effect=fake_generate),
            patch("tempfile.TemporaryDirectory", side_effect=[mock_config_dir, mock_output_dir]),
        ):
            client = TestClient(create_app())
            response = client.post("/api/generate", json={"config": {"name": "my-project"}})

        zf = zipfile.ZipFile(io.BytesIO(response.content))
        names = zf.namelist()
        assert all(n.startswith("midtempo-framework/") for n in names)

    def test_post_generate_zip_filename_uses_repo_name_only(self, temp_dir_mocks):
        """POST /api/generate Content-Disposition filename is {name}.zip with no suffix."""
        mock_config_dir, mock_output_dir = temp_dir_mocks

        with (
            patch("server.app.validate_config_with_enhanced_errors", return_value=None),
            patch("server.app.generate_documentation_with_timing", side_effect=fake_generate),
            patch("tempfile.TemporaryDirectory", side_effect=[mock_config_dir, mock_output_dir]),
        ):
            client = TestClient(create_app())
            response = client.post("/api/generate", json={"config": {"name": "my-project"}})

        assert response.headers["Content-Disposition"] == "attachment; filename=my-project.zip"

    def test_post_generate_zip_files_are_directly_under_root_folder(self, temp_dir_mocks):
        """POST /api/generate zip places files at midtempo-framework/{file}, not midtempo-framework/agents/{name}/{file}."""
        mock_config_dir, mock_output_dir = temp_dir_mocks

        with (
            patch("server.app.validate_config_with_enhanced_errors", return_value=None),
            patch("server.app.generate_documentation_with_timing", side_effect=fake_generate),
            patch("tempfile.TemporaryDirectory", side_effect=[mock_config_dir, mock_output_dir]),
        ):
            client = TestClient(create_app())
            response = client.post("/api/generate", json={"config": {"name": "my-project"}})

        zf = zipfile.ZipFile(io.BytesIO(response.content))
        assert "midtempo-framework/file.md" in zf.namelist()


class TestGenerateEndpointValidationErrors:
    """Test POST /api/generate validation error responses."""

    def test_post_generate_returns_422_when_config_fails_schema_validation(self):
        """POST /api/generate returns {"error": string} HTTP 422 when config fails validate_config."""
        # T2.2 — B4: validate_config raises ValueError; generator not invoked
        with (
            patch(
                "server.app.validate_config_with_enhanced_errors",
                side_effect=ValueError("Missing required field: name"),
            ),
            patch("server.app.generate_documentation_with_timing") as mock_gen,
        ):
            client = TestClient(create_app())
            response = client.post("/api/generate", json={"config": {"invalid": True}})

        assert response.status_code == 422
        assert response.json() == {"error": "Missing required field: name"}
        mock_gen.assert_not_called()

    def test_post_generate_returns_422_when_config_field_missing(self):
        """POST /api/generate returns {"error": string} HTTP 422 when config key absent."""
        # T2.3 — B5: Pydantic rejects at parse stage; existing handler returns {"error": string}
        client = TestClient(create_app())
        response = client.post("/api/generate", json={})

        assert response.status_code == 422
        body = response.json()
        assert "error" in body
        assert isinstance(body["error"], str)
        assert "detail" not in body

    def test_post_generate_returns_422_when_config_value_is_not_a_dict(self):
        """POST /api/generate returns {"error": string} HTTP 422 when config is a string."""
        # T2.4 — B5: Pydantic rejects wrong type at parse stage
        client = TestClient(create_app())
        response = client.post("/api/generate", json={"config": "not-a-dict"})

        assert response.status_code == 422
        body = response.json()
        assert "error" in body
        assert isinstance(body["error"], str)


class TestGenerateEndpointErrorPaths:
    """Test POST /api/generate generator failure handling."""

    def test_post_generate_returns_500_when_generator_raises(self, temp_dir_mocks):
        """POST /api/generate returns {"error": "An unexpected error occurred"} HTTP 500 on generator failure."""
        # T2.5 — B6: generator raises; response contains no internal detail (CG-PH4)
        mock_config_dir, mock_output_dir = temp_dir_mocks

        with (
            patch("server.app.validate_config_with_enhanced_errors", return_value=None),
            patch(
                "server.app.generate_documentation_with_timing",
                side_effect=RuntimeError("generator blew up"),
            ),
            patch("tempfile.TemporaryDirectory", side_effect=[mock_config_dir, mock_output_dir]),
        ):
            client = TestClient(create_app(), raise_server_exceptions=False)
            response = client.post("/api/generate", json={"config": {"name": "my-project"}})

        assert response.status_code == 500
        body = response.json()
        assert body == {"error": "An unexpected error occurred"}
        assert "generator blew up" not in str(body)


class TestGenerateEndpointCleanup:
    """Test POST /api/generate temp dir cleanup in finally block."""

    def test_both_temp_dirs_cleaned_up_on_success(self, temp_dir_mocks):
        """Both TemporaryDirectory instances receive .cleanup() call on successful generation."""
        # T2.6 — B7: Decision 2 constraint: cleanup in finally regardless of outcome
        mock_config_dir, mock_output_dir = temp_dir_mocks

        with (
            patch("server.app.validate_config_with_enhanced_errors", return_value=None),
            patch("server.app.generate_documentation_with_timing", side_effect=fake_generate),
            patch("tempfile.TemporaryDirectory", side_effect=[mock_config_dir, mock_output_dir]),
        ):
            client = TestClient(create_app())
            response = client.post("/api/generate", json={"config": {"name": "my-project"}})

        assert response.status_code == 200
        mock_config_dir.cleanup.assert_called_once()
        mock_output_dir.cleanup.assert_called_once()

    def test_both_temp_dirs_cleaned_up_on_generator_failure(self, temp_dir_mocks):
        """Both TemporaryDirectory instances receive .cleanup() call when generator raises."""
        # T2.7 — B8: Decision 2 constraint: cleanup in finally despite exception path
        mock_config_dir, mock_output_dir = temp_dir_mocks

        with (
            patch("server.app.validate_config_with_enhanced_errors", return_value=None),
            patch(
                "server.app.generate_documentation_with_timing",
                side_effect=RuntimeError("fail"),
            ),
            patch("tempfile.TemporaryDirectory", side_effect=[mock_config_dir, mock_output_dir]),
        ):
            client = TestClient(create_app(), raise_server_exceptions=False)
            response = client.post("/api/generate", json={"config": {"name": "my-project"}})

        assert response.status_code == 500
        mock_config_dir.cleanup.assert_called_once()
        mock_output_dir.cleanup.assert_called_once()


class TestGenerateEndpointMethodRestriction:
    """Test POST /api/generate HTTP method restriction."""

    def test_get_api_generate_returns_405_with_allow_post_header(self):
        """GET /api/generate returns HTTP 405 with Allow: POST header."""
        # T2.8 — B9: CG-PH3; explicit 405 api_route guards against StaticFiles 404 interception
        client = TestClient(create_app())
        response = client.get("/api/generate")

        assert response.status_code == 405
        assert response.headers.get("Allow") == "POST"


class TestGenerateCors:
    """Test CORS headers on POST /api/generate responses."""

    def test_cors_header_set_for_allowed_origin(self, temp_dir_mocks):
        """Access-Control-Allow-Origin is set to the allowed origin when Origin header matches."""
        # T2.9 — B10: CG-PH2, CG-PH5; explicit allowlist, not wildcard
        mock_config_dir, mock_output_dir = temp_dir_mocks

        with (
            patch("server.app.validate_config_with_enhanced_errors", return_value=None),
            patch("server.app.generate_documentation_with_timing", side_effect=fake_generate),
            patch("tempfile.TemporaryDirectory", side_effect=[mock_config_dir, mock_output_dir]),
        ):
            client = TestClient(create_app())
            response = client.post(
                "/api/generate",
                json={"config": {"name": "my-project"}},
                headers={"Origin": "http://localhost:8000"},
            )

        assert response.status_code == 200
        assert response.headers.get("Access-Control-Allow-Origin") == "http://localhost:8000"

    def test_cors_wildcard_absent_from_response(self, temp_dir_mocks):
        """Access-Control-Allow-Origin response header does not equal *."""
        # T2.10 — B11: CG-PH2; wildcard * must never appear in allow-origin header
        mock_config_dir, mock_output_dir = temp_dir_mocks

        with (
            patch("server.app.validate_config_with_enhanced_errors", return_value=None),
            patch("server.app.generate_documentation_with_timing", side_effect=fake_generate),
            patch("tempfile.TemporaryDirectory", side_effect=[mock_config_dir, mock_output_dir]),
        ):
            client = TestClient(create_app())
            response = client.post(
                "/api/generate",
                json={"config": {"name": "my-project"}},
                headers={"Origin": "http://localhost:8000"},
            )

        assert response.headers.get("Access-Control-Allow-Origin") != "*"
