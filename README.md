# MacroPad Python CLI

Python command-line tool for configuring Chinese macro keypads (3-button 1-knob type).

This is a Python reimplementation of [rOzzy1987/MacroPad](https://github.com/rOzzy1987/MacroPad) focusing on CLI usage and supporting the 3-button 1-knob device type.

## Features

- ✅ Python-based CLI interface
- ✅ Support for 3-button 1-knob macro keypad
- ✅ Configure keyboard shortcuts with modifiers
- ✅ Assign media keys (play/pause, volume, etc.)
- ✅ Assign mouse buttons and scrolling
- ✅ Control LED modes (off, on, breathe)
- ✅ No GUI required

## Supported Devices

Currently supports the **3-button 1-knob** macro keypad:
- VID:PID = 1189:8890 (4489:34960 decimal)
- 3 buttons + 1 rotary encoder (with push button)
- Legacy Protocol (version 0)

## Installation

### Prerequisites

Python 3.7+ and pip are required.

### Platform-Specific Setup

#### Windows

No additional setup required! Just install Python dependencies:

```bash
pip install -r requirements.txt
```

**Note:** On Windows, you may need to run the command prompt as Administrator for the first time to access HID devices.

#### Linux

Install libhidapi library:

```bash
# Ubuntu/Debian
sudo apt install libhidapi-libusb0

# Fedora
sudo dnf install hidapi

# Arch Linux
sudo pacman -S hidapi
```

Then install Python dependencies:

```bash
pip install -r requirements.txt
```

#### Linux Permissions

On Linux, you need udev rules to access HID devices without root:

```bash
# Create udev rule
echo 'SUBSYSTEM=="hidraw", ATTRS{idVendor}=="1189", MODE="0666"' | sudo tee /etc/udev/rules.d/99-macropad.rules

# Reload udev rules
sudo udevadm control --reload-rules
sudo udevadm trigger

# Reconnect your device
```

## Usage

### List Devices

```bash
python cli.py list
```

### Configure Buttons and Knob

The 3-button 1-knob device has these actions:
- `button_1`, `button_2`, `button_3` - The three buttons
- `knob_1_cw` - Knob rotation clockwise
- `knob_1_ccw` - Knob rotation counter-clockwise
- `knob_1_press` - Knob push button

### Keyboard Shortcuts

Configure a button to send keyboard keys:

```bash
# Single key with modifiers
python cli.py set-key button_1 "LCTRL+LSHIFT+F5"

# Multiple keystrokes (separated by comma)
python cli.py set-key button_2 "LCTRL+A,ENTER"

# Simple key
python cli.py set-key button_3 "F1"
```

**Note:** The 3-button 1-knob device only stores modifiers for the first key in a sequence!

Available modifiers: `LCTRL`, `LSHIFT`, `LALT`, `LGUI`, `RCTRL`, `RSHIFT`, `RALT`, `RGUI`

Available keys: `A-Z`, `KEY_0-KEY_9`, `F1-F12`, `ENTER`, `ESC`, `SPACE`, `TAB`, `BACKSPACE`, etc.

### Media Keys

```bash
# Play/Pause
python cli.py set-media button_1 play_pause

# Volume control on knob
python cli.py set-media knob_1_cw volume_up
python cli.py set-media knob_1_ccw volume_down

# Other media keys
python cli.py set-media button_2 next_track
python cli.py set-media button_3 prev_track
```

Available media keys: `play_pause`, `stop`, `next_track`, `prev_track`, `volume_up`, `volume_down`, `mute`

### Mouse Buttons

```bash
# Left click
python cli.py set-mouse button_1 left

# Right click
python cli.py set-mouse button_2 right

# Middle click
python cli.py set-mouse button_3 middle

# Scroll
python cli.py set-mouse knob_1_cw scroll_up
python cli.py set-mouse knob_1_ccw scroll_down

# Mouse button with modifiers (only left-side modifiers supported)
python cli.py set-mouse button_1 left -m "LCTRL"
```

### LED Control

```bash
# Turn off
python cli.py set-led off

# Turn on
python cli.py set-led on

# Breathing effect
python cli.py set-led breathe
```

### Verbose Output

Add `-v` or `--verbose` for detailed logging:

```bash
python cli.py -v set-key button_1 "LCTRL+A"
```

## Project Structure

```
macropad-python/
├── macropad/
│   ├── __init__.py       # Package initialization
│   ├── models.py         # Enums and data models
│   ├── hid_interface.py  # HID communication layer
│   ├── protocol.py       # Protocol implementation
│   └── device.py         # High-level device API
├── cli.py                # CLI interface
├── requirements.txt      # Python dependencies
└── README.md
```

## Protocol Details

The 3-button 1-knob device uses the **Legacy Protocol (version 0)**:

- Communication via USB HID reports (64 bytes)
- Each configuration requires multiple reports:
  1. Key/media/mouse function report(s)
  2. Write flash report (to save to device)
- Supports up to 5 keystrokes per button
- Single layer only
- LED modes: OFF, ON, BREATHE (no color support)

## Limitations

For the 3-button 1-knob device:
- ✅ 3 buttons + 1 knob (6 total actions)
- ✅ Up to 5 keystrokes per action
- ⚠️ **Only the first keystroke can have modifiers**
- ✅ Single layer (no multi-layer support)
- ✅ Media keys supported
- ⚠️ Mouse modifiers: only left-side modifiers supported
- ✅ LED modes: OFF, ON, BREATHE (no colors)

## Contributing

This project focuses specifically on the 3-button 1-knob device type. For other device types, please refer to the original [rOzzy1987/MacroPad](https://github.com/rOzzy1987/MacroPad) project.

## License

MIT License

## Credits

Based on the protocol reverse-engineering work from [rOzzy1987/MacroPad](https://github.com/rOzzy1987/MacroPad).

## Troubleshooting

### Device not found
- **Windows:** Ensure device is plugged in. Try running Command Prompt as Administrator.
- **Linux:** Ensure device is plugged in and check udev rules (see Installation section)

### Permission denied (Linux only)
- Set up udev rules (see Installation section)
- Reconnect device after adding rules
- Check with `ls -l /dev/hidraw*` to verify permissions
- If still failing, try running with `sudo` temporarily (not recommended for regular use)

### Configuration not working
- Run with `-v` flag to see detailed logs: `python cli.py -v list`
- Verify your device is the 3-button 1-knob type (VID:PID = 1189:8890)
- Try disconnecting and reconnecting the device
- **Windows:** Some antivirus software may block HID access - temporarily disable to test
