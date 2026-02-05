"""Keyboard input implementation for laptop development."""

import pygame
from .input_base import InputBase, InputEvent, InputType


class KeyboardInput(InputBase):
    """Maps keyboard keys to input events for development on laptop.

    Key mappings:
    - W/A/S/D: Joystick (Up/Left/Down/Right)
    - P: Button A (Select/Confirm)
    - L: Button B (Back/Cancel)
    - M: Button C (Quick Action)
    """

    def __init__(self):
        """Initialize keyboard input handler."""
        pygame.init()

        # Map pygame key constants to InputType
        self.key_map = {
            # Joystick directions
            pygame.K_w: InputType.UP,
            pygame.K_s: InputType.DOWN,
            pygame.K_a: InputType.LEFT,
            pygame.K_d: InputType.RIGHT,

            # Buttons
            pygame.K_p: InputType.BUTTON_A,
            pygame.K_l: InputType.BUTTON_B,
            pygame.K_m: InputType.BUTTON_C,
        }

    def poll(self) -> InputEvent | None:
        """Poll for keyboard events.

        Returns:
            InputEvent if a mapped key was pressed/released, None otherwise.
        """
        for event in pygame.event.get():
            # Handle quit event
            if event.type == pygame.QUIT:
                return InputEvent(input_type=InputType.QUIT, pressed=True)

            # Handle key presses
            if event.type == pygame.KEYDOWN:
                if event.key in self.key_map:
                    return InputEvent(
                        input_type=self.key_map[event.key],
                        pressed=True
                    )
            elif event.type == pygame.KEYUP:
                if event.key in self.key_map:
                    return InputEvent(
                        input_type=self.key_map[event.key],
                        pressed=False
                    )

        return None
