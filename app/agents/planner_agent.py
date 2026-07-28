import logging

from app.enums.agent_role import AgentRole
from app.graph.state import AgentState
from app.schemas.planner_models import PlannerOutput
from app.prompts.planner_prompt import PLANNER_SYSTEM_PROMPT
from app.services.llm_service import LLMService

logger = logging.getLogger(__name__)


class PlannerAgent:
    """
    Planner Agent responsible for creating an execution plan.

    Responsibilities
    ----------------
    - Understand user intent
    - Classify task
    - Generate retrieval-friendly sub-questions
    """

    def __init__(self, llm_service: LLMService):
        self.llm_service = llm_service

    def execute(self, state: AgentState) -> AgentState:
        """
        Execute the planning step.
        """

        logger.info("Planner Agent started.")

        try:
            planner_output: PlannerOutput = (
                self.llm_service.generate_structured_response(
                    role=AgentRole.PLANNER,
                    system_prompt=PLANNER_SYSTEM_PROMPT,
                    user_prompt=state.user_query,
                    response_model=PlannerOutput,
                )
            )

            state.task_type = planner_output.task_type
            state.retrieval_queries = planner_output.retrieval_queries

            logger.debug(
                "Generated retrieval queries: %s",
                state.retrieval_queries,
            )
            logger.info(
                "Planner completed. Task=%s RetrievalQueries=%s",
                state.task_type,
                state.retrieval_queries,
            )

            return state

        except Exception:
            logger.exception("Planner Agent failed.")
            raise