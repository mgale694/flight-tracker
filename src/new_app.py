#!/usr/bin/python
# -*- coding:utf-8 -*-
import sys
import os

picdir = os.path.join(os.path.dirname(os.path.realpath(__file__)), "pic")
libdir = os.path.join(os.path.dirname(os.path.realpath(__file__)), "lib")
if os.path.exists(libdir):
    sys.path.append(libdir)

import logging
from waveshare_epd import epd2in13_V4
import time
from PIL import Image, ImageDraw, ImageFont
import traceback

logging.basicConfig(level=logging.DEBUG)

from FlightRadar24 import FlightRadar24API
from datetime import datetime
from geopy.geocoders import Nominatim
import time


try:
    logging.info("Flight Tracker v1")

    epd = epd2in13_V4.EPD()
    logging.info("init and Clear")
    epd.init()
    epd.Clear(0xFF)

    # Drawing on the image
    font10 = ImageFont.truetype(os.path.join(picdir, "Font.ttc"), 10)
    font15 = ImageFont.truetype(os.path.join(picdir, "Font.ttc"), 15)
    font20 = ImageFont.truetype(os.path.join(picdir, "Font.ttc"), 20)

    logging.info("E-paper refresh")
    epd.init()

    # --- CONFIGURATION ---
    # You can change this address to any valid location
    ADDRESS = "31 Maltings Place, Fulham, London, SW62BU"
    SEARCH_RADIUS_METERS = 3000  # 3km radius
    MAX_FLIGHTS = 20
    MAX_ELAPSED_TIME = 30 * 60  # 30 minutes in seconds

    # --- LOCATION SETUP ---
    loc = Nominatim(user_agent="Geopy Library")
    getLoc = loc.geocode(ADDRESS)
    if not getLoc:
        raise Exception(f"Could not geocode address: {ADDRESS}")

    logging.info(f"Location found: {getLoc.address}")
    logging.info(f"Coordinates: {[getLoc.latitude, getLoc.longitude]}")

    # --- FLIGHT API SETUP ---
    fr_api = FlightRadar24API()

    # --- BOUNDS ---
    bounds = fr_api.get_bounds_by_point(
        getLoc.latitude, getLoc.longitude, SEARCH_RADIUS_METERS
    )

    # --- FETCH FLIGHTS ---
    flights_overhead_detailed = {}
    flights_overhead = {}
    logging.info(
        f"\nFlight status over {getLoc.address.split(',')[0]}, {getLoc.address.split(',')[-1].strip()}"
    )
    logging.info("-" * 80)
    logging.info("Setting up tracker")
    time_image = Image.new("1", (epd.height, epd.width), 255)
    time_draw = ImageDraw.Draw(time_image)
    epd.displayPartBaseImage(epd.getbuffer(time_image))
    num = 0

    start_time = time.time()

    while len(flights_overhead) < MAX_FLIGHTS:
        flights = fr_api.get_flights(bounds=bounds)
        if not flights:
            time.sleep(2)
            continue
        for flight in flights:
            flight_details = fr_api.get_flight_details(flight)
            flight.set_flight_details(flight_details)

            logging.info(f"aircraft_age: {flight.aircraft_age}")
            logging.info(f"aircraft_country_id: {flight.aircraft_country_id}")
            logging.info(f"registration: {flight.registration}")
            logging.info(f"aircraft_model: {flight.aircraft_model}")
            logging.info(f"airline_name: {flight.airline_name}")
            logging.info(f"airline_short_name: {flight.airline_short_name}")

            flights_overhead_detailed[flight.id] = flight
            if flight.callsign not in flights_overhead:
                flights_overhead[flight.callsign] = {
                    "FROM": flight.origin_airport_name,
                    "TO": flight.destination_airport_name,
                }
                logging.info(
                    f"FLIGHT: {flight.callsign} | FROM: {flight.origin_airport_name} | TO: {flight.destination_airport_name} | TIME: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                )
                logging.info(
                    f"  Aircraft: {getattr(flight, 'aircraft_type', 'N/A')}, Altitude: {getattr(flight, 'altitude', 'N/A')} ft, Speed: {getattr(flight, 'ground_speed', 'N/A')} km/h"
                )
                logging.info("-" * 80)
                # Clear image before drawing
                time_image = Image.new("1", (epd.height, epd.width), 255)
                time_draw = ImageDraw.Draw(time_image)

                elapsed = int(time.time() - start_time)
                elapsed_str = time.strftime("%H:%M:%S", time.gmtime(elapsed))
                time_draw.text((5, 2), f"ATC: {flight.callsign}", font=font10, fill=0)
                time_draw.text(
                    (80, 2), f"COUNT: {len(flights_overhead)}", font=font10, fill=0
                )
                time_draw.text((155, 2), f"TIMER: {elapsed_str}", font=font10, fill=0)

                # Horizontal line under top row
                time_draw.line((-5, 15, epd.height, 15), fill=0, width=1)

                from_str = f"FROM: {flight.origin_airport_name}"
                if len(from_str) > 32:
                    from_str = from_str[:32] + "..."
                time_draw.text((5, 20), from_str, font=font15, fill=0)
                time_draw.text(
                    (5, 36), f"AIRLINE: {flight.airline_name}", font=font15, fill=0
                )
                time_draw.text(
                    (5, 52), f"MODEL: {flight.aircraft_model}", font=font15, fill=0
                )
                time_draw.text(
                    (5, 68), f"REG: {flight.registration}", font=font15, fill=0
                )

                time_draw.text(
                    (5, 86),
                    f"{flight.origin_airport_iata} -> {flight.destination_airport_iata}",
                    font=font15,
                    fill=0,
                )

                # Bottom horizontal line
                time_draw.line(
                    (-5, epd.width - 15, epd.height, epd.width - 15), fill=0, width=1
                )

                altitude = getattr(flight, "altitude", "N/A")
                speed = getattr(flight, "ground_speed", "N/A")
                timestamp = datetime.now().strftime("%H:%M:%S")
                time_draw.text(
                    (5, epd.width - 12), f"ALT: {altitude} ft", font=font10, fill=0
                )
                time_draw.text(
                    (80, epd.width - 12), f"SPD: {speed} km/h", font=font10, fill=0
                )
                time_draw.text(
                    (155, epd.width - 12), f"TIME: {timestamp}", font=font10, fill=0
                )

                # Rotate the image 180 degrees before displaying
                rotated_image = time_image.rotate(180)
                epd.displayPartial(epd.getbuffer(rotated_image))

            if len(flights_overhead) >= MAX_FLIGHTS or elapsed > MAX_ELAPSED_TIME:
                break
        time.sleep(2)

    logging.info("Clear...")
    epd.init()
    epd.Clear(0xFF)

    logging.info("Goto Sleep...")
    epd.sleep()

except IOError as e:
    logging.info(e)

except KeyboardInterrupt:
    logging.info("ctrl + c:")

    logging.info("Clear...")
    epd.init()
    epd.Clear(0xFF)

    logging.info("Goto Sleep...")
    epd.sleep()

    epd2in13_V4.epdconfig.module_exit(cleanup=True)
    exit()
