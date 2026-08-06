import sqlite3

DATABASE_PATH = "database/worldcup.db"


def run_query(query: str):
    conn = sqlite3.connect(DATABASE_PATH)

    cursor = conn.cursor()

    cursor.execute(query)

    results = cursor.fetchall()

    conn.close()

    return results