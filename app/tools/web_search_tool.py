from app.graph.state import AgentState
from app.schemas.tool import ToolResult
from app.tools.base_tool import BaseTool


class WebSearchTool(BaseTool):

    @property
    def name(self):
        return "web_search"

    @property
    def description(self):
        return (
            "Search the internet for recent or external "
            "financial information."
        )

    @property
    def parameters(self):
        return {
            "query": {
                "type": "string",
                "description": "Search query"
            }
        }

    def __init__(self, web_search_service):
        self.web_search_service = web_search_service

    def run(self, state) -> AgentState:
        query = state.user_query
        state.web_results = self.web_search_service.search(query, state.top_k)
        return state