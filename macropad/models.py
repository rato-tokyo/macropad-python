"""Data models and enums for MacroPad protocol."""

from enum import IntEnum, IntFlag
from typing import NamedTuple


class Modifier(IntFlag):
    """Keyboard modifiers."""
    NONE = 0x00
    LCTRL = 0x01
    LSHIFT = 0x02
    LALT = 0x04
    LGUI = 0x08
    RCTRL = 0x10
    RSHIFT = 0x20
    RALT = 0x40
    RGUI = 0x80


class KeyCode(IntEnum):
    """USB HID keyboard scan codes."""
    NONE = 0x00

    # Letters
    A = 0x04
    B = 0x05
    C = 0x06
    D = 0x07
    E = 0x08
    F = 0x09
    G = 0x0A
    H = 0x0B
    I = 0x0C
    J = 0x0D
    K = 0x0E
    L = 0x0F
    M = 0x10
    N = 0x11
    O = 0x12
    P = 0x13
    Q = 0x14
    R = 0x15
    S = 0x16
    T = 0x17
    U = 0x18
    V = 0x19
    W = 0x1A
    X = 0x1B
    Y = 0x1C
    Z = 0x1D

    # Numbers
    KEY_1 = 0x1E
    KEY_2 = 0x1F
    KEY_3 = 0x20
    KEY_4 = 0x21
    KEY_5 = 0x22
    KEY_6 = 0x23
    KEY_7 = 0x24
    KEY_8 = 0x25
    KEY_9 = 0x26
    KEY_0 = 0x27

    # Special keys
    ENTER = 0x28
    ESC = 0x29
    BACKSPACE = 0x2A
    TAB = 0x2B
    SPACE = 0x2C
    MINUS = 0x2D
    EQUAL = 0x2E
    LEFTBRACE = 0x2F
    RIGHTBRACE = 0x30
    BACKSLASH = 0x31
    SEMICOLON = 0x33
    APOSTROPHE = 0x34
    GRAVE = 0x35
    COMMA = 0x36
    DOT = 0x37
    SLASH = 0x38
    CAPSLOCK = 0x39

    # Function keys
    F1 = 0x3A
    F2 = 0x3B
    F3 = 0x3C
    F4 = 0x3D
    F5 = 0x3E
    F6 = 0x3F
    F7 = 0x40
    F8 = 0x41
    F9 = 0x42
    F10 = 0x43
    F11 = 0x44
    F12 = 0x45

    # Navigation
    PRINTSCREEN = 0x46
    SCROLLLOCK = 0x47
    PAUSE = 0x48
    INSERT = 0x49
    HOME = 0x4A
    PAGEUP = 0x4B
    DELETE = 0x4C
    END = 0x4D
    PAGEDOWN = 0x4E
    RIGHT = 0x4F
    LEFT = 0x50
    DOWN = 0x51
    UP = 0x52


class MediaKey(IntEnum):
    """Media control keys."""
    PLAY_PAUSE = 0xE8
    STOP = 0xE9
    NEXT_TRACK = 0xEB
    PREV_TRACK = 0xEC
    VOLUME_UP = 0xEF
    VOLUME_DOWN = 0xF0
    MUTE = 0xF1


class MouseButton(IntEnum):
    """Mouse buttons and scroll directions."""
    LEFT = 0x01
    RIGHT = 0x02
    MIDDLE = 0x04
    SCROLL_UP = 0x10
    SCROLL_DOWN = 0x20


class InputAction(IntEnum):
    """Input action types for button/knob assignments."""
    BUTTON_1 = 1
    BUTTON_2 = 2
    BUTTON_3 = 3
    KNOB_1_CW = 4
    KNOB_1_CCW = 5
    KNOB_1_PRESS = 6


class KeyType(IntEnum):
    """Type of key function."""
    BASIC = 0
    MULTIMEDIA = 1
    LED = 2


class LedMode(IntEnum):
    """LED modes for 3-button 1-knob device."""
    OFF = 0
    ON = 1
    BREATHE = 2


class KeySequence(NamedTuple):
    """A single keystroke with modifiers."""
    key: KeyCode
    modifiers: Modifier
