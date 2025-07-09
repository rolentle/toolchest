"""Configuration module for the TTS Toolchest project.

This module centralizes all configuration values and constants used throughout the project.
"""

class AudioConfig:
    """Audio processing configuration."""
    DEFAULT_SAMPLE_RATE = 24000  # MLX Moshi model sample rate
    DEFAULT_BLOCKSIZE = 1920
    DEFAULT_CHANNELS = 1
    AUDIO_CLIP_MIN = -1
    AUDIO_CLIP_MAX = 1
    INITIAL_PLAYBACK_DELAY = 3  # seconds
    LOOP_PLAYBACK_DELAY = 1  # seconds


class TTSConfig:
    """TTS engine configuration."""
    DEFAULT_VOICE = "expresso/ex03-ex01_happy_001_channel1_334s.wav"
    DEFAULT_TEMP = 0.6
    DEFAULT_CFG_COEF = 1.0
    DEFAULT_MAX_PADDING = 8
    DEFAULT_INITIAL_PADDING = 2
    DEFAULT_FINAL_PADDING = 2
    DEFAULT_PADDING_BONUS = 0
    RANDOM_SEED = 299792458
    DEFAULT_MODEL_DTYPE = "bfloat16"  # Use string to avoid importing mx here
    DEFAULT_MODEL_NAME = "model.safetensors"
    CONFIG_FILE_NAME = "config.json"
    ALLOWED_QUANTIZATION_LEVELS = [4, 8]


class URLExtractorConfig:
    """URL extraction configuration."""
    USER_AGENT = "Mozilla/5.0 (compatible; TTS-TextExtractor/1.0)"
    REQUEST_TIMEOUT = 10  # seconds
    DEFAULT_PARSER = "lxml"
    TEXT_ELEMENTS = ["p", "h1", "h2", "h3", "h4", "h5", "h6", "li"]
    REMOVE_ELEMENTS = ["script", "style"]
    VERBOSE_PREVIEW_LENGTH = 200  # characters


class OllamaConfig:
    """Ollama integration configuration."""
    DEFAULT_MODEL = "gemma2:latest"
    FILENAME_PROMPT_TEMPLATE = """Generate a short, descriptive filename (3-5 words) for an audio file containing the following text. 
    The filename should capture the main topic or theme. 
    Use only lowercase letters, numbers, and underscores. 
    Do not include file extensions or special characters.
    
    Text: {text}
    
    Filename:"""
    MAX_FILENAME_LENGTH = 50
    FILENAME_GENERATION_TIMEOUT = 10  # seconds
    MAX_TEXT_LENGTH_FOR_SUMMARY = 1000  # characters to send to Ollama