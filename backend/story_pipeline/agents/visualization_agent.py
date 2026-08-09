from story_pipeline.charts import build_chart_specs, parse_chart_specs
from story_pipeline.llm import ask_llm


class VisualizationAgent:
    def __call__(self, state):
        results = state["results"]
        try:
            candidates = parse_chart_specs(self.generate_specs(results))
            charts = build_chart_specs(results, candidates)
        except (ValueError, TypeError):
            charts = build_chart_specs(results, [])

        return {
            "charts": charts
        }

    def generate_specs(self, results):
        prompt = f"""
You are a data visualization designer preparing specifications for a React Recharts frontend.

Query results:
{results}

Return a JSON array with exactly one object per query result in the same order.
Each object must use this exact shape:
{{
  "type": "line | bar | stacked_bar | scatter | table",
  "title": "concise chart title",
  "description": "one-sentence explanation",
  "x_axis": {{"data_key": "a result column", "label": "human label"}},
  "series": [
    {{"data_key": "a result column", "label": "human label", "color": "#2563eb"}}
  ]
}}

Rules:
- Use only the columns in the corresponding result.
- Use only these colors: #2563eb, #f97316, #16a34a, #9333ea, #dc2626.
- Choose `line` for time trends, `bar` or `stacked_bar` for comparisons,
  `scatter` for relationships, and `table` for individual event lists.
- Every series data_key must be a result column.
- Return only valid JSON; no markdown or explanation.
"""
        return ask_llm(prompt)