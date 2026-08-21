

from typing import Any
from pydantic import BaseModel

from app.schemas.retrieval_model import Citation


class ToolResult(BaseModel):
    tool: str
    success: bool
    output: dict | list
    citations: list[Citation] = []
    metadata: dict = {}
    error: str | None = None