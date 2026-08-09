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
  "type": "line | area | bar | stacked_bar | horizontal_bar | composed | scatter | pie | radar | table",
  "title": "concise chart title",
  "description": "one-sentence explanation",
  "x_axis": {{"data_key": "a result column", "label": "human label"}},
  "y_axis": {{"label": "human label", "format": "number | percentage"}},
  "series": [
    {{"data_key": "a result column", "label": "human label", "render_as": "line | area | bar"}}
  ]
}}

Rules:
- Use only the columns in the corresponding result.
- Choose `line` for time trends, `bar` or `stacked_bar` for comparisons,
  `horizontal_bar` for rankings, `area` for cumulative trends, `composed` when
  mixing bars and lines, `scatter` for relationships, `pie` for small composition
  datasets, `radar` for multi-metric comparisons, and `table` for event lists.
- Every series data_key must be a result column.
- Return only valid JSON; no markdown or explanation.
"""
        return ask_llm(prompt)