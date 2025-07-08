import pytest
from unittest.mock import patch
import sys
import os

# Add parent directory to path to import main
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from main import main


def test_main_prints_hello(capsys):
    """Test that main() prints the expected message."""
    main()
    captured = capsys.readouterr()
    assert captured.out == "Hello from toolchest!\n"


def test_main_module_execution():
    """Test that the module executes main() when run directly."""
    # Create a mock module to simulate running main.py directly
    test_module = type(sys)('test_module')
    test_module.__name__ = '__main__'
    
    with patch('builtins.print') as mock_print:
        # Execute the main.py code in the context where __name__ == '__main__'
        exec(open('main.py').read(), {'__name__': '__main__'})
        
        # Verify that main() was called by checking its output
        mock_print.assert_called_once_with("Hello from toolchest!")