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
    web_results: Optional[List[dict]] = Field(default_factory=list)

    required_tools: List[str] = Field(default_factory=list)
    executed_tools: Optional[List[str]] = Field(default_factory=list)
    tool_results: Optional[List[str]] = Field(default_factory=list)

    retrieved_chunks: List[RetrievedChunk] = Field(default_factory=list)
    citations: list[Citation] = Field(default_factory=list)

    final_answer: Optional[str] = None

    # Reflection
    reflection_passed: Optional[bool] = None
    reflection_feedback: Optional[str] = None
    reflection_issues: Optional[List[str]] = None
    #TODO: Consider `reflection_retry_queries` instead of `reflection_feedback` for better clarity and separation of concerns.
    #reflection_retry_queries: list[str] = []

    # Control
    retry_count: int = 0
    max_retries: int = 2
    error: Optional[str] = None