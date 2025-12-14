"""Main agent for the flight tracker e-ink display client"""
import time
import logging
import toml
from pathlib import Path

import faces
import utils
from log import SessionLog
from tracker import FlightTracker
from ui.display import Display


class FlightTrackerAgent:
    """Main agent that coordinates flight tracking and display"""
    
    def __init__(self, config_path="config.toml"):
        # Load configuration
        self.config = self._load_config(config_path)
        
        # Setup logging
        utils.setup_logging(self.config)
        logging.info("="  * 50)
        logging.info("Flight Tracker Agent Starting")
        logging.info("=" * 50)
        
        # Initialize components
        self.session_log = SessionLog()
        self.tracker = FlightTracker(self.config)
        self.display = Display(self.config)
        
        # Get configuration values
        ui_config = self.config.get("ui", {})
        self.boot_duration = ui_config.get("boot_screen_duration", 10)
        self.flight_interval = ui_config.get("flight_rotation_interval", 5)
        
        self.running = False
        self.current_flight_index = 0
    
    def _load_config(self, config_path):
        """Load configuration from TOML file"""
        config_file = Path(config_path)
        if not config_file.exists():
            logging.error(f"Config file not found: {config_path}")
            raise FileNotFoundError(f"Config file not found: {config_path}")
        
        with open(config_file, "r") as f:
            return toml.load(f)
    
    def boot(self):
        """Boot sequence with display"""
        face, phrase = faces.get_random_boot_face()
        logging.info(f"Boot: {phrase}")
        
        if self.display.is_enabled():
            self.display.render_boot(face, phrase)
            time.sleep(self.boot_duration)
    
    def run(self):
        """Main run loop"""
        self.running = True
        self.boot()
        
        logging.info("Entering main flight tracking loop")
        
        flights = []
        last_fetch_time = 0
        last_display_update = 0
        fetch_interval = 10  # Fetch flights every 10 seconds
        
        try:
            while self.running:
                current_time = time.time()
                
                # Fetch flights periodically
                if current_time - last_fetch_time >= fetch_interval:
                    logging.info("Fetching flights...")
                    flights = self.tracker.get_flights()
                    logging.info(f"Found {len(flights)} flight(s)")
                    last_fetch_time = current_time
                    
                    # Log first flight if we have any
                    if flights:
                        self.session_log.log_flight(flights[0])
                
                # Update display
                if flights and (current_time - last_display_update >= self.flight_interval):
                    # Rotate through flights
                    flight = flights[self.current_flight_index]
                    stats = self.session_log.get_stats()
                    
                    logging.info(f"Displaying flight: {getattr(flight, 'callsign', 'N/A')}")
                    self.display.render_flight(flight, stats)
                    
                    # Move to next flight
                    self.current_flight_index = (self.current_flight_index + 1) % len(flights)
                    last_display_update = current_time
                
                # Sleep to avoid busy loop
                time.sleep(1)
                
        except KeyboardInterrupt:
            logging.info("Keyboard interrupt received")
        except Exception as e:
            logging.error(f"Error in main loop: {e}", exc_info=True)
        finally:
            self.shutdown()
    
    def shutdown(self):
        """Graceful shutdown"""
        logging.info("Shutting down agent...")
        self.running = False
        
        if self.display.is_enabled():
            self.display.sleep()
        
        logging.info("Agent shutdown complete")


def main():
    """Main entry point"""
    agent = FlightTrackerAgent()
    agent.run()


if __name__ == "__main__":
    main()
