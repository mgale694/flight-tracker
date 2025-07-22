from PIL import Image, ImageDraw
import logging
from . import fonts


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
        display_phrase = phrase
        if len(phrase) > 32:
            display_phrase = phrase[:29] + "..."

        draw.text((5, 20), display_phrase, font=fonts.Medium, fill=0)
        draw.text((5, 52), face, font=fonts.Huge, fill=0)

        # Bottom line and timestamp
        draw.line((-5, self.height - 15, self.width, self.height - 15), fill=0, width=1)

        import time

        timestamp = time.strftime("%H:%M:%S")
        draw.text(
            (155, self.height - 12), f"TIME: {timestamp}", font=fonts.Small, fill=0
        )

        # Only rotate for hardware displays, not development
        if self.display.name == "development":
            self.display.display_partial(self._get_image_buffer(image))
        else:
            rotated_image = image.rotate(180)
            # Use pwnagotchi-style render method for hardware displays
            self.display.render(self._get_image_buffer(rotated_image))

    def render_flight_screen(self, flight, stats):
        """Render flight information screen matching original format"""
        image = Image.new("1", (self.width, self.height), 255)
        draw = ImageDraw.Draw(image)

        # Top row with flight info (using small font like font10)
        draw.text((5, 2), f"ATC: {flight.callsign}", font=fonts.Small, fill=0)
        draw.text((80, 2), f"COUNT: {stats['flights_count']}", font=fonts.Small, fill=0)
        draw.text((155, 2), f"TIMER: {stats['elapsed_str']}", font=fonts.Small, fill=0)

        # Horizontal line under top row (using width like epd.height)
        draw.line((-5, 15, self.width, 15), fill=0, width=1)

        # Flight details (using medium font like font15)
        from_str = f"FROM: {flight.origin_airport_name}"
        if len(from_str) > 32:
            from_str = from_str[:32] + "..."

        draw.text((5, 20), from_str, font=fonts.Medium, fill=0)
        draw.text((5, 36), f"AIRLINE: {flight.airline_name}", font=fonts.Medium, fill=0)
        draw.text((5, 52), f"MODEL: {flight.aircraft_model}", font=fonts.Medium, fill=0)
        draw.text((5, 68), f"REG: {flight.registration}", font=fonts.Medium, fill=0)

        # Route (direct format like original)
        route = f"{getattr(flight, 'origin_airport_iata', 'N/A')} -> {getattr(flight, 'destination_airport_iata', 'N/A')}"
        draw.text((5, 86), route, font=fonts.Medium, fill=0)

        # Bottom horizontal line (using height like epd.width)
        draw.line((-5, self.height - 15, self.width, self.height - 15), fill=0, width=1)

        # Bottom row details (using small font like font10)
        altitude = getattr(flight, "altitude", "N/A")
        speed = getattr(flight, "ground_speed", "N/A")

        import time

        timestamp = time.strftime("%H:%M:%S")

        draw.text(
            (5, self.height - 12), f"ALT: {altitude} ft", font=fonts.Small, fill=0
        )
        draw.text(
            (80, self.height - 12), f"SPD: {speed} km/h", font=fonts.Small, fill=0
        )
        draw.text(
            (155, self.height - 12), f"TIME: {timestamp}", font=fonts.Small, fill=0
        )

        # Only rotate for hardware displays, not development
        if self.display.name == "development":
            self.display.display_partial(self._get_image_buffer(image))
        else:
            rotated_image = image.rotate(180)
            # Use pwnagotchi-style render method for hardware displays
            self.display.render(self._get_image_buffer(rotated_image))

    def _get_image_buffer(self, image):
        """Get image buffer for display"""
        # Both development and hardware displays expect PIL Image objects
        return image
