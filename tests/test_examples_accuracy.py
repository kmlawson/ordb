#!/usr/bin/env python3

import unittest
import re
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ordbokene import NorwegianDictExtractor

class TestExamplesAccuracy(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        """Set up test fixtures, load examples.md and initialize extractor"""
        cls.extractor = NorwegianDictExtractor()
        cls.test_data = cls._load_examples_data()
    
    @classmethod
    def _load_examples_data(cls):
        """Load and parse examples.md file"""
        examples_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'examples.md')
        test_data = []
        
        with open(examples_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Skip header line
        for line in lines[1:]:
            line = line.strip()
            if not line:
                continue
            
            parts = line.split()
            if len(parts) < 2:
                continue
                
            url = parts[0]
            
            # Handle error case
            if '- should return error' in line:
                test_data.append({
                    'url': url,
                    'should_error': True
                })
            else:
                # Parse normal test data
                if len(parts) >= 6:
                    test_data.append({
                        'url': url,
                        'entries': int(parts[1]),
                        'definitions': int(parts[2]),
                        'examples': int(parts[3]),
                        'expressions': int(parts[4]),
                        'expression_examples': int(parts[5]),
                        'should_error': False
                    })
        
        return test_data
    
    def _count_entries(self, markdown):
        """Count the number of dictionary entries"""
        # Find all main headers that represent entries
        entry_pattern = r'^# [^#\n]+'
        entries = re.findall(entry_pattern, markdown, re.MULTILINE)
        return len(entries)
    
    def _count_definitions(self, markdown):
        """Count total number of definitions across all entries"""
        # Find all definition headers (### followed by number)
        definition_pattern = r'^### \d+'
        definitions = re.findall(definition_pattern, markdown, re.MULTILINE)
        return len(definitions)
    
    def _count_examples(self, markdown):
        """Count examples from definitions (excluding fixed expressions)"""
        lines = markdown.split('\n')
        example_count = 0
        in_faste_uttrykk = False
        in_definitions = False
        
        for line in lines:
            line = line.strip()
            
            # Track if we're in a Faste uttrykk section
            if line == "## Faste uttrykk":
                in_faste_uttrykk = True
                in_definitions = False
                continue
            elif line.startswith("## ") and line != "## Faste uttrykk":
                in_faste_uttrykk = False
                in_definitions = True
                continue
            elif line.startswith("# "):
                in_faste_uttrykk = False
                in_definitions = False
                continue
            elif line.startswith("### "):
                in_definitions = True
                continue
            
            # Count examples only when in definitions (not in Faste uttrykk)
            if in_definitions and not in_faste_uttrykk and line.startswith("- ") and not line.startswith("- **"):
                example_count += 1
        
        return example_count
    
    def _count_fixed_expressions(self, markdown):
        """Count the number of fixed expressions"""
        lines = markdown.split('\n')
        expression_count = 0
        in_faste_uttrykk = False
        
        for line in lines:
            line = line.strip()
            
            if line == "## Faste uttrykk":
                in_faste_uttrykk = True
                continue
            elif line.startswith("## ") and line != "## Faste uttrykk":
                in_faste_uttrykk = False
                continue
            elif line.startswith("# "):
                in_faste_uttrykk = False
                continue
            
            # Count fixed expressions (bold items in Faste uttrykk section)
            if in_faste_uttrykk and line.startswith("- **"):
                expression_count += 1
        
        return expression_count
    
    def _count_expression_examples(self, markdown):
        """Count examples from fixed expressions (italicized text in expressions)"""
        lines = markdown.split('\n')
        example_count = 0
        in_faste_uttrykk = False
        
        for line in lines:
            line = line.strip()
            
            if line == "## Faste uttrykk":
                in_faste_uttrykk = True
                continue
            elif line.startswith("## ") and line != "## Faste uttrykk":
                in_faste_uttrykk = False
                continue
            elif line.startswith("# "):
                in_faste_uttrykk = False
                continue
            
            # Count italicized examples within fixed expressions
            if in_faste_uttrykk and line.startswith("- **"):
                # Count _text_ patterns (italicized examples) in the expression line
                italic_examples = re.findall(r'_([^_]+)_', line)
                example_count += len(italic_examples)
        
        return example_count

def create_test_method(test_case):
    """Create a test method for a specific test case"""
    def test_method(self):
        if test_case['should_error']:
            # Test that error URLs return None or contain error content
            result = self.extractor.fetch_page(test_case['url'])
            if result is not None:
                # Check if the result contains error indicators
                has_error = ('404 Not Found' in result or 
                           '500 Internal Server Error' in result or
                           'NuxtError' in result)
                self.assertTrue(has_error, f"URL {test_case['url']} should return error content")
        else:
            # Fetch and parse the page
            html_content = self.extractor.fetch_page(test_case['url'])
            self.assertIsNotNone(html_content, f"Failed to fetch {test_case['url']}")
            
            markdown = self.extractor.parse_entry_content(html_content)
            self.assertIsNotNone(markdown, f"Failed to parse {test_case['url']}")
            
            # Count actual values
            actual_entries = self._count_entries(markdown)
            actual_definitions = self._count_definitions(markdown)
            actual_examples = self._count_examples(markdown)
            actual_expressions = self._count_fixed_expressions(markdown)
            actual_expression_examples = self._count_expression_examples(markdown)
            
            # Assert expected values
            self.assertEqual(actual_entries, test_case['entries'], 
                           f"URL {test_case['url']}: Expected {test_case['entries']} entries, got {actual_entries}")
            self.assertEqual(actual_definitions, test_case['definitions'],
                           f"URL {test_case['url']}: Expected {test_case['definitions']} definitions, got {actual_definitions}")
            self.assertEqual(actual_examples, test_case['examples'],
                           f"URL {test_case['url']}: Expected {test_case['examples']} examples, got {actual_examples}")
            self.assertEqual(actual_expressions, test_case['expressions'],
                           f"URL {test_case['url']}: Expected {test_case['expressions']} expressions, got {actual_expressions}")
            self.assertEqual(actual_expression_examples, test_case['expression_examples'],
                           f"URL {test_case['url']}: Expected {test_case['expression_examples']} expression examples, got {actual_expression_examples}")
    
    return test_method

# Dynamically add test methods for each URL in examples.md
def load_tests(loader, tests, pattern):
    """Dynamically generate test cases from examples.md"""
    suite = unittest.TestSuite()
    
    # Load test data
    test_data = TestExamplesAccuracy._load_examples_data()
    
    # Create test methods for each URL
    for i, test_case in enumerate(test_data):
        test_name = f"test_url_{i+1}_{test_case['url'].split('/')[-1]}"
        test_method = create_test_method(test_case)
        test_method.__name__ = test_name
        setattr(TestExamplesAccuracy, test_name, test_method)
    
    # Load the dynamically created test class
    suite.addTests(loader.loadTestsFromTestCase(TestExamplesAccuracy))
    return suite

if __name__ == '__main__':
    unittest.main()