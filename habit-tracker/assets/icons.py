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

# ==============================================================================
# HIGHLIGHTED-CHECKBOXES.PNG SPRITE SHEET (separate from icons.png)
# ==============================================================================
# Note: These coordinates are for the highlighted-checkboxes.png sprite sheet,
# not icons.png. Use with SpriteSheet(Config.HIGHLIGHTED_CHECKBOXES, 16, 16)

# Highlighted numbered boxes (row 3, 1-based = row 2, 0-indexed)
NUMBERED_BOX_1_HIGHLIGHTED = (0, 2)
NUMBERED_BOX_2_HIGHLIGHTED = (1, 2)
NUMBERED_BOX_3_HIGHLIGHTED = (2, 2)
NUMBERED_BOX_4_HIGHLIGHTED = (3, 2)
NUMBERED_BOX_5_HIGHLIGHTED = (4, 2)
NUMBERED_BOX_6_HIGHLIGHTED = (5, 2)

# Non-highlighted numbered boxes (row 4, 1-based = row 3, 0-indexed)
NUMBERED_BOX_1 = (0, 3)
NUMBERED_BOX_2 = (1, 3)
NUMBERED_BOX_3 = (2, 3)
NUMBERED_BOX_4 = (3, 3)
NUMBERED_BOX_5 = (4, 3)
NUMBERED_BOX_6 = (5, 3)

# New shorter pointer for view habits screen (B1, 1-based = column 1, row 0, 0-indexed)
# This is in highlighted-checkboxes.png, not icons.png
POINTER_SHORT = (1, 0)

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
