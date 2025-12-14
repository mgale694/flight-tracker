"""View rendering for flight information"""
from PIL import Image, ImageDraw
import logging
from . import fonts
import sys
sys.path.append('..')
from utils import safe_getattr, truncate_string


class FlightView:
    """Handles rendering flight information to the display"""

    def __init__(self, display):
        self.display = display
        self.width = display.width
        self.height = display.height

    def render_boot_screen(self, face, phrase):
        """Render boot screen with face and phrase"""
        image = Image.new("1", (self.width, self.height), 255)
        draw = ImageDraw.Draw(image)

        # Horizontal line
        draw.line((-5, 15, self.width, 15), fill=0, width=1)

        # Truncate phrase if too long
        display_phrase = truncate_string(phrase, 32)

        draw.text((5, 20), display_phrase, font=fonts.Medium, fill=0)
        draw.text((5, 52), face, font=fonts.Huge, fill=0)

        # Bottom line and timestamp
        draw.line((-5, self.height - 15, self.width, self.height - 15), fill=0, width=1)

        import time
        timestamp = time.strftime("%H:%M:%S")
        draw.text(
            (155, self.height - 12), f"TIME: {timestamp}", font=fonts.Small, fill=0
        )

        # Rotate for hardware displays
        rotated_image = image.rotate(180)
        self.display.render(rotated_image)

    def render_flight_screen(self, flight, stats):
        """Render flight information screen matching original format"""
        image = Image.new("1", (self.width, self.height), 255)
        draw = ImageDraw.Draw(image)

        # Top row with flight info
        callsign = safe_getattr(flight, 'callsign', 'N/A')
        draw.text((5, 2), f"ATC: {callsign}", font=fonts.Small, fill=0)
        draw.text((80, 2), f"COUNT: {stats.get('flights_count', 0)}", font=fonts.Small, fill=0)
        draw.text((155, 2), f"TIMER: {stats.get('elapsed_str', '0m')}", font=fonts.Small, fill=0)

        # Horizontal line under top row
        draw.line((-5, 15, self.width, 15), fill=0, width=1)

        # Flight details
        origin = safe_getattr(flight, 'origin', 'N/A')
        from_str = truncate_string(f"FROM: {origin}", 32)

        draw.text((5, 20), from_str, font=fonts.Medium, fill=0)
        draw.text((5, 36), f"AIRLINE: {safe_getattr(flight, 'airline', 'N/A')}", font=fonts.Medium, fill=0)
        draw.text((5, 52), f"MODEL: {safe_getattr(flight, 'aircraft', 'Unknown')}", font=fonts.Medium, fill=0)
        draw.text((5, 68), f"REG: {safe_getattr(flight, 'registration', 'N/A')}", font=fonts.Medium, fill=0)

        # Route
        origin_code = safe_getattr(flight, 'origin', 'N/A')
        dest_code = safe_getattr(flight, 'destination', 'N/A')
        route = f"{origin_code} -> {dest_code}"
        draw.text((5, 86), route, font=fonts.Medium, fill=0)

        # Bottom horizontal line
        draw.line((-5, self.height - 15, self.width, self.height - 15), fill=0, width=1)

        # Bottom row details
        altitude = safe_getattr(flight, "altitude", "N/A")
        speed = safe_getattr(flight, "speed", "N/A")

        import time
        timestamp = time.strftime("%H:%M:%S")

        draw.text(
            (5, self.height - 12), f"ALT: {altitude} ft", font=fonts.Small, fill=0
        )
        draw.text(
            (80, self.height - 12), f"SPD: {speed} kts", font=fonts.Small, fill=0
        )
        draw.text(
            (155, self.height - 12), f"TIME: {timestamp}", font=fonts.Small, fill=0
        )

        # Rotate for hardware displays
        rotated_image = image.rotate(180)
        self.display.render(rotated_image)
