from Database.schema import load_schema
from Database.db import run_query

from agents.data_agent import DataAgent
from agents.evidence_builder import EvidenceBuilder
from agents.story_planner import StoryPlanner
from agents.story_writer import StoryWriter
from graph import graph


def main():

    question = (
        "Has the competitive gap between traditional football powerhouses and underdog teams decreased in recent FIFA Men's World Cups? Support your answer with statistical evidence and notable examples."
    )

    initial_state = {

        "question": question,

        "queries": [],

        "results": [],

        "evidence": "",

        "plan": "",

        "story": "",

        "charts": []

    }

    final_state = graph.invoke(initial_state)

    print("\n" + "=" * 70)
    print("Query")
    print("=" * 70)
    print(final_state["queries"])

    print("\n" + "=" * 70)
    print("Evidence")
    print("=" * 70)
    print(final_state["evidence"])

    print("\n" + "=" * 70)
    print("Story Plan")
    print("=" * 70)
    print(final_state["plan"])

    print("\n" + "=" * 70)
    print("Story")
    print("=" * 70)
    print(final_state["story"])

    print("\n" + "=" * 70)
    print("Charts")
    print("=" * 70)

    for chart in final_state["charts"]:
        print(chart)


if __name__ == "__main__":
    main()
