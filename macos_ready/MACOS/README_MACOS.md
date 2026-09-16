# macOS / Monterey Intel support

This is the Monterey Intel launcher for the same Blox Fruits fishing macro and premium GUI used on Windows. It targets the shared engine in `WINDOWS/` and swaps in a macOS-specific input and window layer.

> This is a compatibility-oriented port, intended for Intel Macs running macOS Monterey. It follows the same platform-isolation pattern as the Linux launcher so the Windows profile remains untouched unless you explicitly configure a separate macOS profile.

## Before launching

1. Install Python 3.10+ and the project dependencies.

   ```bash
   python3 -m pip install -r WINDOWS/requirements.txt
   python3 -m pip install -r MACOS/requirements-macos.txt
   ```

2. Use a normal desktop session and ensure Roblox is running and visible.

3. Open the project from a terminal and launch:

   ```bash
   python3 MACOS/easy_run_macos.py
   ```

## Notes

- The shared detection and control engine stays in `WINDOWS/`.
- This launcher uses a dedicated runtime context in `MACOS/` to keep config, logs, and calibration state separate from the Windows profile.
- Input injection is done via macOS Quartz/CoreGraphics event posting, which is the closest match to the project’s Windows `SendInput` model.
- Window activation currently uses AppleScript with the Roblox app name; if your Roblox title differs from the default client title, adjust the finder accordingly.

## Limitations

- This port is intentionally conservative and is designed around Intel Monterey.
- macOS focus rules and input behavior can vary by app, display, and accessibility settings.
- If the app cannot find the Roblox client or the Quartz backend is unavailable, the macro will stop before sending input rather than misdirecting clicks.
