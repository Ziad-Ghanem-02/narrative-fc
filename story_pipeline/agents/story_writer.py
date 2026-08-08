from story_pipeline.llm import ask_llm


class StoryWriter:

    def __call__(self, state):

        story = self.write(
            state["question"],
            state["evidence"],
            state["plan"]
        )

        return {
            "story": story
        }

    def write(self, question, evidence, plan):

        prompt = f"""
You are a professional football journalist.

User Question:
{question}

Evidence:
{evidence}

Story Plan:
{plan}

Instructions:

You MUST use every important piece of evidence.

Do not omit important statistics.

Do not omit notable examples.

Do not omit years.

Do not omit numerical trends.

If multiple examples exist, include them all naturally in the story.

The final article should reflect every major finding from the evidence.
- Use ONLY the provided evidence.
- Follow the story plan.
- Do NOT invent facts.
- Do NOT exaggerate.
- Write naturally.
- Write between 500 - 600 words.

Write an analytical football article.

Requirements:

- Use every important evidence point.
- Mention every important statistic.
- Mention every important year.
- Mention every significant underdog example.
- Mention every significant upset.
- Explain why each statistic supports or contradicts the hypothesis.
- Do not ignore evidence because it seems repetitive.
- If evidence conflicts, discuss the conflict.
- Keep a logical flow.
- Do not invent facts.
- Base every claim on the provided evidence.

"""

        print("Calling LLM...")
        return ask_llm(prompt)
        print("LLM returned.")