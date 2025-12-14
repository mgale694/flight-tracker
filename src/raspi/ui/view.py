"""View rendering for flight information"""
from PIL import Image, ImageDraw
import logging
from . import fonts
import sys
sys.path.append('..')
from utils import safe_getattr, truncate_string


class FlightView:
    """Handles rendering flight information to the display"""

    def __init__(self, display, config=None):
        self.display = display
        self.width = display.width
        self.height = display.height
        self.config = config or {}
        
        # Get display fields from config, default to all fields
        main_config = self.config.get("main", {})
        self.display_fields = main_config.get("display_fields", ["FROM", "AIRLINE", "MODEL", "REG", "ROUTE"])

    def render_boot_screen(self, face, phrase):
        """Render boot screen with face and phrase"""
        image = Image.new("1", (self.width, self.height), 255)
        draw = ImageDraw.Draw(image)

        # Strong horizontal lines (width=2 for better visibility)
        draw.line((-5, 15, self.width, 15), fill=0, width=2)

        # Truncate phrase if too long
        display_phrase = truncate_string(phrase, 32)

        # Display phrase and face with strong text
        draw.text((5, 20), display_phrase, font=fonts.Medium, fill=0)
        draw.text((5, 52), face, font=fonts.Huge, fill=0)

        # Bottom line and timestamp (strong line)
        draw.line((-5, self.height - 15, self.width, self.height - 15), fill=0, width=2)

        import time
        timestamp = time.strftime("%H:%M:%S")
        draw.text(
            (155, self.height - 12), f"TIME: {timestamp}", font=fonts.Small, fill=0
        )

        # Rotate for hardware displays
        rotated_image = image.rotate(180)
        self.display.render(rotated_image)

    def render_flight_screen(self, flight, stats):
        """Render flight information screen with configurable fields"""
        image = Image.new("1", (self.width, self.height), 255)
        draw = ImageDraw.Draw(image)

        # Top row with flight info
        callsign = safe_getattr(flight, 'callsign', 'N/A')
        draw.text((5, 2), f"ATC: {callsign}", font=fonts.Small, fill=0)
        draw.text((80, 2), f"COUNT: {stats.get('unique_count', 0)}", font=fonts.Small, fill=0)
        draw.text((155, 2), f"TIMER: {stats.get('elapsed_str', '0m')}", font=fonts.Small, fill=0)

        # Horizontal line under top row
        draw.line((-5, 15, self.width, 15), fill=0, width=1)

        # Prepare field data
        origin_name = safe_getattr(flight, 'origin_airport_name', None)
        origin_code = safe_getattr(flight, 'origin', 'N/A')
        dest_name = safe_getattr(flight, 'destination_airport_name', None)
        dest_code = safe_getattr(flight, 'destination', 'N/A')
        
        # Display full name with code, or just code if name not available
        if origin_name and origin_name != origin_code:
            origin_display = f"{origin_name} ({origin_code})"
        else:
            origin_display = origin_code
            
        if dest_name and dest_name != dest_code:
            dest_display = f"{dest_name} ({dest_code})"
        else:
            dest_display = dest_code
        
        # For route, just show names without codes to save space
        origin_route = origin_name if origin_name and origin_name != origin_code else origin_code
        dest_route = dest_name if dest_name and dest_name != dest_code else dest_code
        
        # Map field names to their display strings
        field_data = {
            "FROM": truncate_string(f"FROM: {origin_display}", 32),
            "TO": truncate_string(f"TO: {dest_display}", 32),
            "AIRLINE": f"AIRLINE: {safe_getattr(flight, 'airline_name', 'N/A')}",
            "MODEL": f"MODEL: {safe_getattr(flight, 'aircraft_model', 'Unknown')}",
            "REG": f"REG: {safe_getattr(flight, 'registration', 'N/A')}",
            "ROUTE": f"{origin_route} -> {dest_route}"
        }
        
        # Render configured fields dynamically
        y_position = 20
        line_spacing = 16
        
        for field_name in self.display_fields:
            if field_name in field_data:
                draw.text((5, y_position), field_data[field_name], font=fonts.Medium, fill=0)
                y_position += line_spacing

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

    def render_blank_screen(self):
        """Render a completely blank white screen"""
        # Create a blank white image (255 = white for 1-bit displays)
        image = Image.new("1", (self.width, self.height), 255)
        
        # Rotate for hardware displays
        rotated_image = image.rotate(180)
        self.display.render(rotated_image)
