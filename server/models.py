"""Server request models for the midtempo framework configuration form."""

from typing import Any

from pydantic import BaseModel, Field


class InitRequest(BaseModel):
    """Request model for POST /api/init."""

    name: str = Field(..., pattern=r"^[a-zA-Z0-9][a-zA-Z0-9._-]*$", max_length=100)
    language: str = Field(..., max_length=50)


class GenerateRequest(BaseModel):
    """Request model for POST /api/generate."""

    config: dict[str, Any]
