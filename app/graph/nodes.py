from app.graph.state import AgentState

from app.agents.planner_agent import PlannerAgent
from app.agents.researcher_agent import ResearcherAgent
from app.agents.synthesizer_agent import SynthesizerAgent
from app.agents.reflection_agent import ReflectionAgent


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

def reflection_node(
    state: AgentState,
    reflection: ReflectionAgent,
) -> AgentState:
    return reflection.execute(state)