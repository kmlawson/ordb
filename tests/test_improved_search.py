#!/usr/bin/env python3
"""
Simple test to verify homonym number extraction from improved database.
"""

import sqlite3
import json

def extract_homonym_number(raw_data):
    """Extract homonym number from raw_data JSON."""
    if not raw_data:
        return None
    
    try:
        data = json.loads(raw_data)
        lemmas = data.get('lemmas', [])
        if lemmas and isinstance(lemmas, list):
            hgno = lemmas[0].get('hgno')
            return hgno if hgno and hgno > 1 else None
    except:
        return None

def test_stein_search():
    """Test search for stein entries with homonym numbers."""
    conn = sqlite3.connect('improved-articles.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT article_id, lemma, word_class, gender, etymology, raw_data
        FROM articles 
        WHERE lemma = ? COLLATE NOCASE
        ORDER BY article_id
    ''', ('stein',))
    
    results = cursor.fetchall()
    
    print(f"Found {len(results)} entries for 'stein':")
    print("=" * 60)
    
    for result in results:
        article_id, lemma, word_class, gender, etymology, raw_data = result
        homonym_num = extract_homonym_number(raw_data)
        
        display_lemma = lemma
        if homonym_num:
            display_lemma = f"{lemma} ({homonym_num})"
        
        print(f"📖 {display_lemma} [{word_class or 'unknown'}]")
        if gender:
            print(f"  Gender: {gender}")
        if etymology:
            print(f"  Etymology: {etymology}")
        print(f"  Article ID: {article_id}")
        print()
    
    conn.close()

if __name__ == '__main__':
    test_stein_search()