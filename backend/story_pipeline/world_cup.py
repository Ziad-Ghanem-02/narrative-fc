from story_pipeline.database import run_query_with_columns
from story_pipeline.serialization import to_json_value


MAP_SUMMARY_QUERY = """
WITH mens_world_cup_tournaments AS (
    SELECT tournament_id
    FROM tournaments
    WHERE tournament_name LIKE '%FIFA Men''s World Cup%'
),
team_stats AS (
    SELECT
        team_id,
        COUNT(DISTINCT match_id) AS matches,
        COUNT(*) FILTER (WHERE win = B'1') AS wins,
        COUNT(*) FILTER (WHERE draw = B'1') AS draws,
        COUNT(*) FILTER (WHERE lose = B'1') AS losses
    FROM team_appearances
    WHERE tournament_id IN (
        SELECT tournament_id FROM mens_world_cup_tournaments
    )
    GROUP BY team_id
),
peak_results AS (
    SELECT team_id, MIN(position) AS best_position
    FROM tournament_standings
    WHERE tournament_id IN (
        SELECT tournament_id FROM mens_world_cup_tournaments
    )
    GROUP BY team_id
),
peak_match_stages AS (
    SELECT
        team_appearances.team_id,
        MAX(
            CASE LOWER(matches.stage_name)
                WHEN 'final' THEN 6
                WHEN 'semi-finals' THEN 5
                WHEN 'third place match' THEN 5
                WHEN 'quarter-finals' THEN 4
                WHEN 'round of 16' THEN 3
                WHEN 'round of 32' THEN 2
                ELSE 1
            END
        ) AS best_stage_rank
    FROM team_appearances
    JOIN matches ON matches.match_id = team_appearances.match_id
    WHERE team_appearances.tournament_id IN (
        SELECT tournament_id FROM mens_world_cup_tournaments
    )
    GROUP BY team_appearances.team_id
)
SELECT
    teams.team_name AS name,
    COALESCE(team_stats.wins, 0) AS wins,
    COALESCE(team_stats.draws, 0) AS draws,
    COALESCE(team_stats.losses, 0) AS losses,
    COALESCE(team_stats.matches, 0) AS matches,
    CASE
        WHEN peak_results.best_position = 1 THEN 'Champions'
        WHEN peak_results.best_position = 2 THEN 'Runners-up'
        WHEN peak_results.best_position = 3 THEN 'Third place'
        WHEN peak_results.best_position = 4 THEN 'Fourth place'
        WHEN peak_match_stages.best_stage_rank = 6 THEN 'Finalists'
        WHEN peak_match_stages.best_stage_rank = 5 THEN 'Semi-finals'
        WHEN peak_match_stages.best_stage_rank = 4 THEN 'Quarter-finals'
        WHEN peak_match_stages.best_stage_rank = 3 THEN 'Round of 16'
        WHEN peak_match_stages.best_stage_rank = 2 THEN 'Round of 32'
        WHEN peak_match_stages.best_stage_rank = 1 THEN 'Group stage'
        ELSE 'Did not qualify'
    END AS peak_stage,
    COALESCE(confederations.confederation_name, 'N/A') AS confederation
FROM teams
LEFT JOIN team_stats ON team_stats.team_id = teams.team_id
LEFT JOIN peak_results ON peak_results.team_id = teams.team_id
LEFT JOIN peak_match_stages ON peak_match_stages.team_id = teams.team_id
LEFT JOIN confederations ON confederations.confederation_id = teams.confederation_id
WHERE teams.mens_team = B'1'
ORDER BY teams.team_name
"""


def load_map_summary() -> list[dict]:
    columns, rows = run_query_with_columns(MAP_SUMMARY_QUERY)
    return [
        to_json_value(dict(zip(columns, row)))
        for row in rows
    ]
