from story_pipeline.llm import ask_llm


class DataAgent:

    def __init__(self, schema):
        self.schema = schema

    def __call__(self, state):

        queries = self.generate_queries(
            state["question"]
        )

        return {
            "queries": queries
        }

    def parse_queries(self, response):
        queries = []
        blocks = response.split("###")

        for block in blocks:
            block = block.strip()
            if not block:
                continue

            purpose_lines = []
            sql_lines = []
            reading_purpose = False
            reading_sql = False

            for line in block.splitlines():
                stripped_line = line.strip()
                if stripped_line.startswith("PURPOSE:"):
                    reading_purpose = True
                    purpose = stripped_line.removeprefix("PURPOSE:").strip()
                    if purpose:
                        purpose_lines.append(purpose)
                elif stripped_line.startswith("SQL:"):
                    reading_purpose = False
                    reading_sql = True
                    sql = stripped_line.removeprefix("SQL:").strip()
                    if sql:
                        sql_lines.append(sql)
                elif reading_purpose and stripped_line:
                    purpose_lines.append(stripped_line)
                elif reading_sql:
                    sql_lines.append(line)

            if sql_lines:
                queries.append({
                    "purpose": " ".join(purpose_lines),
                    "sql": "\n".join(sql_lines).strip(),
                })

        return queries



    def generate_queries(self, question):

        prompt = f"""
You are an expert football data analyst and PostgreSQL developer.

==================================================
DATABASE SCHEMA
==================================================

{self.schema}

==================================================
RESEARCH QUESTION
==================================================

{question}

==================================================
PROJECT OBJECTIVE
==================================================

This project investigates whether the competitive gap between traditional football powerhouses and underdog teams has become smaller over time in the FIFA Men's World Cup.

Your objective is NOT simply to answer the user's question.

Your objective is to collect enough statistical evidence to either SUPPORT or REJECT the hypothesis.

Think like a football researcher preparing figures for an academic paper.

==================================================
DEFINITIONS
==================================================

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
Treat Soviet Union as "Russia".

==================================================
UNDERDOGS
==================================================

every team that is NOT listed above must be treated as an Underdog. like japan, morocco, turkey, korea, croatia, costa rica, mexico and many more

This definition MUST be used consistently in every SQL query.

==================================================
DATABASE RULES
==================================================

read and understand all the dataset carefully first in order to know how to retrieve expected right data

1. Unless explicitly requested otherwise, ONLY use FIFA Men's World Cup tournaments.

2. Men's tournaments are identified using

tournament_name LIKE '%FIFA Men''s World Cup%'

3. Always include this filter whenever the tournaments table is used.

4. Treat West Germany and East Germany as Germany and Soviet Union as Russia.

Whenever statistics are grouped by country use

CASE
WHEN winner='West Germany' OR winner='East Germany' THEN 'Germany'
ELSE winner
END

CASE 
WHEN winner='Soviet Union' THEN 'Russia'
ELSE winner
END

5. Never invent tables.

6. Never invent columns.

7. Generate valid PostgreSQL only. Use PostgreSQL-compatible syntax, string literals,
   identifier quoting, functions, and casts.

8. One read-only SELECT or WITH statement per query. A single optional trailing
   semicolon is allowed; do not include multiple statements.

9. `group_standings.advanced` is a `bit varying` column, not text or boolean.
   Test that a team advanced with `gs.advanced = B'1'`.

10. All stage names in matches table are in lowercase. example: 'quarter-finals', 'semi-finals', 'final', 'group stage, round of 16', 'third place match', 'round of 32'.

==================================================
READABILITY RULES
==================================================

Never return IDs.

The SQL output should be understandable by a human without further lookups.

==================================================
SPECIAL RULES
==================================================

If calculating Goal Difference

DO NOT use

group_standings.goal_difference

Instead calculate it using

ABS(home_team_score-away_team_score)

from the matches table.

==================================================
RESEARCH STRATEGY
==================================================

Before generating SQL,

think like a football analyst.

Determine what evidence would convince someone that the competitive gap has become smaller.

Collect evidence from MULTIPLE independent perspectives.

Your SQL queries must, TOGETHER AS A SET, produce result shapes suitable for a
DIVERSE mix of visualizations. Do NOT let every query produce a "tournament by
year" time series. Aim for this spread across the whole set:

- Line / Area Charts — trends over tournaments (time on the x-axis).
- Bar / Stacked Bar / Horizontal Bar Charts — comparisons and rankings.
- Pie Charts — a single snapshot broken into a small number of categories
  (for example: the share/composition of something in the latest tournament,
  or across all tournaments combined), 3-7 categories, 1 numeric measure.
- Scatter Plots — the relationship between exactly TWO numeric metrics, with
  one row per team or per team-tournament (no time axis).
- Radar Charts — a multi-metric profile comparing a handful (4-8) of teams
  across at least 3 different numeric metrics in the same row.

Generate BETWEEN 7 AND 10 SQL queries.

Each query MUST investigate a different research dimension, AND the queries
must collectively cover EVERY chart shape above at least once. Do not skip the
pie, scatter, or radar shapes just because a time-series query is easier to
write.

If multiple closely related statistics are part of the same analytical dimension,
prefer ONE wider query with multiple numeric columns over several nearly
duplicate queries. Do this especially for knockout-stage representation.

==================================================
REQUIRED RESEARCH DIMENSIONS
==================================================

Your generated SQL queries MUST investigate ALL of the following dimensions.

Do NOT skip any dimension unless the required data does not exist.

==================================================
TEAM CLASSIFICATION RULES
==================================================

Whenever generating SQL:

- Any team in the predefined Big Teams list is a Big Team.
- Every other team is an Underdog.
- Never create your own classification.
- Never change the Big Teams list.
- Always treat West Germany and East Germany as Germany.
- Always treat Soviet Union as Russia.

--------------------------------------------------
1. Goals Scored
--------------------------------------------------

For every FIFA Men's World Cup tournament.
Compare the total number of goals scored by:

- Big Teams
- Underdog Teams

This data should be suitable for a line chart.

Count goals only from the matches table not the goals table. 
By getting the home_team_score and away_team_score columns from the matches table.
And matching the home team and away team against the Big teams and underdogs.
Then sum the goals scored by each group for every tournament.

When counting goals,
Never SUM over any id.

--------------------------------------------------
2. Knockout Stage Representation
--------------------------------------------------

For every tournament calculate all of the following in ONE query:

- Number of Big Teams reaching the quarter-finals
- Number of Underdog Teams reaching the quarter-finals
- Number of Big Teams reaching the semi-finals
- Number of Underdog Teams reaching the semi-finals
- Number of Big Teams reaching the final
- Number of Underdog Teams reaching the final

Return ONE row per tournament.

This result should be suitable for a multi-series grouped bar chart or a composed chart.

Important:
- Do NOT split quarter-finals, semi-finals, and finals into separate queries.
- Do NOT use a stacked bar chart for these stage counts, because the stages are nested rather than additive.
- Use clear column names such as:
  tournament,
  big_quarter_finalists,
  underdog_quarter_finalists,
  big_semi_finalists,
  underdog_semi_finalists,
  big_finalists,
  underdog_finalists

--------------------------------------------------
5. Famous Upsets
--------------------------------------------------

Find famous upsets.

Determine the winner using the home_team_win and away_team_win columns.

The winning team is:

CASE
WHEN home_team_win = 1 AND away_team_win = 0 THEN home_team
WHEN home_team_win = 0 AND away_team_win = 0 THEN 'Draw'
ELSE away_team
END

Include:

- Tournament
- Winning Team
- Losing Team
- Final Score
- Stage

Return team names, never IDs.

--------------------------------------------------
6. Goal Difference
--------------------------------------------------

Using ONLY the matches table,

calculate

ABS(home_team_score-away_team_score)

ONLY for matches between Big Teams and Underdogs.

Compare the average goal difference by tournament.

--------------------------------------------------
7. Group Stage Success
--------------------------------------------------

For every tournament calculate

the percentage of Underdog Teams that qualified for the Knockout Stage.

Use `gs.advanced = B'1'` to identify teams that qualified.

--------------------------------------------------
8. Historical Progression
--------------------------------------------------

Identify Underdog Teams that consistently improved over multiple tournaments.

Return:

Team Name

Tournament

Stage Reached

--------------------------------------------------
9. Confederation Composition Snapshot (PIE CHART)
--------------------------------------------------

Pick the 2026 FIFA Men's World Cup tournament.

For that single tournament, calculate how many round of 16 spots were held by each confederation.

Return exactly:

- Confederation
- Number of teams

This result must have ONLY 2 columns, one categorical (confederation) and one
numeric (count), with 3-7 rows.

--------------------------------------------------
10. Team Performance Relationship (SCATTER PLOT)
--------------------------------------------------

For every team that has played at least 4 matches across all FIFA Men's World
Cup tournaments, calculate:

- Team Name
- Win rate (percentage of matches won)
- Average goal difference (using ABS(home_team_score - away_team_score) from
  the matches table, as defined above)

Return ONE row per team. Do NOT include a year or tournament column. This
result has exactly one categorical column and two independent numeric metrics,
so it can be plotted as a scatter plot of win rate versus goal difference.

--------------------------------------------------
11. Underdog Multi-Metric Profile (RADAR CHART)
--------------------------------------------------

Select the from 2002, 2006, 2010, 2014, 2018, 2022 and 2022 the 4 to 6 Underdog Teams with the most round of 16 (or better)
appearances across all FIFA Men's World Cup tournaments.

For each of these teams, calculate in ONE row:

- Team Name
- Total goals scored
- Total wins
- Total round of 16 (or better) appearances
- Average goal difference in matches against Big Teams

This result must have ONE row per team and AT LEAST 3 numeric columns besides
the team name, so it can be plotted as a radar chart comparing several metrics
per team. Do NOT include a year/tournament column.

DO NOT scale metrics from 0 to 100. Always return the raw numbers. The radar chart can be scaled in the visualization layer.

==================================================
QUALITY REQUIREMENTS
==================================================

Every SQL query should help answer the research question.

Avoid redundant analyses.

Avoid statistics with little explanatory value.

Each query should investigate a DIFFERENT aspect of competitiveness.

Every SQL query should produce results suitable for visualization.

Ensure the FULL SET of queries supports a diverse mix of chart shapes:
time trends (line/area), comparisons and rankings (bar/stacked/horizontal
bar), a single-snapshot composition (pie), a two-metric relationship
(scatter), and a multi-metric team profile (radar). Do NOT make every query
a year-by-year time series.

Avoid returning a single number whenever possible.

==================================================
REASONING
==================================================

Before writing SQL,

reason about:

1. Which evidence best answers the question.

2. Which statistics are strongest.

3. Which visualizations would best support the final story.

Only then generate the SQL.

==================================================
OUTPUT FORMAT
==================================================

Return ONLY the following format.

PURPOSE:
Goals scored comparison

SQL:
SELECT ...

###

PURPOSE:
Quarter-final representation

SQL:
SELECT ...

###

PURPOSE:
Upsets

SQL:
SELECT ...

Rules:

- Return between 7 and 10 SQL queries.
- Every query must have a different PURPOSE.
- The set of queries MUST include the pie-friendly confederation snapshot,
  the scatter-friendly team performance relationship, and the radar-friendly
  underdog multi-metric profile described above.
- Separate every query using ###.
- Do NOT return JSON.
- Do NOT explain anything.
- Return ONLY PURPOSE and SQL.
            """

        print("Calling LLM...")
        response = ask_llm(prompt)
        print("LLM returned.")

        response = response.replace("```sql", "")
        response = response.replace("```", "")
        response = response.strip()

        print(response)

        return self.parse_queries(response)