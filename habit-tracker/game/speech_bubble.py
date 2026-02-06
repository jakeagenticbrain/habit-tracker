"""Speech bubble widget for character dialogue."""

from PIL import Image, ImageDraw
from assets.sprite_loader import SpriteSheet, load_font
from config import Config


class SpeechBubbleWidget:
    """Widget for animated speech bubble with scrolling text."""

    # Text area within the bubble (scaled 2x from 64x64 coords: 14,6 → 28,12)
    TEXT_START_X = 28
    TEXT_START_Y = 12
    TEXT_END_X = 110  # 55 * 2 = 110
    TEXT_MAX_WIDTH = 82  # 110 - 28 = 82px

    def __init__(self):
        """Initialize speech bubble widget."""
        # Load static bubble (64x64) and scale to 128x128
        bubble_64 = Image.open(Config.SPEECH_BUBBLE_STATIC).convert("RGBA")
        self.static_bubble = bubble_64.resize((128, 128), Image.NEAREST)

        # Load animation sprite sheet (5 frames, 64x64 each) and scale to 128x128
        bubble_sheet_64 = SpriteSheet(Config.SPEECH_BUBBLE_ANIM_SHEET, 64, 64)
        self.anim_frames = []
        for i in range(5):
            frame_64 = bubble_sheet_64.get_sprite(i, 0)
            frame_128 = frame_64.resize((128, 128), Image.NEAREST)
            self.anim_frames.append(frame_128)

        # Load font for text
        self.font = load_font(Config.FONT_REGULAR, 8)

        # State machine: hidden, animating_in, showing, animating_out
        self.state = "hidden"
        self.current_frame = 0
        self.frame_timer = 0.0

        # Text state
        self.text = ""
        self.scroll_offset = 0
        self.scroll_timer = 0.0
        self.scroll_delay = 0.15  # Seconds between scroll steps

    def show(self, text: str):
        """Show speech bubble with given text.

        Args:
            text: Text to display in the bubble
        """
        if self.state == "hidden":
            self.text = text
            self.state = "animating_in"
            self.current_frame = 4  # Start at end of animation (largest bubble)
            self.frame_timer = 0.0
            self.scroll_offset = 0
            self.scroll_timer = 0.0

    def hide(self):
        """Hide speech bubble."""
        if self.state == "showing":
            self.state = "animating_out"
            self.current_frame = 0  # Start at beginning (largest bubble)
            self.frame_timer = 0.0

    def toggle(self, text: str = "Hello World"):
        """Toggle speech bubble on/off.

        Args:
            text: Text to display when showing (default: "Hello World")
        """
        if self.state == "hidden":
            self.show(text)
        elif self.state == "showing":
            self.hide()

    def is_visible(self) -> bool:
        """Check if bubble is currently visible (animating or showing).

        Returns:
            True if bubble is visible, False if hidden
        """
        return self.state != "hidden"

    def update(self, delta_time: float):
        """Update animation and text scrolling.

        Args:
            delta_time: Time since last frame in seconds
        """
        if self.state == "animating_in":
            # Play animation backwards (4→3→2→1→0)
            self.frame_timer += delta_time
            if self.frame_timer >= Config.SPEECH_BUBBLE_FRAME_DELAY:
                self.frame_timer = 0.0
                self.current_frame -= 1
                if self.current_frame < 0:
                    # Animation complete, switch to showing
                    self.state = "showing"

        elif self.state == "animating_out":
            # Play animation forwards (0→1→2→3→4)
            self.frame_timer += delta_time
            if self.frame_timer >= Config.SPEECH_BUBBLE_FRAME_DELAY:
                self.frame_timer = 0.0
                self.current_frame += 1
                if self.current_frame >= 5:
                    # Animation complete, hide bubble
                    self.state = "hidden"

        elif self.state == "showing":
            # Update text scrolling if text is too long
            if self._should_scroll():
                self.scroll_timer += delta_time
                if self.scroll_timer >= self.scroll_delay:
                    self.scroll_timer = 0.0
                    # Loop scroll: text + 3 spaces + text
                    max_offset = len(self.text) + 3
                    self.scroll_offset = (self.scroll_offset + 1) % max_offset

    def render(self, buffer: Image.Image):
        """Render speech bubble to buffer.

        Args:
            buffer: PIL Image to draw to
        """
        if self.state == "hidden":
            return

        if self.state == "animating_in" or self.state == "animating_out":
            # Show animation frame
            frame = self.anim_frames[self.current_frame]
            buffer.paste(frame, (0, 0), frame)

        elif self.state == "showing":
            # Show static bubble
            buffer.paste(self.static_bubble, (0, 0), self.static_bubble)

            # Draw text
            self._render_text(buffer)

    def _should_scroll(self) -> bool:
        """Check if text should scroll.

        Returns:
            True if text exceeds max width
        """
        # Rough estimate: 4-5 pixels per character at 8pt
        estimated_width = len(self.text) * 5
        return estimated_width > self.TEXT_MAX_WIDTH

    def _render_text(self, buffer: Image.Image):
        """Render text with scrolling if needed.

        Args:
            buffer: PIL Image to draw to
        """
        draw = ImageDraw.Draw(buffer)

        if self._should_scroll():
            # Create scrolling text: "text   text"
            extended_text = self.text + "   " + self.text
            display_text = extended_text[self.scroll_offset:]
        else:
            display_text = self.text

        # Draw text at specified position
        draw.text(
            (self.TEXT_START_X, self.TEXT_START_Y),
            display_text,
            fill=Config.COLOR_TEXT_DARK,
            font=self.font
        )
