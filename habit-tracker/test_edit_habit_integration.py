#!/usr/bin/env python3
"""Integration test for EditHabitScreen save functionality."""

import os
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from PIL import Image
from data.db import Database
from game.edit_habit_screen import EditHabitScreen
from input.input_base import InputEvent, InputType

def test_save_button_functionality():
    """Test that save button functionality works end-to-end."""
    # Create test database
    test_db_path = "test_edit_habit.db"
    if os.path.exists(test_db_path):
        os.remove(test_db_path)

    db = Database(test_db_path)

    try:
        # Create screen for new habit
        screen = EditHabitScreen(db, habit_data=None)

        # Simulate entering name
        screen.editing_name = True
        screen.text_input.activate()
        screen.text_input.value = "TEST HABIT"
        screen.name = "TEST HABIT"
        screen.editing_name = False
        screen.text_input.deactivate()

        # Navigate to save button (press DOWN 6 times to reach buttons)
        print("Navigating to save button...")
        for i in range(6):
            result = screen.handle_input(InputEvent(InputType.DOWN, True))
            print(f"  DOWN press {i+1}: selected_field={screen.selected_field}, selected_button={screen.selected_button}")
            assert result is None, f"Unexpected navigation on DOWN {i+1}"

        # Verify we're on save button
        assert screen.selected_button == "save", f"Expected save button, got: {screen.selected_button}"
        assert screen.selected_field == -1, f"Expected field -1, got: {screen.selected_field}"
        print("✓ Successfully navigated to save button")

        # Test LEFT/RIGHT navigation between buttons
        print("\nTesting button navigation...")
        result = screen.handle_input(InputEvent(InputType.LEFT, True))
        assert result is None, "LEFT should not navigate away"
        assert screen.selected_button == "cancel", f"Expected cancel button, got: {screen.selected_button}"
        print("  LEFT: switched to cancel button")

        result = screen.handle_input(InputEvent(InputType.RIGHT, True))
        assert result is None, "RIGHT should not navigate away"
        assert screen.selected_button == "save", f"Expected save button, got: {screen.selected_button}"
        print("  RIGHT: switched back to save button")
        print("✓ Button navigation works")

        # Test cancel button
        print("\nTesting cancel button...")
        screen.handle_input(InputEvent(InputType.LEFT, True))  # Switch to cancel
        result = screen.handle_input(InputEvent(InputType.BUTTON_A, True))
        assert result == "view_habits", f"Expected view_habits, got: {result}"

        # Verify no habit was saved
        habits = db.get_all_habits()
        assert len(habits) == 0, f"Expected 0 habits after cancel, got: {len(habits)}"
        print("✓ Cancel button works (no habit saved)")

        # Reset screen for save test
        screen = EditHabitScreen(db, habit_data=None)
        screen.name = "TEST HABIT"

        # Navigate to save button again
        for i in range(6):
            screen.handle_input(InputEvent(InputType.DOWN, True))

        # Test save button
        print("\nTesting save button...")
        result = screen.handle_input(InputEvent(InputType.BUTTON_A, True))
        assert result == "view_habits", f"Expected view_habits, got: {result}"

        # Verify habit was saved
        habits = db.get_all_habits()
        assert len(habits) == 1, f"Expected 1 habit after save, got: {len(habits)}"

        habit = habits[0]
        assert habit['name'] == "TEST HABIT", f"Expected 'TEST HABIT', got: {habit['name']}"
        assert habit['points_per'] == 5, f"Expected 5 points, got: {habit['points_per']}"
        assert habit['recurrence'] == "1/day", f"Expected '1/day', got: {habit['recurrence']}"
        assert habit['category'] == "good", f"Expected 'good', got: {habit['category']}"
        assert habit['active'] == 1, f"Expected active=1, got: {habit['active']}"
        print("✓ Save button works (habit saved to database)")
        print(f"  Saved habit: name={habit['name']}, points={habit['points_per']}, freq={habit['recurrence']}")

        # Test UP navigation from buttons back to fields
        print("\nTesting UP navigation from buttons...")
        screen = EditHabitScreen(db, habit_data=None)
        # Navigate to buttons
        for i in range(6):
            screen.handle_input(InputEvent(InputType.DOWN, True))

        assert screen.selected_button == "save", "Should be on save button"

        # Press UP to go back to fields
        screen.handle_input(InputEvent(InputType.UP, True))
        assert screen.selected_button is None, f"Expected no button selected, got: {screen.selected_button}"
        assert screen.selected_field == 5, f"Expected field 5 (Reminder), got: {screen.selected_field}"
        print("✓ UP from buttons returns to last field")

        # Test that save validates name is not empty
        print("\nTesting save validation (empty name)...")
        screen = EditHabitScreen(db, habit_data=None)
        screen.name = ""  # Empty name

        # Navigate to save button
        for i in range(6):
            screen.handle_input(InputEvent(InputType.DOWN, True))

        # Try to save
        result = screen.handle_input(InputEvent(InputType.BUTTON_A, True))
        assert result is None, "Save with empty name should not navigate away"

        # Verify no new habit was added (still just 1 from before)
        habits = db.get_all_habits()
        assert len(habits) == 1, f"Expected 1 habit (no new habit with empty name), got: {len(habits)}"
        print("✓ Save validation prevents saving with empty name")

        print("\n" + "="*60)
        print("ALL TESTS PASSED!")
        print("="*60)

    finally:
        # Cleanup
        db.close()
        if os.path.exists(test_db_path):
            os.remove(test_db_path)

if __name__ == "__main__":
    test_save_button_functionality()
