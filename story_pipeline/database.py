import os
import re
from pathlib import Path

import psycopg
from dotenv import load_dotenv


load_dotenv(Path(__file__).resolve().parents[1] / ".env")

_READ_ONLY_QUERY = re.compile(r"^\s*(?:SELECT|WITH)\b", re.IGNORECASE)


def _database_url() -> str:
    try:
        return os.environ["DATABASE_URL"]
    except KeyError as error:
        raise RuntimeError("DATABASE_URL must be configured.") from error


def _validate_query(query: str) -> str:
    normalized_query = query.strip()
    if normalized_query.endswith(";"):
        normalized_query = normalized_query[:-1].rstrip()

    if not normalized_query or ";" in normalized_query:
        raise ValueError("Queries must contain exactly one PostgreSQL SELECT or WITH statement.")
    if not _READ_ONLY_QUERY.match(normalized_query):
        raise ValueError("Only read-only PostgreSQL SELECT or WITH statements are allowed.")

    return normalized_query


def run_query_with_columns(query: str) -> tuple[list[str], list[tuple]]:
    """Run one read-only query against the configured Neon PostgreSQL database."""
    normalized_query = _validate_query(query)

    with psycopg.connect(_database_url()) as connection:
        with connection.cursor() as cursor:
            cursor.execute("SET TRANSACTION READ ONLY")
            cursor.execute(normalized_query)
            columns = [column.name for column in cursor.description]
            return columns, cursor.fetchall()


def run_query(query: str) -> list[tuple]:
    """Run one read-only query and return its rows."""
    _, rows = run_query_with_columns(query)
    return rows