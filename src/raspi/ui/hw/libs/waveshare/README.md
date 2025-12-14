"""Waveshare E-ink Display Libraries

This directory should contain the Waveshare EPD library files.

To set up:

1. Download the Waveshare e-Paper library from:
   https://github.com/waveshare/e-Paper/tree/master/RaspberryPi_JetsonNano/python/lib/waveshare_epd

2. Copy the following files to this directory:

   - epd2in13_V4.py (for 2.13" V4 display)
   - epdconfig.py (hardware configuration)

3. Make sure you have the required system packages:
   sudo apt-get install python3-rpi.gpio python3-spidev python3-pil

4. Enable SPI interface:
   sudo raspi-config
   -> Interface Options -> SPI -> Enable
   """
