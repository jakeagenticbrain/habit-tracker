"""Tests for SQLite database interface."""

import pytest
import os
import tempfile
from data.db import Database


@pytest.fixture
def temp_db():
    """Create a temporary database for testing."""
    fd, path = tempfile.mkstemp(suffix='.db')
    os.close(fd)

    db = Database(path)
    yield db

    db.close()
    os.unlink(path)


def test_database_initialization(temp_db):
    """Test that database initializes with correct schema."""
    # Check that tables exist
    cursor = temp_db.conn.cursor()

    # Check habits table
    cursor.execute("""
        SELECT name FROM sqlite_master
        WHERE type='table' AND name='habits'
    """)
    assert cursor.fetchone() is not None

    # Check habit_logs table
    cursor.execute("""
        SELECT name FROM sqlite_master
        WHERE type='table' AND name='habit_logs'
    """)
    assert cursor.fetchone() is not None

    # Check character_state table
    cursor.execute("""
        SELECT name FROM sqlite_master
        WHERE type='table' AND name='character_state'
    """)
    assert cursor.fetchone() is not None


def test_add_habit(temp_db):
    """Test adding a habit to the database."""
    habit_id = temp_db.add_habit(
        name="Gym",
        habit_type="binary",
        points_per=8,
        category="good"
    )

    assert habit_id is not None

    # Verify habit was added
    cursor = temp_db.conn.cursor()
    cursor.execute("SELECT * FROM habits WHERE id = ?", (habit_id,))
    habit = cursor.fetchone()

    assert habit is not None
    assert habit[1] == "Gym"  # name
    assert habit[2] == "binary"  # type
    assert habit[3] == 8  # points_per
    assert habit[4] == "good"  # category


def test_get_all_habits(temp_db):
    """Test retrieving all habits."""
    # Add some habits
    temp_db.add_habit("Gym", "binary", 8, "good")
    temp_db.add_habit("Meditation", "binary", 5, "good")
    temp_db.add_habit("Water", "incremental", 1, "good")

    habits = temp_db.get_all_habits()

    assert len(habits) == 3
    assert habits[0]['name'] == "Gym"
    assert habits[1]['name'] == "Meditation"
    assert habits[2]['name'] == "Water"


def test_save_and_load_character_state(temp_db):
    """Test saving and loading character state."""
    state = {
        'hunger': 75,
        'happiness': 90,
        'last_updated': '2026-01-30T10:30:00'
    }

    temp_db.save_character_state(state)
    loaded_state = temp_db.load_character_state()

    assert loaded_state is not None
    assert loaded_state['hunger'] == 75
    assert loaded_state['happiness'] == 90
    assert loaded_state['last_updated'] == '2026-01-30T10:30:00'


def test_update_habit(temp_db):
    """Test updating an existing habit."""
    # Create initial habit
    habit_id = temp_db.add_habit(
        name="Gym",
        habit_type="binary",
        points_per=8,
        category="good"
    )

    # Update the habit
    temp_db.update_habit(
        habit_id=habit_id,
        name="Gym Updated",
        habit_type="binary",
        points_per=10,
        category="good",
        active=False
    )

    # Verify update
    habits = temp_db.get_all_habits(active_only=False)
    updated = next((h for h in habits if h['id'] == habit_id), None)

    assert updated is not None
    assert updated['name'] == "Gym Updated"
    assert updated['points_per'] == 10
    assert updated['active'] == 0  # SQLite stores bool as int


def test_delete_habit(temp_db):
    """Test deleting a habit."""
    # Create habit
    habit_id = temp_db.add_habit(
        name="Gym",
        habit_type="binary",
        points_per=8,
        category="good"
    )

    # Verify it exists
    habits = temp_db.get_all_habits(active_only=False)
    assert len(habits) == 1

    # Delete it
    temp_db.delete_habit(habit_id)

    # Verify it's gone
    habits = temp_db.get_all_habits(active_only=False)
    assert len(habits) == 0


def test_get_habit_by_id(temp_db):
    """Test retrieving a single habit by ID."""
    # Create habit
    habit_id = temp_db.add_habit(
        name="Meditation",
        habit_type="binary",
        points_per=5,
        category="good"
    )

    # Retrieve by ID
    habit = temp_db.get_habit_by_id(habit_id)

    assert habit is not None
    assert habit['id'] == habit_id
    assert habit['name'] == "Meditation"
    assert habit['points_per'] == 5

    # Test non-existent ID
    missing = temp_db.get_habit_by_id(99999)
    assert missing is None


def test_get_habit_logs(temp_db):
    """Test retrieving habit logs for a date range."""
    # Create habit
    habit_id = temp_db.add_habit(
        name="Water",
        habit_type="incremental",
        points_per=1,
        category="good"
    )

    # Log some completions
    temp_db.log_habit_completion(habit_id, "2026-02-01", completed=True, quantity=3, points_earned=3)
    temp_db.log_habit_completion(habit_id, "2026-02-02", completed=True, quantity=5, points_earned=5)
    temp_db.log_habit_completion(habit_id, "2026-02-03", skipped=True)

    # Get logs for habit
    logs = temp_db.get_habit_logs(habit_id, start_date="2026-02-01", end_date="2026-02-03")

    assert len(logs) == 3
    assert logs[0]['date'] == "2026-02-01"
    assert logs[0]['completed'] == 1
    assert logs[0]['quantity'] == 3
    assert logs[1]['date'] == "2026-02-02"
    assert logs[1]['quantity'] == 5
    assert logs[2]['date'] == "2026-02-03"
    assert logs[2]['skipped'] == 1


def test_get_logs_for_date(temp_db):
    """Test retrieving all habit logs for a specific date."""
    # Create multiple habits
    gym_id = temp_db.add_habit("Gym", "binary", 8, "good")
    water_id = temp_db.add_habit("Water", "incremental", 1, "good")

    # Log completions for same date
    temp_db.log_habit_completion(gym_id, "2026-02-05", completed=True, points_earned=8)
    temp_db.log_habit_completion(water_id, "2026-02-05", completed=True, quantity=6, points_earned=6)

    # Get all logs for date
    logs = temp_db.get_logs_for_date("2026-02-05")

    assert len(logs) == 2
    habit_ids = [log['habit_id'] for log in logs]
    assert gym_id in habit_ids
    assert water_id in habit_ids


def test_get_points_by_day(temp_db):
    """Test getting total points earned per day."""
    # Create habits
    gym_id = temp_db.add_habit("Gym", "binary", 8, "good")
    water_id = temp_db.add_habit("Water", "incremental", 1, "good")

    # Log completions
    temp_db.log_habit_completion(gym_id, "2026-02-01", completed=True, points_earned=8)
    temp_db.log_habit_completion(water_id, "2026-02-01", completed=True, quantity=5, points_earned=5)
    temp_db.log_habit_completion(gym_id, "2026-02-02", completed=True, points_earned=8)
    temp_db.log_habit_completion(water_id, "2026-02-03", completed=True, quantity=3, points_earned=3)

    # Get points by day
    points = temp_db.get_points_by_day(start_date="2026-02-01", end_date="2026-02-03")

    assert len(points) == 3
    assert points[0] == {"date": "2026-02-01", "total_points": 13}
    assert points[1] == {"date": "2026-02-02", "total_points": 8}
    assert points[2] == {"date": "2026-02-03", "total_points": 3}


def test_get_completion_stats(temp_db):
    """Test getting completion stats for all habits in date range."""
    # Create habits
    gym_id = temp_db.add_habit("Gym", "binary", 8, "good")
    water_id = temp_db.add_habit("Water", "incremental", 1, "good")

    # Log completions - gym: 2/3 days, water: 1/3 days
    temp_db.log_habit_completion(gym_id, "2026-02-01", completed=True, points_earned=8)
    temp_db.log_habit_completion(gym_id, "2026-02-02", completed=True, points_earned=8)
    temp_db.log_habit_completion(gym_id, "2026-02-03", skipped=True)
    temp_db.log_habit_completion(water_id, "2026-02-01", completed=True, quantity=5, points_earned=5)
    temp_db.log_habit_completion(water_id, "2026-02-02", skipped=True)

    # Get completion stats
    stats = temp_db.get_completion_stats(start_date="2026-02-01", end_date="2026-02-03")

    assert len(stats) == 2

    gym_stat = next(s for s in stats if s['habit_id'] == gym_id)
    assert gym_stat['habit_name'] == "Gym"
    assert gym_stat['completed_count'] == 2
    assert gym_stat['total_days'] == 3

    water_stat = next(s for s in stats if s['habit_id'] == water_id)
    assert water_stat['habit_name'] == "Water"
    assert water_stat['completed_count'] == 1
    assert water_stat['total_days'] == 2  # Only 2 logs exist
