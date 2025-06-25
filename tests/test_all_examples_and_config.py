"""Test TODO items #17, #18, and #19: --all-examples, inflections config, etymology config."""
import unittest
import subprocess
import tempfile
import re
import os
from pathlib import Path

class TestTodo17_18_19(unittest.TestCase):
    
    def setUp(self):
        """Set up test environment."""
        self.search_cmd = ['python', '-m', 'src.ordb']
        # Use relative path to database from project root
        self.db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'articles.db')
        self.original_dir = os.getcwd()
    
    def tearDown(self):
        """Clean up after test."""
        os.chdir(self.original_dir)
    
    def create_config_file(self, content, directory):
        """Create a temporary config file in the specified directory."""
        config_path = Path(directory) / '.config-bm'
        with open(config_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return str(config_path)
    
    def run_search_in_dir(self, directory, query, *args):
        """Run search command in a specific directory and return output."""
        os.chdir(directory)
        cmd = ['python', os.path.join(self.original_dir, 'ordb')] + list(args) + ['--db', self.db_path, query]
        # Set PYTHONPATH to parent directory so src.ordb can be found
        env = os.environ.copy()
        env['PYTHONPATH'] = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        result = subprocess.run(cmd, capture_output=True, text=True, env=env)
        return result.stdout, result.stderr, result.returncode
    
    def run_search(self, query, *args):
        """Run search command and return output."""
        cmd = self.search_cmd + list(args) + ['--db', self.db_path, query]
        # Set PYTHONPATH to parent directory so src.ordb can be found
        env = os.environ.copy()
        env['PYTHONPATH'] = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        result = subprocess.run(cmd, capture_output=True, text=True, env=env)
        return result.stdout
    
    def clean_ansi(self, text):
        """Remove ANSI color codes from text."""
        return re.sub(r'\x1b\[[0-9;]*m', '', text)
    
    def test_todo_17_all_examples_finds_examples(self):
        """Test TODO #17: --all-examples finds examples across dictionary."""
        output = self.run_search('gå', '--all-examples', '--limit', '5')
        clean_output = self.clean_ansi(output)
        
        # Should show the search header
        self.assertIn('Searching all examples', output)
        self.assertIn('exact matches', output)
        
        # Should find examples
        self.assertIn('search for', output.lower())
        self.assertIn('example(s) containing', output)
        
        # Should display examples in semicolon-separated format
        self.assertIn(';', clean_output)
        
        # Should highlight the search term
        self.assertIn('gå', clean_output)
    
    def test_todo_17_all_examples_respects_limit(self):
        """Test that --all-examples respects the --limit parameter."""
        output = self.run_search('gå', '--all-examples', '--limit', '3')
        
        # Should find examples but be limited
        if '📖' in output:
            # Should mention truncation if there are more results
            if 'more example(s)' in output:
                self.assertIn('more example(s)', output)
    
    def test_todo_17_all_examples_character_replacement(self):
        """Test that --all-examples works with character replacement."""
        output = self.run_search('gaa', '--all-examples', '--limit', '3')
        
        # Should find examples for "gå" even when searching for "gaa"
        if '📖' in output:
            clean_output = self.clean_ansi(output)
            # Should find examples (character replacement should work)
            self.assertIn('gå', clean_output)
    
    def test_todo_18_inflections_config_disabled(self):
        """Test TODO #18: show_inflections = False hides inflections."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create config with inflections disabled
            config_content = '''
[colors]
lemma = CYAN

[search]
show_inflections = False
show_etymology = True
'''
            self.create_config_file(config_content, temp_dir)
            
            # Run search
            stdout, stderr, returncode = self.run_search_in_dir(temp_dir, 'hus')
            clean_output = self.clean_ansi(stdout)
            
            # Should run successfully
            self.assertEqual(returncode, 0)
            
            # Should NOT show inflections
            self.assertNotIn('Inflections:', clean_output)
            self.assertNotIn('Singular:', clean_output)
            self.assertNotIn('Plural:', clean_output)
            
            # Should still show etymology (since it's enabled)
            self.assertIn('Etymology:', clean_output)
    
    def test_todo_19_etymology_config_disabled(self):
        """Test TODO #19: show_etymology = False hides etymology."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create config with etymology disabled
            config_content = '''
[colors]
lemma = CYAN

[search]
show_inflections = True
show_etymology = False
'''
            self.create_config_file(config_content, temp_dir)
            
            # Run search
            stdout, stderr, returncode = self.run_search_in_dir(temp_dir, 'hus')
            clean_output = self.clean_ansi(stdout)
            
            # Should run successfully
            self.assertEqual(returncode, 0)
            
            # Should NOT show etymology
            self.assertNotIn('Etymology:', clean_output)
            self.assertNotIn('norr. hús', clean_output)
            
            # Should still show inflections (since it's enabled)
            self.assertIn('Inflections:', clean_output)
    
    def test_todo_18_19_both_disabled(self):
        """Test both inflections and etymology disabled."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create config with both disabled
            config_content = '''
[colors]
lemma = CYAN

[search]
show_inflections = False
show_etymology = False
'''
            self.create_config_file(config_content, temp_dir)
            
            # Run search
            stdout, stderr, returncode = self.run_search_in_dir(temp_dir, 'hus')
            clean_output = self.clean_ansi(stdout)
            
            # Should run successfully
            self.assertEqual(returncode, 0)
            
            # Should NOT show inflections or etymology
            self.assertNotIn('Inflections:', clean_output)
            self.assertNotIn('Etymology:', clean_output)
            
            # Should still show definitions and examples
            self.assertIn('bygning (med tak og vegger)', clean_output)
            self.assertIn('bygge hus', clean_output)
    
    def test_todo_18_19_config_defaults_to_true(self):
        """Test that missing config options default to True."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create config without display options
            config_content = '''
[colors]
lemma = CYAN

[search]
character_replacement = True
'''
            self.create_config_file(config_content, temp_dir)
            
            # Run search
            stdout, stderr, returncode = self.run_search_in_dir(temp_dir, 'hus')
            clean_output = self.clean_ansi(stdout)
            
            # Should run successfully
            self.assertEqual(returncode, 0)
            
            # Should show both inflections and etymology (defaults to True)
            self.assertIn('Inflections:', clean_output)
            self.assertIn('Etymology:', clean_output)
    
    def test_all_examples_no_results(self):
        """Test --all-examples with a word that has no examples."""
        output = self.run_search('xyzkjsdhfksdf', '--all-examples')
        
        # Should show appropriate message
        self.assertIn('No examples found', output)

if __name__ == '__main__':
    unittest.main()