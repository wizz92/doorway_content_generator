"""Tests for output formatter service."""
import pytest
from app.services.output_formatter import (
    format_combined_articles,
    create_website_file,
    create_zip_archive,
    get_output_filename
)


class TestOutputFormatter:
    """Test cases for output formatter."""
    
    def test_format_combined_articles(self):
        """Test formatting a single keyword-content pair."""
        keyword = "test keyword"
        content = "<h1>Title</h1><p>Content</p>"
        
        result = format_combined_articles(keyword, content)
        
        assert result == f"{keyword} ;; {content}\n"
        assert ";;" in result
    
    def test_create_website_file(self):
        """Test creating a website file."""
        keyword_content_map = {
            "keyword1": "<h1>Title 1</h1><p>Content 1</p>",
            "keyword2": "<h1>Title 2</h1><p>Content 2</p>"
        }
        
        result = create_website_file(1, "hu", "HU", keyword_content_map)
        
        assert "keyword1 ;; <h1>Title 1</h1><p>Content 1</p>" in result
        assert "keyword2 ;; <h1>Title 2</h1><p>Content 2</p>" in result
        assert result.count("\n") == 2  # Two lines
    
    def test_create_zip_archive(self):
        """Test creating a ZIP archive."""
        website_files = {
            1: "keyword1 ;; <h1>Title 1</h1><p>Content 1</p>\n",
            2: "keyword2 ;; <h1>Title 2</h1><p>Content 2</p>\n"
        }
        
        zip_content = create_zip_archive(website_files, "hu", "HU")
        
        assert isinstance(zip_content, bytes)
        assert len(zip_content) > 0
        
        # Verify ZIP structure (basic check)
        assert zip_content.startswith(b'PK')  # ZIP file signature
    
    def test_get_output_filename(self):
        """Test getting output filename."""
        filename = get_output_filename(1, "hu", "HU")
        
        assert filename == "website-1-hu-HU.txt"
        
        filename2 = get_output_filename(5, "en", "US")
        assert filename2 == "website-5-en-US.txt"

