"""Tests for HomeScreen with layered character sprites."""

from PIL import Image
import pytest
from game.screens import HomeScreen
from input.input_base import InputEvent, InputType
from config import Config


def test_home_screen_initialization():
    """Test that HomeScreen loads and scales all sprites correctly."""
    screen = HomeScreen()

    # Verify sprites are loaded and scaled to 128x128
    assert screen.background.size == (128, 128)
    assert screen.character.size == (128, 128)
    assert len(screen.faces) == 6  # Should have 6 face sprites
    for face in screen.faces:
        assert face.size == (128, 128)

    # Verify starting face index
    assert screen.current_face_index == 0


def test_home_screen_face_cycling():
    """Test that Button C cycles through facial expressions."""
    screen = HomeScreen()

    # Start at face 0
    assert screen.current_face_index == 0

    # Press Button C - should cycle to face 1
    event = InputEvent(InputType.BUTTON_C, pressed=True)
    result = screen.handle_input(event)
    assert result is None  # No navigation
    assert screen.current_face_index == 1

    # Press Button C 5 more times - should cycle through remaining faces
    for i in range(5):
        event = InputEvent(InputType.BUTTON_C, pressed=True)
        screen.handle_input(event)

    # Should wrap back to face 0
    assert screen.current_face_index == 0


def test_home_screen_navigation():
    """Test that left/right navigation works."""
    screen = HomeScreen()

    # Right should go to menu
    event = InputEvent(InputType.RIGHT, pressed=True)
    result = screen.handle_input(event)
    assert result == "menu"

    # Left should go to stats
    event = InputEvent(InputType.LEFT, pressed=True)
    result = screen.handle_input(event)
    assert result == "stats"


def test_home_screen_render():
    """Test that render method works without errors."""
    screen = HomeScreen()
    buffer = Image.new("RGB", (128, 128), (255, 255, 255))

    # Should render without errors
    screen.render(buffer)

    # Verify buffer is still 128x128 (not resized)
    assert buffer.size == (128, 128)
