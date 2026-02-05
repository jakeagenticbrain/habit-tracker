"""Tests for Pygame display implementation."""

import pytest
from PIL import Image
from display.pygame_display import PygameDisplay


def test_pygame_display_initialization():
    """Test that PygameDisplay initializes with correct dimensions."""
    display = PygameDisplay(width=128, height=128)
    assert display.width == 128
    assert display.height == 128
    display.close()


def test_pygame_display_get_buffer():
    """Test that get_buffer returns a PIL Image of correct size."""
    display = PygameDisplay(width=128, height=128)
    buffer = display.get_buffer()

    assert isinstance(buffer, Image.Image)
    assert buffer.size == (128, 128)
    assert buffer.mode == 'RGB'

    display.close()


def test_pygame_display_update():
    """Test that update() doesn't crash and accepts PIL Image."""
    display = PygameDisplay(width=128, height=128)
    buffer = display.get_buffer()

    # Draw a red pixel
    buffer.putpixel((0, 0), (255, 0, 0))

    # Should not raise
    display.update(buffer)
    display.close()
