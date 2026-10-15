import logging

from langsmith import traceable

from app.graph.state import AgentState
from app.tools.tool_registry import ToolRegistry
logger = logging.getLogger(__name__)


class ResearcherAgent:
    """
    Researcher Agent responsible for retrieving
    relevant evidence from the vector store.
    """

    def __init__(
        self,
        tool_registry: ToolRegistry = None,
    ):
        if tool_registry is None:
            raise ValueError("ToolRegistry is required")
        self.tool_registry = tool_registry

    @traceable(name="ResearcherAgent")
    def execute(self, state: AgentState) -> AgentState:
        logger.info(
            "Researcher Agent started. retry_count=%s",
            state.retry_count,
        )

        # Initial pass: follow the Planner.
        # Retry pass: follow the Reflection Agent.
        is_retry = bool(state.additional_tools)

        if is_retry:
            # Stop if the maximum number of retries has been reached.
            if state.retry_count >= state.max_retries:
                logger.warning("Maximum retries reached.")
                return state
            else:
                state.retry_count = state.retry_count + 1

            tools_to_run = list(state.additional_tools)
        else:
            tools_to_run = list(state.required_tools)

        if not tools_to_run:
            logger.info("No tools requested.")
            return state

        for tool_name in tools_to_run:
            tool = self.tool_registry.get_tool(tool_name)

            if tool is None:
                raise ValueError(
                    f"Unsupported tool: {tool_name}"
                )

            # Supply recovery queries to the relevant tool.
            if (
                tool_name == "retrieval"
                and state.additional_retrieval_queries
            ):
                state.retrieval_queries = list(
                    state.additional_retrieval_queries
                )

            try:
                logger.info(
                    "Executing tool=%s retry_count=%s",
                    tool_name,
                    state.retry_count,
                )

                tool.run(state)

                if tool_name not in state.executed_tools:
                    state.executed_tools.append(tool_name)

            except Exception:
                logger.exception(
                    "Error while executing tool %s",
                    tool_name,
                )
                raise

        return state