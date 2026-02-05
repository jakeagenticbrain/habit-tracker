"""Tests for text input widget."""

import pytest
from game.text_input import TextInputWidget
from input.input_base import InputEvent, InputType


def test_initial_state():
    """Test widget initializes with empty value."""
    widget = TextInputWidget(max_length=16)
    assert widget.get_value() == ""
    assert widget.is_active() == False


def test_cycle_characters():
    """Test cycling through character set."""
    widget = TextInputWidget()
    widget.activate()

    initial_char = widget.get_current_char()
    widget.handle_input(InputEvent(InputType.RIGHT, True))
    next_char = widget.get_current_char()

    assert next_char != initial_char


def test_add_character():
    """Test confirming character adds to value."""
    widget = TextInputWidget()
    widget.activate()

    widget.handle_input(InputEvent(InputType.BUTTON_A, True))
    assert len(widget.get_value()) == 1


def test_delete_character():
    """Test deleting last character."""
    widget = TextInputWidget()
    widget.activate()

    widget.handle_input(InputEvent(InputType.BUTTON_A, True))  # Add one
    widget.handle_input(InputEvent(InputType.BUTTON_A, True))  # Add another
    assert len(widget.get_value()) == 2

    widget.handle_input(InputEvent(InputType.BUTTON_B, True))  # Delete
    assert len(widget.get_value()) == 1


def test_max_length_limit():
    """Test max length prevents overflow."""
    widget = TextInputWidget(max_length=3)
    widget.activate()

    for _ in range(5):
        widget.handle_input(InputEvent(InputType.BUTTON_A, True))

    assert len(widget.get_value()) == 3


def test_save_deactivates():
    """Test saving returns value and deactivates widget."""
    widget = TextInputWidget()
    widget.activate()

    widget.handle_input(InputEvent(InputType.BUTTON_A, True))
    result = widget.handle_input(InputEvent(InputType.BUTTON_C, True))

    assert result is not None  # Returns the saved value
    assert widget.is_active() == False
