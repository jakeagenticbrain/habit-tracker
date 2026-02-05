"""Base classes and types for input handling."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum, auto


class InputType(Enum):
    """Types of inputs supported by the device."""
    # Joystick directions
    UP = auto()
    DOWN = auto()
    LEFT = auto()
    RIGHT = auto()

    # Physical buttons
    BUTTON_A = auto()  # Select/Confirm
    BUTTON_B = auto()  # Back/Cancel
    BUTTON_C = auto()  # Quick Action

    # System
    QUIT = auto()  # Window close or app quit


@dataclass
class InputEvent:
    """Represents a single input event."""
    input_type: InputType
    pressed: bool  # True for press, False for release


class InputBase(ABC):
    """Abstract base class for input handling.

    Implementations must provide a way to poll for input events from
    their respective hardware (keyboard, GPIO buttons, etc.).
    """

    @abstractmethod
    def poll(self) -> InputEvent | None:
        """Poll for the next input event.

        Returns:
            InputEvent if an event occurred, None otherwise.
        """
        pass
