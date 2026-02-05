"""Edit habit screen with multi-field form for creating/editing habits."""

from PIL import Image, ImageDraw
from typing import Optional
from input.input_base import InputEvent, InputType
from game.screens import ScreenBase
from game.text_input import TextInputWidget
from assets.sprite_loader import SpriteSheet, render_text
from assets import icons
from config import Config
from data.db import Database


class EditHabitScreen(ScreenBase):
    """Edit habit screen with multi-field form.

    Fields:
        - Name: Text input (last 6 chars shown, full edit via popup)
        - Freq: Two-stage (number 1-6, then period day/week)
        - Points: 1-20 adjustable
        - Active: Toggle checkbox
        - Reminder: Toggle checkbox

    Controls:
        - UP/DOWN: Navigate fields
        - BUTTON_A: Edit field / toggle checkbox
        - LEFT: Go back
        - BUTTON_C: Save (when editing name)
    """

    FIELD_NAMES = ["Name", "Freq", "Points", "Type", "Active", "Reminder"]
    FIELD_START_Y = 35  # Moved down from 25
    LINE_HEIGHT = 12
    LABEL_X = 13  # Labels start at x=13
    VALUE_X = 73  # Right column starts at x=73

    # Frequency period options
    FREQ_PERIODS = ["day", "week"]

    def __init__(self, db: Database, habit_data: Optional[dict] = None):
        """Initialize edit habit screen.

        Args:
            db: Database instance for saving habits
            habit_data: Dict with habit fields (None for new habit, must include 'id' for edit)
        """
        self.icons_sheet = SpriteSheet(Config.ICONS_SPRITE_SHEET, 16, 16)

        # Load background - convert RGBA to RGB to avoid transparency
        bg_rgba = Image.open(Config.EDIT_HABIT_BG).convert("RGBA")
        self.background = Image.new("RGB", bg_rgba.size, (255, 255, 255))
        self.background.paste(bg_rgba, (0, 0), bg_rgba)

        # Store database and habit_id
        self.db = db
        self.habit_id = habit_data.get('id') if habit_data else None

        # Load input popup (shown when editing name)
        self.input_popup = Image.open(Config.INPUT_TEXT_POPUP).convert("RGBA")

        # Load button sprites
        self.save_cancel_normal = Image.open(Config.SAVE_CANCEL_NORMAL).convert("RGBA")
        self.save_highlighted = Image.open(Config.SAVE_BUTTON_HIGHLIGHTED).convert("RGBA")
        self.cancel_highlighted = Image.open(Config.CANCEL_BUTTON_HIGHLIGHTED).convert("RGBA")

        # Load font for crisp text rendering
        from assets.sprite_loader import load_font
        self.font = load_font(Config.FONT_REGULAR, 8)

        # Text input widget for name editing
        self.text_input = TextInputWidget(max_length=20)

        # Field values (default or from habit_data)
        if habit_data:
            self.name = habit_data.get("name", "")
            self.freq_number = habit_data.get("freq_number", 1)
            self.freq_period = habit_data.get("freq_period", "day")
            self.points = habit_data.get("points", 5)
            self.is_good = habit_data.get("is_good", True)
            self.active = habit_data.get("active", True)
            self.reminder = habit_data.get("reminder", False)
        else:
            # Default values for new habit
            self.name = ""
            self.freq_number = 1
            self.freq_period = "day"
            self.points = 5
            self.is_good = True
            self.active = True
            self.reminder = False

        # Field selection (-1 when buttons are selected)
        self.selected_field = 0  # 0=Name, 1=Freq, 2=Points, 3=Type, 4=Active, 5=Reminder

        # Editing states
        self.editing_name = False
        self.editing_freq = False
        self.freq_edit_stage = 0  # 0=number, 1=period
        self.editing_points = False

        # Button selection state
        self.selected_button = None  # None, "save", or "cancel"

        # Text scrolling state for long names
        self.scroll_offset = 0
        self.scroll_timer = 0.0
        self.scroll_delay = 0.15  # Seconds between scroll steps

    def load_habit_data(self, habit_data: Optional[dict] = None):
        """Load habit data for editing (called when navigating to this screen).

        Args:
            habit_data: Dict with habit fields (None for new habit)
        """
        if habit_data:
            self.name = habit_data.get("name", "")
            self.freq_number = habit_data.get("freq_num", habit_data.get("freq_number", 1))
            self.freq_period = habit_data.get("freq_period", "day")
            self.points = habit_data.get("points", 5)
            self.is_good = habit_data.get("is_good", True)
            self.active = habit_data.get("active", True)
            self.reminder = habit_data.get("reminder", False)
            self.habit_id = habit_data.get('id')
        else:
            # Default values for new habit
            self.name = ""
            self.freq_number = 1
            self.freq_period = "day"
            self.points = 5
            self.is_good = True
            self.active = True
            self.reminder = False
            self.habit_id = None

        # Reset editing states
        self.selected_field = 0
        self.editing_name = False
        self.editing_freq = False
        self.freq_edit_stage = 0
        self.editing_points = False
        self.selected_button = None
        self.text_input.value = self.name

    def save_habit(self) -> None:
        """Save habit to database (create new or update existing)."""
        # Format recurrence as "num/period"
        recurrence = f"{self.freq_number}/{self.freq_period}"

        # Determine category from is_good
        category = "good" if self.is_good else "bad"

        if self.habit_id is None:
            # Create new habit
            self.habit_id = self.db.add_habit(
                name=self.name,
                habit_type="binary",  # TODO: Add type selection in UI
                points_per=self.points,
                category=category,
                recurrence=recurrence
            )
        else:
            # Update existing habit
            self.db.update_habit(
                habit_id=self.habit_id,
                name=self.name,
                habit_type="binary",  # TODO: Add type selection in UI
                points_per=self.points,
                category=category,
                recurrence=recurrence,
                active=self.active
            )

    def _get_display_name(self) -> str:
        """Get display name with scrolling when selected, truncated when not.

        Returns:
            Scrolling name if selected, truncated if not, full if <= 6 chars
        """
        if len(self.name) <= 6:
            return self.name

        # If Name field is selected (not editing), show scrolling text
        if self.selected_field == 0 and not self.editing_name:
            # Show 6 characters starting from scroll_offset
            # Wrap around with padding for smooth loop
            extended_name = self.name + "   " + self.name  # Add spacing and repeat
            return extended_name[self.scroll_offset:self.scroll_offset + 6]
        else:
            # Not selected - show first 5 chars + "..."
            return self.name[:5] + "..."

    def _get_freq_display(self) -> str:
        """Get frequency display string.

        Returns:
            String like "1/day" or "3/week"
        """
        return f"{self.freq_number}/{self.freq_period}"

    def handle_input(self, event: InputEvent) -> Optional[str]:
        """Handle input events.

        Args:
            event: Input event to process

        Returns:
            Screen name to navigate to, or None
        """
        if not event.pressed:
            return None

        # If editing name, delegate to text input widget
        if self.editing_name:
            result = self.text_input.handle_input(event)

            # BUTTON_C saves and exits name editing
            if event.input_type == InputType.BUTTON_C:
                self.name = self.text_input.get_value()
                self.editing_name = False
                self.text_input.deactivate()
                return None

            # Check if text input returned a value (shouldn't happen with BUTTON_C)
            if result is not None:
                self.name = result
                self.editing_name = False

            return None

        # LEFT/RIGHT: Adjust values when editing, navigate buttons, or go back
        if event.input_type in [InputType.LEFT, InputType.RIGHT]:
            # If on buttons, navigate between save/cancel
            if self.selected_button is not None:
                if event.input_type == InputType.LEFT:
                    self.selected_button = "save"  # Save button is on the left
                else:  # RIGHT
                    self.selected_button = "cancel"  # Cancel button is on the right
            # If editing freq or points, adjust values
            elif self.editing_freq:
                direction = 1 if event.input_type == InputType.RIGHT else -1
                if self.freq_edit_stage == 0:
                    # Adjust number (1-6)
                    self.freq_number = max(1, min(6, self.freq_number + direction))
                else:
                    # Cycle period (day/week)
                    current_idx = self.FREQ_PERIODS.index(self.freq_period)
                    new_idx = (current_idx + direction) % len(self.FREQ_PERIODS)
                    self.freq_period = self.FREQ_PERIODS[new_idx]
            elif self.editing_points:
                direction = 1 if event.input_type == InputType.RIGHT else -1
                self.points = max(1, min(20, self.points + direction))

        # UP/DOWN: Navigate fields or buttons (only when not editing)
        elif event.input_type == InputType.UP:
            if not (self.editing_freq or self.editing_points or self.editing_name):
                if self.selected_button is not None:
                    # Move from buttons back to fields
                    self.selected_button = None
                    self.selected_field = len(self.FIELD_NAMES) - 1  # Select last field
                else:
                    self.selected_field = (self.selected_field - 1) % len(self.FIELD_NAMES)

        elif event.input_type == InputType.DOWN:
            if not (self.editing_freq or self.editing_points or self.editing_name):
                if self.selected_field == len(self.FIELD_NAMES) - 1:
                    # At last field, move down to buttons
                    self.selected_button = "save"  # Default to save button
                    self.selected_field = -1  # Deselect fields
                elif self.selected_button is None:
                    self.selected_field = (self.selected_field + 1) % len(self.FIELD_NAMES)

        # BUTTON_A: Edit field / toggle checkbox / trigger button action
        elif event.input_type == InputType.BUTTON_A:
            # If button is selected, trigger its action
            if self.selected_button == "save":
                if self.name:  # Only save if name is not empty
                    self.save_habit()
                    return "view_habits"
                # TODO: Could show validation message if name is empty
            elif self.selected_button == "cancel":
                return "view_habits"  # Go back without saving

            # Field selection logic (existing code)
            # Name field: Enter text editing mode
            elif self.selected_field == 0:
                self.editing_name = True
                self.text_input.activate()
                # Initialize text input with current name
                self.text_input.value = self.name

            # Freq field: Two-stage editing
            elif self.selected_field == 1:
                if not self.editing_freq:
                    self.editing_freq = True
                    self.freq_edit_stage = 0
                else:
                    # Move to next stage or finish
                    if self.freq_edit_stage == 0:
                        self.freq_edit_stage = 1
                    else:
                        self.editing_freq = False
                        self.freq_edit_stage = 0

            # Points field: Enter editing mode
            elif self.selected_field == 2:
                self.editing_points = not self.editing_points

            # Type field: Toggle between Good and Bad
            elif self.selected_field == 3:
                self.is_good = not self.is_good

            # Active checkbox: Toggle
            elif self.selected_field == 4:
                self.active = not self.active

            # Reminder checkbox: Toggle
            elif self.selected_field == 5:
                self.reminder = not self.reminder

        return None

    def update(self, delta_time: float) -> None:
        """Update screen state.

        Args:
            delta_time: Time since last frame in seconds
        """
        # Update text input widget if active
        if self.editing_name:
            self.text_input.update(delta_time)

        # Scroll long name text when Name field is selected (not editing)
        if self.selected_field == 0 and not self.editing_name and len(self.name) > 6:
            self.scroll_timer += delta_time
            if self.scroll_timer >= self.scroll_delay:
                self.scroll_timer = 0.0
                self.scroll_offset = (self.scroll_offset + 1) % (len(self.name) + 1)
        else:
            # Reset scroll when not on Name field
            self.scroll_offset = 0
            self.scroll_timer = 0.0

    def render(self, buffer: Image.Image) -> None:
        """Render edit habit screen.

        Args:
            buffer: PIL Image to draw to
        """
        # Draw background (RGB, no transparency)
        buffer.paste(self.background, (0, 0))

        # Draw directly on buffer for crisp text
        draw = ImageDraw.Draw(buffer)
        draw.fontmode = '1'  # Disable anti-aliasing for pixel-perfect text

        # Render each field
        for i, field_name in enumerate(self.FIELD_NAMES):
            y = self.FIELD_START_Y + (i * self.LINE_HEIGHT)
            is_selected = (i == self.selected_field)

            # Determine field value and editing state
            if i == 0:  # Name
                value = self._get_display_name()
                is_editing = self.editing_name
            elif i == 1:  # Freq
                value = self._get_freq_display()
                is_editing = self.editing_freq
            elif i == 2:  # Points
                value = str(self.points)
                is_editing = self.editing_points
            elif i == 3:  # Type (Good/Bad)
                value = "Good" if self.is_good else "Bad"
                is_editing = False
            elif i == 4:  # Active
                value = None  # Checkbox
                is_editing = False
            else:  # Reminder
                value = None  # Checkbox
                is_editing = False

            # Render label directly
            # When editing freq/points, label should be black (focus moves to value)
            if i in [1, 2] and is_editing:
                label_color = Config.COLOR_TEXT_DARK
            else:
                label_color = Config.COLOR_BLUE_HIGHLIGHT if is_selected else Config.COLOR_TEXT_DARK
            draw.text((self.LABEL_X, y), field_name + ":", fill=label_color, font=self.font)

            # Render value or checkbox
            if value is not None:
                # Special handling for Freq field - always split to keep positioning consistent
                if i == 1:
                    # Split "3/day" into "3" and "/day"
                    freq_num_str = str(self.freq_number)
                    freq_period_str = f"/{self.freq_period}"

                    # Color based on editing state
                    if self.editing_freq:
                        if self.freq_edit_stage == 0:
                            # Editing number - highlight number only
                            num_color = Config.COLOR_BLUE_HIGHLIGHT
                            period_color = Config.COLOR_TEXT_DARK
                        else:
                            # Editing period - highlight period only
                            num_color = Config.COLOR_TEXT_DARK
                            period_color = Config.COLOR_BLUE_HIGHLIGHT
                    else:
                        # Not editing - both same color
                        num_color = Config.COLOR_TEXT_DARK
                        period_color = Config.COLOR_TEXT_DARK

                    # Draw number
                    draw.text((self.VALUE_X, y), freq_num_str, fill=num_color, font=self.font)

                    # Calculate x offset for period (after number) using font metrics
                    bbox = draw.textbbox((0, 0), freq_num_str, font=self.font)
                    num_width = bbox[2] - bbox[0]
                    period_x = self.VALUE_X + num_width

                    # Draw period
                    draw.text((period_x, y), freq_period_str, fill=period_color, font=self.font)

                # Special handling for Type field - show text only (no checkbox)
                elif i == 3:
                    # Draw "Good" or "Bad" text
                    value_color = Config.COLOR_TEXT_DARK
                    draw.text((self.VALUE_X, y), value, fill=value_color, font=self.font)

                else:
                    # Text value - draw directly
                    value_color = Config.COLOR_BLUE_HIGHLIGHT if is_editing else Config.COLOR_TEXT_DARK
                    draw.text((self.VALUE_X, y), value, fill=value_color, font=self.font)
            else:
                # Checkbox (for Active and Reminder fields)
                if i == 4:  # Active
                    checked = self.active
                else:  # Reminder
                    checked = self.reminder

                if checked:
                    checkbox = self.icons_sheet.get_sprite(*icons.CHECKED_BOX_SMALL)
                else:
                    checkbox = self.icons_sheet.get_sprite(*icons.UNCHECKED_BOX_SMALL)

                # Center checkbox vertically with text (checkbox is 8px, move up 6px)
                # Moved 7 pixels right for better spacing with 8pt text
                buffer.paste(checkbox, (self.VALUE_X + 7, y - 6), checkbox)

        # Render input popup at bottom if editing name
        if self.editing_name:
            # Paste popup background at bottom of screen
            popup_y = 128 - self.input_popup.height
            buffer.paste(self.input_popup, (0, popup_y), self.input_popup)

            # Render text input widget on top of popup
            # Position it centered in the popup area
            self.text_input.render(buffer, x=10, y=popup_y + 8)

        # Render save/cancel buttons at bottom (always visible)
        # Base layer - both buttons not highlighted
        buffer.paste(self.save_cancel_normal, (0, 0), self.save_cancel_normal)

        # Overlay highlighted button if one is selected
        if self.selected_button == "save":
            buffer.paste(self.save_highlighted, (0, 0), self.save_highlighted)
        elif self.selected_button == "cancel":
            buffer.paste(self.cancel_highlighted, (0, 0), self.cancel_highlighted)
