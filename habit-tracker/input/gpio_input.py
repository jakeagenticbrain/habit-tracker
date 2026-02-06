"""GPIO input implementation for Raspberry Pi with Waveshare 1.44" LCD HAT."""

try:
    import RPi.GPIO as GPIO
except (ImportError, RuntimeError):
    # Fallback for non-Pi environments (testing, development)
    GPIO = None

from .input_base import InputBase, InputEvent, InputType


class GPIOInput(InputBase):
    """Maps GPIO pins to input events for Raspberry Pi deployment.

    Hardware: Waveshare 1.44" LCD HAT
    - 4-direction joystick + press
    - 3 physical buttons (KEY1/KEY2/KEY3)
    - All inputs active-low with pull-up resistors

    GPIO Pin Mapping (BCM):
    - Joystick UP: GPIO 6
    - Joystick DOWN: GPIO 19
    - Joystick LEFT: GPIO 5
    - Joystick RIGHT: GPIO 26
    - Joystick PRESS: GPIO 13
    - KEY1 (Button A): GPIO 21
    - KEY2 (Button B): GPIO 20
    - KEY3 (Button C): GPIO 16
    """

    def __init__(self):
        """Initialize GPIO input handler."""
        if GPIO is None:
            raise RuntimeError("RPi.GPIO not available - cannot initialize GPIOInput")

        # Set GPIO mode to BCM (Broadcom pin numbering)
        GPIO.setmode(GPIO.BCM)

        # Pin to InputType mapping (rotated 90° to match display rotation)
        self.pin_map = {
            6: InputType.LEFT,       # Physical UP → LEFT (after rotation)
            19: InputType.RIGHT,     # Physical DOWN → RIGHT (after rotation)
            5: InputType.DOWN,       # Physical LEFT → DOWN (after rotation)
            26: InputType.UP,        # Physical RIGHT → UP (after rotation)
            13: InputType.BUTTON_A,  # Joystick press acts as Button A
            21: InputType.BUTTON_A,  # KEY1
            20: InputType.BUTTON_B,  # KEY2
            16: InputType.BUTTON_C,  # KEY3
        }

        # Configure all pins as inputs with pull-up resistors (active-low)
        for pin in self.pin_map.keys():
            GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

        # Track previous state for edge detection - read initial state
        self.prev_state = {}
        for pin in self.pin_map.keys():
            self.prev_state[pin] = GPIO.input(pin)

    def poll(self) -> InputEvent | None:
        """Poll for GPIO input events.

        Checks all pins for state changes (edge detection).
        Active-low logic: LOW = pressed, HIGH = released.

        Returns:
            InputEvent if a pin state changed, None otherwise.
        """
        if GPIO is None:
            return None

        # Check all pins for state changes
        for pin, input_type in self.pin_map.items():
            current_state = GPIO.input(pin)

            # Detect state change
            if current_state != self.prev_state[pin]:
                self.prev_state[pin] = current_state

                # Active-low: LOW = pressed (True), HIGH = released (False)
                pressed = (current_state == GPIO.LOW)

                return InputEvent(
                    input_type=input_type,
                    pressed=pressed
                )

        return None

    def cleanup(self):
        """Clean up GPIO resources."""
        if GPIO is not None:
            GPIO.cleanup()
