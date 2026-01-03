"""Tests for file processor service."""
import pytest
from io import BytesIO
from fastapi import UploadFile
from app.services.file_processor import (
    extract_keywords_from_csv,
    get_csv_preview,
    FileProcessingError
)


def create_csv_file(content: str, filename: str = "test.csv") -> UploadFile:
    """Helper to create an UploadFile from string content."""
    file_content = content.encode('utf-8')
    file_obj = BytesIO(file_content)
    return UploadFile(filename=filename, file=file_obj)


class TestFileProcessor:
    """Test cases for file processor."""
    
    def test_extract_keywords_valid_csv(self):
        """Test extracting keywords from a valid CSV file."""
        csv_content = "keyword\nkeyword1\nkeyword2\nkeyword3"
        file = create_csv_file(csv_content)
        
        keywords = extract_keywords_from_csv(file, "keyword")
        
        assert len(keywords) == 3
        assert keywords == ["keyword1", "keyword2", "keyword3"]
    
    def test_extract_keywords_with_empty_rows(self):
        """Test extracting keywords with empty rows."""
        csv_content = "keyword\nkeyword1\n\nkeyword2\n  \nkeyword3"
        file = create_csv_file(csv_content)
        
        keywords = extract_keywords_from_csv(file, "keyword")
        
        assert len(keywords) == 3
        assert "keyword1" in keywords
        assert "keyword2" in keywords
        assert "keyword3" in keywords
    
    def test_extract_keywords_missing_column(self):
        """Test error when required column is missing."""
        csv_content = "name,value\nitem1,100\nitem2,200"
        file = create_csv_file(csv_content)
        
        with pytest.raises(Exception) as exc_info:
            extract_keywords_from_csv(file, "keyword")
        
        assert "not found" in str(exc_info.value).lower()
    
    def test_extract_keywords_empty_file(self):
        """Test error with empty file."""
        csv_content = ""
        file = create_csv_file(csv_content)
        
        with pytest.raises(Exception):
            extract_keywords_from_csv(file, "keyword")
    
    def test_extract_keywords_no_keywords(self):
        """Test error when no keywords are found."""
        csv_content = "keyword\n\n  \n"
        file = create_csv_file(csv_content)
        
        with pytest.raises(Exception) as exc_info:
            extract_keywords_from_csv(file, "keyword")
        
        assert "no keywords" in str(exc_info.value).lower()
    
    def test_get_csv_preview(self):
        """Test getting CSV preview."""
        csv_content = "keyword\n" + "\n".join([f"keyword{i}" for i in range(1, 21)])
        file = create_csv_file(csv_content)
        
        preview, total = get_csv_preview(file, "keyword", max_rows=10)
        
        assert len(preview) == 10
        assert total == 20
        assert preview[0] == "keyword1"
    
    def test_extract_keywords_large_file(self):
        """Test extracting keywords from a file with many keywords."""
        keywords = [f"keyword{i}" for i in range(1, 101)]
        csv_content = "keyword\n" + "\n".join(keywords)
        file = create_csv_file(csv_content)
        
        result = extract_keywords_from_csv(file, "keyword")
        
        assert len(result) == 100
        assert result == keywords

