import logging

from langsmith import traceable

from app.enums.agent_role import AgentRole
from app.graph.state import AgentState
from app.schemas.planner_models import PlannerOutput
from app.prompts.planner_prompt import PLANNER_SYSTEM_PROMPT
from app.services.llm_service import LLMService
from app.tools.tool_registry import ToolRegistry

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

    def __init__(self, llm_service: LLMService, tool_registry: ToolRegistry = None):
        self.llm_service = llm_service
        self.tool_registry = tool_registry

    @traceable(name="PlannerAgent")
    def execute(self, state: AgentState) -> AgentState:
        """
        Execute the planning step.
        """

        logger.info("Planner Agent started.")
        available_tools = (
            self.tool_registry.get_tools_description()
        )
        system_prompt = PLANNER_SYSTEM_PROMPT.format(
            available_tools=available_tools
        )

        try:
            planner_output: PlannerOutput = (
                self.llm_service.generate_structured_response(
                    role=AgentRole.PLANNER,
                    system_prompt=system_prompt,
                    user_prompt=state.user_query,
                    response_model=PlannerOutput,
                )
            )

            state.task_type = planner_output.task_type
            state.retrieval_queries = planner_output.retrieval_queries
            state.required_tools = planner_output.required_tools

            logger.debug(
                "Generated retrieval queries: %s",
                state.retrieval_queries,
            )
            logger.info(
                "Planner completed. Task=%s RetrievalQueries=%s RequiredTools=%s",
                state.task_type,
                state.retrieval_queries,
                state.required_tools,
            )

            return state

        except Exception:
            logger.exception("Planner Agent failed.")
            raise