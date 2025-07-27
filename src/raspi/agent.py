import time
import logging
import os
from .api_client import FlightTrackerAPIAdapter
from .ui.display import Display
from .faces import get_random_boot_face
from .voice import Voice


class FlightAgent:
    """Main flight tracking agent following pwnagotchi pattern"""

    def __init__(self, config):
        self.config = config
        print("🔧 Initializing FlightAgent...")

        # Flatten config for tracker (it expects flat structure)
        tracker_config = {
            "address": config.get("main", {}).get(
                "address", "31 Maltings Place, Fulham, London, SW62BU"
            ),
            "search_radius_meters": config.get("main", {}).get(
                "search_radius_meters", 3000
            ),
            "max_flights": config.get("main", {}).get("max_flights", 20),
            "max_elapsed_time": config.get("main", {}).get("max_elapsed_time", 1800),
            "log_path": config.get("logging", {}).get(
                "path", "/tmp/flight_tracker.log"
            ),
        }

        print("🔧 Initializing FlightTracker...")
        try:
            # Try to get config from backend API first, fallback to local config
            backend_url = config.get("api", {}).get(
                "backend_url", "http://localhost:8000"
            )
            self.tracker = FlightTrackerAPIAdapter(tracker_config, backend_url)
            print("✓ FlightTracker initialized (with API backend)")
        except Exception as e:
            print(f"❌ Error initializing FlightTracker: {e}")
            raise

        print("🔧 Initializing Display...")
        try:
            self.display = Display(config)
            print("✓ Display initialized")
        except Exception as e:
            print(f"❌ Error initializing Display: {e}")
            raise

        print("🔧 Initializing Voice...")
        try:
            self.voice = Voice()
            print("✓ Voice initialized")
        except Exception as e:
            print(f"❌ Error initializing Voice: {e}")
            raise

        # State
        self.running = False
        self.boot_complete = False
        print("✓ FlightAgent initialization complete")

    def run(self):
        """Main run loop"""
        try:
            print("🚀 Starting Flight Tracker run loop...")
            self.running = True
            logging.info(self.voice.on_starting())
            print("✓ Voice starting message logged")

            # Boot sequence
            print("🔧 Starting boot sequence...")
            self._boot_sequence()
            print("✓ Boot sequence completed")

            # Main tracking loop
            print("🔧 Starting main tracking loop...")
            self._tracking_loop()
            print("✓ Tracking loop completed")

        except KeyboardInterrupt:
            print("⚠️  Keyboard interrupt received")
            logging.info("Shutting down...")
        except Exception as e:
            print(f"❌ Error in main loop: {e}")
            logging.error(f"Error in main loop: {e}")
            raise
        finally:
            print("🔧 Running shutdown sequence...")
            self._shutdown()
            print("✓ Shutdown complete")

    def _boot_sequence(self):
        """Handle boot sequence with face and phrase"""
        print("🎭 Getting random boot face...")
        face, phrase = get_random_boot_face()
        print(f"✓ Boot face: {phrase}")
        logging.info(f"BOOT: {phrase}")

        print("🖥️  Checking if display is enabled...")
        if self.display.is_enabled():
            print("✓ Display is enabled, rendering boot screen...")
            try:
                self.display.render_boot(face, phrase)
                print("✓ Boot screen rendered")
            except Exception as e:
                print(f"❌ Error rendering boot screen: {e}")
                logging.error(f"Error rendering boot screen: {e}")
                # Continue without display

            # Shorter boot time in development mode
            boot_time = (
                3 if self.config.get("development", {}).get("enabled", False) else 10
            )
            print(f"⏱️  Sleeping for {boot_time} seconds...")
            time.sleep(boot_time)
            print("✓ Boot sleep completed")
        else:
            print("⚠️  Display is disabled, skipping boot screen")

        self.boot_complete = True
        print("✓ Boot sequence complete")
        logging.info(self.voice.on_boot_complete())

    def _tracking_loop(self):
        """Main flight tracking loop"""
        self.tracker.start_session()

        while self.running and self.tracker.should_continue():
            stats = self.tracker.get_session_stats()

            # Get flights in area
            flights = self.tracker.get_flights()

            if not flights:
                # Just wait silently, no scanning screen
                time.sleep(2)
                continue

            # Process each flight
            for flight in flights:
                if not self.tracker.should_continue():
                    break

                # Get detailed flight information
                detailed_flight = self.tracker.get_flight_details(flight)

                # Check if this is a new flight
                if self.tracker.process_flight(detailed_flight):
                    logging.info(
                        self.voice.on_flight_detected(detailed_flight.callsign)
                    )

                    # Rich terminal logging for new flight
                    self._log_flight_details(detailed_flight)

                    # Update display with flight info
                    if self.display.is_enabled():
                        updated_stats = self.tracker.get_session_stats()
                        self.display.render_flight(detailed_flight, updated_stats)
                        print(
                            f"🖥️  Flight {detailed_flight.callsign} displayed on screen"
                        )

            time.sleep(2)

        # Session complete
        stats = self.tracker.get_session_stats()
        logging.info(self.voice.on_session_complete(stats["flights_count"]))

    def _log_flight_details(self, flight):
        """Log rich flight details to terminal"""
        print("\n" + "=" * 60)
        print("✈️  NEW FLIGHT DETECTED")
        print("=" * 60)
        print(f"🏷️  Callsign:     {flight.callsign}")
        print(f"🏢  Airline:      {getattr(flight, 'airline_name', 'Unknown')}")
        print(f"✈️  Aircraft:     {getattr(flight, 'aircraft_model', 'Unknown')}")
        print(f"🔖  Registration: {getattr(flight, 'registration', 'Unknown')}")

        # Route information
        origin = getattr(flight, "origin_airport_name", "Unknown")
        dest = getattr(flight, "destination_airport_name", "Unknown")
        origin_code = getattr(flight, "origin_airport_iata", "N/A")
        dest_code = getattr(flight, "destination_airport_iata", "N/A")

        print(f"🛫  From:         {origin} ({origin_code})")
        print(f"🛬  To:           {dest} ({dest_code})")

        # Flight data
        altitude = getattr(flight, "altitude", "Unknown")
        speed = getattr(flight, "ground_speed", "Unknown")

        print(f"📏  Altitude:     {altitude} ft")
        print(f"🚀  Speed:        {speed} km/h")

        # Position
        if hasattr(flight, "latitude") and hasattr(flight, "longitude"):
            print(f"📍  Position:     {flight.latitude:.4f}, {flight.longitude:.4f}")

        print("=" * 60)
        print()

    def _shutdown(self):
        """Clean shutdown"""
        self.running = False

        if self.display.is_enabled():
            self.display.clear()
            self.display.sleep()

        logging.info("Flight tracker shutdown complete")


def main():
    """Main entry point for production deployment"""
    import toml

    logging.info("Initializing logging configuration...")
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler("/tmp/flight_tracker.log"),
            logging.StreamHandler(),
        ],
    )

    logging.info("Attempting to load configuration from config.toml...")
    # Load configuration from config.toml
    config_path = os.path.join(os.path.dirname(__file__), "config.toml")

    try:
        with open(config_path, "r") as f:
            config = toml.load(f)
        logging.info("Configuration loaded from config.toml")
    except Exception as e:
        logging.error(f"Error loading config: {e}")
        logging.info("Using default configuration")
        # Default configuration as fallback
        config = {
            "main": {
                "address": "31 Maltings Place, Fulham, London, SW62BU",
                "search_radius_meters": 3000,
                "max_flights": 20,
                "max_elapsed_time": 1800,  # 30 minutes
            },
            "display": {"enabled": True, "type": "waveshare2in13v4", "rotation": 180},
            "logging": {"level": "INFO", "path": "/tmp/flight_tracker.log"},
            "development": {"enabled": False},
        }

    logging.info("Instantiating FlightAgent...")
    print("🔧 Creating FlightAgent instance...")
    # Create and run agent
    try:
        agent = FlightAgent(config)
        print("✓ FlightAgent created successfully")
        logging.info("Starting Flight Tracker in production mode")
        print("🚀 Starting main run loop...")
        agent.run()
        print("✓ Flight Tracker run() completed")
    except Exception as e:
        print(f"❌ Error during FlightAgent execution: {e}")
        logging.error(f"Error during FlightAgent execution: {e}")
        raise

    logging.info("Flight Tracker main() has exited")
    print("✓ Flight Tracker main() has exited")


if __name__ == "__main__":
    main()
