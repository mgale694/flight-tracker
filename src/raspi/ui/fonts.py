from PIL import ImageFont

# should not be changed
FONT_NAME = "DejaVuSansMono"

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
    return ImageFont.truetype(STATUS_FONT_NAME, size=old_font.size + SIZE_OFFSET)


def setup(bold, bold_small, medium, huge, bold_big, small):
    global Bold, BoldSmall, Medium, Huge, BoldBig, Small, FONT_NAME

    try:
        Small = ImageFont.truetype(FONT_NAME, small)
        Medium = ImageFont.truetype(FONT_NAME, medium)
        BoldSmall = ImageFont.truetype("%s-Bold" % FONT_NAME, bold_small)
        Bold = ImageFont.truetype("%s-Bold" % FONT_NAME, bold)
        BoldBig = ImageFont.truetype("%s-Bold" % FONT_NAME, bold_big)
        Huge = ImageFont.truetype("%s-Bold" % FONT_NAME, huge)
    except OSError:
        # Fallback to default font if DejaVuSansMono is not available
        try:
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
