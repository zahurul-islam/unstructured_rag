"""
LLM integration module for DeepSeek-R1-Zero.
"""

import logging
import os
from typing import Dict, List, Any, Optional
import time

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
        use_gpu: bool = None,
        gpu_device: int = None,
        temperature: float = None,
        max_tokens: int = None,
        top_p: float = None,
    ):
        """
        Initialize the LLM.

        Args:
            model_name: Name of the model to use
            api_key: DeepSeek API key
            use_gpu: Whether to use GPU (if available)
            gpu_device: GPU device ID to use
            temperature: Temperature for text generation
            max_tokens: Maximum number of tokens to generate
            top_p: Top-p sampling parameter
        """
        self.model_name = model_name or config.llm.model_name
        self.api_key = api_key or config.llm.api_key
        self.use_gpu = use_gpu if use_gpu is not None else config.llm.use_gpu
        self.gpu_device = gpu_device if gpu_device is not None else config.llm.gpu_device
        self.temperature = temperature or config.llm.temperature
        self.max_tokens = max_tokens or config.llm.max_tokens
        self.top_p = top_p or config.llm.top_p

        # Initialize model based on configuration
        self.model = None
        self.tokenizer = None
        self.api_model = None
        self.use_api = self.api_key is not None and ("api" in os.environ.get("LLM_MODE", "").lower() or os.environ.get("LLM_MODE", "").lower() == "api")

        # Initialize
        self._init_model()

    def _init_model(self):
        """Initialize the LLM based on configuration."""
        if self.use_api:
            # Use API-based model
            self._init_api_model()
        else:
            # Use local model with transformers
            self._init_local_model()

    def _init_api_model(self):
        """Initialize API-based model with custom DeepSeek wrapper."""
        try:
            # Import our custom DeepSeek wrapper
            from rag.generation.deepseek_llm import DeepSeekLLM
            
            # Initialize DeepSeekLLM
            self.api_model = DeepSeekLLM(
                api_key=self.api_key,
                model_name=self.model_name,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                top_p=self.top_p,
            )
            
            logger.info(f"Initialized DeepSeek API LLM: {self.model_name}")
            
        except Exception as e:
            logger.error(f"Error initializing API model: {str(e)}")
            self.api_model = None

    def _init_local_model(self):
        """Initialize local model with transformers."""
        try:
            import torch
            from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig

            # Check if GPU is available
            if self.use_gpu and torch.cuda.is_available():
                device = f"cuda:{self.gpu_device}"
                logger.info(f"Initializing model on GPU: {torch.cuda.get_device_name(self.gpu_device)}")

                # Setup quantization config for large models
                if "deepseek" in self.model_name.lower() or "mistral" in self.model_name.lower():
                    bnb_config = BitsAndBytesConfig(
                        load_in_4bit=True,
                        bnb_4bit_use_double_quant=True,
                        bnb_4bit_quant_type="nf4",
                        bnb_4bit_compute_dtype=torch.bfloat16
                    )

                    # Load tokenizer and model
                    self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
                    self.model = AutoModelForCausalLM.from_pretrained(
                        self.model_name,
                        device_map=device,
                        quantization_config=bnb_config,
                        trust_remote_code=True
                    )
                else:
                    # For smaller models, load without quantization
                    self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
                    self.model = AutoModelForCausalLM.from_pretrained(
                        self.model_name,
                        device_map=device,
                        torch_dtype=torch.float16,
                        trust_remote_code=True
                    )
            else:
                # CPU fallback
                device = "cpu"
                logger.info(f"GPU not available or disabled, initializing model on CPU")

                self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
                self.model = AutoModelForCausalLM.from_pretrained(
                    self.model_name,
                    trust_remote_code=True
                )

            # Verify model is on correct device
            if hasattr(self.model, 'device'):
                logger.info(f"Model loaded on: {self.model.device}")
            else:
                logger.info(f"Model loaded with device map: {self.model.hf_device_map}")

            logger.info(f"Initialized local LLM: {self.model_name}")

        except Exception as e:
            logger.error(f"Error initializing local model: {str(e)}")
            self.model = None
            self.tokenizer = None

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
        if self.use_api and self.api_model:
            return self._generate_with_api(prompt, temperature, max_tokens)
        elif self.model and self.tokenizer:
            return self._generate_with_local(prompt, temperature, max_tokens)
        else:
            raise ValueError("No LLM model initialized")

    def _generate_with_api(
        self,
        prompt: str,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> str:
        """Generate text using the API-based model."""
        try:
            # Check if API model is initialized
            if self.api_model is None:
                logger.warning("API model not initialized. Initializing now...")
                self._init_api_model()

                # If still not initialized, raise error
                if self.api_model is None:
                    raise ValueError("Failed to initialize API model")

            # Generate response using custom DeepSeek LLM
            response = self.api_model.generate(
                prompt=prompt,
                temperature=temperature,
                max_tokens=max_tokens
            )

            return response

        except Exception as e:
            logger.error(f"Error generating text with API: {str(e)}")
            raise

    def _generate_with_local(
        self,
        prompt: str,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> str:
        """Generate text using the local model."""
        try:
            import torch

            # Use provided parameters or defaults
            temp = temperature if temperature is not None else self.temperature
            max_new_tokens = max_tokens if max_tokens is not None else self.max_tokens

            # Tokenize the prompt
            inputs = self.tokenizer(prompt, return_tensors="pt")

            # Move input tensors to the model's device
            if self.use_gpu and torch.cuda.is_available():
                inputs = {k: v.to(f"cuda:{self.gpu_device}") for k, v in inputs.items()}

            # Set generation parameters
            generation_config = {
                "max_new_tokens": max_new_tokens,
                "temperature": temp,
                "top_p": self.top_p,
                "do_sample": temp > 0,
                "pad_token_id": self.tokenizer.eos_token_id,
            }

            # Generate text
            start_time = time.time()
            with torch.no_grad():
                outputs = self.model.generate(**inputs, **generation_config)

            # Decode generated text
            generated_text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)

            # Remove the prompt from the generated text
            # Some models already handle this, but we do it explicitly to be sure
            if generated_text.startswith(prompt):
                response = generated_text[len(prompt):].strip()
            else:
                # If we can't find the exact prompt (e.g., due to tokenization differences),
                # just return the full output
                response = generated_text.strip()

            generation_time = time.time() - start_time
            logger.info(f"Generated text in {generation_time:.2f}s")

            return response

        except Exception as e:
            logger.error(f"Error generating text with local model: {str(e)}")
            raise

    def generate_with_chain(
        self,
        template: str,
        input_variables: Dict[str, Any],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> str:
        """
        Generate text using a template with variables.

        Args:
            template: Template string for the prompt
            input_variables: Dictionary of input variables for the template
            temperature: Optional override for temperature
            max_tokens: Optional override for max_tokens

        Returns:
            Generated text
        """
        # Format the template with input variables
        try:
            prompt = template
            for key, value in input_variables.items():
                placeholder = "{" + key + "}"
                prompt = prompt.replace(placeholder, str(value))

            # Try to generate text with the API
            try:
                return self.generate(prompt, temperature, max_tokens)
            except Exception as e:
                logger.warning(f"Error generating with API, falling back to simple response: {str(e)}")
                
                # Use simple response generator as fallback
                from rag.generation.simple_response import generate_simple_response
                return generate_simple_response(
                    query=input_variables.get("query", ""),
                    context=input_variables.get("context", "")
                )

        except Exception as e:
            logger.error(f"Error generating text with template: {str(e)}")
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
