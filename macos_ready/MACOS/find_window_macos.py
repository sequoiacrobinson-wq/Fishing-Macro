"""macOS-specific window find/focus helpers for the shared engine.

The shared code expects a ``find_game_window(title, screen) -> (Rect, bool)``
contract and a ``focus_game_window(title) -> bool`` activation helper.
"""
from __future__ import annotations

import subprocess


def _window_records():
    try:
        import Quartz
    except Exception:  # pragma: no cover
        return []

    try:
        info = Quartz.CGWindowListCopyWindowInfo(
            Quartz.kCGWindowListOptionAll,
            Quartz.kCGNullWindowID,
        )
    except Exception:  # pragma: no cover
        return []
    return list(info) if info else []


def _frame_from_record(rec: dict) -> tuple[int, int, int, int] | None:
    bounds = rec.get("kCGWindowBounds") or {}
    if not isinstance(bounds, dict):
        return None
    try:
        x = int(bounds.get("X", 0))
        y = int(bounds.get("Y", 0))
        width = int(bounds.get("Width", 0))
        height = int(bounds.get("Height", 0))
    except Exception:  # pragma: no cover
        return None
    if width <= 0 or height <= 0:
        return None
    return x, y, width, height


def find_game_window(title: str, screen) -> tuple[object, bool]:
    """Return a Roblox client rect if one is visible, else fall back to the display."""
    from bloxfish.capture import Rect

    wanted = (title or "Roblox").strip().lower()
    best = None
    for rec in _window_records():
        name = (rec.get("kCGWindowName") or "").strip()
        owner = (rec.get("kCGWindowOwnerName") or "").strip()
        if not name and not owner:
            continue
        if name.lower() != wanted and not name.lower().startswith(wanted + " "):
            if owner.lower() != wanted and not owner.lower().startswith(wanted + " "):
                continue
        frame = _frame_from_record(rec)
        if frame is None:
            continue
        left, top, width, height = frame
        area = width * height
        candidate = Rect(left + 8, top + 8, max(1, width - 16), max(1, height - 16))
        if best is None or area > best[0]:
            best = (area, candidate)
    if best is not None:
        return best[1], True
    return screen.primary(), False


def focus_game_window(title: str) -> bool:
    """Activate the Roblox app on the frontmost desktop.

    The project’s Windows behaviour is to bring the target client to the front
    before sending mouse/keyboard input. On macOS Monterey, a direct app
    activation is the practical equivalent, and it avoids introducing a heavy
    window-manager dependency.
    """
    app_name = (title or "Roblox").strip() or "Roblox"
    try:
        subprocess.run([
            "osascript",
            "-e",
            f'tell application "{app_name}" to activate',
        ], check=False, capture_output=True, text=True, timeout=10)
        return True
    except Exception:  # pragma: no cover
        return False
