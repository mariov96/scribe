import os
import time
import logging
import google.generativeai as genai
from google.generativeai.types import content_types

logger = logging.getLogger(__name__)

class ScfCacher:
    """Manages the lifecycle of Gemini API CachedContent."""

    def __init__(self, api_key: str):
        """Initializes the cacher with the Gemini API key."""
        if not api_key:
            raise ValueError("Gemini API key is required.")
        
        genai.configure(api_key=api_key)
        self.model_id = "gemini-1.5-pro-latest"  # Caching-supported model
        self.model = genai.GenerativeModel(self.model_id)
        self.min_cache_tokens = 4096

    def create_cache(self, content: str, display_name: str, ttl: str = "3600s") -> str:
        """Creates a CachedContent object on the Gemini API."""
        logger.info(f"Attempting to create a new cache for: {display_name}...")
        try:
            # Step 1: Create the CachedContent resource
            cache = genai.caching.CachedContent.create(
                model=self.model_id,
                contents=[content_types.to_content(content)],
                display_name=display_name,
                ttl=ttl,
            )
            logger.info(f"Cache created successfully. ID: {cache.name}")
            logger.info(f"Cached Tokens: {cache.usage_metadata.total_token_count}")
            return cache.name

        except Exception as e:
            logger.error(f"Failed to create cache. Ensure your model supports caching and context is large enough. {e}")
            return None

    def generate_with_cache(self, cache_name: str, user_prompt: str):
        """Generates content using the explicit cache."""
        logger.info(f"Querying with Cached Content ID: {cache_name}")
        
        try:
            response = self.model.generate_content(
                contents=user_prompt,
                cached_content=cache_name
            )

            # Validation
            cached_tokens = response.usage_metadata.cached_content_token_count
            prompt_tokens = response.usage_metadata.prompt_token_count
            
            logger.info("Successful Response.")
            logger.info(f"Cached Tokens (Discounted): {cached_tokens}")
            logger.info(f"New Prompt Tokens (Full Cost): {prompt_tokens}")
            
            return response.text

        except Exception as e:
            logger.error(f"Failed to use cache. {e}")
            return None

    def delete_cache(self, cache_name: str):
        """Deletes the CachedContent object to avoid storage costs."""
        logger.info(f"Deleting Cache: {cache_name}")
        try:
            genai.caching.CachedContent.delete(name=cache_name)
            logger.info("Cache deleted successfully. Storage cost stopped.")
        except Exception as e:
            logger.warning(f"Failed to delete cache. You may need to delete it manually. {e}")