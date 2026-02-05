"""Icon coordinate mappings for the icons.png sprite sheet.

Each icon is defined as (column, row) in 0-indexed coordinates.
The sprite sheet is 8x8 grid with 16x16 pixel tiles.
"""

# Large icons (row A)
POINTER_LARGE = (4, 0)
ARROW_LARGE = (5, 0)
HEART_LARGE = (6, 0)
STAR_LARGE = (7, 0)

# Small and checkbox icons (row B)
CHECKED_BOX_SMALL = (0, 1)
X_BOX_SMALL = (1, 1)
CHECKED_BOX_LARGE = (2, 1)
X_BOX_LARGE = (3, 1)
POINTER_SMALL = (4, 1)
ARROW_SMALL = (5, 1)
HEART_SMALL = (6, 1)
STAR_SMALL = (7, 1)

# Utility icons (row C)
UNCHECKED_BOX_SMALL = (0, 2)
CLOCK_ICON = (1, 2)
SETTINGS_ICON = (2, 2)
CHOCOLATE_BAR_ICON = (3, 2)
CANDY_ICON = (4, 2)
TEA_ICON = (5, 2)
COFFEE_ICON = (6, 2)
HOME_ICON = (7, 2)

# Progress bar rows (full-width 128x16)
# Use SpriteSheet.get_row() for these
# Rows from icons.png
PROGRESS_BAR_0 = 3   # 0% filled
PROGRESS_BAR_10 = 4  # 10% filled
PROGRESS_BAR_20 = 5  # 20% filled
PROGRESS_BAR_30 = 6  # 30% filled
PROGRESS_BAR_40 = 7  # 40% filled

# Rows from progress-bars.png
PROGRESS_BAR_50 = 0  # 50% filled
PROGRESS_BAR_60 = 1  # 60% filled
PROGRESS_BAR_70 = 2  # 70% filled
PROGRESS_BAR_80 = 3  # 80% filled (100% = full)
