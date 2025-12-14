#!/usr/bin/env python3
"""
Simple test script to verify Waveshare display hardware works
Run this to test display without starting the full flight tracker
"""

import sys
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def test_imports():
    """Test that all required modules can be imported"""
    print("\n🔍 Testing Python Module Imports...")
    print("=" * 50)
    
    modules = {
        'spidev': 'SPI communication',
        'gpiozero': 'GPIO control',
        'RPi.GPIO': 'Alternative GPIO',
        'PIL': 'Image processing (Pillow)',
    }
    
    all_ok = True
    for module, description in modules.items():
        try:
            __import__(module)
            print(f"✅ {module:12} - {description}")
        except ImportError as e:
            print(f"❌ {module:12} - {description} - ERROR: {e}")
            all_ok = False
    
    return all_ok

def test_waveshare_library():
    """Test that Waveshare library files exist and can be imported"""
    print("\n🔍 Testing Waveshare Library Files...")
    print("=" * 50)
    
    # Add parent directory to path
    script_dir = Path(__file__).parent.absolute()
    sys.path.insert(0, str(script_dir))
    
    try:
        from ui.hw.libs.waveshare import epd2in13_V4
        print("✅ Waveshare library files found and importable")
        print(f"   Location: {epd2in13_V4.__file__}")
        return True
    except ImportError as e:
        print(f"❌ Cannot import Waveshare library: {e}")
        return False

def test_display_init():
    """Test actual display initialization"""
    print("\n🔍 Testing Display Initialization...")
    print("=" * 50)
    
    script_dir = Path(__file__).parent.absolute()
    sys.path.insert(0, str(script_dir))
    
    try:
        from ui.hw.libs.waveshare.epd2in13_V4 import EPD
        
        print("Creating EPD object...")
        epd = EPD()
        
        print("Initializing display...")
        epd.init()
        
        print("✅ Display initialized successfully!")
        
        print("Clearing display...")
        epd.Clear()
        
        print("✅ Display cleared successfully!")
        
        return epd
        
    except Exception as e:
        print(f"❌ Display initialization failed: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_display_render():
    """Test rendering an image to the display"""
    print("\n🔍 Testing Display Render...")
    print("=" * 50)
    
    try:
        from PIL import Image, ImageDraw, ImageFont
        
        # Create a simple test image
        print("Creating test image (250x122)...")
        image = Image.new('1', (250, 122), 255)  # 1-bit white background
        draw = ImageDraw.Draw(image)
        
        # Draw test pattern
        draw.rectangle([0, 0, 249, 121], outline=0)  # Border
        draw.text((10, 10), "Flight Tracker", fill=0)
        draw.text((10, 30), "Display Test", fill=0)
        draw.text((10, 50), "E-ink Working!", fill=0)
        draw.line([0, 60, 250, 60], fill=0)  # Horizontal line
        draw.text((10, 70), "Raspberry Pi", fill=0)
        draw.text((10, 90), "2.13in V4", fill=0)
        
        print("✅ Test image created")
        
        # Initialize display
        epd = test_display_init()
        if epd is None:
            return False
        
        # Render to display
        print("\nRendering to display...")
        buf = epd.getbuffer(image)
        epd.display(buf)
        
        print("✅ Image rendered to display successfully!")
        print("\n🎉 Check your e-ink display - you should see the test pattern!")
        
        # Keep display on for a bit
        print("\nDisplay will remain on. Press Ctrl+C to clear and exit...")
        import time
        time.sleep(5)
        
        # Clear on exit
        print("\nClearing display...")
        epd.Clear()
        print("✅ Display cleared")
        
        return True
        
    except KeyboardInterrupt:
        print("\n\n🛑 Test interrupted by user")
        try:
            epd.Clear()
            print("✅ Display cleared")
        except:
            pass
        return True
        
    except Exception as e:
        print(f"❌ Render test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print("\n" + "=" * 50)
    print("  Waveshare Display Hardware Test")
    print("=" * 50)
    
    # Test 1: Module imports
    imports_ok = test_imports()
    
    if not imports_ok:
        print("\n❌ FAILED: Missing required Python modules")
        print("\nFix with:")
        print("  pip3 install spidev gpiozero RPi.GPIO Pillow")
        print("  or")
        print("  sudo apt-get install python3-spidev python3-gpiozero python3-rpi.gpio python3-pil")
        return False
    
    # Test 2: Waveshare library
    library_ok = test_waveshare_library()
    
    if not library_ok:
        print("\n❌ FAILED: Waveshare library not found")
        print("\nFix with:")
        print("  ./scripts/install-waveshare.sh")
        return False
    
    # Test 3: Display initialization and render
    render_ok = test_display_render()
    
    if render_ok:
        print("\n" + "=" * 50)
        print("✅ ALL TESTS PASSED!")
        print("=" * 50)
        print("\nYour display hardware is working correctly.")
        print("The flight tracker should now work with the display.")
        return True
    else:
        print("\n" + "=" * 50)
        print("❌ DISPLAY TEST FAILED")
        print("=" * 50)
        print("\nPossible issues:")
        print("  1. SPI not enabled: sudo raspi-config → Interface Options → SPI")
        print("  2. Permission issue: Try with sudo")
        print("  3. Display not connected correctly")
        print("  4. Wrong display type (this is for 2.13in V4)")
        return False

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n🛑 Test interrupted by user")
        sys.exit(0)
