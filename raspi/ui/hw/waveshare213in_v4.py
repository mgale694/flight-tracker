import logging

import raspi.ui.fonts as fonts
from raspi.ui.hw.base import DisplayImpl


class Waveshare213V4(DisplayImpl):
    def __init__(self, config):
        super(Waveshare213V4, self).__init__(config, "waveshare213in_v4")
        self._display = None

    def layout(self):
        if self.config["color"] == "black":
            fonts.setup(10, 9, 10, 35, 25, 9)
            self._layout["width"] = 250
            self._layout["height"] = 122
            self._layout["face"] = (0, 40)
            self._layout["name"] = (5, 20)
            self._layout["channel"] = (0, 0)
            self._layout["aps"] = (28, 0)
            self._layout["uptime"] = (185, 0)
            self._layout["line1"] = [0, 14, 250, 14]
            self._layout["line2"] = [0, 108, 250, 108]
            self._layout["friend_face"] = (0, 92)
            self._layout["friend_name"] = (40, 94)
            self._layout["shakes"] = (0, 109)
            self._layout["mode"] = (225, 109)
            self._layout["status"] = {
                "pos": (125, 20),
                "font": fonts.status_font(fonts.Medium),
                "max": 20,
            }
        else:
            fonts.setup(10, 8, 10, 25, 25, 9)
            self._layout["width"] = 212
            self._layout["height"] = 104
            self._layout["face"] = (0, 26)
            self._layout["name"] = (5, 15)
            self._layout["channel"] = (0, 0)
            self._layout["aps"] = (28, 0)
            self._layout["status"] = (91, 15)
            self._layout["uptime"] = (147, 0)
            self._layout["line1"] = [0, 12, 212, 12]
            self._layout["line2"] = [0, 92, 212, 92]
            self._layout["friend_face"] = (0, 76)
            self._layout["friend_name"] = (40, 78)
            self._layout["shakes"] = (0, 93)
            self._layout["mode"] = (187, 93)
            self._layout["status"] = {
                "pos": (125, 20),
                "font": fonts.status_font(fonts.Medium),
                "max": 14,
            }
        return self._layout

    def initialize(self):
        logging.info("initializing waveshare 2.13in v4 display")
        try:
            # Try to import the EPD module - this may fail on non-Pi systems
            from raspi.ui.hw.libs.waveshare.epd2in13_V4 import EPD

            self._display = EPD()
            self._display.init()
            self._display.Clear()
            logging.info("✓ Waveshare 2.13in v4 display initialized successfully")
        except ImportError as e:
            logging.error(
                f"Cannot import Waveshare EPD module (missing Pi libraries): {e}"
            )
            logging.warning("This is normal when running on non-Pi systems")
            self._display = None
        except Exception as e:
            logging.error(f"Failed to initialize Waveshare hardware: {e}")
            if "cannot open resource" in str(e):
                logging.warning(
                    "Hardware resources not available (SPI/GPIO not accessible)"
                )
            self._display = None

    def render(self, canvas):
        if self._display is None:
            return

        buf = self._display.getbuffer(canvas)

        # Try different display methods in order of gentleness
        if hasattr(self._display, "displayPartial"):
            # Best option: true partial refresh with minimal flashing
            self._display.displayPartial(buf)
        elif hasattr(self._display, "display_fast"):
            # Alternative: fast display with reduced flashing
            self._display.display_fast(buf)
        else:
            # Fallback: standard display (may cause flashing)
            self._display.display(buf)

    def clear(self):
        if self._display is None:
            return
        self._display.Clear()

    def sleep(self):
        """Put the display to sleep/standby mode"""
        if self._display is None:
            return
        if hasattr(self._display, "sleep"):
            self._display.sleep()
        elif hasattr(self._display, "Sleep"):
            self._display.Sleep()
