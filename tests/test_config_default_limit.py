"""Test default limit configuration functionality."""
import unittest
import subprocess
import tempfile
import os
from pathlib import Path

class TestConfigDefaultLimit(unittest.TestCase):
    
    def setUp(self):
        """Set up test environment."""
        # Get absolute paths
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.search_script = os.path.join(project_root, 'ordb')
        self.db_path = os.path.join(project_root, 'articles.db')
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
        cmd = ['python', self.search_script] + list(args) + ['--db', self.db_path, query]
        # Set PYTHONPATH to parent directory so src.ordb can be found
        env = os.environ.copy()
        env['PYTHONPATH'] = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        result = subprocess.run(cmd, capture_output=True, text=True, env=env)
        return result.stdout, result.stderr, result.returncode
    
    def test_default_limit_from_config(self):
        """Test that default limit can be set from config file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create config with custom default limit
            config_content = """
[colors]
lemma = CYAN

[search]
character_replacement = True
default_limit = 5
"""
            self.create_config_file(config_content, temp_dir)
            
            # Run a search that would normally return many results
            stdout, stderr, returncode = self.run_search_in_dir(temp_dir, '%hus')  # Full-text search for 'hus'
            
            # Should show only 5 results due to config
            if 'Found' in stdout:
                # Extract number of results shown (count the separators)
                separator_count = stdout.count('────────────────────────────────────────')
                # Should be limited to 5 or fewer
                self.assertLessEqual(separator_count, 5, "Should respect config default_limit of 5")
    
    def test_command_line_overrides_config_limit(self):
        """Test that --limit flag overrides config default."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create config with default limit of 20
            config_content = """
[search]
default_limit = 20
"""
            self.create_config_file(config_content, temp_dir)
            
            # Run search with explicit --limit 3
            stdout, stderr, returncode = self.run_search_in_dir(temp_dir, '%hus', '--limit', '3')
            
            # Should show only 3 results despite config saying 20
            if 'Found' in stdout:
                separator_count = stdout.count('────────────────────────────────────────')
                self.assertLessEqual(separator_count, 3, "Should respect command line --limit of 3")
    
    def test_invalid_config_limit_uses_default(self):
        """Test that invalid config values fall back to default."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create config with invalid limit
            config_content = """
[search]
default_limit = not_a_number
"""
            self.create_config_file(config_content, temp_dir)
            
            # Run search - should not crash and should use default (50)
            stdout, stderr, returncode = self.run_search_in_dir(temp_dir, 'hus')
            
            # Should not crash (returncode should be 0)
            self.assertEqual(returncode, 0, f"Command failed with stderr: {stderr}")
            # Should not contain error messages
            self.assertNotIn('Error', stdout)
            if stdout:
                self.assertIn('search for', stdout.lower())
    
    def test_character_replacement_config_works(self):
        """Test that character replacement can be configured."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create config with character replacement disabled
            config_content = """
[search]
character_replacement = False
"""
            self.create_config_file(config_content, temp_dir)
            
            # Search with 'aa' - should NOT find 'gå' when replacement is disabled
            stdout, stderr, returncode = self.run_search_in_dir(temp_dir, 'gaa')
            
            # Should run without error
            self.assertEqual(returncode, 0, f"Command failed with stderr: {stderr}")
            if stdout:
                self.assertIn('search for', stdout.lower())
            
            # Note: This test is basic - testing the exact behavior would require
            # knowing specific words that exist with 'aa' vs 'å'

if __name__ == '__main__':
    unittest.main()