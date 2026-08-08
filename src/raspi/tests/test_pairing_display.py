from unittest import TestCase

from PIL import Image, ImageDraw

from agent import FlightTrackerAgent
from ui import fonts
from ui.view import FlightView, fit_text_to_width


class FakeDisplay:
    width = 250
    height = 122

    def __init__(self) -> None:
        self.image: Image.Image | None = None
        self.used_full_refresh = False

    def render(self, image: Image.Image) -> None:
        self.image = image

    def render_full(self, image: Image.Image) -> None:
        self.image = image
        self.used_full_refresh = True


class PairingDisplayTests(TestCase):
    def test_pairing_screen_renders_without_hardware(self) -> None:
        fonts.init({})
        display = FakeDisplay()
        view = FlightView(display)

        view.render_pairing_screen(
            "http://192.168.1.10:5173/setup?d=dev-kit-001&c=SKY281",
            "SKY281",
        )

        self.assertIsNotNone(display.image)
        assert display.image is not None
        self.assertEqual(display.image.size, (250, 122))
        self.assertEqual(display.image.mode, "1")
        self.assertTrue(display.used_full_refresh)
        black_pixels = display.image.histogram()[0]
        self.assertGreater(black_pixels, 1_000)

    def test_pairing_url_contains_short_device_parameters(self) -> None:
        agent = object.__new__(FlightTrackerAgent)
        agent.setup_url = "http://flight-tracker.local:5173/setup"
        agent.device_id = "dev-kit-001"
        agent.pairing_code = "SKY281"

        pairing_url = agent._pairing_url()

        self.assertEqual(
            pairing_url,
            "http://flight-tracker.local:5173/setup?d=dev-kit-001&c=SKY281",
        )

    def test_rotation_recovers_when_live_flight_list_shrinks(self) -> None:
        agent = object.__new__(FlightTrackerAgent)
        agent.current_flight_index = 4
        flights = ["first", "second"]

        selected = agent._next_flight(flights)

        self.assertEqual(selected, "first")
        self.assertEqual(agent.current_flight_index, 1)

    def test_long_airport_name_is_ellipsized_to_display_width(self) -> None:
        fonts.init({})
        draw = ImageDraw.Draw(Image.new("1", (250, 122), 255))

        label = fit_text_to_width(
            draw,
            "FROM: A Very Long International Airport Name That Will Not Fit",
            fonts.Medium,
            240,
        )

        self.assertTrue(label.endswith("..."))
        self.assertLessEqual(draw.textbbox((0, 0), label, font=fonts.Medium)[2], 240)
