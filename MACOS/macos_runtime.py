"""macOS Monterey Intel runtime context for the shared macro implementation.

The project core lives under ``WINDOWS/``; macOS needs isolated config storage,
GUI assets, and platform metadata before the shared code imports.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path


HERE = Path(__file__).resolve().parent
CORE = HERE.parent / "WINDOWS"


def macos_environment(config_path: str | Path | None = None) -> dict[str, str]:
    """Return the isolated Monterey Intel runtime environment."""
    config = (Path(config_path).expanduser().resolve() if config_path
              else HERE / "config.json")
    runtime_root = config.parent
    return {
        "BLOXFISH_NO_BOOT": "1",
        "BLOXFISH_CONFIG_PATH": str(config),
        "BLOXFISH_RUNTIME_ROOT": str(runtime_root),
        "BLOXFISH_GUI_ASSETS": str(HERE / "assets" / "gui"),
        "BLOXFISH_PLATFORM": "monterey-intel",
    }


def configure_macos_runtime(config_path: str | Path | None = None) -> Path:
    """Set paths before shared modules import, then expose both code roots."""
    env = macos_environment(config_path)
    os.environ.update(env)
    for path in (str(CORE), str(HERE)):
        if path not in sys.path:
            sys.path.insert(0, path)
    return Path(env["BLOXFISH_CONFIG_PATH"])
