import logging

# Import local hardware display implementations
try:
    from .waveshare213in_v4 import Waveshare213V4

    RASPI_AVAILABLE = True
    logging.info("Local hardware display modules loaded successfully")
except ImportError as e:
    logging.error(f"Failed to import local display modules: {e}")
    RASPI_AVAILABLE = False


def display_for(config):
    """Get the appropriate display implementation"""
    print("🔍 Selecting display implementation...")

    # Check if we're in development mode
    dev_enabled = config.get("development", {}).get("enabled", False)
    print(f"   - Development mode: {dev_enabled}")

    if dev_enabled:
        print("✓ Using DevelopmentDisplay (PyQt GUI)")
        return DevelopmentDisplay(config)

    # Get display type from config (handle both nested and flat structure)
    display_config = config.get("ui", {}).get("display", config.get("display", {}))
    display_type = display_config.get("type", "mock")
    print(f"   - Requested display type: {display_type}")
    print(f"   - RASPI_AVAILABLE: {RASPI_AVAILABLE}")

    # Handle hardware displays if available
    if RASPI_AVAILABLE:
        print("🔧 Checking local hardware display implementations...")
        if display_type in ["waveshare213in_v4", "waveshare2in13v4"]:
            print("✓ Using Waveshare213V4 display (waveshare213in_v4/waveshare2in13v4)")
            return Waveshare213V4(config)
        else:
            print(f"❌ Unknown display type '{display_type}', falling back to mock")

    # Fallback to mock display
    print("⚠️  Using MockDisplay (no hardware output)")
    return MockDisplay()


class DisplayBase:
    """Base class for all display implementations"""

    def __init__(self):
        self.name = "base"
        self.width = 250
        self.height = 122

    def init(self):
        pass

    def clear(self):
        pass

    def display_partial(self, image):
        pass

    def sleep(self):
        pass


class MockDisplay(DisplayBase):
    """Mock display for testing without hardware"""

    def __init__(self):
        super().__init__()
        self.name = "mock"
        logging.info("Using mock display - no hardware output")

    def initialize(self):
        """Mock initialize - no hardware to set up"""
        pass

    def render(self, canvas):
        """Mock render - log that an update would happen"""
        logging.info("Mock display: image updated")

    def display_partial(self, image_buffer):
        logging.info("Mock display: image updated")


class DevelopmentDisplay(DisplayBase):
    """Development display for laptop testing with PyQt GUI preview"""

    def __init__(self, config):
        super().__init__()
        self.name = "development"
        self.config = config
        self.app = None
        self.window = None
        self.image_label = None
        self.status_label = None

        self._init_gui()
        logging.info("Using development display mode: PyQt GUI")

    def _init_gui(self):
        """Initialize PyQt GUI window for visual preview"""
        try:
            # Try PyQt6 first, then PyQt5
            try:
                from PyQt6.QtWidgets import (
                    QApplication,
                    QWidget,
                    QVBoxLayout,
                    QHBoxLayout,
                    QLabel,
                    QPushButton,
                )
                from PyQt6.QtCore import Qt
                from PyQt6.QtGui import QFont

                self.qt_version = 6
            except ImportError:
                try:
                    from PyQt5.QtWidgets import (
                        QApplication,
                        QWidget,
                        QVBoxLayout,
                        QHBoxLayout,
                        QLabel,
                        QPushButton,
                    )
                    from PyQt5.QtCore import Qt
                    from PyQt5.QtGui import QFont

                    self.qt_version = 5
                except ImportError:
                    raise ImportError(
                        "Neither PyQt6 nor PyQt5 found. Please install with: pip install PyQt6 or pip install PyQt5"
                    )

            # Create application if it doesn't exist
            if not QApplication.instance():
                self.app = QApplication([])
            else:
                self.app = QApplication.instance()

            # Create main window
            self.window = QWidget()
            self.window.setWindowTitle("Flight Tracker Display Preview")
            self.window.setFixedSize(600, 500)
            self.window.setStyleSheet("""
                QWidget {
                    background-color: #2b2b2b;
                    color: white;
                }
                QLabel {
                    color: white;
                }
            """)

            # Create layout
            layout = QVBoxLayout()
            layout.setSpacing(20)

            # Title
            title_label = QLabel("Flight Tracker - Development Preview")
            title_font = QFont(
                "Arial", 16, QFont.Weight.Bold if self.qt_version == 6 else QFont.Bold
            )
            title_label.setFont(title_font)
            title_label.setAlignment(
                Qt.AlignmentFlag.AlignCenter if self.qt_version == 6 else Qt.AlignCenter
            )
            layout.addWidget(title_label)

            # Display preview area with e-paper styling
            self.image_label = QLabel()
            self.image_label.setFixedSize(500, 244)
            self.image_label.setStyleSheet("""
                QLabel {
                    background-color: #f5f5f5;
                    border: 3px solid #333;
                    border-radius: 5px;
                    color: #666;
                    font-family: monospace;
                    font-size: 12px;
                }
            """)
            self.image_label.setAlignment(
                Qt.AlignmentFlag.AlignCenter if self.qt_version == 6 else Qt.AlignCenter
            )
            self.image_label.setText(
                "E-Paper Display Preview\n250×122 pixels\n\nWaiting for content..."
            )

            # Center the image label
            image_layout = QHBoxLayout()
            image_layout.addStretch()
            image_layout.addWidget(self.image_label)
            image_layout.addStretch()
            layout.addLayout(image_layout)

            # Status label
            self.status_label = QLabel("Status: Waiting for display data...")
            self.status_label.setStyleSheet("color: #4CAF50;")
            self.status_label.setAlignment(
                Qt.AlignmentFlag.AlignCenter if self.qt_version == 6 else Qt.AlignCenter
            )
            layout.addWidget(self.status_label)

            # Info label
            info_label = QLabel(
                "This window shows what would appear on the e-paper display\nClose the window or press Ctrl+C to stop"
            )
            info_label.setStyleSheet("color: #999;")
            info_label.setAlignment(
                Qt.AlignmentFlag.AlignCenter if self.qt_version == 6 else Qt.AlignCenter
            )
            layout.addWidget(info_label)

            # Close button
            close_button = QPushButton("Close")
            close_button.clicked.connect(self._on_window_close)
            close_button.setStyleSheet("""
                QPushButton {
                    background-color: #f44336;
                    color: white;
                    border: none;
                    padding: 10px;
                    font-size: 12px;
                }
                QPushButton:hover {
                    background-color: #d32f2f;
                }
            """)
            layout.addWidget(close_button)

            self.window.setLayout(layout)
            self.window.show()

            logging.info("PyQt development GUI window initialized")

        except ImportError as e:
            logging.error(f"PyQt not available: {e}")
            logging.info("Install PyQt with: pip install PyQt6 or pip install PyQt5")
            raise

    def _on_window_close(self):
        """Handle window close event"""
        logging.info("GUI window closed by user")
        if self.window:
            self.window.close()
        if self.app:
            self.app.quit()

    def display_partial(self, image_buffer):
        """Display image in PyQt window"""
        if not self.window or not self.image_label:
            return

        try:
            # Check if it's a PIL Image
            if hasattr(image_buffer, "size"):
                from PIL import Image

                # Try PyQt6 first, then PyQt5
                try:
                    from PyQt6.QtGui import QPixmap
                    from PyQt6.QtCore import QBuffer, QIODevice
                except ImportError:
                    from PyQt5.QtGui import QPixmap
                    from PyQt5.QtCore import QBuffer, QIODevice

                # Convert to RGB for better display
                if image_buffer.mode != "RGB":
                    display_img = image_buffer.convert("RGB")
                else:
                    display_img = image_buffer

                # Resize for better viewing (2x scale)
                display_img = display_img.resize((500, 244), Image.Resampling.NEAREST)

                # Convert PIL image to QPixmap
                buffer = QBuffer()
                if self.qt_version == 6:
                    buffer.open(QIODevice.OpenModeFlag.WriteOnly)
                else:
                    buffer.open(QIODevice.WriteOnly)

                display_img.save(buffer, format="PNG")
                pixmap = QPixmap()
                pixmap.loadFromData(buffer.data(), "PNG")

                # Update the image label
                self.image_label.setPixmap(pixmap)
                self.status_label.setText("Status: Display Updated ✓")
                self.status_label.setStyleSheet("color: #4CAF50;")

            else:
                self.status_label.setText("Status: Content Updated")
                self.status_label.setStyleSheet("color: #2196F3;")

            # Process events to update GUI
            if self.app:
                self.app.processEvents()

        except Exception as e:
            logging.error(f"PyQt display error: {e}")
            if self.status_label:
                self.status_label.setText(f"Status: Error - {e}")
                self.status_label.setStyleSheet("color: #f44336;")

    def clear(self):
        """Clear the display"""
        try:
            if self.image_label:
                self.image_label.clear()
                self.image_label.setText(
                    "E-Paper Display Preview\n250×122 pixels\n\nDisplay cleared"
                )
                self.status_label.setText("Status: Display Cleared")
                self.status_label.setStyleSheet("color: #FF9800;")

            if self.app:
                self.app.processEvents()

        except Exception as e:
            logging.error(f"Error clearing display: {e}")

    def sleep(self):
        """Close the PyQt window"""
        try:
            if self.window:
                self.window.close()
            if self.app:
                self.app.quit()
        except Exception as e:
            logging.error(f"Error closing PyQt GUI: {e}")
