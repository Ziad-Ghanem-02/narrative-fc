import logging

from story_pipeline.database import run_query_with_columns
from story_pipeline.llm import ask_llm
from story_pipeline.serialization import to_json_value

logger = logging.getLogger(__name__)


class EvidenceBuilder:

    def __call__(self, state):

        all_results = []

        for query in state["queries"]:
            try:
                columns, rows = run_query_with_columns(query["sql"])
            except Exception as error:
                # The data agent generates SQL with an LLM, so a query can be
                # syntactically or semantically wrong (e.g. referencing a
                # column omitted from a CTE). Skip the broken query and keep
                # going so one bad result does not abort the whole pipeline.
                logger.warning(
                    "Query failed and was skipped: %s\nSQL: %s",
                    error,
                    query["sql"],
                )
                all_results.append({
                    "purpose": query["purpose"],
                    "sql": query["sql"],
                    "columns": [],
                    "data": [],
                    "error": f"{type(error).__name__}: {error}",
                })
                continue

            all_results.append({
                "purpose": query["purpose"],
                "sql": query["sql"],
                "columns": columns,
                "data": [
                    to_json_value(dict(zip(columns, row)))
                    for row in rows
                ],
            })

        evidence = self.build(
            state["question"],
            all_results
        )

        return {

            "results": all_results,

            "evidence": evidence

        }

    def build(self, question, all_results):

        prompt = f"""
You are an Evidence Builder for a football storytelling system.

Research Question:
{question}

Research Results:
{all_results}

Your task:

- Analyze ALL research results together.
- Convert them into factual evidence.
- Combine information from all result sets.
- Identify important trends and relationships.
- Keep ONLY facts supported by the data.

Rules:

- DO NOT mention SQL.
- DO NOT mention databases.
- DO NOT explain how the data was retrieved.
- DO NOT speculate.
- DO NOT invent facts.
- DO NOT answer the user's question yet.

Return a comprehensive evidence report.

For every SQL result:

- Preserve all important statistics.
- Preserve numerical values.
- Preserve years.
- Preserve country names.
- Preserve trends.
- Preserve examples.
- Preserve rankings.
- Preserve comparisons.

Do NOT summarize multiple findings into one sentence.

Every important fact should appear as its own bullet point.

This report will be consumed by another AI agent that writes the final story.

Your output should be a list of evidence that another AI agent can use to write a story.

Your goal is NOT to summarize.

Your goal is to preserve every important fact.

For every research result:

- Include all numerical values.
- Include all years.
- Include all country names.
- Include all tournament stages.
- Include all rankings.
- Include all trends.
- Include every important example.

Never merge multiple findings into one sentence.

Do not omit any statistically significant result.

Structure the report using sections:

## Historical dominance

## Emerging underdogs

## Tournament progression

## Famous upsets

## Statistical trends

## Key observations

The Story Writer will rely entirely on your report.
"""

        print("Calling LLM...")
        response = ask_llm(prompt)
        print("LLM returned.")
        return response