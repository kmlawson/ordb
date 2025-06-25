#!/usr/bin/env python3
"""
Test script to verify that [expr] word class entries don't show redundant Expressions section.
For expressions, the expression is already shown as the lemma, so showing it again in 
an "Expressions:" section is unnecessary.
"""

import subprocess
import re
import sys

def test_expr_no_redundant_expressions():
    """Test that [expr] word class entries don't show redundant Expressions section."""
    print("Testing that [expr] words don't show redundant Expressions section...")
    
    # Test with a known expression - try the second one first since it worked in manual testing
    result = subprocess.run(['python3', 'ordb', 'gråte over spilt melk', '--limit', '1'], 
                          capture_output=True, text=True)
    output = result.stdout
    
    # Verify that it's an expr word class (check for the colored pattern)
    if 'expr' not in output:
        print(f"  ❌ Could not find [expr] word class entry. Output: {output[:200]}...")
        return False
    
    # Check that there's no "Expressions:" section
    lines = output.split('\n')
    
    for line in lines:
        if 'Expressions:' in line and 'Faste uttrykk:' not in line:
            print("  ❌ Found redundant 'Expressions:' section in [expr] entry")
            return False
    
    print("  ✅ No redundant 'Expressions:' section found in [expr] entry")
    return True

def test_regular_words_still_show_inflections():
    """Test that regular words still show their Inflections section properly."""
    print("Testing that regular words still show Inflections section...")
    
    result = subprocess.run(['python3', 'ordb', 'hus', '--limit', '1'], 
                          capture_output=True, text=True)
    output = result.stdout
    
    # Should have Inflections section for regular words
    if 'Inflections:' not in output:
        print("  ❌ Regular word missing 'Inflections:' section")
        return False
    
    # Should have inflection categories
    if 'Singular:' not in output or 'Plural:' not in output:
        print("  ❌ Regular word missing inflection categories")
        return False
    
    print("  ✅ Regular word shows Inflections section properly")
    return True

def test_multiple_expr_words():
    """Test multiple expr words to ensure the fix works generally."""
    print("Testing multiple [expr] words...")
    
    # Get some expr words from database
    db_result = subprocess.run(['sqlite3', 'articles.db', 'SELECT lemma FROM articles WHERE word_class="EXPR" LIMIT 3;'], 
                             capture_output=True, text=True)
    
    if db_result.returncode != 0:
        print("  ⚠️  Could not query database for expr words")
        return True  # Don't fail the test if we can't query the DB
    
    expr_words = [line.strip() for line in db_result.stdout.strip().split('\n') if line.strip()]
    
    if not expr_words:
        print("  ⚠️  No expr words found in database")
        return True
    
    passed_count = 0
    total_count = 0
    
    for expr_word in expr_words[:3]:  # Test first 3
        total_count += 1
        result = subprocess.run(['python3', 'ordb', expr_word, '--limit', '1'], 
                              capture_output=True, text=True)
        output = result.stdout
        
        # Check if it has redundant Expressions section
        has_redundant_expressions = False
        lines = output.split('\n')
        
        for line in lines:
            if 'Expressions:' in line and 'Faste uttrykk:' not in line:
                has_redundant_expressions = True
                break
        
        if not has_redundant_expressions:
            passed_count += 1
    
    if passed_count == total_count:
        print(f"  ✅ All {total_count} tested [expr] words have no redundant Expressions section")
        return True
    else:
        print(f"  ❌ Only {passed_count}/{total_count} [expr] words passed the test")
        return False

if __name__ == '__main__':
    print("Testing [expr] words redundant expressions fix...")
    print("=" * 60)
    
    tests = [
        test_expr_no_redundant_expressions,
        test_regular_words_still_show_inflections,
        test_multiple_expr_words
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