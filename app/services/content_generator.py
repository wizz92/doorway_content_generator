"""Content generation service."""
from typing import List, Dict
from app.services.openrouter_client import OpenRouterClient
from app.config import settings


class ContentGenerator:
    """Service for generating content variations."""
    
    def __init__(self):
        self.openrouter_client = OpenRouterClient()
    
    def generate_content_for_keyword(
        self,
        keyword: str,
        lang: str,
        geo: str,
        website_index: int
    ) -> str:
        """
        Generate content for a keyword for a specific website.
        
        Args:
            keyword: Keyword to generate content for
            lang: Language code
            geo: Geography code
            website_index: Website index (1-based)
            
        Returns:
            Generated HTML content
        """
        return self.openrouter_client.generate_content(
            keyword=keyword,
            lang=lang,
            geo=geo,
            website_index=website_index
        )
    
    def generate_all_variations(
        self,
        keywords: List[str],
        lang: str,
        geo: str,
        num_websites: int
    ) -> Dict[int, Dict[str, str]]:
        """
        Generate content variations for all keywords across all websites.
        
        Args:
            keywords: List of keywords
            lang: Language code
            geo: Geography code
            num_websites: Number of websites
            
        Returns:
            Dictionary mapping website_index to dict of {keyword: content}
        """
        results = {}
        
        for website_index in range(1, num_websites + 1):
            results[website_index] = {}
            
            for keyword in keywords:
                try:
                    content = self.generate_content_for_keyword(
                        keyword=keyword,
                        lang=lang,
                        geo=geo,
                        website_index=website_index
                    )
                    results[website_index][keyword] = content
                except Exception as e:
                    # Log error but continue with other keywords
                    print(f"Error generating content for keyword '{keyword}' on website {website_index}: {e}")
                    results[website_index][keyword] = f"<p>Error generating content: {str(e)}</p>"
        
        return results

