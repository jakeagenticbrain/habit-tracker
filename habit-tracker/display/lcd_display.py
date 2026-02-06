"""LCD display driver for Waveshare 1.44" HAT with ST7735S controller."""

from PIL import Image
from .display_base import DisplayBase

# Graceful import for non-Pi environments
try:
    from ST7735 import ST7735
    HAS_LCD = True
except ImportError:
    HAS_LCD = False


class LCDDisplay(DisplayBase):
    """Display implementation for ST7735S LCD via SPI."""

    def __init__(self, width: int = 128, height: int = 128):
        """Initialize LCD display.

        Args:
            width: Display width in pixels (default 128)
            height: Display height in pixels (default 128)
        """
        super().__init__(width, height)

        if not HAS_LCD:
            raise ImportError(
                "ST7735 library not available. "
                "Install with: pip install st7735"
            )

        # GPIO pins for Waveshare 1.44" HAT (BCM numbering)
        # DC (Data/Command): BCM 25
        # RST (Reset): BCM 27
        # BL (Backlight): BCM 24
        # SPI: SCLK=BCM 11, MOSI=BCM 10, CS=BCM 8 (hardware SPI)
        self._lcd = ST7735(
            port=0,           # SPI port 0
            cs=0,             # CS pin (SPI0 CE0)
            dc=25,            # Data/Command pin
            rst=27,           # Reset pin
            backlight=24,     # Backlight pin
            width=width,
            height=height,
            rotation=90,      # 90° rotation for correct orientation
            spi_speed_hz=4000000,  # 4 MHz SPI speed
            offset_left=2,    # Horizontal offset for Waveshare HAT
            offset_top=3,     # Vertical offset for Waveshare HAT
            invert=True,      # Color inversion for proper colors
            bgr=True          # BGR color order for Waveshare HAT
        )

        # Initialize display
        self._lcd.begin()

        # Create buffer
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
        # ST7735 library expects RGB mode PIL Image
        # The display() method handles RGB565 conversion internally
        self._lcd.display(buffer)

        # Store buffer
        self._buffer = buffer.copy()

    def close(self) -> None:
        """Clean up LCD resources."""
        # ST7735 library handles cleanup automatically
        pass
