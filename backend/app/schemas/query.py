"""Models for query results."""

from typing import Any

from pydantic import BaseModel


class QueryResult(BaseModel):
    columns: list[str]
    rows: list[list[Any]]  # Any: SQLite values can be int, float, str or None
    row_count: int  # rows returned (after the limit was applied)
    truncated: bool  # True if the query had more rows than the limit
