"""About screen showing README content."""

from PIL import Image, ImageDraw
from typing import Optional
from input.input_base import InputEvent, InputType
from game.screens import ScreenBase
from assets.sprite_loader import load_font
from config import Config
import os


class AboutScreen(ScreenBase):
    """About screen that displays README.md content.

    Shows scrollable README text with navigation controls.
    """

    # Layout constants
    TEXT_X = 10
    TEXT_Y = 20
    TEXT_WIDTH = 108  # 128 - 10 (left) - 10 (right)
    LINE_HEIGHT = 10
    VISIBLE_LINES = 10  # Number of lines visible on screen

    def __init__(self):
        """Initialize about screen."""
        # Load font
        self.font = load_font(Config.FONT_REGULAR, 8)

        # Load README content
        self.lines = self._load_readme()
        self.scroll_offset = 0

    def _load_readme(self) -> list[str]:
        """Load and wrap README.md content.

        Returns:
            List of wrapped lines
        """
        readme_path = os.path.join(Config.BASE_DIR, "..", "README.md")

        try:
            with open(readme_path, 'r') as f:
                content = f.read()

            # Simple processing: split by lines and wrap
            lines = []
            for paragraph in content.split('\n'):
                if not paragraph.strip():
                    lines.append('')  # Blank line
                    continue

                # Wrap long lines
                wrapped = self._wrap_line(paragraph)
                lines.extend(wrapped)

            return lines

        except FileNotFoundError:
            return [
                "Habit Tracker",
                "",
                "A tamagotchi-style",
                "habit tracker for",
                "Raspberry Pi Zero.",
                "",
                "README.md not found"
            ]

    def _wrap_line(self, text: str) -> list[str]:
        """Wrap a line to fit within TEXT_WIDTH.

        Args:
            text: Text to wrap

        Returns:
            List of wrapped lines
        """
        if not text:
            return ['']

        # Remove markdown headers
        if text.startswith('#'):
            text = text.lstrip('#').strip()

        words = text.split()
        lines = []
        current_line = ""

        for word in words:
            test_line = f"{current_line} {word}".strip()
            # Measure actual pixel width
            bbox = self.font.getbbox(test_line)
            text_width = bbox[2] - bbox[0]

            if text_width <= self.TEXT_WIDTH:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word

        if current_line:
            lines.append(current_line)

        return lines if lines else ['']

    def handle_input(self, event: InputEvent) -> Optional[str]:
        """Handle input for scrolling and navigation.

        Args:
            event: Input event

        Returns:
            Screen name to navigate to, or None
        """
        if not event.pressed:
            return None

        max_scroll = max(0, len(self.lines) - self.VISIBLE_LINES)

        if event.input_type == InputType.UP:
            self.scroll_offset = max(0, self.scroll_offset - 1)
        elif event.input_type == InputType.DOWN:
            self.scroll_offset = min(max_scroll, self.scroll_offset + 1)
        elif event.input_type == InputType.LEFT or event.input_type == InputType.BUTTON_B:
            return "settings"  # Back to settings

        return None

    def update(self, delta_time: float) -> None:
        """Update about screen (no animations).

        Args:
            delta_time: Time since last frame in seconds
        """
        pass

    def render(self, buffer: Image.Image) -> None:
        """Render about screen to buffer.

        Args:
            buffer: PIL Image to draw to
        """
        # Clear background
        buffer.paste((255, 255, 255), (0, 0, 128, 128))

        draw = ImageDraw.Draw(buffer)

        # Draw title bar
        draw.rectangle([0, 0, 128, 15], fill=Config.COLOR_BLUE_HIGHLIGHT)
        draw.text((5, 3), "ABOUT", fill=Config.COLOR_WHITE, font=self.font)

        # Draw scrollable text
        y_offset = self.TEXT_Y
        visible_lines = self.lines[self.scroll_offset:self.scroll_offset + self.VISIBLE_LINES]

        for line in visible_lines:
            draw.text((self.TEXT_X, y_offset), line, fill=Config.COLOR_TEXT_DARK, font=self.font)
            y_offset += self.LINE_HEIGHT

        # Draw scroll indicator if needed
        if len(self.lines) > self.VISIBLE_LINES:
            total_lines = len(self.lines)
            scroll_pct = self.scroll_offset / max(1, total_lines - self.VISIBLE_LINES)
            indicator_y = 20 + int(scroll_pct * 88)  # 88 = 108 - 20 (usable height)
            draw.rectangle([125, indicator_y, 127, indicator_y + 10], fill=Config.COLOR_BLUE_HIGHLIGHT)
