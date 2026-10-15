
from typing import Literal

from pydantic import BaseModel, Field


class ReflectionResponse(BaseModel):
    passed: bool

    correctness: int = Field(ge=0, le=100)
    groundedness: int = Field(ge=0, le=100)
    completeness: int = Field(ge=0, le=100)
    citation_quality: int = Field(ge=0, le=100)
    numerical_consistency: int = Field(ge=0, le=100)
    relevance: int = Field(ge=0, le=100)
    evidence_sufficiency: int = Field(ge=0, le=100)
    temporal_validity: int = Field(ge=0, le=100)

    issue_categories: list[
        Literal[
            "incorrect_fact",
            "unsupported_claim",
            "missing_information",
            "missing_citation",
            "incorrect_citation",
            "calculation_error",
            "unit_error",
            "period_error",
            "contradiction",
            "irrelevant_content",
            "stale_information",
        ]
    ] = Field(default_factory=list)

    issues: list[str] = Field(default_factory=list)
    missing_information: list[str] = Field(default_factory=list)

    recommended_action: Literal[
        "PASS",
        "RESYNTHESIZE",
        "RETRIEVE_MORE",
        "WEB_SEARCH",
    ]

    search_query: str | None = None
    feedback: str = ""
