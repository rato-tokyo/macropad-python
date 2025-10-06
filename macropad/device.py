"""High-level MacroPad device interface."""

from typing import List, Optional
from .hid_interface import HidInterface
from .protocol import LegacyProtocol, Report
from .models import (
    InputAction, KeyCode, Modifier, MediaKey, MouseButton,
    LedMode, KeySequence
)
import logging

logger = logging.getLogger(__name__)


class MacroPadDevice:
    """High-level interface for MacroPad device configuration."""

    def __init__(self):
        self.hid = HidInterface()
        self.protocol: Optional[LegacyProtocol] = None

    def connect(self, vendor_id: Optional[int] = None, product_id: Optional[int] = None) -> bool:
        """
        Connect to a MacroPad device.

        Args:
            vendor_id: Specific vendor ID (optional)
            product_id: Specific product ID (optional)

        Returns:
            True if connected successfully
        """
        if self.hid.find_device(vendor_id, product_id):
            protocol_version = self.hid.get_protocol_version()

            if protocol_version == 0:
                self.protocol = LegacyProtocol(report_id=0)
                logger.info("Using Legacy Protocol (version 0)")
            elif protocol_version == 1:
                logger.error("Extended protocol not yet implemented")
                self.disconnect()
                return False
            else:
                logger.error(f"Unknown protocol version: {protocol_version}")
                self.disconnect()
                return False

            return True

        return False

    def disconnect(self):
        """Disconnect from device."""
        self.hid.close()
        self.protocol = None

    def _send_reports(self, reports: List[Report]) -> bool:
        """Send a list of reports to the device."""
        if not self.hid.is_open():
            logger.error("Device not connected")
            return False

        for report in reports:
            logger.debug(f"Sending: {report}")
            if not self.hid.write_report(report.report_id, bytes(report.data)):
                logger.error("Failed to send report")
                return False

        return True

    def set_key_sequence(
        self,
        action: InputAction,
        sequence: List[KeySequence],
        layer: int = 0
    ) -> bool:
        """
        Configure a button/knob to send a keyboard sequence.

        Args:
            action: Which button/knob action to configure
            sequence: List of KeySequence tuples
            layer: Layer number (default 0)

        Returns:
            True if successful
        """
        if not isinstance(self.protocol, LegacyProtocol):
            logger.error("Protocol not initialized")
            return False

        if len(sequence) > 5:
            logger.warning("3-button 1-knob device only supports up to 5 keys")
            sequence = sequence[:5]

        reports = self.protocol.create_key_reports(action, layer, sequence)
        success = self._send_reports(reports)

        if success:
            logger.info(f"Configured {action.name} with key sequence: {sequence}")

        return success

    def set_media_key(
        self,
        action: InputAction,
        media_key: MediaKey,
        layer: int = 0
    ) -> bool:
        """
        Configure a button/knob to send a media key.

        Args:
            action: Which button/knob action to configure
            media_key: Media key to assign
            layer: Layer number (default 0)

        Returns:
            True if successful
        """
        if not isinstance(self.protocol, LegacyProtocol):
            logger.error("Protocol not initialized")
            return False

        reports = self.protocol.create_media_reports(action, layer, media_key)
        success = self._send_reports(reports)

        if success:
            logger.info(f"Configured {action.name} with media key: {media_key.name}")

        return success

    def set_mouse_button(
        self,
        action: InputAction,
        button: MouseButton,
        modifiers: Modifier = Modifier.NONE,
        layer: int = 0
    ) -> bool:
        """
        Configure a button/knob to send a mouse button or scroll.

        Args:
            action: Which button/knob action to configure
            button: Mouse button or scroll direction
            modifiers: Modifier keys (only left-side supported on 3-button 1-knob)
            layer: Layer number (default 0)

        Returns:
            True if successful
        """
        if not isinstance(self.protocol, LegacyProtocol):
            logger.error("Protocol not initialized")
            return False

        reports = self.protocol.create_mouse_reports(action, layer, button, modifiers)
        success = self._send_reports(reports)

        if success:
            logger.info(f"Configured {action.name} with mouse: {button.name}")

        return success

    def set_led_mode(self, mode: LedMode, layer: int = 0) -> bool:
        """
        Set LED mode.

        Args:
            mode: LED mode (OFF, ON, BREATHE)
            layer: Layer number (default 0)

        Returns:
            True if successful
        """
        if not isinstance(self.protocol, LegacyProtocol):
            logger.error("Protocol not initialized")
            return False

        reports = self.protocol.create_led_reports(layer, mode)
        if not reports:
            return False

        success = self._send_reports(reports)

        if success:
            logger.info(f"Set LED mode to: {mode.name}")

        return success

    def is_connected(self) -> bool:
        """Check if device is connected."""
        return self.hid.is_open()

    @staticmethod
    def list_devices() -> List[dict]:
        """List all available MacroPad devices."""
        return HidInterface.list_devices()
