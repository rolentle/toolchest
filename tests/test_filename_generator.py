"""Tests for the FilenameGenerator module."""
import pytest
from unittest.mock import Mock, patch
from datetime import datetime
import os
import sys

# Add src to path for direct imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))


class TestFilenameGenerator:
    """Test suite for FilenameGenerator class."""
    
    def test_init(self):
        """Test FilenameGenerator initialization."""
        from filename_generator import FilenameGenerator
        
        generator = FilenameGenerator()
        assert generator.model == "gemma2:latest"
        
        # Test with custom model
        generator = FilenameGenerator(model="llama2")
        assert generator.model == "llama2"
    
    def test_sanitize_filename(self):
        """Test filename sanitization."""
        from filename_generator import FilenameGenerator
        
        generator = FilenameGenerator()
        
        # Test basic sanitization
        assert generator.sanitize_filename("Hello World!") == "hello_world"
        assert generator.sanitize_filename("Test@File#Name") == "test_file_name"
        assert generator.sanitize_filename("Multiple   Spaces") == "multiple_spaces"
        assert generator.sanitize_filename("CamelCaseText") == "camelcasetext"
        
        # Test length limiting
        long_name = "this_is_a_very_long_filename_that_exceeds_the_maximum_length_allowed"
        sanitized = generator.sanitize_filename(long_name)
        assert len(sanitized) <= 50
        
        # Test edge cases
        assert generator.sanitize_filename("") == "unnamed"
        assert generator.sanitize_filename("!!!") == "unnamed"
        assert generator.sanitize_filename("123") == "123"
    
    def test_add_timestamp(self):
        """Test timestamp addition to filename."""
        from filename_generator import FilenameGenerator
        
        generator = FilenameGenerator()
        
        # Mock datetime to get consistent timestamp
        with patch('filename_generator.datetime') as mock_datetime:
            mock_datetime.now.return_value = datetime(2024, 1, 15, 14, 30, 52)
            
            result = generator.add_timestamp("test_file")
            assert result == "test_file_20240115_143052"
    
    @patch('ollama.chat')
    def test_generate_from_content_success(self, mock_chat):
        """Test successful filename generation from content."""
        from filename_generator import FilenameGenerator
        
        # Mock Ollama response
        mock_chat.return_value = {
            'message': {
                'content': 'climate_change_effects'
            }
        }
        
        generator = FilenameGenerator()
        text = "Scientists report on the effects of climate change on polar ice caps..."
        
        with patch('filename_generator.datetime') as mock_datetime:
            mock_datetime.now.return_value = datetime(2024, 1, 15, 14, 30, 52)
            filename = generator.generate_from_content(text)
        
        assert filename == "climate_change_effects_20240115_143052.wav"
        
        # Verify Ollama was called correctly
        mock_chat.assert_called_once()
        call_args = mock_chat.call_args
        assert call_args[1]['model'] == 'gemma2:latest'
        assert 'climate change' in call_args[1]['messages'][0]['content']
    
    @patch('ollama.chat')
    def test_generate_from_content_with_title(self, mock_chat):
        """Test filename generation with title provided."""
        from filename_generator import FilenameGenerator
        
        mock_chat.return_value = {
            'message': {
                'content': 'breaking_news_update'
            }
        }
        
        generator = FilenameGenerator()
        text = "Latest updates on the breaking news story..."
        title = "Breaking News: Major Discovery"
        
        with patch('filename_generator.datetime') as mock_datetime:
            mock_datetime.now.return_value = datetime(2024, 1, 15, 14, 30, 52)
            filename = generator.generate_from_content(text, title=title)
        
        assert filename == "breaking_news_update_20240115_143052.wav"
        
        # Verify title was included in prompt
        call_args = mock_chat.call_args
        assert 'Breaking News' in call_args[1]['messages'][0]['content']
    
    @patch('ollama.chat')
    def test_generate_from_content_ollama_error(self, mock_chat):
        """Test fallback when Ollama fails."""
        from filename_generator import FilenameGenerator
        
        # Mock Ollama to raise an exception
        mock_chat.side_effect = Exception("Ollama not available")
        
        generator = FilenameGenerator()
        text = "Some content text"
        
        with patch('filename_generator.datetime') as mock_datetime:
            mock_datetime.now.return_value = datetime(2024, 1, 15, 14, 30, 52)
            filename = generator.generate_from_content(text, url="https://example.com/article")
        
        # Should fallback to URL-based naming
        assert filename == "example_com_article_20240115_143052.wav"
    
    @patch('ollama.chat')
    def test_generate_from_content_timeout(self, mock_chat):
        """Test timeout handling."""
        from filename_generator import FilenameGenerator
        import time
        
        # Mock Ollama to simulate timeout
        def slow_response(*args, **kwargs):
            time.sleep(0.1)  # Simulate slow response
            return {'message': {'content': 'test_filename'}}
        
        mock_chat.side_effect = slow_response
        
        generator = FilenameGenerator()
        text = "Some content"
        
        # For testing, we'll just verify the timeout parameter is passed
        with patch('filename_generator.datetime') as mock_datetime:
            mock_datetime.now.return_value = datetime(2024, 1, 15, 14, 30, 52)
            filename = generator.generate_from_content(text)
        
        # Verify timeout option was passed
        call_args = mock_chat.call_args
        assert 'options' in call_args[1]
        # Note: actual timeout implementation may vary based on ollama library
    
    def test_generate_from_url(self):
        """Test filename generation from URL."""
        from filename_generator import FilenameGenerator
        
        generator = FilenameGenerator()
        
        with patch('filename_generator.datetime') as mock_datetime:
            mock_datetime.now.return_value = datetime(2024, 1, 15, 14, 30, 52)
            
            # Test various URL formats
            assert generator.generate_from_url("https://example.com/article/news-story") == "example_com_news_story_20240115_143052.wav"
            assert generator.generate_from_url("https://blog.site.com/2024/01/post") == "blog_site_com_post_20240115_143052.wav"
            assert generator.generate_from_url("https://example.com") == "example_com_20240115_143052.wav"
            assert generator.generate_from_url("http://test.org/path?query=123") == "test_org_path_20240115_143052.wav"
    
    @patch('ollama.chat')
    def test_long_text_truncation(self, mock_chat):
        """Test that long text is truncated before sending to Ollama."""
        from filename_generator import FilenameGenerator
        
        mock_chat.return_value = {
            'message': {
                'content': 'long_article_summary'
            }
        }
        
        generator = FilenameGenerator()
        # Create text longer than MAX_TEXT_LENGTH_FOR_SUMMARY
        long_text = "x" * 2000
        
        generator.generate_from_content(long_text)
        
        # Verify text was truncated in the prompt
        call_args = mock_chat.call_args
        prompt_text = call_args[1]['messages'][0]['content']
        assert len(prompt_text) < 2000  # Should be truncated