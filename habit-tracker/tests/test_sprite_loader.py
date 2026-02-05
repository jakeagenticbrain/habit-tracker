"""Tests for sprite loading functionality."""

import pytest
from PIL import Image
from assets.sprite_loader import SpriteSheet, get_progress_bar_for_percentage
from config import Config


@pytest.fixture
def icon_sheet():
    """Load the icons sprite sheet for testing."""
    return SpriteSheet('assets/sprites/icons.png', tile_width=16, tile_height=16)


def test_sprite_sheet_initialization(icon_sheet):
    """Test that SpriteSheet loads correctly."""
    assert icon_sheet.sheet is not None
    assert icon_sheet.width == 128
    assert icon_sheet.height == 128
    assert icon_sheet.tile_width == 16
    assert icon_sheet.tile_height == 16


def test_get_sprite_returns_correct_size(icon_sheet):
    """Test that get_sprite returns 16x16 image."""
    sprite = icon_sheet.get_sprite(0, 0)

    assert isinstance(sprite, Image.Image)
    assert sprite.size == (16, 16)


def test_get_sprite_caching(icon_sheet):
    """Test that sprites are cached after first extraction."""
    sprite1 = icon_sheet.get_sprite(4, 0)  # pointer-large
    sprite2 = icon_sheet.get_sprite(4, 0)  # same sprite

    # Should be the exact same cached object
    assert sprite1 is sprite2


def test_get_row_returns_correct_size(icon_sheet):
    """Test that get_row returns full-width 128x16 image."""
    row_sprite = icon_sheet.get_row(3)  # progress-bar-0

    assert isinstance(row_sprite, Image.Image)
    assert row_sprite.size == (128, 16)


def test_get_row_caching(icon_sheet):
    """Test that rows are cached after first extraction."""
    row1 = icon_sheet.get_row(3)  # progress-bar-0
    row2 = icon_sheet.get_row(3)  # same row

    # Should be the exact same cached object
    assert row1 is row2


def test_get_sprites_range(icon_sheet):
    """Test extracting a range of sprites."""
    # Extract 2x2 grid starting at (0, 1) - checkbox icons
    sprites = icon_sheet.get_sprites_range(0, 1, 1, 2)

    assert len(sprites) == 4
    assert all(isinstance(s, Image.Image) for s in sprites)
    assert all(s.size == (16, 16) for s in sprites)


def test_progress_bar_percentage_mapping_0_percent():
    """Test that 0% maps to progress-bar-0 (icons.png row 3)."""
    info = get_progress_bar_for_percentage(0)
    assert info.sheet_name == 'icons'
    assert info.row == 3


def test_progress_bar_percentage_mapping_100_percent():
    """Test that 100% maps to progress-bar-80 (progress-bars.png row 3)."""
    info = get_progress_bar_for_percentage(100)
    assert info.sheet_name == 'progress-bars'
    assert info.row == 3


def test_progress_bar_percentage_mapping_mid_values():
    """Test that mid-range percentages map correctly."""
    # 25% should round to 20 (icons.png row 5)
    info = get_progress_bar_for_percentage(25)
    assert info.sheet_name == 'icons'
    assert info.row == 5

    # 67% should round to 70 (progress-bars.png row 2)
    info = get_progress_bar_for_percentage(67)
    assert info.sheet_name == 'progress-bars'
    assert info.row == 2

    # 50% should be (progress-bars.png row 0)
    info = get_progress_bar_for_percentage(50)
    assert info.sheet_name == 'progress-bars'
    assert info.row == 0


def test_progress_bar_percentage_clamping():
    """Test that values outside 0-100 are clamped."""
    # Negative should clamp to 0
    info = get_progress_bar_for_percentage(-10)
    assert info.sheet_name == 'icons'
    assert info.row == 3

    # Over 100 should clamp to 100 (progress-bar-80)
    info = get_progress_bar_for_percentage(150)
    assert info.sheet_name == 'progress-bars'
    assert info.row == 3


def test_progress_bar_percentage_mapping_0_percent():
    """Test that 0% maps to progress-bar-0 (icons.png row 3)."""
    info = get_progress_bar_for_percentage(0)
    assert info.sheet_name == 'icons'
    assert info.row == 3


def test_progress_bar_percentage_mapping_100_percent():
    """Test that 100% maps to progress-bar-80 (progress-bars.png row 3)."""
    info = get_progress_bar_for_percentage(100)
    assert info.sheet_name == 'progress-bars'
    assert info.row == 3


def test_progress_bar_percentage_mapping_mid_values():
    """Test that mid-range percentages map correctly."""
    # 25% should round to 20 (icons.png row 5)
    info = get_progress_bar_for_percentage(25)
    assert info.sheet_name == 'icons'
    assert info.row == 5

    # 67% should round to 70 (progress-bars.png row 2)
    info = get_progress_bar_for_percentage(67)
    assert info.sheet_name == 'progress-bars'
    assert info.row == 2

    # 50% should be (progress-bars.png row 0)
    info = get_progress_bar_for_percentage(50)
    assert info.sheet_name == 'progress-bars'
    assert info.row == 0


def test_progress_bar_percentage_clamping():
    """Test that values outside 0-100 are clamped."""
    # Negative should clamp to 0
    info = get_progress_bar_for_percentage(-10)
    assert info.sheet_name == 'icons'
    assert info.row == 3

    # Over 100 should clamp to 100 (progress-bar-80)
    info = get_progress_bar_for_percentage(150)
    assert info.sheet_name == 'progress-bars'
    assert info.row == 3


def test_character_sprite_loads():
    """Test that the character sprite loads correctly."""
    char_sprite = Image.open(Config.CHARACTER_SPRITE)

    assert char_sprite is not None
    assert char_sprite.mode == 'RGBA'  # Should have transparency
    assert char_sprite.size[0] > 0  # Has width
    assert char_sprite.size[1] > 0  # Has height


def test_load_font():
    """Test that load_font loads a TrueType font."""
    from assets.sprite_loader import load_font
    from PIL import ImageFont

    font = load_font(Config.FONT_REGULAR, 8)

    assert font is not None
    assert isinstance(font, ImageFont.FreeTypeFont)


def test_load_font_caching():
    """Test that fonts are cached."""
    from assets.sprite_loader import load_font

    font1 = load_font(Config.FONT_REGULAR, 8)
    font2 = load_font(Config.FONT_REGULAR, 8)

    # Should be the exact same cached object
    assert font1 is font2


def test_render_text_returns_image():
    """Test that render_text returns a PIL Image."""
    from assets.sprite_loader import render_text

    text_img = render_text("Hello", Config.FONT_REGULAR, 8)

    assert isinstance(text_img, Image.Image)
    assert text_img.size[0] > 0  # Has width
    assert text_img.size[1] > 0  # Has height


def test_render_text_with_background():
    """Test rendering text with background color."""
    from assets.sprite_loader import render_text

    text_img = render_text(
        "Test",
        Config.FONT_REGULAR,
        8,
        color=(255, 255, 255),
        background=(0, 0, 0)
    )

    assert text_img.mode == 'RGB'
    assert text_img.getpixel((0, 0)) == (0, 0, 0)  # Background is black


def test_render_text_transparent_background():
    """Test rendering text with transparent background."""
    from assets.sprite_loader import render_text

    text_img = render_text("Test", Config.FONT_REGULAR, 8)

    assert text_img.mode == 'RGBA'  # Should have alpha channel
