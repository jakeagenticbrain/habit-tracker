"""
Visual validation tests for HabitCheckerScreen.

These tests render screens and save them to test_output/ for manual inspection.
"""

import pytest
import os
from PIL import Image
from game.habit_checker_screen import HabitCheckerScreen
from input.input_base import InputEvent, InputType


@pytest.fixture
def habit_checker_screen():
    """Create HabitCheckerScreen instance."""
    return HabitCheckerScreen()


def test_habit_checker_initial_render(habit_checker_screen):
    """Test that habit checker renders with 4-day grid and all habits."""
    buffer = Image.new('RGB', (128, 128), color=(255, 255, 255))
    habit_checker_screen.render(buffer)

    assert buffer.size == (128, 128)
    assert buffer.mode == "RGB"

    # Save for visual inspection
    os.makedirs("test_output", exist_ok=True)
    buffer.save("test_output/habit_checker_initial.png")
    print("\n✅ Saved: test_output/habit_checker_initial.png")
    print("Expected: 4 day letter headers, 4 habits with 4 checkboxes each")


def test_habit_checker_habit_selection(habit_checker_screen):
    """Test habit selection mode (highlight habit name)."""
    buffer = Image.new('RGB', (128, 128), color=(255, 255, 255))

    # Navigate to second habit
    habit_checker_screen.handle_input(InputEvent(InputType.DOWN, True))

    habit_checker_screen.render(buffer)
    buffer.save("test_output/habit_checker_habit_selected.png")
    print("\n✅ Saved: test_output/habit_checker_habit_selected.png")
    print("Expected: Second habit (GYM) highlighted in blue")


def test_habit_checker_checkbox_mode(habit_checker_screen):
    """Test checkbox mode (enter, toggle, verify)."""
    buffer = Image.new('RGB', (128, 128), color=(255, 255, 255))

    # Select first habit
    assert habit_checker_screen.selected_habit == 0

    # Enter checkbox mode
    habit_checker_screen.handle_input(InputEvent(InputType.BUTTON_A, True))
    assert habit_checker_screen.checkbox_mode is True

    # Render with checkbox mode active
    habit_checker_screen.render(buffer)
    buffer.save("test_output/habit_checker_checkbox_mode.png")
    print("\n✅ Saved: test_output/habit_checker_checkbox_mode.png")
    print("Expected: Blue border around rightmost checkbox (today) for WATER")

    # Toggle today's checkbox (was True, should become False)
    original_state = habit_checker_screen.habits[0]["checks"][3]
    habit_checker_screen.handle_input(InputEvent(InputType.BUTTON_A, True))
    new_state = habit_checker_screen.habits[0]["checks"][3]
    assert new_state == (not original_state)

    # Render after toggle
    buffer2 = Image.new('RGB', (128, 128), color=(255, 255, 255))
    habit_checker_screen.render(buffer2)
    buffer2.save("test_output/habit_checker_toggled.png")
    print("✅ Saved: test_output/habit_checker_toggled.png")
    print("Expected: Today's checkbox for WATER toggled (checked → unchecked)")

    # Exit checkbox mode
    habit_checker_screen.handle_input(InputEvent(InputType.BUTTON_B, True))
    assert habit_checker_screen.checkbox_mode is False
