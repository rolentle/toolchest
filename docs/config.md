# config.py

## Overview
Configuration module for the TTS Toolchest project. This module centralizes all configuration values and constants used throughout the project, organized into logical configuration classes.

## Classes

### `AudioConfig`
Audio processing configuration settings.

**Attributes:**
- `DEFAULT_SAMPLE_RATE` (int): Default sample rate for audio processing - 24000 Hz (MLX Moshi model sample rate)
- `DEFAULT_BLOCKSIZE` (int): Default audio block size - 1920
- `DEFAULT_CHANNELS` (int): Number of audio channels - 1 (mono)
- `AUDIO_CLIP_MIN` (int): Minimum audio clipping value - -1
- `AUDIO_CLIP_MAX` (int): Maximum audio clipping value - 1
- `INITIAL_PLAYBACK_DELAY` (int): Initial delay before playback - 3 seconds
- `LOOP_PLAYBACK_DELAY` (int): Delay between loop iterations - 1 second

### `TTSConfig`
Text-to-Speech engine configuration settings.

**Attributes:**
- `DEFAULT_VOICE` (str): Default voice sample - "expresso/ex03-ex01_happy_001_channel1_334s.wav"
- `DEFAULT_TEMP` (float): Default temperature for generation - 0.6
- `DEFAULT_CFG_COEF` (float): Default configuration coefficient - 1.0
- `DEFAULT_MAX_PADDING` (int): Maximum padding - 8
- `DEFAULT_INITIAL_PADDING` (int): Initial padding - 2
- `DEFAULT_FINAL_PADDING` (int): Final padding - 2
- `DEFAULT_PADDING_BONUS` (int): Padding bonus - 0
- `RANDOM_SEED` (int): Random seed for reproducibility - 299792458
- `DEFAULT_MODEL_DTYPE` (str): Default model data type - "bfloat16"
- `DEFAULT_MODEL_NAME` (str): Default model filename - "model.safetensors"
- `CONFIG_FILE_NAME` (str): Configuration filename - "config.json"
- `ALLOWED_QUANTIZATION_LEVELS` (list): Allowed quantization levels - [4, 8]

### `URLExtractorConfig`
URL text extraction configuration settings.

**Attributes:**
- `USER_AGENT` (str): User agent string for web requests - "Mozilla/5.0 (compatible; TTS-TextExtractor/1.0)"
- `REQUEST_TIMEOUT` (int): Request timeout - 10 seconds
- `DEFAULT_PARSER` (str): Default HTML parser - "lxml"
- `TEXT_ELEMENTS` (list): HTML elements to extract text from - ["p", "h1", "h2", "h3", "h4", "h5", "h6", "li"]
- `REMOVE_ELEMENTS` (list): HTML elements to remove - ["script", "style"]
- `VERBOSE_PREVIEW_LENGTH` (int): Character length for verbose preview - 200

### `OllamaConfig`
Ollama integration configuration for AI-powered filename generation.

**Attributes:**
- `DEFAULT_MODEL` (str): Default Ollama model - "gemma2:latest"
- `FILENAME_PROMPT_TEMPLATE` (str): Template for filename generation prompt
- `MAX_FILENAME_LENGTH` (int): Maximum generated filename length - 50 characters
- `FILENAME_GENERATION_TIMEOUT` (int): Timeout for filename generation - 10 seconds
- `MAX_TEXT_LENGTH_FOR_SUMMARY` (int): Maximum text length to send to Ollama - 1000 characters

## Usage Example
```python
from src.config import AudioConfig, TTSConfig, URLExtractorConfig, OllamaConfig

# Access configuration values
sample_rate = AudioConfig.DEFAULT_SAMPLE_RATE
voice = TTSConfig.DEFAULT_VOICE
user_agent = URLExtractorConfig.USER_AGENT
model = OllamaConfig.DEFAULT_MODEL
```