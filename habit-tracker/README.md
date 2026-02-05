# Raspberry Pi Zero Habit Tracker

A tamagotchi-style habit tracker for Raspberry Pi Zero with 128x128 LCD display.

## Development Setup (Laptop)

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python main.py
```

## Controls (Laptop)
- **W/A/S/D**: Joystick (Up/Left/Down/Right)
- **P**: Button A (Select/Confirm)
- **L**: Button B (Back/Cancel)
- **M**: Button C (Quick Action)

## Project Structure
```
habit-tracker/
├── main.py              # Entry point
├── display/
│   ├── renderer.py      # Screen rendering
│   ├── display_base.py  # Abstract display interface
│   ├── pygame_display.py # Pygame implementation
│   └── lcd_display.py   # Pi LCD implementation (future)
├── input/
│   ├── input_base.py    # Abstract input interface
│   ├── keyboard_input.py # Pygame keyboard implementation
│   └── gpio_input.py    # Pi GPIO implementation (future)
├── game/
│   ├── character.py     # Character state & mechanics
│   ├── habits.py        # Habit tracking logic
│   └── screens.py       # Screen navigation & UI
├── data/
│   └── db.py           # SQLite interface
└── assets/
    └── sprites/        # Pixel art (Aseprite exports)
```

## Running Tests
```bash
pytest tests/ -v
pytest tests/ --cov=. --cov-report=html
```
