#!/usr/bin/env python3
"""Text-to-Speech script with CLI interface.

This script provides text-to-speech functionality with support for:
- File input/output
- stdin/stdout streaming
- Voice selection
- Audio configuration
"""

import sys
import argparse
import logging
from pathlib import Path
from typing import Optional

from .tts.config import TTSConfig
from .tts.engine import TTSEngine


def setup_logging(verbose: bool = False) -> None:
    """Setup logging configuration."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )


def list_voices() -> None:
    """List available TTS voices."""
    config = TTSConfig()
    engine = TTSEngine(config)
    
    print("Available voices:")
    for voice in engine.get_voices():
        print(f"  {voice['id']}: {voice['name']} ({voice.get('gender', 'unknown')})")
        if voice.get('languages'):
            print(f"     Languages: {', '.join(voice['languages'])}")
    
    engine.cleanup()


def read_input(input_source: str) -> str:
    """Read text from input source.
    
    Args:
        input_source: Path to file or '-' for stdin
        
    Returns:
        Input text
    """
    if input_source == '-':
        return sys.stdin.read()
    else:
        with open(input_source, 'r', encoding='utf-8') as f:
            return f.read()


def main() -> int:
    """Main entry point for TTS script."""
    parser = argparse.ArgumentParser(
        description="Text-to-Speech tool with file and streaming support"
    )
    
    parser.add_argument(
        'input',
        nargs='?',
        help="Input text file path or '-' for stdin"
    )
    
    parser.add_argument(
        'output',
        nargs='?',
        help="Output audio file path or '-' for stdout/speakers"
    )
    
    parser.add_argument(
        '--voice', '-v',
        type=int,
        default=0,
        help="Voice ID to use (default: 0)"
    )
    
    parser.add_argument(
        '--rate', '-r',
        type=int,
        default=200,
        help="Speech rate in words per minute (default: 200)"
    )
    
    parser.add_argument(
        '--volume',
        type=float,
        default=1.0,
        help="Volume level 0.0-1.0 (default: 1.0)"
    )
    
    parser.add_argument(
        '--quantize', '-q',
        type=int,
        choices=[4, 8, 16],
        help="Quantization bits for audio compression"
    )
    
    parser.add_argument(
        '--list-voices', '-l',
        action='store_true',
        help="List available voices and exit"
    )
    
    parser.add_argument(
        '--verbose',
        action='store_true',
        help="Enable verbose logging"
    )
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(args.verbose)
    logger = logging.getLogger(__name__)
    
    # Handle list voices
    if args.list_voices:
        list_voices()
        return 0
    
    # Check required arguments
    if not args.input or not args.output:
        parser.error("input and output arguments are required")
    
    try:
        # Create configuration
        config = TTSConfig.from_args(args)
        
        # Read input text
        logger.debug(f"Reading input from: {args.input}")
        text = read_input(args.input)
        
        if not text.strip():
            logger.error("Empty input text")
            return 1
        
        # Create TTS engine
        engine = TTSEngine(config)
        
        # Process based on output type
        if args.output == '-':
            # Output to speakers or stdout
            if sys.stdout.isatty():
                # Terminal - play through speakers
                logger.info("Playing audio through speakers...")
                engine.speak(text)
            else:
                # Pipe - stream to stdout
                logger.debug("Streaming audio to stdout")
                engine.stream_to_stdout(text)
        else:
            # Save to file
            logger.info(f"Saving audio to: {args.output}")
            engine.save_to_file(text, args.output)
            logger.info("Audio saved successfully")
        
        # Cleanup
        engine.cleanup()
        return 0
        
    except KeyboardInterrupt:
        logger.info("Operation cancelled by user")
        return 130
    except Exception as e:
        logger.error(f"Error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())