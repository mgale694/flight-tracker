# Flight Tracker API - Polling Implementation

The Flight Tracker API now uses simple HTTP polling instead of WebSockets for real-time updates. This is simpler to implement and more reliable.

## Polling Example for React

```typescript
import { FlightTrackerAPI } from "./api";

class FlightTracker {
  private pollInterval: number = 2000; // 2 seconds
  private intervalId: NodeJS.Timeout | null = null;

  startPolling(onUpdate: (data: any) => void) {
    this.intervalId = setInterval(async () => {
      try {
        // Get current flights
        const flightData = await FlightTrackerAPI.getFlights();

        // Get session status
        const sessionStatus = await FlightTrackerAPI.getSessionStatus();

        onUpdate({
          flights: flightData.flights,
          stats: flightData.stats,
          sessionActive: sessionStatus.active,
        });
      } catch (error) {
        console.error("Polling error:", error);
      }
    }, this.pollInterval);
  }

  stopPolling() {
    if (this.intervalId) {
      clearInterval(this.intervalId);
      this.intervalId = null;
    }
  }
}
```

## Polling Example for Raspi (Python)

```python
import time
import threading
from api_client import FlightTrackerAPIClient

class FlightTrackerPoller:
    def __init__(self, poll_interval=2.0):
        self.poll_interval = poll_interval
        self.running = False
        self.thread = None
        self.api_client = FlightTrackerAPIClient()

    def start_polling(self, callback):
        """Start polling for flight updates"""
        self.running = True
        self.thread = threading.Thread(target=self._poll_loop, args=(callback,))
        self.thread.start()

    def stop_polling(self):
        """Stop polling"""
        self.running = False
        if self.thread:
            self.thread.join()

    def _poll_loop(self, callback):
        """Main polling loop"""
        while self.running:
            try:
                # Get live flight data
                flight_data = self.api_client.get_live_flights()

                # Get session status
                session_status = self.api_client.get_session_status()

                # Call the callback with the data
                callback({
                    'flights': flight_data.get('flights', []),
                    'stats': flight_data.get('stats'),
                    'session_active': session_status.get('active', False)
                })

            except Exception as e:
                print(f"Polling error: {e}")

            time.sleep(self.poll_interval)

# Usage example:
def handle_flight_update(data):
    print(f"Got {len(data['flights'])} flights")
    if data['session_active']:
        print("Session is active")

poller = FlightTrackerPoller()
poller.start_polling(handle_flight_update)

# Later...
poller.stop_polling()
```

## API Endpoints for Polling

- `GET /flights` - Get current flights (basic)
- `GET /flights/live` - Get live flights with enhanced data (for raspi)
- `GET /session/status` - Get session status and stats
- `GET /health` - Check API health
- `POST /session/start` - Start tracking session
- `POST /session/stop` - Stop tracking session

## Benefits of Polling vs WebSockets

1. **Simplicity**: Much easier to implement and debug
2. **Reliability**: No connection state to manage
3. **Error Handling**: Simpler retry logic
4. **Resource Usage**: Lower server resource usage
5. **Scalability**: Better for multiple clients
6. **Firewall Friendly**: Standard HTTP requests work everywhere

## Recommended Polling Intervals

- **React Frontend**: 2-3 seconds (user interface updates)
- **Raspi Display**: 2-5 seconds (display refresh rate)
- **Development/Testing**: 1-2 seconds (faster feedback)
- **Production**: 3-5 seconds (balance between freshness and load)
