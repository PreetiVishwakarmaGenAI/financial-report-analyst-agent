import logging
from functools import partial

from langgraph.graph import StateGraph
from langgraph.graph import START
from langgraph.graph import END
from langsmith import traceable

from app.graph.state import AgentState
from app.graph.nodes import (
    planner_node,
    researcher_node,
    synthesizer_node,
    reflection_node
)

from app.agents.planner_agent import PlannerAgent
from app.agents.researcher_agent import ResearcherAgent
from app.agents.synthesizer_agent import SynthesizerAgent
from app.agents.reflection_agent import ReflectionAgent

from app.services.llm_service import LLMService
from app.services.retrieval_service import RetrievalService
from app.tools.retrieval_tool import RetrievalTool
from app.tools.tool_factory import create_tool_registry
from app.tools.tool_registry import ToolRegistry

logger = logging.getLogger(__name__)

@traceable(name="Query Workflow")
def create_workflow(
    llm_service: LLMService,
    retrieval_service: RetrievalService,
):

    tool_registry = ToolRegistry()
    tool_registry = create_tool_registry(
        retrieval_service
    )
    logger.info("Tool registry created with tools: %s", list(tool_registry.tools.keys()))

    planner = PlannerAgent(llm_service, tool_registry=tool_registry)
    researcher = ResearcherAgent(tool_registry=tool_registry)
    synthesizer = SynthesizerAgent(llm_service)
    reflection = ReflectionAgent(llm_service)
    graph = StateGraph(AgentState)

    graph.add_node(
        "planner",
        partial(
            planner_node,
            planner=planner,
        ),
    )

    graph.add_node(
        "researcher",
        partial(
            researcher_node,
            researcher=researcher,
        ),
    )

    graph.add_node(
        "synthesizer",
        partial(
            synthesizer_node,
            synthesizer=synthesizer,
        ),
    )

    graph.add_node(
        "reflection",
        partial(
            reflection_node,
            reflection=reflection,
        ),
    )

    graph.add_edge(START, "planner")
    graph.add_edge("planner", "researcher")
    graph.add_edge("researcher", "synthesizer")
    graph.add_edge("synthesizer", "reflection")
    graph.add_conditional_edges(
        "reflection",
        reflection.route_after_reflection,
        {
            "retry": "researcher",
            "finish": END,
        }
    )

    return graph.compile()