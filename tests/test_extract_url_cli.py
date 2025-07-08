import subprocess
import pytest
from unittest.mock import patch, Mock


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
    
    # Run CLI with mocked HTTP request
    with patch('src.url_extractor.requests.Session.get') as mock_get:
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = test_html
        mock_get.return_value = mock_response
        
        result = subprocess.run(
            ["uv", "run", "python", "src/extract_url_cli.py", "https://example.com"],
            capture_output=True,
            text=True
        )
        
        assert result.returncode == 0
        assert "Test Page" in result.stdout
        assert "This is a test paragraph." in result.stdout
        assert "[Image: Test image]" in result.stdout
        assert "Another paragraph." in result.stdout


def test_cli_with_verbose():
    """Test CLI with verbose flag"""
    test_html = "<html><body><p>Test</p></body></html>"
    
    with patch('src.url_extractor.requests.Session.get') as mock_get:
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = test_html
        mock_get.return_value = mock_response
        
        result = subprocess.run(
            ["uv", "run", "python", "src/extract_url_cli.py", "-v", "https://example.com"],
            capture_output=True,
            text=True
        )
        
        assert result.returncode == 0
        assert "Test" in result.stdout
        assert "Fetching content from: https://example.com" in result.stderr
        assert "Extracted" in result.stderr
        assert "words" in result.stderr


def test_cli_error_handling():
    """Test CLI error handling"""
    with patch('src.url_extractor.requests.Session.get') as mock_get:
        mock_get.side_effect = Exception("Network error")
        
        result = subprocess.run(
            ["uv", "run", "python", "src/extract_url_cli.py", "https://example.com"],
            capture_output=True,
            text=True
        )
        
        assert result.returncode == 1
        assert "Error:" in result.stderr
        assert "Failed to fetch URL" in result.stderr