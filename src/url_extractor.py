import requests
from bs4 import BeautifulSoup
from typing import Optional
import re

try:
    from .config import URLExtractorConfig
except ImportError:
    from config import URLExtractorConfig


class URLExtractor:
    """Extract human-readable text from URLs for TTS processing."""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': URLExtractorConfig.USER_AGENT
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
            response = self.session.get(url, timeout=URLExtractorConfig.REQUEST_TIMEOUT)
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
            
        soup = BeautifulSoup(html, URLExtractorConfig.DEFAULT_PARSER)
        
        # Remove script and style elements
        for script in soup(URLExtractorConfig.REMOVE_ELEMENTS):
            script.decompose()
        
        # Process the content
        text_parts = []
        processed_texts = set()  # Track processed text to avoid duplicates
        
        # Process block-level elements that should be separated
        for element in soup.find_all(URLExtractorConfig.TEXT_ELEMENTS):
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
    
    def extract_metadata(self, html: str, url: str) -> dict:
        """Extract metadata including title and text from HTML.
        
        Args:
            html: The HTML content
            url: The source URL
            
        Returns:
            Dictionary containing 'title', 'text', and 'url'
        """
        soup = BeautifulSoup(html, URLExtractorConfig.DEFAULT_PARSER)
        
        # Extract title
        title = ""
        title_tag = soup.find('title')
        if title_tag:
            title = title_tag.get_text(strip=True)
        else:
            # Fallback to first heading
            first_heading = soup.find(['h1', 'h2', 'h3'])
            if first_heading:
                title = first_heading.get_text(strip=True)
        
        # Extract text content
        text = self.extract_text(html)
        formatted_text = self.format_for_tts(text)
        
        return {
            'title': title,
            'text': formatted_text,
            'url': url
        }
    
    def extract_from_url_with_metadata(self, url: str) -> dict:
        """Extract text and metadata from a URL.
        
        Args:
            url: The URL to extract from
            
        Returns:
            Dictionary containing 'title', 'text', and 'url'
            
        Raises:
            Exception: If the URL cannot be processed
        """
        html = self.fetch_url(url)
        return self.extract_metadata(html, url)