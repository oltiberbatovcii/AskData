"""Read-only SQLite connection. The ONLY way the app should open the database."""

import sqlite3
from pathlib import Path


def connect_readonly(db_path: Path) -> sqlite3.Connection:
    """Open the database so that nothing can be written, even by a buggy or malicious query.

    Two independent safety layers (defense in depth):
    1. `mode=ro` in the URI: SQLite opens the FILE read-only, so writes fail at the file level.
    2. `PRAGMA query_only = ON`: SQLite refuses any statement that would change data.
    """
    # Without this check, a wrong path gives SQLite's vague "unable to open database file".
    if not db_path.is_file():
        raise FileNotFoundError(f"Database file not found: {db_path}")

    # as_uri() turns C:\...\chinook.sqlite into file:///C:/.../chinook.sqlite (works on any OS)
    uri = f"{db_path.resolve().as_uri()}?mode=ro"
    connection = sqlite3.connect(uri, uri=True)
    connection.execute("PRAGMA query_only = ON")
    return connection
