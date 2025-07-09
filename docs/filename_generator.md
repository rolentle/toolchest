# filename_generator.py

## Overview
Generates descriptive filenames for audio files using AI (Ollama) to analyze text content. This module creates meaningful filenames based on the content being converted to speech, with automatic fallbacks and filesystem-safe sanitization.

## Classes

### `FilenameGenerator`
Main class for AI-powered filename generation with intelligent fallbacks.

#### Constructor
```python
FilenameGenerator(model: Optional[str] = None)
```

**Parameters:**
- `model` (Optional[str]): Ollama model to use (default: "gemma2:latest")

#### Methods

##### `sanitize_filename(filename: str) -> str`
Sanitizes a filename for filesystem compatibility.

**Parameters:**
- `filename` (str): Raw filename to sanitize

**Returns:**
- Sanitized filename safe for filesystem use

**Behavior:**
1. Converts to lowercase
2. Replaces special characters with underscores
3. Removes leading/trailing underscores
4. Eliminates consecutive underscores
5. Handles empty results (defaults to "unnamed")
6. Limits length to 50 characters

##### `add_timestamp(filename: str) -> str`
Adds a timestamp to ensure filename uniqueness.

**Parameters:**
- `filename` (str): Base filename

**Returns:**
- Filename with timestamp in format: `filename_YYYYMMDD_HHMMSS`

##### `generate_from_content(text: str, title: Optional[str] = None, url: Optional[str] = None) -> str`
Generates a descriptive filename using AI analysis of the content.

**Parameters:**
- `text` (str): The text content to analyze
- `title` (Optional[str]): Page title (used to enhance AI context)
- `url` (Optional[str]): Source URL (used as fallback)

**Returns:**
- Generated filename with .wav extension

**Process:**
1. Truncates text to 1000 characters if needed
2. Includes title in prompt if provided
3. Sends prompt to Ollama for analysis
4. Sanitizes AI-generated filename
5. Adds timestamp for uniqueness
6. Falls back to URL-based naming if AI fails

##### `generate_from_url(url: str) -> str`
Generates filename from URL structure (fallback method).

**Parameters:**
- `url` (str): Source URL

**Returns:**
- Generated filename with .wav extension

**Behavior:**
1. Parses URL to extract domain and path
2. Uses meaningful path components (ignores numeric segments)
3. Combines domain and path into filename
4. Sanitizes and adds timestamp

## AI Prompt Template
The module uses a carefully crafted prompt:
```
Generate a short, descriptive filename (3-5 words) for an audio file containing the following text. 
The filename should capture the main topic or theme. 
Use only lowercase letters, numbers, and underscores. 
Do not include file extensions or special characters.

Text: {text}

Filename:
```

## Configuration
Uses settings from `OllamaConfig`:
- Default model: "gemma2:latest"
- Max filename length: 50 characters
- Generation timeout: 10 seconds
- Max text for summary: 1000 characters

## Usage Examples
```python
from src.filename_generator import FilenameGenerator

# Basic usage
generator = FilenameGenerator()

# Generate from text content
text = "This article discusses the impact of AI on healthcare..."
filename = generator.generate_from_content(text)
# Result: "ai_healthcare_impact_20240115_143022.wav"

# With title for better context
filename = generator.generate_from_content(
    text=text,
    title="AI Revolution in Medicine",
    url="https://example.com/ai-medicine"
)
# Result: "ai_revolution_medicine_20240115_143022.wav"

# URL-based fallback
filename = generator.generate_from_url("https://news.site/tech/ai-breakthrough")
# Result: "news_site_ai_breakthrough_20240115_143022.wav"

# Custom model
generator = FilenameGenerator(model="llama2:latest")
```

## Fallback Strategy
The module implements a robust fallback chain:
1. **Primary**: AI-generated filename using Ollama
2. **Secondary**: URL-based filename if AI fails
3. **Tertiary**: Generic "audio_file" with timestamp

## Features
- **AI-Powered**: Uses LLM to understand content and create meaningful names
- **Context-Aware**: Considers both title and content for better results
- **Filesystem-Safe**: Automatic sanitization for all operating systems
- **Unique Names**: Timestamps prevent filename collisions
- **Smart Fallbacks**: Never fails to generate a filename
- **Configurable**: Supports different Ollama models

## Error Handling
- Graceful handling of Ollama failures
- Automatic fallback to URL-based naming
- Always returns a valid filename

## Dependencies
- `ollama`: AI model interaction
- `datetime`: Timestamp generation
- `urllib.parse`: URL parsing
- `re`: Pattern matching for sanitization