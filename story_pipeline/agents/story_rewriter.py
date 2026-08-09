from story_pipeline.llm import ask_llm


class StoryRewriter:
    def rewrite(self, question: str, evidence: str, story: str, instruction: str) -> str:
        prompt = f"""
You are a professional football journalist revising an analytical article.

User question:
{question}

Evidence:
{evidence}

Current story:
{story}

Revision instruction:
{instruction}

Rewrite the story to follow the revision instruction.

Rules:
- Use only the provided evidence.
- Do not invent facts, statistics, years, or examples.
- Preserve factual accuracy even if the requested tone changes.
- Return only the complete revised story with no preface or explanation.
"""
        return ask_llm(prompt)
