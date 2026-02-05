"""Test delete confirmation popup on ViewHabitsScreen."""

from PIL import Image
from game.view_habits_screen import ViewHabitsScreen
from input.input_base import InputEvent, InputType


def test_delete_popup_shows():
    """Test that delete popup appears when BUTTON_C is pressed on a habit."""
    screen = ViewHabitsScreen()
    buffer = Image.new('RGB', (128, 128), (255, 255, 255))

    # Select first habit
    screen.handle_input(InputEvent(InputType.DOWN, True))

    # Press BUTTON_C to show delete confirmation
    screen.handle_input(InputEvent(InputType.BUTTON_C, True))

    # Render with popup
    screen.render(buffer)
    buffer.save("/tmp/delete_popup_ok_selected.png")

    print("✓ Delete popup shown - check /tmp/delete_popup_ok_selected.png")
    assert screen.show_delete_popup == True
    assert screen.popup_selected_button == 0  # OK selected by default


def test_delete_popup_button_navigation():
    """Test that LEFT/RIGHT changes button selection in popup."""
    screen = ViewHabitsScreen()
    buffer = Image.new('RGB', (128, 128), (255, 255, 255))

    # Select first habit and show popup
    screen.handle_input(InputEvent(InputType.DOWN, True))
    screen.handle_input(InputEvent(InputType.BUTTON_C, True))

    # Move to Cancel button
    screen.handle_input(InputEvent(InputType.RIGHT, True))
    screen.render(buffer)
    buffer.save("/tmp/delete_popup_cancel_selected.png")

    print("✓ Cancel button selected - check /tmp/delete_popup_cancel_selected.png")
    assert screen.popup_selected_button == 1


def test_delete_popup_confirms_deletion():
    """Test that pressing OK on popup deletes the habit."""
    screen = ViewHabitsScreen()
    initial_count = len(screen.habits)

    # Select first habit and show popup
    screen.handle_input(InputEvent(InputType.DOWN, True))
    screen.handle_input(InputEvent(InputType.BUTTON_C, True))

    # Confirm deletion (OK button, BUTTON_A)
    screen.handle_input(InputEvent(InputType.BUTTON_A, True))

    assert len(screen.habits) == initial_count - 1
    assert screen.show_delete_popup == False
    print("✓ Habit deleted successfully")


def test_delete_popup_cancels():
    """Test that pressing Cancel on popup closes without deleting."""
    screen = ViewHabitsScreen()
    initial_count = len(screen.habits)

    # Select first habit and show popup
    screen.handle_input(InputEvent(InputType.DOWN, True))
    screen.handle_input(InputEvent(InputType.BUTTON_C, True))

    # Select Cancel and press BUTTON_A
    screen.handle_input(InputEvent(InputType.RIGHT, True))
    screen.handle_input(InputEvent(InputType.BUTTON_A, True))

    assert len(screen.habits) == initial_count  # No deletion
    assert screen.show_delete_popup == False
    print("✓ Cancel closes popup without deleting")


def test_delete_popup_button_b_cancels():
    """Test that BUTTON_B closes popup without deleting."""
    screen = ViewHabitsScreen()
    initial_count = len(screen.habits)

    # Select first habit and show popup
    screen.handle_input(InputEvent(InputType.DOWN, True))
    screen.handle_input(InputEvent(InputType.BUTTON_C, True))

    # Press BUTTON_B to cancel
    screen.handle_input(InputEvent(InputType.BUTTON_B, True))

    assert len(screen.habits) == initial_count  # No deletion
    assert screen.show_delete_popup == False
    print("✓ BUTTON_B closes popup without deleting")


if __name__ == "__main__":
    test_delete_popup_shows()
    test_delete_popup_button_navigation()
    test_delete_popup_confirms_deletion()
    test_delete_popup_cancels()
    test_delete_popup_button_b_cancels()
    print("\n✅ All delete popup tests passed!")
