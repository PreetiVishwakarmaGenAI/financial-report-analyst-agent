from unittest.mock import MagicMock

from app.agents.researcher_agent import ResearcherAgent
from app.graph.state import AgentState
from app.schemas.retrieval_model import RetrievedChunk


def test_researcher_agent():

    retrieval = MagicMock()

    retrieval.retrieve.return_value = [
        RetrievedChunk(
            chunk_id="1",
            content="Tesla revenue increased.",
            similarity_score=0.95,
            page_number=1,
            metadata={},
        )
    ]

    researcher = ResearcherAgent(retrieval)

    state = AgentState(
        user_query="Revenue",
        document_id="tesla",
        retrieval_queries=[
            "Tesla revenue"
        ]
    )

    result = researcher.execute(state)

    assert len(result.retrieved_chunks) == 1

    assert (
        result.retrieved_chunks[0].content
        == "Tesla revenue increased."
    )