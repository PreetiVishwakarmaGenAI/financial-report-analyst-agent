from pydantic import BaseModel, Field
from typing import List, Optional

from app.schemas.retrieval_model import RetrievedChunk, Citation
from app.enums.task_type import TaskType


class AgentState(BaseModel):
    user_query: str
    document_id: Optional[str]
    top_k: int = Field(description="Number of top chunks to retrieve for each query.")

    task_type: Optional[TaskType] = None
    retrieval_queries: List[str] = Field(default_factory=list)
    web_results: Optional[List[dict]] = Field(default_factory=list)

    required_tools: List[str] = Field(default_factory=list)
    executed_tools: Optional[List[str]] = Field(default_factory=list)
    tool_results: Optional[List[str]] = Field(default_factory=list)

    retrieved_chunks: List[RetrievedChunk] = Field(default_factory=list)
    citations: list[Citation] = Field(default_factory=list)

    final_answer: Optional[str] = None

    # Tool-specific recovery queries
    additional_tools: list[str] = Field(default_factory=list)
    additional_retrieval_queries: list[str] = Field(
        default_factory=list
    )
    additional_web_queries: list[str] = Field(
        default_factory=list
    )

    # Reflection
    reflection_status: str | None = None
    reflection_reason: str | None = None
    missing_information: list[str] = Field(
        default_factory=list
    )

    # Control
    retry_count: int = 0
    max_retries: int = 2
    error: Optional[str] = None