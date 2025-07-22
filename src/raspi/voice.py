import random


class Voice:
    def __init__(self):
        pass

    def on_starting(self):
        return random.choice(
            [
                "Flight Tracker starting up...",
                "Scanning the skies...",
                "Ready to track flights!",
                "Looking up for aircraft...",
            ]
        )

    def on_flight_detected(self, callsign):
        return random.choice(
            [
                f"Found {callsign} overhead!",
                f"Tracking {callsign}",
                f"Aircraft {callsign} detected",
                f"New flight: {callsign}",
            ]
        )

    def on_boot_complete(self):
        return random.choice(
            [
                "Boot sequence complete!",
                "System ready!",
                "All systems go!",
                "Ready for flight tracking!",
            ]
        )

    def on_scanning(self):
        return random.choice(
            [
                "Scanning for aircraft...",
                "Listening to the sky...",
                "Searching for flights...",
                "Monitoring airspace...",
            ]
        )

    def on_session_complete(self, count):
        return random.choice(
            [
                f"Session complete! Tracked {count} flights",
                f"Found {count} aircraft today",
                f"Flight tracking session ended: {count} flights",
                f"Monitored {count} flights overhead",
            ]
        )

    def on_no_flights(self):
        return random.choice(
            [
                "Sky is quiet today...",
                "No aircraft detected",
                "Peaceful skies",
                "Waiting for flights...",
            ]
        )
