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
        print("🔧 Initializing fonts...")
        try:
            fonts.init(config)
            print("✓ Fonts initialized")
        except Exception as e:
            print(f"❌ Error initializing fonts: {e}")
            logging.error(f"Error initializing fonts: {e}")

        print(f"🖥️  Display Configuration:")
        print(f"   - Enabled: {self._enabled}")
        print(f"   - Type: {display_type}")
        print(f"   - Rotation: {self._rotation}")

        # Initialize hardware display
        print("🔧 Getting display implementation...")
        self._implementation = display_for(config)
        print(f"✓ Display implementation: {self._implementation.name}")
        print(f"   - Width: {self._implementation.width}")
        print(f"   - Height: {self._implementation.height}")

        self.view = FlightView(self._implementation, config)

        if self._enabled:
            self.init_display()
        else:
            print("⚠️  Display is disabled in config")

    def init_display(self):
        """Initialize the display hardware"""
        if self._enabled:
            print("🔧 Initializing display hardware...")
            logging.info("Initializing display")
            try:
                self._implementation.initialize()
                print("✓ Display hardware initialized")
            except Exception as e:
                print(f"❌ Error during display initialize(): {e}")
                logging.error(f"Error during display initialize(): {e}")

            try:
                self._implementation.clear()
                print("✓ Display hardware cleared")
            except Exception as e:
                print(f"❌ Error during display clear(): {e}")
                logging.error(f"Error during display clear(): {e}")
        else:
            print("⚠️  Display init skipped (disabled)")

    def render_boot(self, face, phrase):
        """Render boot screen"""
        if self._enabled:
            self.view.render_boot_screen(face, phrase)

    def render_flight(self, flight, stats):
        """Render flight information"""
        if self._enabled:
            self.view.render_flight_screen(flight, stats)

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
