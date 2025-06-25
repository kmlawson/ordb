#!/bin/bash
# Installation script for ordb

set -e

echo "Installing ordb - Norwegian dictionary search tool..."

# Check if Python 3.8+ is available
if ! python3 -c "import sys; exit(0 if sys.version_info >= (3, 8) else 1)" 2>/dev/null; then
    echo "Error: Python 3.8 or later is required"
    exit 1
fi

# Install in development mode
echo "Installing ordb in development mode..."
pip3 install -e .

# Make ordb script executable
chmod +x ordb

echo "Installation complete!"
echo "You can now use ordb from the command line:"
echo "  ./ordb gå"
echo "  python -m ordb gå"
echo ""
echo "To run tests:"
echo "  python -m pytest tests/"
echo ""
echo "To configure colors and settings:"
echo "  ./ordb -c"