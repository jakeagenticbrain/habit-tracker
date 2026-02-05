"""UI component drawing helpers using PIL ImageDraw."""

from PIL import Image, ImageDraw
from assets.sprite_loader import render_text
from config import Config


def draw_panel(buffer: Image.Image, x: int, y: int, width: int, height: int,
               title: str = None, fill_color: tuple = None) -> None:
    """Draw a bordered panel with optional title bar.

    Args:
        buffer: PIL Image to draw on
        x, y: Top-left corner position
        width, height: Panel dimensions
        title: Optional title text for header bar
        fill_color: Optional background fill color (default: white)
    """
    draw = ImageDraw.Draw(buffer)

    # Background fill
    if fill_color is None:
        fill_color = (255, 255, 255)
    draw.rectangle((x, y, x + width, y + height), fill=fill_color, outline=(0, 0, 0), width=1)

    # Title bar if provided
    if title:
        # Draw header background
        draw.rectangle((x, y, x + width, y + 12), fill=(100, 100, 100))
        # Title text
        title_img = render_text(title, Config.FONT_BOLD, Config.FONT_SIZE_SMALL, color=(255, 255, 255))
        buffer.paste(title_img, (x + 4, y + 2), title_img)
        # Divider line below header
        draw.line((x, y + 12, x + width, y + 12), fill=(0, 0, 0), width=1)


def draw_list_item(buffer: Image.Image, x: int, y: int, width: int, height: int,
                   text: str, selected: bool = False, icon: Image.Image = None) -> None:
    """Draw a selectable list item with optional icon.

    Args:
        buffer: PIL Image to draw on
        x, y: Top-left corner position
        width, height: Item dimensions
        text: Item text
        selected: Whether item is selected (shows highlight)
        icon: Optional icon image to display before text
    """
    draw = ImageDraw.Draw(buffer)

    # Selection highlight
    if selected:
        draw.rectangle((x, y, x + width, y + height), fill=(200, 200, 200))

    # Icon if provided
    text_x = x + 4
    if icon:
        buffer.paste(icon, (x + 2, y + 2), icon)
        text_x = x + 20

    # Text
    text_img = render_text(text, Config.FONT_REGULAR, Config.FONT_SIZE_NORMAL, color=(0, 0, 0))
    buffer.paste(text_img, (text_x, y + 4), text_img)


def draw_input_field(buffer: Image.Image, x: int, y: int, width: int,
                     value: str, show_cursor: bool = False) -> None:
    """Draw a text input field with optional cursor.

    Args:
        buffer: PIL Image to draw on
        x, y: Top-left corner position
        width: Field width
        value: Current text value
        show_cursor: Whether to show blinking cursor at end
    """
    draw = ImageDraw.Draw(buffer)

    # Field box
    draw.rectangle((x, y, x + width, y + 12), fill=(255, 255, 255), outline=(0, 0, 0), width=1)

    # Text value
    if value:
        text_img = render_text(value, Config.FONT_REGULAR, Config.FONT_SIZE_NORMAL, color=(0, 0, 0))
        buffer.paste(text_img, (x + 2, y + 2), text_img)

    # Cursor
    if show_cursor:
        cursor_x = x + 2 + (len(value) * 6)  # Approximate 6px per char
        draw.line((cursor_x, y + 2, cursor_x, y + 10), fill=(0, 0, 0), width=1)


def draw_button_hint(buffer: Image.Image, x: int, y: int, text: str) -> None:
    """Draw a button hint label at bottom of screen.

    Args:
        buffer: PIL Image to draw on
        x, y: Position for hint text
        text: Hint text (e.g., "P=Select L=Back")
    """
    hint_img = render_text(text, Config.FONT_REGULAR, Config.FONT_SIZE_SMALL, color=(128, 128, 128))
    buffer.paste(hint_img, (x, y), hint_img)


def draw_divider(buffer: Image.Image, y: int, color: tuple = (128, 128, 128)) -> None:
    """Draw a horizontal divider line across the screen.

    Args:
        buffer: PIL Image to draw on
        y: Y position for line
        color: Line color (default: gray)
    """
    draw = ImageDraw.Draw(buffer)
    draw.line((0, y, 128, y), fill=color, width=1)
