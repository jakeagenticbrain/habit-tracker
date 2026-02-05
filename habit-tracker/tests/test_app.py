"""Tests for main application framework."""

import pytest
from game.app import App
from game.screens import HomeScreen
from display.pygame_display import PygameDisplay
from input.keyboard_input import KeyboardInput


def test_app_initialization():
    """Test that App initializes with display and input."""
    display = PygameDisplay(width=128, height=128)
    input_handler = KeyboardInput()
    screens = {"home": HomeScreen()}

    app = App(
        display=display,
        input_handler=input_handler,
        screens=screens,
        initial_screen="home",
        target_fps=20
    )

    assert app.display == display
    assert app.input_handler == input_handler
    assert app.target_fps == 20
    assert app.running is False
    assert app.current_screen_name == "home"

    display.close()


def test_app_frame_time_calculation():
    """Test that frame time is calculated correctly."""
    display = PygameDisplay(width=128, height=128)
    input_handler = KeyboardInput()
    screens = {"home": HomeScreen()}

    app = App(
        display=display,
        input_handler=input_handler,
        screens=screens,
        target_fps=20
    )

    # 20 FPS = 50ms per frame
    assert app._frame_time == 0.05

    display.close()
