"""Text input widget with character picker for joystick navigation."""

from PIL import Image
from input.input_base import InputEvent, InputType
from game.ui_components import draw_input_field, draw_button_hint
from assets.sprite_loader import render_text
from config import Config


class TextInputWidget:
    """Text input widget with ledger-style character cycling.

    Controls:
        - LEFT/RIGHT: Cycle through characters
        - BUTTON_A: Confirm character and add to value
        - BUTTON_B: Delete last character
        - BUTTON_C: Save and return value
    """

    # Character set for input (sections: Uppercase, Lowercase, Space, Numbers, Special)
    CHARSET = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz 0123456789._-"

    # Section boundaries for quick navigation
    SECTION_UPPERCASE_START = 0   # A-Z (indices 0-25)
    SECTION_LOWERCASE_START = 26  # a-z (indices 26-51)
    SECTION_SPACE_START = 52      # space (index 52)
    SECTION_NUMBERS_START = 53    # 0-9 (indices 53-62)
    SECTION_SPECIAL_START = 63    # ._- (indices 63-65)

    def __init__(self, max_length: int = 16, prompt: str = "Enter text:"):
        """Initialize text input widget.

        Args:
            max_length: Maximum characters allowed
            prompt: Prompt text to display
        """
        self.max_length = max_length
        self.prompt = prompt
        self.value = ""
        self.current_char_index = 0
        self.active = False
        self.cursor_blink_timer = 0
        self.show_cursor = True

    def activate(self) -> None:
        """Activate the widget for input."""
        self.active = True
        self.value = ""
        self.current_char_index = 0

    def deactivate(self) -> None:
        """Deactivate the widget."""
        self.active = False

    def is_active(self) -> bool:
        """Check if widget is active."""
        return self.active

    def get_value(self) -> str:
        """Get current input value."""
        return self.value

    def get_current_char(self) -> str:
        """Get currently selected character."""
        return self.CHARSET[self.current_char_index]

    def _get_next_section_start(self) -> int:
        """Get index of start of next section (for DOWN navigation)."""
        sections = [
            self.SECTION_UPPERCASE_START,
            self.SECTION_LOWERCASE_START,
            self.SECTION_SPACE_START,
            self.SECTION_NUMBERS_START,
            self.SECTION_SPECIAL_START,
        ]

        # Find which section we're currently in and return next section start
        for i, section_start in enumerate(sections):
            if self.current_char_index < section_start:
                return section_start

        # If we're in the last section, wrap to first
        return sections[0]

    def _get_prev_section_start(self) -> int:
        """Get index of start of previous section (for UP navigation)."""
        sections = [
            self.SECTION_UPPERCASE_START,
            self.SECTION_LOWERCASE_START,
            self.SECTION_SPACE_START,
            self.SECTION_NUMBERS_START,
            self.SECTION_SPECIAL_START,
        ]

        # Find which section we're currently in
        current_section = 0
        for i, section_start in enumerate(sections):
            if self.current_char_index >= section_start:
                current_section = i

        # Return previous section start (wrap to last if at first)
        prev_section = (current_section - 1) % len(sections)
        return sections[prev_section]

    def handle_input(self, event: InputEvent) -> str | None:
        """Handle input event.

        Args:
            event: Input event to process

        Returns:
            Saved value if BUTTON_C pressed, None otherwise
        """
        if not self.active or not event.pressed:
            return None

        # Cycle characters left/right (within current section)
        if event.input_type == InputType.RIGHT:
            self.current_char_index = (self.current_char_index + 1) % len(self.CHARSET)
        elif event.input_type == InputType.LEFT:
            self.current_char_index = (self.current_char_index - 1) % len(self.CHARSET)

        # Jump to next/previous section with up/down
        elif event.input_type == InputType.DOWN:
            self.current_char_index = self._get_next_section_start()
        elif event.input_type == InputType.UP:
            self.current_char_index = self._get_prev_section_start()

        # Add current character
        elif event.input_type == InputType.BUTTON_A:
            if len(self.value) < self.max_length:
                self.value += self.get_current_char()

        # Delete last character
        elif event.input_type == InputType.BUTTON_B:
            if self.value:
                self.value = self.value[:-1]

        # Save and return value
        elif event.input_type == InputType.BUTTON_C:
            saved_value = self.value
            self.deactivate()
            return saved_value

        return None

    def update(self, delta_time: float) -> None:
        """Update widget state (cursor blink).

        Args:
            delta_time: Time since last frame in seconds
        """
        if not self.active:
            return

        # Cursor blink every 0.5 seconds
        self.cursor_blink_timer += delta_time
        if self.cursor_blink_timer >= 0.5:
            self.show_cursor = not self.show_cursor
            self.cursor_blink_timer = 0

    def render(self, buffer: Image.Image, x: int = 12, y: int = 47) -> None:
        """Render the widget to buffer.

        Args:
            buffer: PIL Image to draw on
            x, y: Position parameters (ignored - uses absolute positioning for typing popup)
        """
        if not self.active:
            return

        from PIL import ImageDraw
        from assets.sprite_loader import load_font

        # Load font for text rendering
        font = load_font(Config.FONT_REGULAR, 8)

        # Draw typed text with cursor at absolute position x=12, y=47
        draw = ImageDraw.Draw(buffer)

        # Text box bounds: x=12 to x=113 (101px wide)
        TEXT_BOX_START = 12
        TEXT_BOX_END = 113
        MAX_WIDTH = TEXT_BOX_END - TEXT_BOX_START

        # Reserve space for cursor (measure cursor width)
        cursor_bbox = draw.textbbox((0, 0), "_", font=font)
        cursor_width = cursor_bbox[2] - cursor_bbox[0]
        max_text_width = MAX_WIDTH - cursor_width

        # Truncate text (without cursor) to fit in remaining space
        display_text = self.value
        bbox = draw.textbbox((0, 0), display_text, font=font)
        text_width = bbox[2] - bbox[0]

        if text_width > max_text_width:
            # Text is too long - show rightmost characters that fit
            while text_width > max_text_width and len(display_text) > 0:
                display_text = display_text[1:]  # Remove first character
                bbox = draw.textbbox((0, 0), display_text, font=font)
                text_width = bbox[2] - bbox[0]

        # Add cursor AFTER truncation (only when blinking on)
        if self.show_cursor:
            display_text += "_"

        draw.text((TEXT_BOX_START, 47), display_text, fill=Config.COLOR_TEXT_DARK, font=font)

        # Character picker display at x=8, y=67 with 8pt font (moved down 7 pixels)
        current_char = self.get_current_char()
        picker_text = f"< {current_char} >"
        draw.text((8, 67), picker_text, fill=Config.COLOR_TEXT_DARK, font=font)
