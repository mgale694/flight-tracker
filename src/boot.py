#!/usr/bin/python
# -*- coding:utf-8 -*-
import os
import random
import sys

picdir = os.path.join(os.path.dirname(os.path.realpath(__file__)), "pic")
libdir = os.path.join(os.path.dirname(os.path.realpath(__file__)), "lib")
if os.path.exists(libdir):
    sys.path.append(libdir)

import logging
import time
import traceback

from PIL import Image, ImageDraw, ImageFont
from waveshare_epd import epd2in13_V4

logging.basicConfig(level=logging.DEBUG)

import time
from datetime import datetime

from FlightRadar24 import FlightRadar24API
from geopy.geocoders import Nominatim

try:
    logging.info("Flight Tracker v1")

    epd = epd2in13_V4.EPD()
    logging.info("init and Clear")
    epd.init()
    epd.Clear(0xFF)

    MAX_ELAPSED_TIME = 20  # seconds

    # Drawing on the image
    font10 = ImageFont.truetype(os.path.join(picdir, "Font.ttc"), 10)
    font15 = ImageFont.truetype(os.path.join(picdir, "Font.ttc"), 15)
    font20 = ImageFont.truetype(os.path.join(picdir, "Font.ttc"), 20)
    font25 = ImageFont.truetype(os.path.join(picdir, "Font.ttc"), 25)
    font30 = ImageFont.truetype(os.path.join(picdir, "Font.ttc"), 30)

    logging.info("E-paper refresh")
    epd.init()

    logging.info("-" * 80)
    logging.info("Setting up boot")
    time_image = Image.new("1", (epd.height, epd.width), 255)
    time_draw = ImageDraw.Draw(time_image)
    epd.displayPartBaseImage(epd.getbuffer(time_image))
    num = 0

    # start_time = time.time()

    faces_and_phrases = [
        ("(-__-)", "Oi I was sleeping!"),  # (°▃▃°)"
        ("(•__•)", "Wakey wakey!"),  # (☓‿‿☓)"
        ("(≤__≤)", "Rise and shine!"),  # (◕‿‿◕)"
        ("(*__*)", "Back from dreamland..."),  # (⌐■_■)"
        ("(≠__≠)", "Did you bring coffee?"),  # (≖__≖)"
        ("(*__*)", "Yawn... what's up?"),  # (⌐■_■)"
        ("(ø__ø)", "Booting up with a smile!"),  # ( ◕‿◕)"
        ("(#__#)", "Let me stretch first..."),  # (#__#)"
        ("(≥__≥)", "Good morning, world!"),  # ( ◕‿◕)"
        ("(O__O)", "Ready for takeoff!"),
    ]
    chosen_face, chosen_phrase = random.choice(faces_and_phrases)

    logging.info("-" * 80)
    # Clear image before drawing
    time_image = Image.new("1", (epd.height, epd.width), 255)
    time_draw = ImageDraw.Draw(time_image)

    # elapsed = int(time.time() - start_time)
    # elapsed_str = time.strftime("%H:%M:%S", time.gmtime(elapsed))
    # time_draw.text((5, 2), f"ATC: {flight.callsign}", font=font10, fill=0)
    # time_draw.text((80, 2), f"COUNT: {len(flights_overhead)}", font=font10, fill=0)
    # time_draw.text((155, 2), f"TIMER: {elapsed_str}", font=font10, fill=0)

    # Horizontal line under top row
    time_draw.line((-5, 15, epd.height, 15), fill=0, width=1)

    from_str = f"{chosen_phrase}"
    if len(from_str) > 32:
        from_str = from_str[:32] + "..."
    time_draw.text((5, 20), from_str, font=font15, fill=0)
    # time_draw.text((5, 36), f"AIRLINE: {flight.airline_name}", font=font15, fill=0)
    time_draw.text((5, 52), f"{chosen_face}", font=font30, fill=0)
    # time_draw.text((5, 68), f"{chosen_face}", font=font20, fill=0)

    # time_draw.text(
    #     (5, 86),
    #     f"{flight.origin_airport_iata} -> {flight.destination_airport_iata}",
    #     font=font15,
    #     fill=0,
    # )

    # Bottom horizontal line
    time_draw.line((-5, epd.width - 15, epd.height, epd.width - 15), fill=0, width=1)

    timestamp = datetime.now().strftime("%H:%M:%S")
    # time_draw.text((5, epd.width - 12), f"ALT: {altitude} ft", font=font10, fill=0)
    # time_draw.text((80, epd.width - 12), f"SPD: {speed} km/h", font=font10, fill=0)
    time_draw.text((155, epd.width - 12), f"TIME: {timestamp}", font=font10, fill=0)

    # Rotate the image 180 degrees before displaying
    rotated_image = time_image.rotate(180)
    epd.displayPartial(epd.getbuffer(rotated_image))

    time.sleep(10)

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
