"""Display abstraction layer for rendering to different outputs."""

from .display_base import DisplayBase
from .pygame_display import PygameDisplay

__all__ = ['DisplayBase', 'PygameDisplay']
