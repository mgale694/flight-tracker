#!/usr/bin/env python3
"""
Simple polling example for the simplified API
"""

import time
import requests


def poll_flights():
    """Simple polling example"""
    print("🛩️  Starting flight polling demo...")
    print("⚡ Polling http://localhost:8000/flights every 3 seconds")
    print("📡 Press Ctrl+C to stop\n")

    while True:
        try:
            response = requests.get("http://localhost:8000/flights", timeout=5)
            data = response.json()

            timestamp = time.strftime("%H:%M:%S")
            flight_count = len(data.get("flights", []))
            location = data.get("location", "Unknown")

            print(f"[{timestamp}] {flight_count} flights detected near {location}")

            if flight_count > 0:
                for flight in data["flights"]:
                    print(
                        f"  ✈️  {flight.get('callsign', 'Unknown')} at {flight.get('altitude', 'Unknown')} ft"
                    )

            time.sleep(3)

        except KeyboardInterrupt:
            print("\n👋 Stopping polling demo")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
            time.sleep(3)


if __name__ == "__main__":
    poll_flights()
