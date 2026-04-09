"""Integration tests for server/app.py — end-to-end generate flow.

Covers:
- Full generate flow: POST /api/init → POST /api/generate returns zip (B12)
- Content-Disposition header names zip correctly (B13)
- Zip contains generated files (B14)

All tests require framework templates on disk and use the real generator.
Marked @pytest.mark.integration — run with: npm run test:python:integration
"""

import io
import zipfile

import pytest
import yaml
from fastapi.testclient import TestClient

from server.app import create_app
from tests.helpers.config_factory import create_valid_config


@pytest.mark.integration
class TestGenerateEndToEnd:
    """End-to-end generate flow using real filesystem and generator."""

    def test_full_generate_flow_returns_zip_from_real_config(self):
        """POST /api/init → POST /api/generate returns a valid zip with Content-Type application/zip."""
        # T3.1 — B12: real generator; no mocks; tmp_path isolates output
        client = TestClient(create_app())
        init_payload = create_valid_config()

        init_response = client.post(
            "/api/init",
            json={"name": init_payload["name"], "language": "python"},
        )
        assert init_response.status_code == 200
        returned_config = init_response.json()["yml"]

        config_dict = yaml.safe_load(returned_config)

        generate_response = client.post("/api/generate", json={"config": config_dict})

        assert generate_response.status_code == 200
        assert generate_response.headers["Content-Type"] == "application/zip"
        assert len(generate_response.content) > 0
        assert zipfile.ZipFile(io.BytesIO(generate_response.content))

    def test_content_disposition_header_names_zip_using_project_name(self):
        """Content-Disposition header is attachment; filename=<name>.zip."""
        # T3.2 — B13: zip filename derived from config name field
        client = TestClient(create_app())
        config_dict = create_valid_config()
        config_dict["name"] = "my-project"

        generate_response = client.post("/api/generate", json={"config": config_dict})

        assert generate_response.status_code == 200
        content_disposition = generate_response.headers.get("Content-Disposition", "")
        assert content_disposition == "attachment; filename=my-project.zip"

    def test_zip_contains_generated_files(self):
        """The zip body returned by POST /api/generate contains at least one generated file."""
        # T3.3 — B14: real generation; zip namelist is non-empty
        client = TestClient(create_app())
        config_dict = create_valid_config()

        generate_response = client.post("/api/generate", json={"config": config_dict})

        assert generate_response.status_code == 200
        with zipfile.ZipFile(io.BytesIO(generate_response.content)) as zf:
            assert len(zf.namelist()) > 0
