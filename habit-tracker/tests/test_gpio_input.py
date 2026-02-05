"""Tests for GPIO input implementation."""

import pytest
from unittest.mock import MagicMock, patch, call
from input.gpio_input import GPIOInput
from input.input_base import InputType, InputEvent


@patch('input.gpio_input.GPIO')
def test_gpio_input_init(mock_gpio):
    """Test that GPIOInput initializes GPIO pins correctly."""
    input_handler = GPIOInput()

    # Verify GPIO mode set to BCM
    mock_gpio.setmode.assert_called_once_with(mock_gpio.BCM)

    # Verify all 8 pins configured with pull-up resistors (active-low)
    expected_pins = [6, 19, 5, 26, 13, 21, 20, 16]  # UP, DOWN, LEFT, RIGHT, PRESS, KEY1, KEY2, KEY3

    assert mock_gpio.setup.call_count == 8
    for pin in expected_pins:
        mock_gpio.setup.assert_any_call(pin, mock_gpio.IN, pull_up_down=mock_gpio.PUD_UP)


@patch('input.gpio_input.GPIO')
def test_gpio_input_poll_joystick_up(mock_gpio):
    """Test that joystick UP press returns correct InputEvent."""
    mock_gpio.LOW = 0
    mock_gpio.HIGH = 1

    # Track state changes - initially all HIGH, then UP goes LOW
    call_count = [0]
    def mock_input(pin):
        call_count[0] += 1
        # During init, all pins HIGH
        if call_count[0] <= 8:
            return mock_gpio.HIGH
        # After init, UP pin goes LOW (pressed)
        return mock_gpio.LOW if pin == 6 else mock_gpio.HIGH

    mock_gpio.input.side_effect = mock_input

    input_handler = GPIOInput()
    event = input_handler.poll()

    assert event is not None
    assert event.input_type == InputType.UP
    assert event.pressed is True


@patch('input.gpio_input.GPIO')
def test_gpio_input_poll_button_a(mock_gpio):
    """Test that Button A (KEY1) press returns correct InputEvent."""
    mock_gpio.LOW = 0
    mock_gpio.HIGH = 1

    # Track state changes - initially all HIGH, then KEY1 goes LOW
    call_count = [0]
    def mock_input(pin):
        call_count[0] += 1
        # During init, all pins HIGH
        if call_count[0] <= 8:
            return mock_gpio.HIGH
        # After init, KEY1 pin goes LOW (pressed)
        return mock_gpio.LOW if pin == 21 else mock_gpio.HIGH

    mock_gpio.input.side_effect = mock_input

    input_handler = GPIOInput()
    event = input_handler.poll()

    assert event is not None
    assert event.input_type == InputType.BUTTON_A
    assert event.pressed is True


@patch('input.gpio_input.GPIO')
def test_gpio_input_poll_no_event(mock_gpio):
    """Test that no state changes returns None."""
    # Mock all pins as HIGH (not pressed)
    mock_gpio.input.return_value = mock_gpio.HIGH
    mock_gpio.HIGH = 1

    input_handler = GPIOInput()

    # First poll establishes baseline state
    event = input_handler.poll()

    # Second poll with no changes should return None
    event = input_handler.poll()
    assert event is None


@patch('input.gpio_input.GPIO')
def test_gpio_input_cleanup(mock_gpio):
    """Test that cleanup calls GPIO.cleanup()."""
    input_handler = GPIOInput()
    input_handler.cleanup()

    mock_gpio.cleanup.assert_called_once()


@patch('input.gpio_input.GPIO')
def test_gpio_input_poll_button_release(mock_gpio):
    """Test that button release returns correct InputEvent with pressed=False."""
    mock_gpio.LOW = 0
    mock_gpio.HIGH = 1

    # Track state through initialization and subsequent polls
    call_count = [0]
    state = ['init']  # init -> pressed -> released

    def mock_input(pin):
        call_count[0] += 1
        # During init (first 8 calls), all pins HIGH
        if call_count[0] <= 8:
            return mock_gpio.HIGH
        # After init, check current state
        if state[0] == 'pressed':
            return mock_gpio.LOW if pin == 21 else mock_gpio.HIGH
        else:  # released or subsequent states
            return mock_gpio.HIGH

    mock_gpio.input.side_effect = mock_input

    input_handler = GPIOInput()

    # First poll: Button A pressed (LOW)
    state[0] = 'pressed'
    event = input_handler.poll()
    assert event is not None
    assert event.input_type == InputType.BUTTON_A
    assert event.pressed is True

    # Second poll: Button A released (HIGH)
    state[0] = 'released'
    event = input_handler.poll()
    assert event is not None
    assert event.input_type == InputType.BUTTON_A
    assert event.pressed is False
