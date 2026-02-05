"""Tests for platform auto-detection in main.py"""

import pytest
from unittest.mock import patch, MagicMock


def test_detect_raspberry_pi_true():
    """Test that is_raspberry_pi returns True when device tree file exists."""
    from main import is_raspberry_pi

    with patch('os.path.exists') as mock_exists:
        mock_exists.return_value = True
        assert is_raspberry_pi() is True
        mock_exists.assert_called_once_with('/proc/device-tree/model')


def test_detect_raspberry_pi_false():
    """Test that is_raspberry_pi returns False when device tree file doesn't exist."""
    from main import is_raspberry_pi

    with patch('os.path.exists') as mock_exists:
        mock_exists.return_value = False
        assert is_raspberry_pi() is False
        mock_exists.assert_called_once_with('/proc/device-tree/model')


def test_main_creates_lcd_display_on_pi():
    """Test that main() uses LCDDisplay and GPIOInput when running on Pi."""
    from main import main

    with patch('main.is_raspberry_pi', return_value=True), \
         patch('main.LCDDisplay') as mock_lcd, \
         patch('main.GPIOInput') as mock_gpio, \
         patch('main.App') as mock_app, \
         patch('main.Database'):

        # Mock the app to prevent actual run
        mock_app_instance = MagicMock()
        mock_app.return_value = mock_app_instance

        try:
            main()
        except KeyboardInterrupt:
            pass

        # Verify LCDDisplay was created with correct params
        mock_lcd.assert_called_once()
        call_kwargs = mock_lcd.call_args[1]
        assert call_kwargs['width'] == 128
        assert call_kwargs['height'] == 128
        assert 'scale' not in call_kwargs

        # Verify GPIOInput was created
        mock_gpio.assert_called_once_with()


def test_main_creates_pygame_display_on_laptop():
    """Test that main() uses PygameDisplay and KeyboardInput when not on Pi."""
    from main import main

    with patch('main.is_raspberry_pi', return_value=False), \
         patch('main.PygameDisplay') as mock_pygame, \
         patch('main.KeyboardInput') as mock_keyboard, \
         patch('main.App') as mock_app, \
         patch('main.Database'):

        # Mock the app to prevent actual run
        mock_app_instance = MagicMock()
        mock_app.return_value = mock_app_instance

        try:
            main()
        except KeyboardInterrupt:
            pass

        # Verify PygameDisplay was created with correct params
        mock_pygame.assert_called_once()
        call_kwargs = mock_pygame.call_args[1]
        assert call_kwargs['width'] == 128
        assert call_kwargs['height'] == 128
        assert call_kwargs['scale'] == 4

        # Verify KeyboardInput was created
        mock_keyboard.assert_called_once_with()
