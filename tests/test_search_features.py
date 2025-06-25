#!/usr/bin/env python3
"""
Test script to demonstrate the new search features in the Norwegian Dictionary.
"""

import sys
import importlib.util

# Import the modular search library
spec = importlib.util.spec_from_file_location("search_modular", "./search-modular.py")
search_modular = importlib.util.module_from_spec(spec)
spec.loader.exec_module(search_modular)
NorwegianDictionary = search_modular.NorwegianDictionary
Colors = search_modular.Colors

def test_search_features():
    """Test all the new search syntax features."""
    
    print(f"{Colors.BOLD}{Colors.CYAN}Norwegian Dictionary - New Search Features Test{Colors.END}\n")
    
    dict_obj = NorwegianDictionary('articles.db')
    
    # Test cases with different search syntaxes
    test_cases = [
        ("ære@", "Prefix search - words starting with 'ære' (shortest first)"),
        ("@jazz", "Anywhere in term - words containing 'jazz' (shortest first)"), 
        ("%nasjonal", "Full-text search - all content containing 'nasjonal'"),
        ("gå", "Regular exact search - exact match for 'gå'"),
        ("jazzfe", "Fallback test - no exact match, falls back to prefix")
    ]
    
    for query, description in test_cases:
        print(f"{Colors.HEADER}Testing: {description}{Colors.END}")
        print(f"Query: {Colors.BOLD}{query}{Colors.END}")
        
        try:
            results = dict_obj.search(query, search_type='auto')
            print(f"Results found: {Colors.GREEN}{len(results)}{Colors.END}")
            
            if results:
                # Show first result
                search_type, clean_query, _ = dict_obj.parse_search_query(query)
                formatted = dict_obj.format_result(results[0], search_term=clean_query, 
                                                 show_examples=False, max_examples=1)
                
                # Show only the header and first definition
                lines = formatted.split('\n')
                header_lines = []
                in_definitions = False
                definition_count = 0
                
                for line in lines:
                    if not in_definitions:
                        header_lines.append(line)
                        if "Definitions:" in line:
                            in_definitions = True
                    else:
                        header_lines.append(line)
                        if line.strip().startswith("1."):
                            definition_count += 1
                        elif definition_count > 0 and line.strip() == "":
                            break
                
                print('\n'.join(header_lines[:15]))  # Limit output
                
        except Exception as e:
            print(f"{Colors.RED}Error: {e}{Colors.END}")
        
        print(f"{Colors.GRAY}{'-' * 60}{Colors.END}\n")

if __name__ == '__main__':
    test_search_features()