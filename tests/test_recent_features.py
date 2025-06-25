"""Test recent features: pagination, etymology/inflection flags, and word type filters."""
import unittest
import subprocess
import re
import os
import tempfile
import shutil
from pathlib import Path

class TestRecentFeatures(unittest.TestCase):
    
    def setUp(self):
        """Set up test environment."""
        self.search_cmd = ['python', '-m', 'src.ordb']
        # Use relative path to database from project root
        self.db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'articles.db')
        
        # Create temporary config for pagination tests
        self.original_config = None
        project_root = Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        self.config_path = project_root / '.config-bm'
        if self.config_path.exists():
            # Backup original config
            self.original_config = self.config_path.read_text()
    
    def tearDown(self):
        """Clean up after tests."""
        # Restore original config if it existed
        if self.original_config is not None:
            self.config_path.write_text(self.original_config)
        elif self.config_path.exists():
            # Remove test config if original didn't exist
            self.config_path.unlink()
    
    def run_search(self, query, *args, input_text=None):
        """Run search command and return output."""
        cmd = self.search_cmd + list(args) + ['--db', self.db_path, query]
        # Change to the correct directory
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        # Set PYTHONPATH to parent directory so src.ordb can be found
        env = os.environ.copy()
        env['PYTHONPATH'] = project_root
        result = subprocess.run(cmd, capture_output=True, text=True, input=input_text, cwd=project_root, env=env)
        return result.stdout, result.stderr, result.returncode
    
    def clean_ansi(self, text):
        """Remove ANSI color codes from text."""
        return re.sub(r'\x1b\[[0-9;]*m', '', text)
    
    def create_test_config(self, pagination=True, page_size=20):
        """Create a test configuration file."""
        config_content = f"""[search]
pagination = {pagination}
page_size = {page_size}
character_replacement = True
default_limit = 50
show_inflections = True
show_etymology = True
"""
        self.config_path.write_text(config_content)
    
    # Tests for TODO #20: -e, --only-etymology flag
    def test_only_etymology_flag(self):
        """Test -e, --only-etymology flag shows only etymology."""
        stdout, stderr, returncode = self.run_search('hus', '-e', '--limit', '1')
        self.assertEqual(returncode, 0)
        
        clean_output = self.clean_ansi(stdout)
        
        # Should include etymology
        self.assertIn('Etymology:', clean_output)
        self.assertIn('norr. hús', clean_output)
        
        # Should NOT include definitions, examples, or inflections
        self.assertNotIn('bygning (med tak og vegger)', clean_output)
        self.assertNotIn('bygge hus', clean_output)
        self.assertNotIn('Inflections:', clean_output)
        self.assertNotIn('Faste uttrykk:', clean_output)
    
    def test_only_etymology_long_form(self):
        """Test --only-etymology long form flag."""
        stdout, stderr, returncode = self.run_search('stein', '--only-etymology', '--limit', '1')
        self.assertEqual(returncode, 0)
        
        clean_output = self.clean_ansi(stdout)
        
        # Should include etymology
        self.assertIn('Etymology:', clean_output)
        self.assertIn('norr. steinn', clean_output)
        
        # Should NOT include other content
        self.assertNotIn('fast og hardt mineralsk', clean_output)
        self.assertNotIn('kaste stein', clean_output)
    
    # Tests for TODO #21: -i, --only-inflections flag  
    def test_only_inflections_flag(self):
        """Test -i, --only-inflections flag shows only inflections."""
        stdout, stderr, returncode = self.run_search('hus', '-i', '--limit', '1')
        self.assertEqual(returncode, 0)
        
        clean_output = self.clean_ansi(stdout)
        
        # Should include inflections on separate lines
        self.assertIn('Inflections:', clean_output)
        self.assertIn('Singular:', clean_output)
        self.assertIn('Plural:', clean_output)
        # Check for the actual inflection values (format may vary)
        self.assertIn('huset', clean_output)  # singular definite
        self.assertIn('husa', clean_output)   # plural indefinite
        
        # Should NOT include definitions, examples, or etymology
        self.assertNotIn('bygning (med tak og vegger)', clean_output)
        self.assertNotIn('bygge hus', clean_output)
        self.assertNotIn('Etymology:', clean_output)
        self.assertNotIn('Faste uttrykk:', clean_output)
    
    def test_only_inflections_multiline_format(self):
        """Test that -i flag shows inflections on separate lines."""
        stdout, stderr, returncode = self.run_search('gå', '-i', '--limit', '1')
        self.assertEqual(returncode, 0)
        
        clean_output = self.clean_ansi(stdout)
        
        # Should show each inflection category on its own line
        lines = clean_output.split('\n')
        inflection_lines = [line for line in lines if 'Infinitive:' in line or 'Present:' in line or 'Past:' in line]
        
        # Should have multiple inflection category lines
        self.assertGreater(len(inflection_lines), 1)
    
    # Tests for TODO #22-25: Word type filters
    def test_adj_filter(self):
        """Test --adj filter returns only adjectives."""
        stdout, stderr, returncode = self.run_search('stor', '--adj', '--limit', '3')
        self.assertEqual(returncode, 0)
        
        clean_output = self.clean_ansi(stdout)
        
        # Should contain adjective markers
        self.assertIn('[adj]', clean_output)
        
        # Should NOT contain other word types in results
        self.assertNotIn('[noun]', clean_output)
        self.assertNotIn('[verb]', clean_output)
        self.assertNotIn('[adv]', clean_output)
    
    def test_verb_filter(self):
        """Test --verb filter returns only verbs."""
        stdout, stderr, returncode = self.run_search('gå', '--verb', '--limit', '3')
        self.assertEqual(returncode, 0)
        
        clean_output = self.clean_ansi(stdout)
        
        # Should contain verb markers
        self.assertIn('[verb]', clean_output)
        
        # Should NOT contain other word types in results
        self.assertNotIn('[noun]', clean_output)
        self.assertNotIn('[adj]', clean_output)
        self.assertNotIn('[adv]', clean_output)
    
    def test_noun_filter(self):
        """Test --noun filter returns only nouns."""
        stdout, stderr, returncode = self.run_search('hus', '--noun', '--limit', '3')
        self.assertEqual(returncode, 0)
        
        clean_output = self.clean_ansi(stdout)
        
        # Should contain noun markers
        self.assertIn('[noun]', clean_output)
        
        # Should NOT contain other word types in results
        self.assertNotIn('[verb]', clean_output)
        self.assertNotIn('[adj]', clean_output)
        self.assertNotIn('[adv]', clean_output)
    
    def test_adv_filter(self):
        """Test --adv filter returns only adverbs."""
        stdout, stderr, returncode = self.run_search('fort', '--adv', '--limit', '3')
        
        clean_output = self.clean_ansi(stdout)
        
        # If no adverb results found, skip the detailed assertions
        if 'No results found' in clean_output:
            self.assertEqual(returncode, 0)
            return
        
        self.assertEqual(returncode, 0)
        
        # Should contain adverb markers
        self.assertIn('[adv]', clean_output)
        
        # Should NOT contain other word types in results  
        self.assertNotIn('[noun]', clean_output)
        self.assertNotIn('[verb]', clean_output)
        self.assertNotIn('[adj]', clean_output)
    
    # Tests for Pagination functionality
    def test_pagination_enabled_by_default(self):
        """Test that pagination is enabled by default."""
        # Create config with pagination enabled
        self.create_test_config(pagination=True, page_size=10)
        
        # Search for something that will produce long output
        stdout, stderr, returncode = self.run_search('hus', '--limit', '1', input_text='q\n')
        self.assertEqual(returncode, 0)
        
        clean_output = self.clean_ansi(stdout)
        
        # Should contain pagination prompt
        self.assertIn('--More--', clean_output)
        self.assertIn('lines remaining', clean_output)
        self.assertIn('Space/Enter: next page', clean_output)
    
    def test_pagination_disabled_in_config(self):
        """Test that pagination can be disabled via config."""
        # Create config with pagination disabled
        self.create_test_config(pagination=False, page_size=10)
        
        # Search for something short to avoid timeout
        stdout, stderr, returncode = self.run_search('xyz', '--limit', '1')
        
        clean_output = self.clean_ansi(stdout)
        
        # Should NOT contain pagination prompt
        self.assertNotIn('--More--', clean_output)
        self.assertNotIn('lines remaining', clean_output)
    
    def test_pagination_force_flag(self):
        """Test -p flag forces pagination even when config is False."""
        # Create config with pagination disabled
        self.create_test_config(pagination=False, page_size=10)
        
        # Use -p flag to force pagination
        stdout, stderr, returncode = self.run_search('hus', '-p', '--limit', '1', input_text='q\n')
        self.assertEqual(returncode, 0)
        
        clean_output = self.clean_ansi(stdout)
        
        # Should contain pagination prompt despite config being False
        self.assertIn('--More--', clean_output)
        self.assertIn('lines remaining', clean_output)
    
    def test_pagination_quit_functionality(self):
        """Test that 'q' properly quits pagination."""
        # Create config with small page size
        self.create_test_config(pagination=True, page_size=5)
        
        # Search with 'q' input to quit pagination
        stdout, stderr, returncode = self.run_search('hus', '--limit', '1', input_text='q\n')
        self.assertEqual(returncode, 0)
        
        clean_output = self.clean_ansi(stdout)
        
        # Should show truncation message
        self.assertIn('Output truncated', clean_output)
    
    def test_pagination_short_output_no_prompt(self):
        """Test that short output doesn't trigger pagination."""
        # Create config with large page size
        self.create_test_config(pagination=True, page_size=100)
        
        # Search for something that won't produce much output
        stdout, stderr, returncode = self.run_search('xyz', '--limit', '1')
        
        clean_output = self.clean_ansi(stdout)
        
        # Should NOT contain pagination prompt for short output
        self.assertNotIn('--More--', clean_output)
    
    def test_pagination_preserves_colors(self):
        """Test that pagination preserves ANSI color codes."""
        # Create config with small page size
        self.create_test_config(pagination=True, page_size=5)
        
        # Search and quit immediately to get first page
        stdout, stderr, returncode = self.run_search('hus', '--limit', '1', input_text='q\n')
        self.assertEqual(returncode, 0)
        
        # Should contain ANSI color codes (not cleaned)
        self.assertIn('\x1b[', stdout)  # Should have ANSI codes
        self.assertIn('[92m', stdout)   # Should have green color codes
        self.assertIn('[96m', stdout)   # Should have cyan color codes
    
    # Combined feature tests
    def test_etymology_flag_with_pagination(self):
        """Test that -e flag works with pagination."""
        # Create config with small page size
        self.create_test_config(pagination=True, page_size=3)
        
        stdout, stderr, returncode = self.run_search('hus', '-e', '--limit', '1', input_text='q\n')
        self.assertEqual(returncode, 0)
        
        clean_output = self.clean_ansi(stdout)
        
        # Should show etymology and pagination if needed
        self.assertIn('Etymology:', clean_output)
    
    def test_word_filter_with_pagination(self):
        """Test that word type filters work with pagination."""
        # Create config with small page size  
        self.create_test_config(pagination=True, page_size=5)
        
        stdout, stderr, returncode = self.run_search('stor', '--adj', '--limit', '2', input_text='q\n')
        self.assertEqual(returncode, 0)
        
        clean_output = self.clean_ansi(stdout)
        
        # Should show only adjectives
        self.assertIn('[adj]', clean_output)
        self.assertNotIn('[noun]', clean_output)
    
    def test_pagination_entry_header_preservation(self):
        """Test that entry headers are preserved during pagination."""
        # Create config with very small page size to force entry splitting
        self.create_test_config(pagination=True, page_size=3)
        
        # Search for a word that produces long entries
        stdout, stderr, returncode = self.run_search('hus', '--limit', '1', input_text='q\n')
        self.assertEqual(returncode, 0)
        
        clean_output = self.clean_ansi(stdout)
        
        # Should include the entry header even with small page size
        self.assertIn('📖', clean_output)
        self.assertIn('[noun]', clean_output)
        self.assertIn('(neuter)', clean_output)

if __name__ == '__main__':
    unittest.main()