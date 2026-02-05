"""Tests for LCD display implementation."""

import sys
import pytest
from unittest.mock import MagicMock
from PIL import Image


# Create mock ST7735 module before importing lcd_display
mock_st7735_module = MagicMock()
sys.modules['ST7735'] = mock_st7735_module


def test_lcd_display_init():
    """Test that LCDDisplay initializes with correct dimensions and calls ST7735."""
    # Reset the mock
    mock_st7735_module.reset_mock()

    # Create a mock instance
    mock_instance = MagicMock()
    mock_st7735_module.ST7735.return_value = mock_instance

    from display.lcd_display import LCDDisplay

    display = LCDDisplay(width=128, height=128)

    assert display.width == 128
    assert display.height == 128

    # Verify ST7735 was called with correct GPIO pins and SPI speed
    mock_st7735_module.ST7735.assert_called_once()
    call_kwargs = mock_st7735_module.ST7735.call_args[1]
    assert call_kwargs['dc'] == 25
    assert call_kwargs['rst'] == 27
    assert call_kwargs['backlight'] == 24
    assert call_kwargs['spi_speed_hz'] == 4000000

    # Verify begin was called
    mock_instance.begin.assert_called_once()

    display.close()


def test_lcd_display_get_buffer():
    """Test that get_buffer returns RGB Image of size (128, 128)."""
    # Reset the mock
    mock_st7735_module.reset_mock()

    mock_instance = MagicMock()
    mock_st7735_module.ST7735.return_value = mock_instance

    from display.lcd_display import LCDDisplay

    display = LCDDisplay(width=128, height=128)
    buffer = display.get_buffer()

    assert isinstance(buffer, Image.Image)
    assert buffer.size == (128, 128)
    assert buffer.mode == 'RGB'

    display.close()


def test_lcd_display_update():
    """Test that update sends buffer to LCD via ST7735 display method."""
    # Reset the mock
    mock_st7735_module.reset_mock()

    # Setup mock
    mock_instance = MagicMock()
    mock_st7735_module.ST7735.return_value = mock_instance

    from display.lcd_display import LCDDisplay

    display = LCDDisplay(width=128, height=128)
    buffer = display.get_buffer()

    # Draw a red pixel
    buffer.putpixel((0, 0), (255, 0, 0))

    # Update display
    display.update(buffer)

    # Verify display method was called with a PIL Image
    mock_instance.display.assert_called_once()
    call_args = mock_instance.display.call_args[0]
    assert isinstance(call_args[0], Image.Image)

    display.close()


def test_lcd_display_close():
    """Test that close cleans up resources."""
    # Reset the mock
    mock_st7735_module.reset_mock()

    mock_instance = MagicMock()
    mock_st7735_module.ST7735.return_value = mock_instance

    from display.lcd_display import LCDDisplay

    display = LCDDisplay(width=128, height=128)

    # Should not raise
    display.close()
