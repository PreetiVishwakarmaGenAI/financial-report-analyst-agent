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
    def execute(self, state: AgentState) -> AgentState:
        logger.info("Reflection Agent started.")

        response: ReflectionResponse = (
            self.llm_service.generate_structured_response(
                role=AgentRole.REFLECTION,
                user_prompt=REFLECTION_PROMPT.format(
                    user_query=state.user_query,
                    final_answer=state.final_answer or "",
                    retrieved_context=state.retrieved_chunks,
                    citations=state.citations,
                ),
                response_model=ReflectionResponse,
                system_prompt=REFLECTION_SYSTEM_PROMPT,
            )
        )

        # response = self.normalize_reflection(response)

        state.reflection_status = response.recommended_action
        state.reflection_reason = response.feedback
        state.missing_information = response.missing_information

        # Reset instructions from any previous reflection pass.
        state.additional_tools = []
        state.additional_web_queries = []
        state.additional_retrieval_queries = []

        if response.recommended_action == "WEB_SEARCH":
            if response.search_query and response.search_query.strip():
                state.additional_tools = ["web_search"]
                state.additional_web_queries = [
                    response.search_query.strip()
                ]
            else:
                logger.warning(
                    "WEB_SEARCH requested without a valid search query."
                )

        elif response.recommended_action == "RETRIEVE_MORE":
            queries = [
                query.strip()
                for query in response.missing_information
                if query.strip()
            ]

            if not queries:
                queries = state.retrieval_queries

            if queries:
                state.additional_tools = ["retrieval"]
                state.additional_retrieval_queries = queries
            else:
                logger.warning(
                    "RETRIEVE_MORE requested without retrieval queries."
                )
        logger.info(
            "Reflection completed. action=%s retry_count=%s "
            "missing_information=%s additional_tools=%s",
            state.reflection_status,
            state.retry_count,
            state.missing_information,
            state.additional_tools,
        )
        # state.retry_count = state.retry_count + 1

        return state

    def route_after_reflection(self, state: AgentState) -> str:
        reflection = state.reflection_status

        if reflection == "PASS":
            return "end"

        if state.retry_count >= state.max_retries:
            return "end"


        if reflection == "WEB_SEARCH":
            if (
                "web_search" in state.additional_tools
                and state.additional_web_queries
            ):
                return "researcher"

            logger.warning(
                "Reflection requested WEB_SEARCH without a valid search query."
            )
            return "end"

        if reflection == "RETRIEVE_MORE":
            if (
                "retrieval" in state.additional_tools
                and state.additional_retrieval_queries
            ):
                return "researcher"

            logger.warning(
                "Reflection requested RETRIEVE_MORE without valid retrieval queries."
            )
            return "end"

        if reflection == "RESYNTHESIZE":
            return "synthesizer"

        logger.warning(
            "Unknown reflection action: %s",
            reflection,
        )
        return "end"


    # def normalize_reflection(self, response):
    #     if (
    #         response.missing_information
    #         and response.recommended_action == "RESYNTHESIZE"
    #         and response.search_query
    #     ):
    #         response.recommended_action = "WEB_SEARCH"
    #         response.additional_tools = list(
    #             set(response.additional_tools) | {"web_search"}
    #         )

    #     return response