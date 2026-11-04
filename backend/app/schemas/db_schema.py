"""Models describing the database structure (used by introspection and the /schema endpoint)."""

from pydantic import BaseModel


class ColumnInfo(BaseModel):
    name: str
    type: str  # SQLite declared type, e.g. "INTEGER", "NVARCHAR(40)"
    primary_key: bool
    not_null: bool


class ForeignKey(BaseModel):
    column: str  # column in this table...
    ref_table: str  # ...points to this table...
    ref_column: str  # ...and this column


class TableInfo(BaseModel):
    name: str
    columns: list[ColumnInfo]
    foreign_keys: list[ForeignKey]
