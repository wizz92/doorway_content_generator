"""OpenRouter API client."""
import time
import requests
from typing import Optional

from app.config import settings
from app.utils.logger import get_logger

logger = get_logger(__name__)


class OpenRouterClient:
    """Client for OpenRouter API."""
    
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None, api_url: Optional[str] = None):
        """
        Initialize OpenRouter client.
        
        Args:
            api_key: Optional API key (uses config default if not provided)
            model: Optional model name (uses config default if not provided)
            api_url: Optional API base URL (uses config default if not provided)
        """
        self.api_key = api_key or settings.openrouter_api_key
        self.model = model or settings.openrouter_model
        self.base_url = api_url or settings.openrouter_api_url
        self.request_delay = settings.request_delay_seconds
    
    def generate_content(
        self,
        keyword: str,
        lang: str,
        geo: str,
        website_index: int,
        model: Optional[str] = None,
        max_retries: int = 3
    ) -> str:
        """
        Generate content using OpenRouter API.
        
        Args:
            keyword: Keyword to generate content for
            lang: Language code (e.g., "hu", "en")
            geo: Geography code (e.g., "HU", "US")
            website_index: Index of website (for variation)
            model: Model to use (optional, uses configured model if not provided)
            max_retries: Maximum number of retry attempts
            
        Returns:
            Generated HTML content
            
        Raises:
            Exception: If content generation fails after retries
        """
        model_to_use = model or self.model
        
        url = f"{self.base_url}/chat/completions"
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        
        system_prompt = (
            "You are an expert SEO and web content writer. "
            "Always follow the user instructions exactly, especially about language, length limits, and HTML-only output. "
            "Never use Markdown or any formatting outside the allowed HTML tags when the user requests it."
        )
        
        # Create variation based on website index
        variation_instruction = self._get_variation_instruction(website_index)
        
        user_prompt = (
            f"Write an article in {lang.upper()} language for the {geo} region, strictly based on the keyword: \"{keyword}\".\n\n"
            f"{variation_instruction}\n\n"
            "Requirements:\n"
            f"- Output language: {lang.upper()} only.\n"
            "- Length: strictly between 450 and 550 words. Do not exceed this range and do not go below it.\n"
            "- Format the entire output as HTML, but ONLY use the following tags: <h1>, <h2>, <h3>, <p>, <ul>, <li>.\n"
            "- Do NOT use any other HTML tags (such as <html>, <head>, <body>, <article>, <section>, <div>, <span>, etc.).\n"
            "- Do NOT use Markdown or any Markdown-like symbols such as '**', '#', '##', '###', backticks, or similar.\n"
            "- Do NOT include any text outside of the allowed HTML tags.\n"
            "- Do NOT add HTML comments.\n"
            "- Produce only the final HTML fragment with the allowed tags, nothing else.\n\n"
            "Structure guidelines:\n"
            "- Start with a single <h1> heading that reflects the topic based on the keyword.\n"
            "- Use 2–3 <h2> sections to structure the main parts of the article.\n"
            "- Optionally use <h3> for subpoints under <h2> sections.\n"
            "- Use multiple <p> paragraphs with natural, human-like text.\n"
            "- Include one <ul> list with several <li> items related to the keyword.\n"
        )
        
        payload = {
            "model": model_to_use,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        }
        
        logger.debug(f"Generating content for keyword '{keyword}' using model '{model_to_use}'")
        
        # Retry logic
        last_error = None
        for attempt in range(max_retries):
            try:
                resp = requests.post(url, headers=headers, json=payload, timeout=180)
                resp.raise_for_status()
                data = resp.json()
                
                # Validate response structure
                if "choices" not in data or not data["choices"]:
                    raise ValueError("Invalid response: no choices in response")
                
                if "message" not in data["choices"][0] or "content" not in data["choices"][0]["message"]:
                    raise ValueError("Invalid response: no content in message")
                
                content = data["choices"][0]["message"]["content"]
                
                if not content or not content.strip():
                    raise ValueError("Empty content received from API")
                
                # Remove line breaks from content
                import re
                content = re.sub(r'[\r\n]+', '', content.strip())
                
                # Add delay to respect rate limits
                time.sleep(self.request_delay)
                
                logger.debug(f"Successfully generated content for keyword '{keyword}'")
                return content
                
            except requests.exceptions.Timeout:
                last_error = f"Request timeout (attempt {attempt + 1}/{max_retries})"
                logger.warning(f"Request timeout for keyword '{keyword}': {last_error}")
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
                    continue
            except requests.exceptions.HTTPError as e:
                if e.response and e.response.status_code == 429:  # Rate limit
                    last_error = f"Rate limit exceeded (attempt {attempt + 1}/{max_retries})"
                    logger.warning(f"Rate limit for keyword '{keyword}': {last_error}")
                    if attempt < max_retries - 1:
                        wait_time = (2 ** attempt) * 5  # Longer wait for rate limits
                        time.sleep(wait_time)
                        continue
                else:
                    last_error = f"HTTP error {e.response.status_code if e.response else 'unknown'}: {str(e)}"
                    logger.error(f"HTTP error for keyword '{keyword}': {last_error}")
                    if attempt < max_retries - 1:
                        time.sleep(2 ** attempt)
                        continue
            except requests.exceptions.RequestException as e:
                last_error = f"Request error: {str(e)}"
                logger.error(f"Request error for keyword '{keyword}': {last_error}", exc_info=True)
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)
                    continue
            except (KeyError, IndexError, ValueError) as e:
                last_error = f"Unexpected response format: {str(e)}"
                logger.error(f"Response format error for keyword '{keyword}': {last_error}", exc_info=True)
                # Don't retry on format errors
                break
            except Exception as e:
                last_error = f"Unexpected error: {str(e)}"
                logger.error(f"Unexpected error for keyword '{keyword}': {last_error}", exc_info=True)
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)
                    continue
        
        error_msg = f"Failed to generate content after {max_retries} attempts. Last error: {last_error}"
        logger.error(f"Content generation failed for keyword '{keyword}': {error_msg}")
        raise Exception(error_msg)
    
    def _get_variation_instruction(self, website_index: int) -> str:
        """Get variation instruction based on website index."""
        variations = [
            "Write in a professional, informative tone with a focus on providing comprehensive information.",
            "Write in a friendly, conversational tone that engages the reader personally.",
            "Write in an authoritative, expert tone that establishes credibility and trust.",
            "Write in a clear, concise tone that prioritizes readability and quick understanding.",
            "Write in a detailed, analytical tone that provides in-depth insights and explanations.",
        ]
        
        index = (website_index - 1) % len(variations)
        return variations[index]

