# url_to_wav.py

## Overview
Converts web page content to speech and saves it as a WAV audio file. This script combines URL text extraction with TTS generation, supporting automatic filename generation and various voice options.

## Usage
```bash
# Basic usage with auto-generated filename
python src/url_to_wav.py https://example.com

# Specify output file
python src/url_to_wav.py https://example.com -o article.wav

# Use different voice
python src/url_to_wav.py https://example.com -v "expresso/ex02_calm.wav"

# With 8-bit quantization and verbose output
python src/url_to_wav.py https://example.com -q 8 --verbose
```

## Command-Line Arguments

### Positional Arguments
- `url` (str): URL to extract text from (required)

### Optional Arguments
- `-o`, `--output`: Output WAV file path (auto-generated if not specified)
- `-v`, `--voice`: Voice to use for TTS (default: "expresso/ex03-ex01_happy_001_channel1_334s.wav")
- `-q`, `--quantize`: Quantization bits for model compression (choices: 4, 8)
- `--verbose`: Enable verbose output for debugging

## Functions

### `convert_url_to_wav(url, output_path=None, voice=DEFAULT_VOICE, quantize=None, verbose=False)`
Main conversion function that orchestrates the entire process.

**Parameters:**
- `url` (str): URL to extract text from
- `output_path` (str, optional): Path to save the WAV file
- `voice` (str): Voice sample for TTS
- `quantize` (int, optional): Quantization bits (4 or 8)
- `verbose` (bool): Enable verbose output

**Returns:**
- `bool`: True if successful, False otherwise

**Process:**
1. Extracts text from URL (with metadata if filename generation needed)
2. Initializes TTS engine with optional quantization
3. Generates audio from extracted text
4. Auto-generates filename if not provided (using AI)
5. Saves audio as WAV file

### `main()`
Command-line interface entry point.

**Behavior:**
- Parses command-line arguments
- Calls `convert_url_to_wav()` with provided options
- Returns appropriate exit code

## Features

### Automatic Filename Generation
When no output path is specified, the script:
1. Extracts page title and content
2. Uses AI (via Ollama) to generate a descriptive filename
3. Creates a filename that captures the content's main theme

### Verbose Output
With `--verbose` flag, displays:
- URL being processed
- Text extraction progress
- Character count and preview
- TTS engine initialization
- Voice being used
- Generated filename (if auto-generated)
- Audio properties (sample rate, duration)
- Save location

## Output Format
- **File Format**: WAV (uncompressed)
- **Sample Rate**: 24000 Hz
- **Channels**: 1 (mono)
- **Bit Depth**: 32-bit float

## Error Handling
- Graceful handling of extraction failures
- Clear error messages to stderr
- Returns exit code 1 on failure

## Examples
```bash
# Convert a blog post with auto-generated filename
python src/url_to_wav.py https://blog.example.com/article

# Convert with custom output and voice
python src/url_to_wav.py https://news.site/story -o news_story.wav -v "expresso/ex01_relaxed.wav"

# Quick conversion with quantization
python src/url_to_wav.py https://example.com -q 8

# Debug mode to see what's happening
python src/url_to_wav.py https://example.com --verbose
```

## Dependencies
- `url_extractor.URLExtractor`: Web content extraction
- `tts_engine.TTSEngine`: Text-to-speech generation
- `filename_generator.FilenameGenerator`: AI-powered filename creation
- `soundfile`: WAV file writing
- `numpy`: Audio data handling

## Integration
This script can be used as:
- Standalone CLI tool
- Python module for programmatic use
- Part of automation pipelines