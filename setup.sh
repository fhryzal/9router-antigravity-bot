#!/bin/bash
# Setup: installs DrissionPage and checks for Chrome
set -e

echo "9Router Antigravity Bot - Setup"
echo "================================"
echo ""

if ! command -v python3 &>/dev/null; then
    echo "[ERROR] Python 3 not found. Install it first."
    exit 1
fi
echo "[OK] Python $(python3 --version 2>&1 | cut -d' ' -f2)"

if command -v google-chrome &>/dev/null; then
    echo "[OK] Chrome: $(google-chrome --version 2>/dev/null | head -1)"
elif command -v chromium-browser &>/dev/null; then
    echo "[OK] Chromium: $(chromium-browser --version 2>/dev/null | head -1)"
elif command -v chromium &>/dev/null; then
    echo "[OK] Chromium: $(chromium --version 2>/dev/null | head -1)"
else
    echo "[WARN] Chrome/Chromium not found."
    echo "       Install: sudo apt install chromium"
fi

echo ""
echo "Installing DrissionPage..."
pip3 install DrissionPage 2>/dev/null || pip3 install --break-system-packages DrissionPage 2>/dev/null || {
    echo "Creating virtual environment..."
    python3 -m venv .venv
    .venv/bin/pip install DrissionPage
    echo ""
    echo "[NOTE] Installed in .venv - run with: .venv/bin/python3 bot.py"
}

echo ""
echo "Setup complete."
echo ""
echo "  1. Create accounts.txt:  email|password"
echo "  2. Run:  python3 bot.py"
echo ""
