from datetime import datetime
import streamlit as st

def fetch_and_display_flights(fr_api, bounds, max_flights=10, address=None):
    """
    Fetch flights using the API and display them in Streamlit.
    """
    flights_overhead_detailed = {}
    flights_overhead = {}

    if address:
        # Extract first line and postcode
        parts = [p.strip() for p in address.split(",")]
        if len(parts) > 1:
            display_address = f"{parts[0]}, {parts[-1]}"
        else:
            display_address = address
        st.subheader(f"\nFlight status over {display_address}")
    else:
        st.subheader("\nFlight status over your location")
    st.divider()

    while len(flights_overhead) < max_flights:
        flights = fr_api.get_flights(bounds=bounds)

        if len(flights) > 0:
            for flight in flights:
                flight_details = fr_api.get_flight_details(flight)
                flight.set_flight_details(flight_details)

                flights_overhead_detailed[flight.id] = flight

                if flight.callsign not in flights_overhead:
                    flights_overhead[flight.callsign] = {"FROM": flight.origin_airport_name, "TO": flight.destination_airport_name}
                    # Display flight info using st.metric
                    st.metric(
                        label=f"{flight.origin_airport_name} → {flight.destination_airport_name}",
                        value=f"Flight: {flight.callsign}",
                        delta=datetime.now().strftime('%H:%M:%S'),
                        delta_color="off",
                        border=True,
                        help=f"Aircraft: {getattr(flight, 'aircraft_type', 'N/A')}, Altitude: {getattr(flight, 'altitude', 'N/A')} ft, Speed: {getattr(flight, 'ground_speed', 'N/A')} km/h"
                    )
                    st.divider()
