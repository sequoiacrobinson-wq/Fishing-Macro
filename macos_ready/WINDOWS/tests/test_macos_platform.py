from __future__ import annotations

import importlib
import os
import sys
import types
import unittest
from pathlib import Path
from unittest import mock

WINDOWS = Path(__file__).resolve().parents[1]
PROJECT = WINDOWS.parent
MACOS = PROJECT / "MACOS"
for path in (str(WINDOWS), str(MACOS)):
    if path not in sys.path:
        sys.path.insert(0, path)

from bloxfish import engine as engine_mod
from bloxfish import shop as shop_mod
from bloxfish.config import Config
from bloxfish.debug import DebugBus
from macos_runtime import macos_environment


class MacosProfileTests(unittest.TestCase):
    def test_macos_context_isolated_from_the_windows_runtime(self) -> None:
        config = MACOS / "profiles" / "monterey.json"
        env = macos_environment(config)
        self.assertEqual(Path(env["BLOXFISH_CONFIG_PATH"]), config.resolve())
        self.assertEqual(Path(env["BLOXFISH_RUNTIME_ROOT"]), config.parent.resolve())
        self.assertEqual(Path(env["BLOXFISH_GUI_ASSETS"]), MACOS / "assets" / "gui")
        self.assertEqual(env["BLOXFISH_PLATFORM"], "monterey-intel")

    def test_backend_patch_replaces_every_engine_platform_seam(self) -> None:
        backend = importlib.import_module("_backend")
        import bloxfish.capture as capture
        import bloxfish.debug as debug_mod

        fake_mouse = type("Mouse", (), {})
        fake_keyboard = type("Keyboard", (), {})
        fake_window = lambda *_args: None
        fake_focus = lambda *_args: True
        fake_overlay = lambda _parent: object()
        inputs = types.ModuleType("inputs_macos")
        inputs.Mouse, inputs.Keyboard = fake_mouse, fake_keyboard
        finder = types.ModuleType("find_window_macos")
        finder.find_game_window, finder.focus_game_window = fake_window, fake_focus
        overlay = types.ModuleType("overlay_macos")
        overlay.create_macos_overlay = fake_overlay
        original = (engine_mod.Mouse, engine_mod.Keyboard, engine_mod.find_game_window,
                    engine_mod.focus_game_window, capture.find_game_window,
                    debug_mod.DEBUG._overlay_factory)
        try:
            with mock.patch.dict(sys.modules, {
                "inputs_macos": inputs, "find_window_macos": finder,
                "overlay_macos": overlay,
            }):
                backend.patch()
            self.assertIs(engine_mod.Mouse, fake_mouse)
            self.assertIs(engine_mod.Keyboard, fake_keyboard)
            self.assertIs(engine_mod.find_game_window, fake_window)
            self.assertIs(engine_mod.focus_game_window, fake_focus)
            self.assertIs(capture.find_game_window, fake_window)
            self.assertIs(debug_mod.DEBUG._overlay_factory, fake_overlay)
        finally:
            (engine_mod.Mouse, engine_mod.Keyboard, engine_mod.find_game_window,
             engine_mod.focus_game_window, capture.find_game_window,
             debug_mod.DEBUG._overlay_factory) = original


if __name__ == "__main__":
    unittest.main()
