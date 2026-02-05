"""Abstract base class for display implementations."""

from abc import ABC, abstractmethod
from PIL import Image


class DisplayBase(ABC):
    """Abstract interface for display output."""

    def __init__(self, width: int, height: int):
        """Initialize display with dimensions.

        Args:
            width: Display width in pixels
            height: Display height in pixels
        """
        self.width = width
        self.height = height

    @abstractmethod
    def get_buffer(self) -> Image.Image:
        """Get a PIL Image buffer for drawing.

        Returns:
            PIL Image object of size (width, height) in RGB mode
        """
        pass

    @abstractmethod
    def update(self, buffer: Image.Image) -> None:
        """Update the display with the provided buffer.

        Args:
            buffer: PIL Image to display
        """
        pass

    @abstractmethod
    def close(self) -> None:
        """Clean up display resources."""
        pass
