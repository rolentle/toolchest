import sys
from datetime import datetime
from typing import Optional, TextIO


class Logger:
    """Centralized logging functionality for the Toolchest application."""
    
    LEVELS = {
        "debug": 0,
        "info": 1,
        "warning": 2,
        "error": 3,
    }
    
    def __init__(self, name: str, level: str = "info", output: Optional[TextIO] = None):
        """
        Initialize a Logger instance.
        
        Args:
            name: The name of the logger (typically module name)
            level: The minimum logging level to output
            output: The output stream (defaults to stderr)
        """
        self.name = name
        self.level = self.LEVELS.get(level.lower(), 1)
        self.output = output or sys.stderr
        
    def _make_log(self, level: str, msg: str) -> str:
        """Format a log message with timestamp, level, and module name."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return f"[{timestamp}] [{level.upper()}] [{self.name}] {msg}"
        
    def _should_log(self, level: str) -> bool:
        """Check if the given level should be logged based on current settings."""
        return self.LEVELS.get(level.lower(), 0) >= self.level
        
    def log(self, level: str, msg: str):
        """Log a message at the specified level."""
        if self._should_log(level):
            self.output.write(self._make_log(level, msg) + "\n")
            self.output.flush()
            
    def debug(self, msg: str):
        """Log a debug message."""
        self.log("debug", msg)
        
    def info(self, msg: str):
        """Log an info message."""
        self.log("info", msg)
        
    def warning(self, msg: str):
        """Log a warning message."""
        self.log("warning", msg)
        
    def error(self, msg: str):
        """Log an error message."""
        self.log("error", msg)