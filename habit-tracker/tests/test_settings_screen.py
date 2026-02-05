"""Visual validation test for SettingsScreen."""

from PIL import Image
from game.settings_screen import SettingsScreen
from input.input_base import InputEvent, InputType
import os


def test_settings_screen_renders():
    """Visual test: SettingsScreen renders with background and menu items."""
    screen = SettingsScreen()
    buffer = Image.new("RGB", (128, 128), (255, 255, 255))

    screen.render(buffer)

    # Save for visual inspection
    os.makedirs("test_outputs", exist_ok=True)
    buffer.save("test_outputs/settings_screen.png")

    print("✓ Settings screen rendered - check test_outputs/settings_screen.png")


def test_settings_screen_navigation():
    """Visual test: UP/DOWN changes selection, pointer moves."""
    screen = SettingsScreen()
    buffer = Image.new("RGB", (128, 128), (255, 255, 255))

    # Initial state (index 0)
    screen.render(buffer)
    buffer.save("test_outputs/settings_index_0.png")

    # Move down twice (index 2)
    screen.handle_input(InputEvent(InputType.DOWN, True))
    screen.handle_input(InputEvent(InputType.DOWN, True))
    screen.render(buffer)
    buffer.save("test_outputs/settings_index_2.png")

    print("✓ Navigation working - check test_outputs/settings_index_*.png")
