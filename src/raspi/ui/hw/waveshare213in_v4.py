"""Waveshare 2.13" V4 E-ink Display Driver"""
import logging
import sys
sys.path.append('../..')
import ui.fonts as fonts
from .base import DisplayImpl


class Waveshare213V4(DisplayImpl):
    """Driver for Waveshare 2.13" V4 e-ink display"""
    
    def __init__(self, config):
        super(Waveshare213V4, self).__init__(config, "waveshare213in_v4")
        self._display = None

    def layout(self):
        """Setup display layout for 2.13" V4"""
        fonts.setup(10, 9, 10, 35, 25, 9)
        self._layout["width"] = 250
        self._layout["height"] = 122
        return self._layout

    def initialize(self):
        """Initialize the Waveshare 2.13" V4 display"""
        logging.info("Initializing Waveshare 2.13in V4 display")
        try:
            # Try to import the EPD module - this requires Raspberry Pi hardware
            from .libs.waveshare.epd2in13_V4 import EPD

            self._display = EPD()
            self._display.init()
            self._display.Clear()
            logging.info("✓ Waveshare 2.13in V4 display initialized successfully")
        except ImportError as e:
            logging.error(
                f"Cannot import Waveshare EPD module (missing Pi libraries): {e}"
            )
            logging.warning("This is normal when running on non-Pi systems")
            logging.warning("Install with: sudo apt-get install python3-rpi.gpio python3-spidev")
            self._display = None
        except Exception as e:
            logging.error(f"Failed to initialize Waveshare hardware: {e}")
            if "cannot open resource" in str(e).lower():
                logging.warning(
                    "Hardware resources not available (SPI/GPIO not accessible)"
                )
                logging.warning("Run with sudo or enable SPI: sudo raspi-config")
            elif "edge detection" in str(e).lower():
                logging.warning("GPIO edge detection failed - this may be a permission or library issue")
                logging.warning("Try: sudo apt-get install python3-lgpio python3-rpi-lgpio")
                logging.warning("Or run with: sudo python3 agent.py")
            elif "lgpio" in str(e).lower() or "gpiozero" in str(e).lower():
                logging.warning("GPIO library issue detected")
                logging.warning("Install: pip3 install lgpio rpi-lgpio --break-system-packages")
            import traceback
            logging.debug(traceback.format_exc())
            self._display = None

    def render(self, canvas):
        """Render image to the display"""
        if self._display is None:
            logging.warning("Display not initialized, skipping render")
            return

        try:
            buf = self._display.getbuffer(canvas)

            # Try different display methods in order of preference
            if hasattr(self._display, "displayPartial"):
                # Best option: true partial refresh with minimal flashing
                self._display.displayPartial(buf)
            elif hasattr(self._display, "display_fast"):
                # Alternative: fast display with reduced flashing
                self._display.display_fast(buf)
            else:
                # Fallback: standard display (may cause flashing)
                self._display.display(buf)
        except Exception as e:
            logging.error(f"Error rendering to display: {e}")

    def clear(self):
        """Clear the display"""
        if self._display is None:
            return
        try:
            self._display.Clear()
        except Exception as e:
            logging.error(f"Error clearing display: {e}")

    def sleep(self):
        """Put the display to sleep mode"""
        if self._display is None:
            return
        try:
            if hasattr(self._display, "sleep"):
                self._display.sleep()
            elif hasattr(self._display, "Sleep"):
                self._display.Sleep()
        except Exception as e:
            logging.error(f"Error putting display to sleep: {e}")
