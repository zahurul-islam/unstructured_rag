"""
LLM integration module for DeepSeek-R1-Zero.
"""

import logging
import os
from typing import Dict, List, Any, Optional

from app.config import config

# Configure logging
logger = logging.getLogger(__name__)


class LLM:
    """
    LLM integration for DeepSeek-R1-Zero.
    """
    
    def __init__(
        self,
        model_name: str = None,
        api_key: str = None,
        temperature: float = None,
        max_tokens: int = None,
        top_p: float = None,
    ):
        """
        Initialize the LLM.
        
        Args:
            model_name: Name of the model to use
            api_key: DeepSeek API key
            temperature: Temperature for text generation
            max_tokens: Maximum number of tokens to generate
            top_p: Top-p sampling parameter
        """
        self.model_name = model_name or config.llm.model_name
        self.api_key = api_key or config.llm.api_key
        self.temperature = temperature or config.llm.temperature
        self.max_tokens = max_tokens or config.llm.max_tokens
        self.top_p = top_p or config.llm.top_p
        
        # Check if API key is provided
        if not self.api_key:
            logger.warning("DeepSeek API key not provided")
        
        # Initialize LangChain
        self._init_langchain()
    
    def _init_langchain(self):
        """Initialize LangChain with the DeepSeek model."""
        try:
            from langchain_deepseek import DeepSeekChat
            from langchain.chains import LLMChain
            from langchain.prompts import PromptTemplate
            
            # Initialize DeepSeekChat
            self.llm = DeepSeekChat(
                model=self.model_name,
                deepseek_api_key=self.api_key,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                top_p=self.top_p,
            )
            
            logger.info(f"Initialized DeepSeek LLM: {self.model_name}")
        
        except Exception as e:
            logger.error(f"Error initializing LLM: {str(e)}")
            self.llm = None
    
    def generate(
        self,
        prompt: str,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> str:
        """
        Generate text using the LLM.
        
        Args:
            prompt: Prompt for text generation
            temperature: Optional override for temperature
            max_tokens: Optional override for max_tokens
            
        Returns:
            Generated text
        """
        if not self.llm:
            raise ValueError("LLM not initialized")
        
        try:
            # Override parameters if provided
            if temperature is not None or max_tokens is not None:
                temp_llm = self.llm.bind(
                    temperature=temperature or self.temperature,
                    max_tokens=max_tokens or self.max_tokens,
                )
                response = temp_llm.invoke(prompt)
            else:
                response = self.llm.invoke(prompt)
            
            return response
        
        except Exception as e:
            logger.error(f"Error generating text: {str(e)}")
            raise
    
    def generate_with_chain(
        self,
        template: str,
        input_variables: Dict[str, Any],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> str:
        """
        Generate text using a LangChain PromptTemplate.
        
        Args:
            template: Template string for the prompt
            input_variables: Dictionary of input variables for the template
            temperature: Optional override for temperature
            max_tokens: Optional override for max_tokens
            
        Returns:
            Generated text
        """
        if not self.llm:
            raise ValueError("LLM not initialized")
        
        try:
            from langchain.prompts import PromptTemplate
            from langchain.chains import LLMChain
            
            # Create prompt template
            prompt_template = PromptTemplate(
                input_variables=list(input_variables.keys()),
                template=template,
            )
            
            # Override parameters if provided
            if temperature is not None or max_tokens is not None:
                temp_llm = self.llm.bind(
                    temperature=temperature or self.temperature,
                    max_tokens=max_tokens or self.max_tokens,
                )
                chain = LLMChain(llm=temp_llm, prompt=prompt_template)
            else:
                chain = LLMChain(llm=self.llm, prompt=prompt_template)
            
            # Run chain
            response = chain.run(**input_variables)
            
            return response
        
        except Exception as e:
            logger.error(f"Error generating text with chain: {str(e)}")
            raise


# Global LLM instance
_llm = None


def get_llm() -> LLM:
    """
    Get the global LLM instance.
    
    Returns:
        LLM instance
    """
    global _llm
    
    if _llm is None:
        _llm = LLM()
    
    return _llm
