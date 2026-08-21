from unittest.mock import MagicMock

from app.graph.state import AgentState
from app.tools.web_search_tool import WebSearchTool


def create_state(required_tools=None):
    """
    Helper method to create AgentState for tests.
    Update fields if your AgentState has additional mandatory attributes.
    """
    return AgentState(
        user_query="Tesla earnings",
        document_id="",
        top_k=0,
        retrieval_queries=[],
        required_tools=required_tools or [],
        tool_results=[],
        retrieved_chunks=[],
        citations=[],
    )

def test_run_success():
    state  = create_state(required_tools=["web_search"])
    mock_service = MagicMock()
    mock_service.search.return_value = [
        {
            "title": "Tesla Earnings",
            "url": "https://example.com",
            "content": "Revenue increased",
            "score": 0.98,
        }
    ]

    tool = WebSearchTool(mock_service)
    result = tool.run(state)
    mock_service.search.assert_called_once_with(
        "Tesla earnings"
    )

    assert result.success is True
    assert result.tool == "web_search"

    assert len(result.output) == 1

    assert result.output[0]["title"] == "Tesla Earnings"


def test_execute_empty_results():

    mock_service = MagicMock()
    mock_service.search.return_value = []
    tool = WebSearchTool(mock_service)

    state = create_state(required_tools=["web_search"])
    result = tool.run(state)

    assert result.success is True
    assert result.output == []