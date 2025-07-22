from FlightRadar24 import FlightRadar24API
from datetime import datetime
import streamlit as st
# importing geopy library and Nominatim class
from geopy.geocoders import Nominatim
from components.direction_selector import select_direction, show_location_map
from components.flight_fetcher import fetch_and_display_flights

# calling the Nominatim tool and create Nominatim class
loc = Nominatim(user_agent="Geopy Library")

fr_api = FlightRadar24API()

st.title("Flight Tracker")

# User input for address/postcode
address_input = st.text_input("Enter your address or postcode:", placeholder="10 Downing St, London or SW1A 2AA")
# Placeholder for displaying location found info
location_found_info = st.empty()

# Address check/confirm logic
address_checked = False
address_confirmed = False
getLoc = None

cols = st.columns(4)
with cols[0]:
    if st.button("Check Address"):
        if address_input:
            getLoc = loc.geocode(address_input)
            if getLoc:
                st.session_state['checked_address'] = getLoc.address
                st.session_state['getLoc'] = getLoc
                address_checked = True
            else:
                st.error("Could not find the location. Please check your input.")
        else:
            st.error("Please enter an address or postcode.")

with cols[1]:
    if 'checked_address' in st.session_state:
        location_found_info.info(f"Location found: {st.session_state['checked_address']}")
        if st.button("Confirm Address"):
            st.session_state['address_confirmed'] = True

if st.session_state.get('address_confirmed', False):
    getLoc = st.session_state['getLoc']
    # Improved options for directions and distances
    options = {
        "North": [getLoc.latitude + 0.02, getLoc.longitude],
        "North-East": [getLoc.latitude + 0.014, getLoc.longitude + 0.014],
        "East": [getLoc.latitude, getLoc.longitude + 0.02],
        "South-East": [getLoc.latitude - 0.014, getLoc.longitude + 0.014],
        "South": [getLoc.latitude - 0.02, getLoc.longitude],
        "South-West": [getLoc.latitude - 0.014, getLoc.longitude - 0.014],
        "West": [getLoc.latitude, getLoc.longitude - 0.02],
        "North-West": [getLoc.latitude + 0.014, getLoc.longitude - 0.014],
        "Overhead": [getLoc.latitude, getLoc.longitude],
    }

    direction = select_direction(options)

    # User can select the search radius
    radius_km = st.slider("How far out do you want to look? (km)", min_value=0.1, max_value=10.0, value=1.0, step=0.1)
    radius_m = radius_km * 1000

    if st.button("Track Flights"):
        translated_latlng = options.get(direction)
        # st.write(f"Real: {[getLoc.latitude, getLoc.longitude]} - Translated: {translated_latlng}")
        # st.write(f"Search radius: {radius_km} km")

        # Show real and translated locations on a map with custom markers and a translucent search radius
        show_location_map(getLoc, translated_latlng, radius_m, radius_km)

        bounds = fr_api.get_bounds_by_point(translated_latlng[0], translated_latlng[1], radius_m)
        fetch_and_display_flights(fr_api, bounds, max_flights=10, address=st.session_state['checked_address'])