from pydantic import BaseModel, Field
from typing import List, Optional

from app.schemas.retrieval_model import RetrievedChunk, Citation
from app.enums.task_type import TaskType


class AgentState(BaseModel):
    user_query: str
    document_id: str
    top_k: int = Field(description="Number of top chunks to retrieve for each query.")

    task_type: Optional[TaskType] = None
    retrieval_queries: List[str] = Field(default_factory=list)

    retrieved_chunks: List[RetrievedChunk] = Field(default_factory=list)
    citations: list[Citation] = Field(default_factory=list)

    final_answer: Optional[str] = None
    error: Optional[str] = None