"""Settings screen with menu list and pointer selector."""

from PIL import Image, ImageDraw
from typing import Optional
from input.input_base import InputEvent, InputType
from game.screens import ScreenBase
from assets.sprite_loader import SpriteSheet
from assets import icons
from config import Config


class SettingsScreen(ScreenBase):
    """Settings menu screen with selectable options."""

    MENU_ITEMS = ["Habits", "Update", "About"]
    MENU_START_Y = 35  # Y position where menu items start (below title bar)
    MENU_LINE_HEIGHT = 12  # Pixels between menu items
    POINTER_X = 93  # X position for pointer icon (right side)
    TEXT_X = 15  # X position for menu text (left side)

    def __init__(self):
        """Initialize settings screen."""
        # Convert background to RGB to avoid transparency overlay issues
        bg_rgba = Image.open(Config.SETTINGS_BG).convert("RGBA")
        self.background = Image.new("RGB", bg_rgba.size, (255, 255, 255))
        self.background.paste(bg_rgba, (0, 0), bg_rgba)

        self.icons_sheet = SpriteSheet(Config.ICONS_SPRITE_SHEET, 16, 16)
        self.selected_index = 0

        # Load font once
        from assets.sprite_loader import load_font
        self.font = load_font(Config.FONT_REGULAR, 8)  # Use size 8 instead of 6 for clarity

    def handle_input(self, event: InputEvent) -> Optional[str]:
        """Handle input - UP/DOWN navigate, BUTTON_A select, LEFT back."""
        if not event.pressed:
            return None

        if event.input_type == InputType.UP:
            self.selected_index = max(0, self.selected_index - 1)
        elif event.input_type == InputType.DOWN:
            self.selected_index = min(len(self.MENU_ITEMS) - 1, self.selected_index + 1)
        elif event.input_type == InputType.BUTTON_A:
            selected_item = self.MENU_ITEMS[self.selected_index]
            if selected_item == "Habits":
                return "view_habits"
            elif selected_item == "Update":
                return "update"
            elif selected_item == "About":
                return "about"
        elif event.input_type == InputType.LEFT:
            return "stats"  # Back to carousel

        return None

    def update(self, delta_time: float) -> None:
        """Update settings screen."""
        pass

    def render(self, buffer: Image.Image) -> None:
        """Render settings screen with menu and pointer."""
        # Paste background (now RGB, no transparency issues)
        buffer.paste(self.background, (0, 0))

        # Draw directly on buffer
        draw = ImageDraw.Draw(buffer)

        # Draw menu items
        for i, item in enumerate(self.MENU_ITEMS):
            y_pos = self.MENU_START_Y + (i * self.MENU_LINE_HEIGHT)

            # Determine color (blue if selected, dark if not)
            color = Config.COLOR_BLUE_HIGHLIGHT if i == self.selected_index else Config.COLOR_TEXT_DARK

            # Draw text directly on buffer
            draw.text((self.TEXT_X, y_pos), item, fill=color, font=self.font)

            # Draw pointer if selected (flip horizontally to point left)
            if i == self.selected_index:
                pointer = self.icons_sheet.get_sprite(*icons.POINTER_SMALL)
                pointer_flipped = pointer.transpose(Image.FLIP_LEFT_RIGHT)
                buffer.paste(pointer_flipped, (self.POINTER_X, y_pos - 6), pointer_flipped)
