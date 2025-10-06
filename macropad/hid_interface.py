"""HID communication interface for MacroPad devices."""

import hid
from typing import Optional, List
import logging

logger = logging.getLogger(__name__)


class DeviceConfig:
    """Configuration for a specific MacroPad device."""

    def __init__(self, vendor_id: int, product_id: int, path_fragment: str, protocol_version: int):
        self.vendor_id = vendor_id
        self.product_id = product_id
        self.path_fragment = path_fragment
        self.protocol_version = protocol_version


# Default configurations for known devices
KNOWN_DEVICES = [
    DeviceConfig(0x1189, 0x8860, "MI_01", 1),  # 4489:34880
    DeviceConfig(0x1189, 0x8890, "MI_01", 0),  # 4489:34960 - 3 buttons 1 knob
    DeviceConfig(0x1189, 0x8830, "MI_00", 1),  # 4489:34864
]


class HidInterface:
    """Handles HID communication with MacroPad devices."""

    def __init__(self):
        self.device: Optional[hid.device] = None
        self.config: Optional[DeviceConfig] = None
        self.output_report_length = 65  # Standard HID report size

    def find_device(self, vendor_id: Optional[int] = None, product_id: Optional[int] = None) -> bool:
        """
        Find and connect to a MacroPad device.

        Args:
            vendor_id: Specific vendor ID to search for (optional)
            product_id: Specific product ID to search for (optional)

        Returns:
            True if device found and opened successfully
        """
        devices_to_search = KNOWN_DEVICES

        if vendor_id and product_id:
            # Search for specific device
            devices_to_search = [d for d in KNOWN_DEVICES
                               if d.vendor_id == vendor_id and d.product_id == product_id]
            if not devices_to_search:
                # Create config for unknown device, assume protocol 0
                devices_to_search = [DeviceConfig(vendor_id, product_id, b"mi_", 0)]

        for config in devices_to_search:
            logger.debug(f"Searching for device {config.vendor_id:04X}:{config.product_id:04X}")

            # Enumerate all HID devices
            for device_info in hid.enumerate(config.vendor_id, config.product_id):
                path = device_info['path']

                # Check if path contains the required fragment
                # Convert both to strings for comparison (case-insensitive)
                try:
                    if isinstance(path, bytes):
                        path_str = path.decode('utf-8', errors='ignore')
                    else:
                        path_str = str(path)

                    if isinstance(config.path_fragment, bytes):
                        fragment_str = config.path_fragment.decode('utf-8', errors='ignore')
                    else:
                        fragment_str = str(config.path_fragment)

                    # Case-insensitive search for Windows/Linux compatibility
                    if fragment_str.upper() not in path_str.upper():
                        continue
                except Exception as e:
                    logger.debug(f"Path check failed: {e}")
                    continue

                try:
                    self.device = hid.device()
                    self.device.open_path(path)
                    self.config = config

                    manufacturer = self.device.get_manufacturer_string()
                    product = self.device.get_product_string()
                    logger.info(f"Connected to: {manufacturer} {product}")
                    logger.info(f"VID:PID = {config.vendor_id:04X}:{config.product_id:04X}")
                    logger.info(f"Protocol version: {config.protocol_version}")

                    return True
                except Exception as e:
                    logger.error(f"Failed to open device: {e}")
                    continue

        logger.error("No compatible MacroPad device found")
        return False

    def close(self):
        """Close the HID device connection."""
        if self.device:
            self.device.close()
            self.device = None
            self.config = None
            logger.info("Device closed")

    def write_report(self, report_id: int, data: bytes) -> bool:
        """
        Write a HID report to the device.

        Args:
            report_id: HID report ID
            data: Report data (should be 64 bytes)

        Returns:
            True if write successful
        """
        if not self.device:
            logger.error("Device not opened")
            return False

        # Prepare buffer: [report_id][data]
        buffer = bytearray(self.output_report_length)
        buffer[0] = report_id

        # Copy data (max 64 bytes)
        data_len = min(len(data), 64)
        buffer[1:data_len+1] = data[:data_len]

        try:
            bytes_written = self.device.write(bytes(buffer))
            logger.debug(f"Wrote {bytes_written} bytes to device")
            # On Windows, write() returns -1 on success for some devices
            # On Linux, it returns the number of bytes written
            # Consider both as success if no exception was raised
            return True
        except Exception as e:
            logger.error(f"Failed to write to device: {e}")
            return False

    def get_protocol_version(self) -> int:
        """Get the protocol version of the connected device."""
        return self.config.protocol_version if self.config else 0

    def is_open(self) -> bool:
        """Check if device is open."""
        return self.device is not None

    @staticmethod
    def list_devices() -> List[dict]:
        """List all potential MacroPad devices."""
        found_devices = []

        for config in KNOWN_DEVICES:
            for device_info in hid.enumerate(config.vendor_id, config.product_id):
                path = device_info['path']

                # Check path fragment (cross-platform, case-insensitive)
                try:
                    if isinstance(path, bytes):
                        path_str = path.decode('utf-8', errors='ignore')
                    else:
                        path_str = str(path)

                    if isinstance(config.path_fragment, bytes):
                        fragment_str = config.path_fragment.decode('utf-8', errors='ignore')
                    else:
                        fragment_str = str(config.path_fragment)

                    if fragment_str.upper() not in path_str.upper():
                        continue
                except:
                    continue

                found_devices.append({
                    'vendor_id': device_info['vendor_id'],
                    'product_id': device_info['product_id'],
                    'manufacturer': device_info['manufacturer_string'],
                    'product': device_info['product_string'],
                    'path': device_info['path'],
                    'protocol': config.protocol_version
                })

        return found_devices
