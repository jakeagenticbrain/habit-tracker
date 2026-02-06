"""Database migration system for habit tracker."""

import sqlite3
from typing import Callable, List, Tuple


# Current schema version
CURRENT_SCHEMA_VERSION = 2


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


def migration_002(conn: sqlite3.Connection) -> None:
    """Fix habit types: set type='incremental' for multi-count daily habits.

    Updates habits where:
    - type = 'binary'
    - recurrence matches 'N/day' where N > 1

    These should be 'incremental' type to show numbered boxes in habit checker.
    """
    cursor = conn.cursor()

    # Find all habits with type='binary' and recurrence like 'N/day'
    cursor.execute("""
        SELECT id, name, recurrence
        FROM habits
        WHERE type = 'binary'
        AND recurrence LIKE '%/day'
    """)

    habits_to_update = []
    for row in cursor.fetchall():
        habit_id, name, recurrence = row
        # Parse recurrence (e.g., "3/day" -> 3)
        if '/' in recurrence:
            count = int(recurrence.split('/')[0])
            if count > 1:
                habits_to_update.append((habit_id, name, recurrence))

    # Update these habits to type='incremental'
    for habit_id, name, recurrence in habits_to_update:
        cursor.execute("""
            UPDATE habits
            SET type = 'incremental'
            WHERE id = ?
        """, (habit_id,))
        print(f"  - Updated habit '{name}' ({recurrence}) to type='incremental'")

    conn.commit()

    if habits_to_update:
        print(f"  Fixed {len(habits_to_update)} habit(s) to use incremental type")


# List of all migrations (in order)
MIGRATIONS: List[Tuple[int, str, Callable]] = [
    (1, "Initial schema", migration_001),
    (2, "Fix habit types for multi-count daily habits", migration_002),
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
