from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase

import toml

from models import ConfigUpdate
from services import ConfigService


class ConfigServicePairingTests(TestCase):
    def setUp(self) -> None:
        self.temporary_directory = TemporaryDirectory()
        self.addCleanup(self.temporary_directory.cleanup)
        self.config_file = Path(self.temporary_directory.name) / "config.toml"
        self.config_file.write_text(
            toml.dumps(
                {
                    "main": {
                        "address": "Test window",
                        "search_radius_meters": 3_000,
                        "max_flights": 20,
                        "max_elapsed_time": 1_800,
                        "display_hold_time": 30,
                    },
                    "viewing_zone": {
                        "bearing_degrees": 0,
                        "field_of_view_degrees": 80,
                        "min_distance_km": 0,
                        "max_distance_km": 35,
                    },
                    "device": {
                        "public_id": "dev-kit-001",
                        "pairing_code": "SKY281",
                        "paired": False,
                        "setup_url": "auto",
                    },
                }
            )
        )
        self.service = ConfigService(self.config_file)

    def test_pairing_requires_matching_device_and_code(self) -> None:
        with self.assertRaises(LookupError):
            self.service.pair_device("unknown", "SKY281")
        with self.assertRaises(PermissionError):
            self.service.pair_device("dev-kit-001", "WRONG1")

        device = self.service.pair_device("dev-kit-001", "sky281")

        self.assertTrue(device["paired"])
        self.assertTrue(self.service.load_config()["device"]["paired"])

    def test_viewing_zone_update_is_persisted(self) -> None:
        config, updates = self.service.update_config(
            ConfigUpdate(
                bearing_degrees=350,
                field_of_view_degrees=70,
                max_distance_km=28,
                display_hold_time=45,
            )
        )

        self.assertEqual(config["viewing_zone"]["bearing_degrees"], 350)
        self.assertEqual(config["viewing_zone"]["field_of_view_degrees"], 70)
        self.assertEqual(config["viewing_zone"]["max_distance_km"], 28)
        self.assertEqual(config["main"]["display_hold_time"], 45)
        self.assertEqual(updates["bearing_degrees"], 350)

    def test_invalid_cross_field_ranges_are_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "viewing distance"):
            self.service.update_config(
                ConfigUpdate(min_distance_km=30, max_distance_km=20)
            )

