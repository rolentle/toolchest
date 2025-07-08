import subprocess
import pytest
from unittest.mock import patch, Mock, MagicMock
import sys
import os


def test_cli_help():
    """Test CLI help output"""
    result = subprocess.run(
        ["uv", "run", "python", "src/extract_url_cli.py", "--help"],
        capture_output=True,
        text=True
    )
    assert result.returncode == 0
    assert "Extract human-readable text from URLs" in result.stdout
    assert "url" in result.stdout


def test_cli_with_mocked_url():
    """Test CLI with mocked URL extraction"""
    # Create a test HTML content
    test_html = """
    <html>
        <body>
            <h1>Test Page</h1>
            <p>This is a test paragraph.</p>
            <img src="test.jpg" alt="Test image">
            <p>Another paragraph.</p>
        </body>
    </html>
    """
    
    # Import the modules directly to test them
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
    
    with patch('requests.Session') as mock_session:
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = test_html
        mock_session.return_value.get.return_value = mock_response
        
        from extract_url_cli import main
        
        # Mock sys.argv to simulate command line arguments
        with patch.object(sys, 'argv', ['extract_url_cli.py', 'https://example.com']):
            # Capture stdout
            from io import StringIO
            captured_output = StringIO()
            with patch('sys.stdout', captured_output):
                main()
            
            output = captured_output.getvalue()
            assert "Test Page" in output
            assert "This is a test paragraph." in output
            assert "[Image: Test image]" in output
            assert "Another paragraph." in output


def test_cli_with_verbose():
    """Test CLI with verbose flag"""
    test_html = "<html><body><p>Test</p></body></html>"
    
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
    
    with patch('requests.Session') as mock_session:
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = test_html
        mock_session.return_value.get.return_value = mock_response
        
        from extract_url_cli import main
        
        # Mock sys.argv to simulate command line arguments with verbose flag
        with patch.object(sys, 'argv', ['extract_url_cli.py', '-v', 'https://example.com']):
            # Capture stdout and stderr
            from io import StringIO
            captured_stdout = StringIO()
            captured_stderr = StringIO()
            with patch('sys.stdout', captured_stdout), patch('sys.stderr', captured_stderr):
                main()
            
            stdout_output = captured_stdout.getvalue()
            stderr_output = captured_stderr.getvalue()
            
            assert "Test" in stdout_output
            assert "Fetching content from: https://example.com" in stderr_output
            assert "Extracted" in stderr_output
            assert "words" in stderr_output


def test_cli_error_handling():
    """Test CLI error handling"""
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
    
    with patch('requests.Session') as mock_session:
        mock_session.return_value.get.side_effect = Exception("Network error")
        
        from extract_url_cli import main
        
        # Mock sys.argv to simulate command line arguments
        with patch.object(sys, 'argv', ['extract_url_cli.py', 'https://example.com']):
            # Capture stderr and check for exit
            from io import StringIO
            captured_stderr = StringIO()
            with patch('sys.stderr', captured_stderr), pytest.raises(SystemExit) as exc_info:
                main()
            
            stderr_output = captured_stderr.getvalue()
            assert exc_info.value.code == 1
            assert "Error:" in stderr_output