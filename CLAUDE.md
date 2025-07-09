# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Toolchest is a Text-to-Speech (TTS) conversion toolkit that converts web content into audio files using the Moshi MLX model. It combines web scraping, AI-powered filename generation, and high-quality TTS synthesis.

## Development Commands

### Running Tests
```bash
# Run all tests
uv run pytest

# Run tests with coverage
uv run pytest --cov=src --cov-report=term-missing

# Run specific test file
uv run pytest tests/test_filename_generator.py

# Run tests with verbose output
uv run pytest -v
```

### Running the Application
```bash
# Extract text from URL
uv run python src/extract_url_cli.py <URL>

# Convert text to speech (from stdin)
echo "Hello world" | uv run python src/tts_mlx.py

# Convert URL to WAV file
uv run python src/url_to_wav.py <URL>
```

## Architecture

### Core Components

1. **Configuration (`src/config.py`)**: Centralized settings for all modules
   - AudioConfig: Sample rates, channels, delays
   - TTSConfig: Voice models, temperature, parameters
   - URLExtractorConfig: Web scraping settings
   - OllamaConfig: LLM settings for filename generation

2. **URL Extraction (`src/url_extractor.py`)**: 
   - Extracts readable text from web pages
   - Formats text with pauses for TTS
   - Handles images, removes scripts/styles

3. **TTS Engine (`src/tts_engine.py`)**:
   - Wraps Moshi MLX model
   - Frame-based audio generation
   - Supports multiple voices and quantization

4. **Filename Generator (`src/filename_generator.py`)**:
   - Uses Ollama to generate descriptive filenames
   - Fallback mechanisms for reliability

### Key Patterns

1. **Import Flexibility**: Modules support both package and direct imports
```python
try:
    from .config import Config
except ImportError:
    from config import Config
```

2. **CLI Design**: Unix-style tools that can pipe together
   - Status messages to stderr
   - Data output to stdout
   - Verbose mode for debugging

3. **Error Handling**: Graceful degradation with fallbacks

## Dependencies

- **ML Framework**: MLX (Apple's ML framework)
- **TTS Model**: Moshi from Kyutai (moshi-mlx)
- **Web Scraping**: BeautifulSoup4, lxml, requests
- **Audio**: sounddevice, soundfile
- **AI**: Ollama for LLM features
- **Package Management**: UV

## Testing

Tests are in `tests/` directory with fixtures in `tests/fixtures/`. Each module has corresponding test file following `test_*.py` naming convention.