"""Visual validation tests for EditHabitScreen."""

import pytest
from PIL import Image
from game.edit_habit_screen import EditHabitScreen
from input.input_base import InputEvent, InputType


def test_render_new_habit(tmp_path):
    """Visual test: Render empty form for new habit."""
    screen = EditHabitScreen()
    buffer = Image.new("RGBA", (128, 128), (255, 255, 255, 255))
    screen.render(buffer)

    output_path = tmp_path / "edit_habit_new.png"
    buffer.save(output_path)
    print(f"\n[VISUAL] New habit form: {output_path}")

    # Verify screen initialized correctly
    assert screen.name == ""
    assert screen.freq_number == 1
    assert screen.freq_period == "day"
    assert screen.points == 5
    assert screen.active is True
    assert screen.reminder is False


def test_render_existing_habit(tmp_path):
    """Visual test: Render pre-filled form for existing habit."""
    habit_data = {
        "name": "WATER",
        "freq_number": 3,
        "freq_period": "day",
        "points": 10,
        "active": True,
        "reminder": True,
    }

    screen = EditHabitScreen(habit_data=habit_data)
    buffer = Image.new("RGBA", (128, 128), (255, 255, 255, 255))
    screen.render(buffer)

    output_path = tmp_path / "edit_habit_existing.png"
    buffer.save(output_path)
    print(f"\n[VISUAL] Existing habit form: {output_path}")

    # Verify fields loaded correctly
    assert screen.name == "WATER"
    assert screen.freq_number == 3
    assert screen.freq_period == "day"
    assert screen.points == 10
    assert screen.active is True
    assert screen.reminder is True


def test_render_name_editing_mode(tmp_path):
    """Visual test: Render with input popup when editing name."""
    screen = EditHabitScreen()

    # Activate name editing
    event_a = InputEvent(InputType.BUTTON_A, pressed=True)
    screen.handle_input(event_a)

    buffer = Image.new("RGBA", (128, 128), (255, 255, 255, 255))
    screen.update(0.0)  # Update to initialize text input
    screen.render(buffer)

    output_path = tmp_path / "edit_habit_name_editing.png"
    buffer.save(output_path)
    print(f"\n[VISUAL] Name editing mode with popup: {output_path}")

    # Verify editing state
    assert screen.editing_name is True
    assert screen.text_input.is_active() is True


def test_display_name_truncation():
    """Test that _get_display_name() returns last 6 characters."""
    screen = EditHabitScreen()

    # Short name (no truncation)
    screen.name = "GYM"
    assert screen._get_display_name() == "GYM"

    # 6 character name (no truncation)
    screen.name = "MEDITA"
    assert screen._get_display_name() == "MEDITA"

    # Long name (truncated to last 6)
    screen.name = "VERYLONGNAME"
    assert screen._get_display_name() == "NGNAME"  # Last 6 chars of "VERYLONGNAME"

    # Another long name
    screen.name = "MEDITATION"
    assert screen._get_display_name() == "TATION"  # Last 6 chars of "MEDITATION"
