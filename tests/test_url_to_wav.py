#!/usr/bin/env python3
"""
Test suite for URL to WAV conversion functionality.
"""
import unittest
from unittest.mock import Mock, patch, MagicMock, call
import numpy as np
from src import url_to_wav


class TestURLToWav(unittest.TestCase):
    
    @patch('src.url_to_wav.sf')
    @patch('src.url_to_wav.TTSEngine')
    @patch('src.url_to_wav.URLExtractor')
    def test_basic_url_to_wav_conversion(self, mock_extractor_class, mock_tts_engine_class, mock_sf):
        """Test basic URL to WAV conversion flow."""
        # Setup mocks
        mock_extractor = mock_extractor_class.return_value
        mock_extractor.extract_from_url.return_value = "Hello world from the URL"
        
        mock_engine = mock_tts_engine_class.return_value
        mock_engine.sample_rate = 24000
        mock_engine.get_audio_frames.return_value = [
            np.array([0.1, 0.2, 0.3]),
            np.array([0.4, 0.5, 0.6])
        ]
        
        # Call the function
        result = url_to_wav.convert_url_to_wav(
            url="https://example.com",
            output_path="output.wav"
        )
        
        # Verify the flow
        mock_extractor_class.assert_called_once()
        mock_extractor.extract_from_url.assert_called_once_with("https://example.com")
        
        mock_tts_engine_class.assert_called_once_with(quantize=None)
        mock_engine.initialize.assert_called_once()
        mock_engine.generate_audio.assert_called_once_with(
            "Hello world from the URL",
            voice="expresso/ex03-ex01_happy_001_channel1_334s.wav"
        )
        
        # Verify audio was saved
        mock_sf.write.assert_called_once()
        call_args = mock_sf.write.call_args[0]
        self.assertEqual(call_args[0], "output.wav")
        np.testing.assert_array_equal(call_args[1], np.array([0.1, 0.2, 0.3, 0.4, 0.5, 0.6]))
        self.assertEqual(call_args[2], 24000)
        
        self.assertTrue(result)
    
    @patch('src.url_to_wav.URLExtractor')
    def test_empty_url_content(self, mock_extractor_class):
        """Test handling of empty URL content."""
        mock_extractor = mock_extractor_class.return_value
        mock_extractor.extract_from_url.return_value = ""
        
        result = url_to_wav.convert_url_to_wav(
            url="https://example.com",
            output_path="output.wav"
        )
        
        self.assertFalse(result)
    
    @patch('src.url_to_wav.URLExtractor')
    def test_url_extraction_error(self, mock_extractor_class):
        """Test handling of URL extraction errors."""
        mock_extractor = mock_extractor_class.return_value
        mock_extractor.extract_from_url.side_effect = Exception("Network error")
        
        result = url_to_wav.convert_url_to_wav(
            url="https://example.com",
            output_path="output.wav"
        )
        
        self.assertFalse(result)
    
    @patch('src.url_to_wav.sf')
    @patch('src.url_to_wav.TTSEngine')
    @patch('src.url_to_wav.URLExtractor')
    def test_custom_voice_and_quantization(self, mock_extractor_class, mock_tts_engine_class, mock_sf):
        """Test using custom voice and quantization settings."""
        mock_extractor = mock_extractor_class.return_value
        mock_extractor.extract_from_url.return_value = "Test content"
        
        mock_engine = mock_tts_engine_class.return_value
        mock_engine.sample_rate = 24000
        mock_engine.get_audio_frames.return_value = [np.array([0.1])]
        
        result = url_to_wav.convert_url_to_wav(
            url="https://example.com",
            output_path="output.wav",
            voice="custom_voice.wav",
            quantize=8
        )
        
        mock_tts_engine_class.assert_called_once_with(quantize=8)
        mock_engine.generate_audio.assert_called_once_with(
            "Test content",
            voice="custom_voice.wav"
        )
        self.assertTrue(result)
    
    @patch('sys.argv', ['url_to_wav.py', 'https://example.com', '-o', 'output.wav'])
    @patch('src.url_to_wav.convert_url_to_wav')
    def test_cli_basic_usage(self, mock_convert):
        """Test command line interface basic usage."""
        mock_convert.return_value = True
        
        # Should not raise
        url_to_wav.main()
        
        mock_convert.assert_called_once_with(
            url='https://example.com',
            output_path='output.wav',
            voice=url_to_wav.TTSConfig.DEFAULT_VOICE,
            quantize=None,
            verbose=False
        )
    
    @patch('sys.argv', ['url_to_wav.py', 'https://example.com', '-o', 'output.wav', '-v', 'custom.wav', '-q', '8', '--verbose'])
    @patch('src.url_to_wav.convert_url_to_wav')
    def test_cli_with_options(self, mock_convert):
        """Test command line interface with all options."""
        mock_convert.return_value = True
        
        url_to_wav.main()
        
        mock_convert.assert_called_once_with(
            url='https://example.com',
            output_path='output.wav',
            voice='custom.wav',
            quantize=8,
            verbose=True
        )
    
    @patch('sys.argv', ['url_to_wav.py', 'https://example.com', '-o', 'output.wav'])
    @patch('src.url_to_wav.convert_url_to_wav')
    def test_cli_error_handling(self, mock_convert):
        """Test CLI error handling."""
        mock_convert.return_value = False
        
        with self.assertRaises(SystemExit) as cm:
            url_to_wav.main()
        
        self.assertEqual(cm.exception.code, 1)
    
    @patch('src.url_to_wav.sf')
    @patch('src.url_to_wav.TTSEngine')
    @patch('src.url_to_wav.URLExtractor')
    def test_no_audio_frames_generated(self, mock_extractor_class, mock_tts_engine_class, mock_sf):
        """Test handling when no audio frames are generated."""
        mock_extractor = mock_extractor_class.return_value
        mock_extractor.extract_from_url.return_value = "Test content"
        
        mock_engine = mock_tts_engine_class.return_value
        mock_engine.sample_rate = 24000
        mock_engine.get_audio_frames.return_value = []  # No frames
        
        result = url_to_wav.convert_url_to_wav(
            url="https://example.com",
            output_path="output.wav"
        )
        
        # Should not call sf.write when no frames
        mock_sf.write.assert_not_called()
        self.assertFalse(result)
    
    @patch('src.url_to_wav.FilenameGenerator')
    @patch('src.url_to_wav.sf')
    @patch('src.url_to_wav.TTSEngine')
    @patch('src.url_to_wav.URLExtractor')
    def test_auto_filename_generation(self, mock_extractor_class, mock_tts_engine_class, mock_sf, mock_filename_gen_class):
        """Test automatic filename generation when no output path is provided."""
        # Setup mocks
        mock_extractor = mock_extractor_class.return_value
        mock_extractor.extract_from_url_with_metadata.return_value = {
            'text': "Test content",
            'title': "Test Article",
            'url': "https://example.com/article"
        }
        
        mock_engine = mock_tts_engine_class.return_value
        mock_engine.sample_rate = 24000
        mock_engine.get_audio_frames.return_value = [np.array([0.1, 0.2])]
        
        mock_filename_gen = mock_filename_gen_class.return_value
        mock_filename_gen.generate_from_content.return_value = "test_article_20240115_143052.wav"
        
        # Call function with no output path
        result = url_to_wav.convert_url_to_wav(
            url="https://example.com/article",
            output_path=None
        )
        
        # Verify filename generation was called
        mock_filename_gen_class.assert_called_once()
        mock_filename_gen.generate_from_content.assert_called_once_with(
            "Test content",
            title="Test Article",
            url="https://example.com/article"
        )
        
        # Verify file was saved with generated name
        mock_sf.write.assert_called_once()
        call_args = mock_sf.write.call_args[0]
        self.assertEqual(call_args[0], "test_article_20240115_143052.wav")
        np.testing.assert_array_equal(call_args[1], np.array([0.1, 0.2]))
        self.assertEqual(call_args[2], 24000)
        
        self.assertTrue(result)
    
    @patch('sys.argv', ['url_to_wav.py', 'https://example.com'])
    @patch('src.url_to_wav.convert_url_to_wav')
    def test_cli_auto_naming(self, mock_convert):
        """Test CLI with automatic naming (no output specified)."""
        mock_convert.return_value = True
        
        url_to_wav.main()
        
        mock_convert.assert_called_once_with(
            url='https://example.com',
            output_path=None,
            voice=url_to_wav.TTSConfig.DEFAULT_VOICE,
            quantize=None,
            verbose=False
        )
    
    @patch('sys.argv', ['url_to_wav.py', 'https://example.com', '-o', 'custom.wav'])
    @patch('src.url_to_wav.convert_url_to_wav')
    def test_cli_custom_output(self, mock_convert):
        """Test CLI with custom output path using -o flag."""
        mock_convert.return_value = True
        
        url_to_wav.main()
        
        mock_convert.assert_called_once_with(
            url='https://example.com',
            output_path='custom.wav',
            voice=url_to_wav.TTSConfig.DEFAULT_VOICE,
            quantize=None,
            verbose=False
        )


if __name__ == '__main__':
    unittest.main()