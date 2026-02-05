"""Habit form screen for adding/editing habits (UI demo)."""

from PIL import Image, ImageDraw
from typing import Optional
from game.screens import ScreenBase
from game.text_input import TextInputWidget
from game.ui_components import draw_panel, draw_list_item, draw_button_hint, draw_divider
from input.input_base import InputEvent, InputType
from assets.sprite_loader import render_text
from config import Config


class HabitFormScreen(ScreenBase):
    """Form screen for adding/editing habits.

    Fields:
        - Name (text input)
        - Type (Binary/Incremental - cycle with left/right)
        - Points (text input - numbers only)
        - Target Time (text input - e.g., "09:00")
        - Days (MTWTFSS - toggle each day)

    Navigation:
        - UP/DOWN: Navigate between fields
        - LEFT/RIGHT: Cycle options (for Type field)
        - BUTTON_A: Activate field for editing
        - BUTTON_B: Go back/cancel
        - BUTTON_C: Save (returns to habits screen)
    """

    HABIT_TYPES = ["Binary", "Incremental"]
    DAYS_OF_WEEK = ["M", "T", "W", "T", "F", "S", "S"]

    def __init__(self, edit_mode: bool = False):
        """Initialize habit form screen.

        Args:
            edit_mode: True if editing existing habit, False if adding new
        """
        self.edit_mode = edit_mode
        self.text_input = TextInputWidget(max_length=16)

        # Form fields
        self.fields = [
            "Name",
            "Type",
            "Points",
            "Time",
            "Days"
        ]
        self.current_field_index = 0

        # Form values (demo placeholders)
        self.form_data = {
            "Name": "Gym" if edit_mode else "",
            "Type": 0,  # Index into HABIT_TYPES
            "Points": "8" if edit_mode else "5",
            "Time": "09:00" if edit_mode else "",
            "Days": [True, True, True, True, True, False, False]  # MTWTF enabled
        }

        # Track which field is being edited
        self.editing_field = None
        self.days_selected_index = 0  # For navigating days toggles

    def handle_input(self, event: InputEvent) -> Optional[str]:
        """Handle input for form navigation and editing."""
        if not event.pressed:
            return None

        # If text input is active, route to it
        if self.text_input.is_active():
            result = self.text_input.handle_input(event)
            if result is not None:
                # Save result to appropriate field
                if self.editing_field == "Name":
                    self.form_data["Name"] = result
                elif self.editing_field == "Points":
                    self.form_data["Points"] = result
                elif self.editing_field == "Time":
                    self.form_data["Time"] = result
                self.editing_field = None
            return None

        # If editing days field
        if self.editing_field == "Days":
            if event.input_type == InputType.LEFT:
                self.days_selected_index = (self.days_selected_index - 1) % 7
            elif event.input_type == InputType.RIGHT:
                self.days_selected_index = (self.days_selected_index + 1) % 7
            elif event.input_type == InputType.BUTTON_A:
                # Toggle selected day
                self.form_data["Days"][self.days_selected_index] = not self.form_data["Days"][self.days_selected_index]
            elif event.input_type == InputType.BUTTON_B:
                # Done editing days
                self.editing_field = None
            return None

        # Normal navigation
        if event.input_type == InputType.UP:
            self.current_field_index = (self.current_field_index - 1) % len(self.fields)
        elif event.input_type == InputType.DOWN:
            self.current_field_index = (self.current_field_index + 1) % len(self.fields)

        # Activate field for editing
        elif event.input_type == InputType.BUTTON_A:
            current_field = self.fields[self.current_field_index]

            if current_field == "Name":
                self.editing_field = "Name"
                self.text_input.activate()
                self.text_input.value = self.form_data["Name"]
            elif current_field == "Points":
                self.editing_field = "Points"
                self.text_input.activate()
                self.text_input.value = self.form_data["Points"]
            elif current_field == "Time":
                self.editing_field = "Time"
                self.text_input.activate()
                self.text_input.value = self.form_data["Time"]
            elif current_field == "Days":
                self.editing_field = "Days"
                self.days_selected_index = 0

        # Cycle Type field with left/right
        elif event.input_type in [InputType.LEFT, InputType.RIGHT]:
            if self.fields[self.current_field_index] == "Type":
                direction = 1 if event.input_type == InputType.RIGHT else -1
                self.form_data["Type"] = (self.form_data["Type"] + direction) % len(self.HABIT_TYPES)

        # Cancel/Back
        elif event.input_type == InputType.BUTTON_B:
            return "habits"

        # Save (demo - just go back)
        elif event.input_type == InputType.BUTTON_C:
            # In real app, would save to database here
            return "habits"

        return None

    def update(self, delta_time: float) -> None:
        """Update form screen state."""
        self.text_input.update(delta_time)

    def render(self, buffer: Image.Image) -> None:
        """Render habit form screen."""
        draw = ImageDraw.Draw(buffer)

        # White background
        draw.rectangle([(0, 0), (128, 128)], fill=(255, 255, 255))

        # If text input is active, render it instead
        if self.text_input.is_active():
            # Title
            title = "Edit Name" if self.editing_field == "Name" else f"Edit {self.editing_field}"
            title_img = render_text(title, Config.FONT_BOLD, Config.FONT_SIZE_NORMAL, color=(0, 0, 0))
            title_x = (128 - title_img.width) // 2
            buffer.paste(title_img, (title_x, 8), title_img)

            draw_divider(buffer, 20)
            self.text_input.render(buffer, x=4, y=24)
            return

        # Title
        title_text = "Edit Habit" if self.edit_mode else "Add Habit"
        title_img = render_text(title_text, Config.FONT_BOLD, Config.FONT_SIZE_LARGE, color=(0, 0, 0))
        title_x = (128 - title_img.width) // 2
        buffer.paste(title_img, (title_x, 4), title_img)

        draw_divider(buffer, 16)

        # Form fields
        y_offset = 20

        for i, field_name in enumerate(self.fields):
            is_selected = (i == self.current_field_index) and (self.editing_field is None)
            is_editing = (self.editing_field == field_name)

            # Field label
            label_color = (0, 0, 0) if is_selected or is_editing else (100, 100, 100)
            label_img = render_text(f"{field_name}:", Config.FONT_REGULAR, Config.FONT_SIZE_SMALL, color=label_color)
            buffer.paste(label_img, (4, y_offset), label_img)

            # Field value
            value_x = 40
            if field_name == "Name":
                value = self.form_data["Name"] if self.form_data["Name"] else "_____"
                value_img = render_text(value, Config.FONT_REGULAR, Config.FONT_SIZE_NORMAL, color=(0, 0, 0))
                buffer.paste(value_img, (value_x, y_offset), value_img)

            elif field_name == "Type":
                type_text = self.HABIT_TYPES[self.form_data["Type"]]
                if is_selected:
                    type_text = f"< {type_text} >"
                value_img = render_text(type_text, Config.FONT_REGULAR, Config.FONT_SIZE_NORMAL, color=(0, 0, 0))
                buffer.paste(value_img, (value_x, y_offset), value_img)

            elif field_name == "Points":
                value = self.form_data["Points"] if self.form_data["Points"] else "__"
                value_img = render_text(value, Config.FONT_REGULAR, Config.FONT_SIZE_NORMAL, color=(0, 0, 0))
                buffer.paste(value_img, (value_x, y_offset), value_img)

            elif field_name == "Time":
                value = self.form_data["Time"] if self.form_data["Time"] else "__:__"
                value_img = render_text(value, Config.FONT_REGULAR, Config.FONT_SIZE_NORMAL, color=(0, 0, 0))
                buffer.paste(value_img, (value_x, y_offset), value_img)

            elif field_name == "Days":
                # Draw day toggles
                day_x = value_x
                for day_idx, day_label in enumerate(self.DAYS_OF_WEEK):
                    is_enabled = self.form_data["Days"][day_idx]
                    is_day_selected = is_editing and (day_idx == self.days_selected_index)

                    # Background for selected day
                    if is_day_selected:
                        draw.rectangle((day_x - 1, y_offset - 1, day_x + 7, y_offset + 9), fill=(200, 200, 200))

                    day_color = (0, 0, 0) if is_enabled else (180, 180, 180)
                    day_img = render_text(day_label, Config.FONT_REGULAR, Config.FONT_SIZE_SMALL, color=day_color)
                    buffer.paste(day_img, (day_x, y_offset), day_img)
                    day_x += 10

            # Selection indicator
            if is_selected:
                draw.rectangle((2, y_offset - 1, 3, y_offset + 9), fill=(0, 0, 0))

            y_offset += 16

        # Button hints
        draw_divider(buffer, 108)
        if self.editing_field == "Days":
            draw_button_hint(buffer, 4, 112, "P=Toggle L/R=Day L=Done")
        else:
            draw_button_hint(buffer, 4, 112, "P=Edit M=Save L=Back")
