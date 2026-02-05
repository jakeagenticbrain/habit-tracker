"""Sprite sheet loading and extraction utilities."""

from PIL import Image, ImageFont, ImageDraw
from typing import Dict, Tuple, NamedTuple, Optional


class ProgressBarInfo(NamedTuple):
    """Information about which progress bar sprite to use."""
    sheet_name: str  # 'icons' or 'progress-bars'
    row: int         # Row index in that sheet


class SpriteSheet:
    """Loads and extracts sprites from a sprite sheet.

    Supports both individual tile extraction and full-row extraction
    (useful for progress bars). Caches extracted sprites for performance.
    """

    def __init__(self, image_path: str, tile_width: int = 16, tile_height: int = 16):
        """Initialize sprite sheet loader.

        Args:
            image_path: Path to the sprite sheet PNG
            tile_width: Width of each tile in pixels (default 16)
            tile_height: Height of each tile in pixels (default 16)
        """
        self.image_path = image_path
        self.tile_width = tile_width
        self.tile_height = tile_height
        self.sheet = Image.open(image_path).convert('RGBA')
        self.width = self.sheet.width
        self.height = self.sheet.height

        # Cache for extracted sprites
        self._tile_cache: Dict[Tuple[int, int], Image.Image] = {}
        self._row_cache: Dict[int, Image.Image] = {}

    def get_sprite(self, col: int, row: int) -> Image.Image:
        """Extract a single tile sprite at (col, row).

        Args:
            col: Column index (0-based)
            row: Row index (0-based)

        Returns:
            PIL Image of the extracted tile
        """
        # Check cache first
        cache_key = (col, row)
        if cache_key in self._tile_cache:
            return self._tile_cache[cache_key]

        # Calculate pixel coordinates
        x = col * self.tile_width
        y = row * self.tile_height

        # Extract tile
        tile = self.sheet.crop((
            x,
            y,
            x + self.tile_width,
            y + self.tile_height
        ))

        # Cache and return
        self._tile_cache[cache_key] = tile
        return tile

    def get_row(self, row: int) -> Image.Image:
        """Extract a full row from the sprite sheet.

        Useful for progress bars or other full-width elements.

        Args:
            row: Row index (0-based)

        Returns:
            PIL Image of the full row (width x tile_height)
        """
        # Check cache first
        if row in self._row_cache:
            return self._row_cache[row]

        # Calculate pixel coordinates
        y = row * self.tile_height

        # Extract full row
        row_sprite = self.sheet.crop((
            0,
            y,
            self.width,
            y + self.tile_height
        ))

        # Cache and return
        self._row_cache[row] = row_sprite
        return row_sprite

    def get_sprites_range(self, start_col: int, start_row: int,
                          end_col: int, end_row: int) -> list[Image.Image]:
        """Extract a range of sprites (useful for animations).

        Args:
            start_col: Starting column (0-based)
            start_row: Starting row (0-based)
            end_col: Ending column (0-based, inclusive)
            end_row: Ending row (0-based, inclusive)

        Returns:
            List of PIL Images in left-to-right, top-to-bottom order
        """
        sprites = []
        for r in range(start_row, end_row + 1):
            for c in range(start_col, end_col + 1):
                sprites.append(self.get_sprite(c, r))
        return sprites


def get_progress_bar_for_percentage(percentage: float) -> ProgressBarInfo:
    """Map a percentage (0-100) to the appropriate progress bar sprite.

    Progress bars range from 0-80 in increments of 10, where:
    - 0% → progress-bar-0 (icons.png, row 3)
    - 100% → progress-bar-80 (progress-bars.png, row 3)

    Args:
        percentage: Value from 0-100

    Returns:
        ProgressBarInfo with sheet name and row index
    """
    # Clamp to 0-100 range
    percentage = max(0, min(100, percentage))

    # Round percentage to nearest 10
    rounded_percentage = round(percentage / 10) * 10

    # Map to bar value (0, 10, 20, ..., 80)
    # 100% and 90% both map to bar 80 (full)
    bar_value = min(rounded_percentage, 80)

    # Map to sprite sheet and row
    if bar_value <= 40:
        # 0, 10, 20, 30, 40 are in icons.png rows 3-7
        return ProgressBarInfo('icons', 3 + (bar_value // 10))
    else:
        # 50, 60, 70, 80 are in progress-bars.png rows 0-3
        return ProgressBarInfo('progress-bars', (bar_value - 50) // 10)


# Font cache to avoid reloading fonts repeatedly
_font_cache: Dict[Tuple[str, int], ImageFont.FreeTypeFont] = {}


def load_font(font_path: str, size: int) -> ImageFont.FreeTypeFont:
    """Load a TrueType font at the specified size.

    Fonts are cached to avoid reloading on every call.

    Args:
        font_path: Path to the TTF font file
        size: Font size in pixels

    Returns:
        PIL ImageFont object
    """
    cache_key = (font_path, size)

    if cache_key not in _font_cache:
        _font_cache[cache_key] = ImageFont.truetype(font_path, size)

    return _font_cache[cache_key]


def render_text(
    text: str,
    font_path: str,
    font_size: int,
    color: Tuple[int, int, int] = (255, 255, 255),
    background: Optional[Tuple[int, int, int]] = None
) -> Image.Image:
    """Render text to a PIL Image with the specified font.

    Args:
        text: Text string to render
        font_path: Path to TTF font file
        font_size: Font size in pixels
        color: Text color as RGB tuple (default white)
        background: Background color as RGB tuple (None for transparent)

    Returns:
        PIL Image containing the rendered text
    """
    font = load_font(font_path, font_size)

    # Create a temporary image to measure text size
    temp_img = Image.new('RGBA', (1, 1))
    draw = ImageDraw.Draw(temp_img)
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]

    # Create final image with proper size
    if background is not None:
        img = Image.new('RGB', (text_width, text_height), color=background)
    else:
        img = Image.new('RGBA', (text_width, text_height), color=(0, 0, 0, 0))

    # Draw text
    draw = ImageDraw.Draw(img)
    draw.text((-bbox[0], -bbox[1]), text, font=font, fill=color)

    return img
