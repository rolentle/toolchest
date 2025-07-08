#!/usr/bin/env python3
"""
Integration tests for URL to WAV conversion functionality.
"""
import os
import tempfile
import unittest
from unittest.mock import patch, Mock
import numpy as np
from src import url_to_wav


class TestURLToWavIntegration(unittest.TestCase):
    """Integration tests that test the full pipeline with minimal mocking."""
    
    @patch('src.url_to_wav.TTSEngine')
    @patch('requests.Session.get')
    def test_integration_full_pipeline(self, mock_get, mock_tts_engine_class):
        """Test the full pipeline from URL to WAV file."""
        # Mock the HTTP response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = """
        <html>
        <head><title>Test Page</title></head>
        <body>
            <h1>Welcome to Test Page</h1>
            <p>This is a paragraph of text that should be extracted.</p>
            <p>This is another paragraph with <strong>bold text</strong>.</p>
            <img src="test.jpg" alt="Test image description">
            <script>console.log('this should be ignored');</script>
            <style>body { color: red; }</style>
        </body>
        </html>
        """
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        # Mock TTS engine
        mock_engine = mock_tts_engine_class.return_value
        mock_engine.sample_rate = 24000
        mock_engine.get_audio_frames.return_value = [
            np.random.rand(24000).astype(np.float32)  # 1 second of audio
        ]
        
        # Test with temporary file
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp_file:
            output_path = tmp_file.name
            
        try:
            result = url_to_wav.convert_url_to_wav(
                url="https://example.com/test",
                output_path=output_path,
                verbose=True
            )
            
            self.assertTrue(result)
            self.assertTrue(os.path.exists(output_path))
            
            # Verify text extraction
            mock_engine.generate_audio.assert_called_once()
            call_args = mock_engine.generate_audio.call_args[0]
            extracted_text = call_args[0]
            
            # Check that extracted text contains expected content
            self.assertIn("Welcome to Test Page", extracted_text)
            self.assertIn("This is a paragraph of text that should be extracted.", extracted_text)
            self.assertIn("This is another paragraph with bold text", extracted_text)
            self.assertIn("[Image: Test image description]", extracted_text)
            
            # Check that unwanted content is not present
            self.assertNotIn("console.log", extracted_text)
            self.assertNotIn("color: red", extracted_text)
            
        finally:
            if os.path.exists(output_path):
                os.unlink(output_path)
    
    @patch('src.url_to_wav.TTSEngine')
    @patch('requests.Session.get')
    def test_integration_empty_html(self, mock_get, mock_tts_engine_class):
        """Test handling of empty or minimal HTML."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = "<html><body></body></html>"
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        result = url_to_wav.convert_url_to_wav(
            url="https://example.com/empty",
            output_path="output.wav"
        )
        
        self.assertFalse(result)
        # TTS engine should not be initialized for empty content
        mock_tts_engine_class.assert_not_called()
    
    @patch('requests.Session.get')
    def test_integration_network_error(self, mock_get):
        """Test handling of network errors."""
        mock_get.side_effect = Exception("Network error")
        
        result = url_to_wav.convert_url_to_wav(
            url="https://example.com/error",
            output_path="output.wav"
        )
        
        self.assertFalse(result)
    
    def test_cli_missing_arguments(self):
        """Test CLI with missing arguments."""
        with patch('sys.argv', ['url_to_wav.py']):
            with self.assertRaises(SystemExit):
                url_to_wav.main()
    
    def test_cli_help(self):
        """Test CLI help message."""
        with patch('sys.argv', ['url_to_wav.py', '--help']):
            with self.assertRaises(SystemExit) as cm:
                url_to_wav.main()
            # Help should exit with code 0
            self.assertEqual(cm.exception.code, 0)


if __name__ == '__main__':
    unittest.main()