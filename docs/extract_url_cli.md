# extract_url_cli.py

## Overview
Command-line interface for extracting human-readable text from URLs for TTS (Text-to-Speech) processing. This script fetches web content and extracts the main text, making it suitable for piping to TTS engines.

## Usage
```bash
# Basic usage
python src/extract_url_cli.py <URL>

# With verbose output
python src/extract_url_cli.py -v <URL>

# Pipe to TTS engine
python src/extract_url_cli.py https://example.com | python src/tts_mlx.py - -
```

## Command-Line Arguments

### Positional Arguments
- `url` (str): The URL to extract text from (required)

### Optional Arguments
- `--verbose`, `-v`: Enable verbose output to stderr (shows extraction progress and word count)

## Functions

### `main()`
Main entry point for the CLI application.

**Behavior:**
1. Parses command-line arguments
2. Creates a URLExtractor instance
3. Extracts text from the provided URL
4. Outputs the extracted text to stdout
5. Optionally prints verbose information to stderr

**Exit Codes:**
- `0`: Success
- `1`: Error (no text found or extraction failed)

## Output
- **stdout**: Extracted text content (for piping)
- **stderr**: Status messages, errors, and verbose output

## Examples
```bash
# Extract text from a website
python src/extract_url_cli.py https://example.com

# Extract with verbose output
python src/extract_url_cli.py -v https://example.com

# Pipe extracted text to TTS
python src/extract_url_cli.py https://example.com | python src/tts_mlx.py - -

# Save extracted text to file
python src/extract_url_cli.py https://example.com > extracted_text.txt
```

## Error Handling
- Handles missing text content gracefully
- Provides clear error messages to stderr
- Returns appropriate exit codes for scripting

## Dependencies
- `url_extractor.URLExtractor`: Core extraction functionality