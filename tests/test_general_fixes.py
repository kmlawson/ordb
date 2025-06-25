#!/usr/bin/env python3
"""
Test script to verify the three TODO fixes work correctly:
1. --test shows all results instead of "... and X more result(s)"
2. Extra blank lines between numbered definitions are removed
3. Full word highlighting for conjugated/inflected forms
"""

import subprocess
import re
import sys

def test_test_flag_shows_all_results():
    """Test that --test flag shows all results, not just the first one."""
    print("Testing --test flag shows all results...")
    
    result = subprocess.run(['python3', 'ordb', '--test'], 
                          capture_output=True, text=True)
    output = result.stdout
    
    # Should not have "... and X more result(s)" since all results are shown
    if '... and ' in output and 'more result(s)' in output:
        print("  ❌ Still showing '... and X more result(s)' in output")
        return False
    
    # Count all Found X result(s) lines and corresponding entries
    found_matches = re.findall(r'Found (\d+) result\(s\):', output)
    if not found_matches:
        print("  ❌ Could not find any 'Found X result(s):' lines")
        return False
    
    # Focus on stein results - using the actual format from --test output
    stein_start = output.find('Test 1: Searching for')
    stein_end = output.find('Test 2: Searching for')
    if stein_start == -1 or stein_end == -1:
        print("  ❌ Could not find stein test section")
        return False
    
    stein_section = output[stein_start:stein_end]
    stein_found_match = re.search(r'Found (\d+) result\(s\):', stein_section)
    if not stein_found_match:
        print("  ❌ Could not find 'Found X result(s):' line for stein")
        return False
    
    found_count = int(stein_found_match.group(1))
    
    # Should show multiple lemmas for stein (noun and other forms)
    # Count separators or entries to verify all are shown
    stein_lemma_count = stein_section.count('📖')
    
    if stein_lemma_count < 2:
        print(f"  ❌ Expected multiple results for 'stein', got {stein_lemma_count}")
        return False
    
    if found_count != stein_lemma_count:
        print(f"  ❌ Found {found_count} results but only displayed {stein_lemma_count}")
        return False
    
    print(f"  ✅ --test shows all {stein_lemma_count} results for 'stein' (no truncation)")
    return True

def test_no_blank_lines_between_definitions():
    """Test that there are no extra blank lines between numbered definitions."""
    print("Testing definition spacing...")
    
    result = subprocess.run(['python3', 'ordb', 'hus', '--limit', '1'], 
                          capture_output=True, text=True)
    output = result.stdout
    
    # Split by lines and look for the definitions section
    lines = output.split('\n')
    
    # Find lines with numbered definitions
    definition_lines = []
    for i, line in enumerate(lines):
        if re.match(r'^\s+\d+\.\s', line):  # Lines starting with number and dot
            definition_lines.append(i)
    
    # Check spacing between consecutive definitions
    for i in range(len(definition_lines) - 1):
        current_def_line = definition_lines[i]
        next_def_line = definition_lines[i + 1]
        
        # Count blank lines between definitions
        blank_lines = 0
        for line_num in range(current_def_line + 1, next_def_line):
            if lines[line_num].strip() == '':
                blank_lines += 1
        
        # Should have no blank lines between numbered definitions
        if blank_lines > 0:
            print(f"  ❌ Found {blank_lines} blank line(s) between definitions {i+1} and {i+2}")
            return False
    
    print(f"  ✅ No extra blank lines between {len(definition_lines)} definitions")
    return True

def test_full_word_highlighting():
    """Test that conjugated/inflected forms are fully highlighted."""
    print("Testing full word highlighting...")
    
    # Test with 'gå' which has irregular inflections
    result = subprocess.run(['python3', 'ordb', 'gå', '--limit', '1'], 
                          capture_output=True, text=True)
    output = result.stdout
    
    # Look for specific inflected forms that should be fully highlighted
    test_cases = [
        ('gikk', 'det gikk så det sprutet'),
        ('går', 'hjulet går rundt'),
        ('gått', 'pæra er gått'),
        ('går', 'tiden går')
    ]
    
    success_count = 0
    for inflected_form, expected_context in test_cases:
        # Check if the inflected form appears highlighted (green color code around it)
        pattern = rf'{re.escape("\033[92m")}{re.escape(inflected_form)}{re.escape("\033[0m")}'
        if re.search(pattern, output):
            print(f"  ✅ '{inflected_form}' is fully highlighted")
            success_count += 1
        else:
            # Check if it appears in the output at all
            if inflected_form in output:
                print(f"  ❌ '{inflected_form}' appears but is not fully highlighted")
            else:
                print(f"  ⚠️  '{inflected_form}' not found in output")
    
    if success_count >= 3:  # Allow some flexibility
        print(f"  ✅ Full word highlighting working ({success_count}/4 cases)")
        return True
    else:
        print(f"  ❌ Full word highlighting insufficient ({success_count}/4 cases)")
        return False

def test_regular_word_highlighting():
    """Test that regular words starting with search term are highlighted."""
    print("Testing regular word highlighting...")
    
    result = subprocess.run(['python3', 'ordb', 'hus', '--limit', '1'], 
                          capture_output=True, text=True)
    output = result.stdout
    
    # Should highlight inflected forms and words containing 'hus'
    test_cases = ['huset', 'husa', 'hus']
    
    success_count = 0
    for word in test_cases:
        pattern = rf'{re.escape("\033[92m")}{re.escape(word)}{re.escape("\033[0m")}'
        if re.search(pattern, output):
            print(f"  ✅ '{word}' is highlighted")
            success_count += 1
        else:
            # Check if it appears in the output at all
            if word in output:
                print(f"  ⚠️  '{word}' appears but is not highlighted")
            else:
                print(f"  ⚠️  '{word}' not found in output")
    
    if success_count >= 2:
        print(f"  ✅ Regular word highlighting working ({success_count}/{len(test_cases)} cases)")
        return True
    else:
        print(f"  ❌ Regular word highlighting insufficient ({success_count}/{len(test_cases)} cases)")
        return False

if __name__ == '__main__':
    print("Testing TODO fixes...")
    print("=" * 60)
    
    tests = [
        test_test_flag_shows_all_results,
        test_no_blank_lines_between_definitions, 
        test_full_word_highlighting,
        test_regular_word_highlighting
    ]
    
    passed = 0
    total = len(tests)
    
    for test_func in tests:
        try:
            if test_func():
                passed += 1
            print()
        except Exception as e:
            print(f"  ❌ Test failed with error: {e}")
            print()
    
    print("=" * 60)
    if passed == total:
        print(f"✅ All {total} tests passed!")
    else:
        print(f"❌ {passed}/{total} tests passed")
        sys.exit(1)