"""File storage service for managing output files."""
from pathlib import Path
from typing import Dict, Optional, List
import hashlib
from app.config import settings


class FileStorageService:
    """Service for managing output files on the filesystem."""
    
    def __init__(self, base_dir: Optional[str] = None):
        """
        Initialize file storage service.
        
        Args:
            base_dir: Base directory for storing files (defaults to OUTPUT_DIR from settings)
        """
        self.base_dir = Path(base_dir or settings.output_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)
    
    def get_job_directory(self, job_id: str) -> Path:
        """
        Get the directory for a specific job.
        
        Args:
            job_id: Job identifier
            
        Returns:
            Path to job directory
        """
        job_dir = self.base_dir / job_id
        job_dir.mkdir(parents=True, exist_ok=True)
        return job_dir
    
    def save_website_file(
        self,
        job_id: str,
        website_index: int,
        lang: str,
        geo: str,
        content: str
    ) -> str:
        """
        Save a website file to the filesystem.
        
        Args:
            job_id: Job identifier
            website_index: Website index (1-based)
            lang: Language code
            geo: Geography code
            content: File content as string
            
        Returns:
            Relative file path
        """
        job_dir = self.get_job_directory(job_id)
        filename = f"website-{website_index}-{lang}-{geo}.txt"
        file_path = job_dir / filename
        
        # Write content to file
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        # Return relative path from base_dir
        return str(file_path.relative_to(self.base_dir))
    
    def get_website_file_path(
        self,
        job_id: str,
        website_index: int,
        lang: str,
        geo: str
    ) -> Path:
        """
        Get the file path for a website file.
        
        Args:
            job_id: Job identifier
            website_index: Website index (1-based)
            lang: Language code
            geo: Geography code
            
        Returns:
            Path to the file
        """
        job_dir = self.get_job_directory(job_id)
        filename = f"website-{website_index}-{lang}-{geo}.txt"
        return job_dir / filename
    
    def read_website_file(
        self,
        job_id: str,
        website_index: int,
        lang: str,
        geo: str
    ) -> str:
        """
        Read a website file from the filesystem.
        
        Args:
            job_id: Job identifier
            website_index: Website index (1-based)
            lang: Language code
            geo: Geography code
            
        Returns:
            File content as string
            
        Raises:
            FileNotFoundError: If file doesn't exist
        """
        file_path = self.get_website_file_path(job_id, website_index, lang, geo)
        
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    
    def get_all_website_files(self, job_id: str, lang: str, geo: str) -> Dict[int, str]:
        """
        Get all website files for a job.
        
        Args:
            job_id: Job identifier
            lang: Language code
            geo: Geography code
            
        Returns:
            Dictionary mapping website_index to file content
        """
        job_dir = self.get_job_directory(job_id)
        files = {}
        
        # Find all website files for this job
        pattern = f"website-*-{lang}-{geo}.txt"
        for file_path in job_dir.glob(pattern):
            # Extract website index from filename
            # Format: website-{index}-{lang}-{geo}.txt
            parts = file_path.stem.split('-')
            if len(parts) >= 2:
                try:
                    website_index = int(parts[1])
                    with open(file_path, 'r', encoding='utf-8') as f:
                        files[website_index] = f.read()
                except (ValueError, IndexError):
                    continue
        
        return files
    
    def delete_job_files(self, job_id: str) -> None:
        """
        Delete all files for a job.
        
        Args:
            job_id: Job identifier
        """
        job_dir = self.get_job_directory(job_id)
        if job_dir.exists():
            import shutil
            shutil.rmtree(job_dir)
    
    def file_exists(self, job_id: str, website_index: int, lang: str, geo: str) -> bool:
        """
        Check if a website file exists.
        
        Args:
            job_id: Job identifier
            website_index: Website index (1-based)
            lang: Language code
            geo: Geography code
            
        Returns:
            True if file exists, False otherwise
        """
        file_path = self.get_website_file_path(job_id, website_index, lang, geo)
        return file_path.exists()
    
    def _sanitize_keyword_for_filename(self, keyword: str) -> str:
        """
        Sanitize keyword to create a safe filename.
        
        Args:
            keyword: Original keyword
            
        Returns:
            Sanitized keyword safe for use in filenames
        """
        # Create a hash of the keyword for uniqueness
        keyword_hash = hashlib.md5(keyword.encode('utf-8')).hexdigest()[:8]
        
        # Sanitize keyword: keep alphanumeric, spaces, hyphens, underscores
        safe_keyword = "".join(c for c in keyword if c.isalnum() or c in (' ', '-', '_')).strip()
        safe_keyword = safe_keyword.replace(' ', '_')[:50]  # Limit length
        
        # Combine sanitized keyword with hash for uniqueness
        return f"{safe_keyword}_{keyword_hash}"
    
    def save_keyword_content(
        self,
        job_id: str,
        website_index: int,
        keyword: str,
        lang: str,
        geo: str,
        content: str
    ) -> str:
        """
        Save individual keyword content to a temporary file.
        This allows incremental saving and resume capability.
        
        Args:
            job_id: Job identifier
            website_index: Website index (1-based)
            keyword: Keyword
            lang: Language code
            geo: Geography code
            content: Generated content for this keyword
            
        Returns:
            File path where content was saved
        """
        job_dir = self.get_job_directory(job_id)
        # Create a subdirectory for keyword-level content
        keyword_dir = job_dir / "keywords" / f"website-{website_index}"
        keyword_dir.mkdir(parents=True, exist_ok=True)
        
        # Sanitize keyword for filename
        safe_keyword = self._sanitize_keyword_for_filename(keyword)
        
        filename = f"{safe_keyword}.html"
        file_path = keyword_dir / filename
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return str(file_path.relative_to(self.base_dir))
    
    def get_completed_keywords(
        self,
        job_id: str,
        website_index: int,
        keywords_list: List[str]
    ) -> List[str]:
        """
        Get list of keywords that have already been generated for a website.
        Matches keywords by comparing with the provided keywords list.
        
        Args:
            job_id: Job identifier
            website_index: Website index (1-based)
            keywords_list: Original list of keywords to match against
            
        Returns:
            List of keyword strings that have been completed
        """
        job_dir = self.get_job_directory(job_id)
        keyword_dir = job_dir / "keywords" / f"website-{website_index}"
        
        if not keyword_dir.exists():
            return []
        
        completed = []
        # Create a set of keyword hashes for fast lookup
        keyword_hashes = {hashlib.md5(k.encode('utf-8')).hexdigest()[:8]: k for k in keywords_list}
        
        for file_path in keyword_dir.glob("*.html"):
            # Extract hash from filename (last 8 characters before .html)
            filename = file_path.stem
            if '_' in filename:
                parts = filename.rsplit('_', 1)
                if len(parts) == 2:
                    keyword_hash = parts[1]
                    if keyword_hash in keyword_hashes:
                        completed.append(keyword_hashes[keyword_hash])
        
        return completed
    
    def load_keyword_content(
        self,
        job_id: str,
        website_index: int,
        keyword: str
    ) -> Optional[str]:
        """
        Load previously generated content for a keyword.
        
        Args:
            job_id: Job identifier
            website_index: Website index (1-based)
            keyword: Keyword
            
        Returns:
            Content string if found, None otherwise
        """
        job_dir = self.get_job_directory(job_id)
        keyword_dir = job_dir / "keywords" / f"website-{website_index}"
        
        # Sanitize keyword for filename
        safe_keyword = self._sanitize_keyword_for_filename(keyword)
        
        file_path = keyword_dir / f"{safe_keyword}.html"
        
        if not file_path.exists():
            return None
        
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()

