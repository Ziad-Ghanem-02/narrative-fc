from Services.scads_client import ask_llm


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

            purpose = ""
            sql = ""

            lines = block.splitlines()

            reading_sql = False

            for line in lines:

                if line.startswith("PURPOSE:"):
                    purpose = line.replace("PURPOSE:", "").strip()

                elif line.startswith("SQL:"):
                    reading_sql = True

                elif reading_sql:
                    sql += line + "\n"

            queries.append({
                "purpose": purpose,
                "sql": sql.strip()
            })

        return queries
    
    

    def generate_queries(self, question):

        prompt = f"""
You are an expert football data analyst and SQLite developer.

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

Treat "West Germany" as "Germany".

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

tournament_name LIKE "%FIFA Men's World Cup%"

3. Always include this filter whenever the tournaments table is used.

4. Treat West Germany as Germany.

Whenever statistics are grouped by country use

CASE
WHEN winner='West Germany' THEN 'Germany'
ELSE winner
END

5. Never invent tables.

6. Never invent columns.

7. Generate valid SQLite only.

8. One SQL statement per query.

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

Your SQL queries should be suitable for visualizations such as:

- Line Charts
- Bar Charts
- Timeline Charts
- Scatter Plots

Generate BETWEEN 7 AND 10 SQL queries.

Each query MUST investigate a different research dimension.

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
- Always treat West Germany as Germany.

--------------------------------------------------
1. Goals Scored
--------------------------------------------------

Compare the total number of goals scored by:

- Big Teams
- Underdog Teams

for every FIFA Men's World Cup tournament.

This data should be suitable for a line chart.

When counting goals,

Never SUM(goal_id).

Every row in the goals table represents exactly one goal.

Count goals using COUNT(*).

--------------------------------------------------
2. Quarter-final Representation
--------------------------------------------------

For every tournament calculate:

- Number of Big Teams reaching the Quarter-finals.
- Number of Underdog Teams reaching the Quarter-finals.

Show how this changes over time.

This should produce data suitable for a stacked bar chart.

--------------------------------------------------
3. Semi-final Representation
--------------------------------------------------

For every tournament calculate:

- Number of Big Teams reaching the Semi-finals.
- Number of Underdog Teams reaching the Semi-finals.

Show the trend over time.

--------------------------------------------------
4. Final Appearances
--------------------------------------------------

For every tournament calculate:

- Number of Big Teams reaching the Final.
- Number of Underdog Teams reaching the Final.

--------------------------------------------------
5. Famous Upsets
--------------------------------------------------

Find famous upsets.

Determine the winner using the match score.

Never rely on the "result" column.

The winning team is:

CASE
WHEN home_team_score > away_team_score THEN home_team
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

--------------------------------------------------
8. Tournament Diversity
--------------------------------------------------

Calculate the number of UNIQUE countries reaching the Quarter-finals in every tournament.

Determine whether diversity increased over time.

--------------------------------------------------
9. Historical Progression
--------------------------------------------------

Identify Underdog Teams that consistently improved over multiple tournaments.

Return:

Team Name

Tournament

Stage Reached

--------------------------------------------------
10. Continental Representation
--------------------------------------------------

Calculate the number of different confederations represented in the Quarter-finals of every tournament.

==================================================
QUALITY REQUIREMENTS
==================================================

Every SQL query should help answer the research question.

Avoid redundant analyses.

Avoid statistics with little explanatory value.

Each query should investigate a DIFFERENT aspect of competitiveness.

Every SQL query should produce results suitable for visualization.

Prefer:

- Line Charts
- Bar Charts
- Timeline Charts

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