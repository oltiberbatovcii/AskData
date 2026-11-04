"""Tests for schema introspection, checked against known facts about Chinook."""

from collections.abc import Iterator
from contextlib import closing
from sqlite3 import Connection

import pytest

from app.core.config import get_settings
from app.db.connection import connect_readonly
from app.db.introspect import get_columns, get_foreign_keys, get_schema, list_tables

CHINOOK_TABLES = [
    "Album",
    "Artist",
    "Customer",
    "Employee",
    "Genre",
    "Invoice",
    "InvoiceLine",
    "MediaType",
    "Playlist",
    "PlaylistTrack",
    "Track",
]


@pytest.fixture
def connection() -> Iterator[Connection]:
    with closing(connect_readonly(get_settings().db_path)) as conn:
        yield conn


def test_lists_all_chinook_tables(connection: Connection) -> None:
    assert list_tables(connection) == CHINOOK_TABLES


def test_columns_have_names_types_and_primary_key(connection: Connection) -> None:
    columns = {c.name: c for c in get_columns(connection, "Invoice")}
    assert columns["InvoiceId"].primary_key
    assert columns["InvoiceId"].type == "INTEGER"
    assert not columns["Total"].primary_key
    assert "CustomerId" in columns


def test_composite_primary_key(connection: Connection) -> None:
    # PlaylistTrack's key is made of TWO columns (a link table between Playlist and Track)
    pk_columns = [c.name for c in get_columns(connection, "PlaylistTrack") if c.primary_key]
    assert sorted(pk_columns) == ["PlaylistId", "TrackId"]


def test_foreign_keys(connection: Connection) -> None:
    fks = {(fk.column, fk.ref_table, fk.ref_column) for fk in get_foreign_keys(connection, "Track")}
    assert ("AlbumId", "Album", "AlbumId") in fks
    assert ("GenreId", "Genre", "GenreId") in fks
    assert ("MediaTypeId", "MediaType", "MediaTypeId") in fks


def test_self_referencing_foreign_key(connection: Connection) -> None:
    # Employee.ReportsTo points to another Employee (their manager)
    fks = get_foreign_keys(connection, "Employee")
    assert any(fk.column == "ReportsTo" and fk.ref_table == "Employee" for fk in fks)


def test_get_schema_covers_every_table(connection: Connection) -> None:
    schema = get_schema(connection)
    assert [t.name for t in schema] == CHINOOK_TABLES
    assert all(t.columns for t in schema)  # every table has at least one column
