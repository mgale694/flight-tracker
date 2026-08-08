"""Main display controller"""
import os
import logging
from .hw import display_for
from .view import FlightView
from . import fonts


class Display:
    """Main display controller"""

    def __init__(self, config):
        self.config = config
        # Handle config structures
        display_config = config.get("ui", {}).get("display", config.get("display", {}))
        self._enabled = display_config.get("enabled", True)
        self._rotation = display_config.get("rotation", 180)
        display_type = display_config.get("type", "waveshare213in_v4")

        # Initialize fonts
        print("Initializing fonts...")
        try:
            fonts.init(config)
            print("PASS: Fonts initialized")
        except Exception as e:
            print(f"FAIL: Error initializing fonts: {e}")
            logging.error(f"Error initializing fonts: {e}")

        print("Display Configuration:")
        print(f"   - Enabled: {self._enabled}")
        print(f"   - Type: {display_type}")
        print(f"   - Rotation: {self._rotation}")

        # Initialize hardware display
        print("Getting display implementation...")
        self._implementation = display_for(config)
        print(f"PASS: Display implementation: {self._implementation.name}")
        print(f"   - Width: {self._implementation.width}")
        print(f"   - Height: {self._implementation.height}")

        self.view = FlightView(self._implementation, config)

        if self._enabled:
            self.init_display()
        else:
            print("WARNING: Display is disabled in config")

    def init_display(self):
        """Initialize the display hardware"""
        if self._enabled:
            print("Initializing display hardware...")
            logging.info("Initializing display")
            try:
                self._implementation.initialize()
                print("PASS: Display hardware initialized")
            except Exception as e:
                print(f"FAIL: Error during display initialize(): {e}")
                logging.error(f"Error during display initialize(): {e}")

            try:
                self._implementation.clear()
                print("PASS: Display hardware cleared")
            except Exception as e:
                print(f"FAIL: Error during display clear(): {e}")
                logging.error(f"Error during display clear(): {e}")
        else:
            print("WARNING: Display init skipped (disabled)")

    def render_boot(self, face, phrase):
        """Render boot screen"""
        if self._enabled:
            self.view.render_boot_screen(face, phrase)

    def render_pairing(self, setup_url, pairing_code):
        """Render the first-boot QR setup state."""

        if self._enabled:
            self.view.render_pairing_screen(setup_url, pairing_code)

    def render_flight(self, flight, stats):
        """Render flight information"""
        if self._enabled:
            self.view.render_flight_screen(flight, stats)

    def update_fields(self, fields):
        """Apply e-paper line choices received from the web settings page."""

        if fields:
            self.view.display_fields = list(fields)[:5]

    def clear(self):
        """Clear the display"""
        if self._enabled:
            self._implementation.clear()

    def render_blank(self):
        """Render a blank white screen"""
        if self._enabled:
            self.view.render_blank_screen()

    def sleep(self):
        """Put display to sleep"""
        if self._enabled:
            self._implementation.sleep()

    def is_enabled(self):
        """Check if display is enabled"""
        return self._enabled
