"""Screen implementations for the habit tracker UI."""

from abc import ABC, abstractmethod
from PIL import Image, ImageDraw
from typing import Optional
from datetime import datetime, timedelta
from input.input_base import InputEvent, InputType
from assets.sprite_loader import SpriteSheet, get_progress_bar_for_percentage, load_font, render_text
from assets import icons
from config import Config
from game.speech_bubble import SpeechBubbleWidget


class ScreenBase(ABC):
    """Abstract base class for screens."""

    @abstractmethod
    def handle_input(self, event: InputEvent) -> Optional[str]:
        """Handle input event.

        Args:
            event: Input event to process

        Returns:
            Screen name to navigate to, or None to stay on current screen
        """
        pass

    @abstractmethod
    def update(self, delta_time: float) -> None:
        """Update screen state.

        Args:
            delta_time: Time since last frame in seconds
        """
        pass

    @abstractmethod
    def render(self, buffer: Image.Image) -> None:
        """Render screen to buffer.

        Args:
            buffer: PIL Image to draw to
        """
        pass


class HomeScreen(ScreenBase):
    """Home screen showing layered character with animated expressions."""

    def __init__(self):
        """Initialize home screen with animated character sprites."""
        # Load and scale background to 128x128 (2x from 64x64 source)
        bg_raw = Image.open(Config.BACKGROUND_SPRITE)
        self.background = bg_raw.resize((128, 128), Image.NEAREST)

        # Load animated body sprite sheet (4 frames, 64x64 each)
        body_sheet = SpriteSheet(Config.CHARACTER_ANIM_SPRITE, 64, 64)
        self.body_frames = []
        for i in range(4):  # 4 frames
            frame_64 = body_sheet.get_sprite(i, 0)  # Get 64x64 frame
            frame_128 = frame_64.resize((128, 128), Image.NEAREST)  # Scale to 128x128
            self.body_frames.append(frame_128)

        # Load animated face sprite sheets (4 frames each, 64x64)
        self.face_animations = {}
        for face_name, face_path in Config.FACE_ANIM_SPRITES.items():
            face_sheet = SpriteSheet(face_path, 64, 64)
            frames = []
            for i in range(4):  # 4 frames per expression
                frame_64 = face_sheet.get_sprite(i, 0)
                frame_128 = frame_64.resize((128, 128), Image.NEAREST)
                frames.append(frame_128)
            self.face_animations[face_name] = frames

        # Animation state
        self.current_frame = 0
        self.frame_timer = 0.0
        self.frame_delay = Config.ANIM_FRAME_DELAY

        # Current facial expression
        self.face_names = list(self.face_animations.keys())
        self.current_face_index = 0

        # Speech bubble widget
        self.speech_bubble = SpeechBubbleWidget()

    def handle_input(self, event: InputEvent) -> Optional[str]:
        """Handle input - Button B toggles speech, Button C cycles faces, L/R navigate."""
        if not event.pressed:
            return None

        # Button B toggles speech bubble
        if event.input_type == InputType.BUTTON_B:
            self.speech_bubble.toggle("Hello World")
            return None

        # Button C cycles facial expressions
        if event.input_type == InputType.BUTTON_C:
            self.current_face_index = (self.current_face_index + 1) % len(self.face_names)
            return None

        # Navigate right to menu
        if event.input_type == InputType.RIGHT:
            return "menu"

        # Navigate left to stats
        if event.input_type == InputType.LEFT:
            return "stats"

        return None

    def update(self, delta_time: float) -> None:
        """Update animation frames."""
        # Advance animation timer
        self.frame_timer += delta_time

        # Advance to next frame when timer exceeds delay
        if self.frame_timer >= self.frame_delay:
            self.frame_timer = 0.0
            self.current_frame = (self.current_frame + 1) % 4  # Loop through 4 frames

        # Update speech bubble
        self.speech_bubble.update(delta_time)

    def render(self, buffer: Image.Image) -> None:
        """Render layered animated character sprites."""
        # Layer 1: Background (sky) - static
        buffer.paste(self.background, (0, 0))

        # Layer 2: Character body - animated
        body_frame = self.body_frames[self.current_frame]
        buffer.paste(body_frame, (0, 0), body_frame)

        # Layer 3: Current facial expression - animated
        current_face_name = self.face_names[self.current_face_index]
        face_frame = self.face_animations[current_face_name][self.current_frame]
        buffer.paste(face_frame, (0, 0), face_frame)

        # Layer 4: Speech bubble (if visible)
        self.speech_bubble.render(buffer)


class MenuScreen(ScreenBase):
    """Menu screen with navigation options."""

    def __init__(self):
        """Initialize menu screen."""
        self.icons_sheet = SpriteSheet(Config.ICONS_SPRITE_SHEET)
        self.menu_items = [
            ("Home", icons.HOME_ICON),
            ("Habits", icons.CHECKED_BOX_LARGE),
            ("Stats", icons.STAR_LARGE),
            ("Settings", icons.SETTINGS_ICON),
        ]
        self.selected_index = 0

    def handle_input(self, event: InputEvent) -> Optional[str]:
        """Handle input - up/down to navigate, P to select, left to go back."""
        if not event.pressed:
            return None

        if event.input_type == InputType.UP:
            self.selected_index = (self.selected_index - 1) % len(self.menu_items)
        elif event.input_type == InputType.DOWN:
            self.selected_index = (self.selected_index + 1) % len(self.menu_items)
        elif event.input_type == InputType.BUTTON_A:
            # Navigate to selected screen
            selected_name = self.menu_items[self.selected_index][0].lower()
            # Map "habits" to "habit_checker" screen
            if selected_name == "habits":
                return "habit_checker"
            return selected_name
        elif event.input_type == InputType.LEFT:
            return "home"

        return None

    def update(self, delta_time: float) -> None:
        """Update menu screen."""
        pass

    def render(self, buffer: Image.Image) -> None:
        """Render menu screen."""
        draw = ImageDraw.Draw(buffer)

        # White background
        draw.rectangle([(0, 0), (128, 128)], fill=(255, 255, 255))

        # Draw title
        title_text = render_text("MENU", Config.FONT_BOLD, Config.FONT_SIZE_LARGE, color=(0, 0, 0))
        title_x = (128 - title_text.width) // 2
        buffer.paste(title_text, (title_x, 10), title_text)

        # Draw menu items
        y_offset = 40
        pointer = self.icons_sheet.get_sprite(*icons.POINTER_SMALL)

        for i, (name, icon_coords) in enumerate(self.menu_items):
            # Draw pointer if selected
            if i == self.selected_index:
                buffer.paste(pointer, (10, y_offset), pointer)

            # Draw icon
            icon = self.icons_sheet.get_sprite(*icon_coords)
            buffer.paste(icon, (30, y_offset), icon)

            # Draw text
            text = render_text(name, Config.FONT_REGULAR, Config.FONT_SIZE_NORMAL, color=(0, 0, 0))
            buffer.paste(text, (50, y_offset + 4), text)

            y_offset += 20


class HabitsScreen(ScreenBase):
    """Habits screen with toggleable checkboxes."""

    def __init__(self):
        """Initialize habits screen."""
        self.icons_sheet = SpriteSheet(Config.ICONS_SPRITE_SHEET)
        self.habits = [
            {"name": "Gym", "completed": False, "icon": icons.STAR_SMALL},
            {"name": "Meditate", "completed": False, "icon": icons.HEART_SMALL},
            {"name": "Water 8x", "completed": True, "icon": icons.COFFEE_ICON},
            {"name": "Read 1hr", "completed": False, "icon": icons.TEA_ICON},
        ]
        # Add special "+ Add Habit" item at end
        self.menu_items = self.habits + [{"name": "+ Add Habit", "is_add_button": True}]
        self.selected_index = 0

    def handle_input(self, event: InputEvent) -> Optional[str]:
        """Handle input - up/down to navigate, P to toggle or add, left to go back."""
        if not event.pressed:
            return None

        if event.input_type == InputType.UP:
            self.selected_index = (self.selected_index - 1) % len(self.menu_items)
        elif event.input_type == InputType.DOWN:
            self.selected_index = (self.selected_index + 1) % len(self.menu_items)
        elif event.input_type == InputType.BUTTON_A:
            selected_item = self.menu_items[self.selected_index]

            # Check if "Add Habit" button
            if selected_item.get("is_add_button"):
                return "habit_form"

            # Otherwise toggle habit completion
            habit_index = self.selected_index
            self.habits[habit_index]["completed"] = not self.habits[habit_index]["completed"]
        elif event.input_type == InputType.BUTTON_B:
            # Edit selected habit (if not add button)
            selected_item = self.menu_items[self.selected_index]
            if not selected_item.get("is_add_button"):
                return "habit_form_edit"
        elif event.input_type == InputType.LEFT:
            return "menu"
        elif event.input_type == InputType.RIGHT:
            return "home"

        return None

    def update(self, delta_time: float) -> None:
        """Update habits screen."""
        pass

    def render(self, buffer: Image.Image) -> None:
        """Render habits screen."""
        draw = ImageDraw.Draw(buffer)

        # White background
        draw.rectangle([(0, 0), (128, 128)], fill=(255, 255, 255))

        # Draw title
        title_text = render_text("HABITS", Config.FONT_BOLD, Config.FONT_SIZE_LARGE, color=(0, 0, 0))
        title_x = (128 - title_text.width) // 2
        buffer.paste(title_text, (title_x, 5), title_text)

        # Draw menu items (habits + add button)
        y_offset = 25
        pointer = self.icons_sheet.get_sprite(*icons.POINTER_SMALL)

        for i, item in enumerate(self.menu_items):
            # Draw pointer if selected
            if i == self.selected_index:
                buffer.paste(pointer, (5, y_offset), pointer)

            # Check if this is the add button
            if item.get("is_add_button"):
                # Draw "+" icon or text
                plus_text = render_text(item["name"], Config.FONT_BOLD, Config.FONT_SIZE_NORMAL, color=(0, 128, 0))
                buffer.paste(plus_text, (20, y_offset + 2), plus_text)
            else:
                # Draw checkbox
                if item["completed"]:
                    checkbox = self.icons_sheet.get_sprite(*icons.CHECKED_BOX_SMALL)
                else:
                    checkbox = self.icons_sheet.get_sprite(*icons.UNCHECKED_BOX_SMALL)
                buffer.paste(checkbox, (20, y_offset), checkbox)

                # Draw habit icon
                habit_icon = self.icons_sheet.get_sprite(*item["icon"])
                buffer.paste(habit_icon, (40, y_offset), habit_icon)

                # Draw habit name
                text = render_text(item["name"], Config.FONT_REGULAR, Config.FONT_SIZE_NORMAL, color=(0, 0, 0))
                buffer.paste(text, (60, y_offset + 4), text)

            y_offset += 16

        # Draw navigation hint
        hint_text = render_text("P=Select L=Edit", Config.FONT_REGULAR, Config.FONT_SIZE_SMALL, color=(128, 128, 128))
        buffer.paste(hint_text, (8, 112), hint_text)


class StatsScreen(ScreenBase):
    """Stats screen showing character metrics with progress bars."""

    def __init__(self, db=None):
        """Initialize stats screen.

        Args:
            db: Database instance for loading stats (None for mock mode)
        """
        self.db = db
        self.icons_sheet = SpriteSheet(Config.ICONS_SPRITE_SHEET)
        self.progress_sheet = SpriteSheet(Config.PROGRESS_BARS_SPRITE_SHEET)

        # Character state (demo values that cycle)
        self.hunger = 50
        self.happiness = 70

        # Stats data
        self.points_data = []
        self.completion_stats = []
        self.total_points = 0
        self.completion_rate = 0

        # Load stats from database
        self._load_stats()

    def _load_stats(self):
        """Load stats from database for past 7 days."""
        if self.db is None:
            # Mock data mode
            return

        # Get date range (past 7 days)
        today = datetime.now()
        end_date = today.strftime("%Y-%m-%d")
        start_date = (today - timedelta(days=6)).strftime("%Y-%m-%d")

        # Get points by day
        self.points_data = self.db.get_points_by_day(start_date, end_date)

        # Get completion stats
        self.completion_stats = self.db.get_completion_stats(start_date, end_date)

        # Calculate totals
        self.total_points = sum(day['total_points'] for day in self.points_data)

        # Calculate average completion rate
        if self.completion_stats:
            total_completed = sum(s['completed_count'] for s in self.completion_stats)
            total_possible = sum(s['total_days'] for s in self.completion_stats)
            self.completion_rate = (total_completed / total_possible * 100) if total_possible > 0 else 0
        else:
            self.completion_rate = 0

    def handle_input(self, event: InputEvent) -> Optional[str]:
        """Handle input - buttons cycle progress bars."""
        if not event.pressed:
            return None

        # Cycle progress bars on button press
        if event.input_type in [InputType.BUTTON_A, InputType.BUTTON_B, InputType.BUTTON_C]:
            self.hunger = (self.hunger + 10) % 110  # 0-100 cycling
            self.happiness = (self.happiness + 15) % 110
            return None

        # Navigate left to home
        if event.input_type == InputType.LEFT:
            return "home"

        # Navigate right to menu
        if event.input_type == InputType.RIGHT:
            return "menu"

        return None

    def update(self, delta_time: float) -> None:
        """Update stats screen."""
        pass

    def render(self, buffer: Image.Image) -> None:
        """Render stats screen."""
        draw = ImageDraw.Draw(buffer)

        # White background
        draw.rectangle([(0, 0), (128, 128)], fill=(255, 255, 255))

        # Draw title
        title_text = render_text("STATS", Config.FONT_BOLD, Config.FONT_SIZE_LARGE, color=(0, 0, 0))
        title_x = (128 - title_text.width) // 2
        buffer.paste(title_text, (title_x, 5), title_text)

        # Display stats
        stats_y = 25

        # Total points (past 7 days)
        points_text = render_text(f"Points: {self.total_points}", Config.FONT_REGULAR, Config.FONT_SIZE_NORMAL, color=(0, 0, 0))
        buffer.paste(points_text, (10, stats_y), points_text)

        # Completion rate
        completion_text = render_text(f"Done: {self.completion_rate:.0f}%", Config.FONT_REGULAR, Config.FONT_SIZE_NORMAL, color=(0, 0, 0))
        buffer.paste(completion_text, (10, stats_y + 15), completion_text)

        # Draw "HUNGER" label
        hunger_text = render_text("HUNGER", Config.FONT_REGULAR, Config.FONT_SIZE_SMALL, color=(0, 0, 0))
        buffer.paste(hunger_text, (10, 55), hunger_text)

        # Draw hunger progress bar
        hunger_info = get_progress_bar_for_percentage(self.hunger)
        if hunger_info.sheet_name == 'icons':
            hunger_bar = self.icons_sheet.get_row(hunger_info.row)
        else:
            hunger_bar = self.progress_sheet.get_row(hunger_info.row)
        buffer.paste(hunger_bar, (0, 65), hunger_bar)

        # Draw "HAPPY" label
        happy_text = render_text("HAPPY", Config.FONT_REGULAR, Config.FONT_SIZE_SMALL, color=(0, 0, 0))
        buffer.paste(happy_text, (10, 80), happy_text)

        # Draw happiness progress bar
        happy_info = get_progress_bar_for_percentage(self.happiness)
        if happy_info.sheet_name == 'icons':
            happy_bar = self.icons_sheet.get_row(happy_info.row)
        else:
            happy_bar = self.progress_sheet.get_row(happy_info.row)
        buffer.paste(happy_bar, (0, 90), happy_bar)

        # Habit breakdown (top 3 habits)
        if self.completion_stats:
            breakdown_y = 105
            for i, stat in enumerate(self.completion_stats[:3]):
                habit_name = stat['habit_name'][:8]  # Truncate to 8 chars
                habit_text = render_text(f"{habit_name} {stat['completed_count']}/{stat['total_days']}",
                                         Config.FONT_REGULAR, Config.FONT_SIZE_SMALL, color=(80, 80, 80))
                buffer.paste(habit_text, (5, breakdown_y), habit_text)
                breakdown_y += 8

        # Draw navigation hint
        hint_text = render_text("P=Cycle L/R=Nav", Config.FONT_REGULAR, Config.FONT_SIZE_SMALL, color=(128, 128, 128))
        buffer.paste(hint_text, (10, 112), hint_text)


class SettingsScreen(ScreenBase):
    """Placeholder settings screen."""

    def __init__(self):
        """Initialize settings screen."""
        pass

    def handle_input(self, event: InputEvent) -> Optional[str]:
        """Handle input - just allow navigation back."""
        if not event.pressed:
            return None

        if event.input_type == InputType.LEFT:
            return "menu"

        return None

    def update(self, delta_time: float) -> None:
        """Update settings screen."""
        pass

    def render(self, buffer: Image.Image) -> None:
        """Render placeholder settings screen."""
        draw = ImageDraw.Draw(buffer)
        draw.rectangle([(0, 0), (128, 128)], fill=(255, 255, 255))

        title_text = render_text("SETTINGS", Config.FONT_BOLD, Config.FONT_SIZE_LARGE, color=(0, 0, 0))
        title_x = (128 - title_text.width) // 2
        buffer.paste(title_text, (title_x, 50), title_text)

        hint_text = render_text("(Coming soon...)", Config.FONT_REGULAR, Config.FONT_SIZE_SMALL, color=(128, 128, 128))
        hint_x = (128 - hint_text.width) // 2
        buffer.paste(hint_text, (hint_x, 70), hint_text)
