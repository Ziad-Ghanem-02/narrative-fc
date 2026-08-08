from langgraph.graph import END, StateGraph

from story_pipeline.state import WorldCupState

from story_pipeline.agents.data_agent import DataAgent
from story_pipeline.agents.evidence_builder import EvidenceBuilder
from story_pipeline.agents.story_planner import StoryPlanner
from story_pipeline.agents.story_writer import StoryWriter
from story_pipeline.agents.visualization_agent import VisualizationAgent
from story_pipeline.schema import load_schema



def create_graph():
    builder = StateGraph(WorldCupState)

    schema = load_schema()

    builder.add_node("data", DataAgent(schema))

    builder.add_node("evidence", EvidenceBuilder())

    builder.add_node("planner", StoryPlanner())

    builder.add_node("writer", StoryWriter())

    builder.add_node("visualizer", VisualizationAgent())

    builder.add_edge("data", "evidence")

    builder.add_edge("evidence", "planner")

    builder.add_edge("evidence", "visualizer")

    builder.add_edge("planner", "writer")

    builder.add_edge("writer", END)
    builder.add_edge("visualizer", END)
    builder.set_entry_point("data")
    return builder.compile()


def run_story(question: str) -> WorldCupState:
    initial_state: WorldCupState = {
        "question": question,
        "queries": [],
        "results": [],
        "evidence": "",
        "plan": "",
        "story": "",
        "charts": [],
    }
    return create_graph().invoke(initial_state)