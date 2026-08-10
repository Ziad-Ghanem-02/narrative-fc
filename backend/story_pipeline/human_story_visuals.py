from story_pipeline.charts import build_chart_specs
from story_pipeline.database import run_query_with_columns
from story_pipeline.serialization import to_json_value


POWERHOUSES = (
    "'Brazil', 'Germany', 'Argentina', 'Italy', 'France', 'Spain', "
    "'England', 'Netherlands', 'Portugal', 'Uruguay'"
)
HUMAN_STORY_QUERIES = [
    (
        "Tournament participation growth",
        f"""
        SELECT year, count_teams
        FROM tournaments
        WHERE tournament_name LIKE '%FIFA Men''s World Cup%'
        ORDER BY year
        """,
    ),
    (
        "Goals scored by team type",
        f"""
        WITH mens_tournaments AS (
            SELECT tournament_id, year
            FROM tournaments
            WHERE tournament_name LIKE '%FIFA Men''s World Cup%'
        )
        SELECT t.year,
            SUM(CASE WHEN home.team_name IN ({POWERHOUSES}, 'West Germany', 'East Germany')
                     THEN m.home_team_score ELSE 0 END
                + CASE WHEN away.team_name IN ({POWERHOUSES}, 'West Germany', 'East Germany')
                       THEN m.away_team_score ELSE 0 END) AS powerhouses_goals,
            SUM(CASE WHEN home.team_name NOT IN ({POWERHOUSES}, 'West Germany', 'East Germany')
                     THEN m.home_team_score ELSE 0 END
                + CASE WHEN away.team_name NOT IN ({POWERHOUSES}, 'West Germany', 'East Germany')
                       THEN m.away_team_score ELSE 0 END) AS underdogs_goals
        FROM matches m
        JOIN mens_tournaments t ON t.tournament_id = m.tournament_id
        JOIN teams home ON home.team_id = m.home_team_id
        JOIN teams away ON away.team_id = m.away_team_id
        GROUP BY t.year
        ORDER BY t.year
        """,
    ),
    (
        "Knockout stage representation",
        f"""
        WITH mens_tournaments AS (
            SELECT tournament_id, year
            FROM tournaments
            WHERE tournament_name LIKE '%FIFA Men''s World Cup%'
        ), team_types AS (
            SELECT team_id,
                CASE WHEN team_name IN ({POWERHOUSES})
                    OR team_name IN ('West Germany', 'East Germany')
                    THEN 'Powerhouses' ELSE 'Underdogs' END AS team_type
            FROM teams
            WHERE mens_team = B'1'
        ), stage_teams AS (
            SELECT DISTINCT m.tournament_id, m.stage_name, ta.team_id, tt.team_type
            FROM matches m
            JOIN team_appearances ta ON ta.match_id = m.match_id
            JOIN team_types tt ON tt.team_id = ta.team_id
            WHERE m.tournament_id IN (SELECT tournament_id FROM mens_tournaments)
              AND LOWER(m.stage_name) IN ('quarter-finals', 'semi-finals', 'final')
        )
        SELECT t.year,
            COUNT(*) FILTER (WHERE s.stage_name = 'quarter-finals' AND s.team_type = 'Powerhouses') AS powerhouses_quarter_finals,
            COUNT(*) FILTER (WHERE s.stage_name = 'quarter-finals' AND s.team_type = 'Underdogs') AS underdogs_quarter_finals,
            COUNT(*) FILTER (WHERE s.stage_name = 'semi-finals' AND s.team_type = 'Powerhouses') AS powerhouses_semi_finals,
            COUNT(*) FILTER (WHERE s.stage_name = 'semi-finals' AND s.team_type = 'Underdogs') AS underdogs_semi_finals,
            COUNT(*) FILTER (WHERE s.stage_name = 'final' AND s.team_type = 'Powerhouses') AS powerhouses_final,
            COUNT(*) FILTER (WHERE s.stage_name = 'final' AND s.team_type = 'Underdogs') AS underdogs_final
        FROM mens_tournaments t
        LEFT JOIN stage_teams s ON s.tournament_id = t.tournament_id
        GROUP BY t.year
        ORDER BY t.year
        """,
    ),
    (
        "Morocco World Cup progression",
        """
           SELECT t.year,
            CASE WHEN t.year = 2022 THEN 'semi-finals'
                 ELSE LOWER(qt.performance)
              END AS stage_name,
              CASE WHEN t.year = 2022 THEN 5
                  WHEN LOWER(qt.performance) = 'group stage' THEN 1
                  WHEN LOWER(qt.performance) = 'round of 16' THEN 3
                  WHEN LOWER(qt.performance) = 'quarter-finals' THEN 4
                  WHEN LOWER(qt.performance) = 'semi-finals' THEN 5
                  ELSE 0
              END AS stage_rank
        FROM qualified_teams qt
        JOIN tournaments t ON t.tournament_id = qt.tournament_id
        JOIN teams team ON team.team_id = qt.team_id
        WHERE t.tournament_name LIKE '%FIFA Men''s World Cup%'
          AND team.team_name = 'Morocco'
        ORDER BY t.year
        """,
    ),
    (
        "Powerhouse-underdog goal gap",
        f"""
        SELECT t.year,
            AVG(ABS(m.home_team_score - m.away_team_score)) AS average_goal_difference
        FROM matches m
        JOIN tournaments t ON t.tournament_id = m.tournament_id
        JOIN teams home ON home.team_id = m.home_team_id
        JOIN teams away ON away.team_id = m.away_team_id
        WHERE t.tournament_name LIKE '%FIFA Men''s World Cup%'
          AND (
            (home.team_name IN ({POWERHOUSES}, 'West Germany', 'East Germany')
             AND away.team_name NOT IN ({POWERHOUSES}, 'West Germany', 'East Germany'))
            OR
            (away.team_name IN ({POWERHOUSES}, 'West Germany', 'East Germany')
             AND home.team_name NOT IN ({POWERHOUSES}, 'West Germany', 'East Germany'))
          )
        GROUP BY t.year
        ORDER BY t.year
        """,
    ),
    (
        "Underdog victories over powerhouses",
        f"""
        SELECT t.year AS tournament,
            CASE LOWER(m.stage_name)
                WHEN 'group stage' THEN 1
                WHEN 'round of 32' THEN 2
                WHEN 'round of 16' THEN 3
                WHEN 'quarter-finals' THEN 4
                WHEN 'semi-finals' THEN 5
                WHEN 'final' THEN 6
                WHEN 'third-place match' THEN 6
                ELSE 0
            END AS upset_stage_rank,
            CASE WHEN m.home_team_win = B'1' THEN home.team_name ELSE away.team_name END AS winning_team,
            CASE WHEN m.home_team_win = B'1' THEN away.team_name ELSE home.team_name END AS losing_team,
            m.score,
            m.stage_name
        FROM matches m
        JOIN tournaments t ON t.tournament_id = m.tournament_id
        JOIN teams home ON home.team_id = m.home_team_id
        JOIN teams away ON away.team_id = m.away_team_id
        WHERE t.tournament_name LIKE '%FIFA Men''s World Cup%'
                    AND t.year BETWEEN 2010 AND 2026
                    AND LOWER(m.stage_name) <> 'third-place match'
                    AND home.team_name <> 'Belgium'
                    AND away.team_name <> 'Belgium'
          AND (
            (m.home_team_win = B'1'
             AND home.team_name NOT IN ({POWERHOUSES}, 'West Germany', 'East Germany')
             AND away.team_name IN ({POWERHOUSES}, 'West Germany', 'East Germany'))
            OR
            (m.away_team_win = B'1'
             AND away.team_name NOT IN ({POWERHOUSES}, 'West Germany', 'East Germany')
             AND home.team_name IN ({POWERHOUSES}, 'West Germany', 'East Germany'))
          )
        ORDER BY t.year, m.match_date
        """,
    ),
    (
        "Underdog deep runs by team",
        f"""
        SELECT team.team_name,
            COUNT(DISTINCT CASE
                WHEN LOWER(m.stage_name) IN ('semi-finals', 'final', 'third-place match')
                THEN m.tournament_id
            END) AS deep_runs
        FROM matches m
        JOIN tournaments t ON t.tournament_id = m.tournament_id
        JOIN teams team ON team.team_id IN (m.home_team_id, m.away_team_id)
        WHERE t.tournament_name LIKE '%FIFA Men''s World Cup%'
          AND team.team_name NOT IN (
              {POWERHOUSES},
              'West Germany', 'East Germany',
              'Czechoslovakia', 'Hungary', 'Yugoslavia', 'Bulgaria', 'Soviet Union'
          )
          AND LOWER(m.stage_name) IN ('semi-finals', 'final', 'third-place match')
        GROUP BY team.team_name
        HAVING COUNT(DISTINCT m.tournament_id) > 0
        ORDER BY deep_runs DESC, team.team_name
        LIMIT 10
        """,
    ),
    (
        "Underdog group-stage advancement rate",
        f"""
        SELECT t.year,
            ROUND(
                100.0 * COUNT(DISTINCT gs.team_id) FILTER (WHERE gs.advanced = B'1')
                / NULLIF(COUNT(DISTINCT gs.team_id), 0),
                1
            ) AS underdog_advancement_rate
        FROM group_standings gs
        JOIN tournaments t ON t.tournament_id = gs.tournament_id
        JOIN teams team ON team.team_id = gs.team_id
        WHERE t.tournament_name LIKE '%FIFA Men''s World Cup%'
          AND team.team_name NOT IN ({POWERHOUSES}, 'West Germany', 'East Germany')
        GROUP BY t.year
        ORDER BY t.year
        """,
    ),
]


def load_human_story_visuals() -> dict:
    results = []
    for purpose, query in HUMAN_STORY_QUERIES:
        columns, rows = run_query_with_columns(query)
        results.append(
            {
                "purpose": purpose,
                "columns": columns,
                "data": [to_json_value(dict(zip(columns, row))) for row in rows],
            }
        )

    charts = build_chart_specs(results, [])
    morocco_chart = charts[3]
    morocco_chart["type"] = "line"
    morocco_chart["x_axis"] = {"data_key": "year", "label": "Year"}
    morocco_chart["y_axis"] = {"label": "Tournament stage", "format": "stage"}
    morocco_chart["series"] = [{
        "data_key": "stage_rank",
        "label": "Morocco progression",
        "color": "#14B8A6",
        "render_as": "line",
    }]

    upset_chart = charts[5]
    upset_chart["type"] = "scatter"
    upset_chart["title"] = "Underdog victories over powerhouses, 2010-2026"
    upset_chart["description"] = "Every FIFA Men's World Cup match from 2010 through 2026 in which an underdog defeated a traditional powerhouse."
    upset_chart["x_axis"] = {"data_key": "tournament", "label": "Tournament year"}
    upset_chart["y_axis"] = {"label": "Stage reached", "format": "stage"}
    upset_chart["series"] = [{
        "data_key": "upset_stage_rank",
        "label": "Upset stage",
        "color": "#F97316",
        "render_as": "line",
    }]

    deep_run_chart = charts[6]
    deep_run_chart["title"] = "Underdog deep runs by team"
    deep_run_chart["description"] = "World Cup semi-final, final, and third-place appearances by teams outside the traditional powerhouse group."

    advancement_chart = charts[7]
    advancement_chart["title"] = "Underdog group-stage advancement rate"
    advancement_chart["description"] = "Percentage of underdog teams advancing from the group stage in each FIFA Men's World Cup."
    advancement_chart["y_axis"] = {"label": "Advancement rate", "format": "percentage"}

    return {
        "queries": [{"purpose": purpose, "sql": query.strip()} for purpose, query in HUMAN_STORY_QUERIES],
        "charts": charts,
    }