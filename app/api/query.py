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

    state = AgentState(
        user_query=query_request.query,
        document_id=query_request.document_id,
        top_k=query_request.top_k,
    )

    try:
        logger.info("Starting agent workflow.")

        final_state = request.app.state.workflow.invoke(state)

        logger.info("Workflow completed successfully.")

        return {
            "question": final_state["user_query"],
            "answer": final_state["final_answer"],
            "citations": final_state["retrieved_chunks"],
        }

    except Exception:
        logger.exception("Query workflow failed.")
        raise