"""Font management for the display"""
from PIL import ImageFont
import os

# Get the absolute path to the local font file
_current_dir = os.path.dirname(os.path.abspath(__file__))
_font_path = os.path.join(_current_dir, "hw", "libs", "fonts", "Font.ttc")

# Font path
FONT_NAME = _font_path

# Font globals
Bold = None
BoldSmall = None
BoldBig = None
Medium = None
Small = None
Huge = None


def init(config):
    """Initialize fonts with configuration"""
    setup(10, 8, 10, 25, 25, 9)


def setup(bold, bold_small, medium, huge, bold_big, small):
    """Setup all font sizes"""
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


def status_font(old_font):
    """Get status font (for compatibility)"""
    return old_font
