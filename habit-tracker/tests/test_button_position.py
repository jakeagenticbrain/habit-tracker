"""Test to verify NEW HABIT button position is exactly at (40, 20)."""

from PIL import Image, ImageDraw
from game.view_habits_screen import ViewHabitsScreen


def test_new_habit_button_position():
    """Verify NEW HABIT button is at (40, 20) and mark it on the image."""
    screen = ViewHabitsScreen()
    buffer = Image.new('RGB', (128, 128), color=(255, 255, 255))

    # Render the screen
    screen.render(buffer)

    # Draw a red crosshair at (40, 20) to verify button position
    draw = ImageDraw.Draw(buffer)

    # Draw crosshair at (40, 20)
    # Horizontal line
    draw.line([(35, 20), (45, 20)], fill=(255, 0, 0), width=1)
    # Vertical line
    draw.line([(40, 15), (40, 25)], fill=(255, 0, 0), width=1)

    # Draw a red box around the expected button position
    # Button sprite is likely around 51x8 based on the constants
    draw.rectangle([(40, 20), (40 + 51, 20 + 8)], outline=(255, 0, 0), width=1)

    # Save the image
    buffer.save("/tmp/button_position_check.png")
    print("\n=== Button Position Verification ===")
    print(f"NEW_HABIT_BUTTON_X = {screen.NEW_HABIT_BUTTON_X}")
    print(f"NEW_HABIT_BUTTON_Y = {screen.NEW_HABIT_BUTTON_Y}")
    print("Expected: (40, 20)")
    print("Red crosshair drawn at (40, 20)")
    print("Red box shows expected button bounds")
    print("Saved: /tmp/button_position_check.png")

    # Assert the values are correct
    assert screen.NEW_HABIT_BUTTON_X == 40, f"Button X is {screen.NEW_HABIT_BUTTON_X}, expected 40"
    assert screen.NEW_HABIT_BUTTON_Y == 20, f"Button Y is {screen.NEW_HABIT_BUTTON_Y}, expected 20"
    print("\n✓ Button position constants are correct (40, 20)")


if __name__ == "__main__":
    test_new_habit_button_position()
