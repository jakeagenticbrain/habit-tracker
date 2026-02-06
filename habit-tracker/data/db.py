"""SQLite database interface for habit tracker."""

import sqlite3
import json
from typing import Optional, List, Dict, Any
from datetime import datetime
from data.migrations import check_and_migrate


class Database:
    """SQLite database wrapper for habit tracking data."""

    def __init__(self, db_path: str = "habit_tracker.db"):
        """Initialize database connection and create schema.

        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row
        self._create_schema()
        # Run any pending migrations
        check_and_migrate(self.conn)

    def _create_schema(self) -> None:
        """Create database tables if they don't exist."""
        cursor = self.conn.cursor()

        # Habits table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS habits (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                type TEXT NOT NULL,
                points_per INTEGER NOT NULL,
                category TEXT NOT NULL,
                target_time TEXT,
                grace_period INTEGER DEFAULT 60,
                recurrence TEXT DEFAULT 'daily',
                active INTEGER DEFAULT 1,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Habit completion logs
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS habit_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                habit_id INTEGER NOT NULL,
                date TEXT NOT NULL,
                completed INTEGER DEFAULT 0,
                skipped INTEGER DEFAULT 0,
                quantity INTEGER DEFAULT 0,
                points_earned INTEGER DEFAULT 0,
                logged_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (habit_id) REFERENCES habits (id),
                UNIQUE(habit_id, date)
            )
        """)

        # Character state
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS character_state (
                id INTEGER PRIMARY KEY CHECK (id = 1),
                state_json TEXT NOT NULL,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

        self.conn.commit()

    def add_habit(
        self,
        name: str,
        habit_type: str,
        points_per: int,
        category: str,
        target_time: Optional[str] = None,
        grace_period: int = 60,
        recurrence: str = "daily"
    ) -> int:
        """Add a new habit to the database.

        Args:
            name: Habit name
            habit_type: 'binary' or 'incremental'
            points_per: Points awarded per completion/unit
            category: 'good' or 'bad'
            target_time: Target time for habit (e.g., '09:00')
            grace_period: Grace period in minutes before reminder
            recurrence: Recurrence pattern (default 'daily')

        Returns:
            ID of the created habit
        """
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO habits (name, type, points_per, category, target_time, grace_period, recurrence)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (name, habit_type, points_per, category, target_time, grace_period, recurrence))

        self.conn.commit()
        habit_id = cursor.lastrowid
        print(f"[DEBUG] Database.add_habit: Created habit ID {habit_id} (name='{name}', active should default to 1)")
        return habit_id

    def update_habit(
        self,
        habit_id: int,
        name: str,
        habit_type: str,
        points_per: int,
        category: str,
        target_time: Optional[str] = None,
        grace_period: int = 60,
        recurrence: str = "daily",
        active: bool = True
    ) -> None:
        """Update an existing habit.

        Args:
            habit_id: ID of habit to update
            name: Habit name
            habit_type: 'binary' or 'incremental'
            points_per: Points awarded per completion/unit
            category: 'good' or 'bad'
            target_time: Target time for habit (e.g., '09:00')
            grace_period: Grace period in minutes before reminder
            recurrence: Recurrence pattern (e.g., '3/day', '4/week', 'daily')
            active: Whether habit is active
        """
        cursor = self.conn.cursor()
        cursor.execute("""
            UPDATE habits
            SET name = ?, type = ?, points_per = ?, category = ?,
                target_time = ?, grace_period = ?, recurrence = ?, active = ?
            WHERE id = ?
        """, (name, habit_type, points_per, category, target_time, grace_period, recurrence, int(active), habit_id))

        self.conn.commit()

    def delete_habit(self, habit_id: int) -> None:
        """Delete a habit and its associated logs.

        Args:
            habit_id: ID of habit to delete
        """
        cursor = self.conn.cursor()

        # Delete associated logs first (foreign key constraint)
        cursor.execute("DELETE FROM habit_logs WHERE habit_id = ?", (habit_id,))

        # Delete the habit
        cursor.execute("DELETE FROM habits WHERE id = ?", (habit_id,))

        self.conn.commit()

    def get_all_habits(self, active_only: bool = True) -> List[Dict[str, Any]]:
        """Get all habits from the database.

        Args:
            active_only: Only return active habits (default True)

        Returns:
            List of habit dictionaries
        """
        cursor = self.conn.cursor()

        if active_only:
            cursor.execute("SELECT * FROM habits WHERE active = 1 ORDER BY created_at")
        else:
            cursor.execute("SELECT * FROM habits ORDER BY created_at")

        rows = cursor.fetchall()
        habits = [dict(row) for row in rows]
        print(f"[DEBUG] Database.get_all_habits(active_only={active_only}): Returning {len(habits)} habits")
        return habits

    def get_habit_by_id(self, habit_id: int) -> Optional[Dict[str, Any]]:
        """Get a single habit by ID.

        Args:
            habit_id: ID of habit to retrieve

        Returns:
            Habit dictionary or None if not found
        """
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM habits WHERE id = ?", (habit_id,))

        row = cursor.fetchone()
        if row is None:
            return None

        return dict(row)

    def save_character_state(self, state: Dict[str, Any]) -> None:
        """Save character state to database.

        Args:
            state: Character state dictionary
        """
        state_json = json.dumps(state)
        cursor = self.conn.cursor()

        cursor.execute("""
            INSERT OR REPLACE INTO character_state (id, state_json, updated_at)
            VALUES (1, ?, CURRENT_TIMESTAMP)
        """, (state_json,))

        self.conn.commit()

    def load_character_state(self) -> Optional[Dict[str, Any]]:
        """Load character state from database.

        Returns:
            Character state dictionary or None if not found
        """
        cursor = self.conn.cursor()
        cursor.execute("SELECT state_json FROM character_state WHERE id = 1")

        row = cursor.fetchone()
        if row is None:
            return None

        return json.loads(row[0])

    def log_habit_completion(
        self,
        habit_id: int,
        date: str,
        completed: bool = False,
        skipped: bool = False,
        quantity: int = 0,
        points_earned: int = 0
    ) -> None:
        """Log a habit completion or skip.

        Args:
            habit_id: ID of the habit
            date: Date string (YYYY-MM-DD)
            completed: Whether habit was completed
            skipped: Whether habit was skipped
            quantity: Quantity for incremental habits
            points_earned: Points earned from this completion
        """
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO habit_logs
            (habit_id, date, completed, skipped, quantity, points_earned, logged_at)
            VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        """, (habit_id, date, int(completed), int(skipped), quantity, points_earned))

        self.conn.commit()

    def get_habit_logs(
        self,
        habit_id: int,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get habit logs for a date range.

        Args:
            habit_id: ID of habit
            start_date: Start date (YYYY-MM-DD) or None for all
            end_date: End date (YYYY-MM-DD) or None for all

        Returns:
            List of log dictionaries ordered by date
        """
        cursor = self.conn.cursor()

        if start_date and end_date:
            cursor.execute("""
                SELECT * FROM habit_logs
                WHERE habit_id = ? AND date >= ? AND date <= ?
                ORDER BY date
            """, (habit_id, start_date, end_date))
        elif start_date:
            cursor.execute("""
                SELECT * FROM habit_logs
                WHERE habit_id = ? AND date >= ?
                ORDER BY date
            """, (habit_id, start_date))
        elif end_date:
            cursor.execute("""
                SELECT * FROM habit_logs
                WHERE habit_id = ? AND date <= ?
                ORDER BY date
            """, (habit_id, end_date))
        else:
            cursor.execute("""
                SELECT * FROM habit_logs
                WHERE habit_id = ?
                ORDER BY date
            """, (habit_id,))

        rows = cursor.fetchall()
        return [dict(row) for row in rows]

    def get_logs_for_date(self, date: str) -> List[Dict[str, Any]]:
        """Get all habit logs for a specific date.

        Args:
            date: Date string (YYYY-MM-DD)

        Returns:
            List of log dictionaries for that date
        """
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT * FROM habit_logs
            WHERE date = ?
            ORDER BY habit_id
        """, (date,))

        rows = cursor.fetchall()
        return [dict(row) for row in rows]

    def get_points_by_day(
        self,
        start_date: str,
        end_date: str
    ) -> List[Dict[str, Any]]:
        """Get total points earned per day in date range.

        Args:
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)

        Returns:
            List of dicts with 'date' and 'total_points' keys
        """
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT date, SUM(points_earned) as total_points
            FROM habit_logs
            WHERE date >= ? AND date <= ?
            GROUP BY date
            ORDER BY date
        """, (start_date, end_date))

        rows = cursor.fetchall()
        return [{"date": row[0], "total_points": row[1]} for row in rows]

    def get_completion_stats(
        self,
        start_date: str,
        end_date: str
    ) -> List[Dict[str, Any]]:
        """Get completion statistics per habit for date range.

        Args:
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)

        Returns:
            List of dicts with habit_id, habit_name, completed_count, total_days
        """
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT
                h.id as habit_id,
                h.name as habit_name,
                SUM(CASE WHEN hl.completed = 1 THEN 1 ELSE 0 END) as completed_count,
                COUNT(*) as total_days
            FROM habits h
            LEFT JOIN habit_logs hl ON h.id = hl.habit_id
            WHERE hl.date >= ? AND hl.date <= ?
            GROUP BY h.id, h.name
            ORDER BY h.name
        """, (start_date, end_date))

        rows = cursor.fetchall()
        return [dict(row) for row in rows]

    def close(self) -> None:
        """Close database connection."""
        self.conn.close()
