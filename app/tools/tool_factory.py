from app.tools.tool_registry import ToolRegistry
from app.tools.retrieval_tool import RetrievalTool
from app.tools.web_search_tool import WebSearchTool
from app.services.web_search_service import WebSearchService


def create_tool_registry(
    retrieval_service,
) -> ToolRegistry:
    """
    Register every tool available in the application.
    """

    registry = ToolRegistry()
    web_search_service = WebSearchService()

    registry.register(
        RetrievalTool(retrieval_service)
    )
    registry.register(
        WebSearchTool(web_search_service)
    )

    # Future tools

   

    # registry.register(
    #     CalculatorTool(...)
    # )

    return registry