from story_pipeline.graph import run_story


def main():

    question = (
        "Has the competitive gap between traditional football powerhouses and underdog teams decreased in recent FIFA Men's World Cups? Support your answer with statistical evidence and notable examples."
    )

    final_state = run_story(question)

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
