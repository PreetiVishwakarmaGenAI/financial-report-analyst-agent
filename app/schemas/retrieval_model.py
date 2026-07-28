from typing import Any
from pydantic import BaseModel, Field

class Citation(BaseModel):
    chunk_id: str
    page_number: int
    source: str

class RetrievedChunk(BaseModel):
    chunk_id: str
    content: str
    page_number: int
    similarity_score: float
    metadata: dict[str, Any] = Field(default_factory=dict)