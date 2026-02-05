"""Tests for StatsScreen."""

import pytest
from PIL import Image
from game.screens import StatsScreen
from input.input_base import InputEvent, InputType


def test_stats_screen_initializes():
    """StatsScreen should initialize with sprite sheets."""
    screen = StatsScreen()
    assert screen.icons_sheet is not None
    assert screen.progress_sheet is not None
    assert screen.hunger == 50
    assert screen.happiness == 70


def test_stats_screen_cycles_values_on_button():
    """Buttons should cycle hunger/happiness values."""
    screen = StatsScreen()
    event = InputEvent(InputType.BUTTON_A, pressed=True)

    result = screen.handle_input(event)

    assert result is None  # Stays on same screen
    assert screen.hunger == 60  # Incremented
    assert screen.happiness == 85  # Incremented


def test_stats_screen_navigates_left():
    """Left should navigate to home."""
    screen = StatsScreen()
    event = InputEvent(InputType.LEFT, pressed=True)

    result = screen.handle_input(event)

    assert result == "home"


def test_stats_screen_navigates_right():
    """Right should navigate to menu."""
    screen = StatsScreen()
    event = InputEvent(InputType.RIGHT, pressed=True)

    result = screen.handle_input(event)

    assert result == "menu"


def test_stats_screen_renders():
    """StatsScreen should render progress bars."""
    screen = StatsScreen()
    buffer = Image.new('RGB', (128, 128), color=(255, 255, 255))

    screen.render(buffer)

    # Should have drawn something (not all white)
    pixels = list(buffer.getdata())
    assert pixels.count((255, 255, 255)) < len(pixels)
