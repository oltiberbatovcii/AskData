"""Read the database structure (tables, columns, keys) straight from SQLite.

The LLM can only write correct SQL if it knows the exact table and column names,
so this is the "source of truth" we later feed into the prompt and the RAG index.
"""

import sqlite3

from app.schemas.db_schema import ColumnInfo, ForeignKey, TableInfo


def list_tables(connection: sqlite3.Connection) -> list[str]:
    """Return user table names, sorted. Skips SQLite's internal `sqlite_*` tables."""
    rows = connection.execute(
        "SELECT name FROM sqlite_master "
        "WHERE type = 'table' AND name NOT LIKE 'sqlite_%' ORDER BY name"
    ).fetchall()
    return [row[0] for row in rows]


def get_columns(connection: sqlite3.Connection, table: str) -> list[ColumnInfo]:
    """Return the columns of one table, in their defined order."""
    # pragma_table_info(?) is the function form of PRAGMA table_info, so the table
    # name is passed as a parameter instead of being pasted into the SQL string.
    rows = connection.execute(
        'SELECT name, type, pk, "notnull" FROM pragma_table_info(?) ORDER BY cid', (table,)
    ).fetchall()
    return [
        ColumnInfo(name=name, type=col_type, primary_key=pk > 0, not_null=bool(not_null))
        for name, col_type, pk, not_null in rows
    ]


def get_foreign_keys(connection: sqlite3.Connection, table: str) -> list[ForeignKey]:
    """Return the foreign keys of one table (which column points to which table.column)."""
    rows = connection.execute(
        'SELECT "from", "table", "to" FROM pragma_foreign_key_list(?) ORDER BY id, seq', (table,)
    ).fetchall()
    return [
        ForeignKey(column=column, ref_table=ref_table, ref_column=ref_column)
        for column, ref_table, ref_column in rows
    ]


def get_schema(connection: sqlite3.Connection) -> list[TableInfo]:
    """Return the full schema: every table with its columns and foreign keys."""
    return [
        TableInfo(
            name=table,
            columns=get_columns(connection, table),
            foreign_keys=get_foreign_keys(connection, table),
        )
        for table in list_tables(connection)
    ]
