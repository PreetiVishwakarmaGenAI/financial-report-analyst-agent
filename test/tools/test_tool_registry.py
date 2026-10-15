from unittest.mock import MagicMock

from app.tools.tool_registry import ToolRegistry
from app.tools.retrieval_tool import RetrievalTool
from app.tools.web_search_tool import WebSearchTool


def test_register_and_get_tools():

    registry = ToolRegistry()
    retrieval_tool = RetrievalTool(
        MagicMock()
    )
    web_search_tool = WebSearchTool(
        MagicMock()
    )
    registry.register(retrieval_tool)
    registry.register(web_search_tool)

    assert registry.get_tool("retrieval") is retrieval_tool
    assert registry.get_tool("web_search") is web_search_tool


def test_list_tools():

    registry = ToolRegistry()
    registry.register(
        RetrievalTool(MagicMock())
    )
    registry.register(
        WebSearchTool(MagicMock())
    )
    tools = registry.list_tools()

    assert len(tools) == 2


def test_unknown_tool_returns_none():

    registry = ToolRegistry()

    assert registry.get_tool("unknown") is None