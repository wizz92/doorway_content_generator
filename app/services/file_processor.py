"""CSV file processing service."""
import csv
import io
from typing import List, Tuple, Optional
from fastapi import UploadFile

from app.exceptions import FileProcessingError


def validate_csv_file(file: UploadFile) -> None:
    """
    Validate uploaded CSV file.
    
    Raises:
        FileProcessingError: If file validation fails
    """
    if not file.filename:
        raise FileProcessingError("No filename provided")
    
    if not file.filename.endswith('.csv'):
        raise FileProcessingError("File must be a CSV file (.csv extension required)")
    
    # Check file size (max 10MB)
    try:
        file.file.seek(0, 2)  # Seek to end
        file_size = file.file.tell()
        file.file.seek(0)  # Reset to beginning
        
        if file_size == 0:
            raise FileProcessingError("File is empty")
        
        if file_size > 10 * 1024 * 1024:  # 10MB
            raise FileProcessingError(f"File size ({file_size / 1024 / 1024:.2f} MB) exceeds 10MB limit")
    except Exception as e:
        if isinstance(e, FileProcessingError):
            raise
        raise FileProcessingError(f"Error reading file: {str(e)}")


def extract_keywords_from_csv(file: UploadFile, column_name: str = "keyword") -> List[str]:
    """
    Extract keywords from CSV file.
    
    Args:
        file: Uploaded CSV file
        column_name: Name of the column containing keywords
        
    Returns:
        List of keywords
        
    Raises:
        FileProcessingError: If extraction fails
    """
    try:
        validate_csv_file(file)
    except FileProcessingError as e:
        raise
    
    # Read file content
    try:
        file.file.seek(0)
        content = file.file.read()
        file.file.seek(0)
        
        # Try to decode as UTF-8
        try:
            content = content.decode('utf-8')
        except UnicodeDecodeError:
            try:
                content = content.decode('latin-1')
            except UnicodeDecodeError:
                raise FileProcessingError("File encoding not supported. Please use UTF-8 or Latin-1 encoding.")
    except Exception as e:
        if isinstance(e, FileProcessingError):
            raise
        raise FileProcessingError(f"Error reading file: {str(e)}")
    
    # Parse CSV
    try:
        reader = csv.DictReader(io.StringIO(content))
        
        if not reader.fieldnames:
            raise FileProcessingError("CSV file appears to be empty or invalid")
        
        if column_name not in reader.fieldnames:
            available = ', '.join(reader.fieldnames or [])
            raise FileProcessingError(
                f"Column '{column_name}' not found in CSV. Available columns: {available}"
            )
        
        keywords = []
        row_num = 1
        for row in reader:
            row_num += 1
            try:
                kw = (row.get(column_name) or "").strip()
                if kw:
                    keywords.append(kw)
            except Exception as e:
                # Skip problematic rows but continue processing
                continue
        
        if not keywords:
            raise FileProcessingError("No keywords found in CSV file. Please ensure the 'keyword' column contains data.")
        
        return keywords
        
    except FileProcessingError:
        raise
    except Exception as e:
        raise FileProcessingError(f"Error parsing CSV: {str(e)}")


def get_csv_preview(file: UploadFile, column_name: str = "keyword", max_rows: int = 10) -> Tuple[List[str], int]:
    """
    Get preview of keywords from CSV file.
    
    Returns:
        Tuple of (preview keywords list, total count)
    """
    keywords = extract_keywords_from_csv(file, column_name)
    preview = keywords[:max_rows]
    return preview, len(keywords)

