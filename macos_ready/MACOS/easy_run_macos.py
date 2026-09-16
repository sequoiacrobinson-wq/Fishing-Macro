#!/usr/bin/env python3
"""The full GUI on macOS Monterey Intel.

This mirrors the Linux launcher pattern: establish the isolated runtime,
preflight the environment, patch in the Quartz backend, and import the shared
Windows GUI code.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
WINDOWS = ROOT / "WINDOWS"
MACOS = Path(__file__).resolve().parent


def _ensure_requirements() -> None:
    """Install the runtime needs automatically on first launch."""
    missing = []
    for module in ("numpy", "cv2", "mss", "customtkinter", "PIL", "pynput"):
        try:
            __import__(module)
        except Exception:  # pragma: no cover
            missing.append(module)
    if not missing:
        return
    print("[macos] Installing project dependencies…")
    subprocess.run([
        sys.executable,
        "-m", "pip",
        "install",
        "-r", str(WINDOWS / "requirements.txt"),
        "-r", str(MACOS / "requirements-macos.txt"),
    ], check=False)


def main() -> int:
    if sys.platform != "darwin":
        print("This is the macOS entry point — run easy_run.py on Windows.")
        return 1

    _ensure_requirements()

    from macos_runtime import configure_macos_runtime
    configure_macos_runtime()

    from _backend import patch
    try:
        patch()
    except Exception as exc:  # pragma: no cover
        print(f"Could not load the macOS backend: {exc}\n")
        print("  1) python3 -m pip install -r WINDOWS/requirements.txt")
        print("  2) python3 -m pip install -r MACOS/requirements-macos.txt")
        return 1

    import easy_run
    app = easy_run.App()
    app.protocol("WM_DELETE_WINDOW", app._close)
    app.mainloop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
