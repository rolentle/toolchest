"""Configuration management for TTS functionality."""

from dataclasses import dataclass
from typing import Optional


@dataclass
class TTSConfig:
    """Configuration for Text-to-Speech engine."""
    
    voice_id: int = 0
    rate: int = 200  # Words per minute
    volume: float = 1.0  # 0.0 to 1.0
    language: str = "en"
    output_format: str = "wav"
    sample_rate: int = 22050
    quantize: Optional[int] = None  # Optional quantization bits
    
    def validate(self) -> None:
        """Validate configuration values."""
        if not 0 <= self.volume <= 1.0:
            raise ValueError("Volume must be between 0.0 and 1.0")
        
        if self.rate <= 0:
            raise ValueError("Rate must be positive")
        
        if self.sample_rate <= 0:
            raise ValueError("Sample rate must be positive")
        
        if self.quantize is not None and self.quantize not in [4, 8, 16]:
            raise ValueError("Quantization must be 4, 8, or 16 bits")
    
    @classmethod
    def from_args(cls, args) -> "TTSConfig":
        """Create config from command line arguments."""
        config = cls()
        
        if hasattr(args, "voice") and args.voice is not None:
            config.voice_id = args.voice
        
        if hasattr(args, "rate") and args.rate is not None:
            config.rate = args.rate
            
        if hasattr(args, "volume") and args.volume is not None:
            config.volume = args.volume
            
        if hasattr(args, "quantize") and args.quantize is not None:
            config.quantize = args.quantize
            
        config.validate()
        return config