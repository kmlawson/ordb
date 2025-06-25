#!/usr/bin/env python3
"""
Test script to verify that color configuration loading works correctly.
"""

import os
import sys
import tempfile
import shutil
from pathlib import Path

# Add parent directory to path to import search module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_default_colors():
    """Test that default colors are loaded when no config file exists."""
    # Save current directory
    orig_dir = os.getcwd()
    
    # Create temporary directory
    with tempfile.TemporaryDirectory() as tmpdir:
        os.chdir(tmpdir)
        
        # Import after changing directory to ensure no config file
        from src.ordb.config import Colors
        
        # Test default colors
        assert Colors.HEADER == '\033[95m', f"Expected HEADER to be purple, got {repr(Colors.HEADER)}"
        assert Colors.LEMMA == '\033[96m', f"Expected LEMMA to be cyan, got {repr(Colors.LEMMA)}"
        assert Colors.WORD_CLASS == '\033[93m', f"Expected WORD_CLASS to be yellow, got {repr(Colors.WORD_CLASS)}"
        assert Colors.HIGHLIGHT == '\033[92m', f"Expected HIGHLIGHT to be green, got {repr(Colors.HIGHLIGHT)}"
        
        print("✅ Default colors test passed")
        
        os.chdir(orig_dir)

def test_custom_config():
    """Test that custom colors are loaded from config file."""
    # Save current directory
    orig_dir = os.getcwd()
    
    # Create temporary directory
    with tempfile.TemporaryDirectory() as tmpdir:
        os.chdir(tmpdir)
        
        # Create custom config
        config_content = """[colors]
header = RED
lemma = BLUE
word_class = GREEN
highlight = YELLOW
"""
        with open('.config-bm', 'w') as f:
            f.write(config_content)
        
        # Remove cached module if exists
        if 'search' in sys.modules:
            del sys.modules['search']
        
        # Import after creating config
        from src.ordb.config import Colors
        
        # Test custom colors
        assert Colors.HEADER == '\033[91m', f"Expected HEADER to be red, got {repr(Colors.HEADER)}"
        assert Colors.LEMMA == '\033[94m', f"Expected LEMMA to be blue, got {repr(Colors.LEMMA)}"
        assert Colors.WORD_CLASS == '\033[92m', f"Expected WORD_CLASS to be green, got {repr(Colors.WORD_CLASS)}"
        assert Colors.HIGHLIGHT == '\033[93m', f"Expected HIGHLIGHT to be yellow, got {repr(Colors.HIGHLIGHT)}"
        
        print("✅ Custom config test passed")
        
        os.chdir(orig_dir)

def test_invalid_config():
    """Test that invalid config values are ignored."""
    # Save current directory
    orig_dir = os.getcwd()
    
    # Create temporary directory
    with tempfile.TemporaryDirectory() as tmpdir:
        os.chdir(tmpdir)
        
        # Create config with invalid values
        config_content = """[colors]
header = INVALID_COLOR
lemma = 123
word_class = 
"""
        with open('.config-bm', 'w') as f:
            f.write(config_content)
        
        # Remove cached module if exists
        if 'search' in sys.modules:
            del sys.modules['search']
        
        # Import after creating config
        from src.ordb.config import Colors
        
        # Test that defaults are used for invalid values
        assert Colors.HEADER == '\033[95m', f"Expected HEADER to use default, got {repr(Colors.HEADER)}"
        assert Colors.LEMMA == '\033[96m', f"Expected LEMMA to use default, got {repr(Colors.LEMMA)}"
        assert Colors.WORD_CLASS == '\033[93m', f"Expected WORD_CLASS to use default, got {repr(Colors.WORD_CLASS)}"
        
        print("✅ Invalid config test passed")
        
        os.chdir(orig_dir)

def test_combined_colors():
    """Test that combined color values work."""
    # Save current directory
    orig_dir = os.getcwd()
    
    # Create temporary directory
    with tempfile.TemporaryDirectory() as tmpdir:
        os.chdir(tmpdir)
        
        # Create config with combined colors
        config_content = """[colors]
header = BOLD_RED
lemma = UNDERLINE_BLUE
"""
        with open('.config-bm', 'w') as f:
            f.write(config_content)
        
        # Remove cached module if exists
        if 'search' in sys.modules:
            del sys.modules['search']
        
        # Import after creating config
        from src.ordb.config import Colors
        
        # Test combined colors
        assert Colors.HEADER == '\033[1m\033[91m', f"Expected HEADER to be bold red, got {repr(Colors.HEADER)}"
        assert Colors.LEMMA == '\033[4m\033[94m', f"Expected LEMMA to be underline blue, got {repr(Colors.LEMMA)}"
        
        print("✅ Combined colors test passed")
        
        os.chdir(orig_dir)

if __name__ == '__main__':
    print("Testing color configuration loading...")
    print("=" * 60)
    
    try:
        test_default_colors()
        test_custom_config()
        test_invalid_config()
        test_combined_colors()
        
        print("\n" + "=" * 60)
        print("✅ All config tests passed!")
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)