"""Quartz input backend for macOS Monterey Intel.

This mirrors the Windows ``bloxfish.inputs`` API while using CoreGraphics event
posting so the shared engine can use the same mouse and keyboard behaviours.
"""
from __future__ import annotations

import time

try:
    import Quartz
    from AppKit import NSEvent
except ImportError as exc:  # pragma: no cover
    raise ImportError(
        "The macOS backend needs pyobjc + Quartz. Install: pip install -r MACOS/requirements-macos.txt"
    ) from exc

# Physical-key mapping for the Roblox hotbar and movement keys. These are the
# ANSI key codes used by macOS (same logical keys as the Windows scan codes).
SC_W = 13
SC_S = 1
SC_A = 0
SC_D = 2
SC_LSHIFT = 56
SC_E = 14
SC_DIGITS = {"1": 18, "2": 19, "3": 20, "4": 21, "5": 23,
             "6": 22, "7": 26, "8": 28, "9": 25, "0": 29}


def digit_scan(slot: str, default: str = "1") -> int:
    key = str(slot).strip()
    if key in SC_DIGITS:
        return SC_DIGITS[key]
    return SC_DIGITS.get(str(default).strip(), SC_DIGITS["1"])


def valid_slot(slot) -> bool:
    return str(slot).strip() in SC_DIGITS


def _post_mouse(button, down: bool) -> None:
    event = Quartz.CGEventCreateMouseEvent(
        None,
        Quartz.kCGEventLeftMouseDown if down else Quartz.kCGEventLeftMouseUp,
        Quartz.CGPointMake(0, 0),
        button,
    )
    Quartz.CGEventPost(Quartz.kCGHIDEventTap, event)


def _post_key(code: int, down: bool) -> None:
    event = Quartz.CGEventCreateKeyboardEvent(None, code, down)
    Quartz.CGEventPost(Quartz.kCGHIDEventTap, event)


class Keyboard:
    def down(self, scan: int) -> None:
        _post_key(scan, True)

    def up(self, scan: int) -> None:
        _post_key(scan, False)

    def tap(self, scan: int, hold: float = 0.06) -> None:
        self.down(scan)
        time.sleep(hold)
        self.up(scan)


class Mouse:
    REASSERT_AFTER = 0.15

    def __init__(self) -> None:
        self._down = False
        self._asserted = 0.0

    @property
    def is_down(self) -> bool:
        return self._down

    def set(self, down: bool) -> None:
        now = time.perf_counter()
        if down != self._down or now - self._asserted >= self.REASSERT_AFTER:
            _post_mouse(Quartz.kCGMouseButtonLeft, down)
            self._down = down
            self._asserted = now

    def press(self) -> None:
        self.set(True)

    def release(self) -> None:
        self.set(False)

    def click(self, hold: float = 0.045) -> None:
        self.press()
        time.sleep(hold)
        self.release()

    def move_to(self, x: int, y: int) -> None:
        Quartz.CGWarpMouseCursorPosition(Quartz.CGPointMake(float(x), float(y)))

    def position(self) -> tuple[int, int]:
        point = NSEvent.mouseLocation()
        return int(point.x), int(point.y)

    def click_at(self, x: int, y: int, settle: float = 0.12, hold: float = 0.05) -> None:
        self.move_to(int(x) - 8, int(y) - 8)
        time.sleep(0.02)
        self.move_to(x, y)
        time.sleep(settle)
        self.click(hold)

    def __enter__(self) -> "Mouse":
        return self

    def __exit__(self, *exc) -> None:
        self.release()
