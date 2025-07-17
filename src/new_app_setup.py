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

logging.basicConfig(level=logging.DEBUG)

from datetime import datetime
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

    logging.info("Setting up tracker")
    time_image = Image.new("1", (epd.height, epd.width), 255)
    time_draw = ImageDraw.Draw(time_image)
    epd.displayPartBaseImage(epd.getbuffer(time_image))

    # Clear the image before drawing
    time_image = Image.new("1", (epd.height, epd.width), 255)
    time_draw = ImageDraw.Draw(time_image)

    # Top row: Callsign and timestamp (small font)
    callsign = "BAW123"
    timestamp = datetime.now().strftime("%H:%M:%S")
    time_draw.text((5, 3), f"{callsign}", font=font10, fill=0)
    time_draw.text((80, 3), f"{timestamp}", font=font10, fill=0)

    # Horizontal line under top row
    time_draw.line((-5, 15, epd.height, 15), fill=0, width=1)

    # Middle: From and To airports (medium font)
    from_airport = "London Heathrow"
    to_airport = "New York JFK"
    from_str = f"FROM: {from_airport}"
    to_str = f"TO:   {to_airport}"
    if len(from_str) > 22:
        from_str = from_str[:20] + "..."
    if len(to_str) > 22:
        to_str = to_str[:20] + "..."
    time_draw.text((5, 20), from_str, font=font10, fill=0)
    time_draw.text((5, 35), to_str, font=font10, fill=0)

    # Bottom horizontal line
    time_draw.line((0, epd.width - 15, epd.height, epd.width - 15), fill=0, width=1)

    # Bottom: Altitude and Speed (small font)
    altitude = 35000
    speed = 900
    time_draw.text((5, epd.width - 12), f"ALT: {altitude} ft", font=font10, fill=0)
    time_draw.text((80, epd.width - 12), f"SPD: {speed} km/h", font=font10, fill=0)

    # Rotate and display
    rotated_image = time_image.rotate(180)
    epd.displayPartial(epd.getbuffer(rotated_image))

    # Rotate the image 180 degrees before displaying
    rotated_image = time_image.rotate(180)
    epd.displayPartial(epd.getbuffer(rotated_image))

    time.sleep(120)

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
