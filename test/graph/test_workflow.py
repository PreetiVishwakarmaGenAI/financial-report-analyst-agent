from unittest.mock import MagicMock, patch

from app.graph.state import AgentState
from app.enums.task_type import TaskType
from app.graph.workflow import create_workflow


@patch("app.graph.workflow.PlannerAgent")
@patch("app.graph.workflow.ResearcherAgent")
@patch("app.graph.workflow.SynthesizerAgent")
def test_workflow(
    mock_synthesizer_cls,
    mock_researcher_cls,
    mock_planner_cls,
):

    planner = MagicMock()
    researcher = MagicMock()
    synthesizer = MagicMock()

    mock_planner_cls.return_value = planner
    mock_researcher_cls.return_value = researcher
    mock_synthesizer_cls.return_value = synthesizer

    planner.execute.return_value = AgentState(
        user_query="test",
        task_type=TaskType.SUMMARY,
        document_id="1",
        top_k=5,
        retrieval_queries=["Q1"],
        retrieved_chunks=[],
        citations=[],
        final_answer=None,
        error=None,
    )

    researcher.execute.return_value = AgentState(
        user_query="test",
        task_type=TaskType.SUMMARY,
        document_id="1",
        top_k=5,
        retrieval_queries=["Q1"],
        retrieved_chunks=[],
        citations=[],
        final_answer=None,  
        error=None,
    )

    synthesizer.execute.return_value = AgentState(
        user_query="test",
        task_type=TaskType.SUMMARY,
        document_id="1",
        top_k=5,
        retrieval_queries=["Q1"],
        retrieved_chunks=[],
        citations=[],
        final_answer="Answer",
        error=None
    )

    workflow = create_workflow(
        MagicMock(),
        MagicMock(),
    )

    result = workflow.invoke(
        AgentState(
            user_query="test",
            document_id="1",
            top_k=5,
            task_type=None,
            retrieval_queries=[],
            retrieved_chunks=[],
            citations=[],
            final_answer=None,
            error=None
        )
    )

    planner.execute.assert_called_once()
    researcher.execute.assert_called_once()
    synthesizer.execute.assert_called_once()

    assert result["final_answer"] == "Answer"