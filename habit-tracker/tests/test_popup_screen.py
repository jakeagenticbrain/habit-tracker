"""Visual validation tests for PopupScreen."""

from PIL import Image
from game.popup_screen import PopupScreen
from input.input_base import InputEvent, InputType


def test_popup_render():
    """Visual test: Render popup with delete confirmation message (OK selected)."""
    screen = PopupScreen(
        message="Are you sure you want to delete this habit?",
        on_ok_screen="view_habits",
        on_cancel_screen="edit_habit"
    )

    buffer = Image.new("RGB", (128, 128), (255, 255, 255))
    screen.render(buffer)

    # Save for visual inspection
    buffer.save("/tmp/popup_ok_selected.png")
    print("\nSaved: /tmp/popup_ok_selected.png")
    print("Expected: Background with caution icon, wrapped text, OK button highlighted")


def test_popup_button_selection():
    """Visual test: Switch to Cancel button."""
    screen = PopupScreen(
        message="Are you sure you want to delete this habit?",
        on_ok_screen="view_habits",
        on_cancel_screen="edit_habit"
    )

    # Switch to Cancel
    screen.handle_input(InputEvent(InputType.RIGHT, True))

    buffer = Image.new("RGB", (128, 128), (255, 255, 255))
    screen.render(buffer)

    # Save for visual inspection
    buffer.save("/tmp/popup_cancel_selected.png")
    print("\nSaved: /tmp/popup_cancel_selected.png")
    print("Expected: Background with caution icon, wrapped text, Cancel button highlighted")


def test_popup_text_wrapping():
    """Visual test: Long message that needs wrapping."""
    screen = PopupScreen(
        message="This is a very long message that should wrap across multiple lines to fit within the popup dialog area",
        on_ok_screen="home",
        on_cancel_screen="settings"
    )

    buffer = Image.new("RGB", (128, 128), (255, 255, 255))
    screen.render(buffer)

    # Save for visual inspection
    buffer.save("/tmp/popup_wrapped_text.png")
    print("\nSaved: /tmp/popup_wrapped_text.png")
    print("Expected: Multi-line wrapped text visible to the right of caution icon")
