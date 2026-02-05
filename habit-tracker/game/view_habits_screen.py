"""View Habits screen showing habit list with NEW HABIT button."""

from PIL import Image, ImageDraw
from typing import Optional
from game.screens import ScreenBase
from input.input_base import InputEvent, InputType
from assets.sprite_loader import SpriteSheet, load_font
from assets import icons
from config import Config
from data.db import Database


class ViewHabitsScreen(ScreenBase):
    """Habits list screen with NEW HABIT button and habit entries."""

    # Class variable to pass selected habit data to EditHabitScreen
    selected_habit_data: Optional[dict] = None

    # Layout constants (aligned with background dividers)
    NEW_HABIT_BUTTON_X = 40    # 40 pixels inward from left edge
    NEW_HABIT_BUTTON_Y = 20    # 20 pixels down from top
    HABIT_LIST_START_Y = 42    # Below NEW HABIT button
    LINE_HEIGHT = 12           # Vertical spacing between habits
    ARROW_X = 0                # Arrow selector at left edge
    NAME_X = 10                # Habit name column (7 + 3 pixels right)
    POINTS_X = 77              # Points column (70 + 7 pixels right)
    FREQ_X = 103               # Frequency column (105 - 2 pixels left)

    def __init__(self, db: Database):
        """Initialize view habits screen.

        Args:
            db: Database instance for loading habits
        """
        # Convert background RGBA to RGB to avoid transparency overlay
        bg_rgba = Image.open(Config.HABIT_SETTINGS_BG).convert("RGBA")
        self.background = Image.new("RGB", bg_rgba.size, (255, 255, 255))
        self.background.paste(bg_rgba, (0, 0), bg_rgba)

        # Load button sprites
        self.button_normal = Image.open(Config.NEW_HABIT_BUTTON_NORMAL).convert('RGBA')
        self.button_highlighted = Image.open(Config.NEW_HABIT_BUTTON_HIGHLIGHTED).convert('RGBA')

        # Load icons
        self.icons_sheet = SpriteSheet(Config.ICONS_SPRITE_SHEET, 16, 16)

        # Load font
        self.font = load_font(Config.FONT_REGULAR, 8)

        # Load popup sprites
        self.popup_bg = Image.open(Config.POPUP_BG).convert('RGBA')
        self.ok_button = Image.open(Config.POPUP_OK_HIGHLIGHTED).convert('RGBA')
        self.cancel_button = Image.open(Config.POPUP_CANCEL_HIGHLIGHTED).convert('RGBA')

        # Store database and load habits
        self.db = db

        # Load habits from database
        self._load_habits()

        # Selection state: -1 = NEW HABIT button, 0+ = habit index
        self.selected_index = -1

        # Text scrolling state for long habit names
        self.scroll_offset = 0
        self.scroll_timer = 0.0
        self.scroll_delay = 0.15  # Seconds between scroll steps

        # Popup state
        self.show_delete_popup = False
        self.popup_selected_button = 0  # 0 = OK, 1 = Cancel

    def _load_habits(self):
        """Load habits from database."""
        db_habits = self.db.get_all_habits(active_only=False)

        # Convert database format to screen format
        self.habits = []
        for h in db_habits:
            # Parse recurrence into freq_num and freq_period
            recurrence = h.get('recurrence', 'daily')
            if '/' in recurrence:
                parts = recurrence.split('/')
                freq_num = int(parts[0])
                freq_period = parts[1]
            else:
                # Default format
                freq_num = 1
                freq_period = "day"

            self.habits.append({
                "id": h['id'],
                "name": h['name'],
                "points": h['points_per'],
                "freq_num": freq_num,
                "freq_period": freq_period,
                "active": bool(h['active']),
                "reminder": False  # TODO: Add reminder field to DB
            })

    def reload_habits(self):
        """Reload habits from database (called when returning to this screen)."""
        self._load_habits()
        # Reset selection if needed
        if self.selected_index >= len(self.habits):
            self.selected_index = -1  # Default to NEW HABIT button

    def handle_input(self, event: InputEvent) -> Optional[str]:
        """Handle input - UP/DOWN navigate, BUTTON_A select, BUTTON_C delete, LEFT back."""
        if not event.pressed:
            return None

        # If popup is showing, handle popup input
        if self.show_delete_popup:
            if event.input_type == InputType.LEFT:
                self.popup_selected_button = 0  # OK
            elif event.input_type == InputType.RIGHT:
                self.popup_selected_button = 1  # Cancel
            elif event.input_type == InputType.BUTTON_A:
                if self.popup_selected_button == 0:  # OK - delete habit
                    if self.selected_index >= 0 and self.selected_index < len(self.habits):
                        habit = self.habits[self.selected_index]
                        self.db.delete_habit(habit["id"])
                        self._load_habits()  # Reload from database
                        # Adjust selection
                        if self.selected_index >= len(self.habits):
                            self.selected_index = len(self.habits) - 1
                self.show_delete_popup = False
                self.popup_selected_button = 0
            elif event.input_type == InputType.BUTTON_B:
                # Cancel - close popup
                self.show_delete_popup = False
                self.popup_selected_button = 0
            return None

        # Normal navigation mode
        if event.input_type == InputType.UP:
            # Navigate up
            self.selected_index -= 1
            if self.selected_index < -1:
                self.selected_index = len(self.habits) - 1
            return None

        elif event.input_type == InputType.DOWN:
            # Navigate down
            self.selected_index += 1
            if self.selected_index >= len(self.habits):
                self.selected_index = -1
            return None

        elif event.input_type == InputType.BUTTON_A:
            # Select item
            if self.selected_index == -1:
                # NEW HABIT button selected - store None to indicate new habit
                ViewHabitsScreen.selected_habit_data = None
                return "edit_habit"
            else:
                # Habit selected - store the habit data for editing
                ViewHabitsScreen.selected_habit_data = self.habits[self.selected_index].copy()
                return "edit_habit"

        elif event.input_type == InputType.BUTTON_C:
            # Show delete confirmation popup
            if self.selected_index >= 0:
                self.show_delete_popup = True
                self.popup_selected_button = 0
            return None

        elif event.input_type == InputType.LEFT:
            # Go back to menu
            return "menu"

        return None

    def update(self, delta_time: float) -> None:
        """Update screen state - handle text scrolling for long habit names."""
        # Scroll selected habit name if long and a habit is selected (not NEW HABIT button)
        if self.selected_index >= 0 and self.selected_index < len(self.habits):
            habit_name = self.habits[self.selected_index]["name"]
            if len(habit_name) > 8:  # Max display length
                self.scroll_timer += delta_time
                if self.scroll_timer >= self.scroll_delay:
                    self.scroll_timer = 0.0
                    self.scroll_offset = (self.scroll_offset + 1) % (len(habit_name) + 1)
            else:
                self.scroll_offset = 0
                self.scroll_timer = 0.0
        else:
            # Reset scroll when NEW HABIT button is selected or no habit selected
            self.scroll_offset = 0
            self.scroll_timer = 0.0

    def render(self, buffer: Image.Image) -> None:
        """Render habits list screen."""
        # Paste background (RGB, no transparency issues)
        buffer.paste(self.background, (0, 0))

        # Draw NEW HABIT button (full-screen overlay sprite, paste at origin)
        if self.selected_index == -1:
            # Highlighted
            buffer.paste(self.button_highlighted, (0, 0), self.button_highlighted)
        else:
            # Normal
            buffer.paste(self.button_normal, (0, 0), self.button_normal)

        # Draw directly on buffer
        draw = ImageDraw.Draw(buffer)
        draw.fontmode = '1'  # CRITICAL: Disable anti-aliasing for pixel-perfect text

        # Draw habit list
        arrow_sprite = self.icons_sheet.get_sprite(*icons.ARROW_SMALL)

        for i, habit in enumerate(self.habits):
            y_pos = self.HABIT_LIST_START_Y + (i * self.LINE_HEIGHT)

            # Draw arrow if selected
            if i == self.selected_index:
                buffer.paste(arrow_sprite, (self.ARROW_X, y_pos - 5), arrow_sprite)

            # Draw habit name (scrolling if selected, truncated if not)
            name = habit["name"]
            is_selected = i == self.selected_index

            if len(name) > 8:
                if is_selected:
                    # Show scrolling text for selected habit
                    extended_name = name + "   " + name  # Add spacing and repeat
                    name_text = extended_name[self.scroll_offset:self.scroll_offset + 8]
                else:
                    # Show truncated text for non-selected habits
                    name_text = name[:7] + "..."
            else:
                name_text = name

            name_color = Config.COLOR_BLUE_HIGHLIGHT if is_selected else Config.COLOR_TEXT_DARK
            draw.text((self.NAME_X, y_pos), name_text, fill=name_color, font=self.font)

            # Draw points (e.g., "+10")
            points_text = f"+{habit['points']}"
            draw.text((self.POINTS_X, y_pos), points_text, fill=Config.COLOR_TEXT_DARK, font=self.font)

            # Draw frequency (e.g., "D3" for 3x/day, "W4" for 4x/week)
            freq_text = self._format_frequency(habit["freq_num"], habit["freq_period"])
            draw.text((self.FREQ_X, y_pos), freq_text, fill=Config.COLOR_TEXT_DARK, font=self.font)

        # Draw delete confirmation popup overlay if showing
        if self.show_delete_popup:
            # Paste popup background (RGBA - transparent outside dialog box)
            buffer.paste(self.popup_bg, (0, 0), self.popup_bg)

            # Draw message text starting at (36, 44), wrapping at x=112
            # Note: fontmode already set to '1' above for pixel-perfect rendering
            message = "Delete this habit?"
            lines = self._wrap_text(message, 36, 112)
            for i, line in enumerate(lines):
                line_y = 44 + (i * 10)  # 10 pixels between lines
                draw.text((36, line_y), line, fill=Config.COLOR_TEXT_DARK, font=self.font)

            # Draw OK button if selected (highlighted)
            if self.popup_selected_button == 0:
                buffer.paste(self.ok_button, (0, 0), self.ok_button)

            # Draw Cancel button if selected (highlighted)
            if self.popup_selected_button == 1:
                buffer.paste(self.cancel_button, (0, 0), self.cancel_button)

    def _truncate_name(self, name: str) -> str:
        """Truncate name to 8 characters max.

        Args:
            name: Habit name

        Returns:
            Truncated name with "..." if longer than 8 chars
        """
        if len(name) > 8:
            return name[:7] + "..."
        return name

    def _format_frequency(self, freq_num: int, freq_period: str) -> str:
        """Format frequency display string.

        Args:
            freq_num: Frequency number (e.g., 3)
            freq_period: Frequency period ("day" or "week")

        Returns:
            Formatted string (e.g., "D3" for 3x/day, "W4" for 4x/week)
        """
        period_char = "D" if freq_period == "day" else "W"
        return f"{period_char}{freq_num}"

    def _wrap_text(self, text: str, start_x: int, max_x: int) -> list[str]:
        """Wrap text to fit within max_x boundary.

        Args:
            text: Text to wrap
            start_x: Starting x position
            max_x: Maximum x position (text will wrap before this)

        Returns:
            List of text lines that fit within the width
        """
        max_width = max_x - start_x
        words = text.split()
        lines = []
        current_line = ""

        for word in words:
            test_line = current_line + (" " if current_line else "") + word
            # Rough estimate: ~5 pixels per character for 8pt font
            if len(test_line) * 5 <= max_width:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word

        if current_line:
            lines.append(current_line)

        return lines
