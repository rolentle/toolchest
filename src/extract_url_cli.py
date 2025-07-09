#!/usr/bin/env python3
"""
Command-line interface for extracting text from URLs for TTS processing.

Usage:
    python src/extract_url_cli.py <URL>
    python src/extract_url_cli.py https://example.com | python src/tts_mlx.py - -
"""

import argparse
import sys
try:
    from .url_extractor import URLExtractor
    from .logger import Logger
except ImportError:
    from url_extractor import URLExtractor
    from logger import Logger


def main():
    parser = argparse.ArgumentParser(
        description="Extract human-readable text from URLs for TTS processing"
    )
    parser.add_argument(
        "url",
        type=str,
        help="The URL to extract text from",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable verbose output to stderr",
    )
    
    args = parser.parse_args()
    
    # Create logger
    logger = Logger("extract_url_cli", level="debug" if args.verbose else "info")
    
    # Create extractor instance
    extractor = URLExtractor()
    
    try:
        logger.info(f"Processing URL: {args.url}")
        
        # Extract text from URL
        text = extractor.extract_from_url(args.url)
        
        if not text:
            logger.error("No text content found at the URL.")
            sys.exit(1)
        
        # Output to stdout for piping
        print(text)
        
        word_count = len(text.split())
        logger.info(f"Successfully extracted {word_count} words")
            
    except Exception as e:
        logger.error(f"Failed to extract text: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()