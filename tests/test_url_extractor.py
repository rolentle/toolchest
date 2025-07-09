import pytest
from unittest.mock import Mock, patch
from src.url_extractor import URLExtractor


class TestURLExtractor:
    def setup_method(self):
        self.extractor = URLExtractor()

    def test_fetch_url_success(self):
        """Test successful URL fetching"""
        with patch('src.url_extractor.requests.Session.get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.text = "<html><body>Test content</body></html>"
            mock_get.return_value = mock_response
            
            result = self.extractor.fetch_url("https://example.com")
            assert result == "<html><body>Test content</body></html>"
            mock_get.assert_called_once_with("https://example.com", timeout=10)

    def test_fetch_url_failure(self):
        """Test URL fetching with network error"""
        with patch('src.url_extractor.requests.Session.get') as mock_get:
            mock_get.side_effect = Exception("Network error")
            
            with pytest.raises(Exception) as exc_info:
                self.extractor.fetch_url("https://example.com")
            assert "Failed to fetch URL" in str(exc_info.value)

    def test_extract_text_simple_html(self):
        """Test text extraction from simple HTML"""
        html = """
        <html>
            <body>
                <p>This is a paragraph.</p>
                <p>This is another paragraph.</p>
            </body>
        </html>
        """
        result = self.extractor.extract_text(html)
        assert "This is a paragraph." in result
        assert "This is another paragraph." in result
        # Check for proper spacing between paragraphs
        assert "\n\n" in result

    def test_extract_text_with_images(self):
        """Test text extraction including image alt tags"""
        html = """
        <html>
            <body>
                <p>Before image</p>
                <img src="test.jpg" alt="A beautiful sunset">
                <p>After image</p>
            </body>
        </html>
        """
        result = self.extractor.extract_text(html)
        assert "Before image" in result
        assert "[Image: A beautiful sunset]" in result
        assert "After image" in result

    def test_extract_text_skip_scripts_and_styles(self):
        """Test that script and style tags are skipped"""
        html = """
        <html>
            <head>
                <style>body { color: red; }</style>
            </head>
            <body>
                <p>Visible text</p>
                <script>console.log('invisible');</script>
            </body>
        </html>
        """
        result = self.extractor.extract_text(html)
        assert "Visible text" in result
        assert "color: red" not in result
        assert "console.log" not in result

    def test_extract_text_decode_entities(self):
        """Test HTML entity decoding"""
        html = """
        <html>
            <body>
                <p>This &amp; that</p>
                <p>&quot;Quoted text&quot;</p>
                <p>&lt;tag&gt;</p>
            </body>
        </html>
        """
        result = self.extractor.extract_text(html)
        assert "This & that" in result
        assert '"Quoted text"' in result
        assert "<tag>" in result

    def test_format_for_tts(self):
        """Test text formatting for TTS"""
        text = "Paragraph one.\nParagraph two.\n\nParagraph three."
        result = self.extractor.format_for_tts(text)
        # Should ensure double line breaks between paragraphs
        assert "Paragraph one.\n\nParagraph two.\n\nParagraph three." in result

    def test_extract_from_url_integration(self):
        """Test the complete extraction process"""
        with patch.object(self.extractor, 'fetch_url') as mock_fetch:
            mock_fetch.return_value = """
            <html>
                <body>
                    <h1>Title</h1>
                    <p>First paragraph.</p>
                    <img src="test.jpg" alt="Test image">
                    <p>Second paragraph.</p>
                </body>
            </html>
            """
            
            result = self.extractor.extract_from_url("https://example.com")
            assert "Title" in result
            assert "First paragraph." in result
            assert "[Image: Test image]" in result
            assert "Second paragraph." in result
            # Check proper spacing
            assert result.count("\n\n") >= 3  # Between title and paragraphs

    def test_extract_text_complex_html(self):
        """Test extraction from complex HTML with nested elements"""
        html = """
        <html>
            <body>
                <div>
                    <h1>Main Title</h1>
                    <div class="content">
                        <p>First <strong>bold</strong> paragraph with <a href="#">link</a>.</p>
                        <ul>
                            <li>List item 1</li>
                            <li>List item 2</li>
                        </ul>
                        <p>Final paragraph.</p>
                    </div>
                </div>
            </body>
        </html>
        """
        result = self.extractor.extract_text(html)
        assert "Main Title" in result
        assert "First bold paragraph with link" in result
        assert "List item 1" in result
        assert "List item 2" in result
        assert "Final paragraph." in result

    def test_extract_text_empty_html(self):
        """Test extraction from empty or minimal HTML"""
        result = self.extractor.extract_text("<html><body></body></html>")
        assert result.strip() == ""
        
        result = self.extractor.extract_text("")
        assert result.strip() == ""

    def test_extract_text_image_without_alt(self):
        """Test handling of images without alt attribute"""
        html = """
        <html>
            <body>
                <p>Before image</p>
                <img src="test.jpg">
                <p>After image</p>
            </body>
        </html>
        """
        result = self.extractor.extract_text(html)
        assert "Before image" in result
        assert "After image" in result
        # Should not include any image placeholder for images without alt
        assert "[Image:" not in result
    
    def test_extract_metadata(self):
        """Test extraction of metadata including title"""
        html = """
        <html>
            <head>
                <title>Test Page Title</title>
            </head>
            <body>
                <h1>Main Heading</h1>
                <p>Some content here.</p>
            </body>
        </html>
        """
        result = self.extractor.extract_metadata(html, "https://example.com/page")
        
        assert result['title'] == "Test Page Title"
        assert result['url'] == "https://example.com/page"
        assert "Main Heading" in result['text']
        assert "Some content here." in result['text']
    
    def test_extract_metadata_no_title(self):
        """Test metadata extraction when no title tag exists"""
        html = """
        <html>
            <body>
                <h1>First Heading</h1>
                <p>Content without title tag.</p>
            </body>
        </html>
        """
        result = self.extractor.extract_metadata(html, "https://example.com")
        
        # Should fallback to first heading or empty string
        assert result['title'] in ["First Heading", ""]
        assert result['url'] == "https://example.com"
        assert "Content without title tag." in result['text']
    
    def test_extract_from_url_with_metadata(self):
        """Test the full extraction pipeline returning metadata"""
        with patch('src.url_extractor.requests.Session.get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.text = """
            <html>
                <head>
                    <title>Article Title</title>
                </head>
                <body>
                    <h1>Main Article</h1>
                    <p>Article content.</p>
                </body>
            </html>
            """
            mock_get.return_value = mock_response
            
            result = self.extractor.extract_from_url_with_metadata("https://example.com/article")
            
            assert isinstance(result, dict)
            assert result['title'] == "Article Title"
            assert result['url'] == "https://example.com/article"
            assert "Main Article" in result['text']
            assert "Article content." in result['text']