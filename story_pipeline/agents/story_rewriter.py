from story_pipeline.llm import ask_llm
from story_pipeline.story_links import retain_valid_chart_markers


class StoryRewriter:
    def rewrite(
        self,
        question: str,
        evidence: str,
        story: str,
        charts: list[dict],
        instruction: str,
    ) -> str:
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

Available charts:
{charts}

Rewrite the story to follow the revision instruction.

Rules:
- Use only the provided evidence.
- Do not invent facts, statistics, years, or examples.
- Preserve factual accuracy even if the requested tone changes.
- Retain existing valid `[chart:CHART_ID]` markers when their claim remains. Add,
  remove, or relocate markers only when needed to keep them relevant.
- Use only chart IDs from Available charts.
- Return only the complete revised story with no preface or explanation.
"""
        return retain_valid_chart_markers(ask_llm(prompt), charts)
