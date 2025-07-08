"""TTS (Text-to-Speech) module for toolchest."""

from .config import TTSConfig
from .engine import TTSEngine
from .audio import AudioProcessor

__all__ = ["TTSConfig", "TTSEngine", "AudioProcessor"]