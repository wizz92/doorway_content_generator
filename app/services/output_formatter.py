"""Output formatting service."""
from typing import Dict, List
import io
import zipfile
from pathlib import Path


def format_combined_articles(keyword: str, content: str) -> str:
    """
    Format a single keyword-content pair in combined_articles.txt format.
    
    Args:
        keyword: The keyword
        content: The HTML content
        
    Returns:
        Formatted line: "keyword ;; <h1>...</h1><p>...</p>"
    """
    return f"{keyword} ;; {content}\n"


def create_website_file(
    website_index: int,
    lang: str,
    geo: str,
    keyword_content_map: Dict[str, str]
) -> str:
    """
    Create a combined_articles.txt format file for a website.
    
    Args:
        website_index: Website index (1-based)
        lang: Language code
        geo: Geography code
        keyword_content_map: Dictionary mapping keywords to content
        
    Returns:
        File content as string
    """
    lines = []
    for keyword, content in keyword_content_map.items():
        lines.append(format_combined_articles(keyword, content))
    
    return "".join(lines)


def create_zip_archive(
    website_files: Dict[int, str],
    lang: str,
    geo: str
) -> bytes:
    """
    Create a ZIP archive containing all website files.
    
    Args:
        website_files: Dictionary mapping website_index to file content
        lang: Language code
        geo: Geography code
        
    Returns:
        ZIP file as bytes
    """
    zip_buffer = io.BytesIO()
    
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for website_index, file_content in website_files.items():
            filename = f"website-{website_index}-{lang}-{geo}.txt"
            zip_file.writestr(filename, file_content.encode('utf-8'))
    
    zip_buffer.seek(0)
    return zip_buffer.read()


def get_output_filename(website_index: int, lang: str, geo: str) -> str:
    """Get output filename for a website."""
    return f"website-{website_index}-{lang}-{geo}.txt"

