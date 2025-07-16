# Toolchest <µ

A Text-to-Speech (TTS) conversion toolkit that transforms web content into audio files using the Moshi MLX model. This project is a "vibe coding" exercise - an exploration of building tools that feel good to use and combine interesting technologies in creative ways.

## What It Does

Toolchest extracts text from web pages and converts it to high-quality speech audio. It features:

- **Smart text extraction** from URLs with readable formatting
- **AI-powered filename generation** using Ollama for descriptive, meaningful filenames
- **High-quality TTS synthesis** via the Moshi MLX model with multiple voice options
- **Unix-style CLI tools** that pipe together beautifully

## Quick Start

```bash
# Install dependencies
uv sync

# Convert a URL directly to audio
uv run python src/url_to_wav.py https://example.com/article

# Or use the tools separately
uv run python src/extract_url_cli.py https://example.com/article | uv run python src/tts_mlx.py > output.wav
```

## Architecture

The project follows a modular design with centralized configuration:

- `extract_url_cli.py` - Extracts and formats text from web pages
- `tts_mlx.py` - Converts text to speech using Moshi MLX
- `url_to_wav.py` - All-in-one tool combining extraction and TTS
- `filename_generator.py` - Uses Ollama to create intelligent filenames
- `config.py` - Centralized configuration for all components

## The Vibe

This project embraces:
- Clean, composable Unix-style tools
- Thoughtful defaults with flexibility when needed  
- AI assistance where it adds delight (smart filenames!)
- Fast, local processing using Apple Silicon optimization

## Requirements

- macOS with Apple Silicon (for MLX)
- Python 3.11+
- Ollama (optional, for smart filenames)
- UV package manager

## Development

```bash
# Run tests
uv run pytest

# Run with coverage
uv run pytest --cov=src --cov-report=term-missing
```

Built with care as an exercise in creating tools that spark joy. <§