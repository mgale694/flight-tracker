from unittest import TestCase

from PIL import Image

from agent import FlightTrackerAgent
from ui import fonts
from ui.view import FlightView


class FakeDisplay:
    width = 250
    height = 122

    def __init__(self) -> None:
        self.image: Image.Image | None = None

    def render(self, image: Image.Image) -> None:
        self.image = image


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
