"""Update screen for checking and installing git updates."""

import subprocess
import sys
from PIL import Image, ImageDraw
from typing import Optional
from input.input_base import InputEvent, InputType
from game.screens import ScreenBase
from assets.sprite_loader import load_font
from config import Config


def debug_log(msg):
    """Print debug message to stdout (visible in systemd journal)."""
    print(f"[UPDATE] {msg}", file=sys.stderr, flush=True)


class UpdateScreen(ScreenBase):
    """Update screen that checks for git updates and prompts to restart.

    Flow:
    1. Shows "Checking for update..." message
    2. Performs git pull
    3. Shows result message with OK/Cancel buttons
    4. OK = restart systemd service, Cancel = back to settings
    """

    # Layout constants
    TEXT_X = 45
    TEXT_MAX_X = 119  # Max x position before wrapping
    TEXT_AREA_TOP = 30  # Top of text area
    TEXT_AREA_HEIGHT = 70  # Available height (30 to 100, before buttons at 107)
    LINE_HEIGHT = 10  # Pixels per line
    OK_BUTTON_X = 23
    CANCEL_BUTTON_X = 55
    BUTTON_Y = 107

    def __init__(self):
        """Initialize update screen."""
        # Load background and button sprites
        self.bg_sprite = Image.open(Config.UPDATE_POPUP_BG).convert("RGBA")
        self.ok_highlighted = Image.open(Config.POPUP_OK_HIGHLIGHTED).convert("RGBA")
        self.cancel_highlighted = Image.open(Config.POPUP_CANCEL_HIGHLIGHTED).convert("RGBA")

        # Load font
        self.font = load_font(Config.FONT_REGULAR, 8)

        # Initialize state
        self._reset_state()

    def _reset_state(self):
        """Reset screen state for next check."""
        self.state = "checking"  # "checking" or "show_result"
        self.selected_button = 0  # 0 = OK, 1 = Cancel
        self.message = "Checking for\nupdate..."
        self.update_checked = False
        self.update_available = False

    def _check_for_updates(self) -> tuple[bool, str]:
        """Check for updates via git pull.

        Returns:
            (success, message) tuple
        """
        try:
            debug_log(f"Starting update check in {Config.BASE_DIR}")

            # First, fetch to see if there are updates
            debug_log("Running: git fetch origin main")
            result = subprocess.run(
                ["git", "fetch", "origin", "main"],
                cwd=Config.BASE_DIR,
                capture_output=True,
                text=True,
                timeout=10
            )

            debug_log(f"Fetch result: rc={result.returncode}")
            debug_log(f"Fetch stdout: {result.stdout}")
            debug_log(f"Fetch stderr: {result.stderr}")

            if result.returncode != 0:
                return False, f"Fetch failed:\n{result.stderr[:40]}"

            # Get local commit
            result_local = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                cwd=Config.BASE_DIR,
                capture_output=True,
                text=True,
                timeout=5
            )
            local_hash = result_local.stdout.strip()[:8] if result_local.returncode == 0 else "unknown"
            debug_log(f"Local commit: {local_hash}")

            # Get remote commit
            result_remote = subprocess.run(
                ["git", "rev-parse", "origin/main"],
                cwd=Config.BASE_DIR,
                capture_output=True,
                text=True,
                timeout=5
            )
            remote_hash = result_remote.stdout.strip()[:8] if result_remote.returncode == 0 else "unknown"
            debug_log(f"Remote commit: {remote_hash}")

            # Check if we're behind
            debug_log("Running: git rev-list --count HEAD..origin/main")
            result = subprocess.run(
                ["git", "rev-list", "--count", "HEAD..origin/main"],
                cwd=Config.BASE_DIR,
                capture_output=True,
                text=True,
                timeout=5
            )

            debug_log(f"Rev-list result: rc={result.returncode}")
            debug_log(f"Rev-list stdout: {result.stdout}")

            if result.returncode != 0:
                return False, "Could not check\nfor updates"

            commits_behind = int(result.stdout.strip())
            debug_log(f"Commits behind: {commits_behind}")

            if commits_behind == 0:
                return False, "Already up\nto date!"

            # There are updates, perform the pull
            result = subprocess.run(
                ["git", "pull", "origin", "main"],
                cwd=Config.BASE_DIR,
                capture_output=True,
                text=True,
                timeout=15
            )

            if result.returncode != 0:
                return False, f"Pull failed:\n{result.stderr[:40]}"

            # Check if requirements-pi.txt changed
            deps_updated = self._install_dependencies_if_needed()

            # Build success message (simplified)
            msg = "Update found"
            if deps_updated:
                msg += "\nDeps installed"
            msg += "\nRestart?"

            return True, msg

        except subprocess.TimeoutExpired:
            return False, "Update timed\nout. Check WiFi."
        except FileNotFoundError:
            return False, "Git not found"
        except Exception as e:
            return False, f"Error:\n{str(e)[:40]}"

    def _install_dependencies_if_needed(self) -> bool:
        """Check if requirements-pi.txt changed and install if needed.

        Returns:
            True if dependencies were installed, False otherwise
        """
        try:
            # Check what files changed in the last pull
            result = subprocess.run(
                ["git", "diff", "--name-only", "HEAD@{1}", "HEAD"],
                cwd=Config.BASE_DIR,
                capture_output=True,
                text=True,
                timeout=5
            )

            if result.returncode != 0:
                return False

            changed_files = result.stdout.strip().split('\n')

            # Check if requirements-pi.txt was modified
            if 'requirements-pi.txt' in changed_files:
                # Update message to show we're installing
                self.message = "Installing\ndependencies..."

                # Install dependencies
                result = subprocess.run(
                    ["pip", "install", "-r", "requirements-pi.txt"],
                    cwd=Config.BASE_DIR,
                    capture_output=True,
                    text=True,
                    timeout=60
                )

                return result.returncode == 0

            return False

        except Exception:
            return False

    def handle_input(self, event: InputEvent) -> Optional[str]:
        """Handle input for button selection.

        Args:
            event: Input event

        Returns:
            Screen name to navigate to, or None
        """
        if not event.pressed:
            return None

        # Only allow input when showing result
        if self.state != "show_result":
            return None

        if event.input_type == InputType.LEFT:
            self.selected_button = 0  # OK
        elif event.input_type == InputType.RIGHT:
            self.selected_button = 1  # Cancel
        elif event.input_type == InputType.BUTTON_A:
            # Confirm selection
            if self.selected_button == 0:
                # OK - restart service if update was successful
                if self.update_available:
                    self._restart_service()
                # Reset state for next time before navigating away
                self._reset_state()
                return "settings"
            else:
                # Cancel - go back to settings
                # Reset state for next time before navigating away
                self._reset_state()
                return "settings"

        return None

    def _restart_service(self):
        """Restart the habit-tracker systemd service."""
        try:
            subprocess.run(
                ["sudo", "systemctl", "restart", "habit-tracker"],
                timeout=5
            )
        except Exception as e:
            # If restart fails, we'll just exit normally
            # The service should auto-restart anyway
            pass

    def _wrap_text(self, text: str) -> list[str]:
        """Wrap text to fit within TEXT_X to TEXT_MAX_X.

        Args:
            text: Text to wrap (can contain newlines)

        Returns:
            List of lines that fit within width
        """
        max_width = self.TEXT_MAX_X - self.TEXT_X
        lines = []

        # Process each line (respect existing newlines)
        for paragraph in text.split('\n'):
            words = paragraph.split()
            if not words:
                lines.append('')
                continue

            current_line = ""
            for word in words:
                test_line = f"{current_line} {word}".strip()
                # Measure actual pixel width
                bbox = self.font.getbbox(test_line)
                text_width = bbox[2] - bbox[0]

                if text_width <= max_width:
                    current_line = test_line
                else:
                    # Line would be too long, start new line
                    if current_line:
                        lines.append(current_line)
                    current_line = word

            if current_line:
                lines.append(current_line)

        return lines

    def update(self, delta_time: float) -> None:
        """Update screen state - trigger git check on first frame.

        Args:
            delta_time: Time since last frame in seconds
        """
        # On first update, check for updates
        if not self.update_checked:
            self.update_checked = True
            self.update_available, self.message = self._check_for_updates()
            self.state = "show_result"

    def render(self, buffer: Image.Image) -> None:
        """Render update screen to buffer.

        Args:
            buffer: PIL Image to draw to
        """
        # Draw background
        buffer.paste(self.bg_sprite, (0, 0), self.bg_sprite)

        # Draw message text with wrapping and auto-centering
        draw = ImageDraw.Draw(buffer)

        # Wrap text to fit within TEXT_X to TEXT_MAX_X
        lines = self._wrap_text(self.message)

        # Calculate vertical centering (adjusted 5px higher)
        total_text_height = len(lines) * self.LINE_HEIGHT
        text_start_y = self.TEXT_AREA_TOP + (self.TEXT_AREA_HEIGHT - total_text_height) // 2 - 5

        # Draw centered text
        y_offset = text_start_y
        for line in lines:
            draw.text((self.TEXT_X, y_offset), line, fill=Config.COLOR_TEXT_DARK, font=self.font)
            y_offset += self.LINE_HEIGHT

        # Draw buttons only when showing result
        # Button sprites are 128x128 full-screen overlays - paste at (0, 0)
        if self.state == "show_result":
            if self.selected_button == 0:
                # OK button highlighted
                buffer.paste(self.ok_highlighted, (0, 0), self.ok_highlighted)
            else:
                # Cancel button highlighted
                buffer.paste(self.cancel_highlighted, (0, 0), self.cancel_highlighted)
