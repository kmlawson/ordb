#!/usr/bin/env python3
"""
ordb - Norwegian dictionary search tool
Entry point script for the modularized ordb package.
"""

import sys
import os

# Add the current directory to the Python path so we can import from src/
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.ordb.cli import main

if __name__ == "__main__":
    main()