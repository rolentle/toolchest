"""Audio processing utilities for TTS."""

import io
import wave
from typing import Optional, Union, BinaryIO

import numpy as np
import sounddevice as sd
from scipy.io import wavfile


class AudioProcessor:
    """Handle audio processing and playback for TTS output."""
    
    def __init__(self, sample_rate: int = 22050):
        """Initialize audio processor.
        
        Args:
            sample_rate: Sample rate for audio output
        """
        self.sample_rate = sample_rate
    
    def play_audio(self, audio_data: np.ndarray) -> None:
        """Play audio data through speakers.
        
        Args:
            audio_data: Audio samples as numpy array
        """
        if audio_data.dtype == np.int16:
            # Normalize int16 to float32 [-1, 1]
            audio_data = audio_data.astype(np.float32) / 32768.0
        
        sd.play(audio_data, self.sample_rate)
        sd.wait()  # Wait until playback is finished
    
    def save_audio(self, audio_data: np.ndarray, output_path: str) -> None:
        """Save audio data to a WAV file.
        
        Args:
            audio_data: Audio samples as numpy array
            output_path: Path to save the WAV file
        """
        # Ensure audio is in the correct format for WAV
        if audio_data.dtype == np.float32 or audio_data.dtype == np.float64:
            # Convert float to int16
            audio_data = np.clip(audio_data * 32768, -32768, 32767).astype(np.int16)
        
        wavfile.write(output_path, self.sample_rate, audio_data)
    
    def stream_audio(self, audio_data: np.ndarray, file_obj: BinaryIO) -> None:
        """Stream audio data to a file object.
        
        Args:
            audio_data: Audio samples as numpy array
            file_obj: File object to write audio data
        """
        # Convert to int16 if needed
        if audio_data.dtype == np.float32 or audio_data.dtype == np.float64:
            audio_data = np.clip(audio_data * 32768, -32768, 32767).astype(np.int16)
        
        # Create WAV file in memory
        wav_buffer = io.BytesIO()
        wavfile.write(wav_buffer, self.sample_rate, audio_data)
        wav_buffer.seek(0)
        
        # Write to file object
        file_obj.write(wav_buffer.read())
    
    def process_audio(self, audio_data: np.ndarray, volume: float = 1.0) -> np.ndarray:
        """Process audio data with volume adjustment.
        
        Args:
            audio_data: Input audio samples
            volume: Volume multiplier (0.0 to 1.0)
            
        Returns:
            Processed audio data
        """
        return audio_data * volume
    
    @staticmethod
    def quantize_audio(audio_data: np.ndarray, bits: int) -> np.ndarray:
        """Quantize audio data to specified bit depth.
        
        Args:
            audio_data: Input audio samples
            bits: Target bit depth (4, 8, or 16)
            
        Returns:
            Quantized audio data
        """
        if bits not in [4, 8, 16]:
            raise ValueError("Bits must be 4, 8, or 16")
        
        # Convert to float32 for processing
        if audio_data.dtype == np.int16:
            audio_data = audio_data.astype(np.float32) / 32768.0
        
        # Quantize
        levels = 2 ** bits
        quantized = np.round(audio_data * (levels / 2)) / (levels / 2)
        
        return quantized