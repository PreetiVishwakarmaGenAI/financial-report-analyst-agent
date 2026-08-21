from unittest.mock import MagicMock

import pytest

from app.agents.researcher_agent import ResearcherAgent
from app.graph.state import AgentState


def create_state(required_tools=None):
    """
    Helper method to create AgentState for tests.
    Update fields if your AgentState has additional mandatory attributes.
    """
    return AgentState(
        user_query="Summarize Tesla revenue",
        document_id="tesla_2024",
        top_k=5,
        retrieval_queries=[],
        required_tools=required_tools or [],
        tool_results=[],
        retrieved_chunks=[],
        citations=[],
    )

def test_execute_single_tool_success():

    # Arrange
    state = create_state(required_tools=["retrieval"])

    updated_state = state
    updated_state.retrieved_chunks = ["Chunk 1", "Chunk 2"]

    tool = MagicMock()
    tool.run.return_value = updated_state

    tool_registry = MagicMock()
    tool_registry.get_tool.return_value = tool

    researcher = ResearcherAgent(tool_registry)

    # Act
    result = researcher.execute(state)

    # Assert
    tool_registry.get_tool.assert_called_once_with("retrieval")
    tool.run.assert_called_once_with(state)

    assert result == updated_state
    assert result.retrieved_chunks == ["Chunk 1", "Chunk 2"]


def test_execute_multiple_tools_in_order():

    # Arrange
    state = create_state(
        required_tools=["retrieval", "calculator"]
    )

    retrieval_tool = MagicMock()
    calculator_tool = MagicMock()

    state_after_retrieval = create_state(
        required_tools=["retrieval", "calculator"]
    )
    state_after_retrieval.retrieved_chunks = ["Chunk"]

    final_state = create_state(
        required_tools=["retrieval", "calculator"]
    )
    final_state.retrieved_chunks = ["Chunk"]
    final_state.final_answer = {
        "revenue": 100
    }

    retrieval_tool.run.return_value = state_after_retrieval
    calculator_tool.run.return_value = final_state

    tool_registry = MagicMock()

    tool_registry.get_tool.side_effect = [
        retrieval_tool,
        calculator_tool,
    ]

    researcher = ResearcherAgent(tool_registry)

    # Act
    result = researcher.execute(state)

    # Assert
    assert tool_registry.get_tool.call_count == 2

    retrieval_tool.run.assert_called_once_with(state)

    calculator_tool.run.assert_called_once_with(
        state_after_retrieval
    )

    assert result == final_state
    assert result.final_answer["revenue"] == 100


def test_unknown_tool_raises_error():

    state = create_state(
        required_tools=["unknown_tool"]
    )

    tool_registry = MagicMock()
    tool_registry.get_tool.return_value = None

    researcher = ResearcherAgent(tool_registry)

    with pytest.raises(ValueError) as exc:

        researcher.execute(state)

    assert "Unsupported tool" in str(exc.value)


def test_tool_exception_is_propagated():

    state = create_state(
        required_tools=["retrieval"]
    )

    tool = MagicMock()
    tool.run.side_effect = RuntimeError(
        "Retrieval failed"
    )

    tool_registry = MagicMock()
    tool_registry.get_tool.return_value = tool

    researcher = ResearcherAgent(tool_registry)

    with pytest.raises(RuntimeError):

        researcher.execute(state)


def test_execute_with_no_required_tools():

    state = create_state(required_tools=[])
    tool_registry = MagicMock()
    researcher = ResearcherAgent(tool_registry)
    result = researcher.execute(state)
    tool_registry.get_tool.assert_not_called()

    assert result == state