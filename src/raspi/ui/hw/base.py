"""Base display implementation class"""
import sys
sys.path.append('../..')
import ui.fonts as fonts


class DisplayImpl(object):
    """Base class for display implementations"""
    
    def __init__(self, config, name):
        self.name = name
        print(f"🔧 DisplayImpl.__init__: name={name}")

        # Handle both config structures
        if "ui" in config and "display" in config["ui"]:
            self.config = config["ui"]["display"]
        elif "display" in config:
            self.config = config["display"]
        else:
            raise KeyError("No display configuration found in config")

        print(f"🔧 Display config: {self.config}")

        self._layout = {
            "width": 250,
            "height": 122,
        }

        # Initialize layout
        self.layout()

    @property
    def width(self):
        """Get display width from layout"""
        return self._layout.get("width", 250)

    @property
    def height(self):
        """Get display height from layout"""
        return self._layout.get("height", 122)

    def layout(self):
        """Setup display layout - override in subclass"""
        raise NotImplementedError

    def initialize(self):
        """Initialize display hardware - override in subclass"""
        raise NotImplementedError

    def render(self, canvas):
        """Render image to display - override in subclass"""
        raise NotImplementedError

    def clear(self):
        """Clear the display - override in subclass"""
        raise NotImplementedError

    def sleep(self):
        """Put display to sleep - override in subclass"""
        pass

    def display_partial(self, image_buffer):
        """Compatibility method - calls render with the image"""
        if hasattr(image_buffer, "mode"):
            # It's a PIL Image
            self.render(image_buffer)
        else:
            self.render(image_buffer)
