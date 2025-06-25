#!/usr/bin/env python3
"""
Test script to verify that search term highlighting works correctly in expressions.
"""

import subprocess
import re

def test_expression_highlighting():
    """Test that search terms are highlighted in expression names, definitions, and examples."""
    
    # Test case 1: Search for 'hus'
    print("Testing highlighting for 'hus'...")
    result = subprocess.run(['python3', 'ordb', 'hus', '--limit', '1'], 
                          capture_output=True, text=True)
    output = result.stdout
    
    # Check if the green highlight code appears with 'hus'
    # The pattern is: ESC[92m (green) followed by 'hus' followed by ESC[0m (reset)
    green_hus_count = output.count('\033[92mhus\033[0m')
    
    if green_hus_count > 0:
        print(f"  ✅ Found {green_hus_count} highlighted occurrences of 'hus'")
        
        # Check specific contexts
        if 'fullt \033[92mhus\033[0m' in output:
            print("  ✅ 'hus' highlighted in expression name 'fullt hus'")
        
        if 'gå \033[92mhus\033[0m' in output:
            print("  ✅ 'hus' highlighted in expression name 'gå hus forbi'")
            
        if 'på \033[92mhus\033[0m' in output:
            print("  ✅ 'hus' highlighted in expression name 'på huset'")
            
        # Check if highlighted in examples
        if 'spille for fullt \033[92mhus\033[0m' in output or 'gått \033[92mhus\033[0m forbi' in output:
            print("  ✅ 'hus' highlighted in expression examples")
    else:
        print("  ❌ No highlighted 'hus' found in expressions")
        return False
    
    # Test case 2: Search for 'gå'
    print("\nTesting highlighting for 'gå'...")
    result = subprocess.run(['python3', 'ordb', 'gå', '--limit', '1'], 
                          capture_output=True, text=True)
    output = result.stdout
    
    green_ga_count = output.count('\033[92mgå\033[0m')
    
    if green_ga_count > 0:
        print(f"  ✅ Found {green_ga_count} highlighted occurrences of 'gå'")
        
        if '\033[92mgå\033[0m\033[1m an\033[0m' in output or '\033[92mgå\033[0m\033[1m av\033[0m' in output:
            print("  ✅ 'gå' highlighted in expression names")
            
        if 'det \033[92mgå\033[0m' in output or 'må \033[92mgå\033[0m' in output:
            print("  ✅ 'gå' highlighted in expression examples")
    else:
        print("  ❌ No highlighted 'gå' found in expressions")
        return False
    
    return True

def test_highlight_preservation():
    """Test that existing colors are preserved when highlighting."""
    result = subprocess.run(['python3', 'ordb', 'hus', '--limit', '1'], 
                          capture_output=True, text=True)
    output = result.stdout
    
    # Check that bold formatting is preserved in expression names
    if '\033[1m' in output and 'Faste uttrykk:' in output:
        print("\n✅ Bold formatting preserved in expressions")
    else:
        print("\n❌ Bold formatting not found in expressions")
        return False
    
    # Check that cyan color is preserved in examples
    if '\033[96m' in output:
        print("✅ Cyan color preserved in examples")
    else:
        print("❌ Cyan color not found in examples")
        return False
    
    return True

if __name__ == '__main__':
    print("Testing search term highlighting in expressions...")
    print("=" * 60)
    
    test1_passed = test_expression_highlighting()
    test2_passed = test_highlight_preservation()
    
    print("\n" + "=" * 60)
    if test1_passed and test2_passed:
        print("✅ All highlighting tests passed!")
    else:
        print("❌ Some highlighting tests failed")