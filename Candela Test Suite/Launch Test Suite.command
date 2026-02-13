#!/bin/bash
# ═══════════════════════════════════════════════════════════════
#  CANDELA Test Suite — Double-click to launch
# ═══════════════════════════════════════════════════════════════
#  Just double-click this file. The visual test suite will open.
#  No technical knowledge required.
# ═══════════════════════════════════════════════════════════════

cd "$(dirname "$0")"

# Find Python 3.11+ (required for the GUI to work on macOS)
PYTHON=""

# Prefer explicit python3.11
if command -v python3.11 &>/dev/null; then
    PYTHON=python3.11
elif command -v /usr/local/bin/python3.11 &>/dev/null; then
    PYTHON=/usr/local/bin/python3.11
fi

# If no explicit 3.11, check whether python3 is >= 3.11
if [ -z "$PYTHON" ] && command -v python3 &>/dev/null; then
    PY_VER=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')" 2>/dev/null)
    PY_MAJOR=$(echo "$PY_VER" | cut -d. -f1)
    PY_MINOR=$(echo "$PY_VER" | cut -d. -f2)
    if [ "$PY_MAJOR" -ge 3 ] 2>/dev/null && [ "$PY_MINOR" -ge 11 ] 2>/dev/null; then
        PYTHON=python3
    fi
fi

if [ -z "$PYTHON" ]; then
    osascript -e 'display dialog "Python 3.11 or later is required but was not found.\n\nYour system has an older version of Python that is not compatible with the test suite GUI.\n\nPlease install Python 3.11+ from python.org and try again." with title "CANDELA Test Suite" buttons {"OK"} default button "OK" with icon stop'
    exit 1
fi

# Verify tkinter is available
if ! "$PYTHON" -c "import tkinter" 2>/dev/null; then
    osascript -e 'display dialog "Python was found but the tkinter module is missing.\n\nThis is needed for the visual interface.\n\nPlease reinstall Python from python.org (the official installer includes tkinter)." with title "CANDELA Test Suite" buttons {"OK"} default button "OK" with icon stop'
    exit 1
fi

# Launch the GUI
exec "$PYTHON" gui_test_suite.py
