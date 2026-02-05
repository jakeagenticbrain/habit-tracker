"""Popup confirmation dialog screen."""

from PIL import Image, ImageDraw
from typing import Optional
from input.input_base import InputEvent, InputType
from game.screens import ScreenBase
from assets.sprite_loader import render_text
from config import Config


class PopupScreen(ScreenBase):
    """Reusable popup dialog with OK/Cancel buttons.

    Displays a background with caution icon, custom message text,
    and OK/Cancel buttons. User can select with LEFT/RIGHT and
    confirm with BUTTON_A.
    """

    # Layout constants
    TEXT_X = 30
    TEXT_Y = 30
    TEXT_WIDTH = 80
    OK_BUTTON_X = 23
    CANCEL_BUTTON_X = 55
    BUTTON_Y = 107

    def __init__(self, message: str, on_ok_screen: str, on_cancel_screen: str):
        """Initialize popup screen.

        Args:
            message: Text to display (will wrap if needed)
            on_ok_screen: Screen to navigate to if OK pressed
            on_cancel_screen: Screen to navigate to if Cancel pressed
        """
        self.message = message
        self.on_ok_screen = on_ok_screen
        self.on_cancel_screen = on_cancel_screen
        self.selected_button = 0  # 0 = OK, 1 = Cancel

        # Load background and button sprites
        self.bg_sprite = Image.open(Config.POPUP_BG).convert("RGBA")
        self.ok_highlighted = Image.open(Config.POPUP_OK_HIGHLIGHTED).convert("RGBA")
        self.cancel_highlighted = Image.open(Config.POPUP_CANCEL_HIGHLIGHTED).convert("RGBA")

        # Wrap message text
        self.wrapped_lines = self._wrap_text(message)

    def _wrap_text(self, text: str) -> list[str]:
        """Wrap text to fit within TEXT_WIDTH.

        Simple word-based wrapping using rough estimate of 4 pixels
        per character for 6pt font.

        Args:
            text: Text to wrap

        Returns:
            List of lines
        """
        words = text.split()
        lines = []
        current_line = ""

        for word in words:
            test_line = f"{current_line} {word}".strip()
            # Rough estimate: 4 pixels per char for 6pt font
            if len(test_line) * 4 <= self.TEXT_WIDTH:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word

        if current_line:
            lines.append(current_line)

        return lines

    def handle_input(self, event: InputEvent) -> Optional[str]:
        """Handle input for button selection.

        Args:
            event: Input event

        Returns:
            Screen name to navigate to, or None
        """
        if event.input_type == InputType.LEFT:
            self.selected_button = 0  # OK
            return None
        elif event.input_type == InputType.RIGHT:
            self.selected_button = 1  # Cancel
            return None
        elif event.input_type == InputType.BUTTON_A:
            # Confirm selection
            if self.selected_button == 0:
                return self.on_ok_screen
            else:
                return self.on_cancel_screen

        return None

    def update(self, delta_time: float) -> None:
        """Update popup state (no animations).

        Args:
            delta_time: Time since last frame in seconds
        """
        pass  # Static popup, no updates needed

    def render(self, buffer: Image.Image) -> None:
        """Render popup dialog to buffer.

        Args:
            buffer: PIL Image to draw to
        """
        # Draw background with caution icon
        buffer.paste(self.bg_sprite, (0, 0), self.bg_sprite)

        # Draw wrapped message text
        y_offset = self.TEXT_Y
        for line in self.wrapped_lines:
            line_img = render_text(
                line,
                Config.FONT_REGULAR,
                Config.FONT_SIZE_TINY,
                Config.COLOR_TEXT_DARK
            )
            buffer.paste(line_img, (self.TEXT_X, y_offset), line_img)
            y_offset += 10  # Line spacing

        # Draw only the highlighted button for selected option
        if self.selected_button == 0:
            # OK button highlighted
            buffer.paste(self.ok_highlighted, (self.OK_BUTTON_X, self.BUTTON_Y), self.ok_highlighted)
        else:
            # Cancel button highlighted
            buffer.paste(self.cancel_highlighted, (self.CANCEL_BUTTON_X, self.BUTTON_Y), self.cancel_highlighted)
