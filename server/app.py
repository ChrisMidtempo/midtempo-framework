"""FastAPI application for the midtempo framework configuration form."""

import asyncio
import io
import logging
import tempfile
import zipfile
from pathlib import Path

import yaml
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import Response

from scripts.generate_docs import generate_documentation_with_timing
from scripts.init_framework import _discover_languages, render_config_string
from scripts.paths import PROJECT_ROOT
from scripts.validate_config import validate_config_with_enhanced_errors
from server.models import GenerateRequest, InitRequest

logger = logging.getLogger(__name__)

UI_DIR = PROJECT_ROOT / "ui"
CORS_ORIGINS = ["http://localhost:8000", "http://127.0.0.1:8000"]
DOCS_WHITELIST = {"README.md", "GUIDE.md", "INSTALL.md"}


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Set security headers on all responses and remove Server header."""

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        """Add security headers and remove Server header from every response."""
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        if "server" in response.headers:
            del response.headers["server"]
        return response


async def validation_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Return first Pydantic validation error as {"error": string} HTTP 422."""
    assert isinstance(exc, RequestValidationError)
    first_error = exc.errors()[0]
    return JSONResponse(status_code=422, content={"error": first_error["msg"]})


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Return generic 500 response without exposing internal detail."""
    logger.error("Unhandled exception", exc_info=exc)
    return JSONResponse(status_code=500, content={"error": "An unexpected error occurred"})


def create_app(ui_dir: Path | None = None) -> FastAPI:
    """Create and configure the FastAPI application."""
    directory = ui_dir or UI_DIR
    _app = FastAPI(docs_url=None, redoc_url=None)
    _app.add_middleware(SecurityHeadersMiddleware)
    _app.add_middleware(
        CORSMiddleware,
        allow_origins=CORS_ORIGINS,
        allow_methods=["POST", "GET"],
        allow_headers=["Content-Type"],
    )
    _app.add_exception_handler(RequestValidationError, validation_exception_handler)
    _app.add_exception_handler(Exception, generic_exception_handler)

    @_app.get("/api/docs/{filename:path}")
    async def get_doc(filename: str) -> Response:
        """Serve whitelisted documentation files as plain text."""
        if filename not in DOCS_WHITELIST:
            return JSONResponse(status_code=404, content={"error": "Not found"})
        content = (PROJECT_ROOT / "midtempo-framework" / filename).read_text(encoding="utf-8")
        return Response(content=content, media_type="text/plain")

    @_app.api_route(
        "/api/docs/{filename:path}",
        methods=["POST", "HEAD", "PUT", "PATCH", "DELETE"],
        include_in_schema=False,
    )
    async def docs_method_not_allowed(request: Request) -> JSONResponse:
        """Return 405 for non-GET methods on /api/docs/{filename}."""
        return JSONResponse(status_code=405, headers={"Allow": "GET"}, content={})

    @_app.post("/api/init")
    async def init(request: InitRequest) -> JSONResponse:
        """Handle POST /api/init — validate language, render config, return yml."""
        languages = _discover_languages()
        if request.language not in languages:
            available = ", ".join(sorted(languages))
            return JSONResponse(
                status_code=400,
                content={
                    "error": f"Language '{request.language}' not supported. Available: {available}"
                },
            )
        try:
            yml = render_config_string(request.name, request.language)
        except ValueError as e:
            return JSONResponse(status_code=400, content={"error": str(e)})
        return JSONResponse(status_code=200, content={"yml": yml})

    @_app.api_route(
        "/api/init",
        methods=["GET", "HEAD", "PUT", "PATCH", "DELETE"],
        include_in_schema=False,
    )
    async def init_method_not_allowed(request: Request) -> JSONResponse:
        """Return 405 for non-POST methods — StaticFiles mount at / would otherwise return 404."""
        return JSONResponse(status_code=405, headers={"Allow": "POST"}, content={})

    @_app.post("/api/generate")
    async def generate(request: GenerateRequest) -> Response:
        """Handle POST /api/generate — validate config, generate docs, return zip."""
        try:
            validate_config_with_enhanced_errors(request.config)
        except ValueError as e:
            return JSONResponse(status_code=422, content={"error": str(e)})
        config_name = str(request.config.get("name", "framework"))
        tmp_config_dir = tempfile.TemporaryDirectory()
        tmp_output_dir = tempfile.TemporaryDirectory()
        try:
            tmp_config_path = Path(tmp_config_dir.name) / "midtempo-framework.yml"
            with tmp_config_path.open("w") as f:
                yaml.dump(request.config, f, allow_unicode=True)
            loop = asyncio.get_running_loop()
            await loop.run_in_executor(
                None,
                generate_documentation_with_timing,
                tmp_config_path,
                Path(tmp_output_dir.name),
            )
            buffer = io.BytesIO()
            with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zf:
                root = "midtempo-framework"
                agents_prefix = Path("agents") / config_name
                for file_path in Path(tmp_output_dir.name).rglob("*"):
                    if file_path.is_file():
                        rel = file_path.relative_to(tmp_output_dir.name)
                        try:
                            rel = rel.relative_to(agents_prefix)
                        except ValueError:
                            pass
                        zf.write(file_path, f"{root}/{rel}")
                zf.write(tmp_config_path, f"{root}/.midtempo-framework.yml")
            return Response(
                content=buffer.getvalue(),
                media_type="application/zip",
                headers={
                    "Content-Disposition": f"attachment; filename={config_name}.zip"
                },
            )
        except Exception:
            logger.error("Generation failed", exc_info=True)
            return JSONResponse(
                status_code=500, content={"error": "An unexpected error occurred"}
            )
        finally:
            tmp_config_dir.cleanup()
            tmp_output_dir.cleanup()

    @_app.api_route(
        "/api/generate",
        methods=["GET", "HEAD", "PUT", "PATCH", "DELETE"],
        include_in_schema=False,
    )
    async def generate_method_not_allowed(request: Request) -> JSONResponse:
        """Return 405 for non-POST methods — StaticFiles mount at / would otherwise return 404."""
        return JSONResponse(status_code=405, headers={"Allow": "POST"}, content={})

    _app.mount("/", StaticFiles(directory=directory, html=True, follow_symlink=True), name="ui")
    return _app


app = create_app()
