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

    def _build_context(self, retrieved_chunks):
        """
        Build context from retrieved chunks.
        """
        return "\n".join([chunk.content for chunk in retrieved_chunks])

    @traceable(name="SynthesizerAgent")
    def execute(
        self,
        state: AgentState,
    ) -> AgentState:
        """
        Synthesize retrieved chunks into a final response.
        """

        try:
            logger.info("Synthesizer Agent started.")
            if not state.retrieved_chunks:
                logger.warning("No retrieved chunks found.")
    
                state.final_answer = (
                    "I couldn't find enough information "
                    "in the provided document."
                )
    
                return state

            context = self._build_context(state.retrieved_chunks)
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
                
            logger.info("Synthesizer completed.")

            return state
        except Exception as e:
            logger.exception("Synthesizer failed.'%s'", e)
            raise