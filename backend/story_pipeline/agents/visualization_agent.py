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

==================================================
BIG TEAMS
==================================================

For this project, the following teams are ALWAYS considered Traditional Football Powerhouses (Big Teams):

Brazil
Germany
Argentina
Italy
France
Spain
England
Netherlands
Portugal
Uruguay

Treat "West Germany" and "East Germany" as "Germany".
Treat "Soviet Union" as "Russia".

==================================================
RULES
==================================================

If a result contains several stage-based metrics that are nested or overlapping
rather than additive (for example quarter-finalists, semi-finalists, and finalists
for the same groups), do NOT use `stacked_bar`, because stacking would imply
a sum of disjoint parts. Prefer `bar` for grouped comparison, or `composed`
if you need to emphasize one subset differently.

Always treat West Germany and East Germany as Germany.
Always treat Soviet Union as Russia.

Every team that is NOT listed above must be treated as an Underdog. like japan, morocco, turkey, egypt, croatia, costa rica, mexico and many more

==================================================
CHART TYPE SELECTION RULES
==================================================

Choose the type that best matches the SHAPE of each individual result:

- `line`: a trend of one or two numeric metrics across years/tournaments.
- `area`: a cumulative or share/percentage trend across years/tournaments.
- `bar`: a plain comparison across a handful of categories.
- `stacked_bar`: comparing 2+ groups' composition across categories/years.
- `horizontal_bar`: a ranking/leaderboard (e.g. biggest upsets, most goals).
- `composed`: mixing a rate/percentage line together with volume bars.
- `scatter`: exactly two independent numeric columns with ONE row per
  team/entity and NO time axis — use this for relationship/correlation data.
- `pie`: a single snapshot broken into 3-7 categories with one numeric
  measure and NO time axis — use this for composition/share-of-total data.
- `radar`: one row per team/entity with 3+ numeric metric columns — use this
  for multi-metric profile comparisons across a small number of teams.
- `table`: only for literal event/match listings with mixed text columns
  that do not reduce to a single numeric measure (e.g. upset listings with
  score strings). Do NOT use `table` merely because a result has several
  columns — prefer a chart whenever the columns are mostly numeric.

==================================================
DIVERSITY REQUIREMENT
==================================================

Across the WHOLE array you return, you MUST use AT LEAST 4 different chart
types. Do NOT assign `line` or `bar` to more than half of the results. Do NOT
use `table` for more than 2 results total. If a result has exactly one
categorical column and one numeric column with 3-7 rows and no time axis,
prefer `pie` over `bar`. If a result has exactly one categorical column and
two numeric columns with no time axis, prefer `scatter`. If a result has one
categorical column and 3+ numeric columns with no time axis, prefer `radar`.
Reserve `line`/`area`/`composed` for results that have a year/date column.

Rules:
- Use only the columns in the corresponding result.
- Every series data_key must be a result column.
- Return only valid JSON; no markdown or explanation.
- Use `stacked_bar` only when the series represent additive parts of a whole
  within each category.
- Do NOT use `stacked_bar` for hierarchical tournament stages such as
  quarter-finals, semi-finals, and finals in the same result.
  Example:
    If columns are:
      tournament,
      big_quarter_finalists,
      underdog_quarter_finalists,
      big_semi_finalists,
      underdog_semi_finalists,
      big_finalists,
      underdog_finalists
    then prefer `bar` over `stacked_bar`.
"""
        return ask_llm(prompt)