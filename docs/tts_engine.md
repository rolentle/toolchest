# tts_engine.py

## Overview
Core Text-to-Speech (TTS) engine that wraps the Moshi MLX model for generating high-quality speech from text. This module provides a high-level interface for TTS generation with support for multiple voices, quantization, and real-time audio streaming.

## Classes

### `TTSEngine`
Main TTS engine class that handles model initialization, text-to-speech conversion, and audio generation.

#### Constructor
```python
TTSEngine(
    hf_repo: str = DEFAULT_DSM_TTS_REPO,
    voice_repo: str = DEFAULT_DSM_TTS_VOICE_REPO,
    quantize: Optional[int] = None
)
```

**Parameters:**
- `hf_repo` (str): HuggingFace repository for the TTS model
- `voice_repo` (str): HuggingFace repository for voice samples
- `quantize` (Optional[int]): Quantization bits (4 or 8) for model compression

#### Methods

##### `initialize()`
Initializes the TTS engine by loading models, tokenizers, and setting up the audio pipeline.

**Behavior:**
1. Sets random seed for reproducibility
2. Loads model configuration from HuggingFace
3. Loads Moshi language model and Mimi audio tokenizer
4. Applies quantization if specified
5. Initializes text tokenizer (SentencePiece)
6. Sets up TTS model with voice and generation parameters

##### `generate_audio(text: str, voice: str = DEFAULT_VOICE, on_frame_callback: Optional[Callable] = None)`
Generates audio from text input.

**Parameters:**
- `text` (str): The text to convert to speech
- `voice` (str): Voice sample to use (default: "expresso/ex03-ex01_happy_001_channel1_334s.wav")
- `on_frame_callback` (Optional[Callable]): Custom callback for audio frame processing

**Returns:**
- Generation result object containing audio frames and metadata

##### `get_audio_frames() -> List[np.ndarray]`
Retrieves all generated audio frames from the internal queue.

**Returns:**
- List of numpy arrays containing audio samples

##### `log(level: str, msg: str)`
Internal logging method for formatted output.

#### Properties

##### `sample_rate`
Returns the audio sample rate (24000 Hz for Moshi model).

##### `frame_rate`
Returns the frame generation rate of the model.

## Internal Methods

### `_on_frame(frame)`
Default frame callback that decodes audio tokens and adds PCM data to the output queue.

**Behavior:**
1. Checks for invalid frames (-1 values)
2. Decodes audio tokens using Mimi decoder
3. Clips audio to [-1, 1] range
4. Adds processed audio to output queue

## Usage Example
```python
from src.tts_engine import TTSEngine

# Initialize engine
engine = TTSEngine(quantize=8)  # 8-bit quantization
engine.initialize()

# Generate speech
text = "Hello, this is a test of the TTS engine."
result = engine.generate_audio(text, voice="expresso/ex03-ex01_happy_001_channel1_334s.wav")

# Get audio frames
audio_frames = engine.get_audio_frames()

# Access properties
print(f"Sample rate: {engine.sample_rate}")
print(f"Frame rate: {engine.frame_rate}")
```

## Configuration
The engine uses configuration values from `src.config`:
- Random seed: 299792458
- Default temperature: 0.6
- Default CFG coefficient: 1.0
- Padding settings for generation
- Audio clipping range: [-1, 1]

## Dependencies
- `mlx`: Apple's machine learning framework
- `moshi_mlx`: Moshi TTS model implementation
- `sentencepiece`: Text tokenization
- `numpy`: Audio data processing