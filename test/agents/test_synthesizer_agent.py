from unittest.mock import MagicMock

import pytest

from app.agents.synthesizer_agent import SynthesizerAgent
from app.graph.state import AgentState
from app.schemas.retrieval_model import RetrievedChunk
from app.services.llm_service import LLMService
from app.enums.task_type import TaskType


def test_synthesizer_agent():
    llm_service = MagicMock(spec=LLMService)
    llm_service.generate_response.return_value = (
        "Apple's revenue increased by 8% year-over-year."
    )
    agent = SynthesizerAgent(
        llm_service=llm_service,
    )
    state = AgentState(
        user_query="How did revenue perform?",
        document_id="Apple_Annual_Report.pdf",
        task_type=TaskType.GENERAL_QA,
        retrieved_chunks=[
            RetrievedChunk(
                chunk_id="1",
                content="Revenue increased by 8% year-over-year.",
                page_number=10,
                similarity_score=0.95,
                metadata={
                    "document_name":"Apple_Annual_Report.pdf",
                },   
            )
        ],
        citations=[],
        final_answer=None,
        error=None,
    )
    updated_state = agent.execute(state)
    assert (
        updated_state.final_answer
        == "Apple's revenue increased by 8% year-over-year."
    )
    llm_service.generate_response.assert_called_once()

def test_synthesizer_agent_no_chunks():
    llm_service = MagicMock(spec=LLMService)
    agent = SynthesizerAgent(
        llm_service=llm_service,
    )
    state = AgentState(
        user_query="How did revenue perform?",
        document_id="Apple_Annual_Report.pdf",
        task_type=TaskType.GENERAL_QA,
        retrieved_chunks=[],
        citations=[],
        final_answer=None,
        error=None,
    )
    updated_state = agent.execute(state)
    assert (
        updated_state.final_answer
        == "I couldn't find enough information in the provided document."
    )
    llm_service.generate_response.assert_not_called()

def test_synthesizer_agent_llm_failure():
    llm_service = MagicMock(spec=LLMService)
    llm_service.generate_response.side_effect = RuntimeError(
        "OpenAI unavailable"
    )
    agent = SynthesizerAgent(
        llm_service=llm_service,
    )
    state = AgentState(
        user_query="How did revenue perform?",
        document_id="Apple_Annual_Report.pdf",
        task_type=TaskType.GENERAL_QA,
        retrieved_chunks=[
            RetrievedChunk(
                chunk_id="1",
                content="Revenue increased by 8% year-over-year.",
                page_number=10,
                similarity_score=0.95,
                metadata={
                    "document_name":"Apple_Annual_Report.pdf",
                },   
            )
        ],
        citations=[],
        final_answer=None,
        error=None,
    )
    with pytest.raises(RuntimeError):
        agent.execute(state)