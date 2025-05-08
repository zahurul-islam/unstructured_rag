"""
DeepSeek LLM integration module.
"""

import logging
import os
import requests
from typing import Dict, List, Any, Optional

# Configure logging
logger = logging.getLogger(__name__)

class DeepSeekLLM:
    """
    Simple integration for DeepSeek API.
    """

    def __init__(
        self,
        api_key: str,
        model_name: str = "deepseek/deepseek-r1-zero:free",
        temperature: float = 0.1,
        max_tokens: int = 4096,
        top_p: float = 0.95,
    ):
        """
        Initialize the DeepSeek LLM.

        Args:
            api_key: DeepSeek API key
            model_name: Name of the model to use
            temperature: Temperature for text generation
            max_tokens: Maximum number of tokens to generate
            top_p: Top-p sampling parameter
        """
        self.api_key = api_key
        self.model_name = model_name
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.top_p = top_p
        self.api_url = "https://api.deepseek.com/v1/chat/completions"
        
        # Validate API key
        if not self.api_key:
            logger.error("DeepSeek API key is not provided")
            raise ValueError("DeepSeek API key is required")
        
        logger.info(f"Initialized DeepSeek API LLM: {self.model_name}")

    def generate(
        self,
        prompt: str,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> str:
        """
        Generate text using the DeepSeek API.

        Args:
            prompt: Prompt for text generation
            temperature: Optional override for temperature
            max_tokens: Optional override for max_tokens

        Returns:
            Generated text
        """
        try:
            # Prepare API request
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            # Prepare messages in chat format
            messages = [
                {"role": "user", "content": prompt}
            ]
            
            # Prepare request data
            data = {
                "model": self.model_name,
                "messages": messages,
                "temperature": temperature if temperature is not None else self.temperature,
                "max_tokens": max_tokens if max_tokens is not None else self.max_tokens,
                "top_p": self.top_p
            }
            
            # Make API request
            response = requests.post(
                self.api_url,
                headers=headers,
                json=data
            )
            
            # Check if request was successful
            response.raise_for_status()
            
            # Extract generated text
            result = response.json()
            generated_text = result["choices"][0]["message"]["content"]
            
            return generated_text
            
        except Exception as e:
            logger.error(f"Error generating text with DeepSeek API: {str(e)}")
            raise
