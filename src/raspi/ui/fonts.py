from PIL import ImageFont
import os

# Get the absolute path to the local font file
_current_dir = os.path.dirname(os.path.abspath(__file__))
_font_path = os.path.join(_current_dir, "hw", "libs", "fonts", "Font.ttc")

# should not be changed - now uses local font file
FONT_NAME = _font_path

# can be changed
STATUS_FONT_NAME = None
SIZE_OFFSET = 0

Bold = None
BoldSmall = None
BoldBig = None
Medium = None
Small = None
Huge = None


def init(config):
    global STATUS_FONT_NAME, SIZE_OFFSET
    # Handle both nested and flat config structures
    if "ui" in config and "font" in config["ui"]:
        STATUS_FONT_NAME = config["ui"]["font"]["name"]
        SIZE_OFFSET = config["ui"]["font"]["size_offset"]
    else:
        # Fallback defaults
        STATUS_FONT_NAME = FONT_NAME
        SIZE_OFFSET = 0
    setup(10, 8, 10, 25, 25, 9)


def status_font(old_font):
    global STATUS_FONT_NAME, SIZE_OFFSET
    # Use the local font path if STATUS_FONT_NAME is not set or is the default
    font_to_use = (
        STATUS_FONT_NAME
        if STATUS_FONT_NAME and STATUS_FONT_NAME != "DejaVuSansMono"
        else FONT_NAME
    )
    return ImageFont.truetype(font_to_use, size=old_font.size + SIZE_OFFSET)


def setup(bold, bold_small, medium, huge, bold_big, small):
    global Bold, BoldSmall, Medium, Huge, BoldBig, Small, FONT_NAME

    try:
        # Use the local Font.ttc file for all variants
        Small = ImageFont.truetype(FONT_NAME, small)
        Medium = ImageFont.truetype(FONT_NAME, medium)
        BoldSmall = ImageFont.truetype(FONT_NAME, bold_small)
        Bold = ImageFont.truetype(FONT_NAME, bold)
        BoldBig = ImageFont.truetype(FONT_NAME, bold_big)
        Huge = ImageFont.truetype(FONT_NAME, huge)
    except OSError:
        # Fallback to system DejaVuSansMono if local font fails
        try:
            fallback_font = "DejaVuSansMono"
            Small = ImageFont.truetype(fallback_font, small)
            Medium = ImageFont.truetype(fallback_font, medium)
            BoldSmall = ImageFont.truetype("%s-Bold" % fallback_font, bold_small)
            Bold = ImageFont.truetype("%s-Bold" % fallback_font, bold)
            BoldBig = ImageFont.truetype("%s-Bold" % fallback_font, bold_big)
            Huge = ImageFont.truetype("%s-Bold" % fallback_font, huge)
        except OSError:
            # Last fallback to default font
            Small = ImageFont.load_default()
            Medium = ImageFont.load_default()
            BoldSmall = ImageFont.load_default()
            Bold = ImageFont.load_default()
            BoldBig = ImageFont.load_default()
            Huge = ImageFont.load_default()
    except Exception:
        # Last resort - create dummy font objects
        Small = None
        Medium = None
        BoldSmall = None
        Bold = None
        BoldBig = None
        Huge = None
