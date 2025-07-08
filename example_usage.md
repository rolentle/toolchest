# URL Text Extraction for TTS - Example Usage

## Basic Usage

Extract text from a URL and pipe it to TTS:

```bash
uv run python src/extract_url_cli.py https://example.com | uv run python src/tts_mlx.py - -
```

## With Verbose Output

See what's being extracted:

```bash
uv run python src/extract_url_cli.py -v https://example.com
```

## Save Extracted Text

Save the extracted text to a file:

```bash
uv run python src/extract_url_cli.py https://example.com > extracted_text.txt
```

## Features

- Extracts all visible text from web pages
- Includes image alt text as "[Image: description]"
- Adds proper spacing between paragraphs for natural TTS pauses
- Skips scripts, styles, and other non-content elements
- Handles HTML entities correctly

## Example with httpbin.org

```bash
# Extract text from a test page
uv run python src/extract_url_cli.py https://httpbin.org/html | head -10

# Convert to speech
uv run python src/extract_url_cli.py https://httpbin.org/html | uv run python src/tts_mlx.py - output.wav
```