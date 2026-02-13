#!/bin/bash
# ═══════════════════════════════════════════════════════════════
#  CANDELA Test Suite — Double-click to launch
# ═══════════════════════════════════════════════════════════════
#  Just double-click this file. The visual test suite will open.
#  No technical knowledge required.
# ═══════════════════════════════════════════════════════════════

cd "$(dirname "$0")"

# Find the right Python (needs 3.11+ for the GUI to work on macOS)
if command -v python3.11 &>/dev/null; then
    PYTHON=python3.11
elif command -v /usr/local/bin/python3.11 &>/dev/null; then
    PYTHON=/usr/local/bin/python3.11
elif command -v python3 &>/dev/null; then
    PYTHON=python3
else
    osascript -e 'display dialog "Python 3 is not installed.\n\nPlease install Python from python.org and try again." with title "CANDELA Test Suite" buttons {"OK"} default button "OK" with icon stop'
    exit 1
fi

# Launch the GUI
exec "$PYTHON" gui_test_suite.py
