# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "huggingface_hub",
#     "moshi_mlx==0.2.9",
#     "numpy",
#     "sounddevice",
# ]
# ///

import argparse
import queue
import sys
import time

import numpy as np
import sounddevice as sd
import sphn
from moshi_mlx.models.tts import (
    DEFAULT_DSM_TTS_REPO,
    DEFAULT_DSM_TTS_VOICE_REPO,
)

from .tts_engine import TTSEngine
from .config import AudioConfig, TTSConfig
from .logger import Logger


def main():
    parser = argparse.ArgumentParser(
        description="Run Kyutai TTS using the PyTorch implementation"
    )
    parser.add_argument("inp", type=str, help="Input file, use - for stdin")
    parser.add_argument(
        "out", type=str, help="Output file to generate, use - for playing the audio"
    )
    parser.add_argument(
        "--hf-repo",
        type=str,
        default=DEFAULT_DSM_TTS_REPO,
        help="HF repo in which to look for the pretrained models.",
    )
    parser.add_argument(
        "--voice-repo",
        default=DEFAULT_DSM_TTS_VOICE_REPO,
        help="HF repo in which to look for pre-computed voice embeddings.",
    )
    parser.add_argument(
        "--voice", default=TTSConfig.DEFAULT_VOICE
    )
    parser.add_argument(
        "--quantize",
        type=int,
        help="The quantization to be applied, e.g. 8 for 8 bits.",
    )
    args = parser.parse_args()

    # Initialize logger
    logger = Logger("tts_mlx")

    # Initialize the TTS engine
    engine = TTSEngine(
        hf_repo=args.hf_repo,
        voice_repo=args.voice_repo,
        quantize=args.quantize,
    )
    engine.initialize()

    # Read input text
    logger.info(f"reading input from {args.inp}")
    if args.inp == "-":
        if sys.stdin.isatty():  # Interactive
            print("Enter text to synthesize (Ctrl+D to end input):")
        text_to_tts = sys.stdin.read().strip()
    else:
        with open(args.inp, "r") as fobj:
            text_to_tts = fobj.read().strip()

    # Handle audio output
    if args.out == "-":
        # Play audio in real-time
        wav_frames = queue.Queue()

        def custom_on_frame(frame):
            if (frame == -1).any():
                return
            _pcm = engine.tts_model.mimi.decode_step(frame[:, :, None])
            _pcm = np.array(_pcm[0, 0])
            _pcm = np.clip(_pcm, AudioConfig.AUDIO_CLIP_MIN, AudioConfig.AUDIO_CLIP_MAX)
            wav_frames.put_nowait(_pcm)

        def audio_callback(outdata, _a, _b, _c):
            try:
                pcm_data = wav_frames.get(block=False)
                outdata[:, 0] = pcm_data
            except queue.Empty:
                outdata[:] = 0

        with sd.OutputStream(
            samplerate=engine.sample_rate,
            blocksize=AudioConfig.DEFAULT_BLOCKSIZE,
            channels=AudioConfig.DEFAULT_CHANNELS,
            callback=audio_callback,
        ):
            engine.generate_audio(text_to_tts, voice=args.voice, on_frame_callback=custom_on_frame)
            time.sleep(AudioConfig.INITIAL_PLAYBACK_DELAY)
            while True:
                if wav_frames.qsize() == 0:
                    break
                time.sleep(AudioConfig.LOOP_PLAYBACK_DELAY)
    else:
        # Generate and save to file
        engine.generate_audio(text_to_tts, voice=args.voice)
        frames = engine.get_audio_frames()
        if frames:
            wav = np.concatenate(frames, -1)
            sphn.write_wav(args.out, wav, engine.sample_rate)


if __name__ == "__main__":
    main()