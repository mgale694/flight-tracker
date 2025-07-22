#!/usr/bin/env python3
"""
Test script to verify display imports work correctly
"""

import sys
import os

# Add the src directory to Python path
src_path = os.path.join(os.path.dirname(__file__), 'src')
sys.path.insert(0, src_path)

try:
    print("Testing display import...")
    from raspi.ui.hw import display_for, RASPI_AVAILABLE
    
    print(f"RASPI_AVAILABLE: {RASPI_AVAILABLE}")
    
    # Test config
    test_config = {
        "display": {
            "type": "waveshare213inb_v4",
            "enabled": True,
            "rotation": 180
        },
        "development": {
            "enabled": False
        }
    }
    
    print("\nTesting display_for with waveshare213inb_v4...")
    display = display_for(test_config)
    print(f"Display implementation: {display.__class__.__name__}")
    print(f"Display name: {getattr(display, 'name', 'unknown')}")
    
    print("\nSuccess! Display imports work correctly.")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
