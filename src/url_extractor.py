import requests
from bs4 import BeautifulSoup
from typing import Optional
import re


class URLExtractor:
    """Extract human-readable text from URLs for TTS processing."""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (compatible; TTS-TextExtractor/1.0)'
        })
    
    def fetch_url(self, url: str) -> str:
        """Fetch content from a URL.
        
        Args:
            url: The URL to fetch
            
        Returns:
            The HTML content as a string
            
        Raises:
            Exception: If the URL cannot be fetched
        """
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            return response.text
        except Exception as e:
            raise Exception(f"Failed to fetch URL: {e}")
    
    def extract_text(self, html: str) -> str:
        """Extract human-readable text from HTML.
        
        Args:
            html: The HTML content
            
        Returns:
            Extracted text with proper formatting for TTS
        """
        if not html:
            return ""
            
        soup = BeautifulSoup(html, 'lxml')
        
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
        
        # Process the content
        text_parts = []
        processed_texts = set()  # Track processed text to avoid duplicates
        
        # Process block-level elements that should be separated
        for element in soup.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'li']):
            # Get text with spaces preserved between inline elements
            text = element.get_text(separator=' ', strip=True)
            if text and text not in processed_texts:
                processed_texts.add(text)
                text_parts.append(text)
        
        # Process images separately
        for img in soup.find_all('img'):
            alt_text = img.get('alt', '').strip()
            if alt_text:
                img_text = f"[Image: {alt_text}]"
                if img_text not in processed_texts:
                    processed_texts.add(img_text)
                    text_parts.append(img_text)
        
        # Join with double newlines for paragraph spacing
        return '\n\n'.join(text_parts)
    
    def format_for_tts(self, text: str) -> str:
        """Format text for optimal TTS processing.
        
        Args:
            text: The extracted text
            
        Returns:
            Formatted text with proper spacing for TTS
        """
        # Ensure consistent paragraph spacing
        # Replace single newlines with double newlines if not already present
        lines = text.split('\n')
        formatted_lines = []
        
        for line in lines:
            line = line.strip()
            if line:
                formatted_lines.append(line)
        
        # Join with double newlines for TTS pauses
        return '\n\n'.join(formatted_lines)
    
    def extract_from_url(self, url: str) -> str:
        """Extract and format text from a URL for TTS.
        
        Args:
            url: The URL to extract text from
            
        Returns:
            Formatted text ready for TTS processing
            
        Raises:
            Exception: If the URL cannot be processed
        """
        html = self.fetch_url(url)
        text = self.extract_text(html)
        return self.format_for_tts(text)