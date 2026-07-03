#!/bin/bash
# Quick setup — installs DrissionPage and verifies Chrome
set -e

echo "═══════════════════════════════════════════"
echo "  9Router × Antigravity — Setup"
echo "═══════════════════════════════════════════"
echo ""

# Check Python
if ! command -v python3 &>/dev/null; then
    echo "✗ Python 3 not found. Install it first."
    exit 1
fi
echo "✓ Python $(python3 --version 2>&1 | cut -d' ' -f2)"

# Check Chrome
if command -v google-chrome &>/dev/null; then
    echo "✓ Chrome found: $(google-chrome --version 2>/dev/null | head -1)"
elif command -v chromium-browser &>/dev/null; then
    echo "✓ Chromium found: $(chromium-browser --version 2>/dev/null | head -1)"
elif command -v chromium &>/dev/null; then
    echo "✓ Chromium found: $(chromium --version 2>/dev/null | head -1)"
else
    echo "⚠ Chrome/Chromium not found."
    echo "  Install: sudo apt install chromium  (or download from google.com/chrome)"
fi

# Install DrissionPage
echo ""
echo "Installing DrissionPage..."
pip3 install DrissionPage 2>/dev/null || pip3 install --break-system-packages DrissionPage 2>/dev/null || {
    echo "Creating virtual environment..."
    python3 -m venv .venv
    .venv/bin/pip install DrissionPage
    echo ""
    echo "⚠ Installed in .venv — run with: .venv/bin/python3 bot.py"
}

echo ""
echo "✓ Setup complete!"
echo ""
echo "  1. Create accounts.txt:  email|password"
echo "  2. Run:  python3 bot.py"
echo ""
