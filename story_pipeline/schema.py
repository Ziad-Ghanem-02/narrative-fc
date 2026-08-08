from story_pipeline.database import run_query


def load_schema() -> dict[str, list[str]]:
    rows = run_query(
        """
        SELECT table_name, column_name, data_type, udt_name
        FROM information_schema.columns
        WHERE table_schema = 'public'
          AND table_name NOT LIKE 'auth_%'
          AND table_name NOT LIKE 'django_%'
        ORDER BY table_name, ordinal_position
        """
    )

    schema: dict[str, list[str]] = {}
    for table_name, column_name, data_type, udt_name in rows:
        schema.setdefault(table_name, []).append(
            f"{column_name} ({data_type}; {udt_name})"
        )

    return schema