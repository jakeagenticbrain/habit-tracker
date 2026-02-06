"""Main application class and game loop."""

import time
from typing import Dict
from PIL import ImageDraw, ImageFont
from display.display_base import DisplayBase
from input.input_base import InputBase, InputType
from game.screens import ScreenBase


class App:
    """Main application with game loop."""

    def __init__(
        self,
        display: DisplayBase,
        input_handler: InputBase,
        screens: Dict[str, ScreenBase],
        initial_screen: str = "home",
        target_fps: int = 20
    ):
        """Initialize the application.

        Args:
            display: Display implementation
            input_handler: Input implementation
            screens: Dictionary mapping screen names to screen instances
            initial_screen: Name of the screen to show first (default "home")
            target_fps: Target frames per second (default 20)
        """
        self.display = display
        self.input_handler = input_handler
        self.screens = screens
        self.current_screen_name = initial_screen
        self.current_screen = screens[initial_screen]
        self.target_fps = target_fps
        self._frame_time = 1.0 / target_fps
        self.running = False

        # FPS tracking
        self._fps_counter = 0
        self._fps_timer = 0.0
        self._current_fps = 0

    def run(self) -> None:
        """Start the main game loop."""
        self.running = True
        last_time = time.time()

        print(f"Starting game loop at {self.target_fps} FPS...")
        print("Controls: WASD (joystick), P (Button A), L (Button B), M (Button C)")

        while self.running:
            current_time = time.time()
            delta_time = current_time - last_time

            # Process input
            self._handle_input()

            # Update game state
            self._update(delta_time)

            # Render frame
            self._render()

            # FPS tracking
            self._update_fps(delta_time)

            # Frame rate limiting
            elapsed = time.time() - current_time
            sleep_time = self._frame_time - elapsed
            if sleep_time > 0:
                time.sleep(sleep_time)

            last_time = current_time

        self.display.close()
        print("Game loop stopped.")

    def _handle_input(self) -> None:
        """Process input events."""
        event = self.input_handler.poll()

        if event is None:
            return

        # Handle quit
        if event.input_type == InputType.QUIT:
            self.running = False
            return

        # Delegate to current screen
        next_screen = self.current_screen.handle_input(event)

        # Handle screen transitions
        if next_screen and next_screen in self.screens:
            # Special handling for edit_habit screen - load selected habit data
            if next_screen == "edit_habit":
                from game.view_habits_screen import ViewHabitsScreen
                from game.edit_habit_screen import EditHabitScreen
                edit_screen = self.screens[next_screen]
                if isinstance(edit_screen, EditHabitScreen):
                    edit_screen.load_habit_data(ViewHabitsScreen.selected_habit_data)
            # Special handling for view_habits screen - reload habit list
            elif next_screen == "view_habits":
                from game.view_habits_screen import ViewHabitsScreen
                view_screen = self.screens[next_screen]
                if isinstance(view_screen, ViewHabitsScreen):
                    view_screen.reload_habits()
            # Special handling for habit_checker screen - reload habit list
            elif next_screen == "habit_checker":
                from game.habit_checker_screen import HabitCheckerScreen
                checker_screen = self.screens[next_screen]
                if isinstance(checker_screen, HabitCheckerScreen):
                    checker_screen.reload_habits()

            self.current_screen_name = next_screen
            self.current_screen = self.screens[next_screen]
            print(f"Switched to screen: {next_screen}")

    def _update(self, delta_time: float) -> None:
        """Update game state.

        Args:
            delta_time: Time since last frame in seconds
        """
        # Delegate to current screen
        self.current_screen.update(delta_time)

    def _render(self) -> None:
        """Render the current frame."""
        # Get drawing buffer
        buffer = self.display.get_buffer()

        # Delegate to current screen
        self.current_screen.render(buffer)

        # Update display
        self.display.update(buffer)

    def _update_fps(self, delta_time: float) -> None:
        """Update FPS counter.

        Args:
            delta_time: Time since last frame in seconds
        """
        self._fps_counter += 1
        self._fps_timer += delta_time

        # Update FPS display every second
        if self._fps_timer >= 1.0:
            self._current_fps = self._fps_counter
            self._fps_counter = 0
            self._fps_timer = 0.0
