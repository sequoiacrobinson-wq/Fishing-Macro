"""Plug the macOS Quartz backends into the shared macro.

This file follows the same patching pattern as the Linux backend: the shared
engine and capture modules live in ``WINDOWS/`` and are swapped at import time
with a platform-specific input/window layer.
"""
from __future__ import annotations

import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_CORE = os.path.join(os.path.dirname(_HERE), "WINDOWS")
for _p in (_CORE, _HERE):
    if _p not in sys.path:
        sys.path.insert(0, _p)


def patch() -> None:
    import bloxfish.engine as engine
    import bloxfish.capture as capture
    from bloxfish.debug import DEBUG
    from inputs_macos import Mouse, Keyboard
    from find_window_macos import find_game_window, focus_game_window

    engine.Mouse = Mouse
    engine.Keyboard = Keyboard
    engine.find_game_window = find_game_window
    engine.focus_game_window = focus_game_window
    capture.find_game_window = find_game_window

    try:
        from overlay_macos import create_macos_overlay
        DEBUG.register_overlay_factory(create_macos_overlay)
    except Exception:  # pragma: no cover
        pass
