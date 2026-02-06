"""
HabitCheckerScreen: 4-day grid for marking habit completion.

Displays habits in rows with checkboxes for past 3 days + today.
Two navigation modes:
- Habit selection mode: highlight habit name, UP/DOWN to navigate, BUTTON_A to enter checkbox mode
- Checkbox mode: LEFT/RIGHT to select day, BUTTON_A to toggle, BUTTON_B to exit
"""

from datetime import datetime, timedelta
from PIL import Image, ImageDraw
from game.screens import ScreenBase
from assets.sprite_loader import render_text, SpriteSheet
from input.input_base import InputEvent, InputType
from typing import Optional
from assets import icons
from config import Config
from data.db import Database


class HabitCheckerScreen(ScreenBase):
    """
    Screen for checking off habits in a 3-day grid.

    Layout:
    - Day letter headers (M, T, W, Th, F, S, Su) at top
    - Habit names on left
    - Checkboxes in grid (3 days × N habits)

    Navigation:
    - Habit selection mode: UP/DOWN to select habit, BUTTON_A to enter checkbox mode
    - Checkbox mode: LEFT/RIGHT to select day, BUTTON_A to toggle, BUTTON_B to exit
    """

    # Layout constants
    DAY_LETTER_Y = 35  # Moved down 12px (was 23)
    HABIT_LIST_START_Y = 47  # Moved down 12px (was 35)
    LINE_HEIGHT = 10
    NAME_X = 9  # Moved right 2px (was 7)
    CHECKBOX_START_X = 74  # Moved right 2px (was 72)
    CHECKBOX_SPACING = 14
    MAX_NAME_LENGTH = 8  # Truncate long habit names

    def __init__(self, db: Database):
        """Initialize HabitCheckerScreen.

        Args:
            db: Database instance for loading/saving habit logs
        """
        # Load background sprite - convert RGBA to RGB with white base
        bg_rgba = Image.open(Config.HABIT_CHECKER_BG).convert('RGBA')
        self.background = Image.new("RGB", bg_rgba.size, (255, 255, 255))
        self.background.paste(bg_rgba, (0, 0), bg_rgba)

        # Load icons sprite sheet
        self.icons_sheet = SpriteSheet(Config.ICONS_SPRITE_SHEET)

        # Load highlighted checkbox sprites (16x16 tiles, stacked vertically)
        self.highlight_sheet = SpriteSheet(Config.HIGHLIGHTED_CHECKBOXES, 16, 16)
        self.checked_highlight = self.highlight_sheet.get_sprite(0, 0)  # Top tile
        self.unchecked_highlight = self.highlight_sheet.get_sprite(0, 1)  # Bottom tile

        # Load font for crisp text rendering
        from assets.sprite_loader import load_font
        self.font = load_font(Config.FONT_REGULAR, 8)

        # Store database and load habits
        self.db = db
        self._load_habits()
        self.selected_habit = 0  # Currently highlighted habit (row)
        self.selected_day = 2  # Currently selected day column (0-2, default to today)
        self.checkbox_mode = False  # False: habit selection, True: checkbox selection

        # Text scrolling state for long habit names
        self.scroll_offset = 0
        self.scroll_timer = 0.0
        self.scroll_delay = 0.15  # Seconds between scroll steps

        # Get day letters dynamically based on current date
        self.day_letters = self._get_past_3_days()

    def _get_past_3_days(self) -> list[str]:
        """
        Get single-letter abbreviations for past 2 days + today.

        Returns:
            List of 3 single-letter day abbreviations (e.g., ["S", "S", "M"])
        """
        today = datetime.now()
        days = []
        for i in range(2, -1, -1):  # 2 days ago to today
            day = today - timedelta(days=i)
            day_abbr = day.strftime("%a")  # Mon, Tue, Wed, etc.

            # Handle Thursday and Sunday specially (2 letters)
            if day_abbr == "Thu":
                days.append("Th")
            elif day_abbr == "Sun":
                days.append("Su")
            else:
                days.append(day_abbr[0])  # First letter only

        return days

    def _load_habits(self):
        """Load habits and their completion status from database."""
        db_habits = self.db.get_all_habits(active_only=True)
        print(f"[DEBUG] HabitCheckerScreen._load_habits: Found {len(db_habits)} active habits")
        for h in db_habits:
            print(f"  - Habit ID {h['id']}: {h['name']} (active={h.get('active', 'N/A')})")

        # Get dates for past 2 days + today
        today = datetime.now()
        dates = [(today - timedelta(days=i)).strftime("%Y-%m-%d") for i in range(2, -1, -1)]

        self.habits = []
        for h in db_habits:
            # Get logs for this habit for the 3-day range
            logs = self.db.get_habit_logs(h['id'], start_date=dates[0], end_date=dates[2])

            # Build checks array (True/False for each day)
            checks = []
            for date in dates:
                log = next((l for l in logs if l['date'] == date), None)
                checks.append(bool(log and log['completed']) if log else False)

            self.habits.append({
                "id": h['id'],
                "name": h['name'],
                "checks": checks
            })

    def reload_habits(self):
        """Reload habits from database (called when returning to this screen)."""
        self._load_habits()
        # Reset selection if out of bounds
        if self.selected_habit >= len(self.habits):
            self.selected_habit = 0
        # Recalculate day letters in case date changed
        self.day_letters = self._get_past_3_days()

    def _save_checkbox(self, habit_idx: int, day_idx: int, checked: bool):
        """Save checkbox state to database.

        Args:
            habit_idx: Index of habit in self.habits
            day_idx: Index of day (0=2 days ago, 1=yesterday, 2=today)
            checked: New checked state
        """
        habit = self.habits[habit_idx]
        habit_id = habit['id']

        # Calculate date for this day index
        today = datetime.now()
        target_date = (today - timedelta(days=(2 - day_idx))).strftime("%Y-%m-%d")

        # Get habit details for points calculation
        db_habit = self.db.get_habit_by_id(habit_id)
        points = db_habit['points_per'] if checked else 0

        # Save to database
        self.db.log_habit_completion(
            habit_id=habit_id,
            date=target_date,
            completed=checked,
            skipped=False,
            quantity=1 if checked else 0,
            points_earned=points
        )

    def handle_input(self, event: InputEvent) -> Optional[str]:
        """
        Handle input for habit checker navigation.

        Two modes:
        - Habit selection: UP/DOWN to select habit, BUTTON_A to enter checkbox mode
        - Checkbox mode: LEFT/RIGHT to select day, BUTTON_A to toggle, BUTTON_B to exit

        Args:
            event: The input event

        Returns:
            Action string or None
        """
        if not event.pressed:
            return None

        # If no habits, only allow going back
        if not self.habits:
            if event.input_type == InputType.LEFT:
                return "menu"
            return None

        if not self.checkbox_mode:
            # Habit selection mode
            if event.input_type == InputType.UP:
                self.selected_habit = (self.selected_habit - 1) % len(self.habits)
            elif event.input_type == InputType.DOWN:
                self.selected_habit = (self.selected_habit + 1) % len(self.habits)
            elif event.input_type == InputType.BUTTON_A:
                # Enter checkbox mode
                self.checkbox_mode = True
            elif event.input_type == InputType.LEFT:
                # Go back to menu
                return "menu"
        else:
            # Checkbox mode
            if event.input_type == InputType.LEFT:
                self.selected_day = (self.selected_day - 1) % 3
            elif event.input_type == InputType.RIGHT:
                self.selected_day = (self.selected_day + 1) % 3
            elif event.input_type == InputType.BUTTON_A:
                # Toggle checkbox
                habit = self.habits[self.selected_habit]
                old_state = habit["checks"][self.selected_day]
                new_state = not old_state
                habit["checks"][self.selected_day] = new_state

                # Save to database
                self._save_checkbox(self.selected_habit, self.selected_day, new_state)
            elif event.input_type == InputType.BUTTON_B:
                # Exit checkbox mode
                self.checkbox_mode = False

        return None

    def update(self, delta_time: float) -> None:
        """Update screen state - handle text scrolling for long habit names."""
        # Scroll selected habit name if long and in habit selection mode
        if not self.checkbox_mode and self.selected_habit < len(self.habits):
            habit_name = self.habits[self.selected_habit]["name"]
            if len(habit_name) > self.MAX_NAME_LENGTH:
                self.scroll_timer += delta_time
                if self.scroll_timer >= self.scroll_delay:
                    self.scroll_timer = 0.0
                    self.scroll_offset = (self.scroll_offset + 1) % (len(habit_name) + 1)
            else:
                self.scroll_offset = 0
                self.scroll_timer = 0.0
        else:
            # Reset scroll when in checkbox mode or no habit selected
            self.scroll_offset = 0
            self.scroll_timer = 0.0

    def render(self, buffer: Image.Image) -> None:
        """
        Render the habit checker screen.

        Args:
            buffer: 128x128 PIL Image to render onto
        """
        # Draw background
        buffer.paste(self.background, (0, 0))

        draw = ImageDraw.Draw(buffer)
        draw.fontmode = '1'  # Disable anti-aliasing for pixel-perfect text

        # Render day letter headers
        for i, day_letter in enumerate(self.day_letters):
            x = self.CHECKBOX_START_X + i * self.CHECKBOX_SPACING

            # Center text over 8px-wide checkboxes
            if len(day_letter) == 2:
                # 2-letter days (Th, Su) - roughly 8-10px wide, add 1px to center
                x += 1
            else:
                # Single-letter days - roughly 4-5px wide, add 3px to center over 8px checkbox
                x += 3

            # Draw text directly for crisp rendering
            draw.text((x, self.DAY_LETTER_Y), day_letter, fill=Config.COLOR_TEXT_DARK, font=self.font)

        # Render habits and checkboxes
        for habit_idx, habit in enumerate(self.habits):
            y = self.HABIT_LIST_START_Y + habit_idx * self.LINE_HEIGHT

            # Handle habit name display (scrolling if selected, truncated if not)
            name = habit["name"]
            is_selected = habit_idx == self.selected_habit and not self.checkbox_mode

            if len(name) > self.MAX_NAME_LENGTH:
                if is_selected:
                    # Show scrolling text for selected habit
                    extended_name = name + "   " + name  # Add spacing and repeat
                    name = extended_name[self.scroll_offset:self.scroll_offset + self.MAX_NAME_LENGTH]
                else:
                    # Show truncated text for non-selected habits
                    name = name[:self.MAX_NAME_LENGTH - 1] + "..."

            # Highlight selected habit name (only in habit selection mode)
            text_color = Config.COLOR_BLUE_HIGHLIGHT if is_selected else Config.COLOR_TEXT_DARK

            # Draw text directly for crisp rendering
            draw.text((self.NAME_X, y), name, fill=text_color, font=self.font)

            # Render checkboxes for each day
            for day_idx, checked in enumerate(habit["checks"]):
                checkbox_x = self.CHECKBOX_START_X + day_idx * self.CHECKBOX_SPACING

                # Check if this checkbox is selected in checkbox mode
                is_selected = self.checkbox_mode and habit_idx == self.selected_habit and day_idx == self.selected_day

                # Choose sprite based on checked state and selection
                if is_selected:
                    # Use highlighted sprite
                    sprite = self.checked_highlight if checked else self.unchecked_highlight
                else:
                    # Use normal sprite
                    if checked:
                        sprite = self.icons_sheet.get_sprite(*icons.CHECKED_BOX_SMALL)
                    else:
                        sprite = self.icons_sheet.get_sprite(*icons.UNCHECKED_BOX_SMALL)

                # Paste checkbox sprite (moved up 5 pixels)
                checkbox_y = y - 5
                buffer.paste(sprite, (checkbox_x, checkbox_y), sprite if sprite.mode == "RGBA" else None)
