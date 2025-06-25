#!/usr/bin/env python3
"""
Test script to check that expressions with multiple definitions are handled correctly.
"""

import sqlite3
import sys
from pathlib import Path

def test_multiple_definitions_for_expressions():
    """Test that expressions with multiple definitions are captured correctly."""
    db_path = 'articles.db'
    
    if not Path(db_path).exists():
        print(f"Error: Database {db_path} not found.")
        sys.exit(1)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Find expressions that have multiple definitions
    cursor.execute('''
        SELECT a.lemma, COUNT(DISTINCT d.id) as def_count
        FROM articles a
        JOIN definitions d ON a.article_id = d.article_id
        WHERE a.word_class = 'EXPR'
        GROUP BY a.article_id, a.lemma
        HAVING def_count > 1
        ORDER BY def_count DESC
        LIMIT 10
    ''')
    
    multi_def_expressions = cursor.fetchall()
    
    if not multi_def_expressions:
        print("No expressions with multiple definitions found in the database.")
        return
    
    print(f"Found {len(multi_def_expressions)} expressions with multiple definitions:")
    print("-" * 60)
    
    for expr_lemma, def_count in multi_def_expressions:
        print(f"\n{expr_lemma}: {def_count} definitions")
        
        # Get all definitions for this expression
        cursor.execute('''
            SELECT d.id, d.content, d.order_num
            FROM articles a
            JOIN definitions d ON a.article_id = d.article_id
            WHERE a.lemma = ? AND a.word_class = 'EXPR'
            ORDER BY d.order_num, d.id
        ''', (expr_lemma,))
        
        definitions = cursor.fetchall()
        for i, (def_id, content, order_num) in enumerate(definitions, 1):
            print(f"  {i}. {content}")
    
    # Specific test for "på huset" if it exists
    cursor.execute('''
        SELECT COUNT(DISTINCT d.id)
        FROM articles a
        JOIN definitions d ON a.article_id = d.article_id
        WHERE a.lemma = 'på huset' AND a.word_class = 'EXPR'
    ''')
    
    pa_huset_count = cursor.fetchone()[0]
    if pa_huset_count > 1:
        print(f"\n✅ Test passed: 'på huset' has {pa_huset_count} definitions")
    elif pa_huset_count == 1:
        print("\n⚠️  Warning: 'på huset' only has 1 definition (expected multiple)")
    else:
        print("\n❌ Test failed: 'på huset' expression not found")
    
    conn.close()

def test_expression_display():
    """Test that the ordb script displays all definitions for expressions."""
    import subprocess
    
    # Run ordb for 'hus' and check if 'på huset' shows multiple definitions
    result = subprocess.run(['python3', 'ordb', 'hus'], 
                          capture_output=True, text=True)
    
    output = result.stdout
    
    # Check if both definitions appear
    def1_found = "på arbeidsplassen; internt" in output
    def2_found = "som blir betalt av en restaurant eller lignende" in output
    
    if def1_found and def2_found:
        print("\n✅ Display test passed: Both definitions of 'på huset' are shown")
    else:
        print("\n❌ Display test failed:")
        if not def1_found:
            print("   - Missing definition: 'på arbeidsplassen; internt'")
        if not def2_found:
            print("   - Missing definition: 'som blir betalt av en restaurant eller lignende'")
    
    # Check for duplicate examples
    example1_count = output.count("vi skal ta for oss forholdene her på huset")
    example2_count = output.count("vi håper vodkaen er på huset")
    
    if example1_count == 1 and example2_count == 1:
        print("✅ No duplicate examples found")
    else:
        print("❌ Duplicate examples detected:")
        if example1_count > 1:
            print(f"   - 'vi skal ta for oss forholdene her på huset' appears {example1_count} times")
        if example2_count > 1:
            print(f"   - 'vi håper vodkaen er på huset' appears {example2_count} times")

if __name__ == '__main__':
    print("Testing expressions with multiple definitions...")
    print("=" * 60)
    
    test_multiple_definitions_for_expressions()
    print("\n" + "=" * 60)
    test_expression_display()