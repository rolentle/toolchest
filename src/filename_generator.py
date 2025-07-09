"""Module for generating descriptive filenames using Ollama."""
import re
import ollama
from datetime import datetime
from urllib.parse import urlparse
from typing import Optional

try:
    from .config import OllamaConfig
    from .logger import Logger
except ImportError:
    from config import OllamaConfig
    from logger import Logger


class FilenameGenerator:
    """Generate descriptive filenames using Ollama LLM."""
    
    def __init__(self, model: Optional[str] = None):
        """Initialize the filename generator.
        
        Args:
            model: Ollama model to use (defaults to OllamaConfig.DEFAULT_MODEL)
        """
        self.model = model or OllamaConfig.DEFAULT_MODEL
        self.logger = Logger("FilenameGenerator")
    
    def sanitize_filename(self, filename: str) -> str:
        """Sanitize a filename for filesystem compatibility.
        
        Args:
            filename: Raw filename to sanitize
            
        Returns:
            Sanitized filename safe for filesystem use
        """
        # Convert to lowercase
        filename = filename.lower()
        
        # Replace special characters and spaces with underscores
        filename = re.sub(r'[^a-z0-9]+', '_', filename)
        
        # Remove leading/trailing underscores
        filename = filename.strip('_')
        
        # Remove consecutive underscores
        filename = re.sub(r'_+', '_', filename)
        
        # Handle empty result
        if not filename:
            filename = "unnamed"
        
        # Limit length
        if len(filename) > OllamaConfig.MAX_FILENAME_LENGTH:
            filename = filename[:OllamaConfig.MAX_FILENAME_LENGTH]
        
        return filename
    
    def add_timestamp(self, filename: str) -> str:
        """Add timestamp to filename.
        
        Args:
            filename: Base filename
            
        Returns:
            Filename with timestamp appended
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"{filename}_{timestamp}"
    
    def generate_from_content(
        self, 
        text: str, 
        title: Optional[str] = None,
        url: Optional[str] = None
    ) -> str:
        """Generate a descriptive filename from text content using Ollama.
        
        Args:
            text: The text content to summarize
            title: Optional page title
            url: Optional source URL (used as fallback)
            
        Returns:
            Generated filename with .wav extension
        """
        try:
            # Truncate text if too long
            if len(text) > OllamaConfig.MAX_TEXT_LENGTH_FOR_SUMMARY:
                text = text[:OllamaConfig.MAX_TEXT_LENGTH_FOR_SUMMARY] + "..."
            
            # Build prompt
            prompt = OllamaConfig.FILENAME_PROMPT_TEMPLATE
            
            # Include title if provided
            if title:
                prompt_text = f"Title: {title}\n\n{text}"
            else:
                prompt_text = text
            
            prompt = prompt.format(text=prompt_text)
            
            # Call Ollama
            self.logger.info(f"Generating filename using Ollama model: {self.model}")
            response = ollama.chat(
                model=self.model,
                messages=[{
                    'role': 'user',
                    'content': prompt
                }],
                options={
                    'timeout': OllamaConfig.FILENAME_GENERATION_TIMEOUT
                }
            )
            
            # Extract filename from response
            generated_name = response['message']['content'].strip()
            self.logger.info(f"Ollama generated filename: {generated_name}")
            
            # Sanitize and add timestamp
            filename = self.sanitize_filename(generated_name)
            filename = self.add_timestamp(filename)
            
            return f"{filename}.wav"
            
        except Exception as e:
            self.logger.warning(f"Failed to generate filename with Ollama: {e}")
            # Fallback to URL-based naming if Ollama fails
            if url:
                self.logger.info("Falling back to URL-based filename generation")
                return self.generate_from_url(url)
            else:
                # Final fallback
                self.logger.info("Using default filename")
                filename = self.add_timestamp("audio_file")
                return f"{filename}.wav"
    
    def generate_from_url(self, url: str) -> str:
        """Generate filename from URL.
        
        Args:
            url: Source URL
            
        Returns:
            Generated filename with .wav extension
        """
        try:
            parsed = urlparse(url)
            
            # Extract domain and path
            domain = parsed.netloc.replace('.', '_')
            path = parsed.path.strip('/')
            
            if path:
                # Get the last part of the path
                path_parts = path.split('/')
                # Take the last meaningful part
                relevant_parts = [p for p in path_parts if p and not p.isdigit()]
                if relevant_parts:
                    path = relevant_parts[-1]
                else:
                    path = ""
            
            # Combine domain and path
            if path:
                base_name = f"{domain}_{path}"
            else:
                base_name = domain
            
            # Sanitize and add timestamp
            filename = self.sanitize_filename(base_name)
            filename = self.add_timestamp(filename)
            
            return f"{filename}.wav"
            
        except Exception:
            # Final fallback
            filename = self.add_timestamp("audio_file")
            return f"{filename}.wav"