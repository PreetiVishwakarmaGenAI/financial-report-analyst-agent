from app.graph.state import AgentState

from app.agents.planner_agent import PlannerAgent
from app.agents.researcher_agent import ResearcherAgent
from app.agents.synthesizer_agent import SynthesizerAgent


def planner_node(
    state: AgentState,
    planner: PlannerAgent,
) -> AgentState:
    return planner.execute(state)


def researcher_node(
    state: AgentState,
    researcher: ResearcherAgent,
) -> AgentState:
    return researcher.execute(state)


def synthesizer_node(
    state: AgentState,
    synthesizer: SynthesizerAgent,
) -> AgentState:
    return synthesizer.execute(state)