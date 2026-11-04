"""Tests for the read-only database connection."""

import sqlite3
from contextlib import closing
from pathlib import Path

import pytest

from app.core.config import get_settings
from app.db.connection import connect_readonly

DB_PATH = get_settings().db_path


def test_can_read() -> None:
    with closing(connect_readonly(DB_PATH)) as connection:
        count = connection.execute("SELECT COUNT(*) FROM Customer").fetchone()[0]
    assert count == 59


@pytest.mark.parametrize(
    "write_sql",
    [
        "DELETE FROM Customer",
        "UPDATE Customer SET FirstName = 'Hacked'",
        "INSERT INTO Genre (GenreId, Name) VALUES (999, 'Test')",
        "DROP TABLE Customer",
        "CREATE TABLE Evil (id INTEGER)",
    ],
)
def test_writes_are_blocked(write_sql: str) -> None:
    with closing(connect_readonly(DB_PATH)) as connection, pytest.raises(sqlite3.OperationalError):
        connection.execute(write_sql)


def test_query_only_pragma_is_on() -> None:
    with closing(connect_readonly(DB_PATH)) as connection:
        assert connection.execute("PRAGMA query_only").fetchone()[0] == 1


def test_missing_file_gives_clear_error(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError, match="Database file not found"):
        connect_readonly(tmp_path / "nope.sqlite")


def test_missing_file_is_not_created(tmp_path: Path) -> None:
    # A normal sqlite3.connect() would silently create an empty DB file here.
    missing = tmp_path / "nope.sqlite"
    with pytest.raises(FileNotFoundError):
        connect_readonly(missing)
    assert not missing.exists()
