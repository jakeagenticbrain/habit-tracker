#!/usr/bin/env python3
"""Entry point for the habit tracker application."""

from display.pygame_display import PygameDisplay
from input.keyboard_input import KeyboardInput
from game.app import App
from game.screens import HomeScreen, MenuScreen, HabitsScreen, StatsScreen
from game.habit_form_screen import HabitFormScreen
from game.settings_screen import SettingsScreen
from game.view_habits_screen import ViewHabitsScreen
from game.edit_habit_screen import EditHabitScreen
from game.habit_checker_screen import HabitCheckerScreen
from game.popup_screen import PopupScreen
from config import Config
from data.db import Database


def main():
    """Initialize and run the habit tracker."""
    # Create display using config
    display = PygameDisplay(
        width=Config.DISPLAY_WIDTH,
        height=Config.DISPLAY_HEIGHT,
        scale=Config.DISPLAY_SCALE
    )

    # Create input handler
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
        db.close()
        display.close()


if __name__ == "__main__":
    main()
