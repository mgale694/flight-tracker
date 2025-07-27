from FlightRadar24 import FlightRadar24API
from datetime import datetime

# importing geopy library and Nominatim class
from geopy.geocoders import Nominatim

# calling the Nominatim tool and create Nominatim class
loc = Nominatim(user_agent="Geopy Library")

# entering the location name
getLoc = loc.geocode("31 Maltings Place, Fulham, London, SW62BU")

# printing address
print(getLoc.address)

fr_api = FlightRadar24API()

SEPERATOR = "---------------------------------------------------------------------------------------------------------------------------"

options = {
    "N": [getLoc.latitude + 0.01, getLoc.longitude],
    "E": [getLoc.latitude, getLoc.longitude + 0.01],
    "SE": [getLoc.latitude - 0.006, getLoc.longitude + 0.016],
    "S": [getLoc.latitude - 0.01, getLoc.longitude],
    "W": [getLoc.latitude , getLoc.longitude - 0.01],
}

translated_latlng = options.get("SE")

print(f"Real: {[getLoc.latitude, getLoc.longitude]} - Translated: {translated_latlng}")

bounds = fr_api.get_bounds_by_point(translated_latlng[0], translated_latlng[1], 1000)

flights_overhead_detailed = {}

flights_overhead = {}

print("\n")
print(f"Flight status over Maltings Place, London, UK")
print(SEPERATOR)

while len(flights_overhead) < 10:

    flights = fr_api.get_flights(bounds=bounds)

    if len(flights) > 0:
        for flight in flights:
            flight_details = fr_api.get_flight_details(flight)
            flight.set_flight_details(flight_details)

            flights_overhead_detailed[flight.id] = flight

            if flight.callsign not in flights_overhead:
                flights_overhead[flight.callsign] = {"FROM": flight.origin_airport_name, "TO": flight.destination_airport_name}
                print_str = f"FLIGHT: {flight.callsign} - FROM: {flight.origin_airport_name} - TO: {flight.destination_airport_name} - OVERHEAD NOW: {datetime.now()}"

                print(print_str)
                print(SEPERATOR)
            
    # else:
    #     print("Nothing overhead right now :(", '\r')
    #     print("--------------------------------------")
        

        
    
flights_overhead


# flight = flights[0]

# flight_details = fr_api.get_flight_details(flight)
# flight.set_flight_details(flight_details)

# print("Flying to", flight.destination_airport_name)
    



# zone = fr_api.get_zones()['europe']
    # bounds = fr_api.get_bounds(zone)

    # flights = fr_api.get_flights(
    #     bounds = bounds
    # )
