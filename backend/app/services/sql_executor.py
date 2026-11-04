"""Run a SQL query with a row limit and a time limit.

Limits protect the app from queries that are valid but too big or too slow,
e.g. an LLM forgetting a JOIN condition and producing millions of rows.
"""

import sqlite3
import time
from contextlib import closing

from app.core.config import Settings
from app.db.connection import connect_readonly
from app.schemas.query import QueryResult

# SQLite calls our progress handler every N internal instructions. Small enough to
# stop a runaway query quickly, large enough that the check itself costs nothing.
PROGRESS_CHECK_EVERY = 1_000


class QueryTimeoutError(Exception):
    """The query ran longer than the allowed time and was stopped."""


def execute_query(
    connection: sqlite3.Connection, sql: str, row_limit: int, timeout_seconds: float
) -> QueryResult:
    """Run `sql` on `connection`, returning at most `row_limit` rows within `timeout_seconds`."""
    deadline = time.monotonic() + timeout_seconds

    def stop_if_too_slow() -> int:
        # Returning non-zero tells SQLite to abort the query ("interrupted").
        return 1 if time.monotonic() > deadline else 0

    connection.set_progress_handler(stop_if_too_slow, PROGRESS_CHECK_EVERY)
    try:
        cursor = connection.execute(sql)
        columns = [description[0] for description in cursor.description or []]
        # Fetch ONE extra row: if it exists, we know the result was cut off,
        # without ever loading the full (possibly huge) result into memory.
        rows = cursor.fetchmany(row_limit + 1)
    except sqlite3.OperationalError as error:
        if "interrupted" in str(error):
            raise QueryTimeoutError(f"Query took longer than {timeout_seconds} seconds") from error
        raise
    finally:
        connection.set_progress_handler(None, 0)  # remove the handler so it can't leak

    truncated = len(rows) > row_limit
    rows = rows[:row_limit]
    return QueryResult(
        columns=columns,
        rows=[list(row) for row in rows],
        row_count=len(rows),
        truncated=truncated,
    )


def run_query(sql: str, settings: Settings) -> QueryResult:
    """Open a read-only connection, run the query with the configured limits, close it."""
    with closing(connect_readonly(settings.db_path)) as connection:
        return execute_query(
            connection,
            sql,
            row_limit=settings.row_limit,
            timeout_seconds=settings.query_timeout_seconds,
        )
