#!/usr/bin/env python3
"""
Convert URL content to speech and save as WAV file.
"""
import argparse
import numpy as np
import soundfile as sf
import sys
try:
    from .url_extractor import URLExtractor
    from .tts_engine import TTSEngine
    from .config import TTSConfig, URLExtractorConfig
    from .filename_generator import FilenameGenerator
except ImportError:
    from url_extractor import URLExtractor
    from tts_engine import TTSEngine
    from config import TTSConfig, URLExtractorConfig
    from filename_generator import FilenameGenerator


def convert_url_to_wav(url, output_path=None, voice=TTSConfig.DEFAULT_VOICE, quantize=None, verbose=False):
    """
    Convert URL content to speech and save as WAV file.
    
    Args:
        url: URL to extract text from
        output_path: Path to save the WAV file
        voice: Voice to use for TTS
        quantize: Quantization bits for the model (4 or 8)
        verbose: Enable verbose output
        
    Returns:
        bool: True if successful, False otherwise
    """
    # Extract text from URL
    if verbose:
        print(f"Extracting text from: {url}")
    
    extractor = URLExtractor()
    try:
        # Use metadata extraction if we need to generate filename
        if output_path is None:
            metadata = extractor.extract_from_url_with_metadata(url)
            text = metadata['text']
            title = metadata.get('title', '')
        else:
            text = extractor.extract_from_url(url)
            title = None
            
        if not text:
            if verbose:
                print("No text extracted from URL", file=sys.stderr)
            return False
            
        if verbose:
            print(f"Extracted {len(text)} characters of text")
            print(f"First {URLExtractorConfig.VERBOSE_PREVIEW_LENGTH} characters:", text[:URLExtractorConfig.VERBOSE_PREVIEW_LENGTH], "...")
    except Exception as e:
        if verbose:
            print(f"Error extracting text: {e}", file=sys.stderr)
        return False
    
    # Initialize TTS engine
    if verbose:
        print("Initializing TTS engine...")
        
    engine = TTSEngine(quantize=quantize)
    engine.initialize()
    
    # Generate audio
    if verbose:
        print(f"Generating audio with voice: {voice}")
        
    result = engine.generate_audio(text, voice=voice)
    
    # Get all audio frames
    frames = engine.get_audio_frames()
    if not frames:
        if verbose:
            print("No audio frames generated", file=sys.stderr)
        return False
    
    # Concatenate all frames
    audio = np.concatenate(frames)
    
    # Generate filename if not provided
    if output_path is None:
        if verbose:
            print("Generating filename...")
        filename_gen = FilenameGenerator()
        output_path = filename_gen.generate_from_content(
            text,
            title=title if 'title' in locals() else None,
            url=url
        )
        if verbose:
            print(f"Generated filename: {output_path}")
    
    # Save to WAV file
    if verbose:
        print(f"Saving audio to: {output_path}")
        print(f"Sample rate: {engine.sample_rate} Hz")
        print(f"Duration: {len(audio) / engine.sample_rate:.2f} seconds")
        
    sf.write(output_path, audio, engine.sample_rate)
    
    if verbose:
        print("Done!")
    
    return True


def main():
    parser = argparse.ArgumentParser(
        description="Convert URL content to speech and save as WAV file"
    )
    parser.add_argument("url", help="URL to extract text from")
    parser.add_argument(
        "-o", "--output",
        dest="output",
        help="Output WAV file path (auto-generated if not specified)"
    )
    parser.add_argument(
        "-v", "--voice",
        default=TTSConfig.DEFAULT_VOICE,
        help="Voice to use for TTS"
    )
    parser.add_argument(
        "-q", "--quantize",
        type=int,
        choices=TTSConfig.ALLOWED_QUANTIZATION_LEVELS,
        help="Quantization bits for the model"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose output"
    )
    
    args = parser.parse_args()
    
    success = convert_url_to_wav(
        url=args.url,
        output_path=args.output,
        voice=args.voice,
        quantize=args.quantize,
        verbose=args.verbose
    )
    
    if not success:
        sys.exit(1)


if __name__ == "__main__":
    main()