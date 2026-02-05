"""Tests for configuration module."""

import pytest
from config import Config


def test_config_display_dimensions():
    """Test display configuration values."""
    assert Config.DISPLAY_WIDTH == 128
    assert Config.DISPLAY_HEIGHT == 128
    assert Config.DISPLAY_SCALE == 4


def test_config_frame_rate():
    """Test frame rate configuration."""
    assert Config.TARGET_FPS == 20
    assert 15 <= Config.TARGET_FPS <= 20


def test_config_colors():
    """Test color definitions."""
    assert Config.COLOR_BLACK == (0, 0, 0)
    assert Config.COLOR_WHITE == (255, 255, 255)
    assert len(Config.COLOR_GREEN) == 3
    assert len(Config.COLOR_RED) == 3


def test_config_paths():
    """Test path configurations."""
    assert Config.DB_PATH == "habit_tracker.db"
    assert "assets" in Config.SPRITES_PATH


def test_config_sprite_file_paths():
    """Test sprite file path configurations."""
    assert "icons.png" in Config.ICONS_SPRITE_SHEET
    assert "progress-bars.png" in Config.PROGRESS_BARS_SPRITE_SHEET
    assert "lilguy.png" in Config.CHARACTER_SPRITE
    assert "sky-bg.png" in Config.BACKGROUND_SPRITE

    # Test FACE_SPRITES is a list of 6 items
    assert isinstance(Config.FACE_SPRITES, list)
    assert len(Config.FACE_SPRITES) == 6

    # Verify all expected face filenames are present
    expected_faces = [
        "face-happy.png",
        "face-sad.png",
        "face-oh.png",
        "face-bruh.png",
        "face-teeth-smile.png",
        "face-little-smile.png",
    ]
    for expected_face in expected_faces:
        assert any(expected_face in sprite_path for sprite_path in Config.FACE_SPRITES)


def test_config_font_paths():
    """Test font path configurations."""
    assert "fonts" in Config.FONTS_PATH
    assert "dogicapixel.ttf" in Config.FONT_REGULAR
    assert "dogicapixelbold.ttf" in Config.FONT_BOLD


def test_config_font_sizes():
    """Test font size configurations."""
    assert Config.FONT_SIZE_SMALL == 8
    assert Config.FONT_SIZE_NORMAL == 8
    assert Config.FONT_SIZE_LARGE == 16
