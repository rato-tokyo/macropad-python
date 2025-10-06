"""Protocol implementation for MacroPad communication."""

from typing import List, Tuple
from .models import (
    InputAction, KeyCode, Modifier, MediaKey, MouseButton,
    LedMode, KeyType, KeySequence
)
import logging

logger = logging.getLogger(__name__)


class Report:
    """HID report to be sent to device."""

    def __init__(self, report_id: int = 0):
        self.report_id = report_id
        self.data = bytearray(64)

    def __repr__(self):
        return f"Report(id={self.report_id}, data={self.data.hex()})"


class LegacyProtocol:
    """
    Legacy protocol implementation for 3-button 1-knob devices.

    This protocol requires multiple reports to configure a button:
    1. Layer selection (if report_id != 0)
    2. Key function report(s)
    3. Write flash report
    """

    def __init__(self, report_id: int = 0):
        self.report_id = report_id

    def create_layer_selection_report(self, layer: int) -> Report:
        """Create layer selection report."""
        report = Report(self.report_id)
        report.data[0] = 0x01  # Layer selection command
        report.data[1] = layer
        return report

    def create_write_flash_report(self, led: bool = False) -> Report:
        """Create write flash report to save settings."""
        report = Report(self.report_id)
        report.data[0] = 0xFE if led else 0xFF  # Write flash command
        return report

    def create_key_reports(
        self,
        action: InputAction,
        layer: int,
        sequence: List[KeySequence]
    ) -> List[Report]:
        """
        Create key function reports for a keyboard sequence.

        For 3-button 1-knob device: Only the first key's modifiers are stored!

        Args:
            action: Which button/knob action to configure
            layer: Layer number (0 for 3-button 1-knob)
            sequence: List of KeySequence tuples

        Returns:
            List of reports to send
        """
        reports = []

        # Add layer selection if needed
        if self.report_id != 0:
            reports.append(self.create_layer_selection_report(layer))

        # If empty sequence, send None key
        if not sequence:
            sequence = [KeySequence(KeyCode.NONE, Modifier.NONE)]

        # Create key function reports
        # Each key in sequence needs its own report, plus one initial report
        for index in range(len(sequence) + 1):
            report = Report(self.report_id)

            report.data[0] = action.value  # Button/knob action
            report.data[1] = KeyType.BASIC  # Key type
            if self.report_id != 0:
                report.data[1] |= (layer << 4) & 0xFF
            report.data[2] = len(sequence)  # Total sequence length
            report.data[3] = index  # Current index

            if index == 0:
                # First report: Send first key's modifiers
                report.data[4] = int(sequence[0].modifiers)
                report.data[5] = 0
            else:
                # Subsequent reports: Send actual keys
                key_seq = sequence[index - 1]
                report.data[4] = int(key_seq.modifiers)
                report.data[5] = int(key_seq.key)

            reports.append(report)

        # Add write flash command
        reports.append(self.create_write_flash_report())

        return reports

    def create_media_reports(
        self,
        action: InputAction,
        layer: int,
        media_key: MediaKey
    ) -> List[Report]:
        """
        Create media key function reports.

        Args:
            action: Which button/knob action to configure
            layer: Layer number
            media_key: Media key to assign

        Returns:
            List of reports to send
        """
        reports = []

        # Add layer selection if needed
        if self.report_id != 0:
            reports.append(self.create_layer_selection_report(layer))

        # Create media key report
        report = Report(self.report_id)
        report.data[0] = action.value
        report.data[1] = KeyType.MULTIMEDIA
        if self.report_id != 0:
            report.data[1] |= (layer << 4) & 0xFF

        # Media key encoding (simplified for protocol 0)
        if self.report_id == 0:
            report.data[2] = media_key.value & 0xFF
            report.data[3] = 0
        else:
            report.data[2] = media_key.value & 0xFF
            report.data[3] = (media_key.value >> 8) & 0xFF

        reports.append(report)
        reports.append(self.create_write_flash_report())

        return reports

    def create_mouse_reports(
        self,
        action: InputAction,
        layer: int,
        button: MouseButton,
        modifiers: Modifier
    ) -> List[Report]:
        """
        Create mouse button function reports.

        Args:
            action: Which button/knob action to configure
            layer: Layer number
            button: Mouse button or scroll direction
            modifiers: Modifier keys

        Returns:
            List of reports to send
        """
        reports = []

        # Add layer selection if needed
        if self.report_id != 0:
            reports.append(self.create_layer_selection_report(layer))

        # Create mouse function report
        report = Report(self.report_id)
        report.data[0] = action.value
        report.data[1] = KeyType.MULTIMEDIA
        if self.report_id != 0:
            report.data[1] |= (layer << 4) & 0xFF

        # Mouse button encoding
        if button in (MouseButton.LEFT, MouseButton.RIGHT, MouseButton.MIDDLE):
            report.data[2] = button.value
            report.data[3] = 0
        else:  # Scroll
            report.data[2] = 0
            report.data[3] = button.value

        report.data[4] = int(modifiers)

        reports.append(report)
        reports.append(self.create_write_flash_report())

        return reports

    def create_led_reports(
        self,
        layer: int,
        mode: LedMode
    ) -> List[Report]:
        """
        Create LED mode reports.

        Args:
            layer: Layer number
            mode: LED mode

        Returns:
            List of reports to send
        """
        # For protocol 0, only modes 0-2 are supported
        if self.report_id == 0 and mode.value > 2:
            logger.warning(f"LED mode {mode} not supported on protocol 0")
            return []

        report = Report(self.report_id)
        report.data[0] = 0xB0  # LED function command
        report.data[1] = mode.value
        report.data[2] = 0  # Color (not supported on 3-button 1-knob)

        return [report, self.create_write_flash_report(led=True)]


class ExtendedProtocol:
    """
    Extended protocol implementation for newer devices.

    This protocol uses a single extended report format for each configuration.
    Not implemented yet as we're focusing on 3-button 1-knob device.
    """

    def __init__(self, report_id: int = 0):
        self.report_id = report_id
        raise NotImplementedError("Extended protocol not yet implemented")
