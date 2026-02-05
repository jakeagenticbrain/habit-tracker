"""Tests for keyboard input implementation."""

import pytest
import pygame
from input.keyboard_input import KeyboardInput
from input.input_base import InputType


def test_keyboard_input_initialization():
    """Test that KeyboardInput initializes correctly."""
    input_handler = KeyboardInput()
    assert input_handler is not None


def test_keyboard_input_poll_no_events():
    """Test polling with no events returns None."""
    pygame.init()
    input_handler = KeyboardInput()

    # Clear event queue
    pygame.event.clear()

    event = input_handler.poll()
    assert event is None

    pygame.quit()


def test_keyboard_input_mapping():
    """Test that key mappings are defined correctly."""
    input_handler = KeyboardInput()

    # Check joystick mappings
    assert pygame.K_w in input_handler.key_map
    assert input_handler.key_map[pygame.K_w] == InputType.UP
    assert input_handler.key_map[pygame.K_s] == InputType.DOWN
    assert input_handler.key_map[pygame.K_a] == InputType.LEFT
    assert input_handler.key_map[pygame.K_d] == InputType.RIGHT

    # Check button mappings
    assert input_handler.key_map[pygame.K_p] == InputType.BUTTON_A
    assert input_handler.key_map[pygame.K_l] == InputType.BUTTON_B
    assert input_handler.key_map[pygame.K_m] == InputType.BUTTON_C
