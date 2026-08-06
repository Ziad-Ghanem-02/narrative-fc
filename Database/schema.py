from Database.db import run_query


def load_schema():

    tables = run_query("""
        SELECT name
        FROM sqlite_master
        WHERE type='table';
    """)

    schema = {}

    for table in tables:

        table_name = table[0]

        columns = run_query(
            f"PRAGMA table_info({table_name});"
        )

        schema[table_name] = [
            column[1] for column in columns
        ]

    return schema