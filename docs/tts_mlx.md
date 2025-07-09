# tts_mlx.py

## Overview
Command-line interface for the Kyutai TTS (Text-to-Speech) system using MLX implementation. This script provides both real-time audio playback and file output capabilities for converting text to high-quality speech.

## Usage
```bash
# Read from file and play audio
python src/tts_mlx.py input.txt -

# Read from stdin and save to WAV file
echo "Hello world" | python src/tts_mlx.py - output.wav

# Read from file and save to WAV
python src/tts_mlx.py input.txt output.wav

# Use custom voice
python src/tts_mlx.py input.txt - --voice "expresso/ex01_relaxed.wav"

# With 8-bit quantization
python src/tts_mlx.py input.txt - --quantize 8
```

## Command-Line Arguments

### Positional Arguments
- `inp` (str): Input file path or `-` for stdin
- `out` (str): Output file path or `-` for real-time audio playback

### Optional Arguments
- `--hf-repo` (str): HuggingFace repository for TTS models (default: DEFAULT_DSM_TTS_REPO)
- `--voice-repo` (str): HuggingFace repository for voice embeddings (default: DEFAULT_DSM_TTS_VOICE_REPO)
- `--voice` (str): Voice sample to use (default: "expresso/ex03-ex01_happy_001_channel1_334s.wav")
- `--quantize` (int): Quantization bits (4 or 8) for model compression

## Functions

### `main()`
Main entry point that handles:
1. Command-line argument parsing
2. TTS engine initialization
3. Input text reading (file or stdin)
4. Audio generation and output (playback or file)

### `custom_on_frame(frame)`
Callback function for real-time audio processing.

**Behavior:**
- Decodes audio frames using Mimi decoder
- Clips audio to valid range [-1, 1]
- Adds processed audio to playback queue

### `audio_callback(outdata, _a, _b, _c)`
SoundDevice callback for real-time audio playback.

**Behavior:**
- Retrieves audio from queue
- Fills output buffer with audio samples
- Provides silence when queue is empty

## Output Modes

### Real-Time Playback (output = "-")
- Streams audio directly to speakers
- Uses custom frame callback for low-latency processing
- Implements buffering with configurable delays:
  - Initial delay: 3 seconds
  - Loop delay: 1 second

### File Output
- Generates complete audio before saving
- Saves as WAV file using sphn library
- Preserves full audio quality at 24kHz sample rate

## Script Metadata
The script includes inline dependencies for use with `uv run`:
- Python >= 3.12
- huggingface_hub
- moshi_mlx==0.2.9
- numpy
- sounddevice

## Examples
```bash
# Interactive mode
python src/tts_mlx.py - -
# Type text, then Ctrl+D to synthesize

# Pipe from URL extractor
python src/extract_url_cli.py https://example.com | python src/tts_mlx.py - -

# Generate audio file with custom voice
python src/tts_mlx.py story.txt story.wav --voice "expresso/ex02_calm.wav"

# Quick test with quantization
echo "Testing TTS with quantization" | python src/tts_mlx.py - - --quantize 8
```

## Audio Configuration
Uses settings from `AudioConfig`:
- Sample rate: 24000 Hz
- Block size: 1920
- Channels: 1 (mono)
- Audio clipping: [-1, 1]

## Dependencies
- `tts_engine.TTSEngine`: Core TTS functionality
- `sounddevice`: Real-time audio playback
- `sphn`: WAV file writing
- `numpy`: Audio data processing