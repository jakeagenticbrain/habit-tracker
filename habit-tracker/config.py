"""Configuration constants for the habit tracker."""

import os


class Config:
    """Application configuration."""

    # Display settings
    DISPLAY_WIDTH = 128
    DISPLAY_HEIGHT = 128
    DISPLAY_SCALE = 4  # Scale factor (1 = native 128x128, 4 = 512x512)

    # Performance settings
    TARGET_FPS = 20  # Target 15-20 FPS for Pi Zero

    # Colors (RGB tuples)
    COLOR_BLACK = (0, 0, 0)
    COLOR_WHITE = (255, 255, 255)
    COLOR_GREEN = (0, 255, 0)
    COLOR_RED = (255, 0, 0)
    COLOR_BLUE = (0, 150, 255)
    COLOR_YELLOW = (255, 255, 0)
    COLOR_GRAY = (128, 128, 128)
    COLOR_DARK_GRAY = (64, 64, 64)

    # New UI colors for habit screens
    COLOR_BLUE_HIGHLIGHT = (91, 110, 225)  # #5b6ee1 - selected text
    COLOR_TEXT_DARK = (50, 60, 57)         # #323c39 - main text
    COLOR_CHECKBOX_INACTIVE = (155, 173, 183)  # #9badb7 - inactive checkboxes

    # Paths
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    ASSETS_PATH = os.path.join(BASE_DIR, "assets")
    SPRITES_PATH = os.path.join(ASSETS_PATH, "sprites")
    FONTS_PATH = os.path.join(ASSETS_PATH, "fonts")
    DB_PATH = "habit_tracker.db"

    # Sprite files
    ICONS_SPRITE_SHEET = os.path.join(SPRITES_PATH, "icons.png")
    PROGRESS_BARS_SPRITE_SHEET = os.path.join(SPRITES_PATH, "progress-bars.png")
    HIGHLIGHTED_CHECKBOXES = os.path.join(SPRITES_PATH, "highlighted-checkboxes.png")
    BACKGROUND_SPRITE = os.path.join(SPRITES_PATH, "sky-bg.png")
    CHARACTER_SPRITE = os.path.join(SPRITES_PATH, "lilguy.png")
    FACE_SPRITES = [
        os.path.join(SPRITES_PATH, "face-happy.png"),
        os.path.join(SPRITES_PATH, "face-sad.png"),
        os.path.join(SPRITES_PATH, "face-oh.png"),
        os.path.join(SPRITES_PATH, "face-bruh.png"),
        os.path.join(SPRITES_PATH, "face-teeth-smile.png"),
        os.path.join(SPRITES_PATH, "face-little-smile.png"),
    ]

    # Animated sprite sheets (64x64 per frame, needs 2x scaling to 128x128)
    CHARACTER_ANIM_SPRITE = os.path.join(SPRITES_PATH, "lilguy-animated.png")
    FACE_ANIM_SPRITES = {
        "happy": os.path.join(SPRITES_PATH, "face-happy-animated.png"),
        "bruh": os.path.join(SPRITES_PATH, "face-bruh-animated.png"),
        "oh": os.path.join(SPRITES_PATH, "face-oh-animated.png"),
        "teeth-smile": os.path.join(SPRITES_PATH, "face-teeth-smile-animated.png"),
        "little-smile": os.path.join(SPRITES_PATH, "face-little-smile-animated.png"),
    }

    # Speech bubble sprites (64x64, needs 2x scaling to 128x128)
    SPEECH_BUBBLE_STATIC = os.path.join(SPRITES_PATH, "speech-bubble.png")
    SPEECH_BUBBLE_ANIM_SHEET = os.path.join(SPRITES_PATH, "speech-bubble-sheet.png")

    # Animation settings
    ANIM_FRAME_DELAY = 0.15  # 150ms per frame (~6.7 FPS for character animation)
    SPEECH_BUBBLE_FRAME_DELAY = 0.1  # 100ms per frame for speech bubble animation

    # New UI screen backgrounds
    SETTINGS_BG = os.path.join(SPRITES_PATH, "settings-page", "settings-bg.png")
    HABIT_SETTINGS_BG = os.path.join(SPRITES_PATH, "habit-settings-page", "habit-settings-page-bg.png")
    EDIT_HABIT_BG = os.path.join(SPRITES_PATH, "edit-habits-settings-page", "edit-habit-bg.png")
    HABIT_CHECKER_BG = os.path.join(SPRITES_PATH, "habit-checker-page", "habits-checker-bg.png")
    POPUP_BG = os.path.join(SPRITES_PATH, "popup", "popup-bg.png")
    UPDATE_POPUP_BG = os.path.join(SPRITES_PATH, "popup", "update-popup.png")

    # UI button sprites
    NEW_HABIT_BUTTON_NORMAL = os.path.join(SPRITES_PATH, "habit-settings-page", "new-habit-button-normal.png")
    NEW_HABIT_BUTTON_HIGHLIGHTED = os.path.join(SPRITES_PATH, "habit-settings-page", "new-habit-button-highlighted.png")
    POPUP_OK_HIGHLIGHTED = os.path.join(SPRITES_PATH, "popup", "ok-highlighted.png")
    POPUP_CANCEL_HIGHLIGHTED = os.path.join(SPRITES_PATH, "popup", "cancel-highlighted.png")
    INPUT_TEXT_POPUP = os.path.join(SPRITES_PATH, "popup", "typing-popup.png")

    # Edit Habit Screen button sprites
    SAVE_BUTTON_HIGHLIGHTED = os.path.join(SPRITES_PATH, "edit-habits-settings-page", "save-highlighted.png")
    CANCEL_BUTTON_HIGHLIGHTED = os.path.join(SPRITES_PATH, "edit-habits-settings-page", "cancel-highlighted.png")
    SAVE_CANCEL_NORMAL = os.path.join(SPRITES_PATH, "edit-habits-settings-page", "save-cancel-not-highlighted.png")

    # Font files
    FONT_REGULAR = os.path.join(FONTS_PATH, "dogicapixel.ttf")
    FONT_BOLD = os.path.join(FONTS_PATH, "dogicapixelbold.ttf")

    # Font sizes (pixel fonts work best at native size or small multiples)
    FONT_SIZE_TINY = 6    # For tiny text on habit screens
    FONT_SIZE_SMALL = 8   # For labels, small text
    FONT_SIZE_NORMAL = 8  # For regular text
    FONT_SIZE_LARGE = 16  # For headings

    # Character settings
    HUNGER_DECAY_RATE = 1  # Points per hour
    MAX_HUNGER = 100
    MAX_HAPPINESS = 100

    # Habit settings
    DEFAULT_GRACE_PERIOD = 60  # minutes
