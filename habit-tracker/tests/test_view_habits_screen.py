"""Visual validation tests for ViewHabitsScreen."""

import pytest
from PIL import Image
from game.view_habits_screen import ViewHabitsScreen
from input.input_base import InputEvent, InputType


def test_render_habits_list():
    """Test rendering habit list with NEW HABIT button."""
    screen = ViewHabitsScreen()
    buffer = Image.new('RGB', (128, 128), color=(255, 255, 255))

    # Render with NEW HABIT button selected (default)
    screen.render(buffer)

    # Visual check: NEW HABIT button should be highlighted
    # Arrow should not be visible yet
    print("\n=== Rendering ViewHabitsScreen with NEW HABIT selected ===")
    print("Expected: NEW HABIT button highlighted, no arrow visible")

    # Save for visual inspection
    buffer.save("/tmp/view_habits_new_habit_selected.png")
    print("Saved: /tmp/view_habits_new_habit_selected.png")


def test_navigate_habit_list():
    """Test navigation through habit list."""
    screen = ViewHabitsScreen()
    buffer = Image.new('RGB', (128, 128), color=(255, 255, 255))

    # Move down to first habit
    screen.handle_input(InputEvent(InputType.DOWN, True))
    screen.render(buffer)

    print("\n=== Rendering ViewHabitsScreen with first habit selected ===")
    print("Expected: Arrow at left of 'WATER', blue highlight on WATER")

    # Save for visual inspection
    buffer.save("/tmp/view_habits_first_habit_selected.png")
    print("Saved: /tmp/view_habits_first_habit_selected.png")

    # Move down to second habit
    screen.handle_input(InputEvent(InputType.DOWN, True))
    screen.render(buffer)

    print("\n=== Rendering ViewHabitsScreen with second habit selected ===")
    print("Expected: Arrow at left of 'GYM', blue highlight on GYM")

    # Save for visual inspection
    buffer.save("/tmp/view_habits_second_habit_selected.png")
    print("Saved: /tmp/view_habits_second_habit_selected.png")


def test_truncate_long_habit_name():
    """Test that long habit names are truncated correctly."""
    screen = ViewHabitsScreen()

    # Test truncation method
    assert screen._truncate_name("WATER") == "WATER"
    assert screen._truncate_name("VERY LONG HABIT NAME") == "VERY LO..."

    # Navigate to long habit name (5th habit)
    buffer = Image.new('RGB', (128, 128), color=(255, 255, 255))
    screen.selected_index = 4  # VERY LONG HABIT NAME
    screen.render(buffer)

    print("\n=== Rendering ViewHabitsScreen with truncated name ===")
    print("Expected: 'VERY LO...' displayed with blue highlight")

    # Save for visual inspection
    buffer.save("/tmp/view_habits_truncated_name.png")
    print("Saved: /tmp/view_habits_truncated_name.png")


def test_frequency_formatting():
    """Test frequency display formatting."""
    screen = ViewHabitsScreen()

    # Test frequency formatting method
    assert screen._format_frequency(3, "day") == "D3"
    assert screen._format_frequency(4, "week") == "W4"
    assert screen._format_frequency(1, "day") == "D1"
    assert screen._format_frequency(7, "week") == "W7"

    print("\n=== Frequency formatting tests passed ===")
    print("D3 for 3x/day, W4 for 4x/week")
