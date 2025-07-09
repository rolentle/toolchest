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
    from .logger import Logger
except ImportError:
    from url_extractor import URLExtractor
    from tts_engine import TTSEngine
    from config import TTSConfig, URLExtractorConfig
    from filename_generator import FilenameGenerator
    from logger import Logger


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
    # Initialize logger
    logger = Logger("url_to_wav", level="debug" if verbose else "info")
    
    # Extract text from URL
    logger.info(f"Starting URL to WAV conversion for: {url}")
    
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
            logger.error("No text extracted from URL")
            return False
            
        logger.info(f"Extracted {len(text)} characters of text")
        logger.debug(f"First {URLExtractorConfig.VERBOSE_PREVIEW_LENGTH} characters: {text[:URLExtractorConfig.VERBOSE_PREVIEW_LENGTH]}...")
    except Exception as e:
        logger.error(f"Failed to extract text: {e}")
        return False
    
    # Initialize TTS engine
    logger.info("Initializing TTS engine...")
        
    engine = TTSEngine(quantize=quantize)
    engine.initialize()
    
    # Generate audio
    logger.info(f"Generating audio with voice: {voice}")
        
    result = engine.generate_audio(text, voice=voice)
    
    # Get all audio frames
    frames = engine.get_audio_frames()
    if not frames:
        logger.error("No audio frames generated")
        return False
    
    # Concatenate all frames
    audio = np.concatenate(frames)
    
    # Generate filename if not provided
    if output_path is None:
        logger.info("Generating filename...")
        filename_gen = FilenameGenerator()
        output_path = filename_gen.generate_from_content(
            text,
            title=title if 'title' in locals() else None,
            url=url
        )
        logger.info(f"Generated filename: {output_path}")
    
    # Save to WAV file
    logger.info(f"Saving audio to: {output_path}")
    logger.info(f"Sample rate: {engine.sample_rate} Hz")
    logger.info(f"Duration: {len(audio) / engine.sample_rate:.2f} seconds")
        
    sf.write(output_path, audio, engine.sample_rate)
    
    logger.info("Conversion completed successfully")
    
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