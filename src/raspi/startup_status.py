#!/usr/bin/env python3
"""Display startup status messages on e-ink display"""
import sys
import time
from pathlib import Path
from PIL import Image, ImageDraw

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent))

from ui.hw import display_for
from ui import fonts
import toml


def load_config():
    """Load configuration"""
    config_path = Path(__file__).parent / "config.toml"
    if not config_path.exists():
        print(f"Config not found: {config_path}")
        return None
    
    with open(config_path) as f:
        return toml.load(f)


def show_status(message, step=None, total=None):
    """Show a status message on the display
    
    Args:
        message: Status message to display
        step: Current step number (optional)
        total: Total number of steps (optional)
    """
    try:
        # Load config
        config = load_config()
        if not config:
            print(f"[NO DISPLAY] {message}")
            return
        
        # Check if display is enabled
        display_config = config.get("ui", {}).get("display", {})
        if not display_config.get("enabled", True):
            print(f"[DISPLAY DISABLED] {message}")
            return
        
        # Initialize display
        fonts.init(config)
        display = display_for(config)
        display.initialize()
        
        # Create image
        width = display.width
        height = display.height
        image = Image.new("1", (width, height), 255)  # White background
        draw = ImageDraw.Draw(image)
        
        # Draw header
        header = "Flight Tracker Setup"
        draw.text((5, 2), header, font=fonts.Small, fill=0)
        draw.line((0, 15, width, 15), fill=0, width=2)
        
        # Draw progress if provided
        if step is not None and total is not None:
            progress_text = f"Step {step}/{total}"
            draw.text((width - 70, 2), progress_text, font=fonts.Small, fill=0)
            
            # Draw progress bar
            bar_width = width - 20
            bar_height = 8
            bar_x = 10
            bar_y = 22
            
            # Background bar
            draw.rectangle(
                [bar_x, bar_y, bar_x + bar_width, bar_y + bar_height],
                outline=0,
                fill=255
            )
            
            # Fill progress
            progress = (step / total) * bar_width
            draw.rectangle(
                [bar_x, bar_y, bar_x + int(progress), bar_y + bar_height],
                outline=0,
                fill=0
            )
        
        # Draw status message (wrap if needed)
        y_pos = 40 if (step and total) else 25
        
        # Split message into lines if too long
        max_chars = 28
        words = message.split()
        lines = []
        current_line = ""
        
        for word in words:
            test_line = current_line + (" " if current_line else "") + word
            if len(test_line) <= max_chars:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word
        
        if current_line:
            lines.append(current_line)
        
        # Draw lines
        for i, line in enumerate(lines[:4]):  # Max 4 lines
            draw.text((5, y_pos + (i * 16)), line, font=fonts.Medium, fill=0)
        
        # Draw timestamp
        timestamp = time.strftime("%H:%M:%S")
        draw.line((0, height - 15, width, height - 15), fill=0, width=1)
        draw.text((width - 70, height - 12), timestamp, font=fonts.Small, fill=0)
        
        # Rotate and display
        rotated = image.rotate(180)
        display.render(rotated)
        
        print(f"✅ Display updated: {message}")
        
    except Exception as e:
        print(f"⚠️  Display error: {e}")
        print(f"   Message was: {message}")


if __name__ == "__main__":
    # Parse command line arguments
    if len(sys.argv) < 2:
        print("Usage: startup_status.py <message> [step] [total]")
        sys.exit(1)
    
    message = sys.argv[1]
    step = int(sys.argv[2]) if len(sys.argv) > 2 else None
    total = int(sys.argv[3]) if len(sys.argv) > 3 else None
    
    show_status(message, step, total)
