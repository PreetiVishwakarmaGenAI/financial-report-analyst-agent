from unittest.mock import Mock

import pytest

from app.agents.reflection_agent import ReflectionAgent, REFLECTION_PROMPT
from app.enums.agent_role import AgentRole
from app.graph.state import AgentState
from app.schemas.reflection_response import ReflectionResponse


def make_state(**overrides):
    values = {
        "user_query": "What was the company's revenue growth?",
        "document_id": "annual-report-2025",
        "top_k": 5,
        "final_answer": "Revenue grew by 8% year over year.",
        "retrieved_chunks": [],
        "citations": [],
        "retrieval_queries": ["revenue growth in 2025"],
        "retry_count": 0,
        "max_retries": 2,
        "additional_tools": [],
        "additional_retrieval_queries": [],
        "additional_web_queries": [],
        "missing_information": [],
    }
    values.update(overrides)
    return AgentState(**values)


def make_response(
    *,
    passed=True,
    issues=None,
    missing_information=None,
    feedback="Looks good.",
    action="PASS",
    search_query=None,
):
    return ReflectionResponse(
        passed=passed,
        correctness=95 if passed else 45,
        groundedness=95 if passed else 40,
        completeness=90 if passed else 50,
        citation_quality=95 if passed else 30,
        numerical_consistency=95 if passed else 40,
        relevance=95,
        evidence_sufficiency=90 if passed else 25,
        temporal_validity=95,
        issues=issues or [],
        missing_information=missing_information or [],
        recommended_action=action,
        search_query=search_query,
        feedback=feedback,
    )


@pytest.fixture
def llm_service():
    return Mock()


def test_execute_passes_structured_response_request_to_llm(llm_service):
    state = make_state()
    llm_service.generate_structured_response.return_value = make_response()
    agent = ReflectionAgent(llm_service)

    result = agent.execute(state)

    assert result is state
    llm_service.generate_structured_response.assert_called_once()
    call = llm_service.generate_structured_response.call_args.kwargs
    assert call["role"] == AgentRole.REFLECTION
    assert call["response_model"] is ReflectionResponse
    assert "What was the company's revenue growth?" in call["user_prompt"]
    assert "Revenue grew by 8% year over year." in call["user_prompt"]
    assert "RETRIEVED EVIDENCE:" in call["user_prompt"]
    assert "CITATIONS:" in call["user_prompt"]
    assert call["system_prompt"] is not None


def test_pass_action_clears_stale_recovery_fields_without_incrementing_retry(
    llm_service,
):
    state = make_state(
        retry_count=1,
        additional_tools=["web_search"],
        additional_retrieval_queries=["old retrieval query"],
        additional_web_queries=["old web query"],
        missing_information=["old missing information"],
    )
    llm_service.generate_structured_response.return_value = make_response(
        passed=True,
        feedback="The answer is supported by the evidence.",
        action="PASS",
    )

    result = ReflectionAgent(llm_service).execute(state)

    assert result.reflection_status == "PASS"
    assert result.reflection_reason == "The answer is supported by the evidence."
    assert result.missing_information == []
    assert result.additional_tools == []
    assert result.additional_retrieval_queries == []
    assert result.additional_web_queries == []
    assert result.retry_count == 1


def test_retrieve_more_sets_targeted_retrieval_queries(llm_service):
    state = make_state()
    llm_service.generate_structured_response.return_value = make_response(
        passed=False,
        issues=["Revenue growth claim is not supported."],
        missing_information=[
            "Find reported revenue for 2024.",
            "Find reported revenue for 2025.",
        ],
        feedback="The report may contain the missing figures.",
        action="RETRIEVE_MORE",
    )

    result = ReflectionAgent(llm_service).execute(state)

    assert result.reflection_status == "RETRIEVE_MORE"
    assert result.reflection_reason == "The report may contain the missing figures."
    assert result.missing_information == [
        "Find reported revenue for 2024.",
        "Find reported revenue for 2025.",
    ]
    assert result.additional_tools == ["retrieval"]
    assert result.additional_retrieval_queries == [
        "Find reported revenue for 2024.",
        "Find reported revenue for 2025.",
    ]
    assert result.additional_web_queries == []
    # Researcher increments this only when it actually starts a retry.
    assert result.retry_count == 0


def test_retrieve_more_falls_back_to_original_queries_when_gap_list_is_empty(
    llm_service,
):
    state = make_state()
    llm_service.generate_structured_response.return_value = make_response(
        passed=False,
        feedback="Search the report again with a more focused query.",
        action="RETRIEVE_MORE",
    )

    result = ReflectionAgent(llm_service).execute(state)

    assert result.additional_tools == ["retrieval"]
    assert result.additional_retrieval_queries == [
        "revenue growth in 2025"
    ]


def test_web_search_sets_search_query(llm_service):
    state = make_state()
    query = "Company revenue growth 2025 annual results"
    llm_service.generate_structured_response.return_value = make_response(
        passed=False,
        missing_information=["Latest revenue growth after the report period"],
        feedback="The question requires information outside the report.",
        action="WEB_SEARCH",
        search_query=query,
    )

    result = ReflectionAgent(llm_service).execute(state)

    assert result.reflection_status == "WEB_SEARCH"
    assert result.additional_tools == ["web_search"]
    assert result.additional_web_queries == [query]
    assert result.additional_retrieval_queries == []
    assert result.retry_count == 0


def test_web_search_without_query_does_not_schedule_a_tool(llm_service):
    state = make_state()
    llm_service.generate_structured_response.return_value = make_response(
        passed=False,
        feedback="External information is required.",
        action="WEB_SEARCH",
        search_query="  ",
    )

    result = ReflectionAgent(llm_service).execute(state)

    assert result.reflection_status == "WEB_SEARCH"
    assert result.additional_tools == []
    assert result.additional_web_queries == []
    assert result.retry_count == 0



def test_resynthesize_does_not_schedule_retrieval_or_web_search(
    llm_service,
):
    state = make_state()

    llm_service.generate_structured_response.return_value = make_response(
        passed=False,
        issues=["The answer needs clearer explanation."],
        feedback=(
            "The evidence is sufficient, but the answer "
            "needs to be rewritten."
        ),
        action="RESYNTHESIZE",
    )

    result = ReflectionAgent(llm_service).execute(state)

    assert result.reflection_status == "RESYNTHESIZE"
    assert result.reflection_reason == (
        "The evidence is sufficient, but the answer "
        "needs to be rewritten."
    )
    assert result.additional_tools == []
    assert result.additional_retrieval_queries == []
    assert result.additional_web_queries == []
    assert result.retry_count == 0

    state = make_state()
    llm_service.generate_structured_response.return_value = make_response(
        passed=False,
        feedback="Evidence is sufficient, but the answer needs correction.",
        action="RESYNTHESIZE",
    )

    result = ReflectionAgent(llm_service).execute(state)

    assert result.reflection_status == "RESYNTHESIZE"
    assert result.additional_tools == []
    assert result.additional_retrieval_queries == []
    assert result.additional_web_queries == []


def test_execute_propagates_llm_exception(llm_service):
    state = make_state()
    llm_service.generate_structured_response.side_effect = RuntimeError(
        "LLM unavailable"
    )

    with pytest.raises(RuntimeError, match="LLM unavailable"):
        ReflectionAgent(llm_service).execute(state)


def test_route_endes_when_reflection_passes(llm_service):
    agent = ReflectionAgent(llm_service)
    state = make_state(reflection_status="PASS", retry_count=0, max_retries=2)

    assert agent.route_after_reflection(state) == "end"


def test_route_retries_when_reflection_requests_retrieval(llm_service):
    agent = ReflectionAgent(llm_service)
    state = make_state(
        reflection_status="RETRIEVE_MORE",
        additional_tools=["retrieval"],
        retry_count=0,
        max_retries=2,
        additional_retrieval_queries=["Find reported revenue for 2024."]
    )

    assert agent.route_after_reflection(state) == "researcher"


def test_route_retries_when_reflection_requests_web_search(llm_service):
    agent = ReflectionAgent(llm_service)
    state = make_state(
        reflection_status="WEB_SEARCH",
        additional_tools=["web_search"],
        retry_count=0,
        max_retries=2,
        additional_web_queries=["HDFC Bank FY2025-26 annual financial results"]
    )

    assert agent.route_after_reflection(state) == "researcher"


@pytest.mark.parametrize("retry_count", [2, 3])
def test_route_endes_when_retry_limit_is_reached(llm_service, retry_count):
    agent = ReflectionAgent(llm_service)
    state = make_state(
        reflection_status="RETRIEVE_MORE",
        additional_tools=["retrieval"],
        retry_count=retry_count,
        max_retries=2,
    )

    assert agent.route_after_reflection(state) == "end"


def test_route_endes_when_reflection_requests_no_usable_recovery_tool(
    llm_service,
):
    agent = ReflectionAgent(llm_service)
    state = make_state(
        reflection_status="WEB_SEARCH",
        additional_tools=[],
        retry_count=0,
        max_retries=2,
    )

    assert agent.route_after_reflection(state) == "end"


def test_reflection_response_rejects_scores_outside_zero_to_hundred():
    with pytest.raises(ValueError):
        make_response().__class__(
            passed=True,
            correctness=101,
            groundedness=90,
            completeness=90,
            citation_quality=90,
            numerical_consistency=90,
            relevance=90,
            evidence_sufficiency=90,
            temporal_validity=90,
            recommended_action="PASS",
        )


def test_reflection_response_rejects_unsupported_recommended_action():
    with pytest.raises(ValueError):
        ReflectionResponse(
            passed=False,
            correctness=50,
            groundedness=50,
            completeness=50,
            citation_quality=50,
            numerical_consistency=50,
            relevance=50,
            evidence_sufficiency=50,
            temporal_validity=50,
            recommended_action="RETRY",
        )

def test_route_resynthesizes_when_reflection_requests_it(
    llm_service,
):
    agent = ReflectionAgent(llm_service)

    state = make_state(
        reflection_status="RESYNTHESIZE",
        retry_count=0,
        max_retries=2,
    )

    assert agent.route_after_reflection(state) == "synthesizer"
