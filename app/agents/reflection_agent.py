import json
import logging

from langchain_core.prompts import ChatPromptTemplate
from langsmith import traceable

from app.enums.agent_role import AgentRole
from app.graph.state import AgentState
from app.schemas.reflection_response import ReflectionResponse
from app.prompts.reflection_prompt import REFLECTION_SYSTEM_PROMPT

logger = logging.getLogger(__name__)

REFLECTION_PROMPT = """
    USER QUESTION:
    {user_query}

    SYNTHESIZED ANSWER:
    {final_answer}

    RETRIEVED EVIDENCE:
    {retrieved_context}

    CITATIONS:
    {citations} 
"""

class ReflectionAgent:

    def __init__(self, llm_service):
        self.llm_service = llm_service

    @traceable(name="ReflectionAgent")
    def execute(self, state):

        logger.info("Reflection Agent started.")

        response = self.llm_service.generate_structured_response(
            role=AgentRole.REFLECTION,                 
            user_prompt=REFLECTION_PROMPT.format(
                user_query=state.user_query,
                final_answer=state.final_answer,
                retrieved_context=state.retrieved_chunks,
                citations=state.citations,
            ),
            response_model = ReflectionResponse,
            system_prompt=REFLECTION_SYSTEM_PROMPT,
        )

        logger.info(
            "Reflection completed. passed=%s",
            response.passed,
        )

        state.reflection_passed = response.passed
        state.reflection_issues = response.issues
        state.reflection_feedback = response.feedback

        if not response.passed:
            state.retry_count += 1
            logger.info(
                "Reflection failed. retry_count=%s",
                state.retry_count,
            )

        return state

    def route_after_reflection(self, state: AgentState) -> str:

        if state.reflection_passed:
            return "finish"

        if state.retry_count >= state.max_retries:
            return "finish"

        return "retry"