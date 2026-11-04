"""Tests for the SQL executor: results, row limit, time limit."""

import sqlite3
import time
from collections.abc import Iterator
from contextlib import closing

import pytest

from app.core.config import Settings, get_settings
from app.db.connection import connect_readonly
from app.services.sql_executor import QueryTimeoutError, execute_query, run_query

# A query that never ends on its own: it counts upwards forever.
ENDLESS_QUERY = """
WITH RECURSIVE counter(n) AS (SELECT 1 UNION ALL SELECT n + 1 FROM counter)
SELECT COUNT(*) FROM counter
"""


@pytest.fixture
def connection() -> Iterator[sqlite3.Connection]:
    with closing(connect_readonly(get_settings().db_path)) as conn:
        yield conn


def test_returns_columns_and_rows(connection: sqlite3.Connection) -> None:
    result = execute_query(
        connection, "SELECT GenreId, Name FROM Genre ORDER BY GenreId LIMIT 2", 100, 5
    )
    assert result.columns == ["GenreId", "Name"]
    assert result.rows == [[1, "Rock"], [2, "Jazz"]]
    assert result.row_count == 2
    assert not result.truncated


def test_row_limit_truncates(connection: sqlite3.Connection) -> None:
    result = execute_query(connection, "SELECT * FROM Track", row_limit=10, timeout_seconds=5)
    assert result.row_count == 10
    assert result.truncated  # Track has 3503 rows


def test_exactly_at_limit_is_not_truncated(connection: sqlite3.Connection) -> None:
    result = execute_query(connection, "SELECT * FROM Genre", row_limit=25, timeout_seconds=5)
    assert result.row_count == 25  # Genre has exactly 25 rows
    assert not result.truncated


def test_empty_result(connection: sqlite3.Connection) -> None:
    result = execute_query(connection, "SELECT * FROM Genre WHERE 1 = 0", 100, 5)
    assert result.rows == []
    assert result.columns  # column names are still known
    assert not result.truncated


def test_slow_query_is_stopped(connection: sqlite3.Connection) -> None:
    start = time.monotonic()
    with pytest.raises(QueryTimeoutError):
        execute_query(connection, ENDLESS_QUERY, row_limit=100, timeout_seconds=0.2)
    assert time.monotonic() - start < 2  # stopped quickly, didn't run forever


def test_connection_still_works_after_timeout(connection: sqlite3.Connection) -> None:
    with pytest.raises(QueryTimeoutError):
        execute_query(connection, ENDLESS_QUERY, row_limit=100, timeout_seconds=0.1)
    result = execute_query(connection, "SELECT COUNT(*) FROM Genre", 100, 5)
    assert result.rows == [[25]]


def test_sql_error_is_raised(connection: sqlite3.Connection) -> None:
    with pytest.raises(sqlite3.OperationalError, match="no such table"):
        execute_query(connection, "SELECT * FROM NotATable", 100, 5)


def test_run_query_uses_settings() -> None:
    settings = Settings(_env_file=None, row_limit=3)
    result = run_query("SELECT * FROM Customer", settings)
    assert result.row_count == 3
    assert result.truncated
