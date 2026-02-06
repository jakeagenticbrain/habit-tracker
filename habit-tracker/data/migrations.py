"""Database migration system for habit tracker."""

import sqlite3
from typing import Callable, List, Tuple


# Current schema version
CURRENT_SCHEMA_VERSION = 1


def get_schema_version(conn: sqlite3.Connection) -> int:
    """Get current schema version from database.

    Args:
        conn: SQLite connection

    Returns:
        Current schema version (0 if table doesn't exist)
    """
    cursor = conn.cursor()

    # Create schema_version table if it doesn't exist
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS schema_version (
            version INTEGER PRIMARY KEY,
            applied_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Get current version
    cursor.execute("SELECT MAX(version) FROM schema_version")
    result = cursor.fetchone()
    version = result[0] if result[0] is not None else 0

    return version


def set_schema_version(conn: sqlite3.Connection, version: int) -> None:
    """Set schema version in database.

    Args:
        conn: SQLite connection
        version: Schema version to set
    """
    cursor = conn.cursor()
    cursor.execute(
        "INSERT OR REPLACE INTO schema_version (version) VALUES (?)",
        (version,)
    )
    conn.commit()


# Migration functions - add new ones as schema changes
def migration_001(conn: sqlite3.Connection) -> None:
    """Initial schema version - no changes needed.

    This is just a placeholder to set version 1.
    """
    pass


# Example future migration:
# def migration_002(conn: sqlite3.Connection) -> None:
#     """Add reminder_enabled column to habits table."""
#     cursor = conn.cursor()
#     cursor.execute("""
#         ALTER TABLE habits
#         ADD COLUMN reminder_enabled INTEGER DEFAULT 0
#     """)
#     conn.commit()


# List of all migrations (in order)
MIGRATIONS: List[Tuple[int, str, Callable]] = [
    (1, "Initial schema", migration_001),
    # Add new migrations here as tuples: (version, description, function)
    # (2, "Add reminder_enabled column", migration_002),
]


def run_migrations(conn: sqlite3.Connection) -> List[str]:
    """Run all pending migrations.

    Args:
        conn: SQLite connection

    Returns:
        List of applied migration descriptions
    """
    current_version = get_schema_version(conn)
    applied = []

    for version, description, migration_func in MIGRATIONS:
        if version > current_version:
            print(f"Applying migration {version}: {description}")
            migration_func(conn)
            set_schema_version(conn, version)
            applied.append(f"v{version}: {description}")

    return applied


def check_and_migrate(conn: sqlite3.Connection) -> None:
    """Check schema version and run migrations if needed.

    Args:
        conn: SQLite connection
    """
    current_version = get_schema_version(conn)

    if current_version < CURRENT_SCHEMA_VERSION:
        print(f"Database schema outdated (v{current_version}), migrating to v{CURRENT_SCHEMA_VERSION}...")
        applied = run_migrations(conn)
        if applied:
            print(f"Applied {len(applied)} migration(s):")
            for migration in applied:
                print(f"  - {migration}")
        print("Database migration complete!")
    elif current_version > CURRENT_SCHEMA_VERSION:
        print(f"WARNING: Database schema version (v{current_version}) is newer than app version (v{CURRENT_SCHEMA_VERSION})")
        print("You may need to update the application.")
