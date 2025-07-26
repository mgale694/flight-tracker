import raspi.ui.fonts as fonts


class DisplayImpl(object):
    def __init__(self, config, name):
        self.name = name
        print(f"🔧 DisplayImpl.__init__: name={name}")
        print(f"🔧 DisplayImpl.__init__: config keys = {list(config.keys())}")

        # Handle both old and new config structures
        if "ui" in config and "display" in config["ui"]:
            self.config = config["ui"]["display"]
            print("🔧 Using ui.display config structure")
        elif "display" in config:
            self.config = config["display"]
            print("🔧 Using display config structure")
        else:
            print("❌ No display config found!")
            raise KeyError("No display configuration found in config")

        print(f"🔧 Display config: {self.config}")

        self._layout = {
            "width": 0,
            "height": 0,
            "face": (0, 0),
            "name": (0, 0),
            "channel": (0, 0),
            "aps": (0, 0),
            "uptime": (0, 0),
            "line1": (0, 0),
            "line2": (0, 0),
            "friend_face": (0, 0),
            "friend_name": (0, 0),
            "shakes": (0, 0),
            "mode": (0, 0),
            # status is special :D
            "status": {
                "pos": (0, 0),
                "font": fonts.status_font(fonts.Medium),
                "max": 20,
            },
        }

        # Initialize layout to get dimensions
        self.layout()

    @property
    def width(self):
        """Get display width from layout"""
        return self._layout.get("width", 250)  # Default to 250 if not set

    @property
    def height(self):
        """Get display height from layout"""
        return self._layout.get("height", 122)  # Default to 122 if not set

    def layout(self):
        raise NotImplementedError

    def initialize(self):
        raise NotImplementedError

    def render(self, canvas):
        raise NotImplementedError

    def clear(self):
        raise NotImplementedError

    def display_partial(self, image_buffer):
        """Compatibility method - calls render with the image as black canvas"""
        if hasattr(image_buffer, "mode"):
            # It's a PIL Image
            self.render(canvasBlack=image_buffer)
        else:
            # Assume it's already processed
            self.render(canvasBlack=image_buffer)
