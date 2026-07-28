from unittest.mock import MagicMock

from app.agents.planner_agent import PlannerAgent
from app.enums.task_type import TaskType
from app.graph.state import AgentState
from app.schemas.planner_models import PlannerOutput


def test_planner_agent():

    llm = MagicMock()

    llm.generate_structured_response.return_value = PlannerOutput(
        task_type=TaskType.SUMMARY,
        retrieval_queries=[
            "What is Tesla revenue?"
        ]
    )

    planner = PlannerAgent(llm)

    state = AgentState(
        user_query="Summarize Tesla revenue",
        document_id="tesla"
    )

    result = planner.execute(state)
    print(result)

    assert result.task_type == TaskType.SUMMARY

    assert len(result.retrieval_queries) == 1