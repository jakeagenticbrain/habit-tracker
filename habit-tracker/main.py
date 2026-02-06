#!/usr/bin/env python3
"""Entry point for the habit tracker application."""

import os
from game.app import App
from game.screens import HomeScreen, MenuScreen, HabitsScreen, StatsScreen
from game.habit_form_screen import HabitFormScreen
from game.settings_screen import SettingsScreen
from game.view_habits_screen import ViewHabitsScreen
from game.edit_habit_screen import EditHabitScreen
from game.habit_checker_screen import HabitCheckerScreen
from game.popup_screen import PopupScreen
from game.update_screen import UpdateScreen
from game.about_screen import AboutScreen
from config import Config
from data.db import Database


def is_raspberry_pi() -> bool:
    """Detect if running on Raspberry Pi by checking device tree.

    Returns:
        True if running on Raspberry Pi, False otherwise.
    """
    return os.path.exists('/proc/device-tree/model')


def main():
    """Initialize and run the habit tracker."""
    # Detect platform
    on_pi = is_raspberry_pi()

    # Create display and input handler based on platform
    if on_pi:
        print("Running on Raspberry Pi - using LCD display and GPIO input")
        from display.lcd_display import LCDDisplay
        from input.gpio_input import GPIOInput
        display = LCDDisplay(
            width=Config.DISPLAY_WIDTH,
            height=Config.DISPLAY_HEIGHT
        )
        input_handler = GPIOInput()
    else:
        print("Running on laptop - using Pygame display and keyboard input")
        from display.pygame_display import PygameDisplay
        from input.keyboard_input import KeyboardInput
        display = PygameDisplay(
            width=Config.DISPLAY_WIDTH,
            height=Config.DISPLAY_HEIGHT,
            scale=Config.DISPLAY_SCALE
        )
        input_handler = KeyboardInput()

    # Initialize database
    db = Database("habit_tracker.db")

    # Create screens
    screens = {
        "home": HomeScreen(),
        "menu": MenuScreen(),
        "habits": HabitsScreen(),
        "stats": StatsScreen(db),
        "settings": SettingsScreen(),
        "habit_form": HabitFormScreen(edit_mode=False),
        "habit_form_edit": HabitFormScreen(edit_mode=True),
        "view_habits": ViewHabitsScreen(db),  # Pass database
        "edit_habit": EditHabitScreen(db),  # Pass database, data loaded on navigation
        "habit_checker": HabitCheckerScreen(db),  # Pass database
        "popup_delete": PopupScreen(
            message="Are you sure you want to delete habit?",
            on_ok_screen="view_habits",
            on_cancel_screen="view_habits"
        ),
        "update": UpdateScreen(),
        "about": AboutScreen(),
    }

    # Create and run app
    app = App(
        display=display,
        input_handler=input_handler,
        screens=screens,
        initial_screen="home",
        target_fps=Config.TARGET_FPS
    )

    try:
        app.run()
    except KeyboardInterrupt:
        print("\nShutting down...")
    finally:
        if hasattr(input_handler, 'cleanup'):
            input_handler.cleanup()
        db.close()
        display.close()


if __name__ == "__main__":
    main()
