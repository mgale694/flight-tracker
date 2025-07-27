#!/usr/bin/env python3
"""
Test script to verify raspi can connect to backend API
"""

import sys
import os

# Add raspi module to path
current_dir = os.path.dirname(os.path.abspath(__file__))
raspi_dir = os.path.join(current_dir, "src", "raspi")
sys.path.insert(0, raspi_dir)

from api_client import FlightTrackerAPIClient


def test_api_connection():
    """Test the API connection"""
    print("🔧 Testing API connection...")

    try:
        client = FlightTrackerAPIClient()

        # Test health check
        print("📡 Testing health endpoint...")
        health = client.health_check()
        print(f"✓ Health check successful: {health}")

        # Test config endpoint
        print("⚙️  Testing config endpoint...")
        config = client.get_raspi_config()
        print(f"✓ Config retrieved: {config['main']['address']}")

        # Test live flights
        print("✈️  Testing live flights endpoint...")
        flights_data = client.get_live_flights()
        flight_count = len(flights_data.get("flights", []))
        print(f"✓ Live flights retrieved: {flight_count} flights found")

        if flight_count > 0:
            first_flight = flights_data["flights"][0]
            print(
                f"   First flight: {first_flight.get('callsign', 'Unknown')} at {first_flight.get('altitude', 'Unknown')} ft"
            )

        print("🎉 All API tests passed!")
        return True

    except Exception as e:
        print(f"❌ API test failed: {e}")
        return False


if __name__ == "__main__":
    success = test_api_connection()
    sys.exit(0 if success else 1)
