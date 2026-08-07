from enum import Enum
from pydantic import BaseModel, Field

from app.enums.task_type import TaskType

class PlannerOutput(BaseModel):
    """
    Structured output returned by Planner Agent.
    """

    task_type: TaskType = Field(
        description="Classification of the user request."
    )

    retrieval_queries: list[str] = Field(
        default_factory=list,
        description="Questions for semantic retrieval."
    )

    required_tools: list[str] = Field(
        default_factory=list,
        description="List of tools required to fulfill the request."
    )