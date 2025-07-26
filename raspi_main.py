#!/usr/bin/env python3
# -*- coding:utf-8 -*-
"""
Flight Tracker - Production Entry Point
Following pwnagotchi architecture patterns
"""

import sys
import os

print("Flight Tracker - Production Mode")
print("=" * 40)

# Add the raspi module to path
current_dir = os.path.dirname(os.path.abspath(__file__))
raspi_dir = os.path.join(current_dir, "raspi")

if not os.path.exists(raspi_dir):
    print(f"ERROR: Cannot find raspi module at {raspi_dir}")
    print("Please ensure you're running from the src directory")
    sys.exit(1)

sys.path.insert(0, raspi_dir)

try:
    from raspi.agent import main

    print("✓ Flight tracker modules loaded")
    print("Starting flight tracking...")
    main()
except ImportError as e:
    print(f"ERROR: Cannot import flight tracker modules: {e}")
    print("\nTroubleshooting:")
    print("1. Check if all Python dependencies are installed:")
    print("   pip install toml Pillow requests pandas")
    print("2. Ensure config.toml exists in the raspi directory")
    print("3. Check the debug script output for more details")
    sys.exit(1)
except Exception as e:
    print(f"ERROR: Flight tracker failed to start: {e}")
    sys.exit(1)
