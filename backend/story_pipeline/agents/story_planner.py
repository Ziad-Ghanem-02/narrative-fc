from story_pipeline.llm import ask_llm


class StoryPlanner:

    def __call__(self, state):

        plan = self.plan(
            state["question"],
            state["evidence"]
        )

        return {
            "plan": plan
        }

    def plan(self, question, evidence):

        prompt = f"""
You are a Story Planner.

User Question:
{question}

Evidence:
{evidence}

Your task:

- Create a logical outline for answering the user's question.
- Organize the evidence into a coherent flow.
- Do NOT write the final story.
- Do NOT invent facts.
- Use ONLY the provided evidence.


For each section of the story:

- State the purpose of the section.
- List exactly which evidence points should be discussed.
- Ensure every important evidence point is assigned to a section.

Do not leave any evidence unused.

Return a numbered outline.
"""

        print("Calling LLM...")
        return ask_llm(prompt)
        print("LLM returned.")