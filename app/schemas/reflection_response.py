

from typing import Any
from pydantic import BaseModel

from app.schemas.retrieval_model import Citation


class ReflectionResponse(BaseModel):
    passed: bool
    issues: list[str]
    feedback: str