from typing import Any
from pydantic import BaseModel


class QueryRequest(BaseModel):
    document_id: str
    query: str
    top_k: int = 5


class SearchResult(BaseModel):
    id: str
    content: str
    metadata: dict[str, Any]
    score: float


class QueryResponse(BaseModel):
    results: list[SearchResult]