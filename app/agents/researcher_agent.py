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
        self.tool_registry = tool_registry

    @traceable(name="ResearcherAgent")
    def execute(
        self,
        state: AgentState,
    ) -> AgentState:
        """
        Retrieve relevant chunks for all retrieval_queries.
        """

        logger.info("Researcher Agent started.")
        for tool_name in state.required_tools:
            tool = self.tool_registry.get_tool(tool_name)
            if tool is None:
                logger.error("Unknown tool requested: %s", tool_name)
                raise ValueError(f"Unsupported tool: {tool_name}")
            try:
                state = tool.run(state)
            except Exception as e:
                logger.error("Error occurred while running tool %s: %s", tool_name, str(e))
                raise
        return state