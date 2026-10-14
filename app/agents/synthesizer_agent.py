import logging

from langsmith import traceable

from app.graph import state
from app.graph.state import AgentState
from app.enums.agent_role import AgentRole
from app.prompts.synthesizer_prompt import SYNTHESIZER_SYSTEM_PROMPT
from app.services.llm_service import LLMService

logger = logging.getLogger(__name__)

class SynthesizerAgent:
    """
    Synthesizer Agent responsible for synthesizing
    retrieved evidence into a coherent response.
    """

    def __init__(
        self,
        llm_service: LLMService,
    ):
        self.llm_service = llm_service

    def _build_context(self, state: AgentState) -> str:
        """
        Build context from retrieved chunks.
        """
        context_parts = []
        logger.info("----------------------------------------------------.")
        logger.info(state.web_results)

        for chunk in state.retrieved_chunks:
            context_parts.append(chunk.content)

        for result in state.web_results:
            context_parts.append(result["content"])

        context = "\n\n".join(context_parts)
        return context

    def validate_state(self, state: AgentState) -> bool:
        """
        Validate the state before synthesis.
        """
        if "retrieval" in state.executed_tools and not state.retrieved_chunks:
            logger.warning("No retrieved chunks found.")

            state.final_answer = (
                "I couldn't find enough information "
                "in the provided document."
            )
            return False
        if "web_search" in state.executed_tools and not state.web_results:
            logger.warning("No web search results found.")

            state.final_answer = (
                "I couldn't find enough information "
            )
            return False
        return True

    @traceable(name="SynthesizerAgent")
    def execute(
        self,
        state: AgentState,
    ) -> AgentState:
        """
        Synthesize retrieved chunks into a final response.
        """

        try:
            if state.retry_count >= state.max_retries:
                logger.warning(
                    "Maximum retries reached. "
                    "Returning the best available answer."
                )
                return state
            logger.info("Synthesizer Agent started.")
            if not self.validate_state(state):
                logger.info("Synthesizer Agent validation failed.")
                return state
            context = self._build_context(state)
            prompt = f"""
            ## Context

            {context}

            ## Question

            {state.user_query}
            """

            final_answer = self.llm_service.generate_response(
                role=AgentRole.SYNTHESIZER,
                user_prompt=prompt,
                system_prompt=SYNTHESIZER_SYSTEM_PROMPT,
            )

            state.final_answer = final_answer
                
            if state.reflection_status == "RESYNTHESIZE":
                logger.info(
                    "Synthesizer completed after reflection. "
                    "retry_count=%s",
                    state.retry_count,
                )
                state.retry_count = state.retry_count + 1
            else:
                logger.info("Synthesizer completed.")

            return state
        except Exception as e:
            logger.exception("Synthesizer failed.'%s'", e)
            raise