"""CSV file processing service."""
import csv
import io
from typing import List, Tuple, Optional

from fastapi import UploadFile

from app.constants import MAX_FILE_SIZE_BYTES, CSV_PREVIEW_MAX_ROWS
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
        
        if file_size > MAX_FILE_SIZE_BYTES:
            raise FileProcessingError(f"File size ({file_size / 1024 / 1024:.2f} MB) exceeds {MAX_FILE_SIZE_BYTES / 1024 / 1024:.0f}MB limit")
    except Exception as e:
        if isinstance(e, FileProcessingError):
            raise
        raise FileProcessingError(f"Error reading file: {str(e)}")


def _read_file_content(file: UploadFile) -> str:
    """
    Read and decode file content.
    
    Args:
        file: Uploaded file
        
    Returns:
        Decoded file content as string
        
    Raises:
        FileProcessingError: If reading or decoding fails
    """
    try:
        file.file.seek(0)
        content = file.file.read()
        file.file.seek(0)
        
        try:
            return content.decode('utf-8')
        except UnicodeDecodeError:
            try:
                return content.decode('latin-1')
            except UnicodeDecodeError:
                raise FileProcessingError(
                    "File encoding not supported. Please use UTF-8 or Latin-1 encoding."
                )
    except FileProcessingError:
        raise
    except Exception as e:
        raise FileProcessingError(f"Error reading file: {str(e)}")


def _parse_csv_keywords(content: str, column_name: str) -> List[str]:
    """
    Parse CSV content and extract keywords from specified column.
    
    Args:
        content: CSV file content as string
        column_name: Name of the column containing keywords
        
    Returns:
        List of keywords
        
    Raises:
        FileProcessingError: If parsing fails
    """
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
        for row in reader:
            try:
                kw = (row.get(column_name) or "").strip()
                if kw:
                    keywords.append(kw)
            except Exception:
                continue
        
        if not keywords:
            raise FileProcessingError(
                "No keywords found in CSV file. Please ensure the 'keyword' column contains data."
            )
        
        return keywords
        
    except FileProcessingError:
        raise
    except Exception as e:
        raise FileProcessingError(f"Error parsing CSV: {str(e)}")


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
    validate_csv_file(file)
    content = _read_file_content(file)
    return _parse_csv_keywords(content, column_name)


def get_csv_preview(file: UploadFile, column_name: str = "keyword", max_rows: int = CSV_PREVIEW_MAX_ROWS) -> Tuple[List[str], int]:
    """
    Get preview of keywords from CSV file.
    
    Returns:
        Tuple of (preview keywords list, total count)
    """
    keywords = extract_keywords_from_csv(file, column_name)
    preview = keywords[:max_rows]
    return preview, len(keywords)

