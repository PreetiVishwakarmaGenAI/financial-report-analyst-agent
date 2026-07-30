from functools import partial

from langgraph.graph import StateGraph
from langgraph.graph import START
from langgraph.graph import END

from app.graph.state import AgentState
from app.graph.nodes import (
    planner_node,
    researcher_node,
    synthesizer_node,
)

from app.agents.planner_agent import PlannerAgent
from app.agents.researcher_agent import ResearcherAgent
from app.agents.synthesizer_agent import SynthesizerAgent

from app.services.llm_service import LLMService
from app.services.retrieval_service import RetrievalService


def create_workflow(
    llm_service: LLMService,
    retrieval_service: RetrievalService,
):

    planner = PlannerAgent(llm_service)
    researcher = ResearcherAgent(retrieval_service)
    synthesizer = SynthesizerAgent(llm_service)
    builder = StateGraph(AgentState)

    builder.add_node(
        "planner",
        partial(
            planner_node,
            planner=planner,
        ),
    )

    builder.add_node(
        "researcher",
        partial(
            researcher_node,
            researcher=researcher,
        ),
    )

    builder.add_node(
        "synthesizer",
        partial(
            synthesizer_node,
            synthesizer=synthesizer,
        ),
    )

    builder.add_edge(START, "planner")
    builder.add_edge("planner", "researcher")
    builder.add_edge("researcher", "synthesizer")
    builder.add_edge("synthesizer", END)

    return builder.compile()