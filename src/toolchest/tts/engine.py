"""TTS engine abstraction for text-to-speech synthesis."""

import io
import sys
from typing import Optional, Union, List
from abc import ABC, abstractmethod

import numpy as np
import pyttsx3

from .config import TTSConfig
from .audio import AudioProcessor


class TTSEngineBase(ABC):
    """Abstract base class for TTS engines."""
    
    @abstractmethod
    def synthesize(self, text: str) -> np.ndarray:
        """Synthesize speech from text.
        
        Args:
            text: Input text to synthesize
            
        Returns:
            Audio data as numpy array
        """
        pass
    
    @abstractmethod
    def get_voices(self) -> List[dict]:
        """Get available voices.
        
        Returns:
            List of voice dictionaries with id and name
        """
        pass


class TTSEngine(TTSEngineBase):
    """Main TTS engine using pyttsx3."""
    
    def __init__(self, config: TTSConfig):
        """Initialize TTS engine with configuration.
        
        Args:
            config: TTS configuration
        """
        self.config = config
        self.audio_processor = AudioProcessor(config.sample_rate)
        self._engine = pyttsx3.init()
        self._setup_engine()
    
    def _setup_engine(self) -> None:
        """Setup engine properties based on configuration."""
        # Set speech rate
        self._engine.setProperty('rate', self.config.rate)
        
        # Set volume
        self._engine.setProperty('volume', self.config.volume)
        
        # Set voice if specified
        voices = self._engine.getProperty('voices')
        if voices and 0 <= self.config.voice_id < len(voices):
            self._engine.setProperty('voice', voices[self.config.voice_id].id)
    
    def synthesize(self, text: str) -> np.ndarray:
        """Synthesize speech from text.
        
        Args:
            text: Input text to synthesize
            
        Returns:
            Audio data as numpy array
        """
        # Since pyttsx3 doesn't directly return audio data,
        # we need to save to a temporary buffer
        temp_buffer = io.BytesIO()
        
        # Use a temporary file approach
        import tempfile
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=True) as tmp_file:
            self._engine.save_to_file(text, tmp_file.name)
            self._engine.runAndWait()
            
            # Read the audio data
            from scipy.io import wavfile
            _, audio_data = wavfile.read(tmp_file.name)
        
        # Apply volume adjustment
        audio_data = self.audio_processor.process_audio(audio_data, self.config.volume)
        
        # Apply quantization if specified
        if self.config.quantize:
            audio_data = AudioProcessor.quantize_audio(audio_data, self.config.quantize)
        
        return audio_data
    
    def get_voices(self) -> List[dict]:
        """Get available voices.
        
        Returns:
            List of voice dictionaries
        """
        voices = self._engine.getProperty('voices')
        return [
            {
                'id': i,
                'name': voice.name,
                'languages': getattr(voice, 'languages', []),
                'gender': getattr(voice, 'gender', 'unknown')
            }
            for i, voice in enumerate(voices)
        ]
    
    def speak(self, text: str) -> None:
        """Speak text directly through speakers.
        
        Args:
            text: Text to speak
        """
        audio_data = self.synthesize(text)
        self.audio_processor.play_audio(audio_data)
    
    def save_to_file(self, text: str, output_path: str) -> None:
        """Save synthesized speech to file.
        
        Args:
            text: Text to synthesize
            output_path: Path to save audio file
        """
        audio_data = self.synthesize(text)
        self.audio_processor.save_audio(audio_data, output_path)
    
    def stream_to_stdout(self, text: str) -> None:
        """Stream synthesized speech to stdout.
        
        Args:
            text: Text to synthesize
        """
        audio_data = self.synthesize(text)
        self.audio_processor.stream_audio(audio_data, sys.stdout.buffer)
    
    def cleanup(self) -> None:
        """Cleanup engine resources."""
        if hasattr(self, '_engine'):
            self._engine.stop()


class MockTTSEngine(TTSEngineBase):
    """Mock TTS engine for testing."""
    
    def __init__(self, config: TTSConfig):
        """Initialize mock engine."""
        self.config = config
        self.audio_processor = AudioProcessor(config.sample_rate)
    
    def synthesize(self, text: str) -> np.ndarray:
        """Generate mock audio data.
        
        Args:
            text: Input text (used to determine length)
            
        Returns:
            Mock audio data
        """
        # Generate silence with length proportional to text
        duration = len(text) * 0.1  # 0.1 seconds per character
        samples = int(duration * self.config.sample_rate)
        
        # Generate a simple sine wave for testing
        t = np.linspace(0, duration, samples)
        frequency = 440  # A4 note
        audio_data = np.sin(2 * np.pi * frequency * t) * 0.5
        
        # Apply volume
        audio_data = self.audio_processor.process_audio(audio_data, self.config.volume)
        
        # Apply quantization if specified
        if self.config.quantize:
            audio_data = AudioProcessor.quantize_audio(audio_data, self.config.quantize)
        
        return audio_data
    
    def get_voices(self) -> List[dict]:
        """Get mock voices for testing.
        
        Returns:
            List of mock voices
        """
        return [
            {'id': 0, 'name': 'Mock Voice 1', 'languages': ['en'], 'gender': 'neutral'},
            {'id': 1, 'name': 'Mock Voice 2', 'languages': ['en'], 'gender': 'neutral'},
        ]