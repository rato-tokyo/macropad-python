#!/usr/bin/env python3
"""Debug script to list all HID devices and help identify MacroPad."""

import hid

print("=== All HID Devices ===\n")

for device in hid.enumerate():
    print(f"VID:PID = {device['vendor_id']:04X}:{device['product_id']:04X}")
    print(f"  Manufacturer: {device['manufacturer_string']}")
    print(f"  Product: {device['product_string']}")
    print(f"  Path: {device['path']}")
    print(f"  Serial: {device['serial_number']}")
    print(f"  Interface: {device['interface_number']}")
    print()

print("\n=== Looking for potential MacroPad devices ===\n")

# Known VID:PID combinations
known_devices = [
    (0x1189, 0x8860, "4489:34880"),
    (0x1189, 0x8890, "4489:34960 - 3 buttons 1 knob"),
    (0x1189, 0x8830, "4489:34864"),
]

for vid, pid, desc in known_devices:
    devices = list(hid.enumerate(vid, pid))
    if devices:
        print(f"✓ Found {desc}:")
        for dev in devices:
            print(f"  Path: {dev['path']}")
            print(f"  Product: {dev['product_string']}")
    else:
        print(f"✗ Not found: {desc}")
    print()

print("\n=== Checking for vendor 0x1189 (4489) ===\n")
vendor_devices = [d for d in hid.enumerate() if d['vendor_id'] == 0x1189]
if vendor_devices:
    print(f"Found {len(vendor_devices)} device(s) from vendor 0x1189:")
    for dev in vendor_devices:
        print(f"  VID:PID = {dev['vendor_id']:04X}:{dev['product_id']:04X}")
        print(f"  Product: {dev['product_string']}")
        print(f"  Path: {dev['path']}")
        print()
else:
    print("No devices from vendor 0x1189 found")
