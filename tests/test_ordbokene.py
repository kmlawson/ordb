#!/usr/bin/env python3

import unittest
import re
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ordbokene import NorwegianDictExtractor

class TestSteinExtraction(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        """Set up test fixtures, load the cached HTML file"""
        cls.extractor = NorwegianDictExtractor()
        
        # Read the cached HTML file
        with open('stein_original.html', 'r', encoding='utf-8') as f:
            cls.html_content = f.read()
        
        # Extract markdown from the cached content
        cls.markdown = cls.extractor.parse_entry_content(cls.html_content)
    
    def test_has_proper_structure(self):
        """Test that the output has proper markdown structure"""
        # Check for proper markdown headers
        self.assertIn('# stein (1)', self.markdown, "Should contain main entry headers")
        self.assertIn('## Opphav', self.markdown, "Should contain section headers")
        self.assertIn('### 1.', self.markdown, "Should contain definition headers")
    
    def test_stein_1_opphav_section(self):
        """Test stein (1) has correct Opphav section"""
        lines = self.markdown.split('\n')
        stein_1_started = False
        opphav_found = False
        expected_opphav = "norrønt steinn; jamfør stein ( 2 II)"
        
        for i, line in enumerate(lines):
            if line.strip() == "# stein (1)":
                stein_1_started = True
            elif stein_1_started and line.strip() == "## Opphav":
                opphav_found = True
                # Check the next line for the expected content
                if i + 1 < len(lines):
                    opphav_content = lines[i + 1].strip()
                    self.assertEqual(opphav_content, expected_opphav, 
                                   f"Opphav content should be '{expected_opphav}'")
                break
            elif stein_1_started and line.startswith("# stein ("):
                # We've moved to the next entry without finding Opphav
                break
        
        self.assertTrue(opphav_found, "stein (1) should have an Opphav section")
    
    def test_stein_1_three_definitions(self):
        """Test stein (1) has exactly 3 definitions"""
        lines = self.markdown.split('\n')
        stein_1_started = False
        definition_count = 0
        
        for line in lines:
            if line.strip() == "# stein (1)":
                stein_1_started = True
            elif stein_1_started and line.startswith("# stein ("):
                # We've moved to the next entry
                break
            elif stein_1_started and line.startswith("### "):
                definition_count += 1
        
        self.assertEqual(definition_count, 3, "stein (1) should have exactly 3 definitions")
    
    def test_stein_1_fifteen_fixed_expressions(self):
        """Test stein (1) has exactly 15 fixed expressions"""
        lines = self.markdown.split('\n')
        stein_1_started = False
        faste_uttrykk_started = False
        expression_count = 0
        
        for line in lines:
            if line.strip() == "# stein (1)":
                stein_1_started = True
            elif stein_1_started and line.startswith("# stein ("):
                # We've moved to the next entry
                break
            elif stein_1_started and line.strip() == "## Faste uttrykk":
                faste_uttrykk_started = True
            elif faste_uttrykk_started and line.startswith("- **"):
                expression_count += 1
        
        self.assertEqual(expression_count, 15, "stein (1) should have exactly 15 fixed expressions")
    
    def test_stein_2_five_definitions(self):
        """Test stein (2) has exactly 5 definitions"""
        lines = self.markdown.split('\n')
        stein_2_started = False
        definition_count = 0
        
        for line in lines:
            if line.strip() == "# stein (2)":
                stein_2_started = True
            elif stein_2_started and line.startswith("# stein ("):
                # We've moved to the next entry
                break
            elif stein_2_started and line.startswith("### "):
                definition_count += 1
        
        self.assertEqual(definition_count, 5, "stein (2) should have exactly 5 definitions")
    
    def test_stein_2_no_fixed_expressions(self):
        """Test stein (2) has no fixed expressions section"""
        lines = self.markdown.split('\n')
        stein_2_started = False
        has_faste_uttrykk = False
        
        for line in lines:
            if line.strip() == "# stein (2)":
                stein_2_started = True
            elif stein_2_started and line.startswith("# stein ("):
                # We've moved to the next entry
                break
            elif stein_2_started and line.strip() == "## Faste uttrykk":
                has_faste_uttrykk = True
                break
        
        self.assertFalse(has_faste_uttrykk, "stein (2) should not have a Faste uttrykk section")
    
    def test_stein_3_one_definition_one_example(self):
        """Test stein (3) has exactly 1 definition and 1 example"""
        lines = self.markdown.split('\n')
        stein_3_started = False
        definition_count = 0
        example_count = 0
        
        for line in lines:
            if line.strip() == "# stein (3)":
                stein_3_started = True
            elif stein_3_started and line.startswith("# stein ("):
                # We've moved to the next entry
                break
            elif stein_3_started and line.startswith("### "):
                definition_count += 1
            elif stein_3_started and line.startswith("- "):
                example_count += 1
        
        self.assertEqual(definition_count, 1, "stein (3) should have exactly 1 definition")
        self.assertEqual(example_count, 1, "stein (3) should have exactly 1 example")
    
    def test_stein_4_two_definitions(self):
        """Test stein (4) has exactly 2 definitions"""
        lines = self.markdown.split('\n')
        stein_4_started = False
        definition_count = 0
        
        for line in lines:
            if line.strip() == "# stein (4)":
                stein_4_started = True
            elif stein_4_started and line.startswith("# stein ("):
                # We've moved to the next entry (shouldn't happen for stein 4)
                break
            elif stein_4_started and line.startswith("### "):
                definition_count += 1
        
        self.assertEqual(definition_count, 2, "stein (4) should have exactly 2 definitions")
    
    def test_all_entries_present(self):
        """Test that all 4 stein entries are present"""
        entries = re.findall(r'^# stein \((\d+)\)', self.markdown, re.MULTILINE)
        expected_entries = ['1', '2', '3', '4']
        self.assertEqual(entries, expected_entries, "Should have stein (1), (2), (3), and (4)")
    
    def test_grammar_information_present(self):
        """Test that grammar information is present for each entry"""
        # Check that each entry has grammar info
        for entry_num in [1, 2, 3, 4]:
            with self.subTest(entry=entry_num):
                pattern = rf'# stein \({entry_num}\)(.*?)(?=# stein \(\d+\)|$)'
                match = re.search(pattern, self.markdown, re.DOTALL)
                self.assertIsNotNone(match, f"Should find stein ({entry_num}) entry")
                
                entry_content = match.group(1)
                # Should have at least one grammar marker
                grammar_found = '*substantiv*' in entry_content or '*adjektiv*' in entry_content or '*adverb*' in entry_content or '*verb*' in entry_content
                self.assertTrue(grammar_found, f"stein ({entry_num}) should have grammar information")

if __name__ == '__main__':
    unittest.main()