# url_extractor.py

## Overview
Extracts human-readable text from web pages for Text-to-Speech (TTS) processing. This module fetches web content, parses HTML, and formats text optimally for TTS engines.

## Classes

### `URLExtractor`
Main class for URL text extraction with intelligent HTML parsing and text formatting.

#### Constructor
```python
URLExtractor()
```
Initializes a requests session with a custom user agent.

#### Methods

##### `fetch_url(url: str) -> str`
Fetches HTML content from a URL.

**Parameters:**
- `url` (str): The URL to fetch

**Returns:**
- HTML content as a string

**Raises:**
- `Exception`: If the URL cannot be fetched

##### `extract_text(html: str) -> str`
Extracts human-readable text from HTML content.

**Parameters:**
- `html` (str): The HTML content to parse

**Returns:**
- Extracted text with proper formatting for TTS

**Behavior:**
1. Removes script and style elements
2. Extracts text from semantic elements (p, h1-h6, li)
3. Preserves image alt text as "[Image: description]"
4. Deduplicates content to avoid repetition
5. Joins text with double newlines for natural pauses

##### `format_for_tts(text: str) -> str`
Formats text for optimal TTS processing.

**Parameters:**
- `text` (str): The extracted text

**Returns:**
- Formatted text with consistent paragraph spacing

**Behavior:**
- Removes extra whitespace
- Ensures double newlines between paragraphs
- Creates natural pauses for TTS engines

##### `extract_from_url(url: str) -> str`
Complete extraction pipeline from URL to TTS-ready text.

**Parameters:**
- `url` (str): The URL to process

**Returns:**
- Formatted text ready for TTS

**Raises:**
- `Exception`: If URL processing fails

##### `extract_metadata(html: str, url: str) -> dict`
Extracts both text content and metadata from HTML.

**Parameters:**
- `html` (str): The HTML content
- `url` (str): The source URL

**Returns:**
- Dictionary containing:
  - `title`: Page title or first heading
  - `text`: Formatted text content
  - `url`: Source URL

##### `extract_from_url_with_metadata(url: str) -> dict`
Extracts text and metadata from a URL in one operation.

**Parameters:**
- `url` (str): The URL to process

**Returns:**
- Dictionary with title, text, and URL

## Configuration
Uses settings from `URLExtractorConfig`:
- User Agent: "Mozilla/5.0 (compatible; TTS-TextExtractor/1.0)"
- Request timeout: 10 seconds
- HTML parser: lxml
- Text elements: p, h1-h6, li
- Removed elements: script, style

## Usage Examples
```python
from src.url_extractor import URLExtractor

# Basic usage
extractor = URLExtractor()
text = extractor.extract_from_url("https://example.com")
print(text)

# With metadata
data = extractor.extract_from_url_with_metadata("https://example.com")
print(f"Title: {data['title']}")
print(f"Text: {data['text'][:200]}...")

# Custom HTML processing
html = extractor.fetch_url("https://example.com")
text = extractor.extract_text(html)
formatted = extractor.format_for_tts(text)
```

## Text Processing Features
- **Intelligent element selection**: Focuses on semantic HTML elements
- **Duplicate removal**: Prevents repeated content
- **Image accessibility**: Includes alt text for screen readers
- **Natural formatting**: Creates pauses between paragraphs
- **Clean output**: Removes scripts, styles, and non-content elements

## Dependencies
- `requests`: HTTP client for fetching URLs
- `beautifulsoup4`: HTML parsing
- `lxml`: Fast XML/HTML parser (optional but recommended)