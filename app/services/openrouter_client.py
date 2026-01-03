"""OpenRouter API client."""
import os
import time
import random
import requests
from typing import List, Optional
from app.config import settings


class OpenRouterClient:
    """Client for OpenRouter API."""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.openrouter_api_key
        self.base_url = "https://openrouter.ai/api/v1"
        self.request_delay = settings.request_delay_seconds
        self.models: List[str] = []
        
    def get_available_models(self) -> List[str]:
        """Fetch available models from OpenRouter."""
        if self.models:
            return self.models
            
        url = f"{self.base_url}/models"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
        }
        
        try:
            resp = requests.get(url, headers=headers, timeout=30)
            resp.raise_for_status()
            data = resp.json()
            
            model_ids = []
            for item in data.get("data", []):
                model_id = item.get("id")
                if not model_id:
                    continue
                
                lower_id = model_id.lower()
                # Filter out image/vision/audio models
                if any(bad in lower_id for bad in ["image", "vision", "speech", "audio"]):
                    continue
                
                model_ids.append(model_id)
            
            if model_ids:
                self.models = model_ids
            else:
                # Fallback to default model
                self.models = ["google/gemini-2.5-flash-lite"]
                
        except Exception as e:
            # Fallback to default model on error
            self.models = ["google/gemini-2.5-flash-lite"]
        
        return self.models
    
    def choose_random_model(self) -> str:
        """Choose a random model from available models."""
        models = self.get_available_models()
        return random.choice(models)
    
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
            model: Model to use (optional, random if not provided)
            max_retries: Maximum number of retry attempts
            
        Returns:
            Generated HTML content
            
        Raises:
            Exception: If content generation fails after retries
        """
        if not model:
            model = self.choose_random_model()
        
        url = f"{self.base_url}/chat/completions"
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://doorway-content-generator.local",
            "X-Title": "doorway_content_generator",
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
            "model": model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        }
        
        # Retry logic
        last_error = None
        for attempt in range(max_retries):
            try:
                resp = requests.post(url, headers=headers, json=payload, timeout=180)
                resp.raise_for_status()
                data = resp.json()
                
                # Validate response structure
                if "choices" not in data or not data["choices"]:
                    raise Exception("Invalid response: no choices in response")
                
                if "message" not in data["choices"][0] or "content" not in data["choices"][0]["message"]:
                    raise Exception("Invalid response: no content in message")
                
                content = data["choices"][0]["message"]["content"]
                
                if not content or not content.strip():
                    raise Exception("Empty content received from API")
                
                # Remove line breaks from content
                import re
                content = re.sub(r'[\r\n]+', '', content.strip())
                
                # Add delay to respect rate limits
                time.sleep(self.request_delay)
                
                return content
                
            except requests.exceptions.Timeout:
                last_error = f"Request timeout (attempt {attempt + 1}/{max_retries})"
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
                    continue
            except requests.exceptions.HTTPError as e:
                if e.response and e.response.status_code == 429:  # Rate limit
                    last_error = f"Rate limit exceeded (attempt {attempt + 1}/{max_retries})"
                    if attempt < max_retries - 1:
                        wait_time = (2 ** attempt) * 5  # Longer wait for rate limits
                        time.sleep(wait_time)
                        continue
                else:
                    last_error = f"HTTP error {e.response.status_code if e.response else 'unknown'}: {str(e)}"
                    if attempt < max_retries - 1:
                        time.sleep(2 ** attempt)
                        continue
            except requests.exceptions.RequestException as e:
                last_error = f"Request error: {str(e)}"
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)
                    continue
            except (KeyError, IndexError) as e:
                last_error = f"Unexpected response format: {str(e)}"
                # Don't retry on format errors
                break
            except Exception as e:
                last_error = f"Unexpected error: {str(e)}"
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)
                    continue
        
        raise Exception(f"Failed to generate content after {max_retries} attempts. Last error: {last_error}")
    
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

