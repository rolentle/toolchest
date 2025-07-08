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
except ImportError:
    from url_extractor import URLExtractor


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
    
    # Create extractor instance
    extractor = URLExtractor()
    
    try:
        if args.verbose:
            print(f"Fetching content from: {args.url}", file=sys.stderr)
        
        # Extract text from URL
        text = extractor.extract_from_url(args.url)
        
        if not text:
            print("No text content found at the URL.", file=sys.stderr)
            sys.exit(1)
        
        # Output to stdout for piping
        print(text)
        
        if args.verbose:
            word_count = len(text.split())
            print(f"\nExtracted {word_count} words", file=sys.stderr)
            
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()