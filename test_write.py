#!/usr/bin/env python3
"""Test script to debug HID write issues."""

import hid
import logging

logging.basicConfig(level=logging.DEBUG, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

# Find the MacroPad device
VID = 0x1189
PID = 0x8890

print("=== Searching for MacroPad device ===\n")

devices = list(hid.enumerate(VID, PID))
if not devices:
    print(f"No device found with VID:PID = {VID:04X}:{PID:04X}")
    exit(1)

print(f"Found {len(devices)} interface(s):\n")

for i, dev_info in enumerate(devices):
    path = dev_info['path']
    path_str = path.decode('utf-8', errors='ignore') if isinstance(path, bytes) else str(path)
    print(f"{i+1}. Interface {dev_info['interface_number']}")
    print(f"   Path: {path_str}")
    print()

# Try to find MI_01 interface
target_device = None
for dev_info in devices:
    path = dev_info['path']
    path_str = path.decode('utf-8', errors='ignore') if isinstance(path, bytes) else str(path)

    if 'MI_01' in path_str.upper():
        target_device = dev_info
        print(f"✓ Selected MI_01 interface")
        print(f"  Path: {path_str}\n")
        break

if not target_device:
    print("⚠ MI_01 interface not found, using first device")
    target_device = devices[0]

# Try to open and write
print("=== Attempting to open device ===\n")

try:
    device = hid.device()
    device.open_path(target_device['path'])
    print("✓ Device opened successfully")

    # Get device info
    try:
        manufacturer = device.get_manufacturer_string()
        product = device.get_product_string()
        print(f"  Manufacturer: {manufacturer}")
        print(f"  Product: {product}")
    except:
        print("  (Could not read device strings)")

    print()

    # Try a simple write test
    print("=== Testing write operation ===\n")

    # Create a test report (LED off command)
    report_id = 0
    test_data = bytearray(64)
    test_data[0] = 0xB0  # LED command
    test_data[1] = 0x00  # OFF mode

    buffer = bytearray(65)
    buffer[0] = report_id
    buffer[1:65] = test_data

    print(f"Report ID: {report_id}")
    print(f"Data (first 10 bytes): {' '.join(f'{b:02X}' for b in test_data[:10])}")
    print()

    try:
        bytes_written = device.write(bytes(buffer))
        print(f"✓ Write successful: {bytes_written} bytes written")
    except Exception as e:
        print(f"✗ Write failed: {e}")
        print(f"  Error type: {type(e).__name__}")

        # Try without report ID
        print("\n=== Trying write without report ID ===\n")
        try:
            bytes_written = device.write(bytes(test_data))
            print(f"✓ Write successful (no report ID): {bytes_written} bytes written")
        except Exception as e2:
            print(f"✗ Write failed again: {e2}")

    device.close()
    print("\n✓ Device closed")

except Exception as e:
    print(f"✗ Failed to open device: {e}")
    print(f"  Error type: {type(e).__name__}")
    import traceback
    traceback.print_exc()
