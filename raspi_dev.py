#!/usr/bin/env python3
"""
Flight Tracker - Development Mode
Run on laptop with GUI preview window
"""

import sys
import os
import toml

# Add the raspi module to path
sys.path.append(os.path.join(os.path.dirname(__file__), "raspi"))

from raspi.agent import FlightAgent


def load_config():
    """Load configuration from config.toml"""
    config_path = os.path.join(os.path.dirname(__file__), "raspi", "config.toml")

    try:
        with open(config_path, "r") as f:
            config = toml.load(f)
        return config
    except Exception as e:
        print(f"Error loading config: {e}")
        return get_default_dev_config()


def get_default_dev_config():
    """Get default development configuration"""
    return {
        "main": {
            "address": "31 Maltings Place, Fulham, London, SW62BU",
            "search_radius_meters": 3000,
            "max_flights": 3,  # Fewer flights for dev
            "max_elapsed_time": 180,  # 3 minutes for dev
        },
        "display": {"enabled": True, "type": "waveshare213in_v4", "rotation": 180},
        "development": {
            "enabled": True,
        },
        "logging": {"level": "INFO", "path": "/tmp/flight_tracker_dev.log"},
    }


def main():
    """Main entry point for development mode"""
    print("Flight Tracker - Development Mode (GUI Preview)")
    print("=" * 60)

    # Load configuration
    config = load_config()

    # Force enable development mode
    config["development"] = {
        "enabled": True,
    }

    # Reduce flight count and time for faster development
    config["main"]["max_flights"] = 3
    config["main"]["max_elapsed_time"] = 180  # 3 minutes

    print(f"Location: {config['main']['address']}")
    print(f"Max flights: {config['main']['max_flights']}")
    print(f"Max time: {config['main']['max_elapsed_time']} seconds")
    print("-" * 60)
    print("GUI window will open to show display preview...")
    print("Close the window or press Ctrl+C to stop")
    print("-" * 60)

    # Create and run agent
    try:
        agent = FlightAgent(config)
        agent.run()
    except KeyboardInterrupt:
        print("\nDevelopment session ended by user")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
