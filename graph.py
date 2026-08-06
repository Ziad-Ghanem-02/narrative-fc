from langgraph.graph import StateGraph

from state import WorldCupState

from agents.data_agent import DataAgent
from agents.evidence_builder import EvidenceBuilder
from agents.story_planner import StoryPlanner
from agents.story_writer import StoryWriter
from agents.visualization_agent import VisualizationAgent
from Database.schema import load_schema



builder = StateGraph(WorldCupState)

schema = load_schema()

builder.add_node("data", DataAgent(schema))

builder.add_node("evidence", EvidenceBuilder())

builder.add_node("planner", StoryPlanner())

builder.add_node("writer", StoryWriter())

builder.add_node("visualizer", VisualizationAgent())

builder.add_edge("data","evidence")

builder.add_edge("evidence","planner")

builder.add_edge("evidence","visualizer")

builder.add_edge("planner","writer")

builder.set_entry_point("data")

graph = builder.compile()