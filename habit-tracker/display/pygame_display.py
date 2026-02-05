"""Pygame-based display for laptop development."""

import os
import pygame
from PIL import Image
from .display_base import DisplayBase


class PygameDisplay(DisplayBase):
    """Display implementation using Pygame window."""

    def __init__(self, width: int = 128, height: int = 128, scale: int = 4):
        """Initialize Pygame display.

        Args:
            width: Logical display width in pixels (default 128)
            height: Logical display height in pixels (default 128)
            scale: Scale factor for window size (default 4 = 512x512 window)
        """
        super().__init__(width, height)
        self.scale = scale

        # CRITICAL: Force nearest-neighbor scaling for pixel-perfect rendering
        # This must be set BEFORE pygame.init()
        os.environ['SDL_RENDER_SCALE_QUALITY'] = '0'  # 0 = nearest, 1 = linear, 2 = best

        pygame.init()
        self.window = pygame.display.set_mode((width * scale, height * scale))
        pygame.display.set_caption("Habit Tracker - Pi Zero Simulator")

        self._buffer = Image.new('RGB', (width, height), color=(0, 0, 0))

    def get_buffer(self) -> Image.Image:
        """Get a PIL Image buffer for drawing.

        Returns:
            PIL Image object of size (width, height) in RGB mode
        """
        return self._buffer.copy()

    def update(self, buffer: Image.Image) -> None:
        """Update the display with the provided buffer.

        Args:
            buffer: PIL Image to display
        """
        # PIXEL-PERFECT SCALING: Scale the PIL image BEFORE converting to Pygame
        # This avoids Pygame's transform altogether
        scaled_pil = buffer.resize(
            (self.width * self.scale, self.height * self.scale),
            Image.NEAREST  # Nearest-neighbor, no interpolation
        )

        # Convert scaled PIL Image to Pygame surface
        mode = scaled_pil.mode
        size = scaled_pil.size
        data = scaled_pil.tobytes()

        surface = pygame.image.fromstring(data, size, mode)

        # Draw to window (no scaling needed - already done in PIL)
        self.window.blit(surface, (0, 0))
        pygame.display.flip()

        # Store original buffer
        self._buffer = buffer.copy()

    def close(self) -> None:
        """Clean up Pygame resources."""
        pygame.quit()
