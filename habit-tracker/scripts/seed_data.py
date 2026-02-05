"""Seed database with sample habits and logs for testing."""

import sys
from pathlib import Path
from datetime import datetime, timedelta

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from data.db import Database


def seed_database(db_path: str = "habit_tracker.db"):
    """Seed database with sample data."""
    db = Database(db_path)

    print("Seeding database with sample data...")

    # Add sample habits
    gym_id = db.add_habit(
        name="GYM",
        habit_type="binary",
        points_per=8,
        category="good",
        recurrence="4/week"
    )
    print(f"Added habit: GYM (id={gym_id})")

    water_id = db.add_habit(
        name="WATER",
        habit_type="incremental",
        points_per=1,
        category="good",
        recurrence="8/day"
    )
    print(f"Added habit: WATER (id={water_id})")

    vitamins_id = db.add_habit(
        name="VITAMINS",
        habit_type="binary",
        points_per=2,
        category="good",
        recurrence="1/day"
    )
    print(f"Added habit: VITAMINS (id={vitamins_id})")

    meditation_id = db.add_habit(
        name="MEDITATE",
        habit_type="binary",
        points_per=5,
        category="good",
        recurrence="1/day"
    )
    print(f"Added habit: MEDITATE (id={meditation_id})")

    # Add logs for past 7 days
    today = datetime.now()

    for i in range(7):
        date = (today - timedelta(days=i)).strftime("%Y-%m-%d")

        # Gym: completed 4/7 days
        if i % 2 == 0:
            db.log_habit_completion(gym_id, date, completed=True, points_earned=8)

        # Water: completed daily with varying amounts
        quantity = 5 + (i % 3)
        db.log_habit_completion(water_id, date, completed=True, quantity=quantity, points_earned=quantity)

        # Vitamins: missed 2 days
        if i not in [1, 4]:
            db.log_habit_completion(vitamins_id, date, completed=True, points_earned=2)

        # Meditation: completed 5/7 days
        if i not in [2, 5]:
            db.log_habit_completion(meditation_id, date, completed=True, points_earned=5)

    print(f"Added 7 days of logs for {4} habits")
    print("Database seeded successfully!")

    db.close()


if __name__ == "__main__":
    seed_database()
