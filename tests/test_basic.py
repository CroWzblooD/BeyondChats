"""
Basic tests for Reddit Persona Analyzer.
"""

import unittest
import sys
import os

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from utils import extract_username_from_url, clean_text, create_output_filename


class TestUtils(unittest.TestCase):
    """Test utility functions."""
    
    def test_extract_username_from_url(self):
        """Test username extraction from various URL formats."""
        test_cases = [
            ("https://www.reddit.com/user/kojied/", "kojied"),
            ("https://www.reddit.com/user/Hungry-Move-6603/", "Hungry-Move-6603"),
            ("https://reddit.com/user/testuser", "testuser"),
            ("https://www.reddit.com/u/simpleuser", "simpleuser"),
            ("https://reddit.com/u/another-user", "another-user"),
        ]
        
        for url, expected in test_cases:
            with self.subTest(url=url):
                result = extract_username_from_url(url)
                self.assertEqual(result, expected)
    
    def test_clean_text(self):
        """Test text cleaning functionality."""
        test_cases = [
            ("  Hello   World  ", "Hello World"),
            ("http://example.com", ""),
            ("**bold** text", "bold text"),
            ("*italic* text", "italic text"),
            ("[link](http://example.com)", "link"),
            ("Text with http://example.com link", "Text with link"),
        ]
        
        for input_text, expected in test_cases:
            with self.subTest(input_text=input_text):
                result = clean_text(input_text)
                self.assertEqual(result, expected)
    
    def test_create_output_filename(self):
        """Test output filename creation."""
        test_cases = [
            ("kojied", "kojied_persona.txt"),
            ("Hungry-Move-6603", "Hungry-Move-6603_persona.txt"),
            ("user@123", "user_123_persona.txt"),
            ("test.user", "test_user_persona.txt"),
        ]
        
        for username, expected in test_cases:
            with self.subTest(username=username):
                result = create_output_filename(username)
                self.assertEqual(result, expected)


if __name__ == '__main__':
    unittest.main() 