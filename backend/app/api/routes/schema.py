"""Schema endpoint: shows the database structure (the frontend sidebar will use this)."""

from contextlib import closing
from typing import Annotated

from fastapi import APIRouter, Depends

from app.core.config import Settings, get_settings
from app.db.connection import connect_readonly
from app.db.introspect import get_schema
from app.schemas.db_schema import TableInfo

router = APIRouter(tags=["schema"])


@router.get("/schema")
def read_schema(settings: Annotated[Settings, Depends(get_settings)]) -> list[TableInfo]:
    """List every table with its columns and foreign keys."""
    with closing(connect_readonly(settings.db_path)) as connection:
        return get_schema(connection)
