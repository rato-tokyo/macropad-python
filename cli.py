#!/usr/bin/env python3
"""MacroPad CLI - Configure Chinese macro keypads from command line."""

import argparse
import sys
import logging
from typing import List

from macropad.device import MacroPadDevice
from macropad.models import (
    InputAction, KeyCode, Modifier, MediaKey, MouseButton,
    LedMode, KeySequence
)


def setup_logging(verbose: bool = False):
    """Configure logging."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(levelname)s: %(message)s'
    )


def list_devices(args):
    """List all available MacroPad devices."""
    devices = MacroPadDevice.list_devices()

    if not devices:
        print("No MacroPad devices found.")
        return 1

    print("Available MacroPad devices:")
    for i, dev in enumerate(devices, 1):
        print(f"\n{i}. {dev['manufacturer']} {dev['product']}")
        print(f"   VID:PID = {dev['vendor_id']:04X}:{dev['product_id']:04X}")
        print(f"   Protocol version: {dev['protocol']}")
        print(f"   Path: {dev['path'].decode('utf-8', errors='ignore')}")

    return 0


def parse_key_sequence(key_str: str) -> List[KeySequence]:
    """
    Parse a key sequence string into KeySequence list.

    Format: "LCTRL+LSHIFT+F5,ENTER" or "LCTRL+A"

    Args:
        key_str: Key sequence string

    Returns:
        List of KeySequence tuples
    """
    sequences = []

    # Split by comma for multiple keystrokes
    keystrokes = key_str.upper().split(',')

    for keystroke in keystrokes:
        parts = keystroke.strip().split('+')

        modifiers = Modifier.NONE
        key = KeyCode.NONE

        for part in parts:
            part = part.strip()

            # Check if it's a modifier
            if hasattr(Modifier, part):
                modifiers |= getattr(Modifier, part)
            # Check if it's a key
            elif hasattr(KeyCode, part):
                key = getattr(KeyCode, part)
            # Check for KEY_ prefix (for numbers)
            elif hasattr(KeyCode, f'KEY_{part}'):
                key = getattr(KeyCode, f'KEY_{part}')
            else:
                raise ValueError(f"Unknown key: {part}")

        sequences.append(KeySequence(key, modifiers))

    return sequences


def set_key_cmd(args):
    """Configure a button/knob with keyboard keys."""
    device = MacroPadDevice()

    if not device.connect():
        print("Error: Could not connect to device")
        return 1

    try:
        action = getattr(InputAction, args.action.upper())
    except AttributeError:
        print(f"Error: Invalid action '{args.action}'")
        print(f"Valid actions: {', '.join(a.name for a in InputAction)}")
        return 1

    try:
        sequence = parse_key_sequence(args.keys)
    except ValueError as e:
        print(f"Error: {e}")
        return 1

    if device.set_key_sequence(action, sequence):
        print(f"Successfully configured {action.name}")
        return 0
    else:
        print("Error: Failed to configure device")
        return 1


def set_media_cmd(args):
    """Configure a button/knob with a media key."""
    device = MacroPadDevice()

    if not device.connect():
        print("Error: Could not connect to device")
        return 1

    try:
        action = getattr(InputAction, args.action.upper())
    except AttributeError:
        print(f"Error: Invalid action '{args.action}'")
        return 1

    try:
        media_key = getattr(MediaKey, args.media_key.upper())
    except AttributeError:
        print(f"Error: Invalid media key '{args.media_key}'")
        print(f"Valid media keys: {', '.join(m.name for m in MediaKey)}")
        return 1

    if device.set_media_key(action, media_key):
        print(f"Successfully configured {action.name} with {media_key.name}")
        return 0
    else:
        print("Error: Failed to configure device")
        return 1


def set_mouse_cmd(args):
    """Configure a button/knob with a mouse button."""
    device = MacroPadDevice()

    if not device.connect():
        print("Error: Could not connect to device")
        return 1

    try:
        action = getattr(InputAction, args.action.upper())
    except AttributeError:
        print(f"Error: Invalid action '{args.action}'")
        return 1

    try:
        mouse_button = getattr(MouseButton, args.button.upper())
    except AttributeError:
        print(f"Error: Invalid mouse button '{args.button}'")
        print(f"Valid buttons: {', '.join(b.name for b in MouseButton)}")
        return 1

    # Parse modifiers if provided
    modifiers = Modifier.NONE
    if args.modifiers:
        for mod in args.modifiers.upper().split('+'):
            try:
                modifiers |= getattr(Modifier, mod.strip())
            except AttributeError:
                print(f"Error: Invalid modifier '{mod}'")
                return 1

    if device.set_mouse_button(action, mouse_button, modifiers):
        print(f"Successfully configured {action.name} with {mouse_button.name}")
        return 0
    else:
        print("Error: Failed to configure device")
        return 1


def set_led_cmd(args):
    """Configure LED mode."""
    device = MacroPadDevice()

    if not device.connect():
        print("Error: Could not connect to device")
        return 1

    try:
        led_mode = getattr(LedMode, args.mode.upper())
    except AttributeError:
        print(f"Error: Invalid LED mode '{args.mode}'")
        print(f"Valid modes: {', '.join(m.name for m in LedMode)}")
        return 1

    if device.set_led_mode(led_mode):
        print(f"Successfully set LED mode to {led_mode.name}")
        return 0
    else:
        print("Error: Failed to configure device")
        return 1


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description='Configure Chinese macro keypads (3 button 1 knob type)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # List devices
  %(prog)s list

  # Set button 1 to Ctrl+Shift+F5, Enter
  %(prog)s set-key button_1 "LCTRL+LSHIFT+F5,ENTER"

  # Set button 2 to play/pause media
  %(prog)s set-media button_2 play_pause

  # Set knob clockwise rotation to volume up
  %(prog)s set-media knob_1_cw volume_up

  # Set button 3 to left mouse click
  %(prog)s set-mouse button_3 left

  # Set LED mode to breathe
  %(prog)s set-led breathe

Actions for 3-button 1-knob device:
  button_1, button_2, button_3
  knob_1_cw (clockwise), knob_1_ccw (counter-clockwise), knob_1_press
        """
    )

    parser.add_argument('-v', '--verbose', action='store_true',
                       help='Enable verbose logging')

    subparsers = parser.add_subparsers(dest='command', help='Command to execute')

    # List command
    list_parser = subparsers.add_parser('list', help='List available devices')
    list_parser.set_defaults(func=list_devices)

    # Set-key command
    key_parser = subparsers.add_parser('set-key', help='Configure keyboard keys')
    key_parser.add_argument('action', help='Button/knob action (e.g., button_1, knob_1_cw)')
    key_parser.add_argument('keys', help='Key sequence (e.g., "LCTRL+A,ENTER")')
    key_parser.set_defaults(func=set_key_cmd)

    # Set-media command
    media_parser = subparsers.add_parser('set-media', help='Configure media key')
    media_parser.add_argument('action', help='Button/knob action')
    media_parser.add_argument('media_key', help='Media key (e.g., play_pause, volume_up)')
    media_parser.set_defaults(func=set_media_cmd)

    # Set-mouse command
    mouse_parser = subparsers.add_parser('set-mouse', help='Configure mouse button')
    mouse_parser.add_argument('action', help='Button/knob action')
    mouse_parser.add_argument('button', help='Mouse button (left, right, middle, scroll_up, scroll_down)')
    mouse_parser.add_argument('-m', '--modifiers', help='Modifier keys (e.g., "LCTRL+LSHIFT")')
    mouse_parser.set_defaults(func=set_mouse_cmd)

    # Set-LED command
    led_parser = subparsers.add_parser('set-led', help='Configure LED mode')
    led_parser.add_argument('mode', help='LED mode (off, on, breathe)')
    led_parser.set_defaults(func=set_led_cmd)

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    setup_logging(args.verbose)

    return args.func(args)


if __name__ == '__main__':
    sys.exit(main())
