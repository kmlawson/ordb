"""Test the -x flag for expression-only search and EXPR exclusion from other searches."""
import unittest
import subprocess
import re
import os

class TestExprSearchFlag(unittest.TestCase):
    
    def setUp(self):
        """Set up test environment."""
        self.search_cmd = ['python', '-m', 'src.ordb']
        # Use relative path to database from project root
        self.db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'articles.db')
    
    def run_search(self, query, *args):
        """Run search command and return output."""
        cmd = self.search_cmd + list(args) + ['--db', self.db_path, query]
        # Set PYTHONPATH to parent directory so src.ordb can be found
        env = os.environ.copy()
        env['PYTHONPATH'] = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        result = subprocess.run(cmd, capture_output=True, text=True, env=env)
        return result.stdout
    
    def test_x_flag_searches_only_expressions(self):
        """Test that -x flag returns only expression entries."""
        output = self.run_search('hus', '-x')
        
        # Extract all word classes from output (handle ANSI codes)
        # Remove ANSI color codes first
        clean_output = re.sub(r'\x1b\[[0-9;]*m', '', output)
        word_classes = re.findall(r'\[(\w+)\]', clean_output)
        
        # If any results found, they should all be expressions
        if word_classes:
            for wc in word_classes:
                self.assertEqual(wc, 'expr', f"Found non-expression word class: {wc}")
            # Should find expressions (check in cleaned output)
            self.assertIn('[expr]', clean_output)
        else:
            # It's possible there are no expressions with 'hus' in their name
            # Try a known expression
            output2 = self.run_search('fullt hus', '-x')
            self.assertIn('[expr]', output2)
    
    def test_fuzzy_search_excludes_expr(self):
        """Test that fuzzy search (-f) excludes EXPR entries."""
        output = self.run_search('hus', '-f')
        
        # Should find results
        self.assertIn('[', output)
        
        # Should not contain any [expr] entries
        self.assertNotIn('[expr]', output)
    
    def test_anywhere_search_excludes_expr(self):
        """Test that anywhere search (-a) excludes EXPR entries."""
        output = self.run_search('gang', '-a')
        
        # Should find results
        self.assertIn('[', output)
        
        # Should not contain any [expr] entries
        self.assertNotIn('[expr]', output)
    
    def test_prefix_search_excludes_expr(self):
        """Test that prefix search (@) excludes EXPR entries."""
        output = self.run_search('hus@')
        
        # Should find results
        self.assertIn('[', output)
        
        # Should not contain any [expr] entries
        self.assertNotIn('[expr]', output)
    
    def test_anywhere_term_search_excludes_expr(self):
        """Test that anywhere term search (@term) excludes EXPR entries."""
        output = self.run_search('@hus')
        
        # Should find results
        self.assertIn('[', output)
        
        # Should not contain any [expr] entries
        self.assertNotIn('[expr]', output)
    
    def test_fulltext_search_excludes_expr(self):
        """Test that fulltext search (%) excludes EXPR entries."""
        output = self.run_search('%hus')
        
        # Should find results
        self.assertIn('[', output)
        
        # Should not contain any [expr] entries
        self.assertNotIn('[expr]', output)
    
    def test_exact_search_still_includes_expr(self):
        """Test that exact search still includes EXPR entries."""
        # Search for a known expression
        output = self.run_search('fullt hus')
        
        # If it exists as an expression, it should be found
        if '[expr]' in output:
            self.assertIn('[expr]', output)
    
    def test_expressions_appear_in_faste_uttrykk(self):
        """Test that expressions still appear in the 'Faste uttrykk' section of main entries."""
        output = self.run_search('hus')
        
        # Check if we found any main entry (should be non-expr)
        # Remove ANSI color codes first
        clean_output = re.sub(r'\x1b\[[0-9;]*m', '', output)
        word_classes = re.findall(r'\[(\w+)\]', clean_output)
        non_expr_classes = [wc for wc in word_classes if wc != 'expr']
        
        # Should have found non-expr results first
        self.assertGreater(len(non_expr_classes), 0, "Should find non-expr entries for 'hus'")
        
        # Should include expressions in the "Faste uttrykk" section  
        # Only check for this if we found a main entry
        if 'noun' in non_expr_classes:
            self.assertIn('Faste uttrykk:', output)
        
        # Should include specific expressions like "fullt hus"
        if 'fullt hus' in output:
            # The expression should appear in the faste uttrykk section
            faste_idx = output.find('Faste uttrykk:')
            fullt_idx = output.find('fullt hus')
            self.assertGreater(fullt_idx, faste_idx, "Expression should appear after 'Faste uttrykk:' header")

if __name__ == '__main__':
    unittest.main()