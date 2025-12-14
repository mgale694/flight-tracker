#!/usr/bin/env python3
"""Test script to diagnose FlightRadar24 API issues"""

from FlightRadar24 import FlightRadar24API

print("Testing FlightRadar24 API...")
print("-" * 50)

fr_api = FlightRadar24API()

# Test 1: Get flights in San Francisco area
print("\n1. Testing San Francisco area (37.7749, -122.4194)...")
try:
    bounds = fr_api.get_bounds({
        'tl_y': 37.8,  # Top latitude
        'tl_x': -122.5,  # Left longitude
        'br_y': 37.7,  # Bottom latitude
        'br_x': -122.3  # Right longitude
    })
    
    print(f"   Type returned: {type(bounds).__name__}")
    
    if isinstance(bounds, dict):
        print(f"   Number of flights: {len(bounds)}")
        if len(bounds) > 0:
            # Show first flight
            first_id = list(bounds.keys())[0]
            first_flight = bounds[first_id]
            print(f"   Sample flight: {first_id}")
            print(f"   Data: {first_flight[:5] if len(first_flight) > 5 else first_flight}")
        else:
            print("   ⚠️  Empty dictionary returned")
    else:
        print(f"   ⚠️  Non-dict returned: {bounds}")
        
except Exception as e:
    print(f"   ❌ Error: {e}")

# Test 2: Get flights worldwide (smaller area)
print("\n2. Testing London area (51.5074, -0.1278)...")
try:
    bounds = fr_api.get_bounds({
        'tl_y': 51.6,
        'tl_x': -0.2,
        'br_y': 51.4,
        'br_x': 0.0
    })
    
    print(f"   Type returned: {type(bounds).__name__}")
    
    if isinstance(bounds, dict):
        print(f"   Number of flights: {len(bounds)}")
    else:
        print(f"   ⚠️  Non-dict returned: {bounds}")
        
except Exception as e:
    print(f"   ❌ Error: {e}")

# Test 3: Get specific zone
print("\n3. Testing get_zones()...")
try:
    zones = fr_api.get_zones()
    print(f"   Zones available: {type(zones).__name__}")
    if isinstance(zones, dict):
        print(f"   Number of zones: {len(zones)}")
except Exception as e:
    print(f"   ❌ Error: {e}")

print("\n" + "-" * 50)
print("Test complete!")
print("\nIf all tests return empty dicts or errors, the FlightRadar24 API")
print("may be rate-limiting or the library needs updating.")
