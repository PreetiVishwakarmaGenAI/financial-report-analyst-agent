import logging

from fastapi import APIRouter, Request

from app.agents.planner_agent import PlannerAgent
from app.agents.researcher_agent import ResearcherAgent
from app.agents.synthesizer_agent import SynthesizerAgent
from app.graph.state import AgentState
from app.schemas.query import QueryRequest

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/query",
    tags=["Query"],
)


@router.post("")
def query_documents(
    query_request: QueryRequest,
    request: Request,
):
    """
    Query a financial document using the multi-agent pipeline.

    Flow:
        Planner -> Researcher -> Synthesizer
    """

    planner_agent: PlannerAgent = request.app.state.planner_agent
    researcher_agent: ResearcherAgent = request.app.state.researcher_agent
    synthesizer_agent: SynthesizerAgent = request.app.state.synthesizer_agent

    state = AgentState(
        user_query=query_request.query,
        document_id=query_request.document_id,
        top_k=query_request.top_k,
    )

    try:
        logger.info("Starting agent workflow.")

        state = planner_agent.execute(state)

        state = researcher_agent.execute(state)

        state = synthesizer_agent.execute(state)

        logger.info("Workflow completed successfully.")

        return {
            "question": state.user_query,
            "answer": state.final_answer,
            "citations": state.retrieved_chunks,
        }

    except Exception:
        logger.exception("Query workflow failed.")
        raise