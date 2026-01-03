"""File storage service for managing output files."""
from pathlib import Path
from typing import Dict, Optional
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

